#!/usr/bin/env python3
"""
export.py — Export OWOX Data Marts to an Open Knowledge Format (OKF) bundle,
            and optionally push that bundle to a GitHub repo.

Configure credentials in a .env file next to this script (see .env.example).
Run `python3 export.py --help` for all options.
Dependencies: Python 3.8+ standard library only. `git` on PATH is needed for --push.
"""

import argparse
import base64
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request


def _load_dotenv():
    """Load KEY=VALUE pairs from a .env file next to this script into os.environ.
    Existing env vars are never overwritten (shell always wins over .env)."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


EXCHANGE_PATH = "/api/auth/api-keys/exchange"
DATA_MART_GET_PATH = "/api/data-marts/{id}"
DATA_NDJSON_PATH = "/api/external/http-data/data-marts/{id}.ndjson"


# --------------------------------------------------------------------------- #
# HTTP helpers (stdlib only)
# --------------------------------------------------------------------------- #
def _http(method, url, headers=None, body=None, timeout=60):
    data = None
    headers = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _http_json(method, url, headers=None, body=None, timeout=60):
    status, raw = _http(method, url, headers, body, timeout)
    if status >= 400:
        raise RuntimeError(f"{method} {url} -> HTTP {status}: {raw[:500].decode('utf-8', 'replace')}")
    if not raw:
        return None
    return json.loads(raw.decode("utf-8"))


# --------------------------------------------------------------------------- #
# OWOX auth
# --------------------------------------------------------------------------- #
def _b64url_decode_json(s):
    padded = s + "=" * (-len(s) % 4)
    return json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))


def parse_api_key(owox_key):
    """owox_key_<base64url(JSON)> -> (apiOrigin, apiKeyId, apiKeySecret)."""
    owox_key = owox_key.strip()
    if not owox_key.startswith("owox_key_"):
        raise ValueError("OWOX API key must start with 'owox_key_'")
    try:
        obj = _b64url_decode_json(owox_key[len("owox_key_"):])
        return obj["apiOrigin"].rstrip("/"), obj["apiKeyId"], obj["apiKeySecret"]
    except KeyError as e:
        raise ValueError(f"Decoded API key is missing field {e}") from None


def exchange_for_token(api_origin, api_key_id, api_key_secret):
    data = _http_json("POST", api_origin + EXCHANGE_PATH,
                      headers={"X-OWOX-Api-Key-Id": api_key_id},
                      body={"apiKeySecret": api_key_secret})
    token = data.get("accessToken")
    if not token:
        raise RuntimeError("Token exchange succeeded but no accessToken in response")
    return token


def project_title_from_token(access_token):
    """Decode the JWT payload (no verification needed — we just need the project title)."""
    try:
        return _b64url_decode_json(access_token.split(".")[1]).get("projectTitle") or ""
    except Exception:
        return ""


def auth_headers(access_token, api_key_id):
    # Send both header styles so the same token works on the management API
    # (standard bearer) and the external data API (x-owox-authorization).
    return {
        "Authorization": f"Bearer {access_token}",
        "x-owox-authorization": f"Bearer {access_token}",
        "X-OWOX-Api-Key-Id": api_key_id,
    }


# --------------------------------------------------------------------------- #
# OWOX data-mart fetching
# --------------------------------------------------------------------------- #
def list_data_marts(api_origin, headers):
    """Page through /api/data-marts and return [{id, title, ...}, ...]."""
    items, offset = [], 0
    while True:
        page = _http_json("GET", f"{api_origin}/api/data-marts?offset={offset}", headers=headers)
        batch = page.get("items", []) if isinstance(page, dict) else (page or [])
        items.extend(batch)
        nxt = page.get("nextOffset") if isinstance(page, dict) else None
        if not nxt:
            break
        offset = nxt
    return items


def get_data_mart(api_origin, headers, mart_id):
    return _http_json("GET", api_origin + DATA_MART_GET_PATH.format(id=mart_id), headers=headers)


RELATIONSHIPS_GRAPH_PATH = "/api/data-marts/{id}/relationships/graph"


def get_relationships_graph(api_origin, headers, mart_id):
    """Fetch a mart's relationship graph. Returns an empty graph if the API refuses,
    so that export still works for keys or projects without relationship access."""
    try:
        return _http_json("GET", api_origin + RELATIONSHIPS_GRAPH_PATH.format(id=mart_id),
                          headers=headers)
    except urllib.error.HTTPError as exc:
        print(f"  ! relationships unavailable for {mart_id} (HTTP {exc.code}); "
              f"falling back to name matching.")
        return {"nodes": []}


def build_join_index(graph, mart_id):
    """Map a mart's direct joins to their real key pairs.

    Returns {path_key: [(source_field, target_field), ...]} where path_key matches
    blendedFieldsConfig's `path` for the same join. Only edges leaving `mart_id` are
    kept; cycle stubs and deeper hops are skipped, and each relationship id is used once.
    """
    index, seen = {}, set()
    for node in (graph or {}).get("nodes") or []:
        if not isinstance(node, dict) or node.get("isCycleStub"):
            continue
        rel = node.get("relationship") or {}
        rel_id = rel.get("id")
        if not rel_id or rel_id in seen:
            continue
        if (rel.get("sourceDataMart") or {}).get("id") != mart_id:
            continue
        path = node.get("aliasPath") or rel.get("targetAlias") or ""
        if not path or "." in path:
            continue
        pairs = [(c["sourceFieldName"], c["targetFieldName"])
                 for c in rel.get("joinConditions") or []
                 if isinstance(c, dict) and c.get("sourceFieldName") and c.get("targetFieldName")]
        if not pairs:
            continue
        seen.add(rel_id)
        index[path] = pairs
    return index


def fetch_sample_rows(api_origin, headers, mart_id, n):
    """Stream the .ndjson endpoint and stop after n rows (does not download all)."""
    if n <= 0:
        return []
    rows = []
    try:
        url = api_origin + DATA_NDJSON_PATH.format(id=mart_id)
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as resp:
            for raw in resp:
                line = raw.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                if len(rows) >= n:
                    break
    except urllib.error.HTTPError as e:
        print(f"  ! could not fetch sample rows for {mart_id}: HTTP {e.code}", file=sys.stderr)
    return rows


# --------------------------------------------------------------------------- #
# OKF rendering
# --------------------------------------------------------------------------- #
def slugify(text, fallback):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or fallback


class _Raw(str):
    """YAML scalar emitted unquoted (use for timestamps and other pre-formatted values)."""


def yaml_scalar(value):
    """Safely emit a single-line YAML string scalar."""
    if isinstance(value, _Raw):
        return str(value)
    s = "" if value is None else str(value)
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")
    return f'"{s}"'


def yaml_list(values):
    return "[" + ", ".join(yaml_scalar(v) for v in values) + "]"


def render_frontmatter(fields):
    lines = ["---"]
    for key, val in fields.items():
        if val is None:
            continue
        if isinstance(val, (list, tuple)):
            lines.append(f"{key}: {yaml_list(val)}")
        else:
            lines.append(f"{key}: {yaml_scalar(val)}")
    lines.append("---")
    return "\n".join(lines)


def extract_columns(schema):
    """Best-effort: pull a list of (name, type, description) from OWOX's schema object."""
    if not isinstance(schema, dict):
        return []
    fields = next(
        (schema[k] for k in ("fields", "columns", "schema") if isinstance(schema.get(k), list)),
        None,
    )
    if fields is None:
        return []
    cols = []
    for f in fields:
        if not isinstance(f, dict):
            continue
        name = f.get("name") or f.get("alias") or f.get("field") or ""
        ftype = f.get("type") or f.get("dataType") or f.get("mode") or ""
        desc = f.get("description") or f.get("title") or ""
        is_pk = bool(f.get("isPrimaryKey"))
        cols.append((str(name), str(ftype), str(desc), is_pk))
    return cols


def render_schema_section(schema, fk=None):
    cols = extract_columns(schema)
    if cols:
        out = ["# Schema", "", "| Column | Type | Description |", "|--------|------|-------------|"]
        for name, ftype, desc, is_pk in cols:
            desc = desc.replace("|", "\\|").replace("\n", " ")
            # Cell order matches the canvas serializer: "PK." marker first, then the
            # description, then any "FK to [Target]" note. The canvas parser reads a
            # leading "PK." as the primary key (parse.ts) — this is what lets the ERD
            # resolve join keys against this mart as a join target.
            parts = []
            if is_pk:
                parts.append("PK.")
            if desc:
                parts.append(desc)
            if fk and name in fk:
                linked_title, linked_fname = fk[name]
                parts.append(f"FK to [{linked_title}](./{linked_fname})")
            out.append(f"| `{name}` | {ftype} | {' '.join(parts).strip()} |")
        return "\n".join(out)
    if schema:
        return "# Schema\n\n```json\n" + json.dumps(schema, indent=2, ensure_ascii=False) + "\n```"
    return ""


def render_data_mart_doc(mart, api_origin, sample_rows, fk=None):
    mart_id = mart.get("id", "")
    title = mart.get("title") or mart_id
    description = mart.get("description") or ""
    definition_type = mart.get("definitionType") or ""
    status = mart.get("status") or ""
    storage = mart.get("storage") or {}
    storage_type = storage.get("type") or ""
    storage_title = storage.get("title") or ""
    modified = _Raw(mart.get("modifiedAt") or now_iso())
    data_url = f"{api_origin}{DATA_NDJSON_PATH.format(id=mart_id)}"

    tags = ["owox"]
    if storage_type:
        tags.append(storage_type.lower())
    if definition_type:
        tags.append(definition_type.lower())
    if mart.get("connectorSourceName"):
        tags.append(slugify(mart["connectorSourceName"], "connector"))

    short_desc = (description.strip().splitlines()[0] if description.strip()
                  else f"OWOX data mart '{title}'.")
    if len(short_desc) > 200:
        short_desc = short_desc[:197] + "..."

    frontmatter = render_frontmatter({
        "type": "OWOX Data Mart",
        "title": title,
        "description": short_desc,
        "resource": data_url,
        "tags": tags,
        "timestamp": modified,
    })

    body = [f"# {title}", ""]
    if description.strip():
        body += [description.strip(), ""]
    body += [
        "## Overview",
        "",
        f"- **ID:** `{mart_id}`",
        f"- **Status:** {status}",
        f"- **Definition type:** {definition_type}",
        f"- **Storage:** {storage_title} ({storage_type})".replace(" ()", ""),
        f"- **Data endpoint:** `GET {data_url}`",
        "",
    ]

    schema_section = render_schema_section(mart.get("schema"), fk=fk)
    if schema_section:
        body += [schema_section, ""]

    if sample_rows:
        preview = "\n".join(json.dumps(r, ensure_ascii=False) for r in sample_rows)
        body += [
            f"## Sample (first {len(sample_rows)} rows)",
            "",
            "> Preview only — the full dataset lives at the data endpoint above.",
            "",
            "```json",
            preview,
            "```",
            "",
        ]

    return frontmatter + "\n\n" + "\n".join(body).rstrip() + "\n"


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- #
# Bundle writing
# --------------------------------------------------------------------------- #
def _build_path_lookup(marts_with_docs):
    """Map OWOX internal path keys (underscore slugs) → (display title, filename, pk_fields)."""
    lookup = {}
    for mart, _ in marts_with_docs:
        title = mart.get("title") or mart.get("id", "")
        fname = slugify(title, mart.get("id", "")) + ".md"
        path_key = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        pks = [f["name"] for f in (mart.get("schema") or {}).get("fields", [])
               if f.get("isPrimaryKey")]
        lookup[path_key] = (title, fname, pks)
    return lookup


def _fk_lookup(mart, path_lookup, join_index=None):
    """Return dict of field_name → (linked_title, linked_fname) for FK fields.

    The FK note belongs on the column that actually carries the foreign key, which the
    relationship graph names explicitly. Without a graph we fall back to the older
    assumption that the FK column is named like the target's primary key.
    """
    sources = (mart.get("blendedFieldsConfig") or {}).get("sources") or []
    direct = [s for s in sources
              if "." not in s.get("path", "") and not s.get("isExcluded")]
    join_index = join_index or {}
    fk = {}
    for src in direct:
        entry = path_lookup.get(src["path"])
        if not entry:
            continue
        linked_title, linked_fname, pks = entry
        pairs = join_index.get(src["path"])
        if pairs:
            for source_field, _target_field in pairs:
                fk[source_field] = (linked_title, linked_fname)
        else:
            for pk in pks:
                fk[pk] = (linked_title, linked_fname)
    return fk


def _render_joins_section(mart, path_lookup, join_index=None):
    """Return a ## Joins markdown section from blendedFieldsConfig, or empty string.

    Join keys come from the mart's relationship graph (`joinConditions`), which is the
    only place the real column pair is recorded — a join may bind columns with different
    names (`sku = product_code`). When a source has no relationship (blend-only sources,
    or an API that withheld the graph) we fall back to the older heuristic: a column named
    exactly like the target's primary key. A link with neither stays bare, as before.
    """
    sources = (mart.get("blendedFieldsConfig") or {}).get("sources") or []
    direct = [s for s in sources
              if "." not in s.get("path", "") and not s.get("isExcluded")]
    if not direct:
        return ""
    join_index = join_index or {}
    local_cols = {f.get("name") for f in (mart.get("schema") or {}).get("fields", [])
                  if isinstance(f, dict)}
    lines = ["## Joins", ""]
    for src in direct:
        alias = (src.get("alias") or src["path"]).replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
        matched = path_lookup.get(src["path"])
        if matched:
            _, fname, target_pks = matched
            pairs = join_index.get(src["path"])
            if not pairs:
                pairs = [(pk, pk) for pk in target_pks if pk in local_cols]
            cond = ", ".join(f"`{left} = {right}`" for left, right in pairs)
            lines.append(f"- [{alias}](./{fname}) — {cond}" if cond
                         else f"- [{alias}](./{fname})")
        else:
            lines.append(f"- {alias}")
    lines.append("")
    return "\n".join(lines)


def write_bundle(out_dir, marts_with_docs, project_folder, project_title="Data Marts"):
    """marts_with_docs: list of (mart_dict, rendered_markdown).
    project_folder: slugified OWOX project name used as the subfolder name."""
    marts_dir = os.path.join(out_dir, project_folder)
    os.makedirs(marts_dir, exist_ok=True)
    ts = _Raw(now_iso())

    path_lookup = _build_path_lookup(marts_with_docs)

    index_rows = []
    for mart, doc in marts_with_docs:
        mart_id = mart.get("id", "")
        fname = slugify(mart.get("title", ""), mart_id) + ".md"
        joins = _render_joins_section(mart, path_lookup)
        if joins:
            doc = doc.rstrip("\n") + "\n\n" + joins
        with open(os.path.join(marts_dir, fname), "w", encoding="utf-8") as fh:
            fh.write(doc)
        index_rows.append((mart.get("title") or mart_id, fname,
                           mart.get("definitionType") or "",
                           (mart.get("storage") or {}).get("type") or ""))

    def _safe_cell(text):
        return text.replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")

    # <project_folder>/index.md
    di = [render_frontmatter({
        "type": "index", "title": project_title,
        "description": "Index of exported OWOX data marts.",
        "tags": ["owox", "index"], "timestamp": ts,
    }), "", f"# {project_title}", "", "| Data Mart | Type | Storage |",
        "|-----------|------|---------|"]
    for title, fname, dtype, stype in sorted(index_rows):
        safe_title = _safe_cell(title)
        di.append(f"| [{safe_title}](./{fname}) | {_safe_cell(dtype)} | {_safe_cell(stype)} |")
    with open(os.path.join(marts_dir, "index.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(di) + "\n")

    # bundle root index.md
    root = [render_frontmatter({
        "type": "index", "title": project_title,
        "description": f"OKF bundle generated from OWOX Data Marts.",
        "tags": ["owox", "index"], "timestamp": ts,
    }), "", f"# {project_title}", "",
        f"Generated {ts}.", "",
        f"- [{project_title}](./{project_folder}/index.md) — {len(index_rows)} concept(s)", ""]
    with open(os.path.join(out_dir, "index.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(root) + "\n")

    return len(index_rows)


# --------------------------------------------------------------------------- #
# Viz HTML generation
# --------------------------------------------------------------------------- #
_VIZ_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>OKF Bundle Viewer</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  font-size: 14px; color: #0f172a; background: #f8fafc;
  display: flex; flex-direction: column; height: 100vh;
}
header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px; background: #fff;
  border-bottom: 1px solid #e2e8f0; flex-shrink: 0;
}
.title strong { font-size: 16px; margin-right: 8px; }
.muted { color: #64748b; font-size: 12px; }
.controls { display: flex; gap: 8px; }
.controls input, .controls select, .controls button {
  font-size: 13px; padding: 5px 8px;
  border: 1px solid #cbd5e1; border-radius: 4px; background: #fff;
}
.controls input { width: 200px; }
.controls button { cursor: pointer; background: #f1f5f9; }
.controls button:hover { background: #e2e8f0; }
main { display: flex; flex: 1; min-height: 0; }
#graph {
  flex: 1 1 60%; background: #fff;
  border-right: 1px solid #e2e8f0; min-width: 0;
}
#detail { flex: 0 0 40%; overflow-y: auto; padding: 18px 22px; background: #fff; }
#detail-empty { text-align: center; margin-top: 40px; color: #64748b; }
.detail-header { margin-bottom: 12px; }
.detail-header h1 { font-size: 18px; margin: 4px 0 2px; font-weight: 600; }
.type-chip {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 11px; font-weight: 600; color: #fff; background: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.5px;
}
dl.frontmatter {
  display: grid; grid-template-columns: 90px 1fr;
  row-gap: 4px; column-gap: 12px; margin: 8px 0 12px; font-size: 13px;
}
dl.frontmatter dt { color: #64748b; font-weight: 500; }
dl.frontmatter dd { margin: 0; word-break: break-all; }
.tag {
  display: inline-block; background: #f1f5f9; border: 1px solid #e2e8f0;
  border-radius: 4px; padding: 1px 6px; font-size: 11px; margin: 1px 2px 1px 0;
}
a.external { color: #3b82f6; word-break: break-all; }
.markdown-body { font-size: 13px; line-height: 1.6; }
.markdown-body h1 { font-size: 16px; margin: 16px 0 8px; }
.markdown-body h2 { font-size: 14px; margin: 14px 0 6px; }
.markdown-body h3 { font-size: 13px; margin: 12px 0 4px; }
.markdown-body code { background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
.markdown-body pre { background: #f1f5f9; padding: 10px; border-radius: 4px; overflow-x: auto; }
.markdown-body pre code { background: none; padding: 0; }
.markdown-body table { border-collapse: collapse; width: 100%; font-size: 12px; }
.markdown-body th, .markdown-body td { border: 1px solid #e2e8f0; padding: 4px 8px; text-align: left; }
.markdown-body th { background: #f8fafc; }
.markdown-body blockquote { border-left: 3px solid #cbd5e1; margin: 0; padding: 4px 12px; color: #64748b; }
#detail-backlinks { margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 12px; }
#detail-backlinks h3 { font-size: 13px; margin: 0 0 6px; }
#backlinks-list { margin: 0; padding-left: 16px; }
#backlinks-list li { margin: 3px 0; }
#backlinks-list a { color: #3b82f6; cursor: pointer; text-decoration: none; }
#backlinks-list a:hover { text-decoration: underline; }
.dim { opacity: 0.15; }
</style>
</head>
<body>
<header>
  <div class="title">
    <strong id="bundle-name"></strong>
    <span class="muted">OKF Bundle</span>
  </div>
  <div class="controls">
    <input id="search" type="search" placeholder="Search…">
    <select id="filter-type"><option value="">All types</option></select>
    <select id="layout">
      <option value="cose">Force</option>
      <option value="concentric">Concentric</option>
      <option value="breadthfirst">Tree</option>
      <option value="circle">Circle</option>
      <option value="grid">Grid</option>
    </select>
    <button id="reset">Reset view</button>
  </div>
</header>
<main>
  <div id="graph"></div>
  <div id="detail">
    <div id="detail-empty"><p>Click a node to explore.</p></div>
    <div id="detail-content" hidden>
      <div class="detail-header">
        <span class="type-chip" id="detail-type"></span>
        <h1 id="detail-title"></h1>
        <div class="muted" id="detail-id"></div>
      </div>
      <dl class="frontmatter">
        <dt>Description</dt><dd id="detail-description"></dd>
        <dt>Resource</dt><dd id="detail-resource"></dd>
        <dt>Tags</dt><dd id="detail-tags"></dd>
      </dl>
      <div id="detail-body" class="markdown-body"></div>
      <div id="detail-backlinks" hidden>
        <h3>Referenced by</h3>
        <ul id="backlinks-list"></ul>
      </div>
    </div>
  </div>
</main>
<script>
window.BUNDLE_NAME = "OWOX_BUNDLE_NAME";
window.BUNDLE = OWOX_BUNDLE_JSON;
</script>
<script>
(function () {
  const bundle = window.BUNDLE;
  document.title = window.BUNDLE_NAME + " — OKF Viewer";
  document.getElementById("bundle-name").textContent = window.BUNDLE_NAME;

  const typeSelect = document.getElementById("filter-type");
  for (const t of bundle.types) {
    const opt = document.createElement("option");
    opt.value = t; opt.textContent = t;
    typeSelect.appendChild(opt);
  }

  const backlinks = {};
  for (const edge of bundle.edges) {
    const { source, target } = edge.data;
    (backlinks[target] = backlinks[target] || []).push(source);
  }

  const nodeIndex = {};
  for (const n of bundle.nodes) nodeIndex[n.data.id] = n.data;

  const cy = cytoscape({
    container: document.getElementById("graph"),
    elements: [...bundle.nodes, ...bundle.edges],
    style: [
      { selector: "node", style: {
          "background-color": "data(color)", "label": "data(label)",
          "color": "#0f172a", "font-size": 11,
          "text-valign": "bottom", "text-margin-y": 4,
          "text-wrap": "wrap", "text-max-width": 120,
          "width": "data(size)", "height": "data(size)",
          "border-width": 1, "border-color": "#0f172a" } },
      { selector: "node:selected", style: { "border-width": 3, "border-color": "#f59e0b" } },
      { selector: "edge", style: {
          "width": 1.5, "line-color": "#cbd5e1",
          "target-arrow-color": "#cbd5e1", "target-arrow-shape": "triangle",
          "curve-style": "bezier", "arrow-scale": 0.9 } },
      { selector: "edge:selected", style: {
          "line-color": "#f59e0b", "target-arrow-color": "#f59e0b", "width": 2.5 } },
      { selector: ".dim", style: { "opacity": 0.15 } },
    ],
    layout: { name: "cose", animate: false, padding: 30 },
    wheelSensitivity: 0.2,
  });

  cy.on("tap", "node", (evt) => showDetail(evt.target.id()));
  cy.on("tap", (evt) => { if (evt.target === cy) clearSelection(); });

  document.getElementById("layout").addEventListener("change", (e) => {
    cy.layout({ name: e.target.value, animate: false, padding: 30 }).run();
  });
  document.getElementById("reset").addEventListener("click", () => {
    cy.fit(null, 30); clearSelection();
  });
  document.getElementById("search").addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) { cy.elements().removeClass("dim"); return; }
    cy.nodes().forEach((n) => {
      const d = n.data();
      const hay = (d.label || "").toLowerCase() + " " + d.id.toLowerCase() + " " + (d.tags || []).join(" ").toLowerCase();
      n.toggleClass("dim", !hay.includes(q));
    });
    cy.edges().forEach((e) => {
      e.toggleClass("dim", e.source().hasClass("dim") || e.target().hasClass("dim"));
    });
  });
  document.getElementById("filter-type").addEventListener("change", (e) => {
    const t = e.target.value;
    if (!t) { cy.elements().removeClass("dim"); return; }
    cy.nodes().forEach((n) => n.toggleClass("dim", n.data("type") !== t));
    cy.edges().forEach((e) => {
      e.toggleClass("dim", e.source().hasClass("dim") || e.target().hasClass("dim"));
    });
  });

  function clearSelection() {
    cy.elements().unselect();
    document.getElementById("detail-empty").hidden = false;
    document.getElementById("detail-content").hidden = true;
  }

  function showDetail(conceptId) {
    const data = nodeIndex[conceptId];
    if (!data) return;
    cy.elements().unselect();
    const node = cy.getElementById(conceptId);
    if (node) node.select();

    document.getElementById("detail-empty").hidden = true;
    document.getElementById("detail-content").hidden = false;

    const chip = document.getElementById("detail-type");
    chip.textContent = data.type; chip.style.background = data.color;
    document.getElementById("detail-title").textContent = data.label;
    document.getElementById("detail-id").textContent = conceptId;
    document.getElementById("detail-description").textContent = data.description || "—";

    const resourceEl = document.getElementById("detail-resource");
    resourceEl.innerHTML = "";
    if (data.resource) {
      const a = document.createElement("a");
      a.href = data.resource; a.textContent = data.resource;
      a.target = "_blank"; a.rel = "noopener"; a.className = "external";
      resourceEl.appendChild(a);
    } else { resourceEl.textContent = "—"; }

    const tagsEl = document.getElementById("detail-tags");
    tagsEl.innerHTML = "";
    for (const t of (data.tags || [])) {
      const span = document.createElement("span");
      span.className = "tag"; span.textContent = t; tagsEl.appendChild(span);
    }
    if (!data.tags || !data.tags.length) tagsEl.textContent = "—";

    document.getElementById("detail-body").innerHTML =
      marked.parse(bundle.bodies[conceptId] || "", { breaks: false, gfm: true });

    const bl = backlinks[conceptId] || [];
    const blSection = document.getElementById("detail-backlinks");
    const blList = document.getElementById("backlinks-list");
    blList.innerHTML = "";
    blSection.hidden = !bl.length;
    for (const src of bl) {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.textContent = nodeIndex[src] ? nodeIndex[src].label : src;
      a.onclick = () => showDetail(src);
      li.appendChild(a); blList.appendChild(li);
    }
  }
})();
</script>
</body>
</html>
"""

_TYPE_COLORS = {
    "VIEW":      "#3b82f6",
    "SQL":       "#10b981",
    "CONNECTOR": "#f59e0b",
}
_STORAGE_COLOR = "#8b5cf6"


def render_viz_html(out_dir, project_folder, marts_with_docs, api_origin):
    nodes, edges, bodies, storage_map = [], [], {}, {}
    types_seen = set()

    for mart, doc in marts_with_docs:
        mart_id = mart.get("id", "")
        title = mart.get("title") or mart_id
        definition_type = mart.get("definitionType") or "Data Mart"
        storage = mart.get("storage") or {}
        storage_title = storage.get("title") or ""
        storage_type = storage.get("type") or ""
        description = (mart.get("description") or "").strip()
        short_desc = description.splitlines()[0][:200] if description else ""
        data_url = f"{api_origin}{DATA_NDJSON_PATH.format(id=mart_id)}"
        node_id = f"{project_folder}/{slugify(title, mart_id)}"
        tags = ["owox"] + ([storage_type.lower()] if storage_type else []) + ([definition_type.lower()] if definition_type else [])

        types_seen.add(definition_type)
        nodes.append({"data": {
            "id": node_id, "label": title, "type": definition_type,
            "description": short_desc, "resource": data_url,
            "tags": tags, "color": _TYPE_COLORS.get(definition_type, "#94a3b8"), "size": 32,
        }})
        bodies[node_id] = doc

        if storage_title and storage_title not in storage_map:
            storage_id = f"storage/{slugify(storage_title, 'storage')}"
            storage_map[storage_title] = storage_id
            nodes.append({"data": {
                "id": storage_id, "label": storage_title,
                "type": storage_type or "Storage", "description": "",
                "resource": "", "tags": ["storage"],
                "color": _STORAGE_COLOR, "size": 40,
            }})
            types_seen.add(storage_type or "Storage")
            bodies[storage_id] = ""

        if storage_title:
            edges.append({"data": {"source": node_id, "target": storage_map[storage_title]}})

    bundle = {"nodes": nodes, "edges": edges, "bodies": bodies, "types": sorted(types_seen)}
    html = (
        _VIZ_TEMPLATE
        .replace("OWOX_BUNDLE_NAME", project_folder)
        .replace("OWOX_BUNDLE_JSON", json.dumps(bundle, ensure_ascii=False))
    )
    with open(os.path.join(out_dir, "viz.html"), "w", encoding="utf-8") as fh:
        fh.write(html)


# --------------------------------------------------------------------------- #
# GitHub push (via git CLI)
# --------------------------------------------------------------------------- #
def _parse_repo(repo_str):
    """Split 'owner/name' or 'owner/name/path/to/folder' into (github_repo, subdir).
    Also accepts full GitHub URLs like 'https://github.com/owner/name/path'.
    The first two slash-delimited segments after the host are the GitHub repo;
    everything after is treated as the target subdirectory path inside that repo."""
    s = repo_str.strip().rstrip("/")
    if s.startswith("https://github.com/"):
        s = s[len("https://github.com/"):]
    elif s.startswith("http://github.com/"):
        s = s[len("http://github.com/"):]
    parts = s.split("/", 2)
    return "/".join(parts[:2]), (parts[2] if len(parts) > 2 else "")


def git_push(bundle_dir, repo, token, branch, commit_msg):
    if not shutil.which("git"):
        raise RuntimeError("git is not on PATH; cannot push.")

    github_repo, subdir = _parse_repo(repo)
    remote = f"https://x-access-token:{token}@github.com/{github_repo}.git"
    work = tempfile.mkdtemp(prefix="okf-push-")
    try:
        cloned = subprocess.run(
            ["git", "clone", "--depth", "1", "-b", branch, remote, work],
            capture_output=True, text=True
        ).returncode == 0
        if not cloned:
            subprocess.run(["git", "init", "-q", work], check=True)
            subprocess.run(["git", "-C", work, "remote", "add", "origin", remote], check=True)
            subprocess.run(["git", "-C", work, "checkout", "-q", "-b", branch], check=True)

        target = os.path.join(work, subdir) if subdir else work
        if os.path.isdir(target) and subdir:
            shutil.rmtree(target)  # replace prior export cleanly
        os.makedirs(target, exist_ok=True)  # create nested dirs if new
        shutil.copytree(bundle_dir, target, dirs_exist_ok=True)

        subprocess.run(["git", "-C", work, "add", "-A"], check=True)
        # Identity (harmless if already configured globally)
        subprocess.run(["git", "-C", work, "config", "user.email", "okf-bot@example.com"], check=True)
        subprocess.run(["git", "-C", work, "config", "user.name", "OKF Export"], check=True)

        if subprocess.run(["git", "-C", work, "diff", "--cached", "--quiet"]).returncode == 0:
            print("No changes to commit — bundle already up to date.")
            return
        subprocess.run(["git", "-C", work, "commit", "-q", "-m", commit_msg], check=True)
        subprocess.run(["git", "-C", work, "push", "-u", "origin", branch], check=True)
        print(f"Pushed OKF bundle to {repo} ({branch}/{subdir or '.'}).")
    finally:
        shutil.rmtree(work, ignore_errors=True)


# --------------------------------------------------------------------------- #
# Config validation
# --------------------------------------------------------------------------- #
def _validate_config(args, p):
    errors = []

    if not args.api_key:
        errors.append(
            "OWOX_API_KEY is missing.\n"
            "  Open .env and paste your key next to OWOX_API_KEY=\n"
            "  (Get it in OWOX: Project Settings → My API Keys → Create API Key)"
        )
    elif not args.api_key.strip().startswith("owox_key_"):
        errors.append(
            f"OWOX_API_KEY looks wrong — it must start with 'owox_key_' (got: '{args.api_key[:20]}...').\n"
            "  Make sure you copied the full key from OWOX."
        )

    if args.push:
        if not args.token:
            errors.append(
                "GITHUB_TOKEN is missing.\n"
                "  Open .env and paste your token next to GITHUB_TOKEN=\n"
                "  (Create one at GitHub → Settings → Developer settings → Personal access tokens)"
            )
        elif not (args.token.startswith("ghp_") or args.token.startswith("github_pat_")):
            errors.append(
                f"GITHUB_TOKEN looks wrong — expected it to start with 'ghp_' or 'github_pat_' "
                f"(got: '{args.token[:12]}...').\n"
                "  Make sure you copied the full token from GitHub."
            )

        if not args.repo:
            errors.append(
                "GITHUB_REPO is missing.\n"
                "  Open .env and set GITHUB_REPO=your-org/your-repo-name\n"
                "  To place the bundle in a subfolder: your-org/your-repo-name/path/to/folder"
            )
        else:
            github_repo, _ = _parse_repo(args.repo)
            parts = github_repo.split("/")
            if len(parts) != 2 or not parts[0] or not parts[1]:
                errors.append(
                    f"GITHUB_REPO must start with 'owner/repo-name' (got: '{args.repo}').\n"
                    "  Example: acme-corp/data-catalog\n"
                    "  With subfolder: acme-corp/data-catalog/okf/my-bundle"
                )

    if errors:
        msg = "\n\n".join(f"  ✗ {e}" for e in errors)
        p.error(f"\n\nConfiguration error(s) found:\n\n{msg}\n")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    _load_dotenv()
    p = argparse.ArgumentParser(description="Export OWOX data marts to an OKF bundle.")
    p.add_argument("--api-key", default=os.environ.get("OWOX_API_KEY"),
                   help="OWOX API key (owox_key_...). Defaults to $OWOX_API_KEY.")
    p.add_argument("--ids", default="", help="Comma-separated data-mart IDs (default: all).")
    p.add_argument("--out", default="bundels", help="Output directory (default: bundels).")
    p.add_argument("--sample-rows", type=int, default=0,
                   help="Embed first N rows as preview per mart (default: 0 = none).")
    # default true unless SHARED_ONLY=false
    _shared_default = os.environ.get("SHARED_ONLY", "true").lower() != "false"
    p.add_argument("--shared-only", dest="shared_only", action="store_true", default=_shared_default,
                   help="Export only data marts available for reporting (default: on).")
    p.add_argument("--no-shared-only", dest="shared_only", action="store_false",
                   help="Export all data marts regardless of reporting availability.")
    # Viz
    _viz_default = os.environ.get("VIZ", "true").lower() != "false"
    p.add_argument("--viz", dest="viz", action="store_true", default=_viz_default,
                   help="Generate viz.html interactive knowledge graph (default: on, $VIZ).")
    p.add_argument("--no-viz", dest="viz", action="store_false",
                   help="Skip viz.html generation.")
    p.add_argument("--folder", default=os.environ.get("BUNDLE_FOLDER"),
                   help="Override the bundle subfolder name (default: slugified project title).")
    p.add_argument("--title", default=os.environ.get("BUNDLE_TITLE"),
                   help="Override the bundle display title (default: the OWOX project title).")
    # GitHub
    p.add_argument("--push", action="store_true", help="Push the bundle to GitHub.")
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPO"),
                   help="Target as owner/repo-name or owner/repo-name/path/to/folder ($GITHUB_REPO).")
    p.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token ($GITHUB_TOKEN).")
    p.add_argument("--branch", default="main", help="Branch to push (default: main).")
    p.add_argument("--commit-msg", default="Update OWOX OKF bundle", help="Commit message.")
    args = p.parse_args()

    _validate_config(args, p)

    print("Parsing API key and exchanging for an access token...")
    api_origin, api_key_id, api_key_secret = parse_api_key(args.api_key)
    token = exchange_for_token(api_origin, api_key_id, api_key_secret)
    headers = auth_headers(token, api_key_id)
    project_title = project_title_from_token(token)
    display_title = args.title or project_title or "Data Marts"
    project_folder = slugify(args.folder, "data-marts") if args.folder else slugify(project_title, "data-marts")
    print(f"  origin: {api_origin}")
    print(f"  project: {project_title or '(unknown)'} → folder: {project_folder}")

    if args.ids.strip():
        ids = [i.strip() for i in args.ids.split(",") if i.strip()]
    else:
        print("Listing data marts...")
        all_marts = list_data_marts(api_origin, headers)
        if args.shared_only:
            filtered = [m for m in all_marts if m.get("availableForReporting")]
            skipped = len(all_marts) - len(filtered)
            if skipped:
                print(f"  Skipped {skipped} data mart(s) not available for reporting "
                      f"(pass --no-shared-only to include them).")
            all_marts = filtered
        ids = [m["id"] for m in all_marts]
    print(f"  {len(ids)} data mart(s) to export.")

    marts_with_docs = []
    for mart_id in ids:
        print(f"Fetching {mart_id} ...")
        mart = get_data_mart(api_origin, headers, mart_id)
        sample = fetch_sample_rows(api_origin, headers, mart_id, args.sample_rows)
        marts_with_docs.append((mart, sample))

    # Render docs after all marts are fetched so FK cross-references can be resolved
    path_lookup_pre = _build_path_lookup([(m, None) for m, _ in marts_with_docs])
    marts_with_docs = [
        (mart, render_data_mart_doc(mart, api_origin, sample,
                                    fk=_fk_lookup(mart, path_lookup_pre)))
        for mart, sample in marts_with_docs
    ]

    if os.path.isdir(args.out):
        shutil.rmtree(args.out)
    count = write_bundle(args.out, marts_with_docs, project_folder, display_title)
    print(f"Wrote OKF bundle to {args.out}/{project_folder}/ ({count} concept docs).")

    if args.viz:
        render_viz_html(args.out, project_folder, marts_with_docs, api_origin)
        print(f"Wrote viz.html to {args.out}/viz.html")

    if args.push:
        if not args.repo or not args.token:
            p.error("--push requires --repo and --token (or $GITHUB_REPO/$GITHUB_TOKEN).")
        print(f"Pushing to GitHub {args.repo} ...")
        git_push(args.out, args.repo, args.token, args.branch, args.commit_msg)


if __name__ == "__main__":
    main()

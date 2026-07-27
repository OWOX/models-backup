"""Unit tests for export.py. Run: python3 -m unittest discover -s tools/odm-to-okf-export -v"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SPEC = importlib.util.spec_from_file_location("export_mod", os.path.join(_HERE, "export.py"))
export = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(export)


def load_fixture(name):
    with open(os.path.join(_HERE, "fixtures", name), encoding="utf-8") as fh:
        return json.load(fh)


class BuildJoinIndexTests(unittest.TestCase):
    def setUp(self):
        self.graph = load_fixture("graph_orders.json")

    def test_indexes_direct_edges_by_path(self):
        idx = export.build_join_index(self.graph, "mart-orders")
        self.assertEqual(sorted(idx), ["customers", "products"])

    def test_keeps_non_matching_field_names(self):
        idx = export.build_join_index(self.graph, "mart-orders")
        self.assertEqual(idx["products"], [("sku", "product_code")])

    def test_skips_cycle_stubs_and_foreign_edges(self):
        idx = export.build_join_index(self.graph, "mart-orders")
        self.assertNotIn("orders", idx)

    def test_skips_foreign_source_mart(self):
        idx = export.build_join_index(self.graph, "mart-orders")
        self.assertNotIn("regions", idx)

    def test_skips_dotted_multi_hop_path(self):
        idx = export.build_join_index(self.graph, "mart-orders")
        self.assertNotIn("customers.region", idx)

    def test_empty_graph_is_empty_index(self):
        self.assertEqual(export.build_join_index({"nodes": []}, "mart-orders"), {})
        self.assertEqual(export.build_join_index(None, "mart-orders"), {})


class RenderJoinsTests(unittest.TestCase):
    def setUp(self):
        self.mart = {
            "id": "mart-orders",
            "title": "Orders",
            "schema": {"fields": [
                {"name": "order_id", "type": "STRING", "isPrimaryKey": True},
                {"name": "customer_id", "type": "STRING"},
                {"name": "sku", "type": "STRING"},
            ]},
            "blendedFieldsConfig": {"sources": [
                {"path": "customers", "alias": "Customers", "fields": {}},
                {"path": "products", "alias": "Products", "fields": {}},
            ]},
        }
        self.path_lookup = {
            "customers": ("Customers", "customers.md", ["customer_id"]),
            "products": ("Products", "products.md", ["product_code"]),
        }
        self.index = export.build_join_index(load_fixture("graph_orders.json"), "mart-orders")

    def test_non_matching_names_get_keys_from_the_api(self):
        out = export._render_joins_section(self.mart, self.path_lookup, self.index)
        self.assertIn("- [Products](./products.md) — `sku = product_code`", out)

    def test_matching_names_still_render(self):
        out = export._render_joins_section(self.mart, self.path_lookup, self.index)
        self.assertIn("- [Customers](./customers.md) — `customer_id = customer_id`", out)

    def test_falls_back_to_name_matching_without_index(self):
        out = export._render_joins_section(self.mart, self.path_lookup, {})
        self.assertIn("- [Customers](./customers.md) — `customer_id = customer_id`", out)
        self.assertIn("- [Products](./products.md)\n", out)

    def test_source_order_is_preserved(self):
        out = export._render_joins_section(self.mart, self.path_lookup, self.index)
        self.assertLess(out.index("Customers"), out.index("Products"))

    def test_multi_condition_join_renders_all_pairs_comma_separated(self):
        # Composite keys are real (a live OWOX mart has a two-field primary key), so a
        # join_index entry with more than one pair must render every pair, in order,
        # comma-separated — not just the first one.
        mart = {
            "id": "mart-orders",
            "title": "Orders",
            "schema": {"fields": [
                {"name": "order_id", "type": "STRING", "isPrimaryKey": True},
                {"name": "warehouse_id", "type": "STRING"},
                {"name": "region_code", "type": "STRING"},
            ]},
            "blendedFieldsConfig": {"sources": [
                {"path": "warehouses", "alias": "Warehouses", "fields": {}},
            ]},
        }
        path_lookup = {
            "warehouses": ("Warehouses", "warehouses.md", ["warehouse_id", "region_code"]),
        }
        join_index = {
            "warehouses": [("warehouse_id", "warehouse_id"), ("region_code", "region_code")],
        }
        out = export._render_joins_section(mart, path_lookup, join_index)
        self.assertIn(
            "- [Warehouses](./warehouses.md) — `warehouse_id = warehouse_id`, `region_code = region_code`",
            out,
        )

    def test_matched_but_keyless_source_renders_bare_link(self):
        # The source's path IS in path_lookup (it's a real, matched join target), but there's
        # no join_index entry for it and no local column name-matches the target's primary
        # key — so it must fall back to a bare link with no " — " suffix.
        mart = {
            "id": "mart-orders",
            "title": "Orders",
            "schema": {"fields": [
                {"name": "order_id", "type": "STRING", "isPrimaryKey": True},
            ]},
            "blendedFieldsConfig": {"sources": [
                {"path": "warehouses", "alias": "Warehouses", "fields": {}},
            ]},
        }
        path_lookup = {
            "warehouses": ("Warehouses", "warehouses.md", ["warehouse_id"]),
        }
        out = export._render_joins_section(mart, path_lookup, {})
        self.assertIn("- [Warehouses](./warehouses.md)\n", out)
        self.assertNotIn(" — ", out)


class FkLookupTests(unittest.TestCase):
    def setUp(self):
        self.mart = {
            "id": "mart-orders",
            "blendedFieldsConfig": {"sources": [
                {"path": "customers", "alias": "Customers", "fields": {}},
                {"path": "products", "alias": "Products", "fields": {}},
            ]},
        }
        self.path_lookup = {
            "customers": ("Customers", "customers.md", ["customer_id"]),
            "products": ("Products", "products.md", ["product_code"]),
        }
        self.index = export.build_join_index(load_fixture("graph_orders.json"), "mart-orders")

    def test_annotates_the_actual_source_column(self):
        fk = export._fk_lookup(self.mart, self.path_lookup, self.index)
        self.assertEqual(fk["sku"], ("Products", "products.md"))

    def test_does_not_annotate_the_target_pk_name(self):
        fk = export._fk_lookup(self.mart, self.path_lookup, self.index)
        self.assertNotIn("product_code", fk)

    def test_falls_back_to_pk_names_without_index(self):
        fk = export._fk_lookup(self.mart, self.path_lookup, {})
        self.assertEqual(fk["customer_id"], ("Customers", "customers.md"))

    def test_composite_key_annotates_every_source_column(self):
        # Composite keys are real (a live OWOX mart has a two-field primary key), so a
        # join_index entry with more than one pair must annotate every source column.
        mart = {
            "id": "mart-warehouses",
            "blendedFieldsConfig": {"sources": [
                {"path": "warehouses", "alias": "Warehouses", "fields": {}},
            ]},
        }
        path_lookup = {
            "warehouses": ("Warehouses", "warehouses.md", ["warehouse_id", "region_code"]),
        }
        join_index = {
            "warehouses": [("warehouse_id", "warehouse_id"), ("region_code", "region_code")],
        }
        fk = export._fk_lookup(mart, path_lookup, join_index)
        # Both source columns should be annotated with the target's (title, filename)
        self.assertEqual(fk["warehouse_id"], ("Warehouses", "warehouses.md"))
        self.assertEqual(fk["region_code"], ("Warehouses", "warehouses.md"))


class RenamedMartJoinTests(unittest.TestCase):
    """Joins must survive a mart being renamed after its relationships were created.

    OWOX freezes the alias a relationship is created with, so a mart created as
    'Orders (E-Commerce)' and later renamed to '🥈 Orders' still carries the alias
    `orders_e_commerce`. Matching that against a key derived from the CURRENT title
    ('orders') misses, and the join used to degrade to plain text — a link the reader
    can't follow and, more importantly, an edge that disappears from the model graph
    when the bundle is imported. Resolution must go through the target mart's id.
    """

    def setUp(self):
        self.graph = {"nodes": [{
            "aliasPath": "products_e_commerce",
            "isCycleStub": False,
            "relationship": {
                "id": "rel-1",
                "sourceDataMart": {"id": "mart-orders"},
                "targetDataMart": {"id": "mart-products"},
                "targetAlias": "products_e_commerce",
                "joinConditions": [{"sourceFieldName": "sku",
                                    "targetFieldName": "product_code"}],
            },
        }]}
        self.mart = {
            "id": "mart-orders",
            "title": "🥈 Orders",
            "schema": {"fields": [{"name": "sku", "type": "STRING"}]},
            "blendedFieldsConfig": {"sources": [
                {"path": "products_e_commerce", "alias": "Products", "fields": {}},
            ]},
        }
        self.marts = [({"id": "mart-products", "title": "🥈 Products",
                        "schema": {"fields": [{"name": "product_code", "type": "STRING",
                                               "isPrimaryKey": True}]}}, None)]

    def test_target_index_maps_alias_path_to_target_id(self):
        idx = export.build_target_index(self.graph, "mart-orders")
        self.assertEqual(idx, {"products_e_commerce": "mart-products"})

    def test_target_index_keeps_keyless_edges(self):
        # build_join_index drops edges with no joinConditions, but a keyless edge is
        # still a real link and must still resolve to a target.
        graph = {"nodes": [{
            "aliasPath": "pages_e_commerce", "isCycleStub": False,
            "relationship": {"id": "rel-2",
                             "sourceDataMart": {"id": "mart-orders"},
                             "targetDataMart": {"id": "mart-pages"},
                             "joinConditions": []},
        }]}
        self.assertEqual(export.build_join_index(graph, "mart-orders"), {})
        self.assertEqual(export.build_target_index(graph, "mart-orders"),
                         {"pages_e_commerce": "mart-pages"})

    def test_renamed_target_still_renders_a_link(self):
        out = export._render_joins_section(
            self.mart, export._build_path_lookup(self.marts),
            export.build_join_index(self.graph, "mart-orders"),
            export.build_target_index(self.graph, "mart-orders"),
            export._build_id_lookup(self.marts))
        self.assertIn("- [Products](./products.md) — `sku = product_code`", out)

    def test_id_resolution_wins_when_both_path_and_alias_are_stale(self):
        # The hard case, and the reason resolution must go through the id: the mart was
        # renamed, so NEITHER the frozen path nor the stored display alias matches the
        # current title. Without the target index this is the unlinked line that broke
        # the imported model graph; with it, the join resolves.
        mart = dict(self.mart, blendedFieldsConfig={"sources": [
            {"path": "products_e_commerce", "alias": "Products (E-Commerce)", "fields": {}}]})
        path_lookup = export._build_path_lookup(self.marts)
        join_index = export.build_join_index(self.graph, "mart-orders")

        without = export._render_joins_section(mart, path_lookup, join_index)
        self.assertIn("- Products (E-Commerce)\n", without)
        self.assertNotIn("](./products.md)", without)

        with_ids = export._render_joins_section(
            mart, path_lookup, join_index,
            export.build_target_index(self.graph, "mart-orders"),
            export._build_id_lookup(self.marts))
        self.assertIn("- [Products (E-Commerce)](./products.md) — `sku = product_code`",
                      with_ids)

    def test_blend_only_source_resolves_via_display_alias(self):
        # A blendedFieldsConfig source with no relationship edge at all: there is no id
        # to resolve through, so the display alias is the last resort.
        mart = dict(self.mart, blendedFieldsConfig={"sources": [
            {"path": "products_e_commerce", "alias": "Products", "fields": {}}]})
        out = export._render_joins_section(
            mart, export._build_path_lookup(self.marts), {}, {},
            export._build_id_lookup(self.marts))
        self.assertIn("- [Products](./products.md)", out)

    def test_related_mart_without_blend_config_still_gets_a_join(self):
        # A plain lookup edge is never written into blendedFieldsConfig, so relying on
        # the blend config alone silently drops the link (live case: Unified Ad Spend →
        # Traffic Sources).
        mart = {"id": "mart-orders", "title": "🥈 Orders",
                "schema": {"fields": [{"name": "sku", "type": "STRING"}]},
                "blendedFieldsConfig": None}
        out = export._render_joins_section(
            mart, export._build_path_lookup(self.marts),
            export.build_join_index(self.graph, "mart-orders"),
            export.build_target_index(self.graph, "mart-orders"),
            export._build_id_lookup(self.marts))
        self.assertIn("- [🥈 Products](./products.md) — `sku = product_code`", out)

    def test_no_relationships_and_no_blend_config_stays_empty(self):
        mart = {"id": "mart-solo", "title": "Solo", "blendedFieldsConfig": None}
        self.assertEqual(export._render_joins_section(mart, {}, {}, {}, {}), "")

    def test_fk_note_resolves_through_the_renamed_target(self):
        fk = export._fk_lookup(
            self.mart, export._build_path_lookup(self.marts),
            export.build_join_index(self.graph, "mart-orders"),
            export.build_target_index(self.graph, "mart-orders"),
            export._build_id_lookup(self.marts))
        self.assertEqual(fk["sku"], ("🥈 Products", "products.md"))


class StorageFilterTests(unittest.TestCase):
    def setUp(self):
        self.storages = [
            {"id": "st-1", "title": "BigQuery [Common]", "type": "GOOGLE_BIGQUERY"},
            {"id": "st-2", "title": "BQ [Marketing]", "type": "GOOGLE_BIGQUERY"},
        ]
        self.marts = [
            {"id": "m1", "storage": {"title": "BigQuery [Common]", "type": "GOOGLE_BIGQUERY"}},
            {"id": "m2", "storage": {"title": "BQ [Marketing]", "type": "GOOGLE_BIGQUERY"}},
        ]

    def test_keeps_only_marts_of_that_storage(self):
        kept, needs_detail = export.filter_marts_by_storage(self.marts, self.storages, "st-1")
        self.assertEqual([m["id"] for m in kept], ["m1"])
        self.assertFalse(needs_detail)

    def test_unknown_storage_id_is_an_error(self):
        with self.assertRaises(SystemExit):
            export.filter_marts_by_storage(self.marts, self.storages, "st-nope")

    def test_ambiguous_title_type_pair_requests_detail_fallback(self):
        storages = self.storages + [{"id": "st-3", "title": "BigQuery [Common]",
                                     "type": "GOOGLE_BIGQUERY"}]
        kept, needs_detail = export.filter_marts_by_storage(self.marts, storages, "st-1")
        self.assertTrue(needs_detail)
        self.assertEqual([m["id"] for m in kept], ["m1"])


class CollectBundlesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self._write("e-commerce", "E-Commerce", ["a.md", "b.md"])
        self._write("saas", "SaaS", ["x.md"])

    def _write(self, folder, title, marts):
        d = os.path.join(self.tmp, folder)
        os.makedirs(d)
        rows = "\n".join(f"| [{m[:-3]}](./{m}) | VIEW | GOOGLE_BIGQUERY |" for m in marts)
        with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as fh:
            fh.write(f'---\ntype: "index"\ntitle: "{title}"\n---\n\n# {title}\n\n'
                     f"| Data Mart | Type | Storage |\n|---|---|---|\n{rows}\n")
        for m in marts:
            with open(os.path.join(d, m), "w", encoding="utf-8") as fh:
                fh.write(f'---\ntype: "OWOX Data Mart"\ntitle: "{m[:-3]}"\n---\n\n# {m[:-3]}\n')

    def test_lists_every_bundle_sorted(self):
        found = export.collect_bundles(self.tmp)
        self.assertEqual([f for f, _, _ in found], ["e-commerce", "saas"])

    def test_reads_title_and_counts_concepts(self):
        found = dict((f, (t, n)) for f, t, n in export.collect_bundles(self.tmp))
        self.assertEqual(found["e-commerce"], ("E-Commerce", 2))
        self.assertEqual(found["saas"], ("SaaS", 1))

    def test_ignores_files_and_folders_without_index(self):
        os.makedirs(os.path.join(self.tmp, "not-a-bundle"))
        with open(os.path.join(self.tmp, "viz.html"), "w") as fh:
            fh.write("x")
        self.assertEqual([f for f, _, _ in export.collect_bundles(self.tmp)],
                         ["e-commerce", "saas"])


class BuildVizDataTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        for folder, title, mart in (("e-commerce", "E-Commerce", "orders"),
                                    ("saas", "SaaS", "account")):
            d = os.path.join(self.tmp, folder)
            os.makedirs(d)
            with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as fh:
                fh.write(f'---\ntype: "index"\ntitle: "{title}"\n---\n\n# {title}\n')
            with open(os.path.join(d, f"{mart}.md"), "w", encoding="utf-8") as fh:
                fh.write(
                    f'---\ntype: "OWOX Data Mart"\ntitle: "{mart.title()}"\n'
                    f'description: "Docs for {mart}."\n'
                    f'resource: "https://app.owox.com/x.ndjson"\n'
                    f'tags: ["owox", "view"]\n---\n\n'
                    f"# {mart.title()}\n\n## Overview\n\n"
                    f"- **ID:** `id-{mart}`\n- **Status:** PUBLISHED\n"
                    f"- **Definition type:** VIEW\n"
                    f"- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)\n")

    def test_lists_all_bundles(self):
        data = export.build_viz_data(self.tmp)
        self.assertEqual(data["bundles"], ["e-commerce", "saas"])

    def test_nodes_are_tagged_with_their_bundle(self):
        data = export.build_viz_data(self.tmp)
        by_id = {n["data"]["id"]: n["data"] for n in data["nodes"]}
        self.assertEqual(by_id["saas/account"]["bundle"], "saas")
        self.assertEqual(by_id["saas/account"]["type"], "VIEW")

    def test_storage_nodes_are_per_bundle(self):
        data = export.build_viz_data(self.tmp)
        ids = {n["data"]["id"] for n in data["nodes"]}
        self.assertIn("e-commerce/storage/bigquery-common", ids)
        self.assertIn("saas/storage/bigquery-common", ids)

    def test_edges_link_mart_to_its_own_bundle_storage(self):
        data = export.build_viz_data(self.tmp)
        pairs = {(e["data"]["source"], e["data"]["target"]) for e in data["edges"]}
        self.assertIn(("saas/account", "saas/storage/bigquery-common"), pairs)

    def test_body_is_the_markdown_file_content(self):
        data = export.build_viz_data(self.tmp)
        self.assertIn("## Overview", data["bodies"]["saas/account"])

    def test_mart_doc_without_overview_section(self):
        # Test graceful degradation when a mart doc has valid frontmatter but no ## Overview section
        d = os.path.join(self.tmp, "e-commerce")
        with open(os.path.join(d, "no_overview.md"), "w", encoding="utf-8") as fh:
            fh.write(
                f'---\ntype: "OWOX Data Mart"\ntitle: "No Overview"\n'
                f'description: "Mart without overview."\n---\n\n'
                f"# No Overview\n\n"
                f"Just some content here.\n")
        data = export.build_viz_data(self.tmp)
        by_id = {n["data"]["id"]: n["data"] for n in data["nodes"]}
        # Node should exist even without ## Overview section
        self.assertIn("e-commerce/no_overview", by_id)
        # Definition type should fall back to "Data Mart" when not in overview
        self.assertEqual(by_id["e-commerce/no_overview"]["type"], "Data Mart")

    def test_mart_doc_without_frontmatter(self):
        # Test graceful degradation when a mart doc has no frontmatter at all
        d = os.path.join(self.tmp, "saas")
        with open(os.path.join(d, "no_frontmatter.md"), "w", encoding="utf-8") as fh:
            fh.write(
                f"# No Frontmatter\n\n"
                f"This document starts directly with a heading.\n"
                f"- **Definition type:** VIEW\n"
                f"- **Storage:** BigQuery (GOOGLE_BIGQUERY)\n")
        data = export.build_viz_data(self.tmp)
        by_id = {n["data"]["id"]: n["data"] for n in data["nodes"]}
        # Node should exist even without frontmatter
        self.assertIn("saas/no_frontmatter", by_id)
        # Label should fall back to filename stem when no title in frontmatter
        self.assertEqual(by_id["saas/no_frontmatter"]["label"], "no_frontmatter")


class UniversalOkfFormatTests(unittest.TestCase):
    def test_render_frontmatter_block_scalar_roundtrips(self):
        import yaml  # test-only; exporter runtime stays stdlib
        from export import render_frontmatter
        desc = "Para line one.\nPara line two.\n\n**Example questions this mart can answer:**\n- Q1?\n- Q2?"
        fm = render_frontmatter({"type": "OWOX Data Mart", "title": "Customer", "description": desc,
                                 "tags": ["owox"]})
        self.assertIn("description: |", fm)
        parsed = yaml.safe_load(fm.replace("---\n", "", 1).rsplit("\n---", 1)[0])
        self.assertTrue(parsed["description"].startswith("Para line one."))
        self.assertIn("Example questions", parsed["description"])
        self.assertEqual(parsed["tags"], ["owox"])

    def test_data_mart_doc_universal_shape(self):
        from export import render_data_mart_doc
        mart = {"id": "M1", "title": "Customer", "description": "Full desc line one.\n\nMore.",
                "definitionType": "VIEW", "status": "PUBLISHED",
                "storage": {"type": "GOOGLE_BIGQUERY", "title": "BigQuery"},
                "schema": {"fields": [{"name": "customer_id", "type": "STRING", "isPrimaryKey": True,
                                       "description": "PK."}]}}
        doc = render_data_mart_doc(mart, "https://app.owox.com", None)
        self.assertNotIn("resource:", doc)
        self.assertIn('tags: ["owox"]', doc)
        self.assertNotIn("## Overview", doc)
        self.assertNotIn("Data endpoint", doc)
        self.assertNotIn("Status:", doc)
        fm = doc.split("---", 2)[1]
        # full description in frontmatter (block scalar for multi-line) — canvas import reads it verbatim
        self.assertIn("description: |", fm)
        self.assertIn("Full desc line one.", fm)
        self.assertIn("More.", fm)
        self.assertNotIn("# Customer", doc)  # no duplicated title heading in the body

    def test_index_table_single_column(self):
        from export import write_bundle
        import tempfile as _tempfile
        with _tempfile.TemporaryDirectory() as d:
            marts = [({"id": "M1", "title": "Customer", "definitionType": "VIEW",
                       "storage": {"type": "GOOGLE_BIGQUERY"},
                       "schema": {"fields": [{"name": "customer_id"}]}}, "# Customer\n")]
            write_bundle(d, marts, "finance", "Finance")
            idx = open(os.path.join(d, "finance", "index.md"), encoding="utf-8").read()
        self.assertIn("| Data Mart | Fields |", idx)
        self.assertNotIn("Type", idx)
        self.assertNotIn("Storage", idx)
        self.assertNotIn("GOOGLE_BIGQUERY", idx)
        self.assertIn("[Customer](./customer.md) | 1 |", idx)

    def test_render_frontmatter_block_scalar_leading_space_is_safe(self):
        import yaml
        from export import render_frontmatter
        fm = render_frontmatter({"type": "OWOX Data Mart", "title": "X",
                                 "description": " Leading space first line.\nSecond line.", "tags": ["owox"]})
        parsed = yaml.safe_load(fm.replace("---\n", "", 1).rsplit("\n---", 1)[0])
        self.assertIn("Leading space first line.", parsed["description"])
        self.assertIn("Second line.", parsed["description"])

    def test_index_uses_project_description(self):
        from export import write_bundle
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            marts = [({"id": "M1", "title": "Customer"}, "# Customer\n")]
            write_bundle(d, marts, "finance", "Finance",
                         project_description="A lending business.\n\n**Example questions this model can answer:**\n- Q?")
            idx = open(os.path.join(d, "finance", "index.md"), encoding="utf-8").read()
        fm = idx.split("---", 2)[1]
        self.assertNotIn("description: |", fm)
        self.assertIn('description: "A lending business."', fm)
        self.assertIn("A lending business.", idx)
        self.assertNotIn("Index of exported OWOX data marts.", idx)


def test_read_preserved_regions_captures_after_block():
    from export import read_preserved_regions, GEN_START, GEN_END
    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "index.md")
        open(p, "w", encoding="utf-8").write(
            f"---\ntype: index\n---\n\n{GEN_START}\n# Finance\n{GEN_END}\n\n## Diagram\n![ERD](./erd.png)\n")
        before, after = read_preserved_regions(p)
    assert before == ""
    assert "## Diagram" in after and "![ERD](./erd.png)" in after

def test_read_preserved_regions_none_without_sentinels():
    from export import read_preserved_regions
    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "index.md")
        open(p, "w", encoding="utf-8").write("---\ntype: index\n---\n\n# Finance\n\n![ERD](./erd.png)\n")
        assert read_preserved_regions(p) == ("", "")

def test_write_bundle_preserves_manual_tail():
    from export import write_bundle, GEN_START, GEN_END
    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        marts = [({"id": "M1", "title": "Customer"}, "# Customer\n")]
        write_bundle(d, marts, "finance", "Finance",
                     preserved_regions=("", "## Diagram\n![ERD](./erd.png)"))
        idx = open(os.path.join(d, "finance", "index.md"), encoding="utf-8").read()
    assert GEN_START in idx and GEN_END in idx
    assert idx.index(GEN_END) < idx.index("## Diagram")   # manual tail after the block
    assert "![ERD](./erd.png)" in idx


def test_split_description_marker_present():
    from export import split_description
    desc = ("Intro line one wraps\nto two lines.\n\n**Example questions this mart can answer:**\n"
            "- Q one?\n- Q two?\n- Q three?")
    intro, qs = split_description(desc)
    assert intro == "Intro line one wraps\nto two lines."
    assert qs == ["Q one?", "Q two?", "Q three?"]

def test_split_description_no_marker():
    from export import split_description
    intro, qs = split_description("Just a plain description.")
    assert intro == "Just a plain description." and qs == []

def test_data_mart_doc_full_description_and_example_questions():
    import yaml
    from export import render_data_mart_doc
    mart = {"id": "M1", "title": "Marketing Spend",
            "description": ("Marketing investment by channel. It funds acquisition.\n\n"
                            "**Example questions this mart can answer:**\n- Q1?\n- Q2?\n- Q3?"),
            "schema": {"fields": [{"name": "spend_id", "type": "STRING", "isPrimaryKey": True}]}}
    doc = render_data_mart_doc(mart, "https://app.owox.com", None)
    fm = doc.split("---", 2)[1]
    body = doc.split("---", 2)[2]
    # FULL description (both sentences) in frontmatter — canvas import reads it verbatim
    assert yaml.safe_load(fm)["description"].strip() == "Marketing investment by channel. It funds acquisition."
    # no duplicated title heading; questions under their own heading AFTER the schema
    assert "# Marketing Spend" not in doc
    assert "# Example Questions" in body
    assert body.index("# Schema") < body.index("# Example Questions")
    assert "- Q1?" in body and "- Q3?" in body
    assert "Marketing investment by channel." not in body
    assert "**Example questions this mart can answer:**" not in doc  # marker stripped

def test_index_fields_column_and_example_questions():
    import yaml
    from export import write_bundle
    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        marts = [({"id": "M1", "title": "Account",
                   "schema": {"fields": [{"name": "a"}, {"name": "b"}, {"name": "c"}]}}, "# Account\n")]
        write_bundle(d, marts, "saas", "SaaS",
                     project_description="A SaaS business. It recurs.\n\n**Example questions this model can answer:**\n- Q1?")
        idx = open(os.path.join(d, "saas", "index.md"), encoding="utf-8").read()
    fm = idx.split("---", 2)[1]
    body = idx.split("---", 2)[2]
    assert yaml.safe_load(fm)["description"].strip() == "A SaaS business. It recurs."   # full, not one sentence
    assert "| Data Mart | Fields |" in idx
    assert "| [Account](./account.md) | 3 |" in idx
    assert "# SaaS" not in idx              # no duplicated title heading in the body
    assert "# Example Questions" in body and "- Q1?" in body
    assert idx.index("| Data Mart | Fields |") < idx.index("# Example Questions")  # questions under the table
    assert "A SaaS business." not in body   # description not duplicated in the body


def _frontmatter_keys(fm_text):
    """Ordered top-level frontmatter keys (ignoring indented block-scalar/list body)."""
    keys = []
    for line in fm_text.splitlines():
        if line and not line[0].isspace():
            key = line.split(":", 1)[0].strip()
            if key:
                keys.append(key)
    return keys


def test_data_mart_frontmatter_type_sits_between_tags_and_timestamp():
    from export import render_data_mart_doc
    mart = {"id": "M1", "title": "Customer", "description": "One sentence.",
            "schema": {"fields": [{"name": "customer_id", "type": "STRING", "isPrimaryKey": True}]}}
    doc = render_data_mart_doc(mart, "https://app.owox.com", None)
    fm = doc.split("---", 2)[1]
    keys = _frontmatter_keys(fm)
    assert keys.index("tags") < keys.index("type") < keys.index("timestamp")
    assert keys.index("title") < keys.index("type")   # type is no longer first


def test_index_authors_are_a_clickable_body_line_under_the_table():
    from export import write_bundle
    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        marts = [({"id": "M1", "title": "Customer", "schema": {"fields": [{"name": "a"}]}}, "# Customer\n")]
        write_bundle(d, marts, "finance", "Finance", project_description="A lending business.")
        idx = open(os.path.join(d, "finance", "index.md"), encoding="utf-8").read()
    fm = idx.split("---", 2)[1]
    body = idx.split("---", 2)[2]
    # authors are NOT in the frontmatter (GitHub renders those as plain text, not links)
    assert "authors" not in _frontmatter_keys(fm)
    assert _frontmatter_keys(fm).index("tags") < _frontmatter_keys(fm).index("type") \
        < _frontmatter_keys(fm).index("timestamp")
    # authors are a clickable markdown line in the body, between the frontmatter table
    # and the Data Mart table
    assert "**Authors:** [Vlad Flaks](https://github.com/vladflaks)" in body
    assert "[Rus Obolonsky](https://github.com/Obolrus)" in body
    assert body.index("**Authors:**") < body.index("| Data Mart | Fields |")


def test_index_canvas_cta_rendered_only_with_bundle_url():
    from export import write_bundle, CANVAS_MODEL_URL_PREFIX
    import tempfile, os
    url = "https://github.com/OWOX/models/tree/main/bundles/finance"
    with tempfile.TemporaryDirectory() as d:
        marts = [({"id": "M1", "title": "Customer", "schema": {"fields": [{"name": "a"}]}}, "# Customer\n")]
        write_bundle(d, marts, "finance", "Finance",
                     project_description="A lending business.\n\n"
                     "**Example questions this model can answer:**\n- Q1?",
                     bundle_url=url)
        with_cta = open(os.path.join(d, "finance", "index.md"), encoding="utf-8").read()
        write_bundle(d, marts, "nocta", "NoCTA", project_description="A lending business.")
        without_cta = open(os.path.join(d, "nocta", "index.md"), encoding="utf-8").read()
    assert "Explore on canvas" in with_cta
    assert f"{CANVAS_MODEL_URL_PREFIX}{url}" in with_cta
    # CTA comes after the example questions
    assert with_cta.index("# Example Questions") < with_cta.index("# Explore this model")
    assert "Explore on canvas" not in without_cta


if __name__ == "__main__":
    unittest.main()

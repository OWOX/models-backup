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


if __name__ == "__main__":
    unittest.main()

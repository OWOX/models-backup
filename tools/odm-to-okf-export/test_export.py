"""Unit tests for export.py. Run: python3 -m unittest discover -s tools/odm-to-okf-export -v"""
import importlib.util
import json
import os
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


if __name__ == "__main__":
    unittest.main()

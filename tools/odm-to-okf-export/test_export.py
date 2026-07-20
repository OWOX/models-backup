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

    def test_empty_graph_is_empty_index(self):
        self.assertEqual(export.build_join_index({"nodes": []}, "mart-orders"), {})
        self.assertEqual(export.build_join_index(None, "mart-orders"), {})


if __name__ == "__main__":
    unittest.main()

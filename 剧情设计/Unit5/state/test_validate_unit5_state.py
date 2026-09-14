"""Regression tests for the Unit5 source/validation tooling (not Unity tests)."""
import unittest
import yaml
from build_source_inventory import build, coverage_plan
from validate_unit5_state import UniqueLoader, ref_id, validate

class ValidationToolTests(unittest.TestCase):
    def test_duplicate_yaml_key_is_rejected(self):
        with self.assertRaises(ValueError):
            yaml.load('loop: 1\nloop: 2\n', Loader=UniqueLoader)

    def test_nested_duplicate_key_is_rejected(self):
        with self.assertRaises(ValueError):
            yaml.load('opening:\n  talk: a\n  talk: b\n', Loader=UniqueLoader)

    def test_material_reference(self):
        self.assertEqual(ref_id({'type': 'item', 'id': 5204}), 5204)
        self.assertEqual(ref_id({'type': 'testimony', 'param': '5055001'}), 5055001)
        self.assertIsNone(ref_id('unresolved'))

    def test_source_inventory_is_reproducible(self):
        self.assertEqual(build(), build())

    def test_explanation_table_is_not_free_npc(self):
        rows = {r['source_id']: r for r in coverage_plan(build())['rows']}
        self.assertFalse(rows['S1-0019']['dialogue_required'])

    def test_backstage_facts_never_become_opening(self):
        rows = {r['source_id']: r for r in coverage_plan(build())['rows']}
        for key in ['S1-0169', 'S1-0171', 'S1-0173']:
            self.assertEqual(rows[key]['planned_carrier'], 'source_constraints.backstage_truth_not_performed')

    def test_explicit_free_npc_preserved(self):
        rows = {r['source_id']: r for r in coverage_plan(build())['rows']}
        self.assertTrue(rows['S1-0396']['dialogue_required'])
        self.assertEqual(rows['S1-0396']['planned_carrier'], 'scenes')

    def test_current_five_states_pass_structural_contract(self):
        result = validate()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['loops_parsed'], 5)

if __name__ == '__main__':
    unittest.main()

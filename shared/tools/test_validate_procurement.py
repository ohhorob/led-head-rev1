import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from validate_procurement import inspect_board

from validate_procurement import BOARDS, calculate, manufacturer_blockers, supplier_plan, unique


class ProcurementTests(unittest.TestCase):
    def setUp(self):
        self.part = {"value": "100n", "footprint": "C", "mpn": "CAP", "source": "test"}
        self.policy = {
            "builds": dict(zip(BOARDS, (1, 1, 6))),
            "owned": {}, "omit": {}, "carrier_slots": 0, "spares": {"passive": 2},
        }
        self.eligible = {(board, "C1"): self.part for board in BOARDS}
        self.rows = [dict(self.part, board=board, ref="C1", disposition="buy") for board in BOARDS]
        self.evidence = dict(
            mpn="CAP", electrical="verified", mechanical="verified", mating="n/a",
            mating_rationale="No mating connector", manufacturer="M", primary_evidence="drawing",
            revision="A", locator="p2", reviewer="R", notes="Ratings and lands match",
            design_commit="commit", distributor="verified", supplier="S", sku="SKU",
            packaging="cut tape", price="USD 1", supplier_evidence="quote", pack_size="4",
            stock_units="12", supplier_checked_on="2026-11-27",
        )

    def test_aggregation_and_spares(self):
        errors = []
        parts, _ = calculate(self.policy, self.eligible, self.rows, errors)
        self.assertEqual(errors, [])
        self.assertEqual(parts["CAP"]["fitted"], 8)
        self.assertEqual(parts["CAP"]["required"], 10)

    def test_coverage_mpn_disposition_and_duplicates(self):
        self.rows[0]["mpn"] = "OTHER"
        self.policy["owned"] = {BOARDS[0]: ["C1", "C99"]}
        errors = []
        calculate(self.policy, self.eligible, [*self.rows[:2], self.rows[1]], errors)
        for expected in ("coverage", "MPN", "disposition", "duplicate", "invalid"):
            with self.subTest(expected=expected):
                self.assertTrue(any(expected in msg for msg in errors), errors)

    def test_evidence_and_pack_rounding(self):
        self.assertEqual(manufacturer_blockers({"CAP"}, [self.evidence], "commit"), [])
        orders, blockers = supplier_plan({"CAP": 10}, [self.evidence], "commit")
        self.assertEqual(blockers, [])
        self.assertEqual(orders["CAP"]["packs"], 3)
        self.assertEqual(orders["CAP"]["units"], 12)

    def test_evidence_revision_reason_and_stock(self):
        self.assertTrue(manufacturer_blockers({"CAP"}, [self.evidence], "stale"))
        self.evidence["mating_rationale"] = ""
        self.assertTrue(manufacturer_blockers({"CAP"}, [self.evidence], "commit"))
        self.evidence["stock_units"] = "11"
        orders, blockers = supplier_plan({"CAP": 10}, [self.evidence], "commit")
        self.assertEqual(orders, {})
        self.assertIn("stock below", blockers[0])

    def test_duplicate_supplier_sku(self):
        other = dict(self.evidence, mpn="OTHER", sku=" sku ")
        _, blockers = supplier_plan({"CAP": 1, "OTHER": 1}, [self.evidence, other], "commit")
        self.assertTrue(any("duplicate supplier SKU" in blocker for blocker in blockers))

    def test_duplicate_reference(self):
        errors = []
        unique([("R1", 1), ("R1", 2)], "fixture", errors)
        self.assertEqual(len(errors), 1)


class NativeParityTests(unittest.TestCase):
    def fixture(self, pcb):
        board = "test-board"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / board).mkdir()
            (root / board / f"{board}.kicad_pcb").write_text(pcb)
            xml = root / "board.xml"
            xml.write_text("""<export><components><comp ref="J1">
              <value>Header</value><footprint>Lib:Header</footprint>
              <property name="Sheetfile" value="child.kicad_sch"/>
              <sheetpath tstamps="/sheet/"/><tstamps>symbol</tstamps>
              <units><unit><pins><pin num="1"/></pins></unit></units>
              </comp></components><nets><net name="GND"><node ref="J1" pin="1"/>
              </net></nets></export>""")
            bom = root / "board.csv"
            bom.write_text("ref,value,footprint,mpn,dnp,excluded\nJ1,Header,Lib:Header,,,\n")
            errors = []
            with patch("validate_procurement.ROOT", root):
                refs, extras, eligible = inspect_board(board, xml, bom, errors)
            return refs, extras, eligible, errors

    def test_matching_hierarchy_pin_and_graphic(self):
        refs, extras, eligible, errors = self.fixture("""(kicad_pcb
          (footprint "Lib:Header" (property "Reference" "J1") (path "/sheet/symbol")
            (pad "1" thru_hole circle (at 0 0) (size 2 2) (drill 1) (net "GND")))
          (footprint "Lib:Logo" (property "Reference" "REF**") (attr board_only)))""")
        self.assertEqual(errors, [])
        self.assertEqual(eligible["J1"]["source"], "test-board/child.kicad_sch")
        self.assertEqual(refs["J1"]["pcb"]["pads"][0][4]["drill"], ["1"])
        self.assertEqual(len(extras), 1)

    def test_wrong_path_net_footprint_and_flags(self):
        _, _, _, errors = self.fixture("""(kicad_pcb
          (footprint "Lib:Wrong" (property "Reference" "J1") (path "/wrong/symbol")
            (attr exclude_from_bom dnp)
            (pad "1" thru_hole circle (net "5V")) (pad "2" thru_hole circle)))""")
        for message in ("UUID path", "schematic net", "footprint mismatch",
                        "BOM exclusion", "DNP", "no matching schematic pin"):
            with self.subTest(message=message):
                self.assertTrue(any(message in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()

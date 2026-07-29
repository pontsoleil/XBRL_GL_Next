#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "graphwalk.py"
if not SCRIPT.is_file():
    SCRIPT = HERE.parent / "tools" / "semantic" / "graphwalk.py"
SPEC = importlib.util.spec_from_file_location("graphwalk_revised", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

BSM_HEADER = MODULE.BSM_HEADER
LHM_HEADER = MODULE.LHM_HEADER


def row(**values: str) -> dict[str, str]:
    result = {name: "" for name in BSM_HEADER}
    result.update(values)
    return result


class GraphWalkTests(unittest.TestCase):
    def write(self, path: Path, rows: list[dict[str, str]], header=None) -> None:
        names = header or BSM_HEADER
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=names)
            writer.writeheader()
            writer.writerows({name: item.get(name, "") for name in names} for item in rows)

    def run_model(self, rows: list[dict[str, str]], roots=("tst:Root",)):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        bsm = root / "bsm.csv"
        lhm = root / "lhm.csv"
        self.write(bsm, rows)
        processor = MODULE.GraphWalk(bsm, lhm, roots)
        output = processor.graph_walk()
        return processor, output, lhm

    def model(self) -> list[dict[str, str]]:
        return [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Root", multiplicity="1", id="TS01"),
            row(sequence="2", level="2", property_type="Attribute", identifier="PK",
                module="tst", class_term="Root", property_term="Root ID",
                representation_term="Identifier", multiplicity="1", id="TS01-01"),
            row(sequence="3", level="2", property_type="Composition", module="tst",
                class_term="Root", property_term="Child property",
                association_role="Child", associated_module="tst",
                associated_class="Child", multiplicity="0..*", id="TS01-02"),
            row(sequence="4", level="1", property_type="Class", module="tst",
                class_term="Child", multiplicity="0..*", id="TS02"),
            row(sequence="5", level="2", property_type="Attribute", module="tst",
                class_term="Child", property_term="Name", representation_term="Text",
                multiplicity="0..1", id="TS02-01"),
        ]

    def test_canonical_17_columns_without_legacy_columns(self):
        _, rows, lhm = self.run_model(self.model())
        with lhm.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            loaded = list(reader)
        self.assertEqual(reader.fieldnames, LHM_HEADER)
        for excluded in ("path", "abbreviation_path", "xpath", "associated_class"):
            self.assertNotIn(excluded, reader.fieldnames)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(len(item) == 17 for item in loaded))
        self.assertTrue(all(item["element"] for item in loaded))

    def test_composition_recurses_and_preserves_occurrence_id(self):
        rows = self.model()
        rows.insert(
            3,
            row(sequence="3a", level="2", property_type="Composition", module="tst",
                class_term="Root", property_term="Second child property",
                association_role="Second Child", associated_module="tst",
                associated_class="Child", multiplicity="0..1", id="TS01-03"),
        )
        _, output, _ = self.run_model(rows)
        names = [item["name"] for item in output]
        self.assertIn("Child_ Child", names)
        self.assertIn("Second Child_ Child", names)
        child_attribute_ids = [
            item["id"] for item in output if item["name"] == "Name"
        ]
        self.assertEqual(child_attribute_ids, ["TS02-01", "TS02-01"])
        child_paths = [
            item["semantic_path"] for item in output if item["name"] == "Name"
        ]
        self.assertEqual(len(set(child_paths)), 2)

    def test_cross_module_composition_uses_target_module_for_class_and_attributes(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Root", multiplicity="1", id="TS01"),
            row(sequence="2", level="2", property_type="Composition", module="tst",
                class_term="Root", property_term="Child property",
                association_role="Child", associated_module="alt",
                associated_class="Child", multiplicity="0..1", id="TS01-01"),
            row(sequence="3", level="1", property_type="Class", module="alt",
                class_term="Child", multiplicity="1", id="AL01"),
            row(sequence="4", level="2", property_type="Attribute", module="alt",
                class_term="Child", property_term="Name",
                representation_term="Text", multiplicity="1", id="AL01-01"),
        ]
        _, output, _ = self.run_model(rows)
        child, attribute = output[1:]
        self.assertEqual(
            (child["type"], child["module"], child["class_term"]),
            ("C", "alt", "Child"),
        )
        self.assertEqual(child["associated_module"], "alt")
        self.assertEqual(
            (attribute["type"], attribute["module"], attribute["class_term"]),
            ("A", "alt", "Child"),
        )
        self.assertEqual(attribute["associated_module"], "alt")

    def test_reference_emits_r_and_ref_then_stops(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Root", multiplicity="1", id="TS01"),
            row(sequence="2", level="2", property_type="Reference", module="tst",
                class_term="Root", property_term="Reference property",
                association_role="Original", associated_module="tst",
                associated_class="Target", multiplicity="0..1", id="TS01-01"),
            row(sequence="3", level="1", property_type="Class", module="tst",
                class_term="Target", multiplicity="1", id="TS02"),
            row(sequence="4", level="2", property_type="Attribute", identifier="PK",
                module="tst", class_term="Target", property_term="Target ID",
                representation_term="Identifier", multiplicity="1", id="TS02-01"),
            row(sequence="5", level="2", property_type="Attribute", module="tst",
                class_term="Target", property_term="Not Traversed",
                representation_term="Text", multiplicity="1", id="TS02-02"),
        ]
        _, output, _ = self.run_model(rows)
        self.assertEqual([item["type"] for item in output], ["C", "R", "A"])
        self.assertEqual(output[1]["name"], "Original_ Target")
        self.assertEqual(output[1]["element"], "")
        self.assertEqual(output[1]["associated_module"], "tst")
        self.assertEqual(output[2]["identifier"], "REF")
        self.assertEqual(output[2]["datatype"], "Identifier")
        self.assertEqual(output[2]["associated_module"], "tst")
        self.assertNotIn("Not Traversed", [item["name"] for item in output])

    def test_cross_module_reference_uses_target_module_for_r_and_ref(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Root", multiplicity="1", id="TS01"),
            row(sequence="2", level="2", property_type="Reference", module="tst",
                class_term="Root", property_term="Reference property",
                association_role="Original", associated_module="alt",
                associated_class="Target", multiplicity="0..1", id="TS01-01"),
            row(sequence="3", level="1", property_type="Class", module="alt",
                class_term="Target", multiplicity="1", id="AL01"),
            row(sequence="4", level="2", property_type="Attribute", identifier="PK",
                module="alt", class_term="Target", property_term="Target ID",
                representation_term="Identifier", multiplicity="1", id="AL01-01"),
        ]
        _, output, _ = self.run_model(rows)
        reference, ref = output[1:]
        self.assertEqual(
            (reference["type"], reference["module"], reference["class_term"]),
            ("R", "alt", "Target"),
        )
        self.assertEqual(reference["associated_module"], "alt")
        self.assertEqual(
            (ref["identifier"], ref["module"], ref["class_term"]),
            ("REF", "alt", "Target"),
        )
        self.assertEqual(ref["associated_module"], "alt")

    def test_property_owner_module_mismatch_is_rejected(self):
        rows = self.model()
        rows[1]["module"] = "alt"
        with self.assertRaisesRegex(MODULE.GraphWalkError, "property owner"):
            self.run_model(rows)

    def test_invalid_multiplicity_is_rejected(self):
        rows = self.model()
        rows[1]["multiplicity"] = "0.*"
        with self.assertRaisesRegex(MODULE.GraphWalkError, "invalid multiplicity"):
            self.run_model(rows)

    def test_reference_many_gets_dimension_element(self):
        rows = self.model()
        rows[2]["property_type"] = "Reference"
        _, output, _ = self.run_model(rows)
        reference = [item for item in output if item["type"] == "R"][0]
        self.assertTrue(reference["element"])

    def test_element_collision_uses_shortest_unique_suffix(self):
        rows = self.model()
        rows.extend(
            [
                row(sequence="6", level="1", property_type="Class", module="tst",
                    class_term="Other", multiplicity="1", id="TS03"),
                row(sequence="7", level="2", property_type="Attribute", module="tst",
                    class_term="Other", property_term="Name", representation_term="Text",
                    multiplicity="1", id="TS03-01"),
            ]
        )
        _, output, _ = self.run_model(rows, roots=("tst:Root", "tst:Other"))
        names = {item["semantic_path"]: item["element"] for item in output if item["name"] == "Name"}
        self.assertEqual(len(set(names.values())), 2)
        self.assertIn("childChildName", names.values())
        self.assertIn("otherName", names.values())

    def test_duplicate_semantic_path_is_rejected(self):
        rows = self.model()
        rows.insert(
            3,
            row(sequence="3a", level="2", property_type="Composition", module="tst",
                class_term="Root", property_term="Duplicate child property",
                association_role="Child", associated_module="tst",
                associated_class="Child", multiplicity="1", id="TS01-03"),
        )
        with self.assertRaisesRegex(MODULE.GraphWalkError, "Duplicate semantic_path"):
            self.run_model(rows)

    def test_composition_cycle_is_rejected(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Root", multiplicity="1", id="TS01"),
            row(sequence="2", level="2", property_type="Composition", module="tst",
                class_term="Root", associated_module="tst", associated_class="Root",
                multiplicity="1", id="TS01-01"),
        ]
        with self.assertRaisesRegex(MODULE.GraphWalkError, "cycle detected"):
            self.run_model(rows)

    def test_undefined_associated_class_is_rejected(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Root", multiplicity="1", id="TS01"),
            row(sequence="2", level="2", property_type="Composition", module="tst",
                class_term="Root", associated_module="tst", associated_class="Missing",
                multiplicity="1", id="TS01-01"),
        ]
        with self.assertRaisesRegex(MODULE.GraphWalkError, "undefined associated"):
            self.run_model(rows)

    def test_same_named_class_from_two_modules_is_rejected_in_one_hierarchy(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Root", multiplicity="1", id="TS01"),
            row(sequence="2", level="2", property_type="Composition", module="tst",
                class_term="Root", property_term="First property",
                association_role="First", associated_module="tst",
                associated_class="Same", multiplicity="1", id="TS01-01"),
            row(sequence="3", level="2", property_type="Composition", module="tst",
                class_term="Root", property_term="Second property",
                association_role="Second", associated_module="alt",
                associated_class="Same", multiplicity="1", id="TS01-02"),
            row(sequence="4", level="1", property_type="Class", module="tst",
                class_term="Same", multiplicity="1", id="TS02"),
            row(sequence="5", level="1", property_type="Class", module="alt",
                class_term="Same", multiplicity="1", id="AL01"),
        ]
        with self.assertRaisesRegex(MODULE.GraphWalkError, "same-named Class"):
            self.run_model(rows)

    def test_header_error_does_not_create_or_overwrite_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bsm = root / "bad.csv"
            lhm = root / "existing.csv"
            bad_header = [name for name in BSM_HEADER if name != "associated_module"]
            self.write(bsm, self.model(), bad_header)
            lhm.write_text("preserve-me", encoding="utf-8")
            processor = MODULE.GraphWalk(bsm, lhm, ["tst:Root"])
            with self.assertRaisesRegex(MODULE.GraphWalkError, "header mismatch"):
                processor.graph_walk()
            self.assertEqual(lhm.read_text(encoding="utf-8"), "preserve-me")

    def test_legacy_15_column_bsm_header_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bsm = root / "legacy.csv"
            lhm = root / "output.csv"
            legacy_header = [
                name for name in BSM_HEADER if name != "association_role"
            ]
            self.write(bsm, self.model(), legacy_header)
            with self.assertRaisesRegex(MODULE.GraphWalkError, "header mismatch"):
                MODULE.GraphWalk(bsm, lhm, ["tst:Root"]).graph_walk()
            self.assertFalse(lhm.exists())

    def test_bsm_header_element_duplicate_and_id_order_are_rejected(self):
        id_index = BSM_HEADER.index("id")
        variants = [
            [*BSM_HEADER, "element"],
            [BSM_HEADER[0], *BSM_HEADER],
            [
                *BSM_HEADER[: id_index - 1],
                "id",
                BSM_HEADER[id_index - 1],
            ],
        ]
        for header in variants:
            with self.subTest(header=header):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    bsm = root / "bsm.csv"
                    lhm = root / "lhm.csv"
                    self.write(bsm, self.model(), header)
                    with self.assertRaisesRegex(MODULE.GraphWalkError, "header mismatch"):
                        MODULE.GraphWalk(bsm, lhm, ["tst:Root"]).graph_walk()

    def test_root_selector_rejects_unknown_prefix_undefined_and_ambiguous(self):
        for selector in ("bad:Root", "Missing"):
            with self.subTest(selector=selector):
                with self.assertRaisesRegex(
                    MODULE.GraphWalkError,
                    "Unknown root Class selector|resolves to 0 Classes",
                ):
                    self.run_model(self.model(), roots=(selector,))

        rows = self.model()
        rows.extend(
            [
                row(sequence="6", level="1", property_type="Class", module="tst",
                    class_term="Shared", multiplicity="1", id="TS03"),
                row(sequence="7", level="1", property_type="Class", module="alt",
                    class_term="Shared", multiplicity="1", id="AL01"),
            ]
        )
        with self.assertRaisesRegex(MODULE.GraphWalkError, "resolves to 2 Classes"):
            self.run_model(rows, roots=("Shared",))

    def test_reference_without_pk_is_nonfatal_and_diagnostic(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Root", multiplicity="1", id="TS01"),
            row(sequence="2", level="2", property_type="Reference", module="tst",
                class_term="Root", property_term="Reference property",
                association_role="Original", associated_module="tst",
                associated_class="Target", multiplicity="0..1", id="TS01-01"),
            row(sequence="3", level="2", property_type="Attribute", module="tst",
                class_term="Root", property_term="After Reference",
                representation_term="Text", multiplicity="1", id="TS01-02"),
            row(sequence="4", level="1", property_type="Class", module="tst",
                class_term="Target", multiplicity="1", id="TS02"),
            row(sequence="5", level="2", property_type="Attribute", module="tst",
                class_term="Target", property_term="Not A Key",
                representation_term="Text", multiplicity="1", id="TS02-01"),
        ]
        processor, output, _ = self.run_model(rows)
        self.assertEqual(
            [item["type"] for item in output],
            ["C", "R", "A"],
        )
        self.assertEqual(output[-1]["name"], "After Reference")
        self.assertNotIn("Not A Key", [item["name"] for item in output])
        self.assertEqual(
            [item["code"] for item in processor.diagnostics],
            ["reference-target-pk-missing"],
        )
        payload = json.loads(processor.diagnostics_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["error_count"], 1)

    def test_deterministic_sha256(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bsm = root / "bsm.csv"
            out1 = root / "lhm1.csv"
            out2 = root / "lhm2.csv"
            self.write(bsm, self.model())
            MODULE.GraphWalk(bsm, out1, ["tst:Root"]).graph_walk()
            MODULE.GraphWalk(bsm, out2, ["tst:Root"]).graph_walk()
            self.assertEqual(
                hashlib.sha256(out1.read_bytes()).digest(),
                hashlib.sha256(out2.read_bytes()).digest(),
            )


if __name__ == "__main__":
    unittest.main()

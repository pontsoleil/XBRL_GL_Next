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
        processor = MODULE.GraphWalk(
            bsm, lhm, roots,
            module_prefixes={**MODULE.MODULE_PREFIX, "tst": "gl-tst", "alt": "gl-alt"},
        )
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

    def test_canonical_18_columns_with_initial_local_name_and_xpath(self):
        _, rows, lhm = self.run_model(self.model())
        with lhm.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            loaded = list(reader)
        self.assertEqual(reader.fieldnames, LHM_HEADER)
        self.assertEqual(reader.fieldnames[16:], ["local_name", "xpath"])
        self.assertNotIn("element", reader.fieldnames)
        self.assertNotIn("local-name", reader.fieldnames)
        for excluded in (
            "domain_name",
            "id",
            "path",
            "abbreviation_path",
            "associated_class",
        ):
            self.assertNotIn(excluded, reader.fieldnames)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(len(item) == 18 for item in loaded))
        self.assertTrue(all(item["local_name"] for item in loaded))
        self.assertTrue(all(":" not in item["local_name"] for item in loaded))
        self.assertTrue(all(MODULE.NCNAME.fullmatch(item["local_name"])
                            for item in loaded))
        self.assertTrue(all(item["xpath"].startswith("/xbrli:xbrl/") for item in loaded))

    def test_repeated_source_bsm_id_on_multiple_paths_is_informational(self):
        rows = self.model()
        rows.insert(
            3,
            row(sequence="3a", level="2", property_type="Composition", module="tst",
                class_term="Root", property_term="Second child property",
                association_role="Second Child", associated_module="tst",
                associated_class="Child", multiplicity="0..1", id="TS01-03"),
        )
        processor, output, _ = self.run_model(rows)
        paths = [item["semantic_path"] for item in output]
        self.assertEqual(len(paths), len(set(paths)))
        reused = [item for item in output if item["source_bsm_id"] == "TS02-01"]
        self.assertEqual(len(reused), 2)
        self.assertNotEqual(reused[0]["semantic_path"], reused[1]["semantic_path"])
        reuse_diagnostics = [
            item for item in processor.diagnostics
            if item["code"] == "SOURCE_BSM_ID_REUSED"
        ]
        self.assertTrue(reuse_diagnostics)
        self.assertTrue(all(item["severity"] == "info" for item in reuse_diagnostics))

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
        self.assertEqual(child["association_role"], "Child")
        self.assertEqual(child["source_bsm_id"], "TS01-01")
        self.assertEqual(
            (attribute["type"], attribute["module"], attribute["class_term"]),
            ("A", "alt", "Child"),
        )
        self.assertEqual(attribute["associated_module"], "alt")
        self.assertEqual(attribute["association_role"], "")
        self.assertEqual(attribute["source_bsm_id"], "AL01-01")
        self.assertEqual(
            attribute["xpath"],
            "/xbrli:xbrl/gl-tst:root/gl-alt:childChild/gl-alt:name",
        )

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
        self.assertEqual(output[1]["associated_module"], "tst")
        self.assertEqual(output[1]["association_role"], "Original")
        self.assertEqual(output[1]["source_bsm_id"], "TS01-01")
        self.assertEqual(output[2]["identifier"], "REF")
        self.assertEqual(output[2]["datatype"], "Identifier")
        self.assertEqual(output[2]["associated_module"], "tst")
        self.assertEqual(output[2]["source_bsm_id"], "TS02-01")
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

    def test_reference_many_remains_in_semantic_lhm(self):
        rows = self.model()
        rows[2]["property_type"] = "Reference"
        _, output, _ = self.run_model(rows)
        reference = [item for item in output if item["type"] == "R"][0]
        self.assertEqual(reference["multiplicity"], "0..*")
        self.assertEqual(reference["local_name"], "childChild")
        self.assertTrue(reference["xpath"].endswith("/gl-tst:childChild"))

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

    def test_input_output_and_diagnostics_path_aliases_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bsm = root / "model.csv"
            output = root / "candidate.csv"
            self.write(bsm, self.model())
            cases = [
                MODULE.GraphWalk(bsm, bsm, ["tst:Root"]),
                MODULE.GraphWalk(
                    bsm, output, ["tst:Root"], diagnostics_file=bsm
                ),
                MODULE.GraphWalk(
                    bsm, output, ["tst:Root"], diagnostics_file=output
                ),
            ]
            for processor in cases:
                with self.subTest(processor=processor):
                    with self.assertRaisesRegex(
                        MODULE.GraphWalkError, "three different paths"
                    ):
                        processor.graph_walk()

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
            prefixes = {**MODULE.MODULE_PREFIX, "tst": "gl-tst"}
            MODULE.GraphWalk(
                bsm, out1, ["tst:Root"], module_prefixes=prefixes
            ).graph_walk()
            MODULE.GraphWalk(
                bsm, out2, ["tst:Root"], module_prefixes=prefixes
            ).graph_walk()
            self.assertEqual(
                hashlib.sha256(out1.read_bytes()).digest(),
                hashlib.sha256(out2.read_bytes()).digest(),
            )

    def test_semantic_path_uses_module_qualified_identifiers(self):
        _, output, _ = self.run_model(self.model())
        self.assertEqual(output[0]["semantic_path"], "$.tst_Root")
        self.assertEqual(output[1]["semantic_path"], "$.tst_Root.tst_RootID")
        self.assertEqual(
            output[2]["semantic_path"], "$.tst_Root.tst_ChildChild"
        )

    def test_semantic_path_term_normalization_removes_non_ascii_letters(self):
        cases = {
            "Entry Header": "EntryHeader",
            "Entry_Header": "EntryHeader",
            "Debit/CreditIndicator": "DebitCreditIndicator",
            "Amount-Type (2)": "AmountType",
            "Mixed.Case, Value": "MixedCaseValue",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(
                    MODULE.normalize_semantic_path_term(source), expected
                )
        self.assertEqual(
            MODULE.semantic_path_association("cor", "Seller", "Party"),
            "cor_SellerParty",
        )

    def test_semantic_path_term_empty_after_normalization_is_rejected(self):
        for source in ("", "_-/(),. 21378", "売上123"):
            with self.subTest(source=source):
                with self.assertRaisesRegex(
                    MODULE.GraphWalkError, "no ASCII letters"
                ):
                    MODULE.normalize_semantic_path_term(source)

        rows = self.model()
        rows[1]["property_term"] = "_-/ 21378"
        with self.assertRaisesRegex(
            MODULE.GraphWalkError,
            ":3:.*parent '\\$.tst_Root'.*module 'tst'.*no ASCII letters",
        ):
            self.run_model(rows)

    def test_semantic_path_normalization_collision_reports_both_terms(self):
        rows = self.model()
        rows.insert(
            2,
            row(
                sequence="2a",
                level="2",
                property_type="Attribute",
                module="tst",
                class_term="Root",
                property_term="Root_ID",
                representation_term="Identifier",
                multiplicity="0..1",
                id="TS01-01B",
            ),
        )
        with self.assertRaisesRegex(
            MODULE.GraphWalkError,
            "normalization collision.*'Root ID'.*'Root_ID'.*tst_RootID",
        ):
            self.run_model(rows)

    def test_initial_lower_camel_local_names_and_hierarchical_xpaths(self):
        _, output, _ = self.run_model(self.model())
        self.assertEqual(output[0]["local_name"], "root")
        self.assertEqual(output[1]["local_name"], "rootId")
        self.assertEqual(output[2]["local_name"], "childChild")
        self.assertEqual(
            MODULE.qualified_name("tst", output[2]["local_name"], {"tst": "gl-tst"}),
            "gl-tst:childChild",
        )
        self.assertEqual(
            output[3]["xpath"],
            "/xbrli:xbrl/gl-tst:root/gl-tst:childChild/gl-tst:name",
        )
        self.assertEqual(
            [item["name"] for item in output],
            ["Root", "Root ID", "Child_ Child", "Name"],
        )

    def test_name_word_rules_moved_to_graphwalk(self):
        cases = {
            "Party Address Name": "partyAddressName",
            "Audit_Number-value": "auditNumberValue",
            "VATCategory 21378 ID": "vatCategory21378Id",
            "  consecutive   spaces ": "consecutiveSpaces",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(MODULE.local_name_from_name(source), expected)

    def test_unregistered_module_and_invalid_ncname_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bsm = root / "bsm.csv"
            lhm = root / "lhm.csv"
            self.write(bsm, self.model())
            with self.assertRaisesRegex(MODULE.GraphWalkError, "registered taxonomy prefix"):
                MODULE.GraphWalk(bsm, lhm, ["tst:Root"]).graph_walk()
        rows = self.model()
        rows[0]["class_term"] = "21378 Root"
        rows[1]["class_term"] = "21378 Root"
        rows[2]["class_term"] = "21378 Root"
        with self.assertRaisesRegex(MODULE.GraphWalkError, "NCName"):
            self.run_model(rows, roots=("tst:21378 Root",))

    def test_association_display_name_keeps_space_but_path_removes_it(self):
        rows = self.model()
        rows[2]["association_role"] = "Seller Party"
        _, output, _ = self.run_model(rows)
        association = output[2]
        self.assertEqual(association["name"], "Seller Party_ Child")
        self.assertEqual(
            association["semantic_path"], "$.tst_Root.tst_SellerPartyChild"
        )

    def test_duplicate_local_name_is_nonblocking_review_diagnostic(self):
        rows = self.model()
        rows.extend([
            row(sequence="6", level="1", property_type="Class", module="tst",
                class_term="Other", multiplicity="1", id="TS03"),
            row(sequence="7", level="2", property_type="Attribute", module="tst",
                class_term="Other", property_term="Name", representation_term="Text",
                multiplicity="1", id="TS03-01"),
        ])
        processor, output, _ = self.run_model(rows, roots=("tst:Root", "tst:Other"))
        self.assertEqual(len(output), 6)
        duplicate = [
            item for item in processor.diagnostics
            if item["code"] == "LOCAL_NAME_DUPLICATE"
        ]
        self.assertEqual(len(duplicate), 1)
        self.assertEqual(duplicate[0]["severity"], "warning")
        self.assertEqual(duplicate[0]["occurrence_count"], 2)

    def test_level_jump_parent_missing_root_type_and_xpath_collision_fail(self):
        cases = [
            ([{"level": "1", "type": "A", "module": "tst", "local_name": "root",
               "semantic_path": "$.tst_Root"}], "level 1 must be type C"),
            ([{"level": "1", "type": "C", "module": "tst", "local_name": "root",
               "semantic_path": "$.tst_Root"},
              {"level": "3", "type": "A", "module": "tst", "local_name": "value",
               "semantic_path": "$.tst_Root.tst_Value"}], "immediate C/R parent"),
            ([{"level": "1", "type": "C", "module": "tst", "local_name": "root",
               "semantic_path": "$.tst_Root"},
              {"level": "2", "type": "A", "module": "tst", "local_name": "value",
               "semantic_path": "$.tst_Root.tst_First"},
              {"level": "2", "type": "A", "module": "tst", "local_name": "value",
               "semantic_path": "$.tst_Root.tst_Second"}], "XPath collision"),
        ]
        for rows, message in cases:
            with self.subTest(message=message):
                processor = MODULE.GraphWalk(
                    "unused.csv", "unused-output.csv", ["tst:Root"],
                    module_prefixes={"tst": "gl-tst"},
                )
                processor.rows = rows
                with self.assertRaisesRegex(MODULE.GraphWalkError, message):
                    processor.assign_xpaths()


if __name__ == "__main__":
    unittest.main()

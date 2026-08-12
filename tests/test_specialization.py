#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "specialization.py"
if not SCRIPT.is_file():
    SCRIPT = HERE.parent / "tools" / "semantic" / "specialization.py"
SPEC = importlib.util.spec_from_file_location("specialization_revised", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

FSM_HEADER = MODULE.FSM_HEADER
BSM_HEADER = MODULE.BSM_HEADER


def row(**values: str) -> dict[str, str]:
    result = {name: "" for name in FSM_HEADER}
    result.update(values)
    return result


class SpecializationTests(unittest.TestCase):
    def write(self, path: Path, rows: list[dict[str, str]], header=None) -> None:
        names = header or FSM_HEADER
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=names)
            writer.writeheader()
            writer.writerows({name: item.get(name, "") for name in names} for item in rows)

    def run_model(self, rows: list[dict[str, str]], **kwargs):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        fsm = root / "fsm.csv"
        bsm = root / "bsm.csv"
        self.write(fsm, rows)
        processor = MODULE.Specialization(
            [fsm],
            bsm,
            module_abbreviations={"tst": "TS", "alt": "AL"},
            **kwargs,
        )
        output = processor.specialization()
        return processor, output, bsm

    def basic_rows(self) -> list[dict[str, str]]:
        return [
            row(
                sequence="1",
                level="1",
                property_type="Abstract Class",
                module="tst",
                class_term="Party",
                multiplicity="0..*",
            ),
            row(
                sequence="2",
                level="2",
                property_type="Attribute",
                module="tst",
                class_term="Party",
                property_term="Name",
                representation_term="Text",
                multiplicity="0..1",
            ),
            row(
                sequence="3",
                level="1",
                property_type="Class",
                module="tst",
                class_term="Address",
                multiplicity="0..*",
            ),
            row(
                sequence="4",
                level="2",
                property_type="Attribute",
                identifier="PK",
                module="tst",
                class_term="Address",
                property_term="Address ID",
                representation_term="Identifier",
                multiplicity="1",
            ),
            row(
                sequence="5",
                level="1",
                property_type="Class",
                module="alt",
                class_term="Customer",
                multiplicity="0..*",
            ),
            row(
                sequence="6",
                level="2",
                property_type="Specialisation",
                module="alt",
                class_term="Customer",
                associated_module="tst",
                associated_class="Party",
                multiplicity="1",
            ),
            row(
                sequence="7",
                level="2",
                property_type="Attribute",
                module="alt",
                class_term="Customer",
                property_term="Name",
                representation_term="Name",
                multiplicity="1",
            ),
            row(
                sequence="8",
                level="2",
                property_type="Composition",
                module="alt",
                class_term="Customer",
                property_term="Address property",
                association_role="",
                associated_module="tst",
                associated_class="Address",
                multiplicity="0..1",
            ),
        ]

    def test_canonical_headers_ids_empty_role_and_property_provenance(self):
        processor, output, bsm = self.run_model(self.basic_rows())
        with bsm.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        self.assertEqual(reader.fieldnames, BSM_HEADER)
        self.assertNotIn("element", reader.fieldnames)
        self.assertTrue(all(len(item) == 16 for item in rows))
        customer = [item for item in rows if item["class_term"] == "Customer"]
        self.assertEqual(customer[0]["id"], "AL01")
        self.assertEqual([item["id"] for item in customer[1:]], ["AL01-01", "AL01-02"])
        self.assertTrue(all(item["module"] == "alt" for item in customer))
        self.assertEqual(customer[1]["module"], "alt")
        self.assertEqual(customer[2]["property_term"], "Address property")
        self.assertEqual(customer[2]["association_role"], "")
        self.assertEqual(customer[2]["associated_module"], "tst")
        self.assertEqual(processor.diagnostics, [])

    def test_canonical_specialisation_is_accepted_without_alias_warning(self):
        processor, output, _ = self.run_model(self.basic_rows())
        self.assertTrue(output)
        self.assertFalse(
            any(
                item["code"] == "NON_CANONICAL_ASSOCIATION_TYPE"
                for item in processor.diagnostics
            )
        )

    def test_legacy_specialization_warns_normalizes_and_matches_bsm(self):
        canonical_rows = self.basic_rows()
        _, canonical_output, canonical_bsm = self.run_model(canonical_rows)

        legacy_rows = [dict(item) for item in canonical_rows]
        legacy_rows[5]["property_type"] = "Specialization"
        processor, legacy_output, legacy_bsm = self.run_model(legacy_rows)

        alias_warnings = [
            item
            for item in processor.diagnostics
            if item["code"] == "NON_CANONICAL_ASSOCIATION_TYPE"
        ]
        self.assertEqual(len(alias_warnings), 1)
        self.assertEqual(alias_warnings[0]["severity"], "warning")
        self.assertEqual(alias_warnings[0]["supplied_value"], "Specialization")
        self.assertEqual(alias_warnings[0]["canonical_value"], "Specialisation")
        self.assertIn("normalised to 'Specialisation'", alias_warnings[0]["message"])
        self.assertEqual(canonical_output, legacy_output)
        self.assertEqual(canonical_bsm.read_bytes(), legacy_bsm.read_bytes())
        self.assertTrue(
            all(item["property_type"] != "Specialization" for item in legacy_output)
        )

    def test_non_exact_specialisation_spellings_are_rejected(self):
        for value in ("specialisation", "SPECIALISATION", "Specializtion"):
            with self.subTest(value=value):
                rows = self.basic_rows()
                rows[5]["property_type"] = value
                with self.assertRaisesRegex(
                    MODULE.SpecializationError, "unsupported property_type"
                ):
                    self.run_model(rows)

    def test_free_text_carriage_returns_are_preserved_as_quoted_csv_newlines(self):
        rows = self.basic_rows()
        rows[3]["definition"] = "first\rsecond"
        rows[3]["definition_local"] = "甲\r乙"
        _, output, bsm = self.run_model(rows)
        source_property = next(
            item for item in output
            if item["class_term"] == "Address" and item["property_term"] == "Address ID"
        )
        self.assertEqual(source_property["definition"], "first\nsecond")
        self.assertEqual(source_property["definition_local"], "甲\n乙")
        with bsm.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            written = list(reader)
        self.assertEqual(len(written), len(output))
        written_property = next(
            item for item in written
            if item["class_term"] == "Address" and item["property_term"] == "Address ID"
        )
        self.assertEqual(written_property["definition"], "first\nsecond")
        self.assertEqual(written_property["definition_local"], "甲\n乙")
        self.assertEqual(written_property["id"], "TS01-01")

    def test_same_class_term_in_different_modules(self):
        rows = [
            row(
                sequence="1", level="1", property_type="Class",
                module="tst", class_term="Same", multiplicity="1"
            ),
            row(
                sequence="2", level="1", property_type="Class",
                module="alt", class_term="Same", multiplicity="1"
            ),
        ]
        _, output, _ = self.run_model(rows)
        self.assertEqual(
            [(item["module"], item["class_term"]) for item in output],
            [("tst", "Same"), ("alt", "Same")],
        )

    def test_two_empty_roles_are_distinguished_by_target(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="A", multiplicity="1"),
            row(sequence="2", level="2", property_type="Composition", module="tst",
                class_term="A", associated_module="tst", associated_class="B",
                multiplicity="1"),
            row(sequence="3", level="2", property_type="Composition", module="tst",
                class_term="A", associated_module="tst", associated_class="C",
                multiplicity="1"),
            row(sequence="4", level="1", property_type="Class", module="tst",
                class_term="B", multiplicity="1"),
            row(sequence="5", level="1", property_type="Class", module="tst",
                class_term="C", multiplicity="1"),
        ]
        _, output, _ = self.run_model(rows)
        a = [item for item in output if item["class_term"] == "A"]
        self.assertEqual(len(a), 3)

    def test_delete_zero_and_zero_zero(self):
        for deletion in ("0", "0..0"):
            with self.subTest(deletion=deletion):
                rows = self.basic_rows()
                rows[6]["multiplicity"] = deletion
                _, output, _ = self.run_model(rows)
                customer_terms = [
                    item["property_term"]
                    for item in output
                    if item["class_term"] == "Customer"
                ]
                self.assertNotIn("Name", customer_terms)

    def test_deleted_property_is_not_inherited_by_descendant(self):
        rows = self.basic_rows()
        rows[6]["multiplicity"] = "0"
        rows.extend(
            [
                row(sequence="9", level="1", property_type="Class", module="alt",
                    class_term="Preferred Customer", multiplicity="1"),
                row(sequence="10", level="2", property_type="Specialisation",
                    module="alt", class_term="Preferred Customer",
                    associated_module="alt", associated_class="Customer",
                    multiplicity="1"),
            ]
        )
        processor, output, _ = self.run_model(rows)
        for class_term in ("Customer", "Preferred Customer"):
            self.assertNotIn(
                "Name",
                [
                    item["property_term"]
                    for item in output
                    if item["class_term"] == class_term
                ],
            )
        deleted = [
            item for item in processor.diagnostics
            if item["code"] == "property-deleted"
        ]
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0]["descendant_inheritance"], "blocked")

    def test_multiplicity_contract_accepts_valid_and_rejects_invalid(self):
        for value in ("0..1", "0..*", "1", "1..1", "1..*"):
            with self.subTest(valid=value):
                rows = self.basic_rows()
                rows[7]["multiplicity"] = value
                self.run_model(rows)
        for value in ("", "0.*", "1.*", "0...*", "..", "*", "0..2"):
            with self.subTest(invalid=value):
                rows = self.basic_rows()
                rows[7]["multiplicity"] = value
                with self.assertRaisesRegex(
                    MODULE.SpecializationError,
                    "required field|invalid multiplicity",
                ):
                    self.run_model(rows)

    def test_property_module_must_match_owning_class(self):
        rows = self.basic_rows()
        rows[7]["module"] = "tst"
        with self.assertRaisesRegex(MODULE.SpecializationError, "owning Class module"):
            self.run_model(rows)

    def test_abstract_association_is_reported_and_excluded(self):
        rows = [
            row(sequence="1", level="1", property_type="Abstract Class",
                module="tst", class_term="Abstract Target", multiplicity="1"),
            row(sequence="2", level="1", property_type="Class",
                module="tst", class_term="Owner", multiplicity="1"),
            row(sequence="3", level="2", property_type="Composition",
                module="tst", class_term="Owner", associated_module="tst",
                associated_class="Abstract Target", multiplicity="1"),
        ]
        processor, output, _ = self.run_model(rows)
        self.assertEqual(len(output), 1)
        self.assertEqual(processor.diagnostics[0]["code"], "abstract-association-excluded")

    def test_header_missing_extra_and_order_are_rejected(self):
        base = self.basic_rows()
        variants = [
            FSM_HEADER[:-1],
            [*FSM_HEADER, "extra"],
            [FSM_HEADER[1], FSM_HEADER[0], *FSM_HEADER[2:]],
            [name for name in FSM_HEADER if name != "association_role"],
            [
                *FSM_HEADER[: FSM_HEADER.index("association_role")],
                "property_term",
                *FSM_HEADER[FSM_HEADER.index("association_role") + 1 :],
            ],
        ]
        for header in variants:
            with self.subTest(header=header):
                with tempfile.TemporaryDirectory() as directory:
                    fsm = Path(directory) / "fsm.csv"
                    self.write(fsm, base, header)
                    processor = MODULE.Specialization(
                        [fsm], Path(directory) / "bsm.csv",
                        module_abbreviations={"tst": "TS", "alt": "AL"},
                    )
                    with self.assertRaisesRegex(MODULE.SpecializationError, "header mismatch"):
                        processor.specialization()

    def test_undefined_associated_class_is_rejected_without_output(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="A", multiplicity="1"),
            row(sequence="2", level="2", property_type="Composition", module="tst",
                class_term="A", associated_module="tst", associated_class="Missing",
                multiplicity="1"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            fsm = Path(directory) / "fsm.csv"
            bsm = Path(directory) / "bsm.csv"
            self.write(fsm, rows)
            processor = MODULE.Specialization(
                [fsm], bsm, module_abbreviations={"tst": "TS"}
            )
            with self.assertRaisesRegex(MODULE.SpecializationError, "undefined associated"):
                processor.specialization()
            self.assertFalse(bsm.exists())

    def test_missing_associated_module_is_rejected(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="A", multiplicity="1"),
            row(sequence="2", level="2", property_type="Composition", module="tst",
                class_term="A", associated_class="A", multiplicity="1"),
        ]
        with self.assertRaisesRegex(MODULE.SpecializationError, "requires associated_module"):
            self.run_model(rows)

    def test_qname_is_rejected(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="tst:A", multiplicity="1"),
        ]
        with self.assertRaisesRegex(MODULE.SpecializationError, "not QName"):
            self.run_model(rows)

    def test_duplicate_class_and_property_are_rejected(self):
        duplicate_class = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="A", multiplicity="1"),
            row(sequence="2", level="1", property_type="Class", module="tst",
                class_term="A", multiplicity="1"),
        ]
        with self.assertRaisesRegex(MODULE.SpecializationError, "duplicate Class"):
            self.run_model(duplicate_class)
        duplicate_property = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="A", multiplicity="1"),
            row(sequence="2", level="2", property_type="Attribute", module="tst",
                class_term="A", property_term="Name",
                representation_term="Text", multiplicity="1"),
            row(sequence="3", level="2", property_type="Attribute", module="tst",
                class_term="A", property_term="Name",
                representation_term="Text", multiplicity="0..1"),
        ]
        with self.assertRaisesRegex(MODULE.SpecializationError, "duplicate property identity"):
            self.run_model(duplicate_property)

    def test_association_kind_and_multiplicity_are_overwritten(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Target", multiplicity="1"),
            row(sequence="2", level="1", property_type="Abstract Class", module="tst",
                class_term="Base", multiplicity="1"),
            row(sequence="3", level="2", property_type="Composition", module="tst",
                class_term="Base", property_term="Base wording",
                association_role="Role", associated_module="tst",
                associated_class="Target", multiplicity="0..1"),
            row(sequence="4", level="1", property_type="Class", module="tst",
                class_term="Child", multiplicity="1"),
            row(sequence="5", level="2", property_type="Specialisation", module="tst",
                class_term="Child", associated_module="tst", associated_class="Base",
                multiplicity="1"),
            row(sequence="6", level="2", property_type="Reference", module="tst",
                class_term="Child", property_term="Child wording",
                association_role="Role", associated_module="tst",
                associated_class="Target", multiplicity="1"),
        ]
        _, output, _ = self.run_model(rows)
        child = [item for item in output if item["class_term"] == "Child"][1]
        self.assertEqual(child["property_type"], "Reference")
        self.assertEqual(child["multiplicity"], "1")
        self.assertEqual(child["property_term"], "Child wording")
        self.assertEqual(child["association_role"], "Role")

    def test_association_identity_ignores_property_term(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Target", multiplicity="1"),
            row(sequence="2", level="1", property_type="Class", module="tst",
                class_term="Owner", multiplicity="1"),
            row(sequence="3", level="2", property_type="Composition", module="tst",
                class_term="Owner", property_term="First wording",
                association_role="Role", associated_module="tst",
                associated_class="Target", multiplicity="1"),
            row(sequence="4", level="2", property_type="Reference", module="tst",
                class_term="Owner", property_term="Second wording",
                association_role="Role", associated_module="tst",
                associated_class="Target", multiplicity="0..1"),
        ]
        with self.assertRaisesRegex(
            MODULE.SpecializationError, "duplicate property identity"
        ):
            self.run_model(rows)

    def test_attribute_rejects_association_role(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="Owner", multiplicity="1"),
            row(sequence="2", level="2", property_type="Attribute", module="tst",
                class_term="Owner", property_term="Name",
                association_role="Not allowed", representation_term="Text",
                multiplicity="1"),
        ]
        with self.assertRaisesRegex(
            MODULE.SpecializationError, "must not define association_role"
        ):
            self.run_model(rows)

    def test_specialization_cycle_is_rejected(self):
        rows = [
            row(sequence="1", level="1", property_type="Class", module="tst",
                class_term="A", multiplicity="1"),
            row(sequence="2", level="2", property_type="Specialisation", module="tst",
                class_term="A", associated_module="tst", associated_class="B",
                multiplicity="1"),
            row(sequence="3", level="1", property_type="Class", module="tst",
                class_term="B", multiplicity="1"),
            row(sequence="4", level="2", property_type="Specialisation", module="tst",
                class_term="B", associated_module="tst", associated_class="A",
                multiplicity="1"),
        ]
        with self.assertRaisesRegex(MODULE.SpecializationError, "cycle detected"):
            self.run_model(rows)


if __name__ == "__main__":
    unittest.main()

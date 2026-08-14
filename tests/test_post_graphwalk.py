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
SCRIPT = HERE / "post_graphwalk.py"
if not SCRIPT.is_file():
    SCRIPT = HERE.parent / "tools" / "semantic" / "post_graphwalk.py"
SPEC = importlib.util.spec_from_file_location("post_graphwalk_revised", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

LHM_HEADER = MODULE.LHM_HEADER


def reviewed_row(**values: str) -> dict[str, str]:
    result = {name: "" for name in LHM_HEADER}
    result.update(values)
    return result


class PostGraphWalkSemanticPathTests(unittest.TestCase):
    def model(self) -> list[dict[str, str]]:
        return [
            reviewed_row(
                sequence="1", module="cor", level="1", type="C",
                name="Accounting Entries", multiplicity="1",
                source_bsm_id="CO01", semantic_path="$.cor_AccountingEntries",
                associated_module="cor", class_term="Accounting Entries",
                local_name="accountingEntries", xpath="input-root-xpath",
            ),
            reviewed_row(
                sequence="2", module="cor", level="2", type="C",
                name="Entry Header", multiplicity="1",
                source_bsm_id="CO01-01",
                semantic_path="$.cor_AccountingEntries.cor_EntryHeader",
                associated_module="cor", class_term="Entry Header",
                local_name="entryHeader", xpath="input-header-xpath",
            ),
            reviewed_row(
                sequence="3", module="cor", level="3", type="C",
                name="Entry Detail", multiplicity="1",
                source_bsm_id="CO02-01",
                semantic_path=(
                    "$.cor_AccountingEntries.cor_EntryHeader.cor_EntryDetail"
                ),
                associated_module="cor", class_term="Entry Detail",
                local_name="entryDetail", xpath="input-detail-xpath",
            ),
            reviewed_row(
                sequence="4", module="cor", level="4", type="A",
                name="Debit/Credit Indicator", datatype="Token",
                multiplicity="1", source_bsm_id="CO03-01",
                semantic_path=(
                    "$.cor_AccountingEntries.cor_EntryHeader.cor_EntryDetail."
                    "cor_DebitCreditIndicator"
                ),
                associated_module="cor", class_term="Entry Detail",
                local_name="debitCreditIndicator", xpath="input-attribute-xpath",
            ),
        ]

    def write_reviewed(self, path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=LHM_HEADER, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def run_model(self, rows: list[dict[str, str]]):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        reviewed = root / "reviewed.csv"
        output = root / "formal"
        self.write_reviewed(reviewed, rows)
        processor = MODULE.PostGraphWalk(reviewed, output)
        return processor, output

    def test_canonical_semantic_path_is_preserved_and_xpath_is_regenerated(self):
        rows = self.model()
        expected_paths = [row["semantic_path"] for row in rows]
        processor, output = self.run_model(rows)
        processor.process()
        hmd = output / "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv"
        with hmd.open(encoding="utf-8-sig", newline="") as handle:
            emitted = list(csv.DictReader(handle))
        self.assertEqual(
            [row["semantic_path"] for row in emitted], expected_paths
        )
        self.assertEqual(
            emitted[-1]["semantic_path"],
            "$.cor_AccountingEntries.cor_EntryHeader.cor_EntryDetail."
            "cor_DebitCreditIndicator",
        )
        self.assertEqual(
            emitted[-1]["xpath"],
            "/xbrli:xbrl/gl-cor:accountingEntries/gl-cor:entryHeader/"
            "gl-cor:entryDetail/gl-cor:debitCreditIndicator",
        )

    def test_noncanonical_segments_are_rejected_without_repair(self):
        invalid_paths = (
            "$.cor_AccountingEntries.cor_Entry_Header",
            "$.cor_AccountingEntries.cor_Debit/CreditIndicator",
            "$.cor_AccountingEntries.cor_Entry2Header",
            "$.cor_AccountingEntries.cor_",
        )
        for semantic_path in invalid_paths:
            with self.subTest(semantic_path=semantic_path):
                rows = self.model()
                rows[1]["semantic_path"] = semantic_path
                processor, output = self.run_model(rows)
                with self.assertRaises(MODULE.PostGraphWalkError):
                    processor.process()
                self.assertFalse(output.exists())
                self.assertIn(
                    "NONCANONICAL_SEMANTIC_PATH",
                    [error["error_code"] for error in processor.errors],
                )
                self.assertEqual(rows[1]["semantic_path"], semantic_path)

    def test_semantic_path_module_and_parent_mismatches_are_rejected(self):
        cases = (
            (
                1,
                "$.cor_AccountingEntries.bus_EntryHeader",
                "SEMANTIC_PATH_MODULE_MISMATCH",
            ),
            (
                2,
                "$.cor_AccountingEntries.cor_OtherHeader.cor_EntryDetail",
                "SEMANTIC_PATH_PARENT_MISMATCH",
            ),
        )
        for index, semantic_path, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                rows = self.model()
                rows[index]["semantic_path"] = semantic_path
                processor, output = self.run_model(rows)
                with self.assertRaises(MODULE.PostGraphWalkError):
                    processor.process()
                self.assertFalse(output.exists())
                self.assertIn(
                    expected_code,
                    [error["error_code"] for error in processor.errors],
                )

    def test_xpath_does_not_use_semantic_path_terms(self):
        rows = self.model()
        replacements = ("Model", "HeaderNode", "DetailNode", "NotXPathSource")
        parent = "$"
        for row, term in zip(rows, replacements):
            parent = f"{parent}.cor_{term}"
            row["semantic_path"] = parent
        processor, output = self.run_model(rows)
        processor.process()
        hmd = output / "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv"
        with hmd.open(encoding="utf-8-sig", newline="") as handle:
            emitted = list(csv.DictReader(handle))
        self.assertTrue(emitted[-1]["semantic_path"].endswith("cor_NotXPathSource"))
        self.assertEqual(
            emitted[-1]["xpath"],
            "/xbrli:xbrl/gl-cor:accountingEntries/gl-cor:entryHeader/"
            "gl-cor:entryDetail/gl-cor:debitCreditIndicator",
        )


if __name__ == "__main__":
    unittest.main()

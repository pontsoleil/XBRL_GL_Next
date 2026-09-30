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
    def test_reviewed_header_uses_value_domain_and_rejects_association_role(self):
        self.assertEqual(LHM_HEADER[8], "value_domain")
        self.assertNotIn("association_role", LHM_HEADER)

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        reviewed = root / "reviewed.csv"
        output = root / "formal"
        legacy_header = list(LHM_HEADER)
        legacy_header[8] = "association_role"
        with reviewed.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=legacy_header, lineterminator="\n")
            writer.writeheader()
            writer.writerow({name: "" for name in legacy_header})

        processor = MODULE.PostGraphWalk(reviewed, output)
        with self.assertRaises(MODULE.PostGraphWalkError):
            processor.process()
        self.assertFalse(output.exists())
        self.assertIn(
            "LHM_HEADER_MISMATCH",
            [error["error_code"] for error in processor.errors],
        )

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
        self.assertFalse(hmd.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertFalse((output / "manifest.csv").read_bytes().startswith(b"\xef\xbb\xbf"))
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

    def test_reviewed_values_are_preserved_including_value_domain(self):
        rows = self.model()
        rows[0]["value_domain"] = ""
        rows[-1]["value_domain"] = "DebitCreditCode"
        expected_fields = (
            "value_domain",
            "local_name",
            "multiplicity",
            "semantic_path",
            "source_bsm_id",
        )
        expected = [
            {name: row[name] for name in expected_fields}
            for row in rows
        ]

        processor, output = self.run_model(rows)
        processor.process()
        hmd = output / "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv"
        self.assertFalse(hmd.read_bytes().startswith(b"\xef\xbb\xbf"))
        with hmd.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames, LHM_HEADER)
            emitted = list(reader)

        self.assertEqual(
            [{name: row[name] for name in expected_fields} for row in emitted],
            expected,
        )
        self.assertEqual(emitted[0]["value_domain"], "")
        self.assertEqual(emitted[-1]["value_domain"], "DebitCreditCode")
        self.assertNotEqual(emitted[-1]["xpath"], rows[-1]["xpath"])

    def test_ivc_attribute_uses_registered_invoice_module_prefix(self):
        rows = [
            reviewed_row(
                sequence="1", module="btx", level="1", type="C",
                name="Business Transactions", multiplicity="1",
                source_bsm_id="BT-ROOT",
                semantic_path="$.btx_BusinessTransactions",
                associated_module="btx", class_term="Business Transactions",
                local_name="businessTransactions",
            ),
            reviewed_row(
                sequence="2", module="ivc", level="2", type="A",
                name="Payment Terms", datatype="String", multiplicity="0..1",
                source_bsm_id="IV-01",
                semantic_path="$.btx_BusinessTransactions.ivc_PaymentTerms",
                associated_module="ivc", class_term="Business Transactions",
                local_name="paymentTerms",
            ),
        ]
        processor, output = self.run_model(rows)
        processor.process()
        hmd = output / "XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv"
        with hmd.open(encoding="utf-8-sig", newline="") as handle:
            emitted = list(csv.DictReader(handle))
        self.assertEqual(emitted[-1]["module"], "ivc")
        self.assertEqual(
            emitted[-1]["xpath"],
            "/xbrli:xbrl/gl-btx:businessTransactions/gl-ivc:paymentTerms",
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

    def test_cross_root_shared_qname_divergence_is_allowed(self):
        rows = [
            reviewed_row(
                sequence="1", module="cor", level="1", type="C",
                name="Accounting Entries", multiplicity="1",
                definition="Accounting root", source_bsm_id="AE-ROOT",
                semantic_path="$.cor_AccountingEntries", associated_module="cor",
                class_term="Accounting Entries", local_name="accountingEntries",
            ),
            reviewed_row(
                sequence="2", module="cor", level="2", type="C",
                name="Shared Class", multiplicity="1", definition="AE definition",
                source_bsm_id="AE-SHARED",
                semantic_path="$.cor_AccountingEntries.cor_SharedClass",
                associated_module="cor", class_term="Shared Class",
                local_name="sharedClass",
            ),
            reviewed_row(
                sequence="3", module="cor", level="3", type="A",
                name="Left Value", datatype="Token", multiplicity="1",
                source_bsm_id="AE-LEFT",
                semantic_path=(
                    "$.cor_AccountingEntries.cor_SharedClass.cor_LeftValue"
                ),
                associated_module="cor", class_term="Shared Class",
                local_name="leftValue",
            ),
            reviewed_row(
                sequence="4", module="btx", level="1", type="C",
                name="Business Transactions", multiplicity="1",
                definition="Business root", source_bsm_id="BT-ROOT",
                semantic_path="$.btx_BusinessTransactions", associated_module="btx",
                class_term="Business Transactions", local_name="businessTransactions",
            ),
            reviewed_row(
                sequence="5", module="cor", level="2", type="C",
                name="Shared Class", multiplicity="1", definition="BT definition",
                source_bsm_id="BT-SHARED",
                semantic_path="$.btx_BusinessTransactions.btx_SharedClass",
                associated_module="cor", class_term="Shared Class",
                local_name="sharedClass",
            ),
            reviewed_row(
                sequence="6", module="bus", level="3", type="A",
                name="Right Value", datatype="Token", multiplicity="1",
                source_bsm_id="BT-RIGHT",
                semantic_path=(
                    "$.btx_BusinessTransactions.btx_SharedClass.bus_RightValue"
                ),
                associated_module="cor", class_term="Shared Class",
                local_name="rightValue",
            ),
        ]
        processor, output = self.run_model(rows)
        try:
            processor.process()
        except MODULE.PostGraphWalkError as exc:
            self.fail(f"cross-root divergence was rejected: {exc}; {processor.errors}")
        self.assertTrue(
            (output / "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv").is_file()
        )
        self.assertTrue(
            (output / "XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv").is_file()
        )
        self.assertEqual(processor.shared_qname_definition_mismatch_count, 0)
        self.assertEqual(processor.shared_qname_content_model_mismatch_count, 0)

    def test_within_root_shared_qname_definition_conflict_is_rejected(self):
        rows = self.within_root_reuse_model()
        rows[5]["definition"] = "Conflicting definition"
        processor, output = self.run_model(rows)
        with self.assertRaises(MODULE.PostGraphWalkError):
            processor.process()
        self.assertFalse(output.exists())
        self.assertIn(
            "HMD_QNAME_DEFINITION_CONFLICT",
            [error["error_code"] for error in processor.errors],
        )

    def test_within_root_shared_qname_content_model_conflict_is_rejected(self):
        processor, output = self.run_model(self.within_root_reuse_model())
        with self.assertRaises(MODULE.PostGraphWalkError):
            processor.process()
        self.assertFalse(output.exists())
        self.assertIn(
            "QNAME_CONTENT_MODEL_MISMATCH",
            [error["error_code"] for error in processor.errors],
        )

    def test_duplicate_semantic_path_check_is_unchanged(self):
        rows = self.model()
        rows[2]["semantic_path"] = rows[1]["semantic_path"]
        processor, output = self.run_model(rows)
        with self.assertRaises(MODULE.PostGraphWalkError):
            processor.process()
        self.assertFalse(output.exists())
        self.assertIn(
            "DUPLICATE_SEMANTIC_PATH",
            [error["error_code"] for error in processor.errors],
        )

    def within_root_reuse_model(self) -> list[dict[str, str]]:
        rows = [
            reviewed_row(
                sequence="1", module="cor", level="1", type="C",
                name="Accounting Entries", multiplicity="1",
                source_bsm_id="ROOT", semantic_path="$.cor_AccountingEntries",
                associated_module="cor", class_term="Accounting Entries",
                local_name="accountingEntries",
            ),
        ]
        for sequence, container, child in (
            (2, "First Container", "Left Value"),
            (5, "Second Container", "Right Value"),
        ):
            container_term = container.replace(" ", "")
            child_term = child.replace(" ", "")
            rows.extend([
                reviewed_row(
                    sequence=str(sequence), module="cor", level="2", type="C",
                    name=container, multiplicity="1",
                    source_bsm_id=f"CONTAINER-{sequence}",
                    semantic_path=f"$.cor_AccountingEntries.cor_{container_term}",
                    associated_module="cor", class_term=container,
                    local_name=container_term[0].lower() + container_term[1:],
                ),
                reviewed_row(
                    sequence=str(sequence + 1), module="cor", level="3", type="C",
                    name="Shared Class", multiplicity="1", definition="Shared definition",
                    source_bsm_id=f"SHARED-{sequence}",
                    semantic_path=(
                        f"$.cor_AccountingEntries.cor_{container_term}.cor_SharedClass"
                    ),
                    associated_module="cor", class_term="Shared Class",
                    local_name="sharedClass",
                ),
                reviewed_row(
                    sequence=str(sequence + 2), module="cor", level="4", type="A",
                    name=child, datatype="Token", multiplicity="1",
                    source_bsm_id=f"CHILD-{sequence}",
                    semantic_path=(
                        f"$.cor_AccountingEntries.cor_{container_term}.cor_SharedClass."
                        f"cor_{child_term}"
                    ),
                    associated_module="cor", class_term="Shared Class",
                    local_name=child_term[0].lower() + child_term[1:],
                ),
            ])
        return rows


if __name__ == "__main__":
    unittest.main()

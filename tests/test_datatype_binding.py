#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINDING_SCRIPT = ROOT / "tools" / "taxonomy" / "datatype_binding.py"
GENERATOR_SCRIPT = ROOT / "tools" / "taxonomy" / "xBRLGL_TaxonomyGenerator.py"

sys.path.insert(0, str(BINDING_SCRIPT.parent))
BINDING = importlib.import_module("datatype_binding")

GENERATOR_SPEC = importlib.util.spec_from_file_location(
    "datatype_binding_generator", GENERATOR_SCRIPT
)
assert GENERATOR_SPEC and GENERATOR_SPEC.loader
GENERATOR = importlib.util.module_from_spec(GENERATOR_SPEC)
GENERATOR_SPEC.loader.exec_module(GENERATOR)


HMD_HEADER = [
    "sequence", "module", "level", "type", "identifier", "name",
    "datatype", "multiplicity", "association_role", "definition",
    "label_local", "definition_local", "source_bsm_id", "semantic_path",
    "associated_module", "class_term", "local_name", "xpath",
]


def write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class DatatypeBindingTests(unittest.TestCase):
    def test_default_mapping_and_explicit_override_precedence(self):
        binding = BINDING.DatatypeBinding()
        default = binding.resolve(
            "Amount", "$.invoice.total", "en16931", "InvoiceTotal"
        )
        self.assertEqual(default.xbrl_item_type, "xbrli:monetaryItemType")
        self.assertEqual(default.origin, "default")
        override = binding.resolve(
            "Text",
            "$.invoice.seller.sellerContact.sellerContactEmailAddress",
            "en16931",
            "SellerContactEmailAddress",
        )
        self.assertEqual(override.xbrl_item_type, "gen:emailAddressItemType")
        self.assertEqual(override.origin, "override")
        self.assertTrue(override.overridden)

    def test_unknown_datatype_has_no_string_fallback(self):
        binding = BINDING.DatatypeBinding()
        with self.assertRaisesRegex(
            BINDING.DatatypeBindingError, "no string fallback"
        ):
            binding.resolve("Unknown type", "$.root.value", "cor", "value")

    def test_review_required_default_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mapping = root / "mapping.csv"
            override = root / "override.csv"
            write_csv(
                mapping,
                BINDING.MAPPING_HEADER,
                [
                    {
                        "hmd_datatype": "Pending type",
                        "xsd_base_type": "xs:string",
                        "xbrl_item_type": "xbrli:stringItemType",
                        "unit_semantics": "none",
                        "status": "review-required",
                        "source": "unit test",
                        "notes": "",
                    }
                ],
            )
            write_csv(override, BINDING.OVERRIDE_HEADER, [])
            binding = BINDING.DatatypeBinding(mapping, override)
            with self.assertRaisesRegex(
                BINDING.DatatypeBindingError, "review-required"
            ):
                binding.resolve(
                    "Pending type", "$.root.value", "cor", "value"
                )

    def test_duplicate_normalized_default_mapping_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mapping = root / "mapping.csv"
            override = root / "override.csv"
            write_csv(
                mapping,
                BINDING.MAPPING_HEADER,
                [
                    {
                        "hmd_datatype": "Date Time",
                        "xsd_base_type": "xs:dateTime",
                        "xbrl_item_type": "xbrli:dateTimeItemType",
                        "unit_semantics": "none",
                        "status": "confirmed",
                        "source": "test",
                        "notes": "",
                    },
                    {
                        "hmd_datatype": "DateTime",
                        "xsd_base_type": "xs:dateTime",
                        "xbrl_item_type": "xbrli:dateTimeItemType",
                        "unit_semantics": "none",
                        "status": "confirmed",
                        "source": "test",
                        "notes": "",
                    },
                ],
            )
            write_csv(override, BINDING.OVERRIDE_HEADER, [])
            with self.assertRaisesRegex(
                BINDING.DatatypeBindingError, "duplicate default mapping"
            ):
                BINDING.DatatypeBinding(mapping, override)

    def test_override_must_match_actual_hmd_identity(self):
        binding = BINDING.DatatypeBinding()
        with self.assertRaisesRegex(
            BINDING.DatatypeBindingError, "override mismatch"
        ):
            binding.resolve(
                "Code",
                "$.invoice.seller.sellerContact.sellerContactEmailAddress",
                "en16931",
                "SellerContactEmailAddress",
            )

    def test_mapping_rejects_invalid_item_type_qname(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mapping = root / "mapping.csv"
            override = root / "override.csv"
            write_csv(
                mapping,
                BINDING.MAPPING_HEADER,
                [{
                    "hmd_datatype": "Text",
                    "xsd_base_type": "xs:string",
                    "xbrl_item_type": "stringItemType",
                    "unit_semantics": "none",
                    "status": "confirmed",
                    "source": "test",
                    "notes": "",
                }],
            )
            write_csv(override, BINDING.OVERRIDE_HEADER, [])
            with self.assertRaisesRegex(
                BINDING.DatatypeBindingError, "lexical QName"
            ):
                BINDING.DatatypeBinding(mapping, override)

    def test_cli_accepts_explicit_binding_resource_paths(self):
        args = GENERATOR.create_argument_parser().parse_args([
            "--hmd-dir", "hmd",
            "--output-dir", "out",
            "--namespace", "http://www.xbrl.org/int/gl/2026-12-31/plt",
            "--datatype-mapping", "mapping.csv",
            "--datatype-override", "override.csv",
        ])
        self.assertEqual(args.datatype_mapping, "mapping.csv")
        self.assertEqual(args.datatype_override, "override.csv")

    def test_generator_does_not_infer_type_from_local_name_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hmd = root / "hmd.csv"
            write_csv(
                hmd,
                HMD_HEADER,
                [
                    {
                        "sequence": "1",
                        "module": "cor",
                        "level": "1",
                        "type": "C",
                        "identifier": "",
                        "name": "Root",
                        "datatype": "",
                        "multiplicity": "1",
                        "association_role": "",
                        "definition": "",
                        "label_local": "",
                        "definition_local": "",
                        "source_bsm_id": "T-1",
                        "semantic_path": "$.cor_Root",
                        "associated_module": "",
                        "class_term": "Root",
                        "local_name": "root",
                        "xpath": "/xbrli:xbrl/gl-cor:root",
                    },
                    {
                        "sequence": "2",
                        "module": "cor",
                        "level": "2",
                        "type": "A",
                        "identifier": "",
                        "name": "Email Address",
                        "datatype": "Text",
                        "multiplicity": "0..1",
                        "association_role": "",
                        "definition": "",
                        "label_local": "",
                        "definition_local": "",
                        "source_bsm_id": "T-2",
                        "semantic_path": "$.cor_Root.cor_EmailAddress",
                        "associated_module": "",
                        "class_term": "Root",
                        "local_name": "emailAddress",
                        "xpath": "/xbrli:xbrl/gl-cor:root/gl-cor:emailAddress",
                    },
                ],
            )
            generator = GENERATOR.xBRLGL_TaxonomyGenerator(
                in_file=str(hmd),
                base_dir=str(root / "out"),
                palette=None,
                root=None,
                lang="ja",
                currency="JPY",
                namespace="http://www.xbrl.org/int/gl/2026-12-31/plt",
                encoding="utf-8-sig",
                trace=False,
                debug=False,
                instance=False,
                taxonomy_type="tuple",
            )
            generator.load_csv_data()
            self.assertEqual(
                generator.records[1]["datatype"], "xbrli:stringItemType"
            )
            self.assertEqual(
                generator.records[1]["semantic_datatype"], "Text"
            )


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import csv
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "taxonomy" / "xBRLGL_TaxonomyGenerator.py"
SPEC = importlib.util.spec_from_file_location("v5_taxonomy_generator", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

HEADER = [
    "sequence", "module", "level", "type", "identifier", "name", "datatype",
    "multiplicity", "association_role", "definition", "label_local",
    "definition_local", "source_bsm_id", "semantic_path", "associated_module",
    "class_term", "local_name", "xpath",
]


def row(**values: str) -> dict[str, str]:
    result = {name: "" for name in HEADER}; result.update(values); return result


class V5TaxonomyGeneratorTests(unittest.TestCase):
    def make_generator(self, root: Path, rows: list[dict[str, str]]):
        root.mkdir(parents=True, exist_ok=True)
        source = root / "lhm.csv"; output = root / "out"
        with source.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        generator = MODULE.xBRLGL_TaxonomyGenerator(
            in_file=str(source), base_dir=str(output), palette=None, root=None,
            lang="ja", currency="JPY",
            namespace="http://www.xbrl.org/int/gl/plt/2026-08-08",
            encoding="utf-8-sig", trace=False, debug=False, instance=False,
            taxonomy_type="tuple",
        )
        generator.load_csv_data()
        return generator

    def test_zero_zero_row_and_structural_subtree_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "lhm.csv"; output = root / "out"
            rows = [
                row(sequence="1", module="cor", level="1", type="C", name="Root",
                    multiplicity="1", local_name="root", source_bsm_id="CO01",
                    semantic_path="$.cor_Root", class_term="Root",
                    xpath="/xbrli:xbrl/gl-cor:root"),
                row(sequence="2", module="cor", level="2", type="R", name="Hidden",
                    multiplicity="0..0", local_name="hidden", source_bsm_id="CO02",
                    semantic_path="$.cor_Root.cor_Hidden", class_term="Hidden",
                    xpath="/xbrli:xbrl/gl-cor:root/gl-cor:hidden"),
                row(sequence="3", module="cor", level="3", type="A", name="Child",
                    datatype="String", multiplicity="1", local_name="child",
                    source_bsm_id="CO03", semantic_path="$.cor_Root.cor_Hidden.cor_Child",
                    class_term="Hidden",
                    xpath="/xbrli:xbrl/gl-cor:root/gl-cor:hidden/gl-cor:child"),
                row(sequence="4", module="cor", level="2", type="A", name="Visible",
                    datatype="String", multiplicity="0..1", local_name="visible",
                    source_bsm_id="CO04", semantic_path="$.cor_Root.cor_Visible",
                    class_term="Root", xpath="/xbrli:xbrl/gl-cor:root/gl-cor:visible"),
            ]
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
                writer.writeheader(); writer.writerows(rows)
            generator = MODULE.xBRLGL_TaxonomyGenerator(
                in_file=str(source), base_dir=str(output), palette=None, root=None,
                lang="ja", currency="JPY",
                namespace="http://www.xbrl.org/int/gl/plt/2026-08-05",
                encoding="utf-8-sig", trace=False, debug=False, instance=False,
                taxonomy_type="tuple",
            )
            generator.load_csv_data()
            elements = {item["element"] for item in generator.records}
            self.assertEqual(elements, {"cor:root", "cor:visible"})
            self.assertFalse(any(item["source_bsm_id"] in {"CO02", "CO03"}
                                 for item in generator.records))

    def test_same_source_bsm_id_can_have_occurrence_specific_qnames_and_types(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "lhm.csv"; output = root / "out"
            rows = [
                row(sequence="1", module="cor", level="1", type="C", name="Root",
                    multiplicity="1", local_name="root", source_bsm_id="CO01",
                    semantic_path="$.cor_Root", class_term="Root",
                    xpath="/xbrli:xbrl/gl-cor:root"),
                row(sequence="2", module="cor", level="2", type="C", name="Document",
                    multiplicity="0..1", local_name="document", source_bsm_id="BU10",
                    semantic_path="$.cor_Root.cor_Document", class_term="Document",
                    xpath="/xbrli:xbrl/gl-cor:root/gl-cor:document"),
                row(sequence="3", module="cor", level="2", type="C", name="Header Document",
                    multiplicity="0..1", local_name="headerDocument", source_bsm_id="BU10",
                    semantic_path="$.cor_Root.cor_HeaderDocument", class_term="Document",
                    xpath="/xbrli:xbrl/gl-cor:root/gl-cor:headerDocument"),
            ]
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
                writer.writeheader(); writer.writerows(rows)
            generator = MODULE.xBRLGL_TaxonomyGenerator(
                in_file=str(source), base_dir=str(output), palette=None, root=None,
                lang="ja", currency="JPY",
                namespace="http://www.xbrl.org/int/gl/plt/2026-08-08",
                encoding="utf-8-sig", trace=False, debug=False, instance=False,
                taxonomy_type="tuple",
            )
            generator.load_csv_data()
            reused = [item for item in generator.records if item["source_bsm_id"] == "BU10"]
            self.assertEqual(
                [(item["element"], item["element_type"]) for item in reused],
                [("cor:document", "cor:documentComplexType"),
                 ("cor:headerDocument", "cor:headerDocumentComplexType")],
            )

    def test_shared_qname_identity_separates_declaration_from_hmd_content(self):
        def rows(child: str, source_id: str):
            return [
                row(sequence="1", module="bus", level="1", type="C", name="Party",
                    multiplicity="1", local_name="party", source_bsm_id=source_id,
                    semantic_path=f"$.bus_{source_id}", class_term="Party",
                    xpath="/xbrli:xbrl/gl-bus:party"),
                row(sequence="2", module="bus", level="2", type="A", name="Name",
                    datatype="String", multiplicity="0..1", local_name=child,
                    source_bsm_id=f"{source_id}-P",
                    semantic_path=f"$.bus_{source_id}.bus_Name", class_term="Party",
                    xpath=f"/xbrli:xbrl/gl-bus:party/gl-bus:{child}"),
            ]
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left = self.make_generator(Path(left_dir), rows("partyName", "LEFT"))
            right = self.make_generator(Path(right_dir), rows("partyName", "RIGHT"))
            self.assertEqual(MODULE.validate_shared_qnames([left, right]), 2)
            MODULE.merge_hmd_generators(left, [right])
            left.process_records()
            left.generate_taxonomy_files(left.xbrl_base)
            schema = ET.parse(Path(left.xbrl_base) / "bus" / "bus-2026-08-08.xsd")
            declarations = schema.findall(
                "./{http://www.w3.org/2001/XMLSchema}element[@name='partyName']"
            )
            self.assertEqual(len(declarations), 1)
            structural = schema.findall(
                "./{http://www.w3.org/2001/XMLSchema}element[@name='party']"
            )
            self.assertEqual(structural, [])
            conflict = self.make_generator(Path(right_dir) / "conflict", rows("legalName", "RIGHT"))
            # bus:party is the same reusable declaration, but its effective
            # direct-child model belongs to each independent HMD content
            # schema and is therefore allowed to differ.
            validation_left = self.make_generator(
                Path(left_dir) / "validation-left",
                rows("partyName", "LEFT"),
            )
            self.assertEqual(
                MODULE.validate_shared_qnames([validation_left, conflict]),
                1,
            )

            declaration_conflict_rows = rows("partyName", "RIGHT")
            declaration_conflict_rows[0]["definition"] = "Different definition"
            declaration_conflict = self.make_generator(
                Path(right_dir) / "declaration-conflict",
                declaration_conflict_rows,
            )
            with self.assertRaisesRegex(ValueError, "Shared QName declaration conflict"):
                MODULE.validate_shared_qnames(
                    [validation_left, declaration_conflict]
                )

    def test_xpath_terminal_qname_is_authority_and_must_match_hmd_columns(self):
        base = [
            row(sequence="1", module="cor", level="1", type="C", name="Root",
                multiplicity="1", local_name="root", source_bsm_id="CO01",
                semantic_path="$.cor_Root", class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            generator = self.make_generator(Path(directory), base)
            self.assertEqual(generator.records[0]["element"], "cor:root")
            self.assertEqual(
                generator.records[0]["expanded_name"],
                "{http://www.xbrl.org/int/gl/cor/2026-08-08}root",
            )
        for field, value, message in (
            ("local_name", "different", "terminal local part"),
            ("module", "bus", "terminal namespace"),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                bad = [dict(base[0])]
                bad[0][field] = value
                with self.assertRaisesRegex(SystemExit, "1"):
                    self.make_generator(Path(directory), bad)

    def test_duplicate_effective_qname_in_one_hmd_is_rejected(self):
        rows = [
            row(sequence="1", module="cor", level="1", type="C", name="Root",
                multiplicity="1", local_name="root", source_bsm_id="C1",
                semantic_path="$.root", class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root"),
            row(sequence="2", module="cor", level="2", type="A", name="Identifier",
                datatype="String", multiplicity="0..1", local_name="identifier",
                source_bsm_id="A1", semantic_path="$.root.identifier1",
                class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root/gl-cor:identifier"),
            row(sequence="3", module="cor", level="2", type="A", name="Identifier",
                datatype="String", multiplicity="0..1", local_name="identifier",
                source_bsm_id="A2", semantic_path="$.root.identifier2",
                class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root/gl-cor:identifier"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SystemExit, "1"):
                self.make_generator(Path(directory), rows)

    def test_parent_child_structure_comes_from_formal_xpath(self):
        rows = [
            row(sequence="1", module="cor", level="1", type="C", name="Root",
                multiplicity="1", local_name="root", source_bsm_id="C1",
                semantic_path="$.root", class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root"),
            row(sequence="2", module="cor", level="2", type="C", name="First",
                multiplicity="0..1", local_name="first", source_bsm_id="C2",
                semantic_path="$.root.first", class_term="First",
                xpath="/xbrli:xbrl/gl-cor:root/gl-cor:first"),
            row(sequence="3", module="cor", level="2", type="C", name="Second",
                multiplicity="0..1", local_name="second", source_bsm_id="C3",
                semantic_path="$.root.second", class_term="Second",
                xpath="/xbrli:xbrl/gl-cor:root/gl-cor:second"),
            # This row follows Second in the CSV, but its formal XPath parent
            # is First. A level-stack implementation would attach it wrongly.
            row(sequence="4", module="cor", level="3", type="A", name="Value",
                datatype="String", multiplicity="0..1", local_name="value",
                source_bsm_id="A1", semantic_path="$.root.first.value",
                class_term="First",
                xpath="/xbrli:xbrl/gl-cor:root/gl-cor:first/gl-cor:value"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            generator = self.make_generator(Path(directory), rows)
            self.assertIn("cor_value", generator.presentation_dict["cor_first"])
            self.assertNotIn(
                "cor_value", generator.presentation_dict.get("cor_second", [])
            )
            value = next(r for r in generator.records if r["element"] == "cor:value")
            self.assertEqual(value["parent_id"], "cor_first")
            self.assertEqual(value["class_ancestors"], ["cor_root", "cor_first"])

    def test_presentation_difference_identical_extra_and_missing(self):
        rel = MODULE.PresentationRelationship(
            MODULE.PRESENTATION_ROLE, MODULE.PARENT_CHILD_ARCROLE,
            "cor_parent", "cor_child", 10,
        )
        self.assertEqual(
            MODULE.presentation_difference({rel}, {rel}),
            MODULE.PresentationDifference((), (), 0),
        )
        extra = MODULE.presentation_difference({rel}, set())
        self.assertEqual(extra.prohibited, (rel,))
        self.assertEqual(extra.optional, ())
        missing = MODULE.presentation_difference(set(), {rel})
        self.assertEqual(missing.prohibited, ())
        self.assertEqual(missing.optional, (rel,))

    def test_parent_and_order_changes_prohibit_then_add(self):
        base = MODULE.PresentationRelationship(
            MODULE.PRESENTATION_ROLE, MODULE.PARENT_CHILD_ARCROLE,
            "cor_oldParent", "cor_child", 10,
        )
        expected = MODULE.PresentationRelationship(
            MODULE.PRESENTATION_ROLE, MODULE.PARENT_CHILD_ARCROLE,
            "cor_newParent", "cor_child", 20,
        )
        difference = MODULE.presentation_difference({base}, {expected})
        self.assertEqual(difference.prohibited, (base,))
        self.assertEqual(difference.optional, (expected,))
        self.assertEqual(difference.override_count, 1)

        order_only = MODULE.PresentationRelationship(
            MODULE.PRESENTATION_ROLE, MODULE.PARENT_CHILD_ARCROLE,
            "cor_oldParent", "cor_child", 20,
        )
        difference = MODULE.presentation_difference({base}, {order_only})
        self.assertEqual(difference.prohibited, (base,))
        self.assertEqual(difference.optional, (order_only,))
        self.assertEqual(difference.override_count, 1)

    def test_non_exempt_attributes_and_base_set_affect_equivalence(self):
        base = MODULE.PresentationRelationship(
            MODULE.PRESENTATION_ROLE, MODULE.PARENT_CHILD_ARCROLE,
            "cor_parent", "cor_child", 10, "http://example/old",
        )
        preferred_changed = MODULE.PresentationRelationship(
            MODULE.PRESENTATION_ROLE, MODULE.PARENT_CHILD_ARCROLE,
            "cor_parent", "cor_child", 10, "http://example/new",
        )
        different_role = MODULE.PresentationRelationship(
            "http://example/other-role", MODULE.PARENT_CHILD_ARCROLE,
            "cor_parent", "cor_child", 10, "http://example/old",
        )
        self.assertEqual(
            MODULE.presentation_difference({base}, {preferred_changed}).override_count,
            1,
        )
        role_difference = MODULE.presentation_difference({base}, {different_role})
        self.assertEqual(role_difference.prohibited, (base,))
        self.assertEqual(role_difference.optional, (different_role,))

    def test_priority_and_extension_serialization_are_deterministic(self):
        self.assertEqual(MODULE.next_presentation_priority([]), 1)
        self.assertEqual(MODULE.next_presentation_priority([0, 4, 2]), 5)
        rel = MODULE.PresentationRelationship(
            MODULE.PRESENTATION_ROLE, MODULE.PARENT_CHILD_ARCROLE,
            "cor_parent", "bus_child", 10,
        )
        difference = MODULE.PresentationDifference((rel,), (), 0)
        first = MODULE.serialize_presentation_extension(
            difference, "2026-12-31"
        )
        second = MODULE.serialize_presentation_extension(
            difference, "2026-12-31"
        )
        self.assertEqual(first, second)
        text = first.decode("utf-8")
        self.assertIn('use="prohibited" priority="1" order="10"', text)
        self.assertIn("../../cor/cor-2026-12-31.xsd#cor_parent", text)
        self.assertIn("../../bus/bus-2026-12-31.xsd#bus_child", text)
        self.assertNotIn("\\", text)
        higher_priority = MODULE.PresentationRelationship(
            MODULE.PRESENTATION_ROLE, MODULE.PARENT_CHILD_ARCROLE,
            "cor_parent", "bus_child", 10, priority=4,
        )
        overridden = MODULE.serialize_presentation_extension(
            MODULE.PresentationDifference((higher_priority,), (), 0),
            "2026-12-31",
        ).decode("utf-8")
        self.assertIn('use="prohibited" priority="5" order="10"', overridden)

    def test_oim_presentation_reuses_domain_member_concept_resolution(self):
        rows = [
            row(sequence="1", module="cor", level="1", type="C", name="Root",
                multiplicity="1", local_name="root", source_bsm_id="C1",
                semantic_path="$.root", class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root"),
            row(sequence="2", module="cor", level="2", type="A", name="Code",
                datatype="String", multiplicity="0..1", local_name="code",
                source_bsm_id="A1", semantic_path="$.root.code",
                class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root/gl-cor:code"),
            row(sequence="3", module="bus", level="2", type="R", name="Party",
                multiplicity="0..1", local_name="party", source_bsm_id="R1",
                semantic_path="$.root.party", class_term="Party",
                xpath="/xbrli:xbrl/gl-cor:root/gl-bus:party"),
            row(sequence="4", module="bus", level="3", type="A", name="Name",
                datatype="String", multiplicity="0..1", local_name="name",
                source_bsm_id="A2", semantic_path="$.root.party.name",
                class_term="Party",
                xpath=("/xbrli:xbrl/gl-cor:root/gl-bus:party/"
                       "gl-bus:name")),
            row(sequence="5", module="bus", level="3", type="C", name="Address",
                multiplicity="0..*", local_name="address", source_bsm_id="C2",
                semantic_path="$.root.party.address", class_term="Address",
                xpath=("/xbrli:xbrl/gl-cor:root/gl-bus:party/"
                       "gl-bus:address")),
            row(sequence="6", module="bus", level="4", type="A", name="City",
                datatype="String", multiplicity="0..1", local_name="city",
                source_bsm_id="A3", semantic_path="$.root.party.address.city",
                class_term="Address",
                xpath=("/xbrli:xbrl/gl-cor:root/gl-bus:party/"
                       "gl-bus:address/gl-bus:city")),
        ]
        with tempfile.TemporaryDirectory() as directory:
            generator = self.make_generator(Path(directory), rows)
            relationships = MODULE.oim_presentation_relationships(generator)
            pairs = {
                (item.parent_id, item.child_id, item.order)
                for item in relationships
            }
            self.assertEqual(
                pairs,
                {
                    ("p_cor_root", "cor_code", 10),
                    ("p_cor_root", "bus_name", 20),
                    ("p_cor_root", "p_bus_address", 30),
                    ("p_bus_address", "bus_city", 10),
                },
            )
            self.assertFalse(any("bus_party" in value for pair in pairs
                                 for value in pair[:2]))
            content = MODULE.serialize_presentation_extension(
                MODULE.presentation_difference(frozenset(), relationships),
                "2026-12-31",
                binding="oim",
            ).decode("utf-8")
            self.assertIn(
                "{HMD_PREFIX}-all-oim-2026-12-31.xsd#p_cor_root", content
            )
            self.assertIn(
                "../../bus/bus-2026-12-31.xsd#bus_name", content
            )
            self.assertNotIn("-content-", content)
            self.assertNotIn("p_bus_party", content)

    def test_formal_package_uses_shared_modules_and_hmd_specific_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_set = root / "LHM_for_taxonomy"
            input_set.mkdir()
            for identifier, file_name, root_module, root_local, source_id in (
                (
                    "AccountingEntries",
                    "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv",
                    "cor", "accountingEntries", "AE",
                ),
                (
                    "BusinessTransactions",
                    "XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv",
                    "btx", "businessTransactions", "BT",
                ),
            ):
                source = input_set / file_name
                rows = [
                    row(
                        sequence="1", module=root_module, level="1", type="C",
                        name=root_local, multiplicity="1", local_name=root_local,
                        source_bsm_id=source_id, semantic_path=f"$.{root_local}",
                        class_term=root_local,
                        xpath=f"/xbrli:xbrl/gl-{root_module}:{root_local}",
                    ),
                    row(
                        sequence="2", module="cor", level="2", type="A",
                        name="Identifier", datatype="String", multiplicity="0..1",
                        local_name="identifier", source_bsm_id="SHARED",
                        semantic_path=f"$.{root_local}.identifier",
                        class_term=root_local,
                        xpath=(f"/xbrli:xbrl/gl-{root_module}:{root_local}"
                               "/gl-cor:identifier"),
                    ),
                ]
                with source.open("w", encoding="utf-8-sig", newline="") as handle:
                    writer = csv.DictWriter(
                        handle, fieldnames=HEADER, lineterminator="\n"
                    )
                    writer.writeheader(); writer.writerows(rows)
            output = root / "package"
            args = SimpleNamespace(
                lhm_for_taxonomy=str(input_set), base_dir=str(output),
                lang="ja",
                namespace="http://www.xbrl.org/int/gl/plt/2026-12-31",
                encoding="utf-8-sig", trace=False, debug=False,
            )
            identifiers = MODULE.generate_formal_hmd_package(args)
            self.assertEqual(
                identifiers,
                ["btx_businessTransactions", "cor_accountingEntries"],
            )
            self.assertTrue((output / "cor" / "cor-2026-12-31.xsd").is_file())
            self.assertTrue((output / "cor" / "cor-pre-2026-12-31.xml").is_file())
            self.assertTrue(
                (output / "cor" / "label" / "cor-lab-en-2026-12-31.xml").is_file()
            )
            self.assertTrue(
                (output / "tuple" / "cor_accountingEntries" /
                 "cor-all-2026-12-31.xsd").is_file()
            )
            self.assertTrue(
                (output / "oim" / "btx_businessTransactions" /
                 "btx-all-oim-2026-12-31.xsd").is_file()
            )
            self.assertTrue(
                (output / "oim" / "btx_businessTransactions" /
                 "btx-all-dim-2026-12-31.xml").is_file()
            )
            self.assertTrue(
                (output / "oim" / "btx_businessTransactions" /
                 "btx-all-pre-2026-12-31.xml").is_file()
            )
            self.assertTrue(
                (output / "tuple" / "cor_accountingEntries" /
                 "cor-all-pre-2026-12-31.xml").is_file()
            )
            self.assertTrue(
                (output / "tuple" / "btx_businessTransactions" /
                 "btx-all-pre-2026-12-31.xml").is_file()
            )
            self.assertFalse((output / "all").exists())
            self.assertFalse((output / "presentation").exists())
            shared_cor_schema = (
                output / "cor" / "cor-2026-12-31.xsd"
            ).read_text(encoding="utf-8-sig")
            self.assertIn(
                '<complexType name="identifierItemType">', shared_cor_schema
            )
            self.assertNotIn("accountingEntriesComplexType", shared_cor_schema)
            self.assertNotIn('name="accountingEntries"', shared_cor_schema)
            self.assertIn('type="cor:identifierItemType"', shared_cor_schema)

            accounting_content = (
                output / "tuple" / "cor_accountingEntries" /
                "cor-content-2026-12-31.xsd"
            ).read_text(encoding="utf-8")
            self.assertIn(
                '<include schemaLocation="../../cor/cor-2026-12-31.xsd"/>',
                accounting_content,
            )
            self.assertIn(
                '<import namespace="http://www.xbrl.org/2003/instance" '
                'schemaLocation="http://www.xbrl.org/2003/'
                'xbrl-instance-2003-12-31.xsd"/>',
                accounting_content,
            )
            content_schemas = sorted(
                (output / "tuple").glob("*/*-content-2026-12-31.xsd")
            )
            self.assertTrue(content_schemas)
            for content_schema in content_schemas:
                with self.subTest(content_schema=content_schema.name):
                    content_text = content_schema.read_text(encoding="utf-8")
                    self.assertEqual(
                        content_text.count(
                            '<import namespace="http://www.xbrl.org/2003/instance" '
                            'schemaLocation="http://www.xbrl.org/2003/'
                            'xbrl-instance-2003-12-31.xsd"/>'
                        ),
                        1,
                    )
            self.assertIn(
                '<complexType name="accountingEntriesComplexType">',
                accounting_content,
            )
            self.assertIn(
                'name="accountingEntries" id="cor_accountingEntries"',
                accounting_content,
            )
            self.assertNotIn('identifierItemType', accounting_content)

            transactions_cor_content = (
                output / "tuple" / "btx_businessTransactions" /
                "cor-content-2026-12-31.xsd"
            ).read_text(encoding="utf-8")
            self.assertNotIn('identifierItemType', transactions_cor_content)
            self.assertNotIn(
                '<complexType name="accountingEntriesComplexType">',
                transactions_cor_content,
            )
            all_entry = (output / "tuple" / "cor_accountingEntries" /
                         "cor-all-2026-12-31.xsd")
            entry_text = all_entry.read_text(encoding="utf-8")
            self.assertIn("../../cor/cor-pre-2026-12-31.xml", entry_text)
            self.assertIn("cor-all-pre-2026-12-31.xml", entry_text)
            self.assertNotIn("../../presentation/", entry_text)
            self.assertNotIn("../../all/", entry_text)
            self.assertIn("../../cor/label/cor-lab-en-2026-12-31.xml", entry_text)
            self.assertIn("../../cor/label/cor-lab-ja-2026-12-31.xml", entry_text)
            oim_entry = (
                output / "oim" / "cor_accountingEntries" /
                "cor-all-oim-2026-12-31.xsd"
            ).read_text(encoding="utf-8")
            self.assertNotIn("-content-", oim_entry)
            self.assertNotIn("ComplexType", oim_entry)
            self.assertIn('name="h_cor_accountingEntries"', oim_entry)
            self.assertIn('name="d_cor_accountingEntries"', oim_entry)
            self.assertIn('name="p_cor_accountingEntries"', oim_entry)
            self.assertIn("../../cor/cor-pre-2026-12-31.xml", oim_entry)
            self.assertIn("cor-all-pre-2026-12-31.xml", oim_entry)
            self.assertNotIn("../../presentation/", oim_entry)
            self.assertNotIn("-content-", oim_entry)
            oim_presentation = (
                output / "oim" / "cor_accountingEntries" /
                "cor-all-pre-2026-12-31.xml"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "cor-all-oim-2026-12-31.xsd#p_cor_accountingEntries",
                oim_presentation,
            )
            self.assertIn(
                "../../cor/cor-2026-12-31.xsd#cor_identifier",
                oim_presentation,
            )
            self.assertNotIn("-content-", oim_presentation)

    def test_lhm_for_taxonomy_directory_is_the_only_formal_package_input(self):
        """The first edition accepts one directory and reads HMDs directly."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_set = root / "LHM_for_taxonomy"
            input_set.mkdir()
            sources = []
            for file_name, root_module, root_local, source_id in (
                (
                    "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv",
                    "cor", "accountingEntries", "AE",
                ),
                (
                    "XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv",
                    "btx", "businessTransactions", "BT",
                ),
            ):
                source = input_set / file_name
                rows = [
                    row(
                        sequence="1", module=root_module, level="1", type="C",
                        name=root_local, multiplicity="1", local_name=root_local,
                        source_bsm_id=source_id, semantic_path=f"$.{root_local}",
                        class_term=root_local,
                        xpath=f"/xbrli:xbrl/gl-{root_module}:{root_local}",
                    ),
                    row(
                        sequence="2", module="cor", level="2", type="A",
                        name="Identifier", datatype="String", multiplicity="0..1",
                        local_name="identifier", source_bsm_id="SHARED",
                        semantic_path=f"$.{root_local}.identifier",
                        class_term=root_local,
                        xpath=(f"/xbrli:xbrl/gl-{root_module}:{root_local}"
                               "/gl-cor:identifier"),
                    ),
                ]
                with source.open("w", encoding="utf-8-sig", newline="") as handle:
                    writer = csv.DictWriter(
                        handle, fieldnames=HEADER, lineterminator="\n"
                    )
                    writer.writeheader(); writer.writerows(rows)
                sources.append(source)

            # manifest.csv is execution-confirmation only.  Deliberately use
            # content that is not the historical manifest schema to prove that
            # taxonomy generation neither requires nor consumes it.
            manifest = input_set / "manifest.csv"
            manifest.write_text(
                "execution_confirmation,only\nnot,a,taxonomy,input\n",
                encoding="utf-8",
            )

            resolved = MODULE.resolve_lhm_for_taxonomy_input(
                str(input_set), "utf-8-sig"
            )
            self.assertEqual(
                [Path(item).name for item in resolved],
                [
                    "XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv",
                    "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv",
                ],
            )

            args = SimpleNamespace(
                lhm_for_taxonomy=str(input_set), base_dir=str(root / "package"),
                lang="ja",
                namespace="http://www.xbrl.org/int/gl/plt/2026-12-31",
                encoding="utf-8-sig", trace=False, debug=False,
            )
            identifiers = MODULE.generate_formal_hmd_package(args)
            self.assertEqual(
                identifiers,
                ["btx_businessTransactions", "cor_accountingEntries"],
            )

            for invalid in [sources[0], manifest]:
                with self.subTest(invalid=invalid.name):
                    with self.assertRaisesRegex(
                        ValueError,
                        "requires one LHM_for_taxonomy directory",
                    ):
                        MODULE.resolve_lhm_for_taxonomy_input(
                            str(invalid), "utf-8-sig"
                        )

    def test_lhm_for_taxonomy_rejects_non_hmd_csv(self):
        """Every CSV other than manifest.csv must satisfy the formal HMD contract."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_set = root / "LHM_for_taxonomy"
            input_set.mkdir()
            (input_set / "notes.csv").write_text(
                "name,value\nnot,an HMD\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "Formal HMD header mismatch"):
                MODULE.resolve_lhm_for_taxonomy_input(
                    str(input_set), "utf-8-sig"
                )

            (input_set / "notes.csv").unlink()
            (input_set / "manifest.csv").write_text(
                "execution confirmation only\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "contains no HMD-for-taxonomy"):
                MODULE.resolve_lhm_for_taxonomy_input(
                    str(input_set), "utf-8-sig"
                )

    def test_formal_package_is_hmd_filename_and_manifest_independent(self):
        """HMD root identity, not file name or manifest, determines processing."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            specs = {
                "AccountingEntries": (
                    "cor", "accountingEntries", "AE",
                ),
                "BusinessTransactions": (
                    "btx", "businessTransactions", "BT",
                ),
            }

            def generate(output, input_set, file_names, create_order, add_manifest):
                input_set.mkdir()
                for identifier in create_order:
                    root_module, root_local, source_id = specs[identifier]
                    source = input_set / file_names[identifier]
                    rows = [
                        row(
                            sequence="1", module=root_module, level="1", type="C",
                            name=root_local, multiplicity="1", local_name=root_local,
                            source_bsm_id=source_id,
                            semantic_path=f"$.{root_local}", class_term=root_local,
                            xpath=f"/xbrli:xbrl/gl-{root_module}:{root_local}",
                        ),
                        row(
                            sequence="2", module="cor", level="2", type="A",
                            name="Identifier", datatype="String",
                            multiplicity="0..1", local_name="identifier",
                            source_bsm_id="SHARED",
                            semantic_path=f"$.{root_local}.identifier",
                            class_term=root_local,
                            xpath=(f"/xbrli:xbrl/gl-{root_module}:{root_local}"
                                   "/gl-cor:identifier"),
                        ),
                    ]
                    with source.open(
                        "w", encoding="utf-8-sig", newline=""
                    ) as handle:
                        writer = csv.DictWriter(
                            handle, fieldnames=HEADER, lineterminator="\n"
                        )
                        writer.writeheader(); writer.writerows(rows)
                if add_manifest:
                    (input_set / "manifest.csv").write_text(
                        "arbitrary,execution,confirmation\nignored,by,generator\n",
                        encoding="utf-8",
                    )
                args = SimpleNamespace(
                    lhm_for_taxonomy=str(input_set), base_dir=str(output),
                    lang="ja",
                    namespace="http://www.xbrl.org/int/gl/plt/2026-12-31",
                    encoding="utf-8-sig", trace=False, debug=False,
                )
                MODULE.generate_formal_hmd_package(args)
                return {
                    path.relative_to(output).as_posix():
                    hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in sorted(output.rglob("*")) if path.is_file()
                }

            first = generate(
                root / "package-first",
                root / "LHM_for_taxonomy_first",
                {
                    "AccountingEntries": "z-accounting.csv",
                    "BusinessTransactions": "a-business.csv",
                },
                ("BusinessTransactions", "AccountingEntries"),
                True,
            )
            second = generate(
                root / "package-second",
                root / "LHM_for_taxonomy_second",
                {
                    "AccountingEntries": "a-accounting.csv",
                    "BusinessTransactions": "z-business.csv",
                },
                ("AccountingEntries", "BusinessTransactions"),
                False,
            )
            self.assertEqual(set(first), set(second))
            self.assertEqual(first, second)
            self.assertTrue(first)


if __name__ == "__main__":
    unittest.main()

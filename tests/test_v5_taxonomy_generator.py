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
    def make_generator(
        self, root: Path, rows: list[dict[str, str]], namespace_prefix_map=None
    ):
        root.mkdir(parents=True, exist_ok=True)
        source = root / "lhm.csv"; output = root / "out"
        with source.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        generator = MODULE.xBRLGL_TaxonomyGenerator(
            in_file=str(source), base_dir=str(output), palette=None, root=None,
            lang="ja", currency="JPY",
            namespace="http://www.xbrl.org/int/gl/2026-08-08/plt",
            encoding="utf-8-sig", trace=False, debug=False, instance=False,
            taxonomy_type="tuple",
            namespace_prefix_map=namespace_prefix_map,
        )
        generator.load_csv_data()
        return generator

    def test_explicit_xpath_prefix_maps_to_hmd_module_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = [
                row(
                    sequence="1", module="en16931", level="1", type="C",
                    name="Invoice", multiplicity="1", local_name="Invoice",
                    source_bsm_id="BG-00", semantic_path="$.invoice",
                    class_term="Invoice", xpath="/xbrli:xbrl/en:Invoice",
                ),
                row(
                    sequence="2", module="en16931", level="2", type="A",
                    name="Invoice number", datatype="String", multiplicity="1..1",
                    local_name="InvoiceNumber", source_bsm_id="BT-1",
                    semantic_path="$.invoice.invoiceNumber", class_term="Invoice",
                    xpath="/xbrli:xbrl/en:Invoice/en:InvoiceNumber",
                ),
            ]
            generator = self.make_generator(
                Path(directory), rows, {"en": "en16931"}
            )
            self.assertEqual(
                [record["element"] for record in generator.records],
                ["en16931:Invoice", "en16931:InvoiceNumber"],
            )
            self.assertEqual(
                generator.records[1]["expanded_name"],
                "{http://www.xbrl.org/int/gl/2026-08-08/en16931}InvoiceNumber",
            )

    def test_unmapped_non_gl_xpath_prefix_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = [
                row(
                    sequence="1", module="en16931", level="1", type="C",
                    name="Invoice", multiplicity="1", local_name="Invoice",
                    source_bsm_id="BG-00", semantic_path="$.invoice",
                    class_term="Invoice", xpath="/xbrli:xbrl/en:Invoice",
                )
            ]
            with self.assertRaises(SystemExit):
                self.make_generator(Path(directory), rows)

    def test_conventional_gl_prefix_resolution_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = [
                row(
                    sequence="1", module="cor", level="1", type="C",
                    name="Root", multiplicity="1", local_name="root",
                    source_bsm_id="CO01", semantic_path="$.cor_Root",
                    class_term="Root", xpath="/xbrli:xbrl/gl-cor:root",
                )
            ]
            generator = self.make_generator(Path(directory), rows)
            self.assertEqual(generator.records[0]["element"], "cor:root")
            self.assertEqual(
                generator.records[0]["expanded_name"],
                "{http://www.xbrl.org/int/gl/2026-08-08/cor}root",
            )

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
                namespace="http://www.xbrl.org/int/gl/2026-08-05/plt",
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
                namespace="http://www.xbrl.org/int/gl/2026-08-08/plt",
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

    def test_shared_qname_requires_one_module_declaration_and_content_model(self):
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
            item = schema.findall(
                "./{http://www.w3.org/2001/XMLSchema}element[@name='partyName']"
            )
            self.assertEqual(len(item), 1)
            structural = schema.findall(
                "./{http://www.w3.org/2001/XMLSchema}element[@name='party']"
            )
            self.assertEqual(len(structural), 1)
            self.assertEqual(
                structural[0].attrib.get("type"), "bus:partyComplexType"
            )

            # Same structural QName with a different direct-child signature is
            # not a shared Palette declaration and must be rejected.
            conflict = self.make_generator(
                Path(right_dir) / "content-conflict", rows("legalName", "RIGHT")
            )
            validation_left = self.make_generator(
                Path(left_dir) / "validation-left", rows("partyName", "LEFT")
            )
            with self.assertRaisesRegex(
                ValueError, "Shared QName declaration/content conflict"
            ):
                MODULE.validate_shared_qnames([validation_left, conflict])

            declaration_conflict_rows = rows("partyName", "RIGHT")
            declaration_conflict_rows[0]["definition"] = "Different definition"
            declaration_conflict = self.make_generator(
                Path(right_dir) / "declaration-conflict",
                declaration_conflict_rows,
            )
            with self.assertRaisesRegex(
                ValueError, "Shared QName declaration/content conflict"
            ):
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
                "{http://www.xbrl.org/int/gl/2026-08-08/cor}root",
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

    def test_module_presentation_recurses_from_module_C_and_R_and_uses_module_schemas(self):
        rows = [
            row(sequence="1", module="cor", level="1", type="C", name="Root",
                multiplicity="1", local_name="root", source_bsm_id="C1",
                semantic_path="$.root", class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root"),
            row(sequence="2", module="bus", level="2", type="R", name="Party Reference",
                multiplicity="0..1", local_name="partyReference", source_bsm_id="R1",
                semantic_path="$.root.partyReference", class_term="Party",
                xpath="/xbrli:xbrl/gl-cor:root/gl-bus:partyReference"),
            row(sequence="3", module="bus", level="3", type="A", name="Party Identifier",
                datatype="String", multiplicity="1", local_name="partyIdentifier",
                source_bsm_id="A1", semantic_path="$.root.partyReference.partyIdentifier",
                class_term="Party",
                xpath=("/xbrli:xbrl/gl-cor:root/gl-bus:partyReference/"
                       "gl-bus:partyIdentifier")),
        ]
        with tempfile.TemporaryDirectory() as directory:
            generator = self.make_generator(Path(directory), rows)
            generator.process_records()
            generator.generate_taxonomy_files(generator.xbrl_base)

            cor_pre = (
                Path(generator.xbrl_base) / "cor" /
                "cor-2026-08-08-presentation.xml"
            ).read_text(encoding="utf-8")
            bus_pre = (
                Path(generator.xbrl_base) / "bus" /
                "bus-2026-08-08-presentation.xml"
            ).read_text(encoding="utf-8")

            # C-root traversal continues across a module boundary through R.
            self.assertIn('cor-2026-08-08.xsd#cor_root', cor_pre)
            self.assertIn(
                '../bus/bus-2026-08-08.xsd#bus_partyReference', cor_pre
            )
            self.assertIn(
                '../bus/bus-2026-08-08.xsd#bus_partyIdentifier', cor_pre
            )
            self.assertIn(
                'xlink:from="cor_root" xlink:to="bus_partyReference"', cor_pre
            )
            self.assertIn(
                'xlink:from="bus_partyReference" '
                'xlink:to="bus_partyIdentifier"', cor_pre
            )
            self.assertNotIn('-content-', cor_pre)

            # R is itself a starting candidate in its owning module forest.
            self.assertIn(
                'bus-2026-08-08.xsd#bus_partyReference', bus_pre
            )
            self.assertIn(
                'bus-2026-08-08.xsd#bus_partyIdentifier', bus_pre
            )
            self.assertIn(
                'xlink:from="bus_partyReference" '
                'xlink:to="bus_partyIdentifier"', bus_pre
            )
            self.assertNotIn('-content-', bus_pre)

    def test_link_presentation_visited_keeps_distinct_incoming_arcs_and_one_subtree(self):
        rows = [
            row(sequence="1", module="cor", level="1", type="C", name="Parent A",
                multiplicity="1", local_name="parentA", source_bsm_id="C1",
                semantic_path="$.parentA", class_term="Parent A",
                xpath="/xbrli:xbrl/gl-cor:parentA"),
            row(sequence="2", module="cor", level="2", type="C", name="Parent B",
                multiplicity="0..1", local_name="parentB", source_bsm_id="C2",
                semantic_path="$.parentA.parentB", class_term="Parent B",
                xpath="/xbrli:xbrl/gl-cor:parentA/gl-cor:parentB"),
            row(sequence="3", module="cor", level="3", type="C", name="Shared Child",
                multiplicity="0..1", local_name="sharedChild", source_bsm_id="C3",
                semantic_path="$.parentA.parentB.sharedChild",
                class_term="Shared Child",
                xpath=("/xbrli:xbrl/gl-cor:parentA/gl-cor:parentB/"
                       "gl-cor:sharedChild")),
            row(sequence="4", module="cor", level="4", type="A", name="Leaf",
                datatype="String", multiplicity="0..1", local_name="leaf",
                source_bsm_id="A1",
                semantic_path="$.parentA.parentB.sharedChild.leaf",
                class_term="Shared Child",
                xpath=("/xbrli:xbrl/gl-cor:parentA/gl-cor:parentB/"
                       "gl-cor:sharedChild/gl-cor:leaf")),
        ]
        with tempfile.TemporaryDirectory() as directory:
            generator = self.make_generator(Path(directory), rows)

            # Exercise linkPresentation directly with two different incoming
            # arcs to the same structural child.  The child subtree is expanded
            # once by visited, but both incoming arcs remain.
            generator.presentation_dict = {
                "cor_sharedChild": ["cor_leaf"],
            }
            generator.lines = []
            generator.locs_defined = {}
            generator.arcs_defined = {}
            visited = set()

            generator.linkPresentation(
                "cor", "cor_parentA", ["cor_sharedChild"], 1, visited
            )
            generator.linkPresentation(
                "cor", "cor_parentB", ["cor_sharedChild"], 1, visited
            )
            rendered = "".join(generator.lines)

            self.assertEqual(
                rendered.count('xlink:href="cor-2026-08-08.xsd#cor_sharedChild"'),
                1,
            )
            self.assertEqual(
                rendered.count('xlink:href="cor-2026-08-08.xsd#cor_leaf"'),
                1,
            )
            self.assertEqual(
                rendered.count(
                    'xlink:from="cor_parentA" xlink:to="cor_sharedChild"'
                ),
                1,
            )
            self.assertEqual(
                rendered.count(
                    'xlink:from="cor_parentB" xlink:to="cor_sharedChild"'
                ),
                1,
            )
            self.assertEqual(
                rendered.count(
                    'xlink:from="cor_sharedChild" xlink:to="cor_leaf"'
                ),
                1,
            )

    def test_oim_module_presentation_uses_p_items_and_traverses_R_transparently(self):
        rows = [
            row(sequence="1", module="cor", level="1", type="C", name="Root",
                multiplicity="1", local_name="root", source_bsm_id="C1",
                semantic_path="$.root", class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root"),
            row(sequence="2", module="bus", level="2", type="R",
                name="Party Reference", multiplicity="0..1",
                local_name="partyReference", source_bsm_id="R1",
                semantic_path="$.root.partyReference", class_term="Party",
                xpath="/xbrli:xbrl/gl-cor:root/gl-bus:partyReference"),
            row(sequence="3", module="bus", level="3", type="A",
                name="Party Identifier", datatype="String", multiplicity="1",
                local_name="partyIdentifier", source_bsm_id="A1",
                semantic_path="$.root.partyReference.partyIdentifier",
                class_term="Party",
                xpath=("/xbrli:xbrl/gl-cor:root/gl-bus:partyReference/"
                       "gl-bus:partyIdentifier")),
        ]
        with tempfile.TemporaryDirectory() as directory:
            generator = self.make_generator(Path(directory), rows)
            generator.taxonomy_type = "shared"
            generator.process_records()
            generator.generate_taxonomy_files(generator.xbrl_base)

            cor_oim = (
                Path(generator.xbrl_base) / "cor" /
                "cor-oim-2026-08-08.xsd"
            ).read_text(encoding="utf-8-sig")
            self.assertIn('name="p_cor_root"', cor_oim)
            self.assertNotIn('substitutionGroup="xbrli:tuple"', cor_oim)

            cor_oim_pre = (
                Path(generator.xbrl_base) / "cor" /
                "cor-oim-2026-08-08-presentation.xml"
            ).read_text(encoding="utf-8")
            self.assertIn(
                'cor-oim-2026-08-08.xsd#p_cor_root',
                cor_oim_pre,
            )
            self.assertIn(
                '../bus/bus-oim-2026-08-08.xsd#bus_partyIdentifier',
                cor_oim_pre,
            )
            self.assertNotIn("bus_partyReference", cor_oim_pre)
            self.assertIn(
                'xlink:from="p_cor_root" xlink:to="bus_partyIdentifier"',
                cor_oim_pre,
            )

            bus_oim = (
                Path(generator.xbrl_base) / "bus" /
                "bus-oim-2026-08-08.xsd"
            ).read_text(encoding="utf-8-sig")
            self.assertNotIn("p_bus_partyReference", bus_oim)
            self.assertNotIn('substitutionGroup="xbrli:tuple"', bus_oim)

    def test_oim_dimensions_follow_occurrence_key_class_lineage(self):
        rows = [
            row(sequence="1", module="cor", level="1", type="C",
                name="Invoice", multiplicity="1", local_name="invoice",
                source_bsm_id="C1", semantic_path="$.invoice",
                class_term="Invoice", xpath="/xbrli:xbrl/gl-cor:invoice"),
            row(sequence="2", module="cor", level="2", type="C",
                name="Invoice Line", multiplicity="1..*",
                local_name="invoiceLine", source_bsm_id="C2",
                semantic_path="$.invoice.invoiceLine", class_term="Invoice Line",
                xpath="/xbrli:xbrl/gl-cor:invoice/gl-cor:invoiceLine"),
            row(sequence="3", module="cor", level="3", type="R",
                name="Item Reference", multiplicity="1..1",
                local_name="itemReference", source_bsm_id="R1",
                semantic_path="$.invoice.invoiceLine.itemReference",
                class_term="Item Information",
                xpath=("/xbrli:xbrl/gl-cor:invoice/gl-cor:invoiceLine/"
                       "gl-cor:itemReference")),
            row(sequence="4", module="cor", level="4", type="C",
                name="Item Information", multiplicity="1..1",
                local_name="itemInformation", source_bsm_id="C3",
                semantic_path=("$.invoice.invoiceLine.itemReference."
                               "itemInformation"),
                class_term="Item Information",
                xpath=("/xbrli:xbrl/gl-cor:invoice/gl-cor:invoiceLine/"
                       "gl-cor:itemReference/gl-cor:itemInformation")),
            row(sequence="5", module="cor", level="5", type="C",
                name="Item Attributes", multiplicity="0..*",
                local_name="itemAttributes", source_bsm_id="C4",
                semantic_path=("$.invoice.invoiceLine.itemReference."
                               "itemInformation.itemAttributes"),
                class_term="Item Attributes",
                xpath=("/xbrli:xbrl/gl-cor:invoice/gl-cor:invoiceLine/"
                       "gl-cor:itemReference/gl-cor:itemInformation/"
                       "gl-cor:itemAttributes")),
            row(sequence="6", module="cor", level="6", type="A",
                name="Item Attribute Name", datatype="String",
                multiplicity="1", local_name="itemAttributeName",
                source_bsm_id="A1",
                semantic_path=("$.invoice.invoiceLine.itemReference."
                               "itemInformation.itemAttributes."
                               "itemAttributeName"),
                class_term="Item Attributes",
                xpath=("/xbrli:xbrl/gl-cor:invoice/gl-cor:invoiceLine/"
                       "gl-cor:itemReference/gl-cor:itemInformation/"
                       "gl-cor:itemAttributes/gl-cor:itemAttributeName")),
        ]
        with tempfile.TemporaryDirectory() as directory:
            generator = self.make_generator(Path(directory), rows)
            generator.taxonomy_type = "oim"
            generator.process_records()

            classes = {
                record["element_id"]: record for record in generator.records
                if record["type"] == "C"
            }
            self.assertTrue(generator.is_occurrence_key_class(classes["cor_invoice"]))
            self.assertTrue(
                generator.is_occurrence_key_class(classes["cor_invoiceLine"])
            )
            self.assertFalse(
                generator.is_occurrence_key_class(classes["cor_itemInformation"])
            )
            self.assertTrue(
                generator.is_occurrence_key_class(classes["cor_itemAttributes"])
            )

            generator.generate_taxonomy_files(generator.xbrl_base)
            palette = (
                Path(generator.xbrl_base) / "plt" / "plt-oim-2026-08-08.xsd"
            ).read_text(encoding="utf-8-sig")
            for class_name in (
                "cor_invoice", "cor_invoiceLine", "cor_itemInformation",
                "cor_itemAttributes",
            ):
                self.assertIn(f'name="h_{class_name}"', palette)
                self.assertIn(f'id="link_{class_name}"', palette)
            for class_name in (
                "cor_invoice", "cor_invoiceLine", "cor_itemAttributes",
            ):
                self.assertIn(f'name="d_{class_name}"', palette)
            self.assertNotIn('name="d_cor_itemInformation"', palette)
            self.assertEqual(
                palette.count('substitutionGroup="xbrldt:dimensionItem"'), 3
            )
            self.assertEqual(palette.count('xbrldt:typedDomainRef="#_v"'), 3)

            module_oim = (
                Path(generator.xbrl_base) / "cor" / "cor-oim-2026-08-08.xsd"
            ).read_text(encoding="utf-8-sig")
            for class_name in (
                "cor_invoice", "cor_invoiceLine", "cor_itemInformation",
                "cor_itemAttributes",
            ):
                self.assertIn(f'name="p_{class_name}"', module_oim)

            definition = (
                Path(generator.xbrl_base) / "plt" / "plt-def-2026-08-08.xml"
            ).read_text(encoding="utf-8-sig")
            role_start = definition.index(
                'role/link_cor_itemAttributes">'
            )
            role_end = definition.index("</link:definitionLink>", role_start)
            item_attributes_cube = definition[role_start:role_end]
            dimension_targets = [
                'xlink:to="d_cor_invoice"',
                'xlink:to="d_cor_invoiceLine"',
                'xlink:to="d_cor_itemAttributes"',
            ]
            for target in dimension_targets:
                self.assertEqual(item_attributes_cube.count(target), 1)
            self.assertNotIn("d_cor_itemInformation", item_attributes_cube)
            self.assertEqual(
                item_attributes_cube.count(
                    'arcrole="http://xbrl.org/int/dim/arcrole/'
                    'hypercube-dimension"'
                ),
                3,
            )
            for target_role in (
                "link_cor_invoiceLine", "link_cor_itemInformation",
                "link_cor_itemAttributes",
            ):
                self.assertIn(f'targetRole="http://www.xbrl.org/xbrl-gl/role/{target_role}"', definition)

    def test_occurrence_key_classifier_rejects_unsupported_class_multiplicity(self):
        cases = (
            ("1", "", True),
            ("1..1", "", True),
            ("1", "parent", False),
            ("1..1", "parent", False),
            ("0..1", "parent", False),
            ("0..*", "parent", True),
            ("1..*", "parent", True),
        )
        for multiplicity, parent_path_key, expected in cases:
            with self.subTest(
                multiplicity=multiplicity, parent_path_key=parent_path_key
            ):
                self.assertEqual(
                    MODULE.xBRLGL_TaxonomyGenerator.is_occurrence_key_class(
                        {
                            "type": "C",
                            "multiplicity": multiplicity,
                            "parent_path_key": parent_path_key,
                        }
                    ),
                    expected,
                )
        with self.assertRaisesRegex(ValueError, "Unsupported Class multiplicity"):
            MODULE.xBRLGL_TaxonomyGenerator.is_occurrence_key_class(
                {"type": "C", "multiplicity": "2..4", "parent_path_key": "p"}
            )

    def test_module_schema_owns_structural_declaration_content_schema_owns_type(self):
        rows = [
            row(sequence="1", module="cor", level="1", type="C", name="Root",
                multiplicity="1", local_name="root", source_bsm_id="C1",
                semantic_path="$.root", class_term="Root",
                xpath="/xbrli:xbrl/gl-cor:root"),
            row(sequence="2", module="cor", level="2", type="A", name="Code",
                datatype="String", multiplicity="0..1", local_name="code",
                source_bsm_id="A1", semantic_path="$.root.code",
                class_term="Root", xpath="/xbrli:xbrl/gl-cor:root/gl-cor:code"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            generator = self.make_generator(Path(directory), rows)
            generator.shared_structural_type_models = MODULE.collect_shared_structural_type_models(generator)
            generator.process_records()
            generator.generate_taxonomy_files(generator.xbrl_base)
            module_schema = (Path(generator.xbrl_base) / "cor" /
                             "cor-2026-08-08.xsd").read_text(encoding="utf-8-sig")
            content_schema = (Path(generator.xbrl_base) / "plt" /
                              "cor-content-2026-08-08.xsd").read_text(encoding="utf-8")
            self.assertIn(
                'name="root" id="cor_root" type="cor:rootComplexType" '
                'substitutionGroup="xbrli:tuple"', module_schema
            )
            self.assertNotIn('<complexType name="rootComplexType">', module_schema)
            self.assertIn('<include schemaLocation="../cor/cor-2026-08-08.xsd"/>', content_schema)
            self.assertIn('<complexType name="rootComplexType">', content_schema)
            self.assertNotIn('name="root" id="cor_root"', content_schema)

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
                namespace="http://www.xbrl.org/int/gl/2026-12-31/plt",
                encoding="utf-8-sig", trace=False, debug=False,
            )
            identifiers = MODULE.generate_formal_hmd_package(args)
            self.assertEqual(
                identifiers,
                ["btx_businessTransactions", "cor_accountingEntries"],
            )
            self.assertFalse(
                any(
                    path.read_bytes().startswith(b"\xef\xbb\xbf")
                    for path in output.rglob("*")
                    if path.is_file()
                )
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
            self.assertFalse(any(output.rglob("*-all-pre-2026-12-31.xml")))
            self.assertFalse((output / "all").exists())
            self.assertFalse((output / "presentation").exists())
            shared_cor_schema = (
                output / "cor" / "cor-2026-12-31.xsd"
            ).read_text(encoding="utf-8-sig")
            self.assertIn(
                '<complexType name="identifierItemType">', shared_cor_schema
            )
            self.assertIn(
                'name="accountingEntries" id="cor_accountingEntries" '
                'type="cor:accountingEntriesComplexType" '
                'substitutionGroup="xbrli:tuple"',
                shared_cor_schema,
            )
            self.assertNotIn(
                '<complexType name="accountingEntriesComplexType">',
                shared_cor_schema,
            )
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
            self.assertNotIn(
                'name="accountingEntries" id="cor_accountingEntries"',
                accounting_content,
            )
            self.assertNotIn('identifierItemType', accounting_content)

            transactions_cor_content = (
                output / "tuple" / "btx_businessTransactions" /
                "cor-content-2026-12-31.xsd"
            ).read_text(encoding="utf-8")
            self.assertNotIn('identifierItemType', transactions_cor_content)
            self.assertIn(
                '<complexType name="accountingEntriesComplexType">',
                transactions_cor_content,
            )
            all_entry = (output / "tuple" / "cor_accountingEntries" /
                         "cor-all-2026-12-31.xsd")
            entry_text = all_entry.read_text(encoding="utf-8")
            self.assertIn("../../cor/cor-pre-2026-12-31.xml", entry_text)
            self.assertNotIn("-all-pre-2026-12-31.xml", entry_text)
            self.assertNotIn("../../bus/bus-pre-2026-12-31.xml", entry_text)
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
            # HMD-specific OIM entry points retain h_/d_ declarations,
            # while Class primary-item anchors move to module-level OIM schemas.
            self.assertNotIn('name="p_cor_accountingEntries"', oim_entry)
            self.assertIn(
                'schemaLocation="../../cor/cor-oim-2026-12-31.xsd"',
                oim_entry,
            )
            self.assertIn(
                "../../cor/label/cor-oim-lab-en-2026-12-31.xml",
                oim_entry,
            )
            self.assertIn(
                "../../cor/label/cor-oim-lab-ja-2026-12-31.xml",
                oim_entry,
            )
            self.assertIn(
                "../../cor/cor-oim-pre-2026-12-31.xml",
                oim_entry,
            )
            self.assertNotIn("../../cor/cor-pre-2026-12-31.xml", oim_entry)
            self.assertNotIn("-all-pre-2026-12-31.xml", oim_entry)
            self.assertNotIn("../../presentation/", oim_entry)
            self.assertNotIn("-content-", oim_entry)

            self.assertTrue(
                (output / "cor" / "cor-oim-2026-12-31.xsd").is_file()
            )
            self.assertTrue(
                (output / "cor" / "cor-oim-pre-2026-12-31.xml").is_file()
            )
            self.assertTrue(
                (output / "cor" / "label" /
                 "cor-oim-lab-en-2026-12-31.xml").is_file()
            )
            self.assertTrue(
                (output / "cor" / "label" /
                 "cor-oim-lab-ja-2026-12-31.xml").is_file()
            )

            tuple_module_presentation = (
                output / "cor" / "cor-pre-2026-12-31.xml"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "cor-2026-12-31.xsd#cor_accountingEntries",
                tuple_module_presentation,
            )
            self.assertNotIn("-content-", tuple_module_presentation)

            oim_module_schema_text = (
                output / "cor" / "cor-oim-2026-12-31.xsd"
            ).read_text(encoding="utf-8-sig")
            self.assertIn(
                'name="p_cor_accountingEntries" id="p_cor_accountingEntries" '
                'substitutionGroup="xbrli:item"',
                oim_module_schema_text,
            )
            self.assertNotIn('substitutionGroup="xbrli:tuple"', oim_module_schema_text)
            self.assertNotIn("accountingEntriesComplexType", oim_module_schema_text)

            oim_module_presentation = (
                output / "cor" / "cor-oim-pre-2026-12-31.xml"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "cor-oim-2026-12-31.xsd#p_cor_accountingEntries",
                oim_module_presentation,
            )
            self.assertNotIn("cor-2026-12-31.xsd#cor_accountingEntries", oim_module_presentation)
            self.assertNotIn("-content-", oim_module_presentation)

            # Binding-specific Presentation Linkbase Set contract.
            ns = {
                "link": "http://www.xbrl.org/2003/linkbase",
                "xlink": "http://www.w3.org/1999/xlink",
                "xs": "http://www.w3.org/2001/XMLSchema",
            }

            def assert_no_duplicates(pre):
                tree = ET.parse(pre)
                for presentation_link in tree.findall(
                    ".//link:presentationLink", ns
                ):
                    locator_keys = [
                        (
                            locator.attrib.get(
                                "{http://www.w3.org/1999/xlink}label", ""
                            ),
                            locator.attrib.get(
                                "{http://www.w3.org/1999/xlink}href", ""
                            ),
                        )
                        for locator in presentation_link.findall("link:loc", ns)
                    ]
                    arc_keys = [
                        (
                            arc.attrib.get(
                                "{http://www.w3.org/1999/xlink}arcrole", ""
                            ),
                            arc.attrib.get(
                                "{http://www.w3.org/1999/xlink}from", ""
                            ),
                            arc.attrib.get(
                                "{http://www.w3.org/1999/xlink}to", ""
                            ),
                            arc.attrib.get("order", ""),
                            arc.attrib.get("use", ""),
                        )
                        for arc in presentation_link.findall(
                            "link:presentationArc", ns
                        )
                    ]
                    self.assertEqual(len(locator_keys), len(set(locator_keys)))
                    self.assertEqual(len(arc_keys), len(set(arc_keys)))
                return tree

            # Tuple module presentation: C/R global tuple declarations are
            # locatable in the owning Tuple module forest.
            tuple_pres = sorted(
                pre for pre in output.glob("*/*-pre-2026-12-31.xml")
                if "-oim-pre-" not in pre.name
            )
            for pre in tuple_pres:
                with self.subTest(tuple_presentation=pre.relative_to(output)):
                    tree = assert_no_duplicates(pre)
                    module = pre.parent.name
                    schema = ET.parse(
                        output / module / f"{module}-2026-12-31.xsd"
                    )
                    structural_ids = {
                        element.attrib["id"]
                        for element in schema.findall("./xs:element", ns)
                        if element.attrib.get("substitutionGroup") == "xbrli:tuple"
                        and element.attrib.get("id")
                    }
                    locator_labels = {
                        locator.attrib.get(
                            "{http://www.w3.org/1999/xlink}label", ""
                        )
                        for locator in tree.findall(".//link:loc", ns)
                    }
                    self.assertTrue(
                        structural_ids.issubset(locator_labels),
                        (module, sorted(structural_ids - locator_labels)),
                    )

            # OIM module presentation: module-owned Class p_* anchors are
            # locatable and every locator targets an xbrli:item concept in an
            # OIM module schema.  Tuple module schemas are not used.
            oim_pres = sorted(
                output.glob("*/*-oim-pre-2026-12-31.xml")
            )
            for pre in oim_pres:
                with self.subTest(oim_presentation=pre.relative_to(output)):
                    tree = assert_no_duplicates(pre)
                    module = pre.parent.name
                    oim_schema = ET.parse(
                        output / module / f"{module}-oim-2026-12-31.xsd"
                    )
                    p_ids = {
                        element.attrib["id"]
                        for element in oim_schema.findall("./xs:element", ns)
                        if element.attrib.get("id", "").startswith("p_")
                    }
                    locator_labels = {
                        locator.attrib.get(
                            "{http://www.w3.org/1999/xlink}label", ""
                        )
                        for locator in tree.findall(".//link:loc", ns)
                    }
                    self.assertTrue(
                        p_ids.issubset(locator_labels),
                        (module, sorted(p_ids - locator_labels)),
                    )
                    for locator in tree.findall(".//link:loc", ns):
                        href = locator.attrib.get(
                            "{http://www.w3.org/1999/xlink}href", ""
                        )
                        self.assertIn("-oim-2026-12-31.xsd#", href)
                        self.assertNotIn("-content-", href)
                        self.assertNotRegex(
                            href,
                            r"(?<!-oim)-2026-12-31\.xsd#",
                        )

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
                namespace="http://www.xbrl.org/int/gl/2026-12-31/plt",
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
                    namespace="http://www.xbrl.org/int/gl/2026-12-31/plt",
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


class CliLocationTests(unittest.TestCase):
    NAMESPACE = "http://www.xbrl.org/int/gl/2026-12-31/plt"

    def parse(self, *arguments: str):
        return MODULE.create_argument_parser().parse_args(
            [*arguments, "--namespace", self.NAMESPACE]
        )

    def test_namespace_prefix_map_is_explicit_repeatable_and_unambiguous(self):
        args = self.parse(
            "--namespace-prefix-map", "en=en16931",
            "--namespace-prefix-map", "ubl=invoice",
        )
        self.assertEqual(
            MODULE.normalize_namespace_prefix_map(args.namespace_prefix_map),
            {"en": "en16931", "ubl": "invoice"},
        )
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            MODULE.normalize_namespace_prefix_map(
                [("en", "en16931"), ("en", "other")]
            )
        with self.assertRaisesRegex(ValueError, "conventional prefix"):
            MODULE.normalize_namespace_prefix_map({"gl-cor": "bus"})

    def test_formal_hmd_and_output_options_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = self.parse(
                "--hmd-dir", str(root / "hmd"),
                "--output-dir", str(root / "output"),
            )
            MODULE.resolve_cli_locations(args)
            self.assertEqual(args.lhm_for_taxonomy, str(root / "hmd"))
            self.assertEqual(args.base_dir, str(root / "output"))

    def test_legacy_positional_and_base_dir_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = self.parse(
                str(root / "hmd"), "--base-dir", str(root / "output")
            )
            MODULE.resolve_cli_locations(args)
            self.assertEqual(args.lhm_for_taxonomy, str(root / "hmd"))
            self.assertEqual(args.base_dir, str(root / "output"))

    def test_equal_legacy_and_formal_locations_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hmd = str(root / "hmd")
            output = str(root / "output")
            args = self.parse(
                hmd, "--hmd-dir", hmd,
                "--base-dir", output, "--output-dir", output,
            )
            MODULE.resolve_cli_locations(args)
            self.assertEqual(args.lhm_for_taxonomy, hmd)
            self.assertEqual(args.base_dir, output)

    def test_conflicting_legacy_and_formal_locations_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = self.parse(
                str(root / "old-hmd"),
                "--hmd-dir", str(root / "new-hmd"),
                "--base-dir", str(root / "output"),
            )
            with self.assertRaisesRegex(ValueError, "Conflicting"):
                MODULE.resolve_cli_locations(args)

            args = self.parse(
                "--hmd-dir", str(root / "hmd"),
                "--base-dir", str(root / "old-output"),
                "--output-dir", str(root / "new-output"),
            )
            with self.assertRaisesRegex(ValueError, "Conflicting"):
                MODULE.resolve_cli_locations(args)

    def test_missing_legacy_and_formal_locations_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "--hmd-dir"):
            MODULE.resolve_cli_locations(self.parse("--output-dir", "output"))
        with self.assertRaisesRegex(ValueError, "--output-dir"):
            MODULE.resolve_cli_locations(self.parse("--hmd-dir", "hmd"))

    def test_missing_hmd_directory_and_non_empty_output_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                ValueError, "requires one LHM_for_taxonomy directory"
            ):
                MODULE.resolve_lhm_for_taxonomy_input(
                    str(root / "missing"), "utf-8-sig"
                )

            output = root / "output"
            output.mkdir()
            (output / "existing.txt").write_text("protected", encoding="utf-8")
            args = self.parse(
                "--hmd-dir", str(
                    ROOT / "semantic-model" / "HMD" / "accounting-entries"
                ),
                "--output-dir", str(output),
            )
            MODULE.resolve_cli_locations(args)
            with self.assertRaisesRegex(ValueError, "must be empty"):
                MODULE.generate_formal_hmd_package(args)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""End-to-end canonical contract test for FSM -> BSM -> LHM."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]
SPECIALIZATION = HERE / "specialization.py"
GRAPHWALK = HERE / "graphwalk.py"
FORMAL_FSM = (
    ROOT / "TaxonomyFramework" / "docs" / "framework"
    / "working-drafts" / "FSM.xlsx"
)
if not SPECIALIZATION.is_file():
    SPECIALIZATION = ROOT / "tools" / "semantic" / "specialization.py"
if not GRAPHWALK.is_file():
    GRAPHWALK = ROOT / "tools" / "semantic" / "graphwalk.py"

FSM_HEADER = [
    "sequence", "level", "property_type", "identifier", "module",
    "class_term", "property_term", "association_role", "representation_term",
    "associated_module", "associated_class", "multiplicity", "definition",
    "label_local", "definition_local",
]
BSM_HEADER = [*FSM_HEADER, "id"]
LHM_HEADER = [
    "sequence", "module", "level", "type", "identifier", "name", "datatype",
    "multiplicity", "domain_name", "definition", "label_local",
    "definition_local", "element", "id", "semantic_path",
    "associated_module", "class_term",
]

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _column_index(reference: str) -> int:
    letters = reference.rstrip("0123456789")
    result = 0
    for letter in letters:
        result = result * 26 + ord(letter.upper()) - ord("A") + 1
    return result - 1


def extract_fsm_sheet(workbook: Path, sheet_name: str, output: Path) -> None:
    """Export one formal FSM workbook sheet using only the Python standard library."""
    with zipfile.ZipFile(workbook) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall(f"{{{MAIN_NS}}}si"):
                shared_strings.append(
                    "".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t"))
                )

        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        relation_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relation_targets = {
            item.attrib["Id"]: item.attrib["Target"]
            for item in relation_root.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
        }
        sheet = next(
            item
            for item in workbook_root.findall(
                f".//{{{MAIN_NS}}}sheet"
            )
            if item.attrib["name"] == sheet_name
        )
        target = relation_targets[sheet.attrib[f"{{{REL_NS}}}id"]]
        sheet_path = "xl/" + target.lstrip("/")
        sheet_root = ET.fromstring(archive.read(sheet_path))

        rows: list[list[str]] = []
        for row_element in sheet_root.findall(f".//{{{MAIN_NS}}}row"):
            values = [""] * len(FSM_HEADER)
            has_value = False
            for cell in row_element.findall(f"{{{MAIN_NS}}}c"):
                index = _column_index(cell.attrib["r"])
                if index >= len(values):
                    continue
                cell_type = cell.attrib.get("t")
                value_node = cell.find(f"{{{MAIN_NS}}}v")
                if cell_type == "inlineStr":
                    value = "".join(
                        node.text or ""
                        for node in cell.iter(f"{{{MAIN_NS}}}t")
                    )
                elif value_node is None:
                    value = ""
                elif cell_type == "s":
                    value = shared_strings[int(value_node.text or "0")]
                else:
                    value = value_node.text or ""
                values[index] = value
                has_value = has_value or bool(value)
            if has_value:
                rows.append(values)

    if not rows or rows[0] != FSM_HEADER:
        raise AssertionError(f"{sheet_name} does not use the formal 15-column FSM header")
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(rows)


def row(**values: str) -> dict[str, str]:
    result = {name: "" for name in FSM_HEADER}
    result.update(values)
    return result


class SemanticPipelineTests(unittest.TestCase):
    def write_fsm(self, path: Path) -> None:
        rows = [
            row(sequence="1", level="1", property_type="Abstract Class",
                module="base", class_term="Base", multiplicity="1"),
            row(sequence="2", level="2", property_type="Attribute",
                module="base", class_term="Base", property_term="Status",
                representation_term="Code", multiplicity="0..1"),
            row(sequence="3", level="1", property_type="Class",
                module="tst", class_term="Address", multiplicity="1"),
            row(sequence="4", level="2", property_type="Attribute", identifier="PK",
                module="tst", class_term="Address", property_term="Address ID",
                representation_term="Identifier", multiplicity="1"),
            row(sequence="5", level="2", property_type="Attribute",
                module="tst", class_term="Address", property_term="Street",
                representation_term="Text", multiplicity="0..1"),
            row(sequence="6", level="1", property_type="Class",
                module="tst", class_term="Line", multiplicity="0..*"),
            row(sequence="7", level="2", property_type="Attribute",
                module="tst", class_term="Line", property_term="Description",
                representation_term="Text", multiplicity="1"),
            row(sequence="8", level="1", property_type="Class",
                module="tst", class_term="Root", multiplicity="1"),
            row(sequence="9", level="2", property_type="Specialization",
                module="tst", class_term="Root", associated_module="base",
                associated_class="Base", multiplicity="1"),
            row(sequence="10", level="2", property_type="Attribute",
                module="tst", class_term="Root", property_term="Status",
                representation_term="Token", multiplicity="1"),
            row(sequence="11", level="2", property_type="Composition",
                module="tst", class_term="Root", property_term="Line property",
                association_role="",
                associated_module="tst", associated_class="Line",
                multiplicity="1..*"),
            row(sequence="12", level="2", property_type="Reference",
                module="tst", class_term="Root", property_term="Address reference",
                association_role="Original",
                associated_module="tst", associated_class="Address",
                multiplicity="0..1"),
        ]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FSM_HEADER, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_pipeline_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fsm = root / "fsm.csv"
            self.write_fsm(fsm)
            hashes: list[tuple[str, str]] = []
            for run in (1, 2):
                bsm = root / f"bsm-{run}.csv"
                lhm = root / f"lhm-{run}.csv"
                specialized = subprocess.run(
                    [
                        sys.executable, str(SPECIALIZATION),
                        "--in", str(fsm), "--out", str(bsm),
                        "--module-abbreviation", "tst=TS",
                        "--module-abbreviation", "base=BA",
                    ],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(specialized.returncode, 0, specialized.stderr)
                walked = subprocess.run(
                    [
                        sys.executable, str(GRAPHWALK), str(bsm), str(lhm),
                        "--root", "tst:Root",
                    ],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(walked.returncode, 0, walked.stderr)
                with bsm.open(encoding="utf-8-sig", newline="") as handle:
                    bsm_reader = csv.DictReader(handle)
                    bsm_rows = list(bsm_reader)
                with lhm.open(encoding="utf-8-sig", newline="") as handle:
                    lhm_reader = csv.DictReader(handle)
                    lhm_rows = list(lhm_reader)
                self.assertEqual(bsm_reader.fieldnames, BSM_HEADER)
                self.assertEqual(lhm_reader.fieldnames, LHM_HEADER)
                root_rows = [
                    item for item in bsm_rows if item["class_term"] == "Root"
                ]
                self.assertTrue(all(item["module"] == "tst" for item in root_rows))
                self.assertEqual(
                    [item["type"] for item in lhm_rows],
                    ["C", "A", "C", "A", "R", "A"],
                )
                self.assertEqual(lhm_rows[1]["module"], "tst")
                self.assertEqual(lhm_rows[-1]["identifier"], "REF")
                self.assertNotIn("Street", [item["name"] for item in lhm_rows])
                self.assertEqual(
                    [item["datatype"] for item in lhm_rows if item["type"] == "A"],
                    ["Token", "Text", "Identifier"],
                )
                hashes.append(
                    (
                        hashlib.sha256(bsm.read_bytes()).hexdigest(),
                        hashlib.sha256(lhm.read_bytes()).hexdigest(),
                    )
                )
            self.assertEqual(hashes[0], hashes[1])

    def test_full_accounting_and_business_transactions_combined_lhm(self):
        """The reviewed 2026-07-29 FSM must produce the full combined LHM."""
        self.assertTrue(FORMAL_FSM.is_file())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fsm = root / "fsm.csv"
            fsm_btx = root / "fsm-btx.csv"
            bsm = root / "bsm.csv"
            lhm = root / "combined-lhm.csv"
            extract_fsm_sheet(FORMAL_FSM, "FSM", fsm)
            extract_fsm_sheet(FORMAL_FSM, "FSM_btx", fsm_btx)
            specialized = subprocess.run(
                [
                    sys.executable, str(SPECIALIZATION),
                    "--in", str(fsm), "--in", str(fsm_btx),
                    "--out", str(bsm),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(specialized.returncode, 0, specialized.stderr)
            walked = subprocess.run(
                [
                    sys.executable, str(GRAPHWALK), str(bsm), str(lhm),
                    "--root", "cor:Accounting Entries",
                    "--root", "btx:Business Transactions",
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(walked.returncode, 0, walked.stderr)

            with bsm.open(encoding="utf-8-sig", newline="") as handle:
                bsm_reader = csv.DictReader(handle)
                bsm_rows = list(bsm_reader)
            with lhm.open(encoding="utf-8-sig", newline="") as handle:
                lhm_reader = csv.DictReader(handle)
                lhm_rows = list(lhm_reader)

            self.assertEqual(bsm_reader.fieldnames, BSM_HEADER)
            self.assertEqual(lhm_reader.fieldnames, LHM_HEADER)
            self.assertEqual(len(bsm_rows), 713)
            self.assertEqual(len(lhm_rows), 498)
            self.assertFalse(
                any(
                    item["module"] == "cor"
                    and item["class_term"] == "Entity_ Party"
                    and item["property_term"] == "Business Description"
                    for item in bsm_rows
                )
            )
            inherited_party_descriptions = [
                item for item in bsm_rows
                if item["module"] == "cor"
                and item["class_term"] == "Entity_ Party"
                and item["property_term"] == "Party Business Description"
            ]
            self.assertEqual(len(inherited_party_descriptions), 1)
            self.assertEqual(inherited_party_descriptions[0]["id"], "CO14-03")

            paths = [item["semantic_path"] for item in lhm_rows]
            self.assertEqual(len(paths), len(set(paths)))
            element_identities: dict[tuple[str, str], str] = {}
            for item in lhm_rows:
                if not item["element"]:
                    continue
                key = (item["module"], item["element"])
                previous = element_identities.setdefault(key, item["id"])
                self.assertEqual(previous, item["id"])
            self.assertEqual(
                sum(
                    item["id"] == "CO14-03"
                    and item["name"] == "Party Business Description"
                    for item in lhm_rows
                ),
                2,
            )


if __name__ == "__main__":
    unittest.main()

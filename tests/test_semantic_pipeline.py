#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""End-to-end v8 contract test for FSM -> BSM -> LHM lifecycle artefacts."""

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
SPECIALISATION = ROOT / "tools" / "semantic" / "specialisation.py"
GRAPHWALK = ROOT / "tools" / "semantic" / "graphwalk.py"
POST_GRAPHWALK = ROOT / "tools" / "semantic" / "post_graphwalk.py"
VALIDATE_LHM = ROOT / "tools" / "semantic" / "validate_lhm.py"
TAXONOMY_GENERATOR = ROOT / "tools" / "taxonomy" / "xBRLGL_TaxonomyGenerator.py"
FORMAL_FSM = ROOT / "semantic-model" / "FSM.xlsx"
FORMAL_GENERATED = {
    "FSM.csv": ROOT / "semantic-model" / "FSM" / "FSM.csv",
    "FSM_btx.csv": ROOT / "semantic-model" / "FSM" / "FSM_btx.csv",
    "BSM.csv": ROOT / "semantic-model" / "BSM" / "BSM.csv",
    "LHM_candidate.csv": ROOT / "semantic-model" / "LHM" / "LHM_candidate.csv",
}
FORMAL_REVIEWED = (
    ROOT / "semantic-model" / "LHM" / "XBRL_GL_Next_LHM_reviewed.csv"
)
FORMAL_HMD_DIRECTORY = ROOT / "semantic-model" / "LHM_for_taxonomy"
FORMAL_TAXONOMY = ROOT / "taxonomy"
FORMAL_CANDIDATE_SHA256 = (
    "ff153c83629a4ae81eed2dcbfe97e6b95c6c9526013f505adecf7808e3a9edfa"
)
TAXONOMY_NAMESPACE = "https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/plt"

FSM_HEADER = [
    "sequence", "level", "property_type", "identifier", "module",
    "class_term", "property_term", "association_role", "representation_term",
    "associated_module", "associated_class", "multiplicity", "definition",
    "label_local", "definition_local",
]
BSM_HEADER = [*FSM_HEADER, "id"]
CANDIDATE_HEADER = [
    "sequence", "module", "level", "type", "identifier", "name", "datatype",
    "multiplicity", "association_role", "definition", "label_local",
    "definition_local", "source_bsm_id", "semantic_path", "associated_module",
    "class_term", "local_name", "xpath",
]
BOUND_HEADER = CANDIDATE_HEADER

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
    """Export one formal FSM workbook sheet using only the standard library."""
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
            for item in workbook_root.findall(f".//{{{MAIN_NS}}}sheet")
            if item.attrib["name"] == sheet_name
        )
        target = relation_targets[sheet.attrib[f"{{{REL_NS}}}id"]]
        sheet_root = ET.fromstring(archive.read("xl/" + target.lstrip("/")))

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
                        node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t")
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
        raise AssertionError(f"{sheet_name} does not use the formal FSM header")
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(rows)


def file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() != ".md"
    }


def row(**values: str) -> dict[str, str]:
    result = {name: "" for name in FSM_HEADER}
    result.update(values)
    return result


class SemanticPipelineTests(unittest.TestCase):
    def write_fsm(self, path: Path) -> None:
        rows = [
            row(sequence="1", level="1", property_type="Abstract Class",
                module="cor", class_term="Base", multiplicity="1"),
            row(sequence="2", level="2", property_type="Attribute",
                module="cor", class_term="Base", property_term="Status",
                representation_term="Code", multiplicity="0..1"),
            row(sequence="3", level="1", property_type="Class",
                module="cor", class_term="Address", multiplicity="1"),
            row(sequence="4", level="2", property_type="Attribute", identifier="PK",
                module="cor", class_term="Address", property_term="Address ID",
                representation_term="Token", multiplicity="1"),
            row(sequence="5", level="2", property_type="Attribute",
                module="cor", class_term="Address", property_term="Street",
                representation_term="String", multiplicity="0..1"),
            row(sequence="6", level="1", property_type="Class",
                module="cor", class_term="Line", multiplicity="0..*"),
            row(sequence="7", level="2", property_type="Attribute",
                module="cor", class_term="Line", property_term="Description",
                representation_term="String", multiplicity="1"),
            row(sequence="8", level="1", property_type="Class",
                module="cor", class_term="Root", multiplicity="1"),
            row(sequence="9", level="2", property_type="Specialisation",
                module="cor", class_term="Root", associated_module="cor",
                associated_class="Base", multiplicity="1"),
            row(sequence="10", level="2", property_type="Attribute",
                module="cor", class_term="Root", property_term="Status",
                representation_term="Token", multiplicity="1"),
            row(sequence="11", level="2", property_type="Composition",
                module="cor", class_term="Root", association_role="Lines",
                associated_module="cor", associated_class="Line",
                multiplicity="1..*"),
            row(sequence="12", level="2", property_type="Reference",
                module="cor", class_term="Root", association_role="Original",
                associated_module="cor", associated_class="Address",
                multiplicity="0..1"),
        ]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FSM_HEADER, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_pipeline_is_reproducible_and_observes_v8_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fsm = root / "fsm.csv"
            self.write_fsm(fsm)
            hashes: list[tuple[str, str, str]] = []
            for run in (1, 2):
                bsm = root / f"bsm-{run}.csv"
                candidate = root / f"lhm-candidate-{run}.csv"
                reviewed = root / f"lhm-reviewed-{run}.csv"
                bound_directory = root / f"hmd-taxonomy-{run}"
                bound = (
                    bound_directory /
                    "XBRL_GL_Next_HMD_Root_for_taxonomy.csv"
                )
                post_diagnostics = root / f"post-diagnostics-{run}.json"
                post_diagnostics_csv = root / f"post-diagnostics-{run}.csv"
                report_json = root / f"report-{run}.json"
                report_md = root / f"report-{run}.md"
                commands = [
                    [sys.executable, str(SPECIALISATION), "--in", str(fsm),
                     "--out", str(bsm), "--module-abbreviation", "cor=CO"],
                    [sys.executable, str(GRAPHWALK), str(bsm), str(candidate),
                     "--root", "cor:Root"],
                ]
                for command in commands:
                    completed = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(completed.returncode, 0, completed.stderr)

                # The test models the required human checkpoint by making an explicit
                # reviewed copy.  Automation still does not designate it authoritative.
                reviewed.write_bytes(candidate.read_bytes())
                checked = subprocess.run(
                    [sys.executable, str(VALIDATE_LHM), str(candidate), "--bsm", str(bsm),
                     "--reviewed", str(reviewed), "--json", str(report_json),
                     "--report", str(report_md)], capture_output=True, text=True,
                )
                self.assertEqual(checked.returncode, 0, checked.stderr)
                processed = subprocess.run(
                    [sys.executable, str(POST_GRAPHWALK), str(reviewed),
                     str(bound_directory), "--diagnostics", str(post_diagnostics),
                     "--diagnostics-csv", str(post_diagnostics_csv),
                     "--manifest", str(bound_directory / "manifest.csv")],
                    capture_output=True, text=True,
                )
                self.assertEqual(processed.returncode, 0, processed.stderr)

                with bsm.open(encoding="utf-8-sig", newline="") as handle:
                    bsm_reader = csv.DictReader(handle); bsm_rows = list(bsm_reader)
                with candidate.open(encoding="utf-8-sig", newline="") as handle:
                    candidate_reader = csv.DictReader(handle); candidate_rows = list(candidate_reader)
                with bound.open(encoding="utf-8-sig", newline="") as handle:
                    bound_reader = csv.DictReader(handle); bound_rows = list(bound_reader)
                self.assertEqual(bsm_reader.fieldnames, BSM_HEADER)
                self.assertEqual(candidate_reader.fieldnames, CANDIDATE_HEADER)
                self.assertEqual(bound_reader.fieldnames, BOUND_HEADER)
                self.assertEqual(len(candidate_rows), len(bound_rows))
                self.assertEqual(
                    [item["type"] for item in candidate_rows],
                    ["C", "A", "C", "A", "R", "A"],
                )
                self.assertEqual(candidate_rows[-1]["identifier"], "REF")
                self.assertNotIn("Street", [item["name"] for item in candidate_rows])
                self.assertEqual(
                    [item["datatype"] for item in candidate_rows if item["type"] == "A"],
                    ["Token", "String", "Token"],
                )
                self.assertNotIn("domain_name", candidate_reader.fieldnames)
                self.assertTrue(all(r["local_name"] for r in candidate_rows))
                self.assertTrue(all(":" not in r["local_name"] for r in candidate_rows))
                self.assertTrue(all(r["xpath"].startswith("/xbrli:xbrl/") for r in candidate_rows))
                bsm_ids = {r["id"] for r in bsm_rows}
                self.assertTrue(all(r["source_bsm_id"] in bsm_ids for r in candidate_rows))
                self.assertTrue(all(r["semantic_path"].startswith("$.cor_") for r in candidate_rows))
                self.assertTrue(all(r["local_name"] for r in bound_rows))
                self.assertTrue(all(r["xpath"].startswith("/xbrli:xbrl/") for r in bound_rows))
                for candidate_row, bound_row in zip(candidate_rows, bound_rows):
                    for column in CANDIDATE_HEADER:
                        if column != "xpath":
                            self.assertEqual(candidate_row[column], bound_row[column])
                hashes.append(tuple(hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in (bsm, candidate, bound)))
            self.assertEqual(hashes[0], hashes[1])

    def test_formal_pipeline_artifacts_are_byte_reproducible(self):
        self.assertTrue(FORMAL_FSM.is_file())
        reviewed_hash_before = hashlib.sha256(FORMAL_REVIEWED.read_bytes()).hexdigest()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fsm = root / "FSM.csv"
            fsm_btx = root / "FSM_btx.csv"
            bsm = root / "BSM.csv"
            candidate = root / "LHM_candidate.csv"
            hmd_directory = root / "LHM_for_taxonomy"
            taxonomy_directory = root / "taxonomy"

            extract_fsm_sheet(FORMAL_FSM, "FSM", fsm)
            extract_fsm_sheet(FORMAL_FSM, "FSM_btx", fsm_btx)
            commands = [
                [sys.executable, str(SPECIALISATION), "--in", str(fsm),
                 "--in", str(fsm_btx), "--out", str(bsm)],
                [sys.executable, str(GRAPHWALK), str(bsm), str(candidate),
                 "--root", "cor:Accounting Entries",
                 "--root", "btx:Business Transactions"],
            ]
            for command in commands:
                completed = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stderr)

            for actual, registered_name in (
                (fsm, "FSM.csv"),
                (fsm_btx, "FSM_btx.csv"),
                (bsm, "BSM.csv"),
                (candidate, "LHM_candidate.csv"),
            ):
                self.assertEqual(actual.read_bytes(), FORMAL_GENERATED[registered_name].read_bytes())

            with candidate.open(encoding="utf-8-sig", newline="") as handle:
                candidate_reader = csv.DictReader(handle)
                candidate_rows = list(candidate_reader)
            with FORMAL_REVIEWED.open(encoding="utf-8-sig", newline="") as handle:
                reviewed_reader = csv.DictReader(handle)
                reviewed_rows = list(reviewed_reader)
            self.assertEqual(candidate_reader.fieldnames, CANDIDATE_HEADER)
            self.assertEqual(reviewed_reader.fieldnames, BOUND_HEADER)
            with bsm.open(encoding="utf-8-sig", newline="") as handle:
                bsm_rows = list(csv.DictReader(handle))
            self.assertEqual(len(bsm_rows), 732)
            self.assertEqual(len(candidate_rows), 833)
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
            semantic_paths = [item["semantic_path"] for item in candidate_rows]
            self.assertEqual(len(semantic_paths), len(set(semantic_paths)))
            self.assertEqual(
                sum(
                    item["source_bsm_id"] == "CO14-03"
                    and item["name"] == "Party Business Description"
                    for item in candidate_rows
                ),
                2,
            )
            self.assertEqual(
                hashlib.sha256(candidate.read_bytes()).hexdigest(),
                FORMAL_CANDIDATE_SHA256,
            )
            self.assertNotEqual(candidate.read_bytes(), FORMAL_REVIEWED.read_bytes())
            self.assertNotEqual(len(candidate_rows), len(reviewed_rows))

            processed = subprocess.run(
                [sys.executable, str(POST_GRAPHWALK), str(FORMAL_REVIEWED),
                 str(hmd_directory), "--manifest", str(hmd_directory / "manifest.csv")],
                capture_output=True, text=True,
            )
            self.assertEqual(processed.returncode, 0, processed.stderr)
            self.assertEqual(file_hashes(hmd_directory), file_hashes(FORMAL_HMD_DIRECTORY))

            generated = subprocess.run(
                [sys.executable, str(TAXONOMY_GENERATOR), str(FORMAL_HMD_DIRECTORY),
                 "--base-dir", str(taxonomy_directory),
                 "--namespace", TAXONOMY_NAMESPACE],
                capture_output=True, text=True,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            self.assertEqual(file_hashes(taxonomy_directory), file_hashes(FORMAL_TAXONOMY))

        self.assertEqual(
            hashlib.sha256(FORMAL_REVIEWED.read_bytes()).hexdigest(),
            reviewed_hash_before,
        )


if __name__ == "__main__":
    unittest.main()

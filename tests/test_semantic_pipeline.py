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
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]
SPECIALIZATION = HERE / "specialization.py"
GRAPHWALK = HERE / "graphwalk.py"
if not SPECIALIZATION.is_file():
    SPECIALIZATION = ROOT / "tools" / "semantic" / "specialization.py"
if not GRAPHWALK.is_file():
    GRAPHWALK = ROOT / "tools" / "semantic" / "graphwalk.py"

FSM_HEADER = [
    "sequence", "level", "property_type", "identifier", "module",
    "class_term", "property_term", "representation_term",
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
                module="tst", class_term="Root", property_term="",
                associated_module="tst", associated_class="Line",
                multiplicity="1..*"),
            row(sequence="12", level="2", property_type="Reference",
                module="tst", class_term="Root", property_term="Original",
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


if __name__ == "__main__":
    unittest.main()

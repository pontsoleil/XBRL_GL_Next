#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: MIT
"""Generate one HMD-for-taxonomy CSV per root in an authoritative LHM reviewed.

The only semantic input is the reviewed 18-column LHM.  Candidate LHM, BSM,
FSM, and Specialisation provenance are deliberately outside this program's
responsibility.  Reviewed values are never repaired: rows with multiplicity
``0..0`` (and their structural descendants) are omitted, ``xpath`` is
regenerated from ``module`` and the reviewed ``local_name``, and every other
value is preserved.  Obsolete ``element`` and ``local-name`` columns are not
accepted as fallbacks.

All HMDs are validated before publication.  A single error prevents every
formal HMD and the manifest from being issued.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Mapping, Sequence


LHM_HEADER = [
    "sequence", "module", "level", "type", "identifier", "name",
    "datatype", "multiplicity", "association_role", "definition",
    "label_local", "definition_local", "source_bsm_id", "semantic_path",
    "associated_module", "class_term", "local_name", "xpath",
]
MODULE_PREFIX = {
    "btx": "gl-btx", "bus": "gl-bus", "cor": "gl-cor",
    "ehm": "gl-ehm", "lnk": "gl-lnk", "muc": "gl-muc",
    "taf": "gl-taf", "usk": "gl-usk",
}
ROW_TYPES = {"C", "A", "R"}
MULTIPLICITIES = {"0..0", "0..1", "0..*", "1", "1..1", "1..*"}
NCNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")
IDENTIFIER_WORD = re.compile(r"[A-Za-z0-9]+")
SEMANTIC_PATH_SEGMENT = re.compile(
    r"^(?P<module>[A-Za-z][A-Za-z0-9]*)_(?P<term>[A-Za-z]+)$"
)
DIAGNOSTIC_CSV_HEADER = [
    "severity", "error_code", "message", "rule", "actual_value",
    "expected_value", "lhm_row", "sequence", "hmd_identifier",
    "semantic_path", "module", "local_name", "xpath", "qname",
    "related_hmd", "related_row",
]
MANIFEST_HEADER = [
    "hmd_identifier", "hmd_name", "file", "input_row_count",
    "zero_zero_row_count", "excluded_descendant_count", "excluded_row_count",
    "output_row_count", "semantic_path_duplicate_count",
    "qname_duplicate_count", "xpath_duplicate_count", "sha256",
]
DEFINITION_FIELDS = [
    "type", "identifier", "name", "datatype", "definition",
    "label_local", "definition_local",
]


class PostGraphWalkError(ValueError):
    """No formal HMD-for-taxonomy files may be issued."""


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest().upper()


def hmd_identifier(row: Mapping[str, str]) -> str:
    source = row.get("name", "") or row.get("class_term", "")
    words = IDENTIFIER_WORD.findall(source)
    return "".join(word[:1].upper() + word[1:] for word in words)


def definition_signature(row: Mapping[str, str]) -> tuple[str, ...]:
    fields = list(DEFINITION_FIELDS)
    if row.get("type") in {"C", "R"}:
        fields.extend(["association_role", "associated_module", "class_term"])
    return tuple(row.get(name, "") for name in fields)


def qualified_name(
    module: str, local_name: str, module_prefixes: Mapping[str, str]
) -> str:
    try:
        prefix = module_prefixes[module]
    except KeyError as exc:
        raise PostGraphWalkError(
            f"module has no registered taxonomy prefix: {module!r}"
        ) from exc
    if not local_name or ":" in local_name or not NCNAME.fullmatch(local_name):
        raise PostGraphWalkError(
            f"local_name is not a valid XML Schema NCName: {local_name!r}"
        )
    return f"{prefix}:{local_name}"


class PostGraphWalk:
    def __init__(
        self,
        reviewed_file: str | Path,
        output_directory: str | Path,
        *,
        encoding: str = "utf-8-sig",
        diagnostics_file: str | Path | None = None,
        diagnostics_csv_file: str | Path | None = None,
        manifest_file: str | Path | None = None,
        module_prefixes: Mapping[str, str] | None = None,
    ) -> None:
        self.reviewed_file = Path(reviewed_file)
        self.output_directory = Path(output_directory)
        self.encoding = encoding
        self.diagnostics_file = Path(
            diagnostics_file or self.output_directory.with_name(
                f"{self.output_directory.name}_diagnostics.json"
            )
        )
        self.diagnostics_csv_file = Path(
            diagnostics_csv_file or self.output_directory.with_name(
                f"{self.output_directory.name}_diagnostics.csv"
            )
        )
        self.manifest_file = Path(
            manifest_file or self.output_directory / "manifest.csv"
        )
        self.module_prefixes = dict(module_prefixes or MODULE_PREFIX)
        self.rows: list[dict[str, str]] = []
        self.hmds: list[dict[str, object]] = []
        self.errors: list[dict[str, str]] = []
        self.shared_qname_count = 0
        self.shared_qname_definition_mismatch_count = 0
        self.shared_qname_content_model_mismatch_count = 0
        self.formal_outputs_issued = False

    def record_error(
        self,
        code: str,
        message: str,
        rule: str,
        actual: str,
        expected: str,
        row: Mapping[str, str] | None = None,
        *,
        hmd: str = "",
        related_hmd: str = "",
        related_row: str = "",
    ) -> None:
        item = row or {}
        self.errors.append({
            "severity": "error", "error_code": code, "message": message,
            "rule": rule, "actual_value": actual, "expected_value": expected,
            "lhm_row": str(item.get("_logical_row", "")),
            "sequence": str(item.get("sequence", "")),
            "hmd_identifier": hmd,
            "semantic_path": str(item.get("semantic_path", "")),
            "module": str(item.get("module", "")),
            "local_name": str(item.get("local_name", "")),
            "xpath": str(item.get("xpath", "")),
            "qname": (
                f"{self.module_prefixes.get(str(item.get('module', '')), '')}:"
                f"{item.get('local_name', '')}"
                if item.get("local_name", "") else ""
            ),
            "related_hmd": related_hmd, "related_row": related_row,
        })

    def raise_errors(self) -> None:
        if self.errors:
            raise PostGraphWalkError(
                f"{len(self.errors)} validation error(s); no formal "
                "HMD-for-taxonomy files were issued"
            )

    def validate_paths(self) -> None:
        reviewed = self.reviewed_file.resolve()
        output = self.output_directory.resolve()
        diagnostics = self.diagnostics_file.resolve()
        diagnostics_csv = self.diagnostics_csv_file.resolve()
        manifest = self.manifest_file.resolve()
        if len({reviewed, diagnostics, diagnostics_csv, manifest}) != 4:
            raise PostGraphWalkError(
                "LHM reviewed, diagnostics JSON, diagnostics CSV, and manifest "
                "must use different paths"
            )
        if output == reviewed or output == diagnostics or output == diagnostics_csv:
            raise PostGraphWalkError("output directory must not alias an input/output file")
        if manifest.parent != output:
            raise PostGraphWalkError(
                "manifest must be located directly in the formal output directory"
            )
        if self.output_directory.exists():
            self.record_error(
                "OUTPUT_DIRECTORY_ALREADY_EXISTS",
                f"formal output directory already exists: {self.output_directory}",
                "Formal outputs must be issued into a new directory; existing "
                "outputs are never overwritten.",
                str(self.output_directory), "nonexistent output directory",
            )
            self.raise_errors()

    def read_reviewed(self) -> None:
        if not self.reviewed_file.is_file():
            self.record_error(
                "LHM_REVIEWED_NOT_FOUND",
                f"LHM reviewed does not exist: {self.reviewed_file}",
                "The first positional argument must be one reviewed CSV file.",
                str(self.reviewed_file), "existing 18-column CSV",
            )
            self.raise_errors()
        try:
            with self.reviewed_file.open(encoding=self.encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                actual = reader.fieldnames or []
                if actual != LHM_HEADER:
                    self.record_error(
                        "LHM_HEADER_MISMATCH",
                        f"LHM reviewed header mismatch: {actual!r}",
                        "The reviewed CSV must use the exact 18-column contract and order.",
                        repr(actual), repr(LHM_HEADER),
                    )
                    self.raise_errors()
                logical = 1
                for source in reader:
                    if not any("" if value is None else str(value)
                               for value in source.values()):
                        continue
                    logical += 1
                    item = {
                        name: "" if source.get(name) is None else str(source[name])
                        for name in LHM_HEADER
                    }
                    item["_logical_row"] = str(logical)
                    self.rows.append(item)
        except (OSError, csv.Error) as exc:
            self.record_error(
                "LHM_READ_ERROR", f"Could not read LHM reviewed: {exc}",
                "The reviewed input must be a readable CSV.", str(exc),
                "readable CSV",
            )
            self.raise_errors()
        if not self.rows:
            self.record_error(
                "EMPTY_LHM_REVIEWED", "LHM reviewed contains no data rows",
                "At least one level-1 HMD root is required.", "0 rows", ">= 1 row",
            )
            self.raise_errors()

    def validate_global_rows(self) -> None:
        seen_sequences: dict[int, str] = {}
        previous_sequence = 0
        for row in self.rows:
            sequence_text = row["sequence"]
            try:
                sequence = int(sequence_text)
            except ValueError:
                sequence = 0
            if sequence <= 0:
                self.record_error(
                    "INVALID_SEQUENCE", "sequence must be a positive integer",
                    "sequence must be a positive integer.", sequence_text,
                    "integer >= 1", row,
                )
            else:
                prior = seen_sequences.get(sequence)
                if prior:
                    self.record_error(
                        "DUPLICATE_SEQUENCE", f"duplicate sequence {sequence}",
                        "sequence must be unique in the reviewed LHM.",
                        sequence_text, "unique positive integer", row,
                        related_row=prior,
                    )
                if sequence <= previous_sequence:
                    self.record_error(
                        "NON_INCREASING_SEQUENCE",
                        f"sequence {sequence} is not strictly increasing",
                        "sequence values must be strictly increasing in file order.",
                        sequence_text, f"> {previous_sequence}", row,
                    )
                seen_sequences[sequence] = row["_logical_row"]
                previous_sequence = max(previous_sequence, sequence)

            try:
                level = int(row["level"])
            except ValueError:
                level = 0
            row["_level_int"] = str(level)
            if level < 1:
                self.record_error(
                    "INVALID_LEVEL", "level must be an integer of at least 1",
                    "level must be an integer >= 1.", row["level"], ">= 1", row,
                )
            if row["type"] not in ROW_TYPES:
                self.record_error(
                    "INVALID_TYPE", f"unsupported type {row['type']!r}",
                    "type must be C, A, or R.", row["type"], "C|A|R", row,
                )
            if row["multiplicity"] not in MULTIPLICITIES:
                self.record_error(
                    "INVALID_MULTIPLICITY",
                    f"unsupported multiplicity {row['multiplicity']!r}",
                    "multiplicity must use the reviewed LHM value set.",
                    row["multiplicity"], "|".join(sorted(MULTIPLICITIES)), row,
                )
            self.validate_local_name(row)

        if self.rows[0].get("_level_int") != "1":
            self.record_error(
                "FIRST_ROW_NOT_HMD_ROOT",
                "the first reviewed data row is not level 1",
                "The first data row must start an HMD with level = 1.",
                self.rows[0]["level"], "1", self.rows[0],
            )

    def validate_local_name(self, row: Mapping[str, str]) -> None:
        module = row["module"]
        if module not in self.module_prefixes:
            self.record_error(
                "UNREGISTERED_MODULE",
                f"module has no registered taxonomy prefix: {module!r}",
                "Every module must have a registered taxonomy prefix.",
                module, "registered module", row,
            )
        local_name = row["local_name"]
        if not local_name:
            self.record_error(
                "EMPTY_LOCAL_NAME", "local_name is empty",
                "local_name must contain one XML local name.",
                local_name, "nonempty NCName", row,
            )
            return
        if ":" in local_name:
            self.record_error(
                "LOCAL_NAME_CONTAINS_PREFIX",
                f"local_name contains a namespace separator: {local_name!r}",
                "local_name must not contain a namespace prefix or colon.",
                local_name, "unprefixed NCName", row,
            )
        if not NCNAME.fullmatch(local_name):
            self.record_error(
                "INVALID_LOCAL_NAME_NCNAME",
                f"local_name is not a valid NCName: {local_name!r}",
                "local_name must satisfy [A-Za-z_][A-Za-z0-9._-]*.",
                local_name, "valid NCName", row,
            )

    def validate_semantic_path(
        self,
        row: Mapping[str, str],
        identifier: str,
        ancestors: Sequence[tuple[int, str, str]],
    ) -> None:
        """Reject noncanonical paths without repairing reviewed values."""
        semantic_path = row["semantic_path"]
        if not semantic_path:
            return
        if not semantic_path.startswith("$."):
            self.record_error(
                "NONCANONICAL_SEMANTIC_PATH",
                f"semantic_path does not start with '$.': {semantic_path!r}",
                "semantic_path must start with '$.' and contain canonical segments.",
                semantic_path,
                "$.<module>_<ASCII-letters>[.<module>_<ASCII-letters>...]",
                row,
                hmd=identifier,
            )
            return

        raw_segments = semantic_path[2:].split(".")
        parsed: list[tuple[str, str]] = []
        for segment in raw_segments:
            match = SEMANTIC_PATH_SEGMENT.fullmatch(segment)
            if match is None:
                self.record_error(
                    "NONCANONICAL_SEMANTIC_PATH",
                    f"semantic_path contains a noncanonical segment: {segment!r}",
                    "Each segment must be <module>_<term>, where term is one or "
                    "more ASCII letters and contains no separators or digits.",
                    semantic_path,
                    "$.<module>_<ASCII-letters>[.<module>_<ASCII-letters>...]",
                    row,
                    hmd=identifier,
                )
                return
            parsed.append((match.group("module"), match.group("term")))

        level = int(row.get("_level_int", "0"))
        if len(parsed) != level:
            self.record_error(
                "SEMANTIC_PATH_DEPTH_MISMATCH",
                f"semantic_path has {len(parsed)} segment(s) at level {level}",
                "semantic_path segment count must equal the reviewed hierarchy level.",
                str(len(parsed)),
                str(level),
                row,
                hmd=identifier,
            )

        actual_module = parsed[-1][0]
        expected_module = (
            ancestors[-1][2]
            if ancestors and row["type"] in {"C", "R"}
            else row["module"]
        )
        if actual_module != expected_module:
            self.record_error(
                "SEMANTIC_PATH_MODULE_MISMATCH",
                "semantic_path segment module does not match Graph Walk rules",
                "A root or Attribute segment uses the row module; a non-root C/R "
                "Association segment uses its immediate parent C/R module.",
                actual_module,
                expected_module,
                row,
                hmd=identifier,
            )

        if ancestors and len(parsed) > 1:
            actual_parent = "$." + ".".join(raw_segments[:-1])
            expected_parent = ancestors[-1][1]
            if actual_parent != expected_parent:
                self.record_error(
                    "SEMANTIC_PATH_PARENT_MISMATCH",
                    "semantic_path does not extend its immediate C/R parent path",
                    "A child semantic_path must equal its immediate parent path plus "
                    "one canonical segment.",
                    actual_parent,
                    expected_parent,
                    row,
                    hmd=identifier,
                )

    def split_hmds(self) -> None:
        starts = [index for index, row in enumerate(self.rows)
                  if row.get("_level_int") == "1"]
        if not starts or starts[0] != 0:
            return
        identifiers: dict[str, str] = {}
        for position, start in enumerate(starts):
            end = starts[position + 1] if position + 1 < len(starts) else len(self.rows)
            root = self.rows[start]
            identifier = hmd_identifier(root)
            if not identifier or not NCNAME.fullmatch(identifier):
                self.record_error(
                    "INVALID_HMD_IDENTIFIER",
                    f"could not generate a valid HMD identifier from {root['name']!r}",
                    "A level-1 name must generate a nonempty NCName identifier.",
                    root["name"], "valid unique HMD identifier", root,
                )
                identifier = f"InvalidHmd{position + 1}"
            folded = identifier.casefold()
            if folded in identifiers:
                self.record_error(
                    "DUPLICATE_HMD_IDENTIFIER",
                    f"duplicate HMD identifier {identifier!r}",
                    "HMD identifiers and output filenames must be unique.",
                    identifier, "unique identifier", root,
                    hmd=identifier, related_row=identifiers[folded],
                )
            else:
                identifiers[folded] = root["_logical_row"]
            self.hmds.append({
                "identifier": identifier,
                "name": root["name"],
                "rows": self.rows[start:end],
                "output_rows": [],
                "zero_zero_row_count": 0,
                "excluded_descendant_count": 0,
                "semantic_path_duplicate_count": 0,
                "qname_duplicate_count": 0,
                "xpath_duplicate_count": 0,
                "filename": f"XBRL_GL_Next_HMD_{identifier}_for_taxonomy.csv",
                "sha256": "",
            })

    def validate_hmd(self, hmd: dict[str, object]) -> None:
        identifier = str(hmd["identifier"])
        rows = hmd["rows"]
        assert isinstance(rows, list)
        root = rows[0]
        if root["type"] != "C":
            self.record_error(
                "INVALID_HMD_ROOT_TYPE", "level-1 HMD root must be type C",
                "Every HMD root must be a Class row.", root["type"], "C",
                root, hmd=identifier,
            )

        ancestors: list[tuple[int, str, str]] = []
        seen_paths: dict[str, str] = {}
        excluded_level: int | None = None
        effective: list[dict[str, str]] = []
        for row in rows:
            level = int(row.get("_level_int", "0"))
            while ancestors and ancestors[-1][0] >= level:
                ancestors.pop()
            if level == 1:
                ancestors.clear()
            elif not ancestors or ancestors[-1][0] != level - 1:
                self.record_error(
                    "INVALID_HMD_HIERARCHY",
                    f"level {level} has no immediate C/R parent",
                    "Each non-root row must have an immediate C/R parent at level-1.",
                    str(level), "immediate C/R parent", row, hmd=identifier,
                )

            semantic_path = row["semantic_path"]
            prior_path = seen_paths.get(semantic_path)
            if not semantic_path:
                self.record_error(
                    "EMPTY_SEMANTIC_PATH", "semantic_path is empty",
                    "Every reviewed row must have a semantic_path.", "",
                    "nonempty unique semantic_path", row, hmd=identifier,
                )
            else:
                self.validate_semantic_path(row, identifier, ancestors)
            if semantic_path:
                if prior_path:
                    hmd["semantic_path_duplicate_count"] = int(
                        hmd["semantic_path_duplicate_count"]
                    ) + 1
                    self.record_error(
                        "DUPLICATE_SEMANTIC_PATH",
                        f"duplicate semantic_path {semantic_path!r}",
                        "semantic_path must be unique within each HMD.",
                        semantic_path, "unique semantic_path", row, hmd=identifier,
                        related_row=prior_path,
                    )
                else:
                    seen_paths[semantic_path] = row["_logical_row"]

            if excluded_level is not None and level <= excluded_level:
                excluded_level = None
            if excluded_level is not None:
                hmd["excluded_descendant_count"] = int(
                    hmd["excluded_descendant_count"]
                ) + 1
            elif row["multiplicity"] == "0..0":
                hmd["zero_zero_row_count"] = int(hmd["zero_zero_row_count"]) + 1
                if row["type"] in {"C", "R"}:
                    excluded_level = level
            else:
                effective.append(dict(row))

            if row["type"] in {"C", "R"}:
                ancestors.append((level, semantic_path, row["module"]))

        if not effective:
            self.record_error(
                "EMPTY_EFFECTIVE_HMD", "all HMD rows were excluded",
                "An HMD must retain its level-1 root.", "0 effective rows",
                ">= 1 effective row", root, hmd=identifier,
            )
            return
        self.generate_and_validate_effective(hmd, effective)

    def generate_and_validate_effective(
        self, hmd: dict[str, object], rows: list[dict[str, str]]
    ) -> None:
        identifier = str(hmd["identifier"])
        ancestors: list[tuple[int, str, str]] = []
        seen_qnames: dict[str, dict[str, str]] = {}
        seen_xpaths: dict[str, str] = {}
        output: list[dict[str, str]] = []
        for row in rows:
            level = int(row["_level_int"])
            while ancestors and ancestors[-1][0] >= level:
                ancestors.pop()
            qname = qualified_name(
                row["module"], row["local_name"], self.module_prefixes
            )
            ancestor_qnames = [
                qualified_name(module, local, self.module_prefixes)
                for _, module, local in ancestors
            ]
            xpath = "/xbrli:xbrl/" + "/".join(ancestor_qnames + [qname])
            prior_qname = seen_qnames.get(qname)
            if prior_qname and definition_signature(prior_qname) != definition_signature(row):
                hmd["qname_duplicate_count"] = int(hmd["qname_duplicate_count"]) + 1
                self.record_error(
                    "HMD_QNAME_DEFINITION_CONFLICT",
                    f"QName {qname!r} has conflicting definitions within one HMD",
                    "Repeated QName use is allowed only for the same taxonomy declaration.",
                    repr(definition_signature(row)),
                    repr(definition_signature(prior_qname)), row, hmd=identifier,
                    related_row=prior_qname["_logical_row"],
                )
            elif prior_qname is None:
                seen_qnames[qname] = row
            prior_xpath = seen_xpaths.get(xpath)
            if prior_xpath:
                hmd["xpath_duplicate_count"] = int(hmd["xpath_duplicate_count"]) + 1
                self.record_error(
                    "DUPLICATE_HMD_XPATH",
                    f"duplicate regenerated xpath {xpath!r}",
                    "Regenerated xpath must be unique within each HMD.",
                    xpath, "unique xpath", row, hmd=identifier,
                    related_row=prior_xpath,
                )
            else:
                seen_xpaths[xpath] = row["_logical_row"]
            row["xpath"] = xpath
            emitted = {name: row[name] for name in LHM_HEADER}
            emitted["_logical_row"] = row["_logical_row"]
            output.append(emitted)
            if row["type"] in {"C", "R"}:
                ancestors.append((level, row["module"], row["local_name"]))
        hmd["output_rows"] = output

    def validate_root_scoped_qnames(self) -> None:
        occurrences: dict[
            tuple[str, str], list[tuple[dict[str, object], dict[str, str]]]
        ] = {}
        for hmd in self.hmds:
            identifier = str(hmd["identifier"])
            for row in hmd["output_rows"]:
                qname = qualified_name(
                    row["module"], row["local_name"], self.module_prefixes
                )
                occurrences.setdefault((identifier, qname), []).append((hmd, row))
        for (_, qname), items in occurrences.items():
            if len(items) < 2:
                continue
            signatures = {definition_signature(row) for _, row in items}
            if len(signatures) == 1:
                continue
            first_hmd, first_row = items[0]
            for hmd, row in items[1:]:
                if definition_signature(row) != definition_signature(first_row):
                    self.record_error(
                        "HMD_QNAME_DEFINITION_CONFLICT",
                        f"QName {qname!r} has conflicting definitions within one HMD",
                        "Repeated QName use within one HMD is allowed only for the same taxonomy declaration.",
                        repr(definition_signature(row)),
                        repr(definition_signature(first_row)), row,
                        hmd=str(hmd["identifier"]),
                        related_row=first_row.get("_logical_row", ""),
                    )

        class_occurrences: dict[
            tuple[str, str],
            list[tuple[dict[str, object], dict[str, str], tuple[tuple[str, str, str], ...]]],
        ] = {}
        for hmd in self.hmds:
            identifier = str(hmd["identifier"])
            rows = hmd["output_rows"]
            assert isinstance(rows, list)
            for index, parent in enumerate(rows):
                if parent["type"] not in {"C", "R"}:
                    continue
                parent_level = int(parent["level"])
                children: list[tuple[str, str, str]] = []
                child_rows: dict[str, dict[str, str]] = {}
                for child in rows[index + 1:]:
                    child_level = int(child["level"])
                    if child_level <= parent_level:
                        break
                    if child_level != parent_level + 1:
                        continue
                    child_qname = qualified_name(
                        child["module"], child["local_name"], self.module_prefixes
                    )
                    prior_child = child_rows.get(child_qname)
                    if prior_child is not None:
                        self.record_error(
                            "DIRECT_CHILD_QNAME_COLLISION",
                            f"Class occurrence has duplicate direct child QName {child_qname!r}",
                            "Distinct direct-child occurrences must not collide on QName.",
                            child_qname, "unique direct-child QName", child,
                            hmd=str(hmd["identifier"]),
                            related_row=prior_child.get("_logical_row", ""),
                        )
                    else:
                        child_rows[child_qname] = child
                    children.append((child_qname, child["type"], child["multiplicity"]))
                parent_qname = qualified_name(
                    parent["module"], parent["local_name"], self.module_prefixes
                )
                class_occurrences.setdefault((identifier, parent_qname), []).append(
                    (hmd, parent, tuple(children))
                )

        for (_, qname), items in class_occurrences.items():
            if len(items) < 2:
                continue
            first_hmd, first_row, first_model = items[0]
            for hmd, row, model in items[1:]:
                if model == first_model:
                    continue
                self.record_error(
                    "QNAME_CONTENT_MODEL_MISMATCH",
                    f"Class QName {qname!r} has inconsistent direct-child content models",
                    "One explicitly reused Class QName within one HMD must have one ordered content model.",
                    repr(model), repr(first_model), row,
                    hmd=str(hmd["identifier"]),
                    related_row=first_row.get("_logical_row", ""),
                )

    def csv_bytes(self, rows: Sequence[Mapping[str, str]], header: Sequence[str]) -> bytes:
        import io
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows({name: row.get(name, "") for name in header} for row in rows)
        return b"\xef\xbb\xbf" + buffer.getvalue().encode("utf-8")

    def manifest_rows(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for hmd in self.hmds:
            input_count = len(hmd["rows"])
            zero_count = int(hmd["zero_zero_row_count"])
            descendant_count = int(hmd["excluded_descendant_count"])
            result.append({
                "hmd_identifier": str(hmd["identifier"]),
                "hmd_name": str(hmd["name"]),
                "file": str(hmd["filename"]),
                "input_row_count": str(input_count),
                "zero_zero_row_count": str(zero_count),
                "excluded_descendant_count": str(descendant_count),
                "excluded_row_count": str(zero_count + descendant_count),
                "output_row_count": str(len(hmd["output_rows"])),
                "semantic_path_duplicate_count": str(
                    hmd["semantic_path_duplicate_count"]
                ),
                "qname_duplicate_count": str(hmd["qname_duplicate_count"]),
                "xpath_duplicate_count": str(hmd["xpath_duplicate_count"]),
                "sha256": str(hmd["sha256"]),
            })
        return result

    def diagnostic_payload(self, status: str) -> dict[str, object]:
        return {
            "status": status,
            "lhm_reviewed": str(self.reviewed_file.resolve()),
            "output_directory": str(self.output_directory.resolve()),
            "manifest": str(self.manifest_file.resolve()),
            "input_row_count": len(self.rows),
            "detected_hmd_count": len(self.hmds),
            "hmds": self.manifest_rows(),
            "shared_qname_count": self.shared_qname_count,
            "shared_qname_definition_mismatch_count": (
                self.shared_qname_definition_mismatch_count
            ),
            "shared_qname_content_model_mismatch_count": (
                self.shared_qname_content_model_mismatch_count
            ),
            "error_count": len(self.errors),
            "errors": self.errors,
            "formal_outputs_issued": self.formal_outputs_issued,
            "upstream_inputs_used": [],
            "note": (
                "Only the authoritative LHM reviewed was read. FSM, BSM, and "
                "candidate LHM were not loaded or compared."
            ),
        }

    def write_diagnostics(self, status: str) -> None:
        payload = self.diagnostic_payload(status)
        self._atomic_write(
            self.diagnostics_file,
            (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        self._atomic_write(
            self.diagnostics_csv_file,
            self.csv_bytes(self.errors, DIAGNOSTIC_CSV_HEADER),
        )

    @staticmethod
    def _atomic_write(path: Path, content: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        os.close(fd)
        temporary = Path(name)
        try:
            temporary.write_bytes(content)
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()

    def publish(self) -> None:
        parent = self.output_directory.parent
        parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{self.output_directory.name}.", dir=parent))
        try:
            for hmd in self.hmds:
                content = self.csv_bytes(hmd["output_rows"], LHM_HEADER)
                hmd["sha256"] = sha256_bytes(content)
                (staging / str(hmd["filename"])).write_bytes(content)
            manifest_content = self.csv_bytes(self.manifest_rows(), MANIFEST_HEADER)
            (staging / self.manifest_file.name).write_bytes(manifest_content)
            os.replace(staging, self.output_directory)
            self.formal_outputs_issued = True
        finally:
            if staging.exists():
                shutil.rmtree(staging)

    def process(self) -> list[dict[str, object]]:
        self.validate_paths()
        self.read_reviewed()
        self.validate_global_rows()
        self.split_hmds()
        for hmd in self.hmds:
            self.validate_hmd(hmd)
        self.validate_root_scoped_qnames()
        self.raise_errors()
        self.publish()
        self.write_diagnostics("PASS")
        return self.hmds

    def format_console_errors(self) -> str:
        blocks = []
        for error in self.errors:
            blocks.append("\n".join([
                f"ERROR: {error['error_code']}",
                f"  message: {error['message']}",
                f"  rule: {error['rule']}",
                f"  actual: {error['actual_value']}",
                f"  expected: {error['expected_value']}",
                f"  LHM row: {error['lhm_row']}",
                f"  HMD: {error['hmd_identifier']}",
                f"  semantic_path: {error['semantic_path']}",
                f"  local_name: {error['local_name']}",
            ]))
        return "\n\n".join(blocks)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate one authoritative 18-column LHM reviewed, split it at "
            "level-1 roots, regenerate xpath, and atomically issue one "
            "HMD-for-taxonomy CSV per root."
        )
    )
    parser.add_argument("reviewed_file", type=Path)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("-e", "--encoding", default="utf-8-sig")
    parser.add_argument("--diagnostics", type=Path)
    parser.add_argument("--diagnostics-csv", type=Path)
    parser.add_argument("--manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    processor = PostGraphWalk(
        args.reviewed_file,
        args.output_directory,
        encoding=args.encoding,
        diagnostics_file=args.diagnostics,
        diagnostics_csv_file=args.diagnostics_csv,
        manifest_file=args.manifest,
    )
    try:
        hmds = processor.process()
    except (OSError, csv.Error, PostGraphWalkError) as exc:
        try:
            processor.write_diagnostics("FAIL")
        except OSError as diagnostics_exc:
            print(
                f"post_graphwalk.py: warning: could not write diagnostics: "
                f"{diagnostics_exc}", file=sys.stderr,
            )
        console = processor.format_console_errors()
        if console:
            print(console, file=sys.stderr)
        print(f"post_graphwalk.py: error: {exc}", file=sys.stderr)
        return 2
    print(
        f"Issued {len(hmds)} HMD-for-taxonomy file(s) to "
        f"{args.output_directory}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

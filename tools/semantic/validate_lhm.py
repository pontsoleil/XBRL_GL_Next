#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: MIT
"""Repeatable checks supporting Part 1 v8 LHM conformance assessment.

Passing this tool does not designate a candidate LHM as authoritative.  That
status requires the recorded assessment of the responsible model definer.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence


BSM_HEADER = [
    "sequence", "level", "property_type", "identifier", "module",
    "class_term", "property_term", "association_role", "representation_term",
    "associated_module", "associated_class", "multiplicity", "definition",
    "label_local", "definition_local", "id",
]
LHM_HEADER = [
    "sequence", "module", "level", "type", "identifier", "name",
    "datatype", "multiplicity", "association_role", "definition",
    "label_local", "definition_local", "source_bsm_id", "semantic_path",
    "associated_module", "class_term",
    "local_name", "xpath",
]
PROHIBITED_COLUMNS = {"domain_name", "id"}
MODULE_PREFIX = {
    "btx": "gl-btx", "bus": "gl-bus", "cor": "gl-cor", "ehm": "gl-ehm",
    "lnk": "gl-lnk", "muc": "gl-muc", "taf": "gl-taf", "usk": "gl-usk",
}
ROW_TYPES = {"C", "A", "R"}
MULTIPLICITIES = {"0..1", "0..*", "1", "1..1", "1..*"}
REVIEW_MULTIPLICITIES = {*MULTIPLICITIES, "0..0"}
IDENTIFIERS = {"", "PK", "REF"}
NCNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path, header: list[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        actual = reader.fieldnames or []
        if actual != header:
            raise ValueError(
                f"{path}: header mismatch; expected {header!r}, got {actual!r}"
            )
        return [dict(row) for row in reader if any((v or "") for v in row.values())]


def multiplicity_bounds(value: str) -> tuple[int, int | None]:
    values = {
        "0..0": (0, 0), "0..1": (0, 1), "0..*": (0, None),
        "1": (1, 1), "1..1": (1, 1), "1..*": (1, None),
    }
    return values[value]


def is_permitted_restriction(candidate: str, reviewed: str) -> bool:
    """Check an LHM-review restriction, not a Specialisation deletion."""
    if candidate not in MULTIPLICITIES or reviewed not in REVIEW_MULTIPLICITIES:
        return False
    candidate_min, candidate_max = multiplicity_bounds(candidate)
    rev_min, rev_max = multiplicity_bounds(reviewed)
    if reviewed == "0..0":
        return candidate_min == 0
    if rev_min < candidate_min:
        return False
    if candidate_max is not None and (
        rev_max is None or rev_max > candidate_max
    ):
        return False
    if rev_max is not None and rev_max < rev_min:
        return False
    return True


def qualified_name(module: str, local_name: str) -> str | None:
    prefix = MODULE_PREFIX.get(module)
    if (
        prefix is None
        or not local_name
        or ":" in local_name
        or not NCNAME.fullmatch(local_name)
    ):
        return None
    return f"{prefix}:{local_name}"


class LHMValidator:
    def __init__(
        self,
        lhm: Path,
        *,
        bsm: Path | None = None,
        comparison: Path | None = None,
        reviewed: Path | None = None,
        graphwalk_diagnostics: Path | None = None,
    ) -> None:
        self.lhm = lhm
        self.bsm = bsm
        self.comparison = comparison
        self.reviewed = reviewed
        self.graphwalk_diagnostics = graphwalk_diagnostics
        self.checks: list[dict[str, object]] = []
        self.errors: list[dict[str, object]] = []

    def error(self, code: str, message: str, **details: object) -> None:
        item: dict[str, object] = {"code": code, "message": message}
        item.update(details)
        self.errors.append(item)

    def check(self, name: str, passed: bool, detail: object = None) -> None:
        self.checks.append({"name": name, "passed": passed, "detail": detail})

    def validate(self) -> dict[str, object]:
        try:
            rows = read_csv(self.lhm, LHM_HEADER)
        except (OSError, csv.Error, ValueError) as exc:
            self.error("LHM_HEADER", str(exc))
            rows = []
        self.check("lhm_header", bool(rows) or not self.errors, LHM_HEADER)

        bsm_ids: set[str] = set()
        resolved_source_rows = 0
        if self.bsm:
            try:
                bsm_rows = read_csv(self.bsm, BSM_HEADER)
                bsm_ids = {row["id"] for row in bsm_rows}
            except (OSError, csv.Error, ValueError) as exc:
                self.error("BSM_INPUT", str(exc))
        else:
            self.error(
                "BSM_REQUIRED",
                "BSM input is required to resolve every source_bsm_id",
            )

        semantic_paths: dict[str, tuple[int, str]] = {}
        row_signatures: dict[tuple[str, ...], int] = {}
        ancestors: list[tuple[int, str, str, str]] = []
        root_paths: list[str] = []
        xpaths: dict[str, tuple[int, str]] = {}
        local_name_occurrences: dict[tuple[str, str], list[int]] = {}
        for index, row in enumerate(rows, start=1):
            line = index + 1
            if row["sequence"] != str(index):
                self.error(
                    "SEQUENCE", "sequence is not continuous", line=line,
                    expected=str(index), actual=row["sequence"],
                )
            try:
                level = int(row["level"])
            except ValueError:
                self.error("LEVEL", "level is not an integer", line=line)
                continue
            if level < 1:
                self.error("LEVEL", "level is less than 1", line=line)
            if row["type"] not in ROW_TYPES:
                self.error("TYPE", "unsupported type", line=line, value=row["type"])
            if row["identifier"] not in IDENTIFIERS:
                self.error(
                    "IDENTIFIER", "unsupported identifier", line=line,
                    value=row["identifier"],
                )
            if row["multiplicity"] not in MULTIPLICITIES:
                self.error(
                    "MULTIPLICITY", "unsupported candidate multiplicity", line=line,
                    value=row["multiplicity"],
                )
            for field in (
                "module", "name", "source_bsm_id", "semantic_path",
                "class_term", "local_name", "xpath",
            ):
                if not row[field]:
                    self.error("REQUIRED", f"{field} is blank", line=line)
            qname = qualified_name(row["module"], row["local_name"])
            if qname is None:
                self.error(
                    "LOCAL_NAME",
                    "local_name is not an unprefixed NCName for a registered module",
                    line=line, module=row["module"], local_name=row["local_name"],
                )
            else:
                local_name_occurrences.setdefault(
                    (row["module"], row["local_name"]), []
                ).append(line)
            source_id = row["source_bsm_id"]
            if bsm_ids and source_id not in bsm_ids:
                self.error(
                    "SOURCE_BSM_ID", "source_bsm_id is absent from BSM", line=line,
                    source_bsm_id=source_id,
                )
            elif source_id and source_id in bsm_ids:
                resolved_source_rows += 1
            path = row["semantic_path"]
            if path in semantic_paths:
                self.error(
                    "SEMANTIC_PATH_DUPLICATE", "semantic_path is duplicated",
                    line=line, first_line=semantic_paths[path][0] + 1,
                    semantic_path=path,
                )
            semantic_paths[path] = (index, source_id)
            signature = tuple(row[name] for name in LHM_HEADER)
            if signature in row_signatures:
                self.error(
                    "DUPLICATE_ROW", "row content is duplicated", line=line,
                    first_line=row_signatures[signature] + 1,
                )
            row_signatures[signature] = index

            while ancestors and ancestors[-1][0] >= level:
                ancestors.pop()
            if level == 1:
                if row["type"] != "C":
                    self.error("ROOT_TYPE", "level-1 row is not C", line=line)
                root_paths.append(path)
                ancestors.clear()
            elif not ancestors or ancestors[-1][0] != level - 1:
                self.error(
                    "HIERARCHY", "row has no immediate C/R parent", line=line,
                    level=level,
                )
            else:
                parent_path = ancestors[-1][1]
                if not path.startswith(parent_path + "."):
                    self.error(
                        "SEMANTIC_PATH_HIERARCHY",
                        "semantic_path does not extend its parent path", line=line,
                        parent_path=parent_path, semantic_path=path,
                    )
            if row["identifier"] == "REF":
                if row["type"] != "A" or not ancestors or ancestors[-1][2] != "R":
                    self.error(
                        "REF_CONTEXT", "REF must be an A row directly below R", line=line
                    )
            expected_xpath = "/xbrli:xbrl/" + "/".join(
                [ancestor[3] for ancestor in ancestors] + [qname or ""]
            )
            if row["xpath"] != expected_xpath:
                self.error(
                    "XPATH",
                    "xpath does not match the hierarchy module/local_name values",
                    line=line, expected=expected_xpath, actual=row["xpath"],
                )
            prior_xpath = xpaths.get(row["xpath"])
            if prior_xpath is not None and prior_xpath[1] != path:
                self.error(
                    "XPATH_DUPLICATE", "xpath is assigned to different paths",
                    line=line, first_line=prior_xpath[0], xpath=row["xpath"],
                    first_semantic_path=prior_xpath[1], semantic_path=path,
                )
            xpaths[row["xpath"]] = (line, path)
            if row["type"] in {"C", "R"}:
                ancestors.append((level, path, row["type"], qname or ""))

        if self.comparison:
            try:
                comparison_rows = read_csv(self.comparison, LHM_HEADER)
                same = rows == comparison_rows
                if not same:
                    self.error(
                        "REPRODUCIBILITY", "comparison LHM is not byte/content equal",
                        comparison=str(self.comparison),
                    )
                self.check("reproducibility", same)
            except (OSError, csv.Error, ValueError) as exc:
                self.error("REPRODUCIBILITY", str(exc))

        if self.reviewed:
            self._validate_review(rows)

        if self.graphwalk_diagnostics:
            try:
                diagnostics = json.loads(
                    self.graphwalk_diagnostics.read_text(encoding="utf-8")
                )
                count = int(diagnostics.get("error_count", 0))
                if count:
                    self.error(
                        "GRAPHWALK_DIAGNOSTICS",
                        "Graph Walk reported unresolved errors", error_count=count,
                    )
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                self.error("GRAPHWALK_DIAGNOSTICS", str(exc))

        self.check("sequence", not any(e["code"] == "SEQUENCE" for e in self.errors))
        self.check("semantic_path_unique", len(semantic_paths) == len(rows))
        self.check(
            "source_bsm_id_present",
            all(bool(row["source_bsm_id"]) for row in rows),
        )
        self.check(
            "source_bsm_id_resolves_to_bsm",
            bool(self.bsm) and resolved_source_rows == len(rows),
            {"resolved_rows": resolved_source_rows, "lhm_rows": len(rows)},
        )
        self.check("root_count", bool(root_paths), len(root_paths))
        duplicate_groups = {
            f"{module}:{local}": lines
            for (module, local), lines in local_name_occurrences.items()
            if len(lines) > 1
        }
        self.check(
            "initial_local_name_duplicates_reported_not_blocking",
            True,
            duplicate_groups,
        )
        return {
            "status": "PASS_SUPPORTING_CHECKS" if not self.errors else "FAIL",
            "authoritative_designation": False,
            "lhm": str(self.lhm),
            "lhm_sha256": sha256(self.lhm) if self.lhm.is_file() else None,
            "row_count": len(rows),
            "checks": self.checks,
            "error_count": len(self.errors),
            "errors": self.errors,
            "note": (
                "A passing result supports, but does not replace, the responsible "
                "model definer's manual review and conformance assessment."
            ),
        }

    def _validate_review(self, candidate: list[dict[str, str]]) -> None:
        try:
            reviewed = read_csv(self.reviewed, LHM_HEADER)  # type: ignore[arg-type]
        except (OSError, csv.Error, ValueError) as exc:
            self.error("LHM_REVIEWED", str(exc))
            return
        if len(reviewed) != len(candidate):
            self.error(
                "LHM_REVIEWED_ROWS", "reviewed row count differs",
                candidate=len(candidate), reviewed=len(reviewed),
            )
            return
        permitted = {"local_name", "multiplicity"}
        for index, (before, after) in enumerate(zip(candidate, reviewed), start=1):
            for column in LHM_HEADER:
                if column not in permitted and before[column] != after[column]:
                    self.error(
                        "LHM_REVIEWED_IMMUTABLE", "immutable reviewed cell changed",
                        line=index + 1, column=column, before=before[column],
                        after=after[column],
                    )
            if qualified_name(after["module"], after["local_name"]) is None:
                self.error(
                    "LHM_REVIEWED_LOCAL_NAME",
                    "reviewed local_name is not an unprefixed NCName",
                    line=index + 1, local_name=after["local_name"],
                )
            if not is_permitted_restriction(
                before["multiplicity"], after["multiplicity"]
            ):
                self.error(
                    "LHM_REVIEWED_MULTIPLICITY",
                    "reviewed multiplicity is not a permitted restriction",
                    line=index + 1, before=before["multiplicity"],
                    after=after["multiplicity"],
                )


def write_report(payload: dict[str, object], path: Path) -> None:
    lines = [
        "# LHM v8 supporting conformance report",
        "",
        f"- Status: `{payload['status']}`",
        f"- Rows: {payload['row_count']}",
        f"- Errors: {payload['error_count']}",
        "- Authoritative designation: `false`",
        "",
        str(payload["note"]),
        "",
        "## Errors",
        "",
    ]
    errors = payload["errors"]
    if errors:
        for item in errors:  # type: ignore[assignment]
            lines.append(f"- `{item['code']}`: {item['message']}")
    else:
        lines.append("- None")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run repeatable checks supporting Part 1 v8 18-column LHM "
            "conformance. "
            "This tool never designates an LHM authoritative."
        )
    )
    parser.add_argument("lhm", type=Path)
    parser.add_argument("--bsm", type=Path, required=True)
    parser.add_argument("--comparison", type=Path)
    parser.add_argument("--reviewed", type=Path)
    parser.add_argument("--graphwalk-diagnostics", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = LHMValidator(
        args.lhm, bsm=args.bsm, comparison=args.comparison,
        reviewed=args.reviewed,
        graphwalk_diagnostics=args.graphwalk_diagnostics,
    ).validate()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_report(payload, args.report)
    print(f"{payload['status']}: {payload['error_count']} error(s)")
    return 0 if payload["status"] == "PASS_SUPPORTING_CHECKS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

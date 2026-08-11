#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: MIT
"""Expand a canonical 16-column BSM into an 18-column candidate LHM.

Graph Walk generates the initial ``local_name`` and physical ``xpath`` for
every emitted occurrence.  QName values are assembled internally from each
row's ``module`` and ``local_name`` and are not stored as a CSV column.  It
never creates or modifies an LHM reviewed.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence


BSM_HEADER = [
    "sequence",
    "level",
    "property_type",
    "identifier",
    "module",
    "class_term",
    "property_term",
    "association_role",
    "representation_term",
    "associated_module",
    "associated_class",
    "multiplicity",
    "definition",
    "label_local",
    "definition_local",
    "id",
]
LHM_HEADER = [
    "sequence",
    "module",
    "level",
    "type",
    "identifier",
    "name",
    "datatype",
    "multiplicity",
    "association_role",
    "definition",
    "label_local",
    "definition_local",
    "source_bsm_id",
    "semantic_path",
    "associated_module",
    "class_term",
    "local_name",
    "xpath",
]

MODULE_PREFIX = {
    "btx": "gl-btx",
    "bus": "gl-bus",
    "cor": "gl-cor",
    "ehm": "gl-ehm",
    "lnk": "gl-lnk",
    "muc": "gl-muc",
    "taf": "gl-taf",
    "usk": "gl-usk",
}

ASSOCIATION_TYPES = {
    "Composition",
    "Aggregation",
    "Reference",
    "Reference Association",
}
REFERENCE_TYPES = {"Reference", "Reference Association"}
COMPOSITION_TYPES = {"Composition", "Aggregation"}
UPPER_ONE = {"1", "0..1", "1..1"}
MULTIPLICITIES = {"0..1", "0..*", "1", "1..1", "1..*"}
NCNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")
CAMEL_BOUNDARIES = (
    (re.compile(r"([A-Z]+)([A-Z][a-z])"), r"\1 \2"),
    (re.compile(r"([a-z0-9])([A-Z])"), r"\1 \2"),
    (re.compile(r"([A-Za-z])([0-9])"), r"\1 \2"),
    (re.compile(r"([0-9])([A-Za-z])"), r"\1 \2"),
)


class GraphWalkError(ValueError):
    """A deterministic canonical LHM cannot be produced."""


def collapse(value: object) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def module_value(value: object) -> str:
    text = collapse(value)
    return re.sub(r"[A-Z]", lambda match: match.group(0).lower(), text)


def normalize_row(row: Mapping[str | None, object]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in BSM_HEADER:
        value = row.get(name, "")
        if name in {"definition", "definition_local"}:
            result[name] = "" if value is None else str(value)
        elif name in {"module", "associated_module"}:
            result[name] = module_value(value)
        else:
            result[name] = collapse(value)
    return result


def class_key(module: str, class_term: str) -> tuple[str, str]:
    return module_value(module), collapse(class_term)


def display_association(role: str, associated_class: str) -> str:
    return f"{role}_ {associated_class}" if role else associated_class


def semantic_path_term(module: str, term: str) -> str:
    """Return a module-qualified semantic-model identifier path segment."""
    collapsed_term = re.sub(r"\s+", "", term)
    return f"{module_value(module)}_{collapsed_term}"


def semantic_path_association(
    module: str, role: str, associated_class: str
) -> str:
    """Return the Association segment used only in semantic_path."""
    role_segment = re.sub(r"\s+", "", role)
    class_segment = re.sub(r"\s+", "", associated_class)
    term = f"{role_segment}_{class_segment}" if role_segment else class_segment
    return f"{module_value(module)}_{term}"


def name_words(value: str) -> list[str]:
    """Return deterministic words for the initial lower-camel local name."""
    text = unicodedata.normalize("NFKC", collapse(value))
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).replace("_", " ")
    for pattern, replacement in CAMEL_BOUNDARIES:
        text = pattern.sub(replacement, text)
    return [word for word in text.split() if word]


def local_name_from_name(name: str) -> str:
    words = name_words(name)
    if not words:
        raise GraphWalkError("name does not contain a usable local-name word")
    local = words[0].lower() + "".join(
        word.lower()[:1].upper() + word.lower()[1:] for word in words[1:]
    )
    if not NCNAME.fullmatch(local):
        raise GraphWalkError(
            f"name generates an invalid XML Schema NCName: {name!r} -> {local!r}"
        )
    return local


def qualified_name(
    module: str, local_name: str, module_prefixes: Mapping[str, str]
) -> str:
    """Build a QName internally without adding a QName column to the LHM."""
    try:
        prefix = module_prefixes[module]
    except KeyError as exc:
        raise GraphWalkError(
            f"module has no registered taxonomy prefix: {module!r}"
        ) from exc
    if not local_name or ":" in local_name or not NCNAME.fullmatch(local_name):
        raise GraphWalkError(
            f"local_name is not a valid XML Schema NCName: {local_name!r}"
        )
    return f"{prefix}:{local_name}"


@dataclass
class BSMRow:
    values: dict[str, str]
    line: int
    owner: tuple[str, str] | None = None


@dataclass
class BSMClass:
    key: tuple[str, str]
    row: BSMRow
    properties: list[BSMRow] = field(default_factory=list)


class GraphWalk:
    def __init__(
        self,
        bsm_file: str | Path,
        lhm_file: str | Path,
        roots: Sequence[str],
        *,
        encoding: str = "utf-8-sig",
        diagnostics_file: str | Path | None = None,
        module_prefixes: Mapping[str, str] | None = None,
    ) -> None:
        self.bsm_file = Path(bsm_file)
        self.lhm_file = Path(lhm_file)
        self.root_selectors = list(roots)
        self.encoding = encoding
        self.diagnostics_file = (
            Path(diagnostics_file)
            if diagnostics_file
            else self.lhm_file.with_name(
                f"{self.lhm_file.stem}_graphwalk_diagnostics.json"
            )
        )
        self.module_prefixes = dict(
            MODULE_PREFIX if module_prefixes is None else module_prefixes
        )
        self.classes: OrderedDict[tuple[str, str], BSMClass] = OrderedDict()
        self.rows: list[dict[str, str]] = []
        self._semantic_paths: dict[str, int] = {}
        self._source_bsm_ids: dict[str, tuple[int, str]] = {}
        self._local_name_occurrences: dict[
            tuple[str, str], list[dict[str, object]]
        ] = {}
        self.diagnostics: list[dict[str, object]] = []

    def validate_paths(self) -> None:
        paths = [
            self.bsm_file.resolve(),
            self.lhm_file.resolve(),
            self.diagnostics_file.resolve(),
        ]
        if len(set(paths)) != len(paths):
            raise GraphWalkError(
                "BSM input, candidate LHM output, and diagnostics must use "
                "three different paths"
            )

    def diagnostic(
        self,
        severity: str,
        code: str,
        message: str,
        *,
        bsm_line: int | None = None,
        **details: object,
    ) -> None:
        item: dict[str, object] = {
            "severity": severity,
            "code": code,
            "message": message,
        }
        if bsm_line is not None:
            item["bsm_file"] = str(self.bsm_file)
            item["bsm_line"] = bsm_line
        item.update(details)
        self.diagnostics.append(item)

    def load(self) -> None:
        if not self.bsm_file.is_file():
            raise GraphWalkError(f"BSM input does not exist: {self.bsm_file}")
        with self.bsm_file.open(encoding=self.encoding, newline="") as handle:
            reader = csv.DictReader(handle)
            actual = reader.fieldnames or []
            if actual != BSM_HEADER:
                raise GraphWalkError(
                    f"{self.bsm_file}: BSM header mismatch; "
                    f"expected {BSM_HEADER!r}, got {actual!r}"
                )
            current: BSMClass | None = None
            ids: dict[str, int] = {}
            for line, raw in enumerate(reader, start=2):
                if not any("" if value is None else str(value) for value in raw.values()):
                    continue
                row = BSMRow(normalize_row(raw), line)
                values = row.values
                if not values["id"]:
                    raise GraphWalkError(f"{self.bsm_file}:{line}: id is required")
                if values["id"] in ids:
                    raise GraphWalkError(
                        f"{self.bsm_file}:{line}: duplicate id {values['id']!r}; "
                        f"first used at line {ids[values['id']]}"
                    )
                ids[values["id"]] = line

                if values["property_type"] == "Class":
                    if not values["module"] or not values["class_term"]:
                        raise GraphWalkError(
                            f"{self.bsm_file}:{line}: Class requires module and class_term"
                        )
                    key = class_key(values["module"], values["class_term"])
                    if key in self.classes:
                        raise GraphWalkError(
                            f"{self.bsm_file}:{line}: duplicate Class {key!r}"
                        )
                    current = BSMClass(key, row)
                    row.owner = key
                    self.classes[key] = current
                    continue

                if current is None:
                    raise GraphWalkError(
                        f"{self.bsm_file}:{line}: property appears before a Class"
                    )
                row.owner = current.key
                if (
                    values["module"] != current.key[0]
                    or values["class_term"] != current.key[1]
                ):
                    raise GraphWalkError(
                        f"{self.bsm_file}:{line}: property owner "
                        f"{(values['module'], values['class_term'])!r} does not match "
                        f"owning Class {current.key!r}"
                    )
                if values["property_type"] not in {"Attribute", *ASSOCIATION_TYPES}:
                    raise GraphWalkError(
                        f"{self.bsm_file}:{line}: unsupported property_type "
                        f"{values['property_type']!r}"
                    )
                if values["multiplicity"] not in MULTIPLICITIES:
                    raise GraphWalkError(
                        f"{self.bsm_file}:{line}: invalid multiplicity "
                        f"{values['multiplicity']!r}"
                    )
                if values["property_type"] in ASSOCIATION_TYPES:
                    if not values["associated_module"] or not values["associated_class"]:
                        raise GraphWalkError(
                            f"{self.bsm_file}:{line}: Association requires "
                            "associated_module and associated_class"
                        )
                    target = class_key(
                        values["associated_module"], values["associated_class"]
                    )
                    if target not in self.classes:
                        # Forward references are checked after the complete file is loaded.
                        pass
                current.properties.append(row)

        for definition in self.classes.values():
            for row in definition.properties:
                values = row.values
                if values["property_type"] in ASSOCIATION_TYPES:
                    target = class_key(
                        values["associated_module"], values["associated_class"]
                    )
                    if target not in self.classes:
                        raise GraphWalkError(
                            f"{self.bsm_file}:{row.line}: undefined associated Class "
                            f"{target!r}"
                        )
                elif values["associated_module"] or values["associated_class"]:
                    raise GraphWalkError(
                        f"{self.bsm_file}:{row.line}: Attribute must not define "
                        "associated Class"
                    )

    def resolve_roots(self) -> list[tuple[str, str]]:
        roots: list[tuple[str, str]] = []
        for selector_group in self.root_selectors:
            for selector in (part for part in selector_group.split("+") if part):
                if ":" in selector:
                    module, term = selector.split(":", 1)
                    key = class_key(module, term)
                    if key not in self.classes:
                        raise GraphWalkError(f"Unknown root Class selector: {selector!r}")
                else:
                    candidates = [
                        key for key in self.classes if key[1] == collapse(selector)
                    ]
                    if len(candidates) != 1:
                        raise GraphWalkError(
                            f"Root {selector!r} resolves to {len(candidates)} Classes: "
                            f"{candidates!r}"
                        )
                    key = candidates[0]
                if key not in roots:
                    roots.append(key)
        if not roots:
            raise GraphWalkError("At least one --root is required")
        return roots

    def append_row(
        self,
        row: dict[str, str],
        segments: list[str],
    ) -> None:
        row["sequence"] = str(len(self.rows) + 1)
        row["semantic_path"] = "$." + ".".join(segments)
        if row["semantic_path"] in self._semantic_paths:
            first = self._semantic_paths[row["semantic_path"]]
            self.diagnostic(
                "error", "SEMANTIC_PATH_DUPLICATE",
                "semantic_path is duplicated",
                first_output_row=first,
                output_row=len(self.rows) + 1,
                semantic_path=row["semantic_path"],
            )
            raise GraphWalkError(
                f"Duplicate semantic_path {row['semantic_path']!r} at output rows "
                f"{first} and {len(self.rows) + 1}"
            )
        local = local_name_from_name(row["name"])
        qname = qualified_name(row["module"], local, self.module_prefixes)
        row["local_name"] = local
        row["xpath"] = ""
        occurrence = {
            "output_row": len(self.rows) + 1,
            "module": row["module"],
            "local_name": local,
            "qname": qname,
            "semantic_path": row["semantic_path"],
            "source_bsm_id": row["source_bsm_id"],
        }
        self._local_name_occurrences.setdefault((row["module"], local), []).append(
            occurrence
        )

        source_bsm_id = row["source_bsm_id"]
        prior = self._source_bsm_ids.get(source_bsm_id)
        if prior is not None:
            prior_row, prior_path = prior
            self.diagnostic(
                "info", "SOURCE_BSM_ID_REUSED",
                "source_bsm_id is reused in another traversal context",
                source_bsm_id=source_bsm_id,
                first_output_row=prior_row,
                first_semantic_path=prior_path,
                output_row=len(self.rows) + 1,
                semantic_path=row["semantic_path"],
            )
        self.rows.append(row)
        self._semantic_paths[row["semantic_path"]] = len(self.rows)
        if prior is None:
            self._source_bsm_ids[source_bsm_id] = (
                len(self.rows), row["semantic_path"]
            )

    def base_row(
        self,
        *,
        module: str,
        level: int,
        row_type: str,
        identifier: str,
        name: str,
        datatype: str,
        multiplicity: str,
        association_role: str,
        definition: str,
        label_local: str,
        definition_local: str,
        source_bsm_id: str,
        associated_module: str,
        class_term: str,
    ) -> dict[str, str]:
        return {
            "sequence": "",
            "module": module,
            "level": str(level),
            "type": row_type,
            "identifier": identifier,
            "name": name,
            "datatype": datatype,
            "multiplicity": multiplicity,
            "association_role": association_role,
            "definition": definition,
            "label_local": label_local,
            "definition_local": definition_local,
            "source_bsm_id": source_bsm_id,
            "semantic_path": "",
            "associated_module": associated_module,
            "class_term": class_term,
            "local_name": "",
            "xpath": "",
        }

    def assign_xpaths(self) -> None:
        """Build every initial XPath from the emitted C/R occurrence hierarchy."""
        ancestors: list[tuple[int, str, str, str]] = []
        assigned: dict[str, tuple[int, str]] = {}
        for index, row in enumerate(self.rows, start=1):
            level = int(row["level"])
            while ancestors and ancestors[-1][0] >= level:
                ancestors.pop()
            if level == 1:
                if row["type"] != "C":
                    raise GraphWalkError(
                        f"Output row {index}: level 1 must be type C"
                    )
                ancestors.clear()
            elif not ancestors or ancestors[-1][0] != level - 1:
                raise GraphWalkError(
                    f"Output row {index}: level {level} has no unique immediate "
                    "C/R parent"
                )
            current_qname = qualified_name(
                row["module"], row["local_name"], self.module_prefixes
            )
            ancestor_qnames = [
                qualified_name(item[1], item[2], self.module_prefixes)
                for item in ancestors
            ]
            row["xpath"] = "/xbrli:xbrl/" + "/".join(
                ancestor_qnames + [current_qname]
            )
            prior = assigned.get(row["xpath"])
            if prior is not None and prior[1] != row["semantic_path"]:
                self.diagnostic(
                    "error",
                    "XPATH_COLLISION",
                    "initial xpath is assigned to different semantic_path values",
                    xpath=row["xpath"],
                    first_output_row=prior[0],
                    first_semantic_path=prior[1],
                    output_row=index,
                    semantic_path=row["semantic_path"],
                )
                raise GraphWalkError(
                    f"XPath collision {row['xpath']!r}: {prior[1]!r} and "
                    f"{row['semantic_path']!r}"
                )
            assigned[row["xpath"]] = (index, row["semantic_path"])
            if row["type"] in {"C", "R"}:
                ancestors.append(
                    (level, row["module"], row["local_name"], row["type"])
                )

    def diagnose_local_name_duplicates(self) -> None:
        """Report initial taxonomy-name collisions without blocking generation."""
        for (module, local), occurrences in self._local_name_occurrences.items():
            if len(occurrences) < 2:
                continue
            self.diagnostic(
                "warning",
                "LOCAL_NAME_DUPLICATE",
                "initial (module, local_name) is reused; model-definer "
                "review is required before post-Graph Walk processing",
                module=module,
                local_name=local,
                occurrence_count=len(occurrences),
                occurrences=occurrences,
            )

    def walk_class(
        self,
        key: tuple[str, str],
        *,
        level: int,
        segments: list[str],
        selected_modules: dict[str, str],
        stack: list[tuple[str, str]],
    ) -> None:
        if key in stack:
            cycle = " -> ".join(f"{m}:{c}" for m, c in [*stack, key])
            raise GraphWalkError(f"Composition cycle detected: {cycle}")
        selected = selected_modules.get(key[1])
        if selected is not None and selected != key[0]:
            raise GraphWalkError(
                f"One hierarchy selects same-named Class {key[1]!r} from "
                f"both {selected!r} and {key[0]!r}"
            )
        selected_modules[key[1]] = key[0]
        definition = self.classes[key]
        stack.append(key)

        for item in definition.properties:
            values = item.values
            kind = values["property_type"]
            if kind == "Attribute":
                row = self.base_row(
                    module=values["module"],
                    level=level,
                    row_type="A",
                    identifier=values["identifier"],
                    name=values["property_term"],
                    datatype=values["representation_term"],
                    multiplicity=values["multiplicity"],
                    association_role="",
                    definition=values["definition"],
                    label_local=values["label_local"],
                    definition_local=values["definition_local"],
                    source_bsm_id=values["id"],
                    associated_module=key[0],
                    class_term=key[1],
                )
                self.append_row(
                    row,
                    [
                        *segments,
                        semantic_path_term(values["module"], values["property_term"]),
                    ],
                )
                continue

            target_key = class_key(
                values["associated_module"], values["associated_class"]
            )
            association_name = display_association(
                values["association_role"], values["associated_class"]
            )
            association_path_segment = semantic_path_association(
                values["module"], values["association_role"],
                values["associated_class"]
            )
            if kind in COMPOSITION_TYPES:
                target = self.classes[target_key]
                class_values = target.row.values
                row = self.base_row(
                    module=target_key[0],
                    level=level,
                    row_type="C",
                    identifier=values["identifier"],
                    name=association_name,
                    datatype="",
                    multiplicity=values["multiplicity"],
                    association_role=values["association_role"],
                    definition=values["definition"] or class_values["definition"],
                    label_local=values["label_local"] or class_values["label_local"],
                    definition_local=(
                        values["definition_local"] or class_values["definition_local"]
                    ),
                    source_bsm_id=values["id"],
                    associated_module=target_key[0],
                    class_term=target_key[1],
                )
                child_segments = [*segments, association_path_segment]
                self.append_row(
                    row,
                    child_segments,
                )
                self.walk_class(
                    target_key,
                    level=level + 1,
                    segments=child_segments,
                    selected_modules=selected_modules,
                    stack=stack,
                )
                continue

            target = self.classes[target_key]
            row = self.base_row(
                module=target_key[0],
                level=level,
                row_type="R",
                identifier=values["identifier"],
                name=association_name,
                datatype="",
                multiplicity=values["multiplicity"],
                association_role=values["association_role"],
                definition=values["definition"],
                label_local=values["label_local"],
                definition_local=values["definition_local"],
                source_bsm_id=values["id"],
                associated_module=target_key[0],
                class_term=target_key[1],
            )
            reference_segments = [*segments, association_path_segment]
            self.append_row(row, reference_segments)
            primary_keys = [
                pk
                for pk in target.properties
                if pk.values["property_type"] == "Attribute"
                and pk.values["identifier"] == "PK"
            ]
            if not primary_keys:
                self.diagnostic(
                    "error",
                    "reference-target-pk-missing",
                    (
                        "Reference Association target has no Attribute with "
                        "identifier=PK; emitted the R row, skipped all rows below "
                        "that reference occurrence, and resumed the originating Class"
                    ),
                    bsm_line=item.line,
                    originating_module=key[0],
                    originating_class=key[1],
                    association_role=values["association_role"],
                    associated_module=target_key[0],
                    associated_class=target_key[1],
                    reference_id=values["id"],
                    reference_semantic_path=row["semantic_path"],
                )
                continue
            for pk in primary_keys:
                pk_values = pk.values
                ref = self.base_row(
                    module=target_key[0],
                    level=level + 1,
                    row_type="A",
                    identifier="REF",
                    name=pk_values["property_term"],
                    datatype=pk_values["representation_term"],
                    multiplicity=pk_values["multiplicity"],
                    association_role="",
                    definition=pk_values["definition"],
                    label_local=pk_values["label_local"],
                    definition_local=pk_values["definition_local"],
                    source_bsm_id=pk_values["id"],
                    associated_module=target_key[0],
                    class_term=target_key[1],
                )
                self.append_row(
                    ref,
                    [
                        *reference_segments,
                        semantic_path_term(
                            pk_values["module"], pk_values["property_term"]
                        ),
                    ],
                )

        stack.pop()

    def generate(self) -> list[dict[str, str]]:
        for root_key in self.resolve_roots():
            definition = self.classes[root_key]
            values = definition.row.values
            root_segments = [semantic_path_term(root_key[0], root_key[1])]
            root = self.base_row(
                module=root_key[0],
                level=1,
                row_type="C",
                identifier=values["identifier"],
                name=root_key[1],
                datatype="",
                multiplicity=values["multiplicity"],
                association_role="",
                definition=values["definition"],
                label_local=values["label_local"],
                definition_local=values["definition_local"],
                source_bsm_id=values["id"],
                associated_module=root_key[0],
                class_term=root_key[1],
            )
            self.append_row(
                root,
                root_segments,
            )
            self.walk_class(
                root_key,
                level=2,
                segments=root_segments,
                selected_modules={},
                stack=[],
            )
        return self.rows

    def write(self) -> None:
        self.lhm_file.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{self.lhm_file.name}.",
            suffix=".tmp",
            dir=self.lhm_file.parent,
        )
        os.close(fd)
        temporary = Path(temporary_name)
        try:
            with temporary.open("w", encoding=self.encoding, newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=LHM_HEADER, lineterminator="\n")
                writer.writeheader()
                writer.writerows(
                    {name: row.get(name, "") for name in LHM_HEADER}
                    for row in self.rows
                )
            os.replace(temporary, self.lhm_file)
        finally:
            if temporary.exists():
                temporary.unlink()

    def graph_walk(self) -> list[dict[str, str]]:
        self.validate_paths()
        self.load()
        rows = self.generate()
        self.assign_xpaths()
        self.diagnose_local_name_duplicates()
        self.write()
        self.write_diagnostics()
        return rows

    def write_diagnostics(self) -> None:
        self.diagnostics_file.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{self.diagnostics_file.name}.",
            suffix=".tmp",
            dir=self.diagnostics_file.parent,
        )
        os.close(fd)
        temporary = Path(temporary_name)
        try:
            payload = {
                "bsm_file": str(self.bsm_file),
                "output_file": str(self.lhm_file),
                "diagnostic_count": len(self.diagnostics),
                "error_count": sum(
                    item["severity"] == "error" for item in self.diagnostics
                ),
                "diagnostics": self.diagnostics,
            }
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            os.replace(temporary, self.diagnostics_file)
        finally:
            if temporary.exists():
                temporary.unlink()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the canonical Part 1 v8 18-column candidate LHM from "
            "a 16-column BSM and one or more ordered roots."
        )
    )
    parser.add_argument("BSM_file")
    parser.add_argument("LHM_file")
    parser.add_argument("-r", "--root", action="append", required=True)
    parser.add_argument("-e", "--encoding", default="utf-8-sig")
    parser.add_argument(
        "--diagnostics",
        help=(
            "JSON diagnostics path; defaults to "
            "<LHM_file_stem>_graphwalk_diagnostics.json"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    processor = GraphWalk(
        args.BSM_file,
        args.LHM_file,
        args.root,
        encoding=args.encoding,
        diagnostics_file=args.diagnostics,
    )
    try:
        rows = processor.graph_walk()
    except (OSError, csv.Error, GraphWalkError) as exc:
        processor.diagnostic("error", "GRAPHWALK_ABORTED", str(exc))
        try:
            processor.write_diagnostics()
        except OSError as diagnostics_exc:
            print(
                f"graphwalk.py: warning: could not write diagnostics: "
                f"{diagnostics_exc}", file=sys.stderr,
            )
        print(f"graphwalk.py: error: {exc}", file=sys.stderr)
        return 2
    root_count = len(processor.resolve_roots())
    output_kind = "candidate LHM"
    print(f"Wrote {len(rows)} {output_kind} row(s) for {root_count} root(s) "
          f"to {args.LHM_file}")
    error_count = sum(
        item["severity"] == "error" for item in processor.diagnostics
    )
    if error_count:
        print(
            f"graphwalk.py: completed with {error_count} non-fatal error "
            f"diagnostic(s); see {processor.diagnostics_file}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

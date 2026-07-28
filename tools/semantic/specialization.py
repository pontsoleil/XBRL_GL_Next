#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: MIT
"""Generate the canonical 15-column XBRL GL Next BSM from 14-column FSM CSVs."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import os
import re
import sys
import tempfile
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence


FSM_HEADER = [
    "sequence",
    "level",
    "property_type",
    "identifier",
    "module",
    "class_term",
    "property_term",
    "representation_term",
    "associated_module",
    "associated_class",
    "multiplicity",
    "definition",
    "label_local",
    "definition_local",
]
BSM_HEADER = [*FSM_HEADER, "id"]

CLASS_TYPES = {"Class", "Abstract Class"}
ASSOCIATION_TYPES = {
    "Composition",
    "Aggregation",
    "Reference",
    "Reference Association",
}
PROPERTY_TYPES = {"Attribute", *ASSOCIATION_TYPES}
DELETION_MULTIPLICITIES = {"0", "0..0"}
MULTIPLICITIES = {"0", "0..0", "0..1", "0..*", "1", "1..1", "1..*"}
KNOWN_MODULE_ABBREVIATIONS = {
    "bus": "BU",
    "cor": "CO",
    "muc": "MU",
    "lnk": "LN",
    "usk": "US",
    "ehm": "EH",
    "taf": "TA",
    "btx": "BT",
}


class SpecializationError(ValueError):
    """A deterministic canonical BSM cannot be produced."""


def collapse(value: object) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def module_value(value: object) -> str:
    text = collapse(value)
    return re.sub(r"[A-Z]", lambda match: match.group(0).lower(), text)


def free_text(value: object) -> str:
    """Preserve free text while normalizing line endings for valid CSV output."""
    return ("" if value is None else str(value)).replace("\r\n", "\n").replace("\r", "\n")


def normalize_row(row: Mapping[str | None, object]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in FSM_HEADER:
        value = row.get(name, "")
        if name in {"definition", "definition_local"}:
            result[name] = free_text(value)
        elif name in {"module", "associated_module"}:
            result[name] = module_value(value)
        else:
            result[name] = collapse(value)
    return result


def reject_qname(value: str, *, field_name: str, location: str) -> None:
    if ":" in value:
        raise SpecializationError(
            f"{location}: {field_name} must be a logical model value, not QName {value!r}"
        )


def class_key(module: str, class_term: str) -> tuple[str, str]:
    return module_value(module), collapse(class_term)


def property_identity(row: Mapping[str, str]) -> tuple[str, ...]:
    kind = row.get("property_type", "")
    term = collapse(row.get("property_term", ""))
    if kind == "Attribute":
        if not term:
            raise SpecializationError("Attribute property_term is required")
        return ("Attribute", term)
    if kind in ASSOCIATION_TYPES:
        return (
            "Association",
            term,
            module_value(row.get("associated_module", "")),
            collapse(row.get("associated_class", "")),
        )
    raise SpecializationError(f"Unsupported property_type for identity: {kind!r}")


@dataclass
class SourceRow:
    values: dict[str, str]
    source: Path
    line: int
    owner: tuple[str, str] | None = None
    origin: tuple[str, str] | None = None

    @property
    def location(self) -> str:
        sequence = self.values.get("sequence", "")
        suffix = f", sequence {sequence}" if sequence else ""
        return f"{self.source}:{self.line}{suffix}"


@dataclass
class ClassDefinition:
    key: tuple[str, str]
    row: SourceRow
    order: int
    parents: list[tuple[str, str]] = field(default_factory=list)
    properties: list[SourceRow] = field(default_factory=list)

    @property
    def abstract(self) -> bool:
        return self.row.values["property_type"] == "Abstract Class"


class Specialization:
    def __init__(
        self,
        fsm_files: Sequence[str | Path],
        bsm_file: str | Path,
        *,
        encoding: str = "utf-8-sig",
        module_abbreviations: Mapping[str, str] | None = None,
        diagnostics_file: str | Path | None = None,
        strict_deletions: bool = False,
    ) -> None:
        self.fsm_files = [Path(item) for item in fsm_files]
        self.bsm_file = Path(bsm_file)
        self.encoding = encoding
        self.module_abbreviations = dict(KNOWN_MODULE_ABBREVIATIONS)
        if module_abbreviations:
            self.module_abbreviations.update(
                {module_value(k): collapse(v).upper() for k, v in module_abbreviations.items()}
            )
        self.diagnostics_file = Path(diagnostics_file) if diagnostics_file else None
        self.strict_deletions = strict_deletions
        self.classes: OrderedDict[tuple[str, str], ClassDefinition] = OrderedDict()
        self._resolved: dict[tuple[str, str], OrderedDict[tuple[str, ...], SourceRow]] = {}
        self._resolving: list[tuple[str, str]] = []
        self.diagnostics: list[dict[str, object]] = []
        self._class_counter = 0

    def diagnostic(
        self,
        severity: str,
        code: str,
        message: str,
        row: SourceRow | None = None,
        **details: object,
    ) -> None:
        item: dict[str, object] = {
            "severity": severity,
            "code": code,
            "message": message,
        }
        if row:
            item.update(
                {
                    "input_file": str(row.source),
                    "line": row.line,
                    "sequence": row.values.get("sequence", ""),
                }
            )
        item.update(details)
        self.diagnostics.append(item)

    def _read_file(self, path: Path) -> list[SourceRow]:
        if not path.is_file():
            raise SpecializationError(f"FSM input does not exist: {path}")
        with path.open(encoding=self.encoding, newline="") as handle:
            reader = csv.DictReader(handle)
            actual = reader.fieldnames or []
            if actual != FSM_HEADER:
                raise SpecializationError(
                    f"{path}: FSM header mismatch; expected {FSM_HEADER!r}, got {actual!r}"
                )
            return [
                SourceRow(normalize_row(row), path, line)
                for line, row in enumerate(reader, start=2)
                if any("" if value is None else str(value) for value in row.values())
            ]

    def load(self) -> None:
        all_keys: set[tuple[str, str]] = set()
        for path in self.fsm_files:
            rows = self._read_file(path)
            current: ClassDefinition | None = None
            for source_row in rows:
                row = source_row.values
                kind = row["property_type"]
                required = ("sequence", "level", "property_type", "module", "class_term", "multiplicity")
                missing = [name for name in required if not row[name]]
                if missing:
                    raise SpecializationError(
                        f"{source_row.location}: required field(s) are empty: {missing!r}"
                    )
                if row["multiplicity"] not in MULTIPLICITIES:
                    raise SpecializationError(
                        f"{source_row.location}: invalid multiplicity "
                        f"{row['multiplicity']!r}; expected one of {sorted(MULTIPLICITIES)!r}"
                    )
                if kind in CLASS_TYPES:
                    if not row["module"] or not row["class_term"]:
                        raise SpecializationError(
                            f"{source_row.location}: Class requires module and class_term"
                        )
                    reject_qname(row["module"], field_name="module", location=source_row.location)
                    reject_qname(
                        row["class_term"],
                        field_name="class_term",
                        location=source_row.location,
                    )
                    key = class_key(row["module"], row["class_term"])
                    if key in all_keys:
                        previous = self.classes[key].row.location
                        raise SpecializationError(
                            f"{source_row.location}: duplicate Class {key!r}; first defined at {previous}"
                        )
                    all_keys.add(key)
                    self._class_counter += 1
                    current = ClassDefinition(key, source_row, self._class_counter)
                    self.classes[key] = current
                    source_row.owner = key
                    source_row.origin = key
                    continue

                if current is None:
                    raise SpecializationError(
                        f"{source_row.location}: row appears before a Class boundary"
                    )
                source_row.owner = current.key
                source_row.origin = current.key
                if row["module"] != current.key[0]:
                    raise SpecializationError(
                        f"{source_row.location}: module {row['module']!r} does not match "
                        f"owning Class module {current.key[0]!r}"
                    )
                if row["class_term"] and row["class_term"] != current.key[1]:
                    raise SpecializationError(
                        f"{source_row.location}: class_term {row['class_term']!r} "
                        f"does not match owning Class {current.key[1]!r}"
                    )
                row["class_term"] = current.key[1]
                row["module"] = current.key[0]

                if kind == "Specialization":
                    self._validate_reference(source_row)
                    parent = class_key(row["associated_module"], row["associated_class"])
                    if parent in current.parents:
                        raise SpecializationError(
                            f"{source_row.location}: duplicate Specialization {parent!r}"
                        )
                    current.parents.append(parent)
                elif kind in PROPERTY_TYPES:
                    if kind in ASSOCIATION_TYPES:
                        self._validate_reference(source_row)
                    elif row["associated_module"] or row["associated_class"]:
                        raise SpecializationError(
                            f"{source_row.location}: Attribute must not define associated Class"
                        )
                    elif not row["property_term"] or not row["representation_term"]:
                        raise SpecializationError(
                            f"{source_row.location}: Attribute requires property_term "
                            "and representation_term"
                        )
                    current.properties.append(source_row)
                else:
                    raise SpecializationError(
                        f"{source_row.location}: unsupported property_type {kind!r}"
                    )

        for definition in self.classes.values():
            seen: dict[tuple[str, ...], SourceRow] = {}
            for item in definition.properties:
                try:
                    identity = property_identity(item.values)
                except SpecializationError as exc:
                    raise SpecializationError(f"{item.location}: {exc}") from exc
                if identity in seen:
                    raise SpecializationError(
                        f"{item.location}: duplicate property identity {identity!r} in "
                        f"{definition.key!r}; first defined at {seen[identity].location}"
                    )
                seen[identity] = item

        for definition in self.classes.values():
            for parent in definition.parents:
                if parent not in self.classes:
                    raise SpecializationError(
                        f"{definition.row.location}: undefined superclass {parent!r} "
                        f"for {definition.key!r}"
                    )
            for item in definition.properties:
                if item.values["property_type"] in ASSOCIATION_TYPES:
                    target = class_key(
                        item.values["associated_module"],
                        item.values["associated_class"],
                    )
                    if target not in self.classes:
                        raise SpecializationError(
                            f"{item.location}: undefined associated Class {target!r} "
                            f"from {definition.key!r}"
                        )

    def _validate_reference(self, item: SourceRow) -> None:
        row = item.values
        if not row["associated_module"] or not row["associated_class"]:
            raise SpecializationError(
                f"{item.location}: {row['property_type']} requires associated_module "
                "and associated_class"
            )
        reject_qname(
            row["associated_module"],
            field_name="associated_module",
            location=item.location,
        )
        reject_qname(
            row["associated_class"],
            field_name="associated_class",
            location=item.location,
        )

    def _merge(self, inherited: SourceRow, child: SourceRow) -> SourceRow:
        merged = copy.deepcopy(inherited)
        for name in FSM_HEADER:
            value = child.values.get(name, "")
            if value or name in {"property_type", "multiplicity"}:
                merged.values[name] = value
        assert child.owner is not None
        merged.owner = child.owner
        merged.origin = child.origin
        merged.values["module"] = child.owner[0]
        merged.values["class_term"] = child.owner[1]
        merged.source = child.source
        merged.line = child.line
        return merged

    def resolve_class(
        self, key: tuple[str, str]
    ) -> OrderedDict[tuple[str, ...], SourceRow]:
        if key in self._resolved:
            return copy.deepcopy(self._resolved[key])
        if key in self._resolving:
            cycle = " -> ".join(f"{module}:{term}" for module, term in [*self._resolving, key])
            raise SpecializationError(f"Specialization cycle detected: {cycle}")
        self._resolving.append(key)
        definition = self.classes[key]
        result: OrderedDict[tuple[str, ...], SourceRow] = OrderedDict()

        for parent in definition.parents:
            for identity, item in self.resolve_class(parent).items():
                if identity in result:
                    raise SpecializationError(
                        f"{definition.row.location}: inherited property identity "
                        f"{identity!r} is supplied by multiple super Classes of "
                        f"{definition.key!r}"
                    )
                inherited = copy.deepcopy(item)
                inherited.owner = key
                inherited.values["module"] = key[0]
                inherited.values["class_term"] = key[1]
                result[identity] = inherited

        for item in definition.properties:
            identity = property_identity(item.values)
            deletion = item.values["multiplicity"] in DELETION_MULTIPLICITIES
            if deletion:
                if identity in result:
                    removed = result.pop(identity)
                    origin = removed.origin or removed.owner
                    self.diagnostic(
                        "info",
                        "property-deleted",
                        f"Inherited property {identity!r} was removed from {definition.key!r}",
                        item,
                        child_class={"module": key[0], "class_term": key[1]},
                        property_identity=list(identity),
                        removed_property_origin=(
                            {"module": origin[0], "class_term": origin[1]}
                            if origin
                            else None
                        ),
                        removed_property_source={
                            "input_file": str(removed.source),
                            "line": removed.line,
                            "sequence": removed.values.get("sequence", ""),
                        },
                        bsm_reflection="not-emitted",
                        descendant_inheritance="blocked",
                    )
                else:
                    message = (
                        f"Deletion instruction {identity!r} has no inherited property "
                        f"in {definition.key!r}"
                    )
                    if self.strict_deletions:
                        raise SpecializationError(f"{item.location}: {message}")
                    self.diagnostic("warning", "unmatched-deletion", message, item)
                continue
            if identity in result:
                result[identity] = self._merge(result[identity], item)
            else:
                direct = copy.deepcopy(item)
                direct.owner = key
                direct.values["module"] = key[0]
                direct.values["class_term"] = key[1]
                result[identity] = direct

        self._resolving.pop()
        self._resolved[key] = copy.deepcopy(result)
        return result

    def resolve(self) -> None:
        for key in self.classes:
            self.resolve_class(key)

    def _validate_abbreviations(self, emitted: Iterable[ClassDefinition]) -> None:
        modules = {definition.key[0] for definition in emitted}
        used: dict[str, str] = {}
        for module in sorted(modules):
            abbreviation = self.module_abbreviations.get(module, "")
            if not re.fullmatch(r"[A-Z]{2}", abbreviation):
                raise SpecializationError(
                    f"Module {module!r} requires an explicit two-letter abbreviation; "
                    "use --module-abbreviation module=XX"
                )
            folded = abbreviation.casefold()
            if folded in used and used[folded] != module:
                raise SpecializationError(
                    f"Module abbreviation collision: {abbreviation} is assigned to "
                    f"{used[folded]!r} and {module!r}"
                )
            used[folded] = module

    def build_rows(self) -> list[dict[str, str]]:
        emitted = [definition for definition in self.classes.values() if not definition.abstract]
        self._validate_abbreviations(emitted)
        per_module: defaultdict[str, int] = defaultdict(int)
        rows: list[dict[str, str]] = []
        sequence = 0

        for definition in emitted:
            module, term = definition.key
            per_module[module] += 1
            class_number = per_module[module]
            if class_number > 99:
                raise SpecializationError(
                    f"Module {module!r} has more than 99 emitted Classes; XXnn is insufficient"
                )
            class_id = f"{self.module_abbreviations[module]}{class_number:02d}"
            class_row = {name: definition.row.values.get(name, "") for name in FSM_HEADER}
            class_row["module"] = module
            class_row["class_term"] = term
            class_row["property_type"] = "Class"
            class_row["associated_module"] = ""
            class_row["associated_class"] = ""
            class_row["id"] = class_id
            sequence += 1
            class_row["sequence"] = str(sequence)
            rows.append(class_row)

            valid_properties: list[SourceRow] = []
            for item in self._resolved[definition.key].values():
                row = item.values
                if row["multiplicity"] in DELETION_MULTIPLICITIES:
                    continue
                if row["property_type"] in ASSOCIATION_TYPES:
                    target_key = class_key(row["associated_module"], row["associated_class"])
                    target = self.classes[target_key]
                    if target.abstract:
                        self.diagnostic(
                            "warning",
                            "abstract-association-excluded",
                            "Association from a concrete Class to an Abstract Class was excluded",
                            item,
                            source_class={"module": module, "class_term": term},
                            property_term=row["property_term"],
                            target_class={
                                "module": target_key[0],
                                "class_term": target_key[1],
                            },
                        )
                        continue
                valid_properties.append(item)

            width = max(2, len(str(len(valid_properties))))
            for property_number, item in enumerate(valid_properties, start=1):
                output = {name: item.values.get(name, "") for name in FSM_HEADER}
                output["module"] = module
                output["class_term"] = term
                output["id"] = f"{class_id}-{property_number:0{width}d}"
                sequence += 1
                output["sequence"] = str(sequence)
                rows.append(output)

        ids = [row["id"] for row in rows]
        if len(ids) != len(set(ids)):
            raise SpecializationError("Generated BSM identifiers are not unique")
        return rows

    def _write_diagnostics(self) -> None:
        if not self.diagnostics_file:
            return
        payload = {
            "processing_status": (
                "poc-with-errors"
                if any(item["severity"] == "error" for item in self.diagnostics)
                else "poc-with-warnings"
                if self.diagnostics
                else "success"
            ),
            "error_count": sum(item["severity"] == "error" for item in self.diagnostics),
            "warning_count": sum(item["severity"] == "warning" for item in self.diagnostics),
            "items": self.diagnostics,
        }
        self.diagnostics_file.parent.mkdir(parents=True, exist_ok=True)
        self.diagnostics_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def write(self, rows: Sequence[Mapping[str, str]]) -> None:
        self.bsm_file.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{self.bsm_file.name}.",
            suffix=".tmp",
            dir=self.bsm_file.parent,
        )
        os.close(fd)
        temporary = Path(temporary_name)
        try:
            with temporary.open("w", encoding=self.encoding, newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=BSM_HEADER, lineterminator="\n")
                writer.writeheader()
                writer.writerows({name: row.get(name, "") for name in BSM_HEADER} for row in rows)
            os.replace(temporary, self.bsm_file)
        finally:
            if temporary.exists():
                temporary.unlink()

    def specialization(self) -> list[dict[str, str]]:
        self.load()
        self.resolve()
        rows = self.build_rows()
        self.write(rows)
        self._write_diagnostics()
        return rows


def parse_abbreviations(values: Sequence[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SpecializationError(
                f"Invalid module abbreviation {value!r}; expected module=XX"
            )
        module, abbreviation = value.split("=", 1)
        module = module_value(module)
        abbreviation = collapse(abbreviation).upper()
        if not module or not re.fullmatch(r"[A-Z]{2}", abbreviation):
            raise SpecializationError(
                f"Invalid module abbreviation {value!r}; expected module=XX"
            )
        result[module] = abbreviation
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert canonical 14-column FSM CSV files to a 15-column BSM."
    )
    parser.add_argument("fsm_files", nargs="*", help="FSM input CSV file(s).")
    parser.add_argument("bsm_file", nargs="?", help="BSM output CSV.")
    parser.add_argument("--in", dest="input_options", action="append", default=[])
    parser.add_argument("--out", dest="output_option")
    parser.add_argument("-e", "--encoding", default="utf-8-sig")
    parser.add_argument(
        "--module-abbreviation",
        action="append",
        default=[],
        metavar="MODULE=XX",
    )
    parser.add_argument("--diagnostics")
    parser.add_argument("--strict-deletions", action="store_true")
    return parser


def resolve_cli(args: argparse.Namespace) -> tuple[list[str], str]:
    inputs: list[str] = []
    for item in [*args.input_options, *args.fsm_files]:
        inputs.extend(part for part in item.split("+") if part)
    output = args.output_option or args.bsm_file
    if not inputs or not output:
        raise SpecializationError("FSM input(s) and BSM output are required")
    return inputs, output


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        inputs, output = resolve_cli(args)
        processor = Specialization(
            inputs,
            output,
            encoding=args.encoding,
            module_abbreviations=parse_abbreviations(args.module_abbreviation),
            diagnostics_file=args.diagnostics,
            strict_deletions=args.strict_deletions,
        )
        rows = processor.specialization()
    except (OSError, csv.Error, SpecializationError) as exc:
        print(f"specialization.py: error: {exc}", file=sys.stderr)
        return 2
    print(
        f"Wrote {len(rows)} BSM row(s) to {output}; "
        f"diagnostics={len(processor.diagnostics)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

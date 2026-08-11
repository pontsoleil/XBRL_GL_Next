#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: MIT
"""Generate a deterministic minimal XBRL taxonomy from an 18-column bound HMD.

This is a candidate-C proof of concept. It deliberately does not replace the
legacy xBRLGL_TaxonomyGenerator.py.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from xml.sax.saxutils import escape, quoteattr

HEADER = [
    "sequence", "module", "level", "type", "identifier", "name", "datatype",
    "multiplicity", "domain_name", "definition", "label_local",
    "definition_local", "element", "id", "semantic_path", "associated_module",
    "class_term", "xpath",
]
NS_HEADER = ["module", "prefix", "namespace_uri"]
UNIT_HEADER = ["id", "unit_qname"]
CLASS_HEADER = ["module", "class_term"]
QNAME = re.compile(r"^(?P<prefix>[A-Za-z_][A-Za-z0-9._-]*):(?P<local>[A-Za-z_][A-Za-z0-9._-]*)$")
NCNAME_BAD = re.compile(r"[^A-Za-z0-9._-]")
UPPER_ONE = {"1", "0..1", "1..1"}

TYPE_BINDINGS = {
    "Text": "xbrli:stringItemType", "Name": "xbrli:stringItemType",
    "String": "xbrli:stringItemType", "anyURI": "xbrli:anyURIItemType",
    "Identifier": "xbrli:tokenItemType", "Code": "xbrli:tokenItemType",
    "Token": "xbrli:tokenItemType", "Date": "xbrli:dateItemType",
    "Date Time": "xbrli:dateTimeItemType", "Amount": "xbrli:monetaryItemType",
    "Monetary": "xbrli:monetaryItemType", "Indicator": "xbrli:booleanItemType",
    "Boolean": "xbrli:booleanItemType", "Decimal": "xbrli:decimalItemType",
    "Integer": "xbrli:integerItemType", "QName": "xbrli:QNameItemType",
}

class GeneratorError(ValueError):
    pass

@dataclass(frozen=True)
class Namespace:
    module: str
    prefix: str
    uri: str

@dataclass(frozen=True)
class Concept:
    module: str
    prefix: str
    namespace: str
    local: str
    row_type: str
    row_id: str
    name: str
    datatype: str
    xbrl_type: str
    semantic_path: str
    xpath: str
    definition: str
    label_local: str
    unit_qname: str


def read_csv(path: Path, expected: list[str]) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != expected:
                raise GeneratorError(
                    f"{path}: header mismatch; expected {expected!r}, got {reader.fieldnames!r}"
                )
            return [dict(row) for row in reader]
    except (OSError, csv.Error) as exc:
        raise GeneratorError(f"{path}: cannot read CSV: {exc}") from exc


def read_namespaces(path: Path) -> dict[str, Namespace]:
    result: dict[str, Namespace] = {}
    prefixes: set[str] = set()
    uris: set[str] = set()
    for line, row in enumerate(read_csv(path, NS_HEADER), 2):
        module, prefix, uri = row["module"], row["prefix"], row["namespace_uri"]
        if not module or prefix != f"gl-{module}" or not uri:
            raise GeneratorError(f"{path}:{line}: invalid namespace binding {row!r}")
        if module in result or prefix in prefixes or uri in uris:
            raise GeneratorError(f"{path}:{line}: duplicate namespace binding")
        result[module] = Namespace(module, prefix, uri)
        prefixes.add(prefix); uris.add(uri)
    if not result:
        raise GeneratorError("namespace mapping is empty")
    return result


def read_units(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    result: dict[str, str] = {}
    for line, row in enumerate(read_csv(path, UNIT_HEADER), 2):
        if not row["id"] or not QNAME.fullmatch(row["unit_qname"]):
            raise GeneratorError(f"{path}:{line}: invalid unit binding {row!r}")
        if row["id"] in result:
            raise GeneratorError(f"{path}:{line}: duplicate unit binding for {row['id']!r}")
        result[row["id"]] = row["unit_qname"]
    return result


def read_classes(path: Path | None) -> set[tuple[str, str]]:
    if path is None:
        return set()
    return {(row["module"], row["class_term"]) for row in read_csv(path, CLASS_HEADER)}


def xml_id(value: str) -> str:
    value = NCNAME_BAD.sub("_", value or "concept")
    if not re.match(r"^[A-Za-z_]", value):
        value = "c_" + value
    return value


def validate_and_collect(
    rows: list[dict[str, str]], namespaces: dict[str, Namespace],
    units: dict[str, str], classes: set[tuple[str, str]],
) -> list[Concept]:
    if not rows:
        raise GeneratorError("bound HMD is empty")
    paths: set[str] = set()
    concepts: OrderedDict[tuple[str, str], Concept] = OrderedDict()
    for line, row in enumerate(rows, 2):
        row_type = row["type"]
        if row_type not in {"C", "A", "R"}:
            raise GeneratorError(f"line {line}: unsupported row type {row_type!r}")
        if not row["semantic_path"] or row["semantic_path"] in paths:
            raise GeneratorError(f"line {line}: missing or duplicate semantic_path")
        paths.add(row["semantic_path"])
        module = row["module"]
        if module not in namespaces:
            raise GeneratorError(f"line {line}: unknown module {module!r}")
        ns = namespaces[module]
        if row_type == "R" and classes and (module, row["class_term"]) not in classes:
            raise GeneratorError(
                f"line {line}: undefined associated Class {(module, row['class_term'])!r}"
            )
        needs_element = row_type in {"C", "A"} or (
            row_type == "R" and row["multiplicity"] not in UPPER_ONE
        )
        if not needs_element:
            if row["element"] or row["xpath"]:
                raise GeneratorError(f"line {line}: upper-one R must not have element or xpath")
            continue
        match = QNAME.fullmatch(row["element"])
        if not match:
            raise GeneratorError(f"line {line}: invalid or missing element QName {row['element']!r}")
        if match.group("prefix") != ns.prefix:
            raise GeneratorError(
                f"line {line}: QName prefix {match.group('prefix')!r} does not match module {module!r}"
            )
        if not row["xpath"].startswith("/xbrli:xbrl/") or not row["xpath"].endswith("/" + row["element"]):
            raise GeneratorError(f"line {line}: xpath does not locate the row QName")
        datatype = row["datatype"]
        if row_type == "C" and not datatype:
            xbrl_type = "xbrli:stringItemType"
        else:
            if datatype not in TYPE_BINDINGS:
                raise GeneratorError(f"line {line}: unknown or blank datatype {datatype!r}")
            xbrl_type = TYPE_BINDINGS[datatype]
        unit = units.get(row["id"], "")
        if xbrl_type == "xbrli:monetaryItemType" and not unit:
            raise GeneratorError(f"line {line}: monetary item {row['id']!r} requires an explicit unit")
        concept = Concept(
            module, ns.prefix, ns.uri, match.group("local"), row_type, row["id"],
            row["name"], datatype, xbrl_type, row["semantic_path"], row["xpath"],
            row["definition"], row["label_local"], unit,
        )
        key = (module, concept.local)
        previous = concepts.get(key)
        if previous and (previous.row_id != concept.row_id or previous.row_type != concept.row_type):
            raise GeneratorError(
                f"element collision for {ns.prefix}:{concept.local}: "
                f"{previous.row_id!r} versus {concept.row_id!r}"
            )
        concepts.setdefault(key, concept)
    if not concepts:
        raise GeneratorError("bound HMD contains no physical concepts")
    return list(concepts.values())


def sample_value(concept: Concept) -> str:
    return {
        "xbrli:dateItemType": "2026-07-30", "xbrli:dateTimeItemType": "2026-07-30T00:00:00",
        "xbrli:monetaryItemType": "100.00", "xbrli:booleanItemType": "true",
        "xbrli:decimalItemType": "1.0", "xbrli:integerItemType": "1",
        "xbrli:anyURIItemType": "https://example.invalid/", "xbrli:QNameItemType": "xbrli:item",
    }.get(concept.xbrl_type, "sample")


def schema_text(ns: Namespace, concepts: list[Concept], base: str) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:{ns.prefix}={quoteattr(ns.uri)} targetNamespace={quoteattr(ns.uri)} elementFormDefault="qualified">',
        '  <xs:annotation><xs:appinfo>',
        '    <link:linkbaseRef xlink:type="simple" xlink:href="candidate-c-minimal-label.xml" xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>',
        '    <link:linkbaseRef xlink:type="simple" xlink:href="candidate-c-minimal-presentation.xml" xlink:role="http://www.xbrl.org/2003/role/presentationLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>',
        '  </xs:appinfo></xs:annotation>',
        '  <xs:import namespace="http://www.xbrl.org/2003/instance" schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>',
    ]
    for c in concepts:
        abstract = ' abstract="true"' if c.row_type == "C" else ""
        lines.append(
            f'  <xs:element id={quoteattr(xml_id(c.row_id))} name={quoteattr(c.local)} type={quoteattr(c.xbrl_type)} substitutionGroup="xbrli:item" xbrli:periodType="instant" nillable="true"{abstract}/>'
        )
    lines.append('</xs:schema>')
    return "\n".join(lines) + "\n"


def label_text(ns: Namespace, concepts: list[Concept]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xml="http://www.w3.org/XML/1998/namespace">',
        '  <link:labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">',
    ]
    for index, c in enumerate(concepts, 1):
        locator = f"loc{index}"; label = f"lab{index}"
        lines += [
            f'    <link:loc xlink:type="locator" xlink:href={quoteattr("candidate-c-minimal.xsd#" + xml_id(c.row_id))} xlink:label={quoteattr(locator)}/>',
            f'    <link:label xlink:type="resource" xlink:label={quoteattr(label)} xlink:role="http://www.xbrl.org/2003/role/label" xml:lang="en">{escape(c.name)}</link:label>',
            f'    <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from={quoteattr(locator)} xlink:to={quoteattr(label)}/>',
        ]
    lines += ['  </link:labelLink>', '</link:linkbase>']
    return "\n".join(lines) + "\n"


def presentation_text(concepts: list[Concept]) -> str:
    root = next((c for c in concepts if c.row_type == "C"), concepts[0])
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink">',
        '  <link:presentationLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">',
    ]
    for index, c in enumerate(concepts, 1):
        lines.append(f'    <link:loc xlink:type="locator" xlink:href={quoteattr("candidate-c-minimal.xsd#" + xml_id(c.row_id))} xlink:label={quoteattr("loc" + str(index))}/>')
    root_index = concepts.index(root) + 1
    order = 1
    for index, c in enumerate(concepts, 1):
        if c is root:
            continue
        lines.append(f'    <link:presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from={quoteattr("loc" + str(root_index))} xlink:to={quoteattr("loc" + str(index))} order={quoteattr(str(order))}/>')
        order += 1
    lines += ['  </link:presentationLink>', '</link:linkbase>']
    return "\n".join(lines) + "\n"


def instance_text(ns: Namespace, concepts: list[Concept]) -> str:
    unit_prefixes = OrderedDict()
    for c in concepts:
        if c.unit_qname:
            prefix = c.unit_qname.split(':', 1)[0]
            if prefix == 'iso4217':
                unit_prefixes[prefix] = 'http://www.xbrl.org/2003/iso4217'
            else:
                raise GeneratorError(f"unsupported unit namespace prefix {prefix!r}")
    attrs = [
        'xmlns:xbrli="http://www.xbrl.org/2003/instance"',
        f'xmlns:{ns.prefix}={quoteattr(ns.uri)}',
        'xmlns:iso4217="http://www.xbrl.org/2003/iso4217"',
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        'xmlns:link="http://www.xbrl.org/2003/linkbase"',
        'xmlns:xlink="http://www.w3.org/1999/xlink"',
        f'xsi:schemaLocation={quoteattr(ns.uri + " candidate-c-minimal.xsd")}',
    ]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<xbrli:xbrl ' + ' '.join(attrs) + '>']
    lines += [
        '  <link:schemaRef xlink:type="simple" xlink:href="candidate-c-minimal.xsd"/>',
        '  <xbrli:context id="c1"><xbrli:entity><xbrli:identifier scheme="https://example.invalid/entity">sample</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:instant>2026-07-30</xbrli:instant></xbrli:period></xbrli:context>',
    ]
    seen_units: OrderedDict[str, str] = OrderedDict()
    for c in concepts:
        if c.unit_qname and c.unit_qname not in seen_units:
            uid = f"u{len(seen_units) + 1}"; seen_units[c.unit_qname] = uid
            lines.append(f'  <xbrli:unit id={quoteattr(uid)}><xbrli:measure>{escape(c.unit_qname)}</xbrli:measure></xbrli:unit>')
    for c in concepts:
        if c.row_type == "C":
            continue
        extra = ''
        if c.xbrl_type == 'xbrli:monetaryItemType':
            extra = f' unitRef={quoteattr(seen_units[c.unit_qname])} decimals="2"'
        elif c.xbrl_type in {'xbrli:decimalItemType', 'xbrli:integerItemType'}:
            extra = ' decimals="0"'
        lines.append(f'  <{c.prefix}:{c.local} contextRef="c1"{extra}>{escape(sample_value(c))}</{c.prefix}:{c.local}>')
    lines.append('</xbrli:xbrl>')
    return "\n".join(lines) + "\n"


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")
    ET.parse(path)


def generate(input_file: Path, output_dir: Path, namespaces_file: Path,
             units_file: Path | None = None, classes_file: Path | None = None) -> int:
    if output_dir.exists():
        raise GeneratorError(f"output directory already exists: {output_dir}")
    rows = read_csv(input_file, HEADER)
    namespaces = read_namespaces(namespaces_file)
    units = read_units(units_file)
    classes = read_classes(classes_file)
    concepts = validate_and_collect(rows, namespaces, units, classes)
    modules = {c.module for c in concepts}
    if len(modules) != 1:
        raise GeneratorError(f"minimal prototype requires one module, got {sorted(modules)!r}")
    ns = namespaces[next(iter(modules))]
    parent = output_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=output_dir.name + ".tmp-", dir=parent))
    try:
        write_text(temporary / "candidate-c-minimal.xsd", schema_text(ns, concepts, ""))
        write_text(temporary / "candidate-c-minimal-label.xml", label_text(ns, concepts))
        write_text(temporary / "candidate-c-minimal-presentation.xml", presentation_text(concepts))
        write_text(temporary / "candidate-c-minimal-instance.xbrl", instance_text(ns, concepts))
        with (temporary / "concepts.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["module", "id", "name", "datatype", "xbrl_type", "element", "semantic_path", "xpath", "unit_qname"])
            for c in concepts:
                writer.writerow([c.module, c.row_id, c.name, c.datatype, c.xbrl_type, f"{c.prefix}:{c.local}", c.semantic_path, c.xpath, c.unit_qname])
        os.replace(temporary, output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return len(concepts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate candidate-C minimal taxonomy from exact 18-column bound HMD")
    parser.add_argument("input_hmd", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--namespaces", type=Path, required=True)
    parser.add_argument("--units", type=Path)
    parser.add_argument("--classes", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        count = generate(args.input_hmd, args.output_dir, args.namespaces, args.units, args.classes)
    except GeneratorError as exc:
        print(f"generate_minimal_taxonomy.py: error: {exc}", file=sys.stderr)
        return 2
    except (OSError, ET.ParseError) as exc:
        print(f"generate_minimal_taxonomy.py: error: {exc}", file=sys.stderr)
        return 2
    print(f"Generated {count} concept(s) in {args.output_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
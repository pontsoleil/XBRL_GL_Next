#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: MIT
"""Generate an isolated Tuple or dimensional OIM DTS from 17-column HMD."""

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
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape, quoteattr


HEADER = [
    "sequence", "module", "level", "type", "identifier", "name", "datatype",
    "multiplicity", "domain_name", "definition", "label_local",
    "definition_local", "element", "id", "semantic_path", "class_term",
    "xpath",
]
ROW_TYPES = {"C", "A", "R"}
UPPER_ONE = {"1", "0..1", "1..1"}
MULTIPLICITIES = {"0..1", "0..*", "1", "1..1", "1..*"}
NCNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")
DATATYPES = {
    "Token": "xbrli:tokenItemType",
    "String": "xbrli:stringItemType",
    "QName": "xbrli:QNameItemType",
    "Date Time": "xbrli:dateTimeItemType",
    "Decimal": "xbrli:decimalItemType",
    "Boolean": "xbrli:booleanItemType",
    "anyURI": "xbrli:anyURIItemType",
    "Date": "xbrli:dateItemType",
    "Integer": "xbrli:integerItemType",
    "Monetary": "xbrli:monetaryItemType",
    "Pure": "xbrli:pureItemType",
}
VERSION = "2026-07-31"


class RevisedHmdTaxonomyError(ValueError):
    """The requested DTS cannot be generated deterministically."""


@dataclass(frozen=True)
class Concept:
    module: str
    element: str
    row_type: str
    identifier: str
    name: str
    datatype: str
    definition: str
    label_local: str
    definition_local: str

    @property
    def key(self) -> tuple[str, str]:
        return self.module, self.element

    @property
    def xml_id(self) -> str:
        return f"gl-{self.module}_{self.element}"

    @property
    def prefix(self) -> str:
        return f"gl-{self.module}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def qname_parts(value: str, module: str) -> tuple[str, str]:
    expected_prefix = f"gl-{module}"
    parts = value.split(":")
    if len(parts) != 2 or parts[0] != expected_prefix:
        raise RevisedHmdTaxonomyError(
            f"element must be a registered QName for module {module!r}: {value!r}"
        )
    if not NCNAME.fullmatch(parts[0]) or not NCNAME.fullmatch(parts[1]):
        raise RevisedHmdTaxonomyError(f"element is not a valid QName: {value!r}")
    return parts[0], parts[1]


def read_hmd(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise RevisedHmdTaxonomyError(f"HMD does not exist: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if (reader.fieldnames or []) != HEADER:
            raise RevisedHmdTaxonomyError(
                f"{path}: expected exact 17-column header {HEADER!r}, "
                f"got {reader.fieldnames!r}"
            )
        rows = []
        semantic_paths: set[str] = set()
        for line, raw in enumerate(reader, 2):
            if not any(value not in (None, "") for value in raw.values()):
                continue
            row = {name: clean(raw.get(name)) for name in HEADER}
            if row["type"] not in ROW_TYPES:
                raise RevisedHmdTaxonomyError(
                    f"{path}:{line}: unsupported type {row['type']!r}"
                )
            if row["multiplicity"] not in MULTIPLICITIES:
                raise RevisedHmdTaxonomyError(
                    f"{path}:{line}: unsupported multiplicity "
                    f"{row['multiplicity']!r}"
                )
            for field in (
                "sequence", "module", "level", "name", "id", "semantic_path",
                "class_term", "element", "xpath",
            ):
                if not row[field]:
                    raise RevisedHmdTaxonomyError(
                        f"{path}:{line}: {field} is required"
                    )
            try:
                level = int(row["level"])
            except ValueError as exc:
                raise RevisedHmdTaxonomyError(
                    f"{path}:{line}: level must be an integer"
                ) from exc
            if level < 1:
                raise RevisedHmdTaxonomyError(
                    f"{path}:{line}: level must be positive"
                )
            if row["semantic_path"] in semantic_paths:
                raise RevisedHmdTaxonomyError(
                    f"{path}:{line}: duplicate semantic_path "
                    f"{row['semantic_path']!r}"
                )
            semantic_paths.add(row["semantic_path"])
            qname_parts(row["element"], row["module"])
            expected_xpath_suffix = "/" + row["element"]
            if not row["xpath"].startswith("/xbrli:xbrl/") or not row[
                "xpath"
            ].endswith(expected_xpath_suffix):
                raise RevisedHmdTaxonomyError(
                    f"{path}:{line}: xpath is inconsistent with element QName"
                )
            if row["type"] == "A" and row["datatype"] not in DATATYPES:
                raise RevisedHmdTaxonomyError(
                    f"{path}:{line}: unknown or blank datatype "
                    f"{row['datatype']!r}"
                )
            rows.append(row)
    if not rows:
        raise RevisedHmdTaxonomyError(f"{path}: no HMD rows")
    return rows


def included(row: Mapping[str, str], kind: str) -> bool:
    if not row["element"]:
        return False
    if kind == "oim" and row["type"] in {"C", "R"}:
        return row["multiplicity"] not in UPPER_ONE or int(row["level"]) == 1
    return True


def hierarchy(
    rows: Sequence[dict[str, str]], kind: str
) -> tuple[list[tuple[tuple[str, str], tuple[str, str]]], dict[int, tuple[str, str] | None]]:
    stack: list[tuple[int, tuple[str, str] | None, str]] = []
    edges: list[tuple[tuple[str, str], tuple[str, str]]] = []
    effective_parent: dict[int, tuple[str, str] | None] = {}
    seen_edges: set[tuple[tuple[str, str], tuple[str, str]]] = set()
    for index, row in enumerate(rows):
        level = int(row["level"])
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else None
        effective_parent[index] = parent
        current = (
            (row["module"], qname_parts(row["element"], row["module"])[1])
            if included(row, kind) else None
        )
        if current and parent and current != parent:
            edge = parent, current
            if edge not in seen_edges:
                seen_edges.add(edge)
                edges.append(edge)
        child_parent = current or parent
        if row["type"] in {"C", "R"}:
            stack.append((level, child_parent, row["type"]))
    return edges, effective_parent


def collect_concepts(
    rows: Sequence[dict[str, str]], kind: str
) -> dict[tuple[str, str], Concept]:
    concepts: dict[tuple[str, str], Concept] = {}
    identities: dict[tuple[str, str], tuple[str, str]] = {}
    for row in rows:
        if not included(row, kind):
            continue
        _, local_name = qname_parts(row["element"], row["module"])
        key = row["module"], local_name
        identity = row["id"], row["type"]
        if key in identities and identities[key] != identity:
            raise RevisedHmdTaxonomyError(
                f"element collision {key!r}: {identities[key]!r} and "
                f"{identity!r}"
            )
        identities[key] = identity
        concepts.setdefault(
            key,
            Concept(
                module=row["module"],
                element=local_name,
                row_type=row["type"],
                identifier=row["id"],
                name=row["name"],
                datatype=row["datatype"],
                definition=row["definition"],
                label_local=row["label_local"],
                definition_local=row["definition_local"],
            ),
        )
    return concepts


def module_namespace(module: str) -> str:
    return f"urn:xbrl-gl-next:{module}:{VERSION}"


def dim_namespace(taxonomy_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", taxonomy_name.lower()).strip("-")
    return f"urn:xbrl-gl-next:{slug}:dimensions:{VERSION}"


def xml_header() -> str:
    return '<?xml version="1.0" encoding="UTF-8"?>\n'


def module_schema(module: str, concepts: Iterable[Concept]) -> str:
    lines = [
        xml_header().rstrip(),
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"',
        '  xmlns:xbrli="http://www.xbrl.org/2003/instance"',
        f'  xmlns:gl-{module}={quoteattr(module_namespace(module))}',
        f'  targetNamespace={quoteattr(module_namespace(module))}',
        '  elementFormDefault="qualified" attributeFormDefault="unqualified">',
        '  <xs:import namespace="http://www.xbrl.org/2003/instance"',
        '    schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>',
    ]
    for concept in sorted(concepts, key=lambda item: item.element):
        item_type = (
            DATATYPES[concept.datatype]
            if concept.row_type == "A"
            else "xbrli:stringItemType"
        )
        abstract = "false" if concept.row_type == "A" else "true"
        lines.append(
            f'  <xs:element name={quoteattr(concept.element)} '
            f'id={quoteattr(concept.xml_id)} type={quoteattr(item_type)} '
            f'substitutionGroup="xbrli:item" nillable="true" '
            f'abstract="{abstract}" xbrli:periodType="instant"/>'
        )
    lines.append("</xs:schema>")
    return "\n".join(lines) + "\n"


def dimensions_schema(taxonomy_name: str, containers: Sequence[Concept]) -> str:
    namespace = dim_namespace(taxonomy_name)
    lines = [
        xml_header().rstrip(),
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"',
        '  xmlns:xbrli="http://www.xbrl.org/2003/instance"',
        '  xmlns:xbrldt="http://xbrl.org/2005/xbrldt"',
        f'  xmlns:dim={quoteattr(namespace)}',
        f'  targetNamespace={quoteattr(namespace)}',
        '  elementFormDefault="qualified" attributeFormDefault="unqualified">',
        '  <xs:import namespace="http://www.xbrl.org/2003/instance"',
        '    schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>',
        '  <xs:import namespace="http://xbrl.org/2005/xbrldt"',
        '    schemaLocation="http://www.xbrl.org/2005/xbrldt-2005.xsd"/>',
    ]
    for container in containers:
        token = f"{container.module}_{container.element}"
        lines.extend([
            f'  <xs:element name="h_{token}" id="dim_h_{token}" '
            'type="xbrli:stringItemType" substitutionGroup="xbrldt:hypercubeItem" '
            'nillable="true" abstract="true" xbrli:periodType="instant"/>',
            f'  <xs:element name="d_{token}" id="dim_d_{token}" '
            'type="xbrli:stringItemType" substitutionGroup="xbrldt:dimensionItem" '
            'nillable="true" abstract="true" xbrli:periodType="instant"/>',
            f'  <xs:element name="dom_{token}" id="dim_dom_{token}" '
            'type="xbrli:stringItemType" substitutionGroup="xbrli:item" '
            'nillable="true" abstract="true" xbrli:periodType="instant"/>',
            f'  <xs:element name="m_{token}" id="dim_m_{token}" '
            'type="xbrli:stringItemType" substitutionGroup="xbrli:item" '
            'nillable="true" abstract="false" xbrli:periodType="instant"/>',
        ])
    lines.append("</xs:schema>")
    return "\n".join(lines) + "\n"


def entry_schema(
    modules: Sequence[str], kind: str, taxonomy_name: str
) -> str:
    namespace_lines = [
        f'  xmlns:gl-{module}={quoteattr(module_namespace(module))}'
        for module in modules
    ]
    if kind == "oim":
        namespace_lines.append(f'  xmlns:dim={quoteattr(dim_namespace(taxonomy_name))}')
    lines = [
        xml_header().rstrip(),
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"',
        '  xmlns:link="http://www.xbrl.org/2003/linkbase"',
        '  xmlns:xlink="http://www.w3.org/1999/xlink"',
        '  xmlns:xbrli="http://www.xbrl.org/2003/instance"',
        *namespace_lines,
        '  elementFormDefault="qualified" attributeFormDefault="unqualified">',
        '  <xs:import namespace="http://www.xbrl.org/2003/instance"',
        '    schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>',
    ]
    for module in modules:
        lines.append(
            f'  <xs:import namespace={quoteattr(module_namespace(module))} '
            f'schemaLocation={quoteattr(module + ".xsd")}/>'
        )
    if kind == "oim":
        lines.append(
            f'  <xs:import namespace={quoteattr(dim_namespace(taxonomy_name))} '
            'schemaLocation="dimensions.xsd"/>'
        )
    lines.extend([
        "  <xs:annotation><xs:appinfo>",
        '    <link:linkbaseRef xlink:type="simple" '
        'xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase" '
        'xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef" '
        'xlink:href="../linkbases/labels.xml"/>',
        '    <link:linkbaseRef xlink:type="simple" '
        'xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase" '
        'xlink:role="http://www.xbrl.org/2003/role/presentationLinkbaseRef" '
        'xlink:href="../linkbases/presentation.xml"/>',
        '    <link:linkbaseRef xlink:type="simple" '
        'xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase" '
        'xlink:role="http://www.xbrl.org/2003/role/definitionLinkbaseRef" '
        'xlink:href="../linkbases/definition.xml"/>',
        "  </xs:appinfo></xs:annotation>",
        "</xs:schema>",
    ])
    return "\n".join(lines) + "\n"


def concept_href(concept: Concept) -> str:
    return f"../schema/{concept.module}.xsd#{concept.xml_id}"


def labels_linkbase(concepts: Sequence[Concept]) -> str:
    lines = [
        xml_header().rstrip(),
        '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">',
        '  <link:labelLink xlink:type="extended" '
        'xlink:role="http://www.xbrl.org/2003/role/link">',
    ]
    for index, concept in enumerate(concepts, 1):
        loc = f"loc_{index}"
        lab_en = f"lab_en_{index}"
        lab_ja = f"lab_ja_{index}"
        lines.extend([
            f'    <link:loc xlink:type="locator" '
            f'xlink:href={quoteattr(concept_href(concept))} '
            f'xlink:label={quoteattr(loc)}/>',
            f'    <link:label xlink:type="resource" '
            f'xlink:label={quoteattr(lab_en)} '
            'xlink:role="http://www.xbrl.org/2003/role/label" '
            f'xml:lang="en">{escape(concept.name)}</link:label>',
            f'    <link:labelArc xlink:type="arc" '
            'xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" '
            f'xlink:from={quoteattr(loc)} xlink:to={quoteattr(lab_en)}/>',
        ])
        if concept.label_local:
            lines.extend([
                f'    <link:label xlink:type="resource" '
                f'xlink:label={quoteattr(lab_ja)} '
                'xlink:role="http://www.xbrl.org/2003/role/label" '
                f'xml:lang="ja">{escape(concept.label_local)}</link:label>',
                f'    <link:labelArc xlink:type="arc" '
                'xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" '
                f'xlink:from={quoteattr(loc)} xlink:to={quoteattr(lab_ja)}/>',
            ])
    lines.extend(["  </link:labelLink>", "</link:linkbase>"])
    return "\n".join(lines) + "\n"


def relationship_linkbase(
    concepts: Mapping[tuple[str, str], Concept],
    edges: Sequence[tuple[tuple[str, str], tuple[str, str]]],
    arc_name: str,
    arcrole: str,
) -> str:
    used = sorted({item for edge in edges for item in edge})
    labels = {key: f"loc_{index}" for index, key in enumerate(used, 1)}
    lines = [
        xml_header().rstrip(),
        '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">',
        f'  <link:{arc_name.replace("Arc", "Link")} xlink:type="extended" '
        'xlink:role="http://www.xbrl.org/2003/role/link">',
    ]
    for key in used:
        lines.append(
            f'    <link:loc xlink:type="locator" '
            f'xlink:href={quoteattr(concept_href(concepts[key]))} '
            f'xlink:label={quoteattr(labels[key])}/>'
        )
    for order, (parent, child) in enumerate(edges, 1):
        lines.append(
            f'    <link:{arc_name} xlink:type="arc" '
            f'xlink:arcrole={quoteattr(arcrole)} '
            f'xlink:from={quoteattr(labels[parent])} '
            f'xlink:to={quoteattr(labels[child])} order={quoteattr(str(order))}/>'
        )
    lines.extend([
        f'  </link:{arc_name.replace("Arc", "Link")}>',
        "</link:linkbase>",
    ])
    return "\n".join(lines) + "\n"


def oim_definition_linkbase(
    taxonomy_name: str,
    concepts: Mapping[tuple[str, str], Concept],
    edges: Sequence[tuple[tuple[str, str], tuple[str, str]]],
    containers: Sequence[Concept],
) -> str:
    dim_file = "../schema/dimensions.xsd"
    used = sorted(set(concepts) | {item for edge in edges for item in edge})
    labels = {key: f"c_{index}" for index, key in enumerate(used, 1)}
    lines = [
        xml_header().rstrip(),
        '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xmlns:xbrldt="http://xbrl.org/2005/xbrldt">',
        '  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/all" '
        'xlink:type="simple" '
        'xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#all"/>',
        '  <link:arcroleRef '
        'arcroleURI="http://xbrl.org/int/dim/arcrole/hypercube-dimension" '
        'xlink:type="simple" '
        'xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#hypercube-dimension"/>',
        '  <link:arcroleRef '
        'arcroleURI="http://xbrl.org/int/dim/arcrole/dimension-domain" '
        'xlink:type="simple" '
        'xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#dimension-domain"/>',
        '  <link:arcroleRef '
        'arcroleURI="http://xbrl.org/int/dim/arcrole/domain-member" '
        'xlink:type="simple" '
        'xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#domain-member"/>',
        '  <link:definitionLink xlink:type="extended" '
        'xlink:role="http://www.xbrl.org/2003/role/link">',
    ]
    for key in used:
        lines.append(
            f'    <link:loc xlink:type="locator" '
            f'xlink:href={quoteattr(concept_href(concepts[key]))} '
            f'xlink:label={quoteattr(labels[key])}/>'
        )
    for index, container in enumerate(containers, 1):
        token = f"{container.module}_{container.element}"
        for suffix in ("h", "d", "dom", "m"):
            lines.append(
                f'    <link:loc xlink:type="locator" '
                f'xlink:href={quoteattr(dim_file + "#dim_" + suffix + "_" + token)} '
                f'xlink:label={quoteattr(suffix + "_" + str(index))}/>'
            )
        primary = labels[container.key]
        lines.extend([
            f'    <link:definitionArc xlink:type="arc" '
            'xlink:arcrole="http://xbrl.org/int/dim/arcrole/all" '
            f'xlink:from={quoteattr(primary)} xlink:to={quoteattr("h_" + str(index))} '
            f'order="1" xbrldt:closed="false" xbrldt:contextElement="segment"/>',
            f'    <link:definitionArc xlink:type="arc" '
            'xlink:arcrole="http://xbrl.org/int/dim/arcrole/hypercube-dimension" '
            f'xlink:from={quoteattr("h_" + str(index))} '
            f'xlink:to={quoteattr("d_" + str(index))} order="1"/>',
            f'    <link:definitionArc xlink:type="arc" '
            'xlink:arcrole="http://xbrl.org/int/dim/arcrole/dimension-domain" '
            f'xlink:from={quoteattr("d_" + str(index))} '
            f'xlink:to={quoteattr("dom_" + str(index))} order="1"/>',
            f'    <link:definitionArc xlink:type="arc" '
            'xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" '
            f'xlink:from={quoteattr("dom_" + str(index))} '
            f'xlink:to={quoteattr("m_" + str(index))} order="1"/>',
        ])
    for order, (parent, child) in enumerate(edges, 1):
        lines.append(
            '    <link:definitionArc xlink:type="arc" '
            'xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" '
            f'xlink:from={quoteattr(labels[parent])} '
            f'xlink:to={quoteattr(labels[child])} order={quoteattr(str(order))}/>'
        )
    lines.extend(["  </link:definitionLink>", "</link:linkbase>"])
    return "\n".join(lines) + "\n"


def sample_value(concept: Concept) -> tuple[str, str, str]:
    datatype = concept.datatype
    if datatype == "Boolean":
        return "false", "", ""
    if datatype == "Date":
        return VERSION, "", ""
    if datatype == "Date Time":
        return f"{VERSION}T00:00:00", "", ""
    if datatype == "Integer":
        return "0", ' unitRef="pure" decimals="INF"', ""
    if datatype in {"Decimal", "Pure"}:
        return "0", ' unitRef="pure" decimals="INF"', ""
    if datatype == "Monetary":
        return "0", ' unitRef="JPY" decimals="2"', ""
    if datatype == "QName":
        return f"{concept.prefix}:{concept.element}", "", ""
    if datatype == "anyURI":
        return "urn:example", "", ""
    return "sample", "", ""


def sample_instance(
    concepts: Sequence[Concept],
    modules: Sequence[str],
    kind: str,
    taxonomy_name: str,
    containers: Sequence[Concept],
    container_for_key: Mapping[tuple[str, str], tuple[str, str] | None],
) -> str:
    namespaces = [
        'xmlns:xbrli="http://www.xbrl.org/2003/instance"',
        'xmlns:link="http://www.xbrl.org/2003/linkbase"',
        'xmlns:xlink="http://www.w3.org/1999/xlink"',
        'xmlns:iso4217="http://www.xbrl.org/2003/iso4217"',
        *[
            f'xmlns:gl-{module}={quoteattr(module_namespace(module))}'
            for module in modules
        ],
    ]
    if kind == "oim":
        namespaces.extend([
            'xmlns:xbrldi="http://xbrl.org/2006/xbrldi"',
            f'xmlns:dim={quoteattr(dim_namespace(taxonomy_name))}',
        ])
    lines = [
        xml_header().rstrip(),
        "<xbrli:xbrl " + " ".join(namespaces) + ">",
        '  <link:schemaRef xlink:type="simple" xlink:href="../schema/entry.xsd"/>',
    ]
    selected = [concept for concept in concepts if concept.row_type == "A"][:12]
    container_map = {container.key: container for container in containers}
    for index, concept in enumerate(selected, 1):
        context_id = f"c{index}"
        lines.extend([
            f'  <xbrli:context id="{context_id}">',
            '    <xbrli:entity><xbrli:identifier scheme="urn:example">'
            'entity</xbrli:identifier>',
        ])
        if kind == "oim":
            container_key = container_for_key.get(concept.key)
            if container_key and container_key in container_map:
                container = container_map[container_key]
                token = f"{container.module}_{container.element}"
                lines.extend([
                    "      <xbrli:segment>",
                    f'        <xbrldi:explicitMember '
                    f'dimension={quoteattr("dim:d_" + token)}>'
                    f'dim:m_{token}</xbrldi:explicitMember>',
                    "      </xbrli:segment>",
                ])
        lines.extend([
            "    </xbrli:entity>",
            f"    <xbrli:period><xbrli:instant>{VERSION}</xbrli:instant>"
            "</xbrli:period>",
            "  </xbrli:context>",
        ])
    lines.extend([
        '  <xbrli:unit id="JPY"><xbrli:measure>iso4217:JPY'
        "</xbrli:measure></xbrli:unit>",
        '  <xbrli:unit id="pure"><xbrli:measure>xbrli:pure'
        "</xbrli:measure></xbrli:unit>",
    ])
    for index, concept in enumerate(selected, 1):
        value, attributes, _ = sample_value(concept)
        lines.append(
            f'  <{concept.prefix}:{concept.element} contextRef="c{index}"'
            f"{attributes}>{escape(value)}</{concept.prefix}:{concept.element}>"
        )
    lines.append("</xbrli:xbrl>")
    return "\n".join(lines) + "\n"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")
    if path.suffix.lower() in {".xml", ".xsd", ".xbrl"}:
        ET.parse(path)


def write_trace(
    path: Path,
    rows: Sequence[dict[str, str]],
    kind: str,
    effective_parent: Mapping[int, tuple[str, str] | None],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        fields = [
            *HEADER, "taxonomy_kind", "included", "effective_parent_module",
            "effective_parent_element", "exclusion_reason",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for index, row in enumerate(rows):
            parent = effective_parent.get(index)
            is_included = included(row, kind)
            reason = ""
            if not row["element"]:
                reason = "no physical element"
            elif not is_included:
                reason = "at-most-one C/R flattened for OIM"
            writer.writerow({
                **row,
                "taxonomy_kind": kind,
                "included": "true" if is_included else "false",
                "effective_parent_module": parent[0] if parent else "",
                "effective_parent_element": parent[1] if parent else "",
                "exclusion_reason": reason,
            })


def write_manifest(root: Path) -> None:
    manifest = root / "manifest" / "SHA256SUMS.csv"
    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and path != manifest
    )
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["relative_path", "size", "sha256"])
        for path in files:
            writer.writerow([
                path.relative_to(root).as_posix(),
                path.stat().st_size,
                sha256(path),
            ])


def generate(
    input_hmd: Path,
    output_dir: Path,
    *,
    kind: str,
    taxonomy_name: str,
    source_workbook: str,
    source_sheet: str,
    workbook_sha256: str,
) -> dict[str, int]:
    if kind not in {"tuple", "oim"}:
        raise RevisedHmdTaxonomyError(f"unsupported taxonomy kind: {kind!r}")
    if output_dir.exists():
        raise RevisedHmdTaxonomyError(
            f"output directory already exists: {output_dir}"
        )
    rows = read_hmd(input_hmd)
    concepts = collect_concepts(rows, kind)
    edges, effective_parent = hierarchy(rows, kind)
    modules = sorted({concept.module for concept in concepts.values()})
    if not modules:
        raise RevisedHmdTaxonomyError("no concepts to generate")
    containers = sorted(
        (
            concept for concept in concepts.values()
            if concept.row_type in {"C", "R"}
        ),
        key=lambda item: item.key,
    )
    parent_for_concept: dict[tuple[str, str], tuple[str, str] | None] = {}
    for parent, child in edges:
        parent_for_concept.setdefault(child, parent)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(
        prefix=f"{output_dir.name}.tmp-", dir=output_dir.parent
    ))
    try:
        grouped: dict[str, list[Concept]] = defaultdict(list)
        for concept in concepts.values():
            grouped[concept.module].append(concept)
        for module in modules:
            write_text(
                temporary / "schema" / f"{module}.xsd",
                module_schema(module, grouped[module]),
            )
        if kind == "oim":
            write_text(
                temporary / "schema" / "dimensions.xsd",
                dimensions_schema(taxonomy_name, containers),
            )
        write_text(
            temporary / "schema" / "entry.xsd",
            entry_schema(modules, kind, taxonomy_name),
        )
        ordered_concepts = sorted(concepts.values(), key=lambda item: item.key)
        write_text(
            temporary / "linkbases" / "labels.xml",
            labels_linkbase(ordered_concepts),
        )
        write_text(
            temporary / "linkbases" / "presentation.xml",
            relationship_linkbase(
                concepts,
                edges,
                "presentationArc",
                "http://www.xbrl.org/2003/arcrole/parent-child",
            ),
        )
        if kind == "oim":
            definition = oim_definition_linkbase(
                taxonomy_name, concepts, edges, containers
            )
        else:
            definition = relationship_linkbase(
                concepts,
                edges,
                "definitionArc",
                "http://xbrl.org/int/dim/arcrole/domain-member",
            )
        write_text(temporary / "linkbases" / "definition.xml", definition)
        write_text(
            temporary / "instances" / "sample.xbrl",
            sample_instance(
                ordered_concepts, modules, kind, taxonomy_name, containers,
                parent_for_concept,
            ),
        )
        write_trace(
            temporary / "trace" / "hmd-trace.csv",
            rows,
            kind,
            effective_parent,
        )
        generator_sha = sha256(Path(__file__))
        metadata = {
            "taxonomy_name": taxonomy_name,
            "taxonomy_kind": kind,
            "source_workbook": source_workbook,
            "source_sheet": source_sheet,
            "source_workbook_sha256": workbook_sha256,
            "input_hmd_sha256": sha256(input_hmd),
            "entry_point": "schema/entry.xsd",
            "generator": "tools/taxonomy/generate_revised_hmd_taxonomy.py",
            "generator_sha256": generator_sha,
            "status": "for-review",
            "license_status": "license-hold",
            "rows": len(rows),
            "concepts": len(concepts),
            "relationships": len(edges),
            "containers": len(containers),
        }
        write_text(
            temporary / "logs" / "generation.json",
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
        )
        readme = "\n".join([
            f"# {taxonomy_name}",
            "",
            f"- taxonomy_name: `{taxonomy_name}`",
            f"- taxonomy_kind: `{kind}`",
            f"- source_workbook: `{source_workbook}`",
            f"- source_sheet: `{source_sheet}`",
            f"- source_workbook_sha256: `{workbook_sha256}`",
            "- entry_point: `schema/entry.xsd`",
            "- generator: `tools/taxonomy/generate_revised_hmd_taxonomy.py`",
            f"- generator_sha256: `{generator_sha}`",
            "- status: `for-review`",
            "- license_status: `license-hold`",
            "",
            "`manifest/SHA256SUMS.csv` covers every generated payload file "
            "except the manifest itself.",
            "",
        ])
        write_text(temporary / "README.md", readme)
        write_manifest(temporary)
        os.replace(temporary, output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {
        "rows": len(rows),
        "concepts": len(concepts),
        "relationships": len(edges),
        "containers": len(containers),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an isolated Tuple or OIM DTS from taxonomy HMD"
    )
    parser.add_argument("input_hmd", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--kind", choices=("tuple", "oim"), required=True)
    parser.add_argument("--taxonomy-name", required=True)
    parser.add_argument("--source-workbook", required=True)
    parser.add_argument("--source-sheet", required=True)
    parser.add_argument("--workbook-sha256", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        counts = generate(
            args.input_hmd,
            args.output_dir,
            kind=args.kind,
            taxonomy_name=args.taxonomy_name,
            source_workbook=args.source_workbook,
            source_sheet=args.source_sheet,
            workbook_sha256=args.workbook_sha256,
        )
    except (OSError, csv.Error, ET.ParseError, RevisedHmdTaxonomyError) as exc:
        print(f"generate_revised_hmd_taxonomy.py: error: {exc}", file=sys.stderr)
        return 2
    print(
        f"Generated {args.kind} taxonomy in {args.output_dir}: "
        + ", ".join(f"{name}={value}" for name, value in counts.items())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

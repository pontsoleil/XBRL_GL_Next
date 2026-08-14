#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Static conformance checks for the accepted XBRL GL Next package.

2026-08-12 binding-specific module presentation contract:

Tuple module components:
  <module>-<V>.xsd
  <module>-pre-<V>.xml
  labels

OIM module components:
  <module>-oim-<V>.xsd
  <module>-oim-pre-<V>.xml
  OIM-specific labels

Tuple C/R declarations and their presentation locators never enter an OIM DTS.
OIM Class presentation uses module-level p_<module>_* xbrli:item anchors.
R occurrences are transparent in OIM presentation.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

XSD = "http://www.w3.org/2001/XMLSchema"
XLINK = "http://www.w3.org/1999/xlink"
LINK = "http://www.xbrl.org/2003/linkbase"
XBRLI = "http://www.xbrl.org/2003/instance"

XLINK_HREF = f"{{{XLINK}}}href"
XLINK_ROLE = f"{{{XLINK}}}role"
XLINK_LABEL = f"{{{XLINK}}}label"
XLINK_FROM = f"{{{XLINK}}}from"
XLINK_TO = f"{{{XLINK}}}to"
XLINK_ARCROLE = f"{{{XLINK}}}arcrole"

PRESENTATION_REF_ROLE = "http://www.xbrl.org/2003/role/presentationLinkbaseRef"

VERSION_DEFAULT = "2026-12-31"
MODULES = ("btx", "bus", "cor", "ehm", "lnk", "muc", "taf")
HMD_PREFIXES = {
    "cor_accountingEntries": "cor",
    "btx_businessTransactions": "btx",
}
HMD_MODULES = {
    "cor_accountingEntries": ("bus", "cor", "ehm", "lnk", "muc", "taf"),
    "btx_businessTransactions": (
        "btx", "bus", "cor", "ehm", "lnk", "muc", "taf",
    ),
}
# One generic schema, eight binding-specific artefacts per module, and for each
# HMD one Tuple entry point, one Tuple content schema per used module, one OIM
# entry point, and one dimensional linkbase.
EXPECTED_FILE_COUNT = (
    1
    + 8 * len(MODULES)
    + sum(len(modules) + 3 for modules in HMD_MODULES.values())
)
RESERVED_TOP_LEVEL = {"gen", "tuple", "oim"}


def lname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def is_remote(ref: str) -> bool:
    return bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", ref))


def parse_xml(path: Path, failures: list[str]):
    try:
        return ET.parse(path)
    except Exception as exc:
        failures.append(f"invalid XML {path}: {exc}")
        return None


def split_ref(source: Path, ref: str):
    if "#" in ref:
        path_part, fragment = ref.split("#", 1)
    else:
        path_part, fragment = ref, ""
    target = source if not path_part else (source.parent / path_part).resolve()
    return target, fragment


def ids_in(path: Path, failures: list[str]) -> dict[str, ET.Element]:
    tree = parse_xml(path, failures)
    if tree is None:
        return {}
    return {
        node.attrib["id"]: node
        for node in tree.iter()
        if node.attrib.get("id")
    }


def global_elements(path: Path, failures: list[str]) -> dict[str, ET.Element]:
    tree = parse_xml(path, failures)
    if tree is None:
        return {}
    root = tree.getroot()
    return {
        node.attrib["id"]: node
        for node in root.findall(f"./{{{XSD}}}element")
        if node.attrib.get("id")
    }


def presentation_stats(path: Path, failures: list[str]):
    tree = parse_xml(path, failures)
    if tree is None:
        return {
            "locators": 0,
            "arcs": 0,
            "duplicate_locators": 0,
            "duplicate_arcs": 0,
        }

    locator_keys = []
    arc_keys = []
    for link in [
        node for node in tree.iter() if lname(node.tag) == "presentationLink"
    ]:
        for node in link:
            if lname(node.tag) == "loc":
                locator_keys.append(
                    (node.attrib.get(XLINK_LABEL, ""), node.attrib.get(XLINK_HREF, ""))
                )
            elif lname(node.tag) == "presentationArc":
                arc_keys.append(
                    (
                        node.attrib.get(XLINK_ARCROLE, ""),
                        node.attrib.get(XLINK_FROM, ""),
                        node.attrib.get(XLINK_TO, ""),
                        node.attrib.get("use", ""),
                        node.attrib.get("priority", ""),
                        node.attrib.get("order", ""),
                        node.attrib.get("preferredLabel", ""),
                    )
                )
    return {
        "locators": len(locator_keys),
        "arcs": len(arc_keys),
        "duplicate_locators": sum(v > 1 for v in Counter(locator_keys).values()),
        "duplicate_arcs": sum(v > 1 for v in Counter(arc_keys).values()),
    }


def schema_import_targets(path: Path, failures: list[str]) -> list[str]:
    tree = parse_xml(path, failures)
    if tree is None:
        return []
    return [
        node.attrib.get("schemaLocation", "")
        for node in tree.iter(f"{{{XSD}}}import")
        if node.attrib.get("schemaLocation")
    ]


def presentation_refs(path: Path, failures: list[str]) -> list[str]:
    tree = parse_xml(path, failures)
    if tree is None:
        return []
    return [
        node.attrib.get(XLINK_HREF, "")
        for node in tree.iter()
        if lname(node.tag) == "linkbaseRef"
        and node.attrib.get(XLINK_ROLE) == PRESENTATION_REF_ROLE
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_root", type=Path)
    parser.add_argument("--version", default=VERSION_DEFAULT)
    args = parser.parse_args()

    root = args.package_root.resolve()
    version = args.version
    failures: list[str] = []

    if not root.is_dir():
        print(f"ERROR: package root not found: {root}")
        return 1

    all_files = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".xsd", ".xml"}
    )
    if len(all_files) != EXPECTED_FILE_COUNT:
        failures.append(
            f"formal package file count must be {EXPECTED_FILE_COUNT}; "
            f"got {len(all_files)}"
        )

    for obsolete in (root / "all", root / "presentation"):
        if obsolete.exists():
            failures.append(f"obsolete top-level directory exists: {obsolete.name}")

    obsolete_pre = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob(f"*-all-pre-{version}.xml")
    )
    if obsolete_pre:
        failures.append(f"obsolete HMD-specific presentation remains: {obsolete_pre}")

    # Required module-level Tuple and OIM palette components.
    for module in MODULES:
        expected = (
            root / module / f"{module}-{version}.xsd",
            root / module / f"{module}-pre-{version}.xml",
            root / module / f"{module}-oim-{version}.xsd",
            root / module / f"{module}-oim-pre-{version}.xml",
            root / module / "label" / f"{module}-lab-en-{version}.xml",
            root / module / "label" / f"{module}-lab-ja-{version}.xml",
            root / module / "label" / f"{module}-oim-lab-en-{version}.xml",
            root / module / "label" / f"{module}-oim-lab-ja-{version}.xml",
        )
        for path in expected:
            if not path.is_file():
                failures.append(f"missing required module artefact: {path.relative_to(root)}")

    # Current formal HMD outputs.
    entries = {}
    for hmd, prefix in HMD_PREFIXES.items():
        tuple_entry = root / "tuple" / hmd / f"{prefix}-all-{version}.xsd"
        oim_entry = root / "oim" / hmd / f"{prefix}-all-oim-{version}.xsd"
        dim = root / "oim" / hmd / f"{prefix}-all-dim-{version}.xml"
        for path in (tuple_entry, oim_entry, dim):
            if not path.is_file():
                failures.append(f"missing HMD artefact: {path.relative_to(root)}")
        entries[f"tuple:{hmd}"] = tuple_entry
        entries[f"oim:{hmd}"] = oim_entry

    # Generic local-reference and fragment-resolution checks.
    local_refs = 0
    unresolved_files = 0
    unresolved_fragments = 0
    for path in all_files:
        if path.suffix.lower() not in {".xsd", ".xml"}:
            continue
        tree = parse_xml(path, failures)
        if tree is None:
            continue
        for node in tree.iter():
            refs = []
            schema_location = node.attrib.get("schemaLocation")
            if schema_location:
                refs.append(schema_location)
            href = node.attrib.get(XLINK_HREF)
            if href:
                refs.append(href)
            for ref in refs:
                if ref.startswith("#") or is_remote(ref):
                    continue
                local_refs += 1
                target, fragment = split_ref(path, ref)
                if not target.exists():
                    unresolved_files += 1
                    failures.append(
                        f"{path.relative_to(root)} unresolved local file {ref!r}"
                    )
                    continue
                if fragment:
                    target_ids = ids_in(target, failures)
                    if fragment not in target_ids:
                        unresolved_fragments += 1
                        failures.append(
                            f"{path.relative_to(root)} unresolved local fragment {ref!r}"
                        )

    # Tuple and OIM entry points must select binding-specific root-module
    # presentation linkbases.
    for hmd, prefix in HMD_PREFIXES.items():
        tuple_entry = entries[f"tuple:{hmd}"]
        oim_entry = entries[f"oim:{hmd}"]
        if tuple_entry.exists():
            refs = presentation_refs(tuple_entry, failures)
            expected = [f"../../{prefix}/{prefix}-pre-{version}.xml"]
            if refs != expected:
                failures.append(
                    f"{tuple_entry.relative_to(root)} presentation refs "
                    f"{refs!r} != {expected!r}"
                )
        if oim_entry.exists():
            refs = presentation_refs(oim_entry, failures)
            expected = [f"../../{prefix}/{prefix}-oim-pre-{version}.xml"]
            if refs != expected:
                failures.append(
                    f"{oim_entry.relative_to(root)} presentation refs "
                    f"{refs!r} != {expected!r}"
                )

    # Binding-specific module schemas.
    tuple_schema_elements = {}
    oim_schema_elements = {}
    for module in MODULES:
        tuple_schema = root / module / f"{module}-{version}.xsd"
        oim_schema = root / module / f"{module}-oim-{version}.xsd"

        tuple_elements = global_elements(tuple_schema, failures)
        oim_elements = global_elements(oim_schema, failures)
        tuple_schema_elements[module] = tuple_elements
        oim_schema_elements[module] = oim_elements

        # Tuple module schema may contain A/C/R declarations.
        for element_id, node in tuple_elements.items():
            substitution = node.attrib.get("substitutionGroup", "")
            if substitution not in {"xbrli:item", "xbrli:tuple"}:
                failures.append(
                    f"{tuple_schema.relative_to(root)} {element_id} has "
                    f"unexpected substitutionGroup {substitution!r}"
                )

        # OIM module schema must be standalone with item-only concepts:
        # A items and module-owned p_ Class anchors. h_/d_ remain HMD-specific.
        for element_id, node in oim_elements.items():
            substitution = node.attrib.get("substitutionGroup", "")
            if substitution == "xbrli:tuple":
                failures.append(
                    f"{oim_schema.relative_to(root)} contains Tuple concept {element_id}"
                )
            if element_id.startswith(("h_", "d_")):
                failures.append(
                    f"{oim_schema.relative_to(root)} contains HMD-specific "
                    f"dimensional concept {element_id}"
                )
            if element_id.startswith("p_") and substitution != "xbrli:item":
                failures.append(
                    f"{oim_schema.relative_to(root)} primary item {element_id} "
                    f"is not xbrli:item"
                )
            if node.attrib.get("type", "").endswith("ComplexType"):
                failures.append(
                    f"{oim_schema.relative_to(root)} has Tuple structural type "
                    f"reference on {element_id}"
                )

    # Binding-specific presentation linkbases.
    presentation_summary = {}
    for module in MODULES:
        tuple_pre = root / module / f"{module}-pre-{version}.xml"
        oim_pre = root / module / f"{module}-oim-pre-{version}.xml"

        for binding, pre in (("tuple", tuple_pre), ("oim", oim_pre)):
            stats = presentation_stats(pre, failures)
            presentation_summary[f"{binding}:{module}"] = stats
            if stats["duplicate_locators"]:
                failures.append(
                    f"{pre.relative_to(root)} duplicate locator groups "
                    f"{stats['duplicate_locators']}"
                )
            if stats["duplicate_arcs"]:
                failures.append(
                    f"{pre.relative_to(root)} duplicate presentationArc groups "
                    f"{stats['duplicate_arcs']}"
                )

            tree = parse_xml(pre, failures)
            if tree is None:
                continue
            for locator in [
                node for node in tree.iter() if lname(node.tag) == "loc"
            ]:
                href = locator.attrib.get(XLINK_HREF, "")
                if "-content-" in href:
                    failures.append(
                        f"{pre.relative_to(root)} locator targets content schema {href!r}"
                    )
                if not href or is_remote(href):
                    continue
                target, fragment = split_ref(pre, href)
                if not target.exists() or not fragment:
                    continue
                target_elements = global_elements(target, failures)
                concept = target_elements.get(fragment)
                if concept is None:
                    failures.append(
                        f"{pre.relative_to(root)} locator does not target a global "
                        f"concept declaration: {href!r}"
                    )
                    continue
                substitution = concept.attrib.get("substitutionGroup", "")

                if binding == "tuple":
                    if "-oim-" in target.name:
                        failures.append(
                            f"{pre.relative_to(root)} Tuple presentation uses OIM schema {href!r}"
                        )
                    if substitution not in {"xbrli:item", "xbrli:tuple"}:
                        failures.append(
                            f"{pre.relative_to(root)} invalid Tuple concept target {href!r}"
                        )
                else:
                    if "-oim-" not in target.name:
                        failures.append(
                            f"{pre.relative_to(root)} OIM presentation uses Tuple schema {href!r}"
                        )
                    if substitution != "xbrli:item":
                        failures.append(
                            f"{pre.relative_to(root)} OIM locator target is not "
                            f"xbrli:item: {href!r}"
                        )
                    if fragment.startswith(("h_", "d_")):
                        failures.append(
                            f"{pre.relative_to(root)} OIM presentation uses "
                            f"dimensional-only concept {href!r}"
                        )

    # OIM entry-point imports must use exactly the OIM schemas for the modules
    # declared by the current formal HMD contract (besides remote imports).
    for hmd, prefix in HMD_PREFIXES.items():
        oim_entry = entries[f"oim:{hmd}"]
        if not oim_entry.exists():
            continue
        imports = schema_import_targets(oim_entry, failures)
        local_imports = [ref for ref in imports if not is_remote(ref)]
        module_imports = [ref for ref in local_imports if "/../" in ref or ref.startswith("../")]
        oim_module_imports = [ref for ref in module_imports if f"-oim-{version}.xsd" in ref]
        tuple_module_imports = [
            ref for ref in module_imports
            if f"-oim-{version}.xsd" not in ref and f"-{version}.xsd" in ref
        ]
        if tuple_module_imports:
            failures.append(
                f"{oim_entry.relative_to(root)} imports Tuple module schema(s): "
                f"{tuple_module_imports}"
            )
        expected_imports = [
            f"../../{module}/{module}-oim-{version}.xsd"
            for module in HMD_MODULES[hmd]
        ]
        if sorted(oim_module_imports) != sorted(expected_imports):
            failures.append(
                f"{oim_entry.relative_to(root)} OIM module imports "
                f"{sorted(oim_module_imports)!r} != {sorted(expected_imports)!r}"
            )

    # Tuple entry points must not import module OIM schemas.
    for hmd in HMD_PREFIXES:
        tuple_entry = entries[f"tuple:{hmd}"]
        if not tuple_entry.exists():
            continue
        imports = schema_import_targets(tuple_entry, failures)
        bad = [ref for ref in imports if "-oim-" in ref]
        if bad:
            failures.append(
                f"{tuple_entry.relative_to(root)} imports OIM module schema(s): {bad}"
            )

    # OIM dimensional linkbases may resolve primary items to module OIM
    # schemas and h_/d_/role declarations to the HMD OIM entry point, but must
    # never target Tuple module/content schemas.
    dimensional_locators = 0
    for hmd, prefix in HMD_PREFIXES.items():
        dim = root / "oim" / hmd / f"{prefix}-all-dim-{version}.xml"
        tree = parse_xml(dim, failures)
        if tree is None:
            continue
        for locator in [
            node for node in tree.iter() if lname(node.tag) == "loc"
        ]:
            dimensional_locators += 1
            href = locator.attrib.get(XLINK_HREF, "")
            if "-content-" in href:
                failures.append(
                    f"{dim.relative_to(root)} dimensional locator targets Tuple "
                    f"content schema {href!r}"
                )
            if href.startswith("../../") and "-oim-" not in href:
                failures.append(
                    f"{dim.relative_to(root)} dimensional locator targets Tuple "
                    f"module schema {href!r}"
                )

    print(f"package: {root}")
    print(f"files: {len(all_files)}")
    print(f"local references checked: {local_refs}")
    print(f"unresolved local files: {unresolved_files}")
    print(f"unresolved local fragments: {unresolved_fragments}")
    print(f"dimensional locators checked: {dimensional_locators}")
    for module in MODULES:
        t = presentation_summary.get(f"tuple:{module}", {})
        o = presentation_summary.get(f"oim:{module}", {})
        print(
            f"presentation {module}: "
            f"tuple locators={t.get('locators', 0)} arcs={t.get('arcs', 0)} "
            f"dupLoc={t.get('duplicate_locators', 0)} dupArc={t.get('duplicate_arcs', 0)}; "
            f"oim locators={o.get('locators', 0)} arcs={o.get('arcs', 0)} "
            f"dupLoc={o.get('duplicate_locators', 0)} dupArc={o.get('duplicate_arcs', 0)}"
        )
    print(f"failures: {len(failures)}")
    for failure in failures:
        print(f"ERROR: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

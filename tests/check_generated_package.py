#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Static conformance checks for one generated XBRL GL Next formal package."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
XLINK_ROLE = "{http://www.w3.org/1999/xlink}role"
PRESENTATION_REF_ROLE = "http://www.xbrl.org/2003/role/presentationLinkbaseRef"
HMD_PREFIXES = {
    "cor_accountingEntries": "cor",
    "btx_businessTransactions": "btx",
}


def is_remote(ref: str) -> bool:
    return bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", ref))


def local_target(source: Path, ref: str) -> Path:
    path_part = ref.split("#", 1)[0]
    return source if not path_part else (source.parent / path_part).resolve()


def parse_xml(path: Path, failures: list[str]):
    try:
        return ET.parse(path)
    except Exception as exc:
        failures.append(f"invalid XML {path}: {exc}")
        return None


def discover_dts(entry: Path, failures: list[str]) -> set[Path]:
    seen: set[Path] = set()
    stack = [entry.resolve()]
    while stack:
        path = stack.pop()
        if path in seen:
            continue
        if not path.exists():
            failures.append(f"missing DTS resource: {path}")
            continue
        seen.add(path)
        tree = parse_xml(path, failures)
        if tree is None:
            continue
        for node in tree.iter():
            local = node.tag.rsplit("}", 1)[-1]
            ref = None
            if local in {"import", "include", "redefine"}:
                ref = node.attrib.get("schemaLocation")
            elif local == "linkbaseRef":
                ref = node.attrib.get(XLINK_HREF)
            if not ref or ref.startswith("#") or is_remote(ref):
                continue
            target = local_target(path, ref)
            if target.exists():
                stack.append(target)
            else:
                failures.append(
                    f"{path}: unresolved DTS reference {ref!r}"
                )
    return seen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_root", type=Path)
    parser.add_argument("--version", default="2026-12-31")
    args = parser.parse_args()
    root = args.package_root.resolve()
    version = args.version
    failures: list[str] = []

    if not root.is_dir():
        print(f"ERROR: package root not found: {root}")
        return 1

    for obsolete in (root / "all", root / "presentation"):
        if obsolete.exists():
            failures.append(f"obsolete top-level directory exists: {obsolete.name}")

    entries: dict[str, Path] = {}
    presentations: dict[str, Path] = {}
    for hmd, prefix in HMD_PREFIXES.items():
        tuple_root = root / "tuple" / hmd
        oim_root = root / "oim" / hmd
        expected = [
            tuple_root / f"{prefix}-all-{version}.xsd",
            tuple_root / f"{prefix}-all-pre-{version}.xml",
            oim_root / f"{prefix}-all-oim-{version}.xsd",
            oim_root / f"{prefix}-all-dim-{version}.xml",
            oim_root / f"{prefix}-all-pre-{version}.xml",
        ]
        for path in expected:
            if not path.is_file():
                failures.append(f"missing expected artefact: {path.relative_to(root)}")
        entries[f"tuple:{hmd}"] = expected[0]
        presentations[f"tuple:{hmd}"] = expected[1]
        entries[f"oim:{hmd}"] = expected[2]
        presentations[f"oim:{hmd}"] = expected[4]

    old_names = []
    old_pattern = re.compile(
        r"^(cor_accountingEntries|btx_businessTransactions)-(?:all|oim|dim|pre)-"
    )
    for path in root.rglob("*"):
        if path.is_file() and old_pattern.match(path.name):
            old_names.append(path.relative_to(root).as_posix())
    if old_names:
        failures.append(f"obsolete HMD filenames remain: {sorted(old_names)}")

    local_refs = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".xsd", ".xml"}:
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
                if "../../all/" in ref or "../../presentation/" in ref:
                    failures.append(
                        f"{path.relative_to(root)} has obsolete reference {ref!r}"
                    )
                if ref.startswith("#") or is_remote(ref):
                    continue
                local_refs += 1
                target = local_target(path, ref)
                if not target.exists():
                    failures.append(
                        f"{path.relative_to(root)} has unresolved local reference {ref!r}"
                    )

    for key, entry in entries.items():
        if not entry.exists():
            continue
        tree = parse_xml(entry, failures)
        if tree is None:
            continue
        refs = [
            node.attrib.get(XLINK_HREF, "")
            for node in tree.iter()
            if node.tag.rsplit("}", 1)[-1] == "linkbaseRef"
            and node.attrib.get(XLINK_ROLE) == PRESENTATION_REF_ROLE
        ]
        hmd = key.split(":", 1)[1]
        prefix = HMD_PREFIXES[hmd]
        expected_hmd = f"{prefix}-all-pre-{version}.xml"
        hmd_refs = [ref for ref in refs if ref.endswith(f"-all-pre-{version}.xml")]
        if hmd_refs != [expected_hmd]:
            failures.append(
                f"{entry.relative_to(root)} must reference exactly one HMD "
                f"presentation {expected_hmd!r}; got {hmd_refs!r}"
            )

    for key, entry in entries.items():
        if not entry.exists():
            continue
        reached = discover_dts(entry, failures)
        rel = [p.relative_to(root).as_posix() for p in reached if p.is_relative_to(root)]
        if key.startswith("tuple:"):
            bad = [item for item in rel if item.startswith("oim/")]
            if bad:
                failures.append(f"{key} reaches OIM resources: {sorted(bad)}")
            for path in reached:
                if path.suffix.lower() != ".xsd":
                    continue
                text = path.read_text(encoding="utf-8-sig")
                if any(token in text for token in ('name="h_', 'name="d_', 'name="p_')):
                    failures.append(
                        f"{key} reaches OIM h_/d_/p_ declarations in {path}"
                    )
        else:
            bad = [
                item for item in rel
                if item.startswith("tuple/") or "-content-" in item
            ]
            if bad:
                failures.append(f"{key} reaches Tuple content: {sorted(bad)}")

    for key, path in presentations.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8-sig")
        hmd = key.split(":", 1)[1]
        prefix = HMD_PREFIXES[hmd]
        if key.startswith("tuple:"):
            if "../../all/" in text or "../../presentation/" in text:
                failures.append(f"{path.relative_to(root)} has obsolete Tuple locator")
            structural = re.findall(
                rf'xlink:href="([^\"]+-content-{re.escape(version)}\.xsd#[^\"]+)"',
                text,
            )
            if not structural:
                failures.append(
                    f"{path.relative_to(root)} has no HMD content-schema structural locator"
                )
        else:
            if "-content-" in text:
                failures.append(f"{path.relative_to(root)} references Tuple content")
            if re.search(r"#[hd]_", text):
                failures.append(f"{path.relative_to(root)} has h_/d_ presentation locator")
            for href in re.findall(r'xlink:href="([^\"]+#p_[^\"]+)"', text):
                if not href.startswith(f"{prefix}-all-oim-{version}.xsd#p_"):
                    failures.append(
                        f"{path.relative_to(root)} has incorrect p_ locator {href!r}"
                    )

    print(f"package: {root}")
    print(f"local references checked: {local_refs}")
    print(f"failures: {len(failures)}")
    for failure in failures:
        print(f"ERROR: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

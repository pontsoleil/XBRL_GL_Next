#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate Tuple XML and formal xBRL-CSV from an HMD-selected View supplied as Excel or CSV.

Task-local candidate. Source workbook and taxonomy are always read-only.
Run `inspect` first, then provide an approved binding and context configuration.
No accounting values, entity identifiers or reporting dates are defaulted.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from structured_oim import emit_structured_oim

S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
X = "http://www.w3.org/2001/XMLSchema"
NS = {"s": S}
STANDARD = {
    "xbrli": "http://www.xbrl.org/2003/instance",
    "link": "http://www.xbrl.org/2003/linkbase",
    "xlink": "http://www.w3.org/1999/xlink",
    "iso4217": "http://www.xbrl.org/2003/iso4217",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        f.write(data)


def save_json(path, data):
    save(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_sheet(path, sheet_name):
    # One byte snapshot prevents mixing cells from different saves of an open file.
    raw = Path(path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rel = {r.get("Id"): r.get("Target") for r in
               ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheets = [s for s in wb.find("s:sheets", NS) if s.get("name") == sheet_name]
        if len(sheets) != 1:
            raise ValueError(f"Sheet not uniquely defined: {sheet_name}")
        rid = sheets[0].get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        target = rel[rid]
        target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(t.text or "" for t in si.iter(f"{{{S}}}t"))
                       for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        cells = {}
        for c in ET.fromstring(z.read(target)).iter(f"{{{S}}}c"):
            if c.find("s:f", NS) is not None:
                raise ValueError(f"Formula requires explicit recalculated input: {c.get('r')}")
            kind = c.get("t", "n")
            val = c.findtext("s:v", default="", namespaces=NS)
            if kind == "s":
                val = strings[int(val)]
            elif kind == "inlineStr":
                val = "".join(t.text or "" for t in c.iter(f"{{{S}}}t"))
            if kind == "e":
                raise ValueError(f"Excel error at {c.get('r')}: {val}")
            cells[c.get("r")] = {"value": val, "kind": kind, "style": c.get("s")}
        prop = wb.find("s:workbookPr", NS)
        date1904 = prop is not None and prop.get("date1904") in ("1", "true")
    return view_from_cells(path, hashlib.sha256(raw).hexdigest(), sheet_name, date1904, cells)


def view_from_cells(path, digest, sheet_name, date1904, cells):
    columns = [cells.get(f"{col}1", {}).get("value", "") for col in "ABCDEFGHIJK"]
    expected = ["sequence", "module", "level", "type", "identifier", "name", "datatype",
                "multiplicity", "value_domain", "semantic_path", "local_name"]
    if columns != expected:
        raise ValueError(f"Unexpected view schema: {columns}")
    rows, stack = [], []
    for row_no in sorted({int(re.search(r"\d+$", a)[0]) for a in cells}):
        if row_no == 1 or not cells.get(f"J{row_no}", {}).get("value"):
            continue
        row = dict(zip(columns, [cells.get(f"{col}{row_no}", {}).get("value", "") for col in "ABCDEFGHIJK"]))
        row["excel_row"] = row_no
        level = int(row["level"])
        while stack and int(stack[-1]["level"]) >= level:
            stack.pop()
        row["parent"] = stack[-1]["semantic_path"] if stack else None
        if row["parent"] and not row["semantic_path"].startswith(row["parent"] + "."):
            raise ValueError(f"Hierarchy/path disagreement at row {row_no}")
        if row["type"] == "C":
            stack.append(row)
        rows.append(row)
    if len({r["semantic_path"] for r in rows}) != len(rows):
        raise ValueError("Duplicate view semantic_path")
    if len({(r["module"], r["local_name"]) for r in rows}) != len(rows):
        raise ValueError("Duplicate module/local_name in view")
    return {"path": str(Path(path).resolve()), "sha256": digest,
            "sheet": sheet_name, "date1904": date1904, "rows": rows, "cells": cells}


def csv_record_comparison(raw):
    """Comparison only: preserve quoted values; normalise record CRLF only."""
    out, state, i = bytearray(), "start", 0
    if raw.startswith(b"\xef\xbb\xbf"):
        out.extend(raw[:3]); i = 3
    while i < len(raw):
        c = raw[i]
        if state == "quoted":
            if c == 34:
                if i + 1 < len(raw) and raw[i + 1] == 34:
                    out.extend(raw[i:i+2]); i += 2; continue
                state = "after"
            out.append(c); i += 1; continue
        if c == 34:
            if state != "start":
                raise ValueError("CSV quote outside field start")
            state = "quoted"; out.append(c); i += 1; continue
        if c == 44:
            state = "start"; out.append(c); i += 1; continue
        if c in (10, 13):
            if c == 13 and i + 1 < len(raw) and raw[i + 1] == 10:
                out.append(10); i += 2
            else:
                out.append(c); i += 1
            state = "start"; continue
        if state == "after":
            raise ValueError("CSV characters after quoted field")
        state = "unquoted"; out.append(c); i += 1
    if state == "quoted":
        raise ValueError("Unclosed CSV quoted field")
    return bytes(out)


def column_name(number):
    result = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def read_view_csv(path, sheet_name):
    raw = Path(path).read_bytes()
    csv_record_comparison(raw)
    records = list(csv.reader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True))
    if not records or len(records[0]) < 12:
        raise ValueError("View CSV requires structure columns and value columns")
    width = len(records[0])
    if any(len(row) != width for row in records):
        raise ValueError("Inconsistent View CSV column count")
    cells = {f"{column_name(col)}{row_no}": {"value": value, "kind": "str", "style": None}
             for row_no, row in enumerate(records, 1)
             for col, value in enumerate(row, 1)}
    view = view_from_cells(path, hashlib.sha256(raw).hexdigest(), sheet_name, False, cells)
    view["source_kind"] = "csv"
    view["comparison_sha256"] = hashlib.sha256(csv_record_comparison(raw)).hexdigest()
    return view


def export_view_csv(view, output):
    """Full existing View grid; dates use the existing lexical conversion."""
    cells = view["cells"]
    nonempty = [a for a, c in cells.items() if c["value"] != ""]
    max_row = max(int(re.search(r"\d+$", a)[0]) for a in nonempty)
    cols = {re.sub(r"\d", "", a) for a in nonempty}
    names = sorted(cols, key=lambda c: (len(c), c))
    max_col = names[-1]
    width = 0
    for char in max_col:
        width = width * 26 + ord(char) - 64
    date_rows = {r["excel_row"] for r in view["rows"] if r["datatype"] == "Date"}
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    for row_no in range(1, max_row + 1):
        row = []
        for col in range(1, width + 1):
            cell = cells.get(f"{column_name(col)}{row_no}", {"value": "", "kind": "str"})
            value = cell["value"]
            if col > 11 and row_no in date_rows and value != "":
                value = lexical(cell, "Date", view, {})
            row.append(value)
        writer.writerow(row)
    save(output, buffer.getvalue())
    return {"csv": str(Path(output).resolve()), "csv_sha256": sha(output),
            "csv_comparison_sha256": hashlib.sha256(csv_record_comparison(Path(output).read_bytes())).hexdigest(),
            "comparison_profile": "CRLF-to-LF-record-separators-only;quoted-values-preserved",
            "workbook_sha256": view["sha256"], "sheet": view["sheet"],
            "records_including_header": max_row, "columns": width,
            "selected_model_rows": len(view["rows"]),
            "date_policy": "Existing Excel Date lexical conversion to ISO; CSV dates are strings"}


def resolve_config_paths(config, config_path):
    config = dict(config)
    for key in ("hmd", "taxonomy_root", "tuple_entry", "oim_entry", "view_definition"):
        if key not in config:
            continue
        p = Path(config[key])
        config[key] = str((Path(config_path).parent / p).resolve()) if not p.is_absolute() else str(p)
    return config


def bounds(value):
    if value == "1":
        return 1, 1
    lo, hi = value.split("..")
    return int(lo), None if hi == "*" else int(hi)


def binding_from_sheet(view):
    """Read occurrence identifiers explicitly supplied above the view rows."""
    classes = [r for r in view["rows"] if r["type"] == "C"]
    first = min(r["excel_row"] for r in view["rows"])
    by_label = {"d" + r["local_name"][0].upper() + r["local_name"][1:]: r for r in classes}
    if len(by_label) != len(classes):
        raise ValueError("Occurrence header names are ambiguous across modules")
    data_columns = sorted({re.sub(r"\d", "", a) for a, c in view["cells"].items()
                           if c["value"] and re.sub(r"\d", "", a) not in list("ABCDEFGHIJK")},
                          key=lambda c: (len(c), c))
    binding = {c: {} for c in data_columns}
    for i in range(2, first):
        label = view["cells"].get(f"K{i}", {}).get("value")
        if not label:
            continue
        if label not in by_label:
            raise ValueError(f"Unknown occurrence header K{i}: {label}")
        row = by_label[label]
        qname = f"{row['module']}:{row['local_name']}"
        for col in data_columns:
            value = view["cells"].get(f"{col}{i}", {}).get("value")
            if value:
                binding[col][qname] = value
    # One report wrapper is a structural occurrence key, never a business fact.
    roots = [r for r in classes if r["parent"] is None]
    if len(roots) != 1:
        raise ValueError("This view binding requires exactly one root class")
    root = roots[0]
    for col in binding:
        binding[col][f"{root['module']}:{root['local_name']}"] = "1"
        for cls in classes:
            if cls["parent"] and bounds(cls["multiplicity"])[1] == 1:
                parent = next(r for r in classes if r["semantic_path"] == cls["parent"])
                if f"{parent['module']}:{parent['local_name']}" in binding[col]:
                    binding[col][f"{cls['module']}:{cls['local_name']}"] = "1"
    return binding


def load_authority(config, view):
    hmd = Path(config["hmd"])
    with hmd.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if len(reader.fieldnames) != 18 or reader.fieldnames[8] != "value_domain":
            raise ValueError("HMD must retain the 18-column value_domain schema")
        records = list(reader)
    by_path = {r["semantic_path"]: r for r in records}
    if len(by_path) != len(records):
        raise ValueError("Duplicate HMD semantic_path")
    comparisons = []
    for row in view["rows"]:
        base = by_path.get(row["semantic_path"])
        if base is None:
            raise ValueError(f"View concept absent from HMD: {row['semantic_path']}")
        for field in ("module", "local_name", "type", "datatype", "level", "sequence"):
            if base[field] != row[field]:
                raise ValueError(f"View/HMD {field} mismatch at row {row['excel_row']}")
        vlo, vhi = bounds(row["multiplicity"])
        hlo, hhi = bounds(base["multiplicity"])
        if vlo < hlo or (hhi is not None and (vhi is None or vhi > hhi)):
            raise ValueError(f"View relaxes HMD multiplicity at row {row['excel_row']}")
        comparisons.append({"row": row["excel_row"], "view_multiplicity": row["multiplicity"],
                            "hmd_multiplicity": base["multiplicity"], "semantic_path": row["semantic_path"]})
    root = Path(config["taxonomy_root"])
    namespaces = dict(STANDARD)
    for module in {r["module"] for r in view["rows"]}:
        namespaces[module] = ET.parse(root / module / f"{module}-2026-12-31.xsd").getroot().get("targetNamespace")
    oim = ET.parse(config["oim_entry"]).getroot()
    namespaces["plt"] = oim.get("targetNamespace")
    dimension_names = {x.get("name") for x in oim.findall(f"{{{X}}}element")
                       if x.get("substitutionGroup") == "xbrldt:dimensionItem"}
    for row in view["rows"]:
        for suffix in ("", "-oim"):
            schema = root / row["module"] / f"{row['module']}{suffix}-2026-12-31.xsd"
            concept_name = (f"p_{row['module']}_{row['local_name']}"
                            if suffix and row["type"] == "C" else row["local_name"])
            found = [x for x in ET.parse(schema).getroot().findall(f"{{{X}}}element")
                     if x.get("name") == concept_name]
            if len(found) != 1:
                raise ValueError(f"Undefined taxonomy concept: {schema} / {row['local_name']}")
            row["period_type"] = found[0].get(f"{{{STANDARD['xbrli']}}}periodType")
    return by_path, namespaces, dimension_names, comparisons


def lexical(cell, datatype, view, config):
    value = cell["value"]
    if re.search(r"_x(?:000D|005F)_", value, re.I):
        raise ValueError("Office escape semantics require source review")
    if datatype == "Date" and cell["kind"] == "n":
        serial = float(value)
        if serial != int(serial) or (not view["date1904"] and serial == 60):
            raise ValueError("Unsupported Excel date/time value")
        origin = dt.datetime(1904, 1, 1) if view["date1904"] else dt.datetime(1899, 12, 30)
        if not view["date1904"] and serial < 60:
            serial += 1
        return (origin + dt.timedelta(days=serial)).date().isoformat()
    if datatype == "QName":
        value = config.get("qname_values", {}).get(value, value)
        if ":" not in value:
            raise ValueError(f"QName namespace mapping required: {value}")
        return value
    if "\n" in value or "\r" in value:
        raise ValueError("Fact text contains an unapproved embedded line break")
    return value


def build(view, config, hmd, namespaces, dimensions):
    if config.get("binding_confirmed") is not True:
        raise ValueError("USER_INPUT_REQUIRED: column occurrence binding is not confirmed")
    for key in ("entity_scheme", "entity_identifier", "instant", "currency", "decimals"):
        if config.get(key) is None or config.get(key) == "":
            raise ValueError(f"USER_INPUT_REQUIRED: {key}")
    if "T" not in config["instant"]:
        raise ValueError("Specify an exact ISO datetime for the instant; do not infer a day boundary")
    dt.datetime.fromisoformat(config["instant"].replace("Z", "+00:00"))
    nodes, facts, sources = {}, {}, []
    rows = {r["semantic_path"]: r for r in view["rows"]}
    overrides = config.get("cell_overrides", {})
    for address, value in overrides.items():
        if view["cells"].get(address, {}).get("value"):
            raise ValueError(f"Override must not replace a populated source cell: {address}")
        if not value or not value.get("approval") or value.get("value") in (None, ""):
            raise ValueError(f"Unapproved or empty override: {address}")
    for row in view["rows"]:
        if row["type"] == "C":
            continue
        for column, binding in config["column_occurrences"].items():
            address = f"{column}{row['excel_row']}"
            cell = view["cells"].get(address, {"value": "", "kind": "s"})
            if address in overrides:
                cell = {"value": str(overrides[address]["value"]), "kind": "s"}
            if cell["value"] == "":
                continue
            lineage = []
            parent = row["parent"]
            while parent:
                lineage.insert(0, rows[parent])
                parent = rows[parent]["parent"]
            chain = []
            for cls in lineage:
                name = f"{cls['module']}:{cls['local_name']}"
                if name not in binding:
                    raise ValueError(f"No occurrence binding for {address} under {name}")
                chain.append((cls["semantic_path"], str(binding[name])))
                node_key = tuple(chain)
                nodes.setdefault(node_key, {"row": cls, "key": node_key, "parent": node_key[:-1]})
            value = lexical(cell, row["datatype"], view, config)
            identity = (tuple(chain), row["semantic_path"])
            if identity in facts and facts[identity]["value"] != value:
                raise ValueError(f"Conflicting fact values for one occurrence: {address}")
            facts.setdefault(identity, {"row": row, "node": tuple(chain), "value": value, "cells": []})["cells"].append(address)
            sources.append({"cell": address, "value": value, "semantic_path": row["semantic_path"],
                            "occurrences": chain, "override": address in overrides})
    used = {s["cell"] for s in sources}
    for address, cell in view["cells"].items():
        column = re.sub(r"\d", "", address)
        is_data_row = int(re.search(r"\d+$", address)[0]) in {r["excel_row"] for r in view["rows"]}
        if is_data_row and column in config["column_occurrences"] and cell["value"] and address not in used:
            raise ValueError(f"Unconsumed data cell: {address}")
    if set(overrides) - used:
        raise ValueError("Unconsumed overrides")
    violations = []
    for node_key, node in nodes.items():
        for child in view["rows"]:
            if child["parent"] != node["row"]["semantic_path"]:
                continue
            count = sum(n["parent"] == node_key and n["row"]["semantic_path"] == child["semantic_path"] for n in nodes.values()) if child["type"] == "C" else int((node_key, child["semantic_path"]) in facts)
            lo, hi = bounds(child["multiplicity"])
            if count < lo or (hi is not None and count > hi):
                violations.append({"node": node_key, "semantic_path": child["semantic_path"],
                                   "required": child["multiplicity"], "actual": count})
    if violations:
        raise ValueError("View occurrence constraints unmet: " + json.dumps(violations, ensure_ascii=False))
    return nodes, facts, sources


def emit(view, config, namespaces, dimensions, nodes, facts, out, profiles):
    tuple_path = out / "tuple" / "accountingEntries-view1.xml"
    oim_path = out / "oim" / (config.get("oim_basename", "accountingEntries-view1") + ".json")
    namespaces["ent"] = config["entity_scheme"]
    xml = ET.Element("xbrli:xbrl", {f"xmlns:{k}": v for k, v in namespaces.items() if k != "ent"})
    ET.SubElement(xml, "link:schemaRef", {"xlink:type": "simple", "xlink:href": os.path.relpath(config["tuple_entry"], tuple_path.parent).replace("\\", "/")})
    ctx = ET.SubElement(xml, "xbrli:context", {"id": "c1"})
    entity = ET.SubElement(ctx, "xbrli:entity")
    ET.SubElement(entity, "xbrli:identifier", {"scheme": config["entity_scheme"]}).text = config["entity_identifier"]
    period = ET.SubElement(ctx, "xbrli:period")
    ET.SubElement(period, "xbrli:instant").text = config["instant"]
    for uid, measure in (("uCurrency", "iso4217:" + config["currency"]), ("uPure", "xbrli:pure")):
        unit = ET.SubElement(xml, "xbrli:unit", {"id": uid})
        ET.SubElement(unit, "xbrli:measure").text = measure
    # The full HMD order also orders a restricted view's Tuple content.
    def numeric(row):
        return row["datatype"] in ("Monetary", "Pure", "Decimal", "Integer", "Float", "Double")
    def write_node(node_key, parent):
        node = nodes[node_key]
        row = node["row"]
        element = ET.SubElement(parent, f"{row['module']}:{row['local_name']}")
        content = [(int(n["row"]["sequence"]), "node", k) for k, n in nodes.items() if n["parent"] == node_key]
        content += [(int(f["row"]["sequence"]), "fact", k) for k, f in facts.items() if f["node"] == node_key]
        for _, kind, key in sorted(content, key=lambda x: x[0]):
            if kind == "node":
                write_node(key, element)
            else:
                f = facts[key]
                row = f["row"]
                attr = {"contextRef": "c1", "id": f"f{list(facts).index(key) + 1}"}
                if numeric(row):
                    attr.update(unitRef="uCurrency" if row["datatype"] == "Monetary" else "uPure", decimals=str(config["decimals"]))
                ET.SubElement(element, f"{row['module']}:{row['local_name']}", attr).text = f["value"]
    for key in nodes:
        if len(key) == 1:
            write_node(key, xml)
    ET.indent(xml, space="  ")
    if "tuple" in profiles:
        save(tuple_path, '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(xml, encoding="unicode") + "\n")
    if "oim" in profiles:
        emit_structured_oim(view, config, namespaces, dimensions, nodes, facts, out)
    return tuple_path, oim_path


def validate(executable, instances, out, profiles):
    records = []
    for profile, instance in zip(("tuple", "oim"), instances):
        if profile not in profiles:
            continue
        log = (out / f"{profile}.arelle.xml").resolve()
        argv = [str(executable), "--file", str(instance.resolve()), "--validate", "--internetConnectivity=offline",
                "--logLevel=info", "--logFile", str(log)]
        start = dt.datetime.now().astimezone().isoformat()
        run = subprocess.run(argv, capture_output=True, cwd=Path.cwd())
        end = dt.datetime.now().astimezone().isoformat()
        for suffix, content in (("stdout", run.stdout), ("stderr", run.stderr)):
            path = out / f"{profile}.{suffix}.txt"
            with path.open("xb") as f:
                f.write(content)
        messages = []
        if log.exists():
            for entry in ET.parse(log).getroot().iter("entry"):
                messages.append({"level": entry.get("level"), "code": entry.get("code"),
                                 "text": "".join(entry.itertext()).strip()})
        errors = sum(str(m["level"]).lower() in ("error", "fatal", "critical") for m in messages)
        warnings = sum(str(m["level"]).lower() in ("warning", "warn") for m in messages)
        validated = any("validated" in m["text"] for m in messages)
        records.append({"profile": profile, "argv": argv, "cwd": str(Path.cwd()), "start": start, "end": end,
                        "exit": run.returncode, "errors": errors, "warnings": warnings, "messages": messages,
                        "instance_sha256": sha(instance), "log_sha256": sha(log) if log.exists() else None,
                        "result": "PASS" if run.returncode == 0 and not errors and validated else "FAIL"})
    save_json(out / "ARELLE_RESULTS.json", records)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inspect", "export-csv", "generate"))
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--workbook", type=Path)
    source.add_argument("--csv", type=Path, dest="view_csv")
    parser.add_argument("--sheet", default="LHM_view1_cor")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--output-profiles", choices=("tuple", "oim"), nargs="+", default=["tuple", "oim"])
    parser.add_argument("--arelle", type=Path)
    parser.add_argument("--validate-profiles", choices=("tuple", "oim"), nargs="+", default=["tuple", "oim"])
    args = parser.parse_args()
    input_path = args.view_csv or args.workbook
    view = read_view_csv(args.view_csv, args.sheet) if args.view_csv else read_sheet(args.workbook, args.sheet)
    if args.mode == "export-csv":
        if not args.workbook:
            parser.error("export-csv requires --workbook")
        record = export_view_csv(view, args.output)
        save_json(args.output.with_suffix(".source.json"), record)
        print(json.dumps(record))
        return 0
    if args.mode == "inspect":
        save_json(args.output / "SOURCE_SHEET.json", view)
        print(json.dumps({"sheet": args.sheet, "sha256": view["sha256"], "rows": len(view["rows"])}))
        return 0
    if not args.config:
        parser.error("generate requires --config")
    config = resolve_config_paths(json.loads(args.config.read_text(encoding="utf-8")), args.config)
    if args.view_csv:
        if view["comparison_sha256"] != config["csv_comparison_sha256"]:
            raise ValueError("View CSV content changed since binding approval")
    elif view["sha256"] != config["workbook_sha256"]:
        raise ValueError("Workbook changed since binding approval")
    hmd, namespaces, dims, comparisons = load_authority(config, view)
    protected = {str(input_path): view["sha256"], str(args.config): sha(args.config),
                 config["hmd"]: sha(config["hmd"])}
    protected.update({str(p): sha(p) for p in Path(config["taxonomy_root"]).rglob("*") if p.is_file()})
    nodes, facts, sources = build(view, config, hmd, namespaces, dims)
    if sha(input_path) != view["sha256"]:
        raise ValueError("View input changed during processing")
    instances = emit(view, config, namespaces, dims, nodes, facts, args.output, args.output_profiles)
    save_json(args.output / "SOURCE_TO_FACTS.json", sources)
    save_json(args.output / "VIEW_HMD_COMPARISON.json", comparisons)
    save_json(args.output / "INPUT_SHA256.json", protected)
    results = validate(args.arelle, instances, args.output, [p for p in args.validate_profiles if p in args.output_profiles]) if args.arelle else []
    unchanged = all(sha(path) == digest for path, digest in protected.items())
    save_json(args.output / "SUMMARY.json", {"facts": len(facts), "source_cells": len(sources),
                                            "class_occurrences": len(nodes), "originals_unchanged": unchanged,
                                            "validation": [r["result"] for r in results]})
    print(json.dumps({"facts": len(facts), "originals_unchanged": unchanged, "validation": [r["result"] for r in results]}))
    return 0 if unchanged and all(r["result"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(f"HOLD: {exc}", file=sys.stderr)
        sys.exit(2)

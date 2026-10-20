#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Serialise class-occurrence rows with one fact column per selected property."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path


def emit_structured_oim(view, config, namespaces, dimensions, nodes, facts, out):
    path = Path(out) / "oim" / (config.get("oim_basename", "accountingEntries-view1") + ".json")
    attributes = [r for r in view["rows"] if r["type"] == "A"]
    classes = sorted((r for r in view["rows"] if r["type"] == "C"), key=lambda r: int(r["sequence"]))
    dimrows = [r for r in classes if f"d_{r['module']}_{r['local_name']}" in dimensions]
    omitted_dimrows = [r for r in dimrows if r["module"] == "bus" and r["local_name"] == "partyWebSite"]
    dimrows = [r for r in dimrows if r not in omitted_dimrows]
    view_definition = json.loads(Path(config["view_definition"]).read_text(encoding="utf-8"))
    row_mode = config.get("view_row_mode", "aggregate")
    if row_mode not in ("separate", "aggregate"):
        raise ValueError("Unsupported View row mode")
    actual_hmd_sha = hashlib.sha256(Path(config["hmd"]).read_bytes()).hexdigest()
    if actual_hmd_sha.lower() != view_definition["hmd_sha256"].lower():
        raise ValueError("View definition/HMD version mismatch")
    class_by_path = {r["semantic_path"]: r for r in classes}
    rule_evidence = []
    for rule in view_definition["rules"]:
        source, target = class_by_path[rule["sourceRef"]], class_by_path[rule["targetRef"]]
        if source["parent"] != target["semantic_path"] or rule["maxOccurrencesPerTarget"] != 1:
            raise ValueError("Unsupported or invalid targetRef compaction rule")
        if rule["occurrenceDimension"] != f"plt:d_{source['module']}_{source['local_name']}":
            raise ValueError("View occurrence dimension disagrees with source class")
        expected_column = "d" + source["local_name"][0].upper() + source["local_name"][1:]
        if rule["omitColumn"] != expected_column or source not in dimrows:
            raise ValueError("View physical column/reference mismatch")
        counts = []
        for target_key, node in nodes.items():
            if node["row"]["semantic_path"] == target["semantic_path"]:
                count = sum(n["parent"] == target_key and n["row"]["semantic_path"] == source["semantic_path"]
                            for n in nodes.values())
                if count > 1 and row_mode == "aggregate":
                    raise ValueError(f"Repeated source class cannot be compacted: {rule['sourceRef']}")
                counts.append({"target_occurrence": target_key, "count": count})
        rule_evidence.append({"sourceRef": rule["sourceRef"], "targetRef": rule["targetRef"], "counts": counts})
        if row_mode == "aggregate":
            omitted_dimrows.append(source)
            dimrows.remove(source)
    Path(out).mkdir(parents=True, exist_ok=True)
    with (Path(out) / "TARGET_REF_CHECKS.json").open("x", encoding="utf-8", newline="\n") as f:
        json.dump(rule_evidence, f, ensure_ascii=False, indent=2)
        f.write("\n")
    dimension_columns = {}
    for r in dimrows:
        label = "d" + r["local_name"][0].upper() + r["local_name"][1:]
        if label in dimension_columns:
            label = r["module"] + "_" + label
        dimension_columns[label] = (r["semantic_path"], f"plt:d_{r['module']}_{r['local_name']}")
    property_columns = {}
    for r in attributes:
        name = r["local_name"]
        if sum(a["local_name"] == name for a in attributes) > 1 or name in dimension_columns:
            name = r["module"] + "_" + name
        if name in property_columns:
            raise ValueError("Ambiguous physical fact column name")
        property_columns[name] = r
    headers = list(dimension_columns) + list(property_columns)
    rows = []
    trace = []
    def visit(key):
        direct = [f for f in facts.values() if f["node"] == key]
        if direct:
            record = {name: "" for name in headers}
            lineage = dict(key)
            for label, (semantic_path, _) in dimension_columns.items():
                if semantic_path in lineage:
                    record[label] = lineage[semantic_path]
            for fact in direct:
                label = next(name for name, r in property_columns.items() if r["semantic_path"] == fact["row"]["semantic_path"])
                value = fact["value"]
                record[label] = "#" + value if value.startswith("#") else "#empty" if value == "" else value
            rows.append(record)
            trace.append({"csv_row": len(rows) + 1, "class_semantic_path": nodes[key]["row"]["semantic_path"],
                          "class_occurrences": key, "source_cells": [c for f in direct for c in f["cells"]]})
        children = sorted((k for k, n in nodes.items() if n["parent"] == key),
                          key=lambda k: int(nodes[k]["row"]["sequence"]))
        for child in children:
            visit(child)
    for key in nodes:
        if len(key) == 1:
            visit(key)
    # Coalesce compatible rows with the same remaining occurrence keys.
    merged, origins = {}, {}
    for record, origin in zip(rows, trace):
        key = tuple(record[d] for d in dimension_columns)
        if key not in merged:
            merged[key] = dict(record)
            origins[key] = []
        else:
            for label in property_columns:
                old, new = merged[key][label], record[label]
                if old and new and old != new:
                    raise ValueError(f"Conflicting values while merging {label}")
                if new:
                    merged[key][label] = new
        origins[key].append(origin)
    rows = list(merged.values())
    trace = [{"csv_row": i + 2, "source_occurrence_rows": origins[key]}
             for i, key in enumerate(merged)]
    columns = {name: {} for name in dimension_columns}
    for label, r in property_columns.items():
        dims = {"concept": f"{r['module']}:{r['local_name']}"}
        # A column may omit a physical occurrence key only when all its
        # facts share one actual key; keep that key on this fact column alone.
        for cls in omitted_dimrows:
            if r["semantic_path"].startswith(cls["semantic_path"] + "."):
                values = {dict(f["node"])[cls["semantic_path"]] for f in facts.values()
                          if f["row"]["semantic_path"] == r["semantic_path"]}
                if len(values) != 1:
                    raise ValueError("Omitted occurrence column does not have one fixed source key")
                dims[f"plt:d_{cls['module']}_{cls['local_name']}"] = next(iter(values))
        column = {"dimensions": dims}
        if r["datatype"] in ("Monetary", "Pure", "Decimal", "Integer", "Float", "Double"):
            if r["datatype"] == "Monetary":
                dims["unit"] = "iso4217:" + config["currency"]
            column["decimals"] = "#none" if config["decimals"] == "INF" else int(config["decimals"])
        columns[label] = column
    namespaces = dict(namespaces)
    namespaces["ent"] = config["entity_scheme"]
    metadata = {
        "documentInfo": {"documentType": "https://xbrl.org/2021/xbrl-csv", "namespaces": namespaces,
                         "taxonomy": [os.path.relpath(config["oim_entry"], path.parent).replace("\\", "/")]},
        "dimensions": {"entity": "ent:" + config["entity_identifier"], "period": config["instant"]},
        "tableTemplates": {"structured": {"columns": columns,
                            "dimensions": {qname: "$" + label for label, (_, qname) in dimension_columns.items()}}},
        "tables": {"structured": {"template": "structured", "url": path.with_suffix(".csv").name}},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    with path.with_suffix(".csv").open("x", encoding="utf-8", newline="") as f:
        f.write(buffer.getvalue())
    for destination, data in ((path, metadata), (Path(out) / "STRUCTURED_ROW_TRACE.json", trace)):
        with destination.open("x", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

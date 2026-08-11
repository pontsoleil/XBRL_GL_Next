#!/usr/bin/env python3
# coding: utf-8
"""
xBRLGL_TaxonomyGenerator.py

This script generate XBRL GL Taxonomy.

designed by SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)
written by SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)

Creation Date: 2025-04-03
Last Modified: 2026-08-11

2026-08-08 revised-to-formal integration:
    The input contract is the formal 18-column HMD generated and validated by
    Post-Graph Walk.  The HMD ``xpath`` is the authority for physical
    hierarchy and its terminal step supplies the element QName.  ``module``
    and ``local_name`` are consistency checks for that resolved QName.
    Reconstruction of XPath from ``level + module + local_name`` was removed.
    Multiple-HMD input, shared-QName integration, input-order independence and
    non-zero error exits are retained. ``source_bsm_id`` is provenance only.
    Rows whose
    reviewed multiplicity is ``0..0`` and structural subtrees below such rows
    remain in the input CSV but are excluded from generated taxonomy content.

2026-08-11 LHM for taxonomy input set:
    This is the first-edition formal input contract. Taxonomy generation accepts
    exactly one ``LHM_for_taxonomy`` directory and discovers the formal 18-column
    HMD-for-taxonomy CSV files contained directly in that directory.
    ``manifest.csv`` is an execution-confirmation artefact only: it is neither
    required nor read by the generator and does not determine taxonomy content.
    HMD inputs are validated by their formal column contract and single-root
    identity, then processed in deterministic root-identifier order. Direct HMD
    CSV input, standalone Tuple generation and standalone OIM generation are not
    part of this edition and are not accepted by the CLI.

2026-08-11 HMD package layout:
    Formal package output separates shared module declarations from HMD-bound
    entry points.  Shared schemas, presentation linkbases and labels are
    written once below the package root.  Tuple and OIM entry points are
    written below ``tuple/<root-module>_<root-local-name>`` and
    ``oim/<root-module>_<root-local-name>`` respectively.  HMD-level artefacts
    use the root module prefix plus ``all``: for example ``btx-all-<V>.xsd``
    and ``btx-all-pre-<V>.xml`` for Tuple, and ``btx-all-oim-<V>.xsd``,
    ``btx-all-dim-<V>.xml`` and ``btx-all-pre-<V>.xml`` for OIM.  This layout
    keeps the choice of Tuple versus OIM explicit without duplicating shared
    concept declarations.

2026-08-11 HMD presentation extensions:
    The former top-level ``presentation/<HMD>`` directory is abolished.
    Shared module presentation linkbases remain the base network.  Each
    Tuple HMD writes its deterministic difference linkbase directly below
    ``tuple/<HMD>`` as ``<prefix>-all-pre-<V>.xml``; each OIM HMD writes its
    own binding-specific presentation linkbase below ``oim/<HMD>`` with the
    same ``<prefix>-all-pre-<V>.xml`` naming convention.

2026-08-09 Palette declaration/type separation:
    Shared module schemas contain only reusable item declarations and their
    QName-derived ItemTypes.  HMD-specific content schemas contain Tuple C/R
    declarations and structural ComplexTypes.  OIM entry points use h_, d_
    and p_ concepts plus the reusable item modules and never discover Tuple
    content schemas.  A Tuple structural QName is therefore resolved only in
    its selected HMD DTS, while every item QName is valid in both bindings.

2026-08-09 XMLSpy Tuple validation compatibility:
    Every HMD-specific content schema directly imports the XBRL 2.1 instance
    schema used by its ``xbrli:tuple`` substitution-group references.  The
    generator no longer relies on the same-namespace included module schema
    to make that external namespace visible to schema validators.

2026-08-10 binding-specific HMD presentation:
    Tuple and OIM entry points discover separate HMD presentation linkbases.
    The OIM presentation reuses the dimensional domain-member concept
    resolution: a Class is represented by its ``p_`` primary item, an
    Attribute by the shared module element, and an Association is traversed
    transparently.  OIM presentation locators never discover Tuple content
    schemas.

MIT License

(c) 2025 SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse
import os
import sys
import csv
import json
import re
import glob
import shutil
import tempfile
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

TRACE = False
DEBUG = False

PRESENTATION_ROLE = "http://www.xbrl.org/2003/role/link"
PARENT_CHILD_ARCROLE = "http://www.xbrl.org/2003/arcrole/parent-child"

FORMAL_HMD_HEADER = [
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


def _formal_hmd_identity(path, encoding="utf-8-sig"):
    """Return the single formal root identifier for one HMD CSV.

    The HMD itself is the taxonomy-generation input.  File names and any
    execution-confirmation manifest do not determine the HMD identity.
    """
    path = Path(path)
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        actual_header = [
            name.lstrip("\ufeff") for name in (reader.fieldnames or [])
        ]
        if actual_header != FORMAL_HMD_HEADER:
            raise ValueError(
                f"Formal HMD header mismatch in {path.name!r}. "
                f"Expected {FORMAL_HMD_HEADER!r}, got {actual_header!r}."
            )
        roots = []
        for raw in reader:
            if not any((value or "").strip() for value in raw.values()):
                continue
            row = {
                (key or "").lstrip("\ufeff"): (value or "").strip()
                for key, value in raw.items()
            }
            if row.get("level") != "1":
                continue
            if row.get("type") != "C":
                raise ValueError(
                    f"Formal HMD level-1 row must be Class (C) in {path.name!r}."
                )
            module = row.get("module", "")
            local_name = row.get("local_name", "")
            if not module or not local_name:
                raise ValueError(
                    f"Formal HMD root module/local_name is blank in {path.name!r}."
                )
            roots.append(f"{module}_{local_name}")
    if len(roots) != 1:
        raise ValueError(
            f"Each HMD for taxonomy must contain exactly one level-1 root; "
            f"found {len(roots)} in {path.name!r}."
        )
    return roots[0]


def resolve_lhm_for_taxonomy_input(lhm_for_taxonomy_dir, encoding="utf-8-sig"):
    """Discover formal HMD inputs from one ``LHM_for_taxonomy`` directory.

    ``manifest.csv`` may coexist in the directory as an execution-confirmation
    artefact, but it is intentionally ignored.  The HMD CSVs themselves are
    the sole taxonomy-generation inputs.
    """
    value = str(lhm_for_taxonomy_dir).strip()
    if not value:
        raise ValueError("LHM_for_taxonomy directory is required.")

    input_dir = Path(file_path(value)).resolve()
    if not input_dir.is_dir():
        raise ValueError(
            "Formal taxonomy generation requires one LHM_for_taxonomy directory; "
            f"got {input_dir}."
        )

    candidates = sorted(
        path for path in input_dir.glob("*.csv")
        if path.name.casefold() != "manifest.csv"
    )
    if not candidates:
        raise ValueError(
            f"LHM_for_taxonomy contains no HMD-for-taxonomy CSV files: {input_dir}"
        )

    resolved = []
    seen_identifiers = set()
    for candidate in candidates:
        identifier = _formal_hmd_identity(candidate, encoding)
        folded = identifier.casefold()
        if folded in seen_identifiers:
            raise ValueError(
                f"Duplicate HMD root identifier in LHM_for_taxonomy: {identifier}"
            )
        seen_identifiers.add(folded)
        resolved.append((folded, identifier, str(candidate.resolve())))

    return [item[2] for item in sorted(resolved)]


@dataclass(frozen=True, order=True)
class PresentationRelationship:
    """One effective presentation relationship and its non-exempt attributes."""

    link_role: str
    arcrole: str
    parent_id: str
    child_id: str
    order: int
    preferred_label: str = ""
    priority: int = field(default=0, compare=False)

    @property
    def pair_key(self):
        return self.link_role, self.arcrole, self.parent_id, self.child_id


@dataclass(frozen=True)
class PresentationDifference:
    """Difference between a shared module network and one HMD network."""

    prohibited: tuple
    optional: tuple
    override_count: int

def file_path(pathname):
    _pathname = pathname.replace("/", os.sep)
    if os.sep == _pathname[0]:
        return _pathname
    dir = os.path.dirname(__file__)
    return os.path.join(dir, _pathname)

class xBRLGL_TaxonomyGenerator:
    def __init__(
            self, 
            in_file,
            base_dir,
            palette,
            root,
            lang,
            currency,
            namespace,
            encoding,
            trace,
            debug,
            instance,
            taxonomy_type,
        ):

        self.palette = palette
        self.TRACE = trace
        self.DEBUG = debug
        self.INSTANCE = instance
        self.taxonomy_type = taxonomy_type

        self.root = root.strip() if root else None
        self.lang = lang.strip() if lang else "ja"
        self.currency = currency.strip().upper() if currency else "JPY"
        self.namespace = namespace.strip() if namespace else 'http://www.xbrl.org/xbrl-gl"'
        self.version = self.namespace[-10:]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.version):
            self.error_print(
                "Namespace must end in an explicit YYYY-MM-DD version date; "
                f"got {self.namespace!r}."
            )
        self.encoding = encoding.strip() if encoding else "utf-8-sig"

        self.records = []
        self.presentation_dict = OrderedDict()
        self.dimension_dict = OrderedDict()
        self.parent_dict = OrderedDict()
        self.element_dict = OrderedDict()
        self.role_map = OrderedDict()

        self.lines = None
        self.locs_defined = None
        self.arcs_defined = None

        if in_file:
            self.core_file = file_path(in_file.strip())
        else:
            print(f"INFO: Input ADC definition CSV file {self.core_file} is missing.")
            raise SystemExit(1)
        if not os.path.isfile(self.core_file):
            print(f"INFO: Input ADC definition CSV file {self.core_file} does not exist.")
            raise SystemExit(1)

        if not base_dir:
            base_dir = ""
        self.base_dir = file_path(base_dir.strip())
        if not os.path.isdir(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)
            print(f"INFO: Created output base directory: {self.base_dir}")

        self.xbrl_base = self.base_dir
        if not os.path.isdir(self.xbrl_base):
            os.makedirs(self.xbrl_base, exist_ok=True)
            print(f"INFO: Created output base directory: {self.xbrl_base}")

    def debug_print(self, message):
        if self.DEBUG:
            print(f"DEBUG: {message}")

    def trace_print(self, message):
        if self.TRACE or self.DEBUG:
            print(f"TRACE: {message}")

    def ensure_gl_gen_schema(self):
        gen_dir = os.path.join(self.xbrl_base, "gen")
        os.makedirs(gen_dir, exist_ok=True)
        target = os.path.join(gen_dir, f"gl-gen-{self.version}.xsd")
        if os.path.isfile(target):
            return target

        candidates = [
            os.path.join(gen_dir, "gl-gen-*.xsd"),
            os.path.join(os.path.dirname(__file__), "taxonomy", "gen", "gl-gen-*.xsd"),
            os.path.join(os.path.dirname(__file__), "gl", "gen", "gl-gen-*.xsd"),
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "taxonomy",
                "gen",
                "gl-gen-*.xsd",
            ),
        ]
        source = None
        for pattern in candidates:
            matches = sorted(path for path in glob.glob(pattern) if os.path.isfile(path))
            if matches:
                source = matches[-1]
                break
        if not source:
            self.error_print(
                "Required gl-gen schema source was not found. "
                "Place gl-gen-*.xsd in the output gen directory or in "
                "taxonomy/gen before generation."
            )

        with open(source, "r", encoding=self.encoding) as f:
            text = f.read()
        text = re.sub(r"gl-gen-\d{4}-\d{2}-\d{2}\.xsd", f"gl-gen-{self.version}.xsd", text)
        text = text.replace("2026-MM-DD", self.version)
        text = re.sub(r"/gen/\d{4}-\d{2}-\d{2}", f"/gen/{self.version}", text)
        with open(target, "w", encoding=self.encoding, newline="") as f:
            f.write(text)
        self.trace_print(f"-- {target}")
        return target

    def gl_gen_schema_location(self, from_directory):
        target = self.ensure_gl_gen_schema()
        return os.path.relpath(target, from_directory).replace(os.sep, "/")

    def concept_item_type(self, record):
        element_type = record["element_type"]
        matches = [x for x in self.gen_types if element_type.endswith(x)]
        if matches:
            match = matches[0]
            return f"gen:{match[0].lower() + match[1:]}"
        return record.get("datatype") or "xbrli:stringItemType"

    def error_print(self, text):
        print(f"** ERROR: {text}")
        raise SystemExit(1)

    # lower camel case concatenate
    def LC3(self, term):
        if not term:
            return ""
        terms = term.split(" ")
        name = ""
        for i in range(len(terms)):
            if i == 0:
                if "TAX" == terms[i]:
                    name += terms[i].lower()
                elif len(terms[i]) > 0:
                    name += terms[i][0].lower() + terms[i][1:]
            else:
                name += terms[i][0].upper() + terms[i][1:]
        return name

    def titleCase(self, text):
        text = text.replace("ID", "Identification Identifier")
        # Example Camel case string
        camel_case_str = text  # "exampleCamelCaseString"
        # Use regular expression to split the string at each capital letter
        split_str = re.findall("[A-Z][a-z]*[_]?", camel_case_str)
        # Join the split string with a space and capitalize each word
        title_case_str = " ".join([x.capitalize() for x in split_str])
        title_case_str = title_case_str.replace("Identification Identifier", "ID")
        return title_case_str

    # snake concatenate
    def SC(self, term):
        if not term:
            return ""
        terms = term.split(" ")
        name = "_".join(terms)
        return name

    def getRecord(self, element_id, abbreviation_path=None):
        if abbreviation_path:
            candidate = self.getRecord(element_id)
            if candidate:
                return candidate
            element_id = f"{abbreviation_path}_{element_id}"
        if "$." in element_id:
            record = next((x for x in self.records if element_id == x["semantic_path"]), None)
            if not record:
                record = next((x for x in self.records if x["semantic_path"].endswith(element_id)), None)
        else:
            record = next((x for x in self.records if element_id == x["abbreviation_path"]), None)
            if not record:
                record = next((x for x in self.records if x["abbreviation_path"].endswith(element_id)), None)
            if not record:
                record = next((x for x in self.records if x["element_id"]==element_id), None)
            if not record:
                record = next((x for x in self.records if x["element"]==element_id), None)
            if not record:
                record = next((x for x in self.records if f"$.{element_id}" == x["semantic_path"]), None)
        return record

    def getParent(self, element_id):
        if element_id in self.parent_dict:
            parent = self.parent_dict[element_id]
        else:
            parent = None
        return parent

    def getChildren(self, element_id):
        record = self.getRecord(element_id)
        if record:
            return record["children"]
        return []

    def getElementID(self, cor_id):
        record = self.getRecord(cor_id)
        if record:
            return record["element_id"]
        return None

    def domainMember(self, children, primary_id, abbreviation_path = None):
        # global count
        lines = []
        for _child_element_id in children: # children are abbrebiated name list
            if not _child_element_id:
                continue
            child = self.getRecord(_child_element_id, abbreviation_path)
            if not child:
                continue
            child_element_id = child['element_id']
            if not child_element_id:
                continue
            child_type = child["type"]
            child_name = child["name"]
            if "R" == child_type:
                # An LHM Association row is a Tuple structural element, but
                # not an OIM fact.  Traverse it transparently so its
                # attributes remain in the current cube and any descendant
                # Classes become targetRole-linked child cubes.
                lines += self.domainMember(
                    self.presentation_dict.get(child_element_id, []),
                    primary_id,
                    child["abbreviation_path"],
                )
                continue
            taxonomy_schema, link_id, href = self.roleRecord(child_element_id)
            if "C" == child_type:
                target_id = self.oim_presentation_concept_id(child)
                target_name = child_element_id #[1+child_element_id.index('-'):]
                target_link = f"link_{target_name}"
                self.debug_print(
                    f'domain-member: {primary_id} to {target_id} {child["name"]} order={self.count} in {target_link} targetRole="http://www.xbrl.org/xbrl-gl/role/{target_link}'
                )
                lines.append(f"    <!-- {primary_id} to targetRole {target_link} -->\n")
                if primary_id not in self.locs_defined:
                    self.locs_defined[primary_id] = set()
                if not target_id in self.locs_defined[primary_id]:
                    self.locs_defined[primary_id].add(target_id)
                    lines.append(
                        f'    <link:loc xlink:type="locator" xlink:href="plt-oim-{self.version}.xsd#{target_id}" xlink:label="{target_id}" xlink:title="{target_id} {child_name}"/>\n'
                    )
                self.count += 1
                arc_id = f"{primary_id} TO {target_link}"
                if primary_id not in self.arcs_defined:
                    self.arcs_defined[primary_id] = set()
                if not arc_id in self.arcs_defined[primary_id]:
                    self.arcs_defined[primary_id].add(arc_id)
                    lines.append(
                        f'    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xbrldt:targetRole="http://www.xbrl.org/xbrl-gl/role/{target_link}" xlink:from="{primary_id}" xlink:to="{target_id}" xlink:title="domain-member: {primary_id} to {target_id} in {target_link}" order="{self.count}"/>\n'
                    )
            else:
                target_id = self.oim_presentation_concept_id(child)
                self.debug_print(f'domain-member: {primary_id} to {target_id} {child["name"]} order={self.count}')
                if primary_id not in self.locs_defined:
                    self.locs_defined[primary_id] = set()
                if target_id not in self.locs_defined[primary_id]:
                    self.locs_defined[primary_id].add(target_id)
                    lines.append(
                        f'    <link:loc xlink:type="locator" xlink:href="{taxonomy_schema}#{target_id}" xlink:label="{target_id}" xlink:title="{target_id} {child_name}"/>\n'
                    )
                self.count += 1
                arc_id = f"{primary_id} TO {target_id}"
                if primary_id not in self.arcs_defined:
                    self.arcs_defined[primary_id] = set()
                if arc_id not in self.arcs_defined[primary_id]:
                    self.arcs_defined[primary_id].add(arc_id)
                    lines.append(
                        f'    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="{primary_id}" xlink:to="{target_id}" xlink:title="domain-member: {primary_id} to {target_id} {child["name"]}" order="{self.count}"/>\n'
                    )
        return lines

    @staticmethod
    def oim_presentation_concept_id(record):
        """Resolve one HMD row to the concept used by OIM networks.

        This is the shared binding rule used by the dimensional
        domain-member and OIM presentation networks.  C rows become ``p_``
        primary items, A rows retain their shared module element, and R rows
        are transparent structural traversal nodes.
        """
        if record["type"] == "C":
            return f'p_{record["element_id"]}'
        if record["type"] == "A":
            return record["element_id"]
        if record["type"] == "R":
            return None
        raise ValueError(f'Unsupported HMD row type: {record["type"]!r}')

    def defineHypercube(self, root):
        dimension_id_list = []
        taxonomy_schema, link_id, href = self.roleRecord(root['element_id'])
        for schema_id in root.get("class_ancestors", [root["element_id"]]):
            if schema_id not in self.roleMap:
                continue
            dimension_id = f"d_{schema_id}"
            if dimension_id not in dimension_id_list:
                dimension_id_list.append(dimension_id)
        element_id = f"{link_id[5:]}"
        self.locs_defined[link_id] = set()
        self.arcs_defined[link_id] = set()
        primary_name = element_id#[1+element_id.index('-'):]
        hypercube_id = f"h_{primary_name}"
        primary_id = f"p_{primary_name}"
        self.lines += [
            f'  <link:definitionLink xlink:type="extended" xlink:role="http://www.xbrl.org/xbrl-gl/role/{link_id}">\n',
            # all (has-hypercube)
            f"    <!-- {primary_id} all (has-hypercube) {hypercube_id} {link_id} -->\n",
            f'    <link:loc xlink:type="locator" xlink:href="plt-oim-{self.version}.xsd#{primary_id}" xlink:label="{primary_id}" xlink:title="{primary_id}"/>\n',
            f'    <link:loc xlink:type="locator" xlink:href="plt-oim-{self.version}.xsd#{hypercube_id}" xlink:label="{hypercube_id}" xlink:title="{hypercube_id}"/>\n',
            f'    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/all" xlink:from="{primary_id}" xlink:to="{hypercube_id}" xlink:title="all (has-hypercube): {primary_id} to {hypercube_id}" order="1" xbrldt:closed="true" xbrldt:contextElement="segment"/>\n',
        ]
        self.debug_print(f"all(has-hypercube) {primary_id} to {hypercube_id} ")
        # hypercube-dimension
        self.lines.append("    <!-- hypercube-dimension -->\n")
        self.count = 0
        for dimension_id in dimension_id_list:
            self.lines.append(
                f'    <link:loc xlink:type="locator" xlink:href="plt-oim-{self.version}.xsd#{dimension_id}" xlink:label="{dimension_id}" xlink:title="{dimension_id}"/>\n'
            )
            self.count += 1
            self.lines.append(
                f'    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:from="{hypercube_id}" xlink:to="{dimension_id}" xlink:title="hypercube-dimension: {hypercube_id} to {dimension_id}" order="{self.count}"/>\n'
            )
            self.debug_print(f"hypercube-dimension {hypercube_id} to {dimension_id} ")
        # domain-member
        self.lines.append("    <!-- domain-member -->\n")
        element_id = root['element_id']
        record = next((x for x in self.records if element_id == x["element_id"]), None)
        abbreviation_path = record['abbreviation_path']
        dimension = self.dimension_dict[abbreviation_path]
        if 'children' in dimension:
            children = dimension["children"]
            self.lines += self.domainMember(children, primary_id, abbreviation_path)
        self.lines.append("  </link:definitionLink>\n")

    def roleRecord(self, _element_id):
        record = self.getRecord(_element_id)
        element_id = record["element_id"]
        module = element_id[:element_id.index("_")]
        taxonomy_schema = f"../{module}/{module}-{self.version}.xsd"
        link_id = f"link_{element_id}"
        href = f"{taxonomy_schema}/{link_id}"
        return taxonomy_schema, link_id, href

    def linkPresentation(self, _module, element_id, children, n):
        if not element_id:
            return
        order = 0
        record = next((x for x in self.records if element_id == x["element_id"]), None)
        if not record:
            return
        module = element_id[: element_id.index("_")]
        name = record["name"]
        if not element_id in self.locs_defined:
            self.locs_defined[element_id] = name
            self.lines.append(f"    <!-- {name} -->\n")
            if _module==module:
                self.lines.append(
                    f'    <loc xlink:type="locator" xlink:href="{module}-{self.version}.xsd#{element_id}" xlink:label="{element_id}" xlink:title="loc: {element_id}"/>\n'
                )
            else:
                self.lines.append(
                    f'    <loc xlink:type="locator" xlink:href="../{module}/{module}-{self.version}.xsd#{element_id}" xlink:label="{element_id}" xlink:title="loc: {element_id}"/>\n'
                )
        for child_element_id in children:
            if not child_element_id:
                continue
            child = next((x for x in self.records if child_element_id == x["element_id"]), None)
            if not child:
                continue
            child_module = child_element_id[:child_element_id.index("_")]
            child_name = child["name"]
            order += 10
            arc_id = f"{element_id} to {child_element_id}"
            if arc_id not in self.arcs_defined:
                self.arcs_defined[arc_id] = f"presentation: {element_id} to {child_element_id}"
                if _module==child_module:
                    self.lines += [
                        f'    <loc xlink:type="locator" xlink:href="{child_module}-{self.version}.xsd#{child_element_id}" xlink:label="{child_element_id}" xlink:title="presentation: {element_id} to {child_element_id} {child_name}"/>\n',
                        f'    <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="{element_id}" xlink:to="{child_element_id}" xlink:title="presentation: {element_id} to {child_element_id}" use="optional" order="{order}"/>\n',
                    ]
                else:
                    self.lines += [
                        f'    <loc xlink:type="locator" xlink:href="../{child_module}/{child_module}-{self.version}.xsd#{child_element_id}" xlink:label="{child_element_id}" xlink:title="presentation: {element_id} to {child_element_id} {child_name}"/>\n',
                        f'    <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="{element_id}" xlink:to="{child_element_id}" xlink:title="presentation: {element_id} to {child_element_id}" use="optional" order="{order}"/>\n',
                    ]
            if child_element_id in self.presentation_dict:
                grand_children = self.presentation_dict[child_element_id]
                if n > 10:
                    self.error_print(f"linkPresentation exceeds depth {n}")
                self.linkPresentation(_module, child_element_id, grand_children, n + 1)
        children = None

    @staticmethod
    def escape_text(text):
        if not text:
            return ""
        escaped = text.replace("&", "&amp;")
        escaped = escaped.replace("<", "&lt;")
        escaped = escaped.replace(">", "&gt;")
        return escaped

    def module_namespace(self, module):
        return f"http://www.xbrl.org/int/gl/{module}/{self.version}"

    def parse_hmd_xpath(self, xpath):
        """Resolve the formal HMD XPath to ordered expanded QNames."""
        root = "/xbrli:xbrl"
        if not xpath.startswith(root + "/"):
            self.error_print(
                f"Formal HMD xpath must start with {root + '/'!r}: {xpath!r}"
            )
        lexical_steps = xpath[len(root) + 1 :].split("/")
        ncname = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")
        resolved = []
        for lexical_qname in lexical_steps:
            if lexical_qname.count(":") != 1:
                self.error_print(
                    f"Formal HMD xpath step must be a lexical QName: "
                    f"{lexical_qname!r} in {xpath!r}"
                )
            prefix, local_name = lexical_qname.split(":", 1)
            if not ncname.fullmatch(prefix) or not ncname.fullmatch(local_name):
                self.error_print(
                    f"Invalid QName step {lexical_qname!r} in formal HMD "
                    f"xpath {xpath!r}."
                )
            if not prefix.startswith("gl-") or len(prefix) == 3:
                self.error_print(
                    f"Unsupported formal HMD xpath prefix {prefix!r}."
                )
            module = prefix[3:]
            namespace = self.module_namespace(module)
            resolved.append(
                {
                    "lexical": lexical_qname,
                    "module": module,
                    "local_name": local_name,
                    "namespace": namespace,
                    "expanded_name": f"{{{namespace}}}{local_name}",
                    "element": f"{module}:{local_name}",
                }
            )
        return resolved

    def normalize_lhm_record(self, raw):
        record = {}
        for key, value in raw.items():
            if not key:
                continue
            name = key.lstrip("\ufeff")
            if name in {"definition", "definition_local"}:
                record[name] = "" if value is None else str(value)
            else:
                record[name] = (value or "").strip()

        module = record["module"]
        local_name = record["local_name"]
        ncname = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")
        if not ncname.fullmatch(module):
            self.error_print(f"Invalid HMD module: {module!r}")
        if not ncname.fullmatch(local_name) or ":" in local_name:
            self.error_print(f"Invalid HMD local_name: {local_name!r}")
        xpath_steps = self.parse_hmd_xpath(record["xpath"])
        terminal = xpath_steps[-1]
        expected_namespace = self.module_namespace(module)
        if terminal["namespace"] != expected_namespace:
            self.error_print(
                f"Formal HMD xpath terminal namespace {terminal['namespace']!r} "
                f"does not match module {module!r} namespace "
                f"{expected_namespace!r}."
            )
        if terminal["local_name"] != local_name:
            self.error_print(
                f"Formal HMD xpath terminal local part "
                f"{terminal['local_name']!r} does not match local_name "
                f"{local_name!r}."
            )
        # QName identity comes from the resolved terminal XPath step.  The
        # source_bsm_id and display name do not participate in identity.
        record["element"] = terminal["element"]
        record["expanded_name"] = terminal["expanded_name"]
        record["xpath_steps"] = xpath_steps
        record["physical_path_key"] = "/".join(
            step["expanded_name"] for step in xpath_steps
        )
        record["parent_path_key"] = "/".join(
            step["expanded_name"] for step in xpath_steps[:-1]
        )

        semantic_path = record["semantic_path"]
        record["abbreviation_path"] = record["physical_path_key"]
        record["instance"] = "o"
        record["lhm_level"] = ""
        return record

    def load_csv_data(self):
        # ====================================================================
        # 1. csv -> schema
        self.records = []
        self.dimension_dict = OrderedDict()
        self.parent_dict = OrderedDict()
        self.presentation_dict = OrderedDict()

        header = FORMAL_HMD_HEADER
        datatype_map = {
            "DECIMAL": "xbrli:decimalItemType",
            "FLOAT": "xbrli:floatItemType",
            "DOUBLE": "xbrli:doubleItemType",
            "INTEGER": "xbrli:integerItemType",
            "NONPOSITIVEINTEGER": "xbrli:nonPositiveIntegerItemType",
            "NEGATIVEINTEGER": "xbrli:negativeIntegerItemType",
            "LONG": "xbrli:longItemType",
            "INT": "xbrli:intItemType",
            "SHORT": "xbrli:shortItemType",
            "BYTE": "xbrli:byteItemType",
            "NONNEGATIVEINTEGER": "xbrli:nonNegativeIntegerItemType",
            "UNSIGNEDLONG": "xbrli:unsignedLongItemType",
            "UNSIGNEDINT": "xbrli:unsignedIntItemType",
            "UNSIGNEDSHORT": "xbrli:unsignedShortItemType",
            "UNSIGNEDBYTE": "xbrli:unsignedByteItemType",
            "POSITIVEINTEGER": "xbrli:positiveIntegerItemType",
            "MONETARY": "xbrli:monetaryItemType",
            "SHARES": "xbrli:sharesItemType",
            "PURE": "xbrli:pureItemType",
            "FRACTION": "xbrli:fractionItemType",
            "STRING": "xbrli:stringItemType",
            "BOOLEAN": "xbrli:booleanItemType",
            "HEXBINARY": "xbrli:hexBinaryItemType",
            "BASE64BINARY": "xbrli:base64BinaryItemType",
            "ANYURI": "xbrli:anyURIItemType",
            "QNAME": "xbrli:QNameItemType",
            "ENUMERATION": "enum:enumerationItemType",
            "DURATION": "xbrli:durationItemType",
            "DATETIME": "xbrli:dateTimeItemType",
            "TIME": "xbrli:timeItemType",
            "DATE": "xbrli:dateItemType",
            "GYEARMONTH": "xbrli:gYearMonthItemType",
            "GYEAR": "xbrli:gYearItemType",
            "GMONTHDAY": "xbrli:gMonthDayItemType",
            "GDAY": "xbrli:gDayItemType",
            "GMONTH": "xbrli:gMonthItemType",
            "NORMALIZEDSTRING": "xbrli:normalizedStringItemType",
            "TOKEN": "xbrli:tokenItemType",
            "LANGUAGE": "xbrli:languageItemType",
            "NAME": "xbrli:NameItemType",
            "NCNAME": "xbrli:NCNameItemType",
            # "anyURI": "xbrli:anyURIItemType",
            # "Boolean": "xbrli:booleanItemType",
            # "Date": "xbrli:dateItemType",
            # "Date Time": "xbrli:dateTimeItemType",
            # "Decimal": "xbrli:decimalItemType",
            # "Integer": "xbrli:integerItemType",
            # "Monetary": "xbrli:monetaryItemType",
            # "NonNegativeInteger": "xbrli:nonNegativeIntegerItemType",
            # "Pure": "xbrli:pureItemType",
            # "QName": "xbrli:QNameItemType",
            # "String": "xbrli:stringItemType",
            # "Token": "xbrli:tokenItemType",
            "": ""
        }
        self.gen_types = [
            "ActiveItemType",
            "AmountItemType",
            "BookTaxDifferenceItemType",
            "DebitCreditCodeItemType",
            "DocumentTypeItemType", # https://service.unece.org/trade/untdid/d23a/tred/tred1001.htm
            "EmailAddressItemType",
            "EmailAddressUsageItemType",
            "EntriesTypeItemType",
            "EntryTypeItemType",
            "FaxNumberItemType",
            "FaxNumberUsageItemType",
            "IdentifierOrganizationTypeItemType",
            "IdentifierTypeItemType",
            "InvoiceTypeItemType",
            "PhoneNumberDescriptionItemType",
            "PhoneNumberItemType",
            "PostingStatusItemType",
            "QualifierEntryItemType",
            "RevisesUniqueIDActionItemType",
            "SignOfAmountItemType",
            "SourceJournalIDItemType",
        ]
        with open(self.core_file, encoding=self.encoding, newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                self.error_print(f"Input LHM CSV file {self.core_file} has no header.")
            actual_header = [name.lstrip("\ufeff") for name in reader.fieldnames]
            if actual_header != header:
                self.error_print(
                    "Input LHM header mismatch. "
                    f"Expected {header!r}, got {actual_header!r}."
                )
            raw_rows = list(reader)
            sem_sort = 1
            class_id = None
            seen_semantic_paths = set()
            excluded_level = None
            qname_definitions = {}
            records_by_physical_path = {}
            for raw in raw_rows:
                if not any((value or "").strip() for value in raw.values()):
                    continue
                record = self.normalize_lhm_record(raw)
                semantic_path = record["semantic_path"]
                abbreviation_path = record["abbreviation_path"]
                if not abbreviation_path:
                    self.error_print("Formal HMD xpath must not be blank.")
                if semantic_path in seen_semantic_paths:
                    self.error_print(f"Duplicate LHM semantic_path: {semantic_path}")
                seen_semantic_paths.add(semantic_path)
                d_level = len(record["xpath_steps"])
                _type = record["type"]
                cor_id = record["xpath_steps"][-1]["local_name"]
                if "C" == _type:
                    class_id = cor_id
                elif _type not in {"R", "A"}:
                    self.error_print(f"Unsupported LHM type: {_type!r}")
                sem_sort = record["sequence"]
                identifier = record["identifier"]
                lhm_level = ""
                try:
                    level = int(record["level"])
                except ValueError:
                    self.error_print(f"Invalid LHM level: {record['level']!r}")
                if level < 1:
                    self.error_print(f"HMD level must be positive: {level}")
                if level != d_level:
                    self.error_print(
                        f"HMD level {level} does not match formal xpath depth "
                        f"{d_level} for {record['xpath']!r}."
                    )
                physical_depth = d_level
                if excluded_level is not None and physical_depth <= excluded_level:
                    excluded_level = None
                object_class = record["class_term"]
                multiplicity = record["multiplicity"]
                if multiplicity not in {"0..0", "1", "0..1", "1..1", "0..*", "1..*"}:
                    self.error_print(f"Unsupported LHM multiplicity: {multiplicity!r}")
                if excluded_level is not None:
                    continue
                if multiplicity == "0..0":
                    excluded_level = physical_depth
                    continue
                name = record["name"]
                element = record["element"]
                element_id = element.replace(":", "_")
                if record["type"] in {"C", "R"}:
                    if record["datatype"]:
                        self.error_print(
                            f"Structural LHM row {element!r} must not have datatype "
                            f"{record['datatype']!r}."
                        )
                    element_type = f"{element}ComplexType"
                elif 'A'==record['type']:
                    element_type = f"{element}ItemType"
                else:
                    continue
                datatype = ''
                if _type in ['A']:
                    datatype_key = record["datatype"].replace(' ','').upper()
                    if not datatype_key or datatype_key not in datatype_map:
                        self.error_print(
                            f"Unknown or blank LHM datatype for {element!r}: "
                            f"{record['datatype']!r}"
                        )
                    datatype = datatype_map[datatype_key]
                definition_signature = (_type, datatype)
                expanded_name = record["expanded_name"]
                previous_signature = qname_definitions.get(expanded_name)
                if (
                    previous_signature is not None
                    and previous_signature != definition_signature
                ):
                    self.error_print(
                        f"Conflicting LHM definitions for QName {element!r}: "
                        f"{previous_signature!r} and {definition_signature!r}."
                    )
                if previous_signature is not None:
                    self.error_print(
                        f"Duplicate effective QName in one formal HMD: "
                        f"{element!r}."
                    )
                qname_definitions[expanded_name] = definition_signature
                xpath = record["xpath"]
                instance = True
                physical_class_ancestors = []
                ancestor_path = record["parent_path_key"]
                while ancestor_path:
                    ancestor_record = records_by_physical_path.get(ancestor_path)
                    if not ancestor_record:
                        self.error_print(
                            f"Cannot resolve formal HMD xpath ancestor "
                            f"{ancestor_path!r} for {xpath!r}."
                        )
                    if ancestor_record["type"] == "C":
                        physical_class_ancestors.insert(
                            0, ancestor_record["element_id"]
                        )
                    ancestor_path = ancestor_record.get("parent_path_key", "")
                data = {
                    "level": level,
                    "lhm_level": lhm_level,
                    "sem_sort": int(sem_sort),
                    "d_level": d_level,
                    "type": _type,
                    "class_id": class_id,
                    "identifier": identifier,
                    "name": name,
                    "datatype": datatype,
                    "element": element,
                    "expanded_name": expanded_name,
                    "element_type": element_type,
                    "element_id": element_id,
                    "object_class": object_class,
                    "multiplicity": multiplicity,
                    "semantic_path": semantic_path,
                    "abbreviation_path": abbreviation_path,
                    "parent_path_key": record["parent_path_key"],
                    "xpath": xpath,
                    "definition": record["definition"],
                    "label_local": record["label_local"],
                    "definition_local": record["definition_local"],
                    "source_bsm_id": record["source_bsm_id"],
                    "id": cor_id,
                    "instance": instance,
                    "class_ancestors": [
                        *physical_class_ancestors
                    ] + ([element_id] if _type == "C" else []),
                }
                parent_path_key = record["parent_path_key"]
                if not parent_path_key:
                    if element_id not in self.presentation_dict:
                        self.presentation_dict[element_id] = []
                else:
                    parent_record = records_by_physical_path.get(parent_path_key)
                    if not parent_record:
                        self.error_print(
                            f"Formal HMD xpath parent is missing or follows its child: "
                            f"{record['xpath']!r}."
                        )
                    parent_id = parent_record["element_id"]
                    data["parent_id"] = parent_id
                    if parent_id not in self.presentation_dict:
                        self.presentation_dict[parent_id] = []
                    if element_id not in self.presentation_dict[parent_id]:
                        self.presentation_dict[parent_id].append(element_id)
                """
                definition link
                """
                is_effective_class = 'C' == data["type"]
                if is_effective_class:
                    d_parent = abbreviation_path
                    self.dimension_dict[d_parent] = {
                        "parent_id": element,
                        "multiplicity": multiplicity,
                        "children": [],
                        "instance": instance,
                    }

                _id = data["abbreviation_path"]
                d_parent = ""
                ancestor_path = parent_path_key
                while ancestor_path:
                    if ancestor_path in self.dimension_dict:
                        d_parent = ancestor_path
                        break
                    ancestor_record = records_by_physical_path.get(ancestor_path)
                    if not ancestor_record:
                        self.error_print(
                            f"Cannot resolve formal HMD xpath ancestor "
                            f"{ancestor_path!r} for {xpath!r}."
                        )
                    ancestor_path = ancestor_record.get("parent_path_key", "")
                data["parent_sem_id"] = d_parent

                if d_parent and _id not in self.dimension_dict[d_parent]["children"]:
                    if _id:
                        self.dimension_dict[d_parent]["children"].append(_id)

                self.records.append(data)
                records_by_physical_path[abbreviation_path] = data

        # Keep C, R and A rows in both bindings.  Tuple uses C/R as physical
        # tuple structures.  OIM does not declare them as module facts, but it
        # still needs them to traverse the LHM and assign descendant
        # attributes to the correct closed cubes and target roles.

    def process_records(self):
        for cor_id, record in list(self.dimension_dict.items()):
            if "children" in record:
                children = record["children"]
                for child_element_id in children:
                    child = self.getRecord(child_element_id)
                    if child and "C" == child["type"]:
                        if child["multiplicity"].endswith("*"):
                            child_element_id = child["element_id"]
                            parent_element_id = self.getElementID(cor_id)
                            self.parent_dict[child_element_id] = parent_element_id

        self.roleMap = {}
        for cor_id, data in self.dimension_dict.items():
            record = self.getRecord(cor_id)
            self.roleMap[record["element_id"]] = record

    @staticmethod
    def occurrence_attributes(multiplicity):
        occurrences = {
            "1": ("1", "1"),
            "1..1": ("1", "1"),
            "0..1": ("0", "1"),
            "0..*": ("0", "unbounded"),
            "1..*": ("1", "unbounded"),
        }
        if multiplicity not in occurrences:
            raise ValueError(f"Unsupported multiplicity: {multiplicity!r}")
        minimum, maximum = occurrences[multiplicity]
        attributes = []
        if minimum != "1":
            attributes.append(f'minOccurs="{minimum}"')
        if maximum != "1":
            attributes.append(f'maxOccurs="{maximum}"')
        return (" " + " ".join(attributes)) if attributes else ""

    def write_tuple_linkbases(self, element_dict, xbrl_base):
        """Write reusable item labels and the shared item presentation base.

        Structural C/R concepts live in HMD content schemas and cannot have a
        reusable locator in a module-level linkbase.  Their HMD presentation
        locators are written by ``write_presentation_extension``.
        """
        for module, data in element_dict.items():
            for language, suffix, label_field, definition_field in (
                ("en", "", "name", "definition"),
                (self.lang, f"-{self.lang}", "label_local", "definition_local"),
            ):
                lines = [
                    '<?xml version="1.0" encoding="UTF-8"?>\n',
                    '<linkbase xmlns="http://www.xbrl.org/2003/linkbase"\n',
                    '  xmlns:xlink="http://www.w3.org/1999/xlink">\n',
                    '  <labelLink xlink:type="extended" '
                    'xlink:role="http://www.xbrl.org/2003/role/link">\n',
                ]
                for record in data:
                    if record["type"] != "A":
                        continue
                    element = record["element"]
                    element_id = element.replace(":", "_")
                    local_name = element.split(":", 1)[1]
                    label = record.get(label_field) or record.get("name") or local_name
                    definition = record.get(definition_field) or ""
                    lines += [
                        f'    <loc xlink:type="locator" '
                        f'xlink:href="../{module}-{self.version}.xsd#{element_id}" '
                        f'xlink:label="loc_{element_id}"/>\n',
                        f'    <label xlink:type="resource" '
                        f'xlink:label="lab_{element_id}" '
                        f'xlink:role="http://www.xbrl.org/2003/role/label" '
                        f'xml:lang="{language}">{self.escape_text(label)}</label>\n',
                        f'    <labelArc xlink:type="arc" '
                        f'xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" '
                        f'xlink:from="loc_{element_id}" '
                        f'xlink:to="lab_{element_id}"/>\n',
                    ]
                    if definition:
                        lines += [
                            f'    <label xlink:type="resource" '
                            f'xlink:label="doc_{element_id}" '
                            f'xlink:role="http://www.xbrl.org/2003/role/documentation" '
                            f'xml:lang="{language}">{self.escape_text(definition)}</label>\n',
                            f'    <labelArc xlink:type="arc" '
                            f'xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" '
                            f'xlink:from="loc_{element_id}" '
                            f'xlink:to="doc_{element_id}"/>\n',
                        ]
                lines += ["  </labelLink>\n", "</linkbase>\n"]
                directory = file_path(f"{xbrl_base}/{module}/lang")
                os.makedirs(directory, exist_ok=True)
                target = file_path(
                    f"{directory}/{module}-{self.version}-label{suffix}.xml"
                )
                with open(target, "w", encoding=self.encoding, newline="") as f:
                    f.writelines(lines)

        for module, data in element_dict.items():
            self.locs_defined = {}
            self.arcs_defined = {}
            self.lines = [
                '<?xml version="1.0" encoding="UTF-8"?>\n',
                '<linkbase xmlns="http://www.xbrl.org/2003/linkbase"\n',
                '  xmlns:xlink="http://www.w3.org/1999/xlink">\n',
                '  <presentationLink xlink:type="extended" '
                'xlink:role="http://www.xbrl.org/2003/role/link">\n',
            ]
            # A rows do not encode structural parent-child relationships.
            # Keep a deterministic, empty shared base; each Tuple HMD writes
            # its complete structural presentation as an extension.
            self.lines += ["  </presentationLink>\n", "</linkbase>\n"]
            target = file_path(
                f"{xbrl_base}/{module}/{module}-{self.version}-presentation.xml"
            )
            with open(target, "w", encoding=self.encoding, newline="") as f:
                f.writelines(self.lines)

    def generate_taxonomy_files(self, xbrl_base):
        if not xbrl_base:
            xbrl_base = self.xbrl_base
        ###################################
        # xBRL GD Pallete Schema
        #
        elementsDefined = set()
        element_dict = {}

        for parent_id, children in self.presentation_dict.items():
            parent_record = next((x for x in self.records if parent_id == x["element_id"]), None)
            if not parent_record:
                continue
            if '_' not in parent_id:
                pass
            parent_element = parent_id.replace("_", ":")
            parent_module = parent_id[:parent_id.index("_")]
            if parent_module not in element_dict:
                element_dict[parent_module] = []
            _parent_record = next((x for x in element_dict[parent_module] if parent_element == x["element"]), None)
            if not _parent_record:
                element_data = {
                    "type": parent_record["type"],
                    "element": parent_element,
                    "id": parent_record["id"],
                    "name": parent_record["name"],
                    "definition": parent_record["definition"],
                    "label_local": parent_record["label_local"],
                    "definition_local": parent_record["definition_local"],
                    "multiplicity": parent_record["multiplicity"],
                    "datatype": parent_record["datatype"],
                    "element_type": parent_record["element_type"],
                    "children": children,
                }
                element_dict[parent_module].append(element_data)

            for element_id in children:
                record = next((x for x in self.records if element_id == x["element_id"]), None)
                if not record:
                    continue
                element = record["element"]
                if not element:
                    continue
                id = record["id"]
                module = element[:element.index(":")]
                if module not in element_dict:
                    element_dict[module] = []
                _type = record["type"]
                multiplicity = record["multiplicity"]
                datatype = record["datatype"]
                element_type = record["element_type"]
                name = record["name"]
                definition = record["definition"]
                label_local = record["label_local"]
                definition_local = record["definition_local"]
                if element_id in self.presentation_dict:
                    _children = self.presentation_dict[element_id]
                    element_data = {
                        "type": _type,
                        "element": element,
                        "id": id,
                        "name": name,
                        "definition": definition,
                        "label_local": label_local,
                        "definition_local": definition_local,
                        "multiplicity": multiplicity,
                        "datatype": datatype,
                        "element_type": element_type,
                        "children": _children,
                    }
                    if element_data not in element_dict[module]:
                        element_dict[module].append(element_data)
                else:
                    element_data = {
                        "type": _type,
                        "element": element,
                        "id": id,
                        "name": name,
                        "definition": definition,
                        "label_local": label_local,
                        "definition_local": definition_local,
                        "multiplicity": multiplicity,
                        "datatype": datatype,
                        "element_type": element_type,
                    }
                    if element_data not in element_dict[module]:
                        element_dict[module].append(element_data)

        # A formal multi-HMD run may contain the same palette QName in more
        # than one HMD.  The reusable declaration and labels are written once,
        # while the base presentation view is the deterministic union of the
        # direct relationships seen in the supplied HMDs.  HMD-specific child
        # order and occurrence constraints remain in each content schema.
        for module, data in tuple(element_dict.items()):
            consolidated = OrderedDict()
            for record in data:
                element = record["element"]
                existing = consolidated.get(element)
                if existing is None:
                    copied = dict(record)
                    if "children" in copied:
                        copied["children"] = list(copied["children"])
                    consolidated[element] = copied
                    continue
                existing_children = existing.setdefault("children", [])
                for child_id in record.get("children", []):
                    if child_id not in existing_children:
                        existing_children.append(child_id)
            element_dict[module] = list(consolidated.values())

        for module, data in element_dict.items():
            modules = set()
            # modules.add("gen")
            for record in data:
                element = record["element"]
                _module = element[:element.index(":")]
                modules.add(_module)

            """
            Module taxonomy schema
            """
            module_directory = file_path(f"{xbrl_base}/{module}")
            html = [
                '<?xml version="1.0" encoding="UTF-8"?>\n',
                "<!-- (c) XBRL International.  See http://www.xbrl.org/legal -->\n",
                f'<schema targetNamespace="http://www.xbrl.org/int/gl/{module}/{self.version}" attributeFormDefault="unqualified" elementFormDefault="qualified"\n',
                '  xmlns="http://www.w3.org/2001/XMLSchema"\n',
                '  xmlns:link="http://www.xbrl.org/2003/linkbase"\n'
                '  xmlns:xlink="http://www.w3.org/1999/xlink"\n',
                '  xmlns:xbrli="http://www.xbrl.org/2003/instance"\n',
                '  xmlns:xbrldt="http://xbrl.org/2005/xbrldt"\n',
                f'  xmlns:gen="http://www.xbrl.org/int/gl/gen/{self.version}"\n'
            ]
            for _module in modules:
                html.append(
                    f'  xmlns:{_module}="http://www.xbrl.org/int/gl/{_module}/{self.version}"\n'
                )
            html.append(
                ">\n"
            )

            html += [
                '  <import namespace="http://www.xbrl.org/2003/instance" schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>\n',
                '  <import namespace="http://www.xbrl.org/2003/linkbase" schemaLocation="http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"/>\n',
                '  <import namespace="http://xbrl.org/2005/xbrldt" schemaLocation="http://www.xbrl.org/2005/xbrldt-2005.xsd"/>\n',
                f'  <import namespace="http://www.xbrl.org/int/gl/gen/{self.version}" schemaLocation="{self.gl_gen_schema_location(module_directory)}"/>\n'
            ]

            for _module in modules:
                if _module != module:
                    html.append(
                        f'  <import namespace="http://www.xbrl.org/int/gl/{_module}/{self.version}" schemaLocation="../{_module}/{_module}-{self.version}.xsd"/>\n'
                    )

            html.append("  <!-- reusable item type -->\n")
            defined_item_types = {}
            for line in data:
                if line["type"] != "A":
                    continue
                element = line["element"]
                local_name = element.split(":", 1)[1]
                type_name = local_name + "ItemType"
                base_type = line["datatype"]
                type_signature = ("A", base_type)
                if (
                    type_name in defined_item_types
                    and defined_item_types[type_name] != type_signature
                ):
                    self.error_print(
                        f"Conflicting shared item types for {element!r}."
                    )
                if type_name in defined_item_types:
                    continue
                defined_item_types[type_name] = type_signature
                html += [
                    f'  <complexType name="{type_name}">\n',
                    "    <simpleContent>\n",
                    f'      <restriction base="{base_type}"/>\n',
                    "    </simpleContent>\n",
                    "  </complexType>\n",
                ]

            html.append("  <!-- reusable item element -->\n")
            for line in data:
                element = line["element"]
                line_type = line['type']
                name = element[1 + element.index(":"):]
                element_id = element.replace(":", "_")
                element_type = line["element_type"]
                multiplicity = line["multiplicity"]
                if element in elementsDefined:
                    continue
                elementsDefined.add(element)
                if 'A' == line_type:
                    html.append(
                        f'  <element name="{name}" id="{element_id}" type="{element_type}" substitutionGroup="xbrli:item" nillable="true" xbrli:periodType="instant"/>\n'
                    )
            html.append("</schema>")

            """
            Write module taxonomy schema file
            """
            xsd_file = file_path(
                f"{xbrl_base}/{module}/{module}-{self.version}.xsd"
            )
            directory = os.path.dirname(xsd_file)
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
                self.trace_print(f"Created moduke taxonomy schema directory: {directory}")            
            with open(xsd_file, "w", encoding=self.encoding, newline="") as f:
                f.writelines(html)
            self.trace_print(f"-- {xsd_file}")

        if self.taxonomy_type == "shared":
            # Shared output owns reusable item declarations, ItemTypes and
            # item-only linkbases. Tuple declarations remain HMD-specific.
            self.write_tuple_linkbases(element_dict, xbrl_base)
            return

        if self.taxonomy_type == "tuple":
            """
            Module content-model schemas.  C and R rows are structural Tuple
            elements; their immediate LHM children are assembled in LHM order.
            """
            content_directory = file_path(f"{xbrl_base}/plt")
            os.makedirs(content_directory, exist_ok=True)
            for module, data in element_dict.items():
                dependencies = set()
                for record in data:
                    for child_id in record.get("children", []):
                        child = self.getRecord(child_id)
                        if child:
                            dependencies.add(child["element"].split(":", 1)[0])

                html = [
                    '<?xml version="1.0" encoding="UTF-8"?>\n',
                    f'<schema targetNamespace="http://www.xbrl.org/int/gl/{module}/{self.version}" '
                    'elementFormDefault="qualified" attributeFormDefault="unqualified"\n',
                    '  xmlns="http://www.w3.org/2001/XMLSchema"\n',
                    '  xmlns:xbrli="http://www.xbrl.org/2003/instance"\n',
                    f'  xmlns:{module}="http://www.xbrl.org/int/gl/{module}/{self.version}"\n',
                ]
                for dependency in sorted(dependencies):
                    if dependency != module:
                        html.append(
                            f'  xmlns:{dependency}="http://www.xbrl.org/int/gl/'
                            f'{dependency}/{self.version}"\n'
                        )
                html.append(">\n")
                html.append(
                    '  <import namespace="http://www.xbrl.org/2003/instance" '
                    'schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>\n'
                )
                html.append(
                    f'  <include schemaLocation="../{module}/{module}-{self.version}.xsd"/>\n'
                )
                for dependency in sorted(dependencies):
                    if dependency != module:
                        html.append(
                            f'  <import namespace="http://www.xbrl.org/int/gl/'
                            f'{dependency}/{self.version}" '
                            f'schemaLocation="{dependency}-content-{self.version}.xsd"/>\n'
                        )

                html.append("  <!-- HMD-specific Tuple element -->\n")
                for record in data:
                    if record["type"] not in {"C", "R"}:
                        continue
                    element = record["element"]
                    local_name = element.split(":", 1)[1]
                    element_id = element.replace(":", "_")
                    html.append(
                        f'  <element name="{local_name}" id="{element_id}" '
                        f'type="{module}:{local_name}ComplexType" '
                        'substitutionGroup="xbrli:tuple" nillable="false"/>\n'
                    )

                html.append("  <!-- HMD-specific structural type -->\n")
                defined_types = {}
                for record in data:
                    element = record["element"]
                    local_name = element.split(":", 1)[1]
                    if record["type"] == "A":
                        continue
                    if record["type"] not in {"C", "R"}:
                        continue
                    type_name = local_name + "ComplexType"
                    content_signature = tuple(
                        (
                            self.getRecord(child_id)["element"],
                            self.getRecord(child_id)["multiplicity"],
                        )
                        for child_id in record.get("children", [])
                        if self.getRecord(child_id)
                    )
                    type_signature = (record["type"], content_signature)
                    if (
                        type_name in defined_types
                        and defined_types[type_name] != type_signature
                    ):
                        self.error_print(
                            f"Conflicting Tuple content models for {element!r}."
                        )
                    if type_name in defined_types:
                        continue
                    defined_types[type_name] = type_signature
                    html += [
                        f'  <complexType name="{type_name}">\n',
                        "    <sequence>\n",
                    ]
                    for child_id in record.get("children", []):
                        child = self.getRecord(child_id)
                        if not child:
                            self.error_print(
                                f"Unresolved LHM child {child_id!r} of {element!r}."
                            )
                        occurs = self.occurrence_attributes(child["multiplicity"])
                        html.append(
                            f'      <element ref="{child["element"]}"{occurs}/>\n'
                        )
                    html += [
                        "    </sequence>\n",
                        '    <attribute name="id" type="ID"/>\n',
                        "  </complexType>\n",
                    ]
                html.append("</schema>\n")
                target = file_path(
                    f"{content_directory}/{module}-content-{self.version}.xsd"
                )
                with open(target, "w", encoding=self.encoding, newline="") as f:
                    f.writelines(html)

            roots = [record for record in self.records if int(record["level"]) == 1]
            if not roots:
                self.error_print(
                    "Tuple HMD input must contain at least one level-1 root."
                )
            root_modules = sorted(
                {record["element"].split(":", 1)[0] for record in roots}
            )
            palette_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>\n',
                f'<schema targetNamespace="http://www.xbrl.org/int/gl/plt/{self.version}" '
                'elementFormDefault="qualified" attributeFormDefault="unqualified"\n',
                '  xmlns="http://www.w3.org/2001/XMLSchema"\n',
                '  xmlns:link="http://www.xbrl.org/2003/linkbase"\n',
                '  xmlns:xlink="http://www.w3.org/1999/xlink">\n',
                '  <import namespace="http://www.xbrl.org/2003/linkbase" '
                'schemaLocation="http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"/>\n',
                "  <annotation><appinfo>\n",
            ]
            for module in sorted(element_dict):
                palette_lines += [
                    f'    <link:linkbaseRef xlink:type="simple" '
                    f'xlink:href="../{module}/lang/{module}-{self.version}-label.xml" '
                    'xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef" '
                    'xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>\n',
                    f'    <link:linkbaseRef xlink:type="simple" '
                    f'xlink:href="../{module}/lang/{module}-{self.version}-label-ja.xml" '
                    'xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef" '
                    'xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>\n',
                    f'    <link:linkbaseRef xlink:type="simple" '
                    f'xlink:href="../{module}/{module}-{self.version}-presentation.xml" '
                    'xlink:role="http://www.xbrl.org/2003/role/presentationLinkbaseRef" '
                    'xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>\n',
                ]
            palette_lines.append("  </appinfo></annotation>\n")
            for root_module in root_modules:
                palette_lines.append(
                    f'  <import namespace="http://www.xbrl.org/int/gl/{root_module}/'
                    f'{self.version}" schemaLocation="{root_module}-content-{self.version}.xsd"/>\n'
                )
            palette_lines.append("</schema>\n")
            palette_file = file_path(
                f"{xbrl_base}/plt/plt-all-{self.version}.xsd"
            )
            with open(palette_file, "w", encoding=self.encoding, newline="") as f:
                f.writelines(palette_lines)

            self.write_tuple_linkbases(element_dict, xbrl_base)
            return

        plt_all_file = file_path(f"{xbrl_base}/plt/plt-all-{self.version}.xsd")
        if os.path.exists(plt_all_file):
            os.remove(plt_all_file)
            self.trace_print(f"Removed tuple palette schema file {plt_all_file}")

        """
        OIM schema
        """
        os.makedirs(file_path(f"{xbrl_base}/plt"), exist_ok=True)
        modules = element_dict.keys()
        html = [
            '<?xml version="1.0" encoding="UTF-8"?>\n',
            "<!-- (c) XBRL International.  See http://www.xbrl.org/legal -->\n",
            f'<schema targetNamespace="http://www.xbrl.org/int/gl/plt/{self.version}" attributeFormDefault="unqualified" elementFormDefault="qualified"\n',
            '  xmlns="http://www.w3.org/2001/XMLSchema"\n',
            '  xmlns:xbrli="http://www.xbrl.org/2003/instance"\n',
            '  xmlns:link="http://www.xbrl.org/2003/linkbase"\n',
            '  xmlns:xlink="http://www.w3.org/1999/xlink"\n',
            '  xmlns:xbrldt="http://xbrl.org/2005/xbrldt"\n',
            f'  xmlns:plt="http://www.xbrl.org/int/gl/plt/{self.version}">\n'
        ]

        html += [
            '  <import namespace="http://www.xbrl.org/2003/instance" schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>\n',
            '  <import namespace="http://www.xbrl.org/2003/linkbase" schemaLocation="http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"/>\n',
            '  <import namespace="http://xbrl.org/2005/xbrldt" schemaLocation="http://www.xbrl.org/2005/xbrldt-2005.xsd"/>\n'
        ]

        html += [
            "  <annotation>\n",
            "    <appinfo>\n"
        ]

        for module in modules:
            html += [
                f'      <link:linkbaseRef xlink:type="simple" xlink:href="../{module}/lang/{module}-{self.version}-label.xml" xlink:title="Label Links, all" xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>\n',
                f'      <link:linkbaseRef xlink:type="simple" xlink:href="../{module}/lang/{module}-{self.version}-label-ja.xml" xlink:title="Label Links, ja" xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>\n'
            ]

        html.append(
            f'      <link:linkbaseRef xlink:type="simple" xlink:href="plt-def-{self.version}.xml" xlink:title="Definition" xlink:role="http://www.xbrl.org/2003/role/definitionLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>\n',
        )

        html += [
            "      <!-- \n",
            "        role type\n",
            "      -->\n",
            '      <link:roleType id="xbrl-role" roleURI="http://www.xbrl.org/xbrl-gl/role">\n',
            "        <link:definition>link xbrl-gl</link:definition>\n",
            "        <link:usedOn>link:definitionLink</link:usedOn>\n",
            "        <link:usedOn>link:presentationLink</link:usedOn>\n",
            "      </link:roleType>\n"
        ]

        for element_id in self.roleMap.keys():
            element_name = element_id
            html += [
                f'      <link:roleType id="link_{element_name}" roleURI="http://www.xbrl.org/xbrl-gl/role/link_{element_name}">\n',
                "        <link:usedOn>link:definitionLink</link:usedOn>\n",
                "      </link:roleType>\n"
            ]

        html += [
            "    </appinfo>\n",
            "  </annotation>\n"
        ]

        html += [
            "  <!-- typed dimension referenced element -->\n",
            '  <element name="_v" id="_v">\n',
            "    <simpleType>\n",
            '    <restriction base="string"/>\n',
            "    </simpleType>\n",
            "  </element>\n"
        ]

        html.append("  <!-- Hypercube -->\n")
        for element_id in self.roleMap.keys():
            element_name = element_id
            html.append(
                f'  <element name="h_{element_name}" id="h_{element_name}" substitutionGroup="xbrldt:hypercubeItem" type="xbrli:stringItemType" nillable="true" abstract="true" xbrli:periodType="instant"/>\n'
            )

        html.append("  <!-- Dimension -->\n")
        for element_id in self.roleMap.keys():
            element_name = element_id
            html.append(
                f'  <element name="d_{element_name}" id="d_{element_name}" substitutionGroup="xbrldt:dimensionItem" type="xbrli:stringItemType" abstract="true" xbrli:periodType="instant" xbrldt:typedDomainRef="#_v"/>\n'
            )

        html.append("  <!-- Primary -->\n")
        for element_id in self.roleMap.keys():
            element_name = element_id
            html.append(
                f'  <element name="p_{element_name}" id="p_{element_name}" substitutionGroup="xbrli:item" type="xbrli:stringItemType" nillable="true" xbrli:periodType="instant"/>\n'
            )

        html.append(
            "</schema>\n"
        )

        """
        Write xBRL-CSV schema file
        """
        xsd_file = file_path(
            f"{xbrl_base}/plt/plt-oim-{self.version}.xsd"
        )
        with open(xsd_file, "w", encoding=self.encoding, newline="") as f:
            f.writelines(html)
        self.trace_print(f"xBRL-CSV schema file {xsd_file}")

        ###################################
        # labelLink en
        #
        for module, data in element_dict.items():
            self.lines = [
                '<?xml version="1.0" encoding="UTF-8"?>\n',
                "<!-- (c) XBRL International.  See http://www.xbrl.org/legal -->\n",
                '<linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"\n',
                '    xmlns="http://www.xbrl.org/2003/linkbase"\n',
                '    xmlns:xlink="http://www.w3.org/1999/xlink">\n',
                '    <labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">\n',
            ]

            for record in data:
                if "A" != record["type"]:
                    continue
                element = record["element"]
                name = record["name"]
                desc = record["definition"].replace('\\n','\n') if "definition" in record else None
                module = element[:element.index(":")]
                element_name = element[1 + element.index(":"):]
                self.lines += [
                    f"        <!-- {element} {name} -->\n",
                    f'        <loc xlink:type="locator" xlink:href="../{module}-{self.version}.xsd#{module}_{element_name}" xlink:label="{element_name}"/>\n',
                    f'        <label xlink:type="resource" xlink:label="{element_name}_lbl" xlink:role="http://www.xbrl.org/2003/role/label" xlink:title="{module}_{element_name}_en" xml:lang="en">{name}</label>\n',
                    f'        <label xlink:type="resource" xlink:label="{element_name}_lbl" xlink:role="http://www.xbrl.org/2003/role/documentation" xml:lang="{self.lang}">{desc}</label>\n',
                    f'        <labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{element_name}" xlink:to="{element_name}_lbl"/>\n',
                ]

            self.lines.append("  </labelLink>\n")
            self.lines.append("</linkbase>\n")
            """
            Write label linkbase file
            """
            directory = file_path(
                f"{xbrl_base}/{module}/lang"
            )
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
                self.trace_print(f"Created label linkbase directory: {directory}")
            label_file = file_path(
                f"{xbrl_base}/{module}/lang/{module}-{self.version}-label.xml"
            )
            with open(label_file, "w", encoding=self.encoding, newline="") as f:
                f.writelines(self.lines)
            self.trace_print(f"-- {label_file}")

        ###################################
        # labelLink lang
        #
        for module, data in element_dict.items():
            self.lines = [
                '<?xml version="1.0" encoding="UTF-8"?>\n',
                "<!-- (c) XBRL International.  See http://www.xbrl.org/legal -->\n",
                '<linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"\n',
                '    xmlns="http://www.xbrl.org/2003/linkbase"\n',
                '    xmlns:xlink="http://www.w3.org/1999/xlink">\n',
                '    <labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">\n',
            ]

            for record in data:
                if "A" != record["type"]:
                    continue
                element = record["element"]
                label_local = record["label_local"]
                definition_local = (
                    record["definition_local"].replace('\\n','\n') if "definition_local" in record else None
                )
                module = element[:element.index(":")]
                element_name = element[1 + element.index(":"):]
                self.lines += [
                    f"        <!-- {element} {label_local} -->\n",
                    f'        <loc xlink:type="locator" xlink:href="../{module}-{self.version}.xsd#{module}_{element_name}" xlink:label="{element_name}"/>\n',
                    f'        <label xlink:type="resource" xlink:label="{element_name}_lbl" xlink:role="http://www.xbrl.org/2003/role/label" xlink:title="{module}_{element_name}_{self.lang}" xml:lang="en">{label_local}</label>\n',
                    f'        <label xlink:type="resource" xlink:label="{element_name}_lbl" xlink:role="http://www.xbrl.org/2003/role/documentation" xml:lang="{self.lang}">{definition_local}</label>\n',
                    f'        <labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{element_name}" xlink:to="{element_name}_lbl"/>\n',
                ]

            self.lines.append("  </labelLink>\n")
            self.lines.append("</linkbase>\n")
            """
            Write label linkbase file
            """
            label_file = file_path(
                f"{xbrl_base}/{module}/lang/{module}-{self.version}-label-{self.lang}.xml"
            )
            with open(label_file, "w", encoding=self.encoding, newline="") as f:
                f.writelines(self.lines)
            self.trace_print(f"-- {label_file}")

        ###################################
        #   presentationLink (Tuple binding)
        #
        # OIM hierarchy is represented by the Part 3 dimensional definition
        # linkbase (closed cubes and targetRole).  Reusing the Tuple
        # presentation tree would create locators for C/R elements that are
        # intentionally not declared as OIM facts.
        if self.taxonomy_type == "tuple":
            presentation_items = element_dict.items()
        else:
            presentation_items = ()
        for module, data in presentation_items:
            self.locs_defined = {}
            self.arcs_defined = {}
            self.lines = [
                '<?xml version="1.0" encoding="UTF-8"?>\n',
                "<!-- (c) XBRL International.  See http://www.xbrl.org/legal -->\n",
                '<linkbase xmlns="http://www.xbrl.org/2003/linkbase"\n',
                '  xmlns:xlink="http://www.w3.org/1999/xlink"\n',
                '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">\n',
                '  <presentationLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">\n',
            ]
            class_records = [x for x in data if 'C'==x["type"]]
            for record in class_records:
                element = record["element"]
                element_id = element.replace(":", "_")
                self.count = 0
                if "children" in record:
                    children = record["children"]
                    self.linkPresentation(module, element_id, children, 1)

            self.lines.append("  </presentationLink>\n")
            self.lines.append("</linkbase>\n")

            """
            Write presentation linkbase file
            """
            presentation_file = file_path(
                f"{xbrl_base}/{module}/{module}-{self.version}-presentation.xml"
            )
            with open(presentation_file, "w", encoding=self.encoding, newline="") as f:
                f.writelines(self.lines)
            self.trace_print(f"-- {presentation_file}")

        ###################################
        # definitionLink
        #
        self.locs_defined = {}
        self.arcs_defined = {}
        self.lines = [
            '<?xml version="1.0" encoding="UTF-8"?>\n',
            "<!-- (c) XBRL International.  See http://www.xbrl.org/legal -->\n",
            "<link:linkbase\n",
            '\txmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n',
            '\txsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"\n',
            '\txmlns:link="http://www.xbrl.org/2003/linkbase"\n',
            '\txmlns:xbrldt="http://xbrl.org/2005/xbrldt"\n',
            '\txmlns:xlink="http://www.w3.org/1999/xlink">\n',
        ]
        self.lines.append("  <!-- roleRef -->\n")
        #   <link:roleRef roleURI="http://www.xbrl.org/xbrl-gl/role/link_cor_accontingEntries" xlink:type="simple" xlink:href="core.xsd#link_cor_accontingEntries"/>
        for record in self.roleMap.values():
            taxonomy_schema, link_id, href = self.roleRecord(record['element_id'])
            self.lines.append(
                f'  <link:roleRef roleURI="http://www.xbrl.org/xbrl-gl/role/{link_id}" xlink:type="simple" xlink:href="plt-oim-{self.version}.xsd#{link_id}"/>\n'
            )

        self.lines += [
            "  <!-- arcroleRef -->\n",
            '  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/all" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#all"/>\n',
            '  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/domain-member" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#domain-member"/>\n',
            '  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#hypercube-dimension"/>\n',
            '  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/dimension-domain" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#dimension-domain"/>\n',
        ]

        for cor_id, record in self.roleMap.items():
            # role = roleRecord(record)
            self.count = 0
            self.defineHypercube(record)

        self.lines.append("</link:linkbase>\n")

        cor_definition_file = file_path(
            f"{xbrl_base}/plt/plt-def-{self.version}.xml"
        )
        with open(cor_definition_file, "w", encoding=self.encoding, newline="") as f:
            f.writelines(self.lines)
        self.trace_print(f"-- {cor_definition_file}")

    def json_meta_file(self, taxonomy, xbrl_base=None):
        if not xbrl_base:
            xbrl_base = self.xbrl_base
        json_meta = {
            "documentInfo": {
                "documentType": "https://xbrl.org/2021/xbrl-csv",
                "namespaces": {
                    "ns0": "http://www.example.com",
                    "link": "http://www.xbrl.org/2003/linkbase",
                    "iso4217": "http://www.xbrl.org/2003/iso4217",
                    "iso639": "http://www.xbrl.org/2003/iso639",
                    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "xbrli": "http://www.xbrl.org/2003/instance",
                    "xbrldi": "http://xbrl.org/2006/xbrldi",
                    "xlink": "http://www.w3.org/1999/xlink",
                    "gen": f"http://www.xbrl.org/int/gl/gen/{self.version}",
                    "cor": f"http://www.xbrl.org/int/gl/cor/{self.version}",
                    "bus": f"http://www.xbrl.org/int/gl/bus/{self.version}",
                    "muc": f"http://www.xbrl.org/int/gl/muc/{self.version}",
                    "usk": f"http://www.xbrl.org/int/gl/usk/{self.version}",
                    "taf": f"http://www.xbrl.org/int/gl/taf/{self.version}",
                    "ehm": f"http://www.xbrl.org/int/gl/ehm/{self.version}",
                    "lnk": f"http://www.xbrl.org/int/gl/lnk/{self.version}",
                    "btx": f"http://www.xbrl.org/int/gl/btx/{self.version}",
                    "plt": f"http://www.xbrl.org/int/gl/plt/{self.version}"
                },
                "taxonomy": [
                    taxonomy
                ]
            },
            "tableTemplates": {
                "xbrl-gl_template": {
                    "dimensions": {
                        "period": "2025-05-17T00:00:00",
                        "entity": "ns0:Example Co.",
                    },
                    "columns": OrderedDict(),   # keep deterministic insertion order
                }
            },
            "tables": {"xbrl-gl_table": {"template": "xbrl-gl_template"}},
        }

        if self.root:
            header_columns = []
            root_id = next((x for x in self.dimension_dict.keys() if self.root in x), None)
            if not root_id:
                self.error_print(f"{self.root} not defined.")

            root_element_id = next((x for x in self.records if root_id == x["id"]), None)["element_id"]
            root_name = root_element_id#[1 + root_element_id.index("-"):]
            self.trace_print(f"json meta columns:{root_name}")
            header_columns.append(root_name)

            dimensions = [
                v["parent_id"]
                for k, v in self.dimension_dict.items()
                if isinstance(v, dict)
                and v["instance"]
                and "multiplicity" in v
                and "*"==v["multiplicity"][-1]
            ]

            properties = [
                x["element_id"]
                for x in self.records
                if x["instance"] and x["element_id"] not in dimensions and "A" == x["type"]
            ]

            json_meta["tableTemplates"]["xbrl-gl_template"]["dimensions"][
                f"plt:d_{root_name}"
            ] = f"${root_name}"
            json_meta["tableTemplates"]["xbrl-gl_template"]["columns"][root_name] = {}

            for dimension in dimensions[1:]:
                dimension_name = dimension.replace(":","_")
                json_meta["tableTemplates"]["xbrl-gl_template"]["dimensions"][f"plt:d_{dimension_name}"] = f"${dimension_name}"
                json_meta["tableTemplates"]["xbrl-gl_template"]["columns"][dimension_name] = {}
                self.trace_print(f"json meta columns:{dimension_name}")
                header_columns.append(dimension_name)

            for property in properties:
                property_column = property[1 + property.index("_"):]
                property_name = property
                property_module = property[:property.index("_")]
                if property.endswith("Amount"):
                    json_meta["tableTemplates"]["xbrl-gl_template"]["columns"][property_name] = {
                        "dimensions": {
                            "concept": f"{property_module}:{property_column}",
                            "unit": f"iso4217:{self.currency}",
                        }
                    }
                else:
                    json_meta["tableTemplates"]["xbrl-gl_template"]["columns"][property_name] = {
                        "dimensions": {
                            "concept": f"{property_module}:{property_column}"
                        }
                    }
                self.trace_print(f"json meta columns:{property_name}")
                header_columns.append(property_name)

            out = "xbrl-gl"
            csv_file = f"{out}_skeleton.csv"
            json_meta["tables"]["xbrl-gl_table"]["url"] = csv_file

            json_meta_file = file_path(
                f"{xbrl_base}/{out}.json"
            )
            try:
                with open(json_meta_file, "w", encoding=self.encoding) as file:
                    json.dump(json_meta, file, ensure_ascii=False, indent=4)
                self.trace_print(f"JSON file '{json_meta_file}'")
            except Exception as e:
                print(f"An error occurred while creating the JSON file: {e}")

            out_file = file_path(
                f"{xbrl_base}/{csv_file}"
            )

            try:
                with open(out_file, "w", encoding=self.encoding, newline="") as file:
                    writer = csv.writer(file)
                    # Write the header and columnname rows
                    writer.writerow(header_columns)
                self.trace_print(f"CSV template file '{out_file}'")
            except Exception as e:
                print(f"An error occurred while creating the JSON file: {e}")

        print("** END **")

def presentation_relationships(presentation_dict):
    """Return the effective relationship set encoded by a presentation map."""
    relationships = set()
    for parent_id, children in presentation_dict.items():
        for index, child_id in enumerate(children, 1):
            relationships.add(
                PresentationRelationship(
                    PRESENTATION_ROLE,
                    PARENT_CHILD_ARCROLE,
                    parent_id,
                    child_id,
                    index * 10,
                )
            )
    return frozenset(relationships)


def oim_presentation_relationships(generator):
    """Return the HMD presentation expressed with OIM concepts.

    C rows are replaced by their ``p_`` primary items. A rows continue to
    reference the shared module elements. R rows are not OIM facts and are
    traversed transparently, matching ``domainMember``.
    """
    relationships = set()

    def visible_children(parent_id, active=()):
        if parent_id in active:
            raise ValueError(
                f"Cyclic HMD presentation traversal at {parent_id!r}."
            )
        result = []
        for child_id in generator.presentation_dict.get(parent_id, []):
            child = generator.getRecord(child_id)
            if not child:
                raise ValueError(
                    f"Unresolved HMD presentation child: {child_id!r}."
                )
            concept_id = generator.oim_presentation_concept_id(child)
            if concept_id is None:
                result.extend(
                    visible_children(child["element_id"], (*active, parent_id))
                )
            else:
                result.append(concept_id)
        return result

    for record in generator.records:
        if record["type"] != "C":
            continue
        parent_id = generator.oim_presentation_concept_id(record)
        for index, child_id in enumerate(
            visible_children(record["element_id"]), 1
        ):
            relationships.add(
                PresentationRelationship(
                    PRESENTATION_ROLE,
                    PARENT_CHILD_ARCROLE,
                    parent_id,
                    child_id,
                    index * 10,
                )
            )
    return frozenset(relationships)


def module_presentation_relationships(generator, modules):
    """Return the reusable module presentation base.

    Module schemas now contain A concepts only.  Structural relationships are
    HMD-specific, so the reusable base is intentionally empty.
    """
    return frozenset()


def presentation_difference(base, expected):
    """Return deterministic prohibited and optional extension relationships."""
    base = frozenset(base)
    expected = frozenset(expected)
    prohibited = tuple(sorted(base - expected))
    optional = tuple(sorted(expected - base))
    base_by_child = {relationship.child_id for relationship in base}
    base_pairs = {relationship.pair_key for relationship in base}
    override_count = sum(
        relationship.child_id in base_by_child
        or relationship.pair_key in base_pairs
        for relationship in optional
    )
    return PresentationDifference(prohibited, optional, override_count)


def next_presentation_priority(existing_priorities):
    """Choose a deterministic priority above every equivalent base arc."""
    priorities = tuple(existing_priorities)
    return max(priorities, default=0) + 1


def _xml_attribute(value):
    return str(value).replace("&", "&amp;").replace('"', "&quot;")


def serialize_presentation_extension(
    difference, version, structural_ids=(), binding="tuple"
):
    """Serialize one HMD presentation difference as an XBRL linkbase."""
    if binding not in {"tuple", "oim"}:
        raise ValueError(f"Unsupported presentation binding: {binding!r}")
    relationships = (*difference.prohibited, *difference.optional)
    concept_ids = sorted(
        {item.parent_id for item in relationships}
        | {item.child_id for item in relationships}
    )
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<linkbase xmlns="http://www.xbrl.org/2003/linkbase"\n',
        '  xmlns:xlink="http://www.w3.org/1999/xlink">\n',
        f'  <presentationLink xlink:type="extended" '
        f'xlink:role="{PRESENTATION_ROLE}">\n',
    ]
    structural_ids = frozenset(structural_ids)
    for element_id in concept_ids:
        if binding == "oim" and element_id.startswith("p_"):
            href = f"{{HMD_PREFIX}}-all-oim-{version}.xsd#{element_id}"
        else:
            module = element_id.split("_", 1)[0]
        if binding == "tuple" and element_id in structural_ids:
            # The HMD presentation linkbase now lives beside the HMD content
            # schemas below tuple/<HMD>, so structural locators are local.
            href = f"{module}-content-{version}.xsd#{element_id}"
        elif binding == "tuple" or not element_id.startswith("p_"):
            href = f"../../{module}/{module}-{version}.xsd#{element_id}"
        lines.append(
            f'    <loc xlink:type="locator" xlink:href="{href}" '
            f'xlink:label="loc_{element_id}" '
            f'xlink:title="loc: {element_id}"/>\n'
        )
    priority = next_presentation_priority(
        item.priority for item in difference.prohibited
    )
    for use, items in (
        ("prohibited", difference.prohibited),
        ("optional", difference.optional),
    ):
        for item in items:
            preferred = (
                f' preferredLabel="{_xml_attribute(item.preferred_label)}"'
                if item.preferred_label else ""
            )
            lines.append(
                f'    <presentationArc xlink:type="arc" '
                f'xlink:arcrole="{item.arcrole}" '
                f'xlink:from="loc_{item.parent_id}" '
                f'xlink:to="loc_{item.child_id}" '
                f'xlink:title="presentation: {item.parent_id} to '
                f'{item.child_id}" use="{use}" priority="{priority}" '
                f'order="{item.order}"{preferred}/>\n'
            )
    lines += ["  </presentationLink>\n", "</linkbase>\n"]
    return "".join(lines).encode("utf-8")


def write_presentation_extension(
    target, difference, version, structural_ids=(), binding="tuple"
):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    package_id = target.parent.name
    hmd_prefix = package_id.split("_", 1)[0]
    content = serialize_presentation_extension(
        difference, version, structural_ids, binding
    ).replace(b"{HMD_PREFIX}", hmd_prefix.encode("utf-8"))
    target.write_bytes(content)


def add_schema_linkbase_refs(schema_file, hrefs):
    """Add sorted presentation linkbaseRefs to one generated entry point."""
    schema_file = Path(schema_file)
    text = schema_file.read_text(encoding="utf-8-sig")
    unique_hrefs = sorted(set(hrefs))
    additions = []
    for href in unique_hrefs:
        if f'xlink:href="{href}"' in text:
            continue
        additions.append(
            '    <link:linkbaseRef xlink:type="simple" '
            f'xlink:href="{href}" '
            'xlink:role="http://www.xbrl.org/2003/role/'
            'presentationLinkbaseRef" '
            'xlink:arcrole="http://www.w3.org/1999/xlink/properties/'
            'linkbase"/>\n'
        )
    if additions:
        marker = "</appinfo>"
        if marker not in text:
            raise ValueError(
                f"Generated entry point has no appinfo marker: {schema_file}"
            )
        text = text.replace(marker, "".join(additions) + marker, 1)
        schema_file.write_text(text, encoding="utf-8", newline="")


def validate_shared_qnames(generators):
    """Validate explicit shared declarations by QName, never by provenance ID.

    Returns the number of QNames present in more than one supplied HMD.
    Ordered direct-child QNames and multiplicities are intentionally excluded:
    they belong to the effective ComplexType in each independent HMD DTS.
    """
    declarations = {}
    shared = set()
    for generator in generators:
        for record in generator.records:
            qname = record["expanded_name"]
            signature = (
                record["type"], record["datatype"], record["element_type"],
                record["definition"], record["name"], record["label_local"],
                record["definition_local"], record["element_id"],
            )
            if qname in declarations:
                shared.add(qname)
                if declarations[qname] != signature:
                    raise ValueError(
                        f"Shared QName declaration conflict for {qname!r}: "
                        f"{declarations[qname]!r} != {signature!r}"
                    )
            else:
                declarations[qname] = signature
    return len(shared)


def merge_hmd_generators(primary, additional):
    """Merge validated HMD occurrences for one shared-declaration DTS."""
    generators = sorted(
        [primary, *additional],
        key=lambda generator: (
            tuple(
                record["element"]
                for record in generator.records
                if int(record["level"]) == 1
            ),
            os.path.basename(generator.core_file),
        ),
    )
    validate_shared_qnames(generators)
    primary, *additional = generators
    for other in additional:
        primary.records.extend(other.records)
        for parent, children in other.presentation_dict.items():
            target = primary.presentation_dict.setdefault(parent, [])
            for child in children:
                if child not in target:
                    target.append(child)
        for path, value in other.dimension_dict.items():
            if path in primary.dimension_dict and primary.dimension_dict[path] != value:
                raise ValueError(f"Conflicting HMD hierarchy at {path!r}.")
            primary.dimension_dict[path] = value
    return primary


def hmd_package_id(generator):
    """Return the stable HMD identifier derived from its single root QName."""
    roots = [record for record in generator.records if int(record["level"]) == 1]
    if len(roots) != 1:
        raise ValueError(
            "Each formal HMD must contain exactly one level-1 root; "
            f"found {len(roots)} in {generator.core_file!r}."
        )
    return roots[0]["element"].replace(":", "_", 1)


def _generator_for_file(in_file, base_dir, args, taxonomy_type):
    generator = xBRLGL_TaxonomyGenerator(
        in_file=in_file,
        base_dir=str(base_dir),
        palette=None,
        root=None,
        lang=args.lang,
        currency="JPY",
        namespace=args.namespace,
        encoding=args.encoding,
        trace=args.trace,
        debug=args.debug,
        instance=True,
        taxonomy_type=taxonomy_type,
    )
    generator.load_csv_data()
    return generator


def _write_transformed(source, target, replacements):
    text = Path(source).read_text(encoding="utf-8-sig")
    for old, new in replacements:
        text = text.replace(old, new)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="")


def _copy_shared_module_files(generated_root, package_root, modules, version):
    """Copy stable shared declarations once; never move HMD types into them."""
    generated_root = Path(generated_root)
    package_root = Path(package_root)
    gen_source = generated_root / "gen"
    if gen_source.is_dir():
        shutil.copytree(gen_source, package_root / "gen")

    for module in sorted(modules):
        source = generated_root / module
        target = package_root / module
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            source / f"{module}-{version}.xsd",
            target / f"{module}-{version}.xsd",
        )
        presentation = source / f"{module}-{version}-presentation.xml"
        if presentation.exists():
            shutil.copy2(
                presentation,
                target / f"{module}-pre-{version}.xml",
            )
        label_target = target / "label"
        label_target.mkdir(exist_ok=True)
        shutil.copy2(
            source / "lang" / f"{module}-{version}-label.xml",
            label_target / f"{module}-lab-en-{version}.xml",
        )
        shutil.copy2(
            source / "lang" / f"{module}-{version}-label-ja.xml",
            label_target / f"{module}-lab-ja-{version}.xml",
        )


def _copy_hmd_content_schema(source, target, module, version):
    """Copy one HMD-derived content schema and adjust only its include path."""
    _write_transformed(
        source,
        target,
        [
            (
                f'../{module}/{module}-{version}.xsd',
                f'../../{module}/{module}-{version}.xsd',
            )
        ],
    )


def generate_formal_hmd_package(args):
    """Generate the first-edition formal Tuple/OIM taxonomy package.

    ``args.lhm_for_taxonomy`` MUST name one ``LHM_for_taxonomy`` directory.
    Formal HMD-for-taxonomy CSVs are discovered directly from that directory.
    Any ``manifest.csv`` present there is execution-confirmation only and is
    not consumed by taxonomy generation.
    """
    hmd_inputs = resolve_lhm_for_taxonomy_input(
        args.lhm_for_taxonomy, args.encoding
    )
    output_root = Path(args.base_dir).resolve()
    if output_root.exists() and any(output_root.iterdir()):
        raise ValueError(
            f"Formal package output directory must be empty: {output_root}"
        )
    output_root.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="xbrl-gl-package-", dir=output_root.parent
    ) as temporary:
        temporary = Path(temporary)
        package_root = temporary / "published"
        package_root.mkdir()
        merged_items = [
            _generator_for_file(
                in_file,
                temporary / "merged",
                args,
                "tuple",
            )
            for in_file in hmd_inputs
        ]
        validate_shared_qnames(merged_items)
        merged = merge_hmd_generators(merged_items[0], merged_items[1:])
        merged.taxonomy_type = "shared"
        merged.process_records()
        merged.generate_taxonomy_files(merged.xbrl_base)
        version = merged.namespace[-10:]
        modules = {
            record["element"].split(":", 1)[0]
            for record in merged.records
        }
        _copy_shared_module_files(
            merged.xbrl_base, package_root, modules, version
        )

        package_ids = set()
        for index, in_file in enumerate(hmd_inputs):
            tuple_generator = _generator_for_file(
                in_file,
                temporary / f"hmd-{index}-tuple",
                args,
                "tuple",
            )
            package_id = hmd_package_id(tuple_generator)
            if package_id in package_ids:
                raise ValueError(f"Duplicate HMD package identifier: {package_id}")
            package_ids.add(package_id)
            tuple_generator.process_records()
            tuple_generator.generate_taxonomy_files(tuple_generator.xbrl_base)
            hmd_modules = {
                record["element"].split(":", 1)[0]
                for record in tuple_generator.records
            }
            expected_network = presentation_relationships(
                tuple_generator.presentation_dict
            )
            base_network = module_presentation_relationships(
                merged, hmd_modules
            )
            presentation_diff = presentation_difference(
                base_network, expected_network
            )
            hmd_prefix = package_id.split("_", 1)[0]
            tuple_plt = Path(tuple_generator.xbrl_base) / "plt"
            tuple_target = package_root / "tuple" / package_id
            tuple_target.mkdir(parents=True, exist_ok=True)
            for content in sorted(tuple_plt.glob(f"*-content-{version}.xsd")):
                module = content.name.split("-content-", 1)[0]
                _copy_hmd_content_schema(
                    content, tuple_target / content.name, module, version
                )
            tuple_entry = tuple_target / f"{hmd_prefix}-all-{version}.xsd"
            _write_transformed(
                tuple_plt / f"plt-all-{version}.xsd",
                tuple_entry,
                [
                    (
                        f"../{module}/lang/{module}-{version}-label.xml",
                        f"../../{module}/label/{module}-lab-en-{version}.xml",
                    )
                    for module in sorted(hmd_modules)
                ] + [
                    (
                        f"../{module}/lang/{module}-{version}-label-ja.xml",
                        f"../../{module}/label/{module}-lab-ja-{version}.xml",
                    )
                    for module in sorted(hmd_modules)
                ] + [
                    (
                        f"../{module}/{module}-{version}-presentation.xml",
                        f"../../{module}/{module}-pre-{version}.xml",
                    )
                    for module in sorted(hmd_modules)
                ],
            )
            tuple_presentation_name = f"{hmd_prefix}-all-pre-{version}.xml"
            write_presentation_extension(
                tuple_target / tuple_presentation_name,
                presentation_diff,
                version,
                {
                    record["element_id"]
                    for record in tuple_generator.records
                    if record["type"] in {"C", "R"}
                },
            )
            tuple_presentation_refs = [
                f"../../{module}/{module}-pre-{version}.xml"
                for module in sorted(hmd_modules)
            ] + [tuple_presentation_name]
            add_schema_linkbase_refs(tuple_entry, tuple_presentation_refs)

            oim_generator = _generator_for_file(
                in_file,
                temporary / f"hmd-{index}-oim",
                args,
                "oim",
            )
            oim_generator.process_records()
            oim_generator.generate_taxonomy_files(oim_generator.xbrl_base)
            oim_plt = Path(oim_generator.xbrl_base) / "plt"
            oim_target = package_root / "oim" / package_id
            oim_target.mkdir(parents=True, exist_ok=True)
            oim_entry_name = f"{hmd_prefix}-all-oim-{version}.xsd"
            dim_name = f"{hmd_prefix}-all-dim-{version}.xml"
            oim_modules = {
                record["element"].split(":", 1)[0]
                for record in oim_generator.records
            }
            if oim_modules != hmd_modules:
                raise ValueError(
                    f"Tuple/OIM module mismatch for {package_id}: "
                    f"{sorted(hmd_modules)!r} != {sorted(oim_modules)!r}"
                )
            _write_transformed(
                oim_plt / f"plt-oim-{version}.xsd",
                oim_target / oim_entry_name,
                [
                    (
                        f"../{module}/lang/{module}-{version}-label.xml",
                        f"../../{module}/label/{module}-lab-en-{version}.xml",
                    )
                    for module in sorted(hmd_modules)
                ] + [
                    (
                        f"../{module}/lang/{module}-{version}-label-ja.xml",
                        f"../../{module}/label/{module}-lab-ja-{version}.xml",
                    )
                    for module in sorted(hmd_modules)
                ] + [(f"plt-def-{version}.xml", dim_name)],
            )
            _write_transformed(
                oim_plt / f"plt-def-{version}.xml",
                oim_target / dim_name,
                [
                    (f"plt-oim-{version}.xsd", oim_entry_name),
                    ('xlink:href="../', 'xlink:href="../../'),
                ],
            )
            oim_presentation_name = f"{hmd_prefix}-all-pre-{version}.xml"
            oim_presentation_diff = presentation_difference(
                frozenset(),
                oim_presentation_relationships(oim_generator),
            )
            write_presentation_extension(
                oim_target / oim_presentation_name,
                oim_presentation_diff,
                version,
                binding="oim",
            )
            add_schema_linkbase_refs(
                oim_target / oim_entry_name,
                [
                    f"../../{module}/{module}-pre-{version}.xml"
                    for module in sorted(hmd_modules)
                ] + [oim_presentation_name],
            )

        # Publish only after every HMD and both bindings have been generated.
        # os.replace is performed on the same filesystem because the staging
        # directory is a sibling of the requested output directory.
        if output_root.exists():
            output_root.rmdir()
        os.replace(package_root, output_root)

    return sorted(package_ids)


def main():
    global DEBUG, TRACE

    parser = argparse.ArgumentParser(
        description=(
            "Generate the XBRL GL Next formal Tuple/OIM taxonomy package "
            "from one LHM_for_taxonomy input-set directory."
        )
    )
    parser.add_argument(
        "lhm_for_taxonomy",
        help=(
            "Formal LHM_for_taxonomy directory containing the formal "
            "HMD-for-taxonomy CSV files"
        ),
    )
    parser.add_argument(
        "-b", "--base-dir", dest="base_dir", required=True,
        help="Empty output directory for the generated formal taxonomy package",
    )
    parser.add_argument("-l", "--lang", default="ja")
    parser.add_argument(
        "-n", "--namespace", required=True,
        help=(
            "Palette namespace ending in the explicit taxonomy version date, "
            "for example http://www.xbrl.org/int/gl/plt/2026-12-31"
        ),
    )
    parser.add_argument("-e", "--encoding", default="utf-8-sig")
    parser.add_argument("-t", "--trace", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()
    DEBUG = args.debug
    TRACE = args.trace

    try:
        package_ids = generate_formal_hmd_package(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

    print("Generated formal HMD packages: " + ", ".join(package_ids))


if __name__ == "__main__":
    main()

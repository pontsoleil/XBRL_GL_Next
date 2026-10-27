#!/usr/bin/env python3
"""Generate a root-specific full Tavi taxonomy from an 18-column HMD.

The default mode reproduces the accepted v3 representation. Documentation
labels are an explicit extension, selected with --include-documentation
or --documentation-target.
No reference taxonomy is read by the generator. Python standard library only.
"""
import argparse
import csv
import json
import re
from pathlib import Path

SCHEMA = ['sequence', 'module', 'level', 'type', 'identifier', 'name',
          'datatype', 'multiplicity', 'value_domain', 'definition',
          'label_local', 'definition_local', 'source_bsm_id', 'semantic_path',
          'associated_module', 'class_term', 'local_name', 'xpath']
BASE_TYPES = {'String': 'xs:string', 'Token': 'xs:token',
              'Date Time': 'xs:dateTime', 'Boolean': 'xs:boolean',
              'Monetary': 'xbrli:monetary', 'Decimal': 'xs:decimal',
              'QName': 'xs:QName', 'Pure': 'xbrli:pureType',
              'Date': 'xs:date', 'Integer': 'xs:integer', 'anyURI': 'xs:anyURI',
              'Identifier': 'xs:string', 'Code': 'xs:token',
              'Text': 'xs:string', 'Amount': 'xbrli:monetary'}
NAMESPACES = {m: 'https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/' + m
              for m in ('bus', 'cor', 'ehm', 'lnk', 'muc', 'taf', 'plt')}
NAMESPACES.update(xbrl='https://xbrl.org/2025',
                  xbrli='https://xbrl.org/2025/instance',
                  xs='http://www.w3.org/2001/XMLSchema')


def read_hmd(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != SCHEMA:
            raise ValueError('The HMD must use the accepted 18-column value_domain schema')
        rows = list(reader)
    if not rows:
        raise ValueError('Empty HMD')
    seen_paths = set()
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError('Malformed CSV row')
        if row['type'] not in ('C', 'A', 'R'):
            raise ValueError('Unsupported row type: ' + row['type'])
        if row['semantic_path'] in seen_paths:
            raise ValueError('Duplicate semantic path: ' + row['semantic_path'])
        seen_paths.add(row['semantic_path'])
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', row['module']) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*', row['local_name']):
            raise ValueError('Unsupported module or local_name')
        if row['type'] == 'A' and row['datatype'] not in BASE_TYPES:
            raise ValueError('Unsupported datatype: ' + row['datatype'])
    return rows


def generate(rows, version, documentation_targets=(), include_documentation=False):
    classes = [r for r in rows if r['type'] == 'C']
    by_path = {r['semantic_path']: r for r in classes}
    roots = [r for r in classes if not any(r['semantic_path'].startswith(p + '.') for p in by_path if p != r['semantic_path'])]
    if len(roots) != 1:
        raise ValueError('Expected exactly one HMD root')
    root = roots[0]
    root_key = root['module'] + '_' + root['local_name']
    # Preserve the exact historical COR document and namespace ordering.
    namespaces = dict(NAMESPACES)
    for row in rows:
        module = row['module']
        if module not in namespaces:
            namespaces[module] = 'https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/' + module

    def key(r):
        return r['module'] + '_' + r['local_name']

    def concept(r):
        return r['module'] + ':' + ('p_' + key(r) if r['type'] == 'C' else r['local_name'])

    def ancestors(r, include_self=False):
        path = r['semantic_path']
        return sorted((c for p, c in by_path.items()
                       if path.startswith(p + '.') or (include_self and path == p)),
                      key=lambda c: len(c['semantic_path']))

    def owner(r):
        chain = ancestors(r)
        if not chain:
            raise ValueError('No class owner: ' + r['semantic_path'])
        return chain[-1]

    def repeating(r):
        upper = r['multiplicity'].split('..')[-1]
        if upper == '*':
            return True
        try:
            return int(upper) > 1
        except ValueError:
            raise ValueError('Unsupported multiplicity: ' + r['multiplicity'])

    included = [r for r in rows if r['type'] != 'R']
    names = [concept(r) for r in included]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate concept identity')
    children = {r['semantic_path']: [] for r in classes}
    for r in included:
        if r is not roots[0]:
            children[owner(r)['semantic_path']].append(r)
    data_types = [{'name': concept(r) + 'ItemType', 'baseType': BASE_TYPES[r['datatype']]}
                  for r in rows if r['type'] == 'A']
    concepts = [{'name': concept(r),
                 'dataType': 'xs:string' if r['type'] == 'C' else concept(r) + 'ItemType',
                 'periodType': 'instant', 'nillable': True} for r in included]
    dimensions = [{'name': 'plt:d_' + key(r), 'domainDataType': 'xs:string'}
                  for r in classes if repeating(r)]
    domains = []
    cubes = []
    relationships = []
    network_name = 'plt:' + root_key + 'Hierarchy'
    for c in classes:
        attrs = [r for r in children[c['semantic_path']] if r['type'] == 'A']
        cube_dims = []
        if attrs:
            domain_name = 'plt:domain_' + key(c)
            domains.append({'name': domain_name, 'root': 'xbrl:conceptDomain',
                            'relationships': [{'source': 'xbrl:conceptDomain', 'target': concept(r), 'order': i}
                                              for i, r in enumerate(attrs, 1)]})
            cube_dims.append({'dimensionName': 'xbrl:concept', 'domainName': domain_name})
        cube_dims.extend({'dimensionName': 'plt:d_' + key(r), 'typedSort': 'asc', 'allowDomainFacts': False}
                         for r in ancestors(c, True) if repeating(r))
        cubes.append({'name': 'plt:h_' + key(c), 'cubeDimensions': cube_dims, 'cubeNetworks': [network_name]})
        relationships.extend({'source': concept(c), 'target': concept(r), 'order': i}
                             for i, r in enumerate(children[c['semantic_path']], 1))
    labels = []
    for r in included:
        for lang, field in (('en', 'name'), ('ja', 'label_local')):
            if r[field]:
                labels.append({'relatedName': concept(r), 'labelType': 'xbrl:label',
                               'language': lang, 'value': r[field]})
    targets = set(names) if include_documentation else set(documentation_targets)
    if targets - set(names):
        raise ValueError('Unknown documentation target: ' + ', '.join(sorted(targets - set(names))))
    for r in included:
        if concept(r) in targets:
            for lang, field in (('en', 'definition'), ('ja', 'definition_local')):
                if not r[field]:
                    if include_documentation:
                        continue
                    raise ValueError('Missing requested documentation: ' + concept(r))
                labels.append({'relatedName': concept(r), 'labelType': 'xbrl:documentation',
                               'language': lang, 'value': r[field]})
    return {'documentInfo': {'documentType': 'https://xbrl.org/2025/taxonomy',
                             'namespaces': namespaces, 'documentNamespace': 'plt'},
            'taxonomy': {'name': 'plt:' + root_key + 'TaviTaxonomy',
                         'frameworkName': ('XBRL GL Next — Accounting Entries HMD Tavi Taxonomy'
                                           if root_key == 'cor_accountingEntries'
                                           else 'XBRL GL Next — ' + root['name'] + ' HMD Tavi Taxonomy'),
                         'version': version, 'resolved': False,
                         'dataTypes': data_types, 'concepts': concepts,
                         'dimensions': dimensions, 'domains': domains, 'cubes': cubes,
                         'networks': [{'name': network_name, 'relationshipTypeName': 'xbrl:parent-child',
                                       'roots': [concept(roots[0])], 'relationships': relationships}],
                         'labels': labels}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hmd', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--version', required=True)
    parser.add_argument('--documentation-target', action='append', default=[])
    parser.add_argument('--include-documentation', action='store_true',
                        help='Emit all available English and Japanese HMD definitions as documentation labels')
    args = parser.parse_args()
    if args.hmd.resolve() == args.output.resolve():
        parser.error('Output must not overwrite the input')
    if args.output.exists():
        parser.error('Output exists; select a new candidate path')
    try:
        doc = generate(read_hmd(args.hmd), args.version, args.documentation_target, args.include_documentation)
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: len(v) for k, v in doc['taxonomy'].items() if isinstance(v, list)}))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Validate a conservative static outlined SVG profile; never rewrite inputs."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from xml.etree.ElementTree import ParseError

from defusedxml import ElementTree as ET
from defusedxml.common import DefusedXmlException

SVG_NS = 'http://www.w3.org/2000/svg'
MAX_BYTES = 1_000_000
MAX_ELEMENTS = 5_000
MAX_DEPTH = 32
MAX_PATH_TOKENS = 50_000
NUMBER = r'[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?'
NUM_RE = re.compile(NUMBER)
ID_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_.-]*\Z')
COMMON = {'id', 'fill', 'stroke', 'fill-rule', 'stroke-width',
          'stroke-linecap', 'stroke-linejoin', 'stroke-miterlimit',
          'opacity', 'fill-opacity', 'stroke-opacity', 'transform'}
GEOMETRY = {
    'path': {'d'}, 'rect': {'x', 'y', 'width', 'height', 'rx', 'ry'},
    'circle': {'cx', 'cy', 'r'}, 'ellipse': {'cx', 'cy', 'rx', 'ry'},
    'line': {'x1', 'y1', 'x2', 'y2'}, 'polyline': {'points'},
    'polygon': {'points'},
}
ALLOWED = {'svg': COMMON | {'viewBox', 'width', 'height', 'preserveAspectRatio',
                          'role', 'aria-label', 'aria-labelledby', 'aria-describedby',
                          'aria-hidden'},
           'g': COMMON, 'title': {'id'}, 'desc': {'id'}}
ALLOWED.update({tag: COMMON | attrs for tag, attrs in GEOMETRY.items()})
ENUMS = {'fill-rule': {'nonzero', 'evenodd'},
         'stroke-linecap': {'butt', 'round', 'square'},
         'stroke-linejoin': {'miter', 'round', 'bevel'},
         'role': {'img', 'presentation', 'none'}, 'aria-hidden': {'true', 'false'}}
OPACITIES = {'opacity', 'fill-opacity', 'stroke-opacity'}
LENGTHS = {'x', 'y', 'cx', 'cy', 'r', 'rx', 'ry', 'x1', 'x2', 'y1', 'y2',
           'width', 'height', 'stroke-width', 'stroke-miterlimit'}
COLORS = re.compile(r'(?:#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}|black|white|none)\Z')


class ProfileError(ValueError):
    pass


def number(value: str) -> float:
    if not NUM_RE.fullmatch(value):
        raise ProfileError(f'Expected unitless finite number: {value[:60]!r}')
    result = float(value)
    if not math.isfinite(result) or abs(result) > 1_000_000:
        raise ProfileError('Numeric magnitude exceeds 1,000,000 or is non-finite')
    return result


def numbers(value: str) -> list[float]:
    parts = re.split(r'[\s,]+', value.strip())
    if not parts or not all(parts):
        raise ProfileError('Empty numeric list')
    return [number(part) for part in parts]


def check_transform(value: str) -> None:
    pos = 0
    count = 0
    for match in re.finditer(r'([A-Za-z]+)\s*\(([^()]*)\)', value):
        if value[pos:match.start()].strip(' ,\t\r\n'):
            raise ProfileError('Invalid transform syntax')
        kind, args = match.groups()
        values = numbers(args)
        arities = {'matrix': {6}, 'translate': {1, 2}, 'scale': {1, 2},
                   'rotate': {1, 3}, 'skewX': {1}, 'skewY': {1}}
        if kind not in arities or len(values) not in arities[kind]:
            raise ProfileError(f'Unsupported transform or parameter count: {kind}')
        count += 1
        pos = match.end()
    if not count or count > 32 or value[pos:].strip(' ,\t\r\n'):
        raise ProfileError('Invalid or excessive transform list')


def check_path(value: str) -> None:
    # Explicit command/number tokenizer, followed by command-arity validation.
    token_re = re.compile(r'[MmZzLlHhVvCcSsQqTtAa]|' + NUMBER)
    tokens = []
    pos = 0
    for match in token_re.finditer(value):
        if value[pos:match.start()].strip(' ,\t\r\n'):
            raise ProfileError('Unrecognized path data')
        tokens.append(match.group())
        pos = match.end()
        if len(tokens) > MAX_PATH_TOKENS:
            raise ProfileError('Path token limit exceeded')
    if value[pos:].strip(' ,\t\r\n') or not tokens or tokens[0] not in {'M', 'm'}:
        raise ProfileError('Path must start with moveto and contain valid data')
    arity = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4,
             'Q': 4, 'T': 2, 'A': 7}
    i = 0
    while i < len(tokens):
        command = tokens[i]
        if len(command) != 1 or command.upper() not in set(arity) | {'Z'}:
            raise ProfileError('Path needs an explicit command after closepath')
        i += 1
        if command.upper() == 'Z':
            continue
        start = i
        while i < len(tokens) and not tokens[i].isalpha():
            i += 1
        group = tokens[start:i]
        size = arity[command.upper()]
        if not group or len(group) % size:
            raise ProfileError(f'Incorrect parameter count for {command}')
        values = [number(token) for token in group]
        if command.upper() == 'A':
            for offset in range(0, len(values), 7):
                if values[offset] < 0 or values[offset + 1] < 0:
                    raise ProfileError('Arc radii must be nonnegative')
                if group[offset + 3] not in {'0', '1'} or group[offset + 4] not in {'0', '1'}:
                    raise ProfileError('Arc flags must be literal 0 or 1 (separated)')


def read_svg(path: Path) -> bytes:
    with path.open('rb') as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ProfileError('File exceeds 1,000,000 bytes')
    return data


def inspect_svg(data: bytes):
    """Return (JSON-safe report, parsed root or None). Warnings do not fail."""
    report = {'profile': 'flat-outlined-v1', 'ok': False, 'errors': [], 'warnings': []}
    root = None
    try:
        if len(data) > MAX_BYTES:
            raise ProfileError('File exceeds 1,000,000 bytes')
        source = data.decode('utf-8-sig')
        if re.search(r'<\?xml(?!\s+version\b)', source, re.I):
            raise ProfileError('Processing instructions are unsupported')
        # Reject all PIs except the initial XML declaration, including stylesheet PIs.
        without_declaration = re.sub(r'^\s*<\?xml\s+[^?]*\?>', '', source, count=1)
        if '<?' in without_declaration:
            raise ProfileError('Processing instructions are unsupported')
        root = ET.fromstring(data, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        if root.tag != f'{{{SVG_NS}}}svg':
            raise ProfileError('Root must be svg in the SVG namespace')
        viewbox = numbers(root.get('viewBox', ''))
        if len(viewbox) != 4 or viewbox[2] <= 0 or viewbox[3] <= 0:
            raise ProfileError('viewBox needs four numbers with positive width and height')
        report['viewBox'] = viewbox
        ids = set()
        refs = []
        drawings = 0
        total_tokens = 0
        count = 0
        stack = [(root, 1)]
        while stack:
            node, depth = stack.pop()
            count += 1
            if count > MAX_ELEMENTS or depth > MAX_DEPTH:
                raise ProfileError('Element count or nesting depth limit exceeded')
            if not isinstance(node.tag, str) or not node.tag.startswith(f'{{{SVG_NS}}}'):
                raise ProfileError('Foreign or missing element namespace')
            tag = node.tag[len(SVG_NS) + 2:]
            if tag not in ALLOWED or (node is not root and tag == 'svg'):
                raise ProfileError(f'Unsupported element: {tag}')
            if tag not in {'svg', 'g'} and list(node):
                raise ProfileError(f'{tag} cannot contain child elements in this profile')
            if tag not in {'title', 'desc'} and (node.text or '').strip():
                raise ProfileError('Visible text requires outlined geometry in this profile')
            if (node.tail or '').strip():
                raise ProfileError('Unexpected text outside title/desc')
            for key, value in node.attrib.items():
                if key not in ALLOWED[tag]:
                    raise ProfileError(f'Unsupported attribute on {tag}: {key}')
                if key == 'id':
                    if not ID_RE.fullmatch(value) or value in ids:
                        raise ProfileError('Invalid or duplicate ID')
                    ids.add(value)
                elif key in {'fill', 'stroke'}:
                    if not COLORS.fullmatch(value):
                        raise ProfileError('Paint must be #RGB, #RRGGBB, black, white, or none')
                elif key in OPACITIES:
                    if not 0 <= number(value) <= 1:
                        raise ProfileError('Opacity must be in [0,1]')
                elif key in LENGTHS:
                    numeric = number(value[:-2] if tag == 'svg' and value.endswith('px') else value)
                    if key in {'r', 'rx', 'ry', 'width', 'height', 'stroke-width'} and numeric < 0:
                        raise ProfileError(f'{key} cannot be negative')
                    if tag == 'svg' and key in {'width', 'height'} and numeric <= 0:
                        raise ProfileError('Root dimensions must be positive')
                    if key == 'stroke-miterlimit' and numeric < 1:
                        raise ProfileError('stroke-miterlimit must be at least 1')
                elif key in ENUMS and value not in ENUMS[key]:
                    raise ProfileError(f'Unsupported value for {key}')
                elif key == 'transform':
                    check_transform(value)
                elif key == 'preserveAspectRatio' and value not in {'xMidYMid', 'xMidYMid meet'}:
                    raise ProfileError('Only centered meet aspect-ratio behavior is supported')
                elif key in {'aria-labelledby', 'aria-describedby'}:
                    if not value.split():
                        raise ProfileError('Empty accessibility ID reference')
                    refs.extend(value.split())
            if tag in GEOMETRY:
                drawings += 1
            if tag == 'path':
                d = node.get('d', '')
                total_tokens += len(re.findall(NUMBER, d))
                if total_tokens > MAX_PATH_TOKENS:
                    raise ProfileError('Total path coordinate limit exceeded')
                check_path(d)
            elif tag in {'polygon', 'polyline'}:
                coords = numbers(node.get('points', ''))
                if len(coords) % 2 or len(coords) < (6 if tag == 'polygon' else 4):
                    raise ProfileError('Point list needs complete coordinate pairs and enough vertices')
            elif tag == 'rect' and not {'width', 'height'} <= node.attrib.keys():
                raise ProfileError('rect requires explicit width and height')
            elif tag == 'circle' and 'r' not in node.attrib:
                raise ProfileError('circle requires r')
            elif tag == 'ellipse' and not {'rx', 'ry'} <= node.attrib.keys():
                raise ProfileError('ellipse requires rx and ry')
            stack.extend((child, depth + 1) for child in node)
        if any(ref not in ids for ref in refs):
            raise ProfileError('Unresolved accessibility ID reference')
        if not drawings:
            raise ProfileError('No geometry elements found')
        if not any(n.tag == f'{{{SVG_NS}}}title' and (n.text or '').strip() for n in root):
            report['warnings'].append('No root title; accessible naming must be supplied in the embedding context')
        report['elements'] = count
        report['geometry_elements'] = drawings
        report['warnings'].append('Manual bounds, optical, rights, and application review still required')
        report['ok'] = True
    except (ProfileError, UnicodeError, ParseError, DefusedXmlException) as exc:
        report['errors'].append(str(exc))
    return report, root


def validate_file(path: Path) -> dict:
    try:
        report, _ = inspect_svg(read_svg(path))
    except (OSError, ProfileError) as exc:
        report = {'profile': 'flat-outlined-v1', 'ok': False, 'errors': [str(exc)], 'warnings': []}
    return {'file': str(path), **report}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--json', action='store_true', help='Emit a JSON array, including for one input')
    args = parser.parse_args(argv)
    results = [validate_file(path) for path in args.files]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print(f"{'PASS' if result['ok'] else 'FAIL'} {result['file']}")
            for error in result['errors']:
                print(f'  error: {error}')
            for warning in result['warnings']:
                print(f'  warning: {warning}')
    return 0 if all(item['ok'] for item in results) else 1


if __name__ == '__main__':
    sys.exit(main())

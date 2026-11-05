#!/usr/bin/env python3
"""Check package paths, local Markdown links, metadata, source hashes, and manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

import yaml

REQUIRED = ['SKILL.md', 'agents/openai.yaml', 'README.md', 'VALIDATION.md',
            'BUILD-REPORT.md', 'requirements.txt', 'requirements-dev.txt',
            'scripts/validate_svg.py', 'scripts/render_tests.py', 'scripts/check_package.py',
            'templates/intake-brief.md', 'templates/strategy.md', 'templates/concepts.md',
            'templates/critique-scorecard.md', 'templates/brand-guidelines.md',
            'templates/handoff.md', 'tests/test_svg.py', 'tests/test_render.py']


def inside(root, target):
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def check(root: Path, require_manifest=False):
    root = root.resolve()
    errors = []
    for name in REQUIRED:
        if not (root / name).is_file():
            errors.append(f'Missing required file: {name}')
    files = sorted(path for path in root.rglob('*') if path.is_file())
    for path in root.rglob('*'):
        if path.is_symlink() or not inside(root, path):
            errors.append(f'Unsafe path: {path}')
    for path in files:
        if not inside(root, path):
            continue
        if path.suffix == '.md':
            text = path.read_text(encoding='utf-8')
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', link) or link.startswith('#'):
                    continue
                local, _, anchor = unquote(link.strip('<>')).partition('#')
                target = path.parent / local
                if not inside(root, target) or not target.is_file():
                    errors.append(f'Broken/escaping local link: {path.relative_to(root)} -> {link}')
                elif anchor and target.suffix == '.md':
                    headings = re.findall(r'^#{1,6}\s+(.+)$', target.read_text(encoding='utf-8'), re.M)
                    slugs = {re.sub(r'[^\w -]', '', h.lower()).replace(' ', '-') for h in headings}
                    if anchor not in slugs:
                        errors.append(f'Missing heading anchor: {link}')
    try:
        skill = (root / 'SKILL.md').read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---\n', skill, re.S)
        if not match:
            raise ValueError('Missing YAML frontmatter')
        meta = yaml.safe_load(match.group(1))
        if meta.get('name') != root.name or not isinstance(meta.get('description'), str):
            errors.append('Skill name/directory or description mismatch')
        if len(skill.split()) > 1500:
            errors.append('SKILL.md exceeds package entrypoint budget (1,500 words)')
        ui = yaml.safe_load((root / 'agents/openai.yaml').read_text(encoding='utf-8'))['interface']
        if not 25 <= len(ui['short_description']) <= 64 or '$brand-identity-director' not in ui['default_prompt']:
            errors.append('Invalid UI short description or default prompt')
        source_root = root / 'references/source-reports'
        manifest = json.loads((source_root / 'source-manifest.json').read_text(encoding='utf-8'))
        for entry in manifest['reports']:
            path = source_root / entry['path']
            if not inside(source_root, path):
                errors.append('Escaping source report path')
                continue
            data = path.read_bytes()
            if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
                errors.append(f'Source hash mismatch: {entry["path"]}')
    except (OSError, KeyError, ValueError, TypeError, yaml.YAMLError) as exc:
        errors.append(f'Metadata/source validation error: {exc}')
    checksum_file = root / 'MANIFEST.sha256'
    if require_manifest or checksum_file.exists():
        try:
            seen = set()
            for line in checksum_file.read_text(encoding='utf-8').splitlines():
                digest, name = line.split('  ', 1)
                target = root / name
                if name in seen or not inside(root, target) or not target.is_file():
                    errors.append(f'Invalid manifest path: {name}')
                    continue
                seen.add(name)
                if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                    errors.append(f'Checksum mismatch: {name}')
            expected = {str(p.relative_to(root)).replace('\\', '/') for p in files if p != checksum_file
                        and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts}
            if seen != expected:
                errors.append('Manifest inventory differs from package files')
        except (OSError, ValueError) as exc:
            errors.append(f'Manifest error: {exc}')
    return {'ok': not errors, 'errors': errors, 'file_count': len(files)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, nargs='?', default=Path(__file__).resolve().parents[1])
    parser.add_argument('--require-manifest', action='store_true')
    args = parser.parse_args(argv)
    result = check(args.root, args.require_manifest)
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())

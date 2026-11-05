import json
from pathlib import Path
import subprocess
import sys

import pytest

from validate_svg import MAX_BYTES, inspect_svg, validate_file

ROOT = Path(__file__).resolve().parents[1]


def wrap(body, attrs='viewBox="0 0 100 100"'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>{body}</svg>'.encode()


@pytest.mark.parametrize('body', [
    '<path d="M0 0 L10 10 Z"/>',
    '<path d="M 1e1 -2e-1 h 10 v 10 l -10 -10 z"/>',
    '<path d="M0 0 C1 2 3 4 5 6 S7 8 9 10 Q3 4 5 6 T8 9 A2 3 0 0 1 10 10 Z"/>',
    '<rect width="20" height="40" rx="3" fill="#abc"/>',
    '<circle r="10" fill="none" stroke="#000000" stroke-width="2"/>',
    '<ellipse rx="10" ry="5"/>',
    '<line x1="0" y1="0" x2="20" y2="20" stroke="black"/>',
    '<polyline points="0,0 10,10 20,0"/>',
    '<polygon points="0 0 10 10 20 0"/>',
    '<g transform="translate(2,3) rotate(20 10 10) scale(0.5)"><circle r="3"/></g>',
    '<g transform="matrix(1 0 0 1 5 6) skewX(2) skewY(3)"><circle r="3"/></g>',
])
def test_supported_geometry(body):
    report, _ = inspect_svg(wrap(body))
    assert report['ok'], report


@pytest.mark.parametrize('body', [
    '<script>alert(1)</script>',
    '<foreignObject><div>HTML</div></foreignObject>',
    '<image href="https://example.org/image.png"/>',
    '<image href="data:image/png;base64,AA=="/>',
    '<use href="#a"/>',
    '<style>@import url(https://example.org);</style>',
    '<animate attributeName="x"/>',
    '<text>Requires a font</text>',
    '<filter id="a"/>',
    '<defs><clipPath id="a"><circle r="10"/></clipPath></defs>',
    '<path d="M0 0L2 2" onload="alert(1)"/>',
    '<path d="M0 0L2 2" style="fill:url(https://example.org)"/>',
    '<path d="M0 0L2 2" class="x"/>',
    '<path d="M0 0L2 2" fill="url(#paint)"/>',
    '<path d="M0 0L2 2" fill="currentColor"/>',
    '<path xmlns:x="http://www.w3.org/1999/xlink" x:href="file:///etc/passwd" d="M0 0L2 2"/>',
    '<x:circle xmlns:x="urn:foreign" r="10"/>',
    '<g id="same"/><circle id="same" r="10"/>',
    '<circle id="bad id" r="10"/>',
    '<circle r="-1"/>',
    '<circle r="NaN"/>',
    '<circle r="1e999"/>',
    '<circle r="1000001"/>',
    '<circle r="1" opacity="1.1"/>',
    '<circle r="1" stroke-width="-1"/>',
    '<circle r="1" stroke-miterlimit="0"/>',
    '<circle r="1" stroke-linecap="pointy"/>',
    '<circle r="1" transform="translate(1) garbage"/>',
    '<circle r="1" transform="matrix(1 0 1)"/>',
    '<circle r="1" transform="url(http://example.org)"/>',
    '<rect width="10"/>', '<circle/>', '<ellipse rx="2"/>',
    '<polygon points="0 0 10"/>', '<polyline points="0 0"/>',
    '<path d="L0 0"/>', '<path d="M0"/>', '<path d="M0 0 L1"/>',
    '<path d="M0 0 X1 2"/>', '<path d="M0 0z1 2"/>',
    '<path d="M0 0 A2 3 0 2 0 4 5"/>',
    '<path d="M0 0 A-2 3 0 0 0 4 5"/>',
    '<path d="M0 0 1e999 2"/>', '<path d=""/>',
    '<circle r="1"><circle r="2"/></circle>',
    '<g>unexpected visible text<circle r="1"/></g>',
    '<svg viewBox="0 0 1 1"><circle r="1"/></svg>',
    '<title>title only</title>',
])
def test_reject_unsupported_or_malformed(body):
    report, _ = inspect_svg(wrap(body))
    assert not report['ok'], report
    assert report['errors']


@pytest.mark.parametrize('attrs', [
    '', 'viewBox="0 0 0 10"', 'viewBox="0 0 -1 10"',
    'viewBox="0 0 10"', 'viewBox="0 0 NaN 10"',
    'viewBox="0 0 10 10" width="0"',
    'viewBox="0 0 10 10" preserveAspectRatio="none"',
    'viewBox="0 0 10 10" aria-labelledby="missing"',
])
def test_root_errors(attrs):
    assert not inspect_svg(wrap('<circle r="1"/>', attrs))[0]['ok']


def test_accessible_id_reference():
    data = wrap('<title id="t">Test</title><circle r="1"/>',
                'viewBox="0 0 10 10" role="img" aria-labelledby="t"')
    assert inspect_svg(data)[0]['ok']


@pytest.mark.parametrize('data', [
    b'', b'<svg>', b'<svg xmlns="urn:wrong"/>',
    b'<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>&xxe;</title><circle r="1"/></svg>',
    b'<!DOCTYPE svg><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle r="1"/></svg>',
    b'<?xml-stylesheet href="https://example.org/style.css"?>' + wrap('<circle r="1"/>'),
    b'\xff' + wrap('<circle r="1"/>'),
])
def test_parser_safety(data):
    assert not inspect_svg(data)[0]['ok']


def test_limits():
    assert not inspect_svg(b' ' * (MAX_BYTES + 1))[0]['ok']
    assert not inspect_svg(wrap('<g>' * 33 + '<circle r="1"/>' + '</g>' * 33))[0]['ok']
    assert not inspect_svg(wrap('<circle r="1"/>' * 5001))[0]['ok']
    assert not inspect_svg(wrap('<path d="M0 0' + ' L1 1' * 26000 + '"/>'))[0]['ok']


def test_file_api_and_cli_do_not_modify_source(tmp_path):
    source = tmp_path / 'mark.svg'
    original = wrap('<rect width="10" height="10"/>')
    source.write_bytes(original)
    process = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_svg.py'),
                              str(source), '--json'], capture_output=True, text=True)
    assert process.returncode == 0
    assert json.loads(process.stdout)[0]['ok']
    assert source.read_bytes() == original
    assert not validate_file(tmp_path / 'missing.svg')['ok']


def test_cli_invalid_input_has_nonzero_json_result(tmp_path):
    source = tmp_path / 'bad.svg'
    source.write_bytes(wrap('<script/>'))
    process = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_svg.py'),
                              str(source), '--json'], capture_output=True, text=True)
    assert process.returncode == 1
    assert not json.loads(process.stdout)[0]['ok']

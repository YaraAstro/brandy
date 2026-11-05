import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image
import pytest

import render_tests
from render_tests import generate, parse_sizes
from validate_svg import ProfileError

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / 'examples/assets/sample-mark.svg'
WIDE = ROOT / 'examples/assets/wide-mark.svg'


def test_render_dimensions_backgrounds_silhouette_and_provenance(tmp_path):
    out = tmp_path / 'renders'
    result = generate(SAMPLE, out, [16, 32])
    assert result['input_sha256'] == hashlib.sha256(SAMPLE.read_bytes()).hexdigest()
    for size in [16, 32]:
        with Image.open(out / f'{size}-transparent.png') as pic:
            assert pic.size == (size, size)
            assert pic.mode == 'RGBA'
            assert pic.getchannel('A').getextrema() == (0, 255)
        with Image.open(out / f'{size}-light.png') as pic:
            assert pic.getpixel((0, 0)) == (255, 255, 255)
        with Image.open(out / f'{size}-dark.png') as pic:
            assert pic.getpixel((0, 0)) == (17, 24, 39)
        with Image.open(out / f'{size}-mono-black.png') as pic:
            assert pic.getpixel((size // 5, size // 2)) == (0, 0, 0)
        with Image.open(out / f'{size}-mono-white.png') as pic:
            assert pic.getpixel((size // 5, size // 2)) == (255, 255, 255)
        with Image.open(out / f'{size}-gray.png') as pic:
            assert pic.getchannel('R').tobytes() == pic.getchannel('G').tobytes() == pic.getchannel('B').tobytes()
    assert (out / 'contact-sheet.png').is_file()
    assert json.loads((out / 'results.json').read_text())['preserve_aspect_ratio']


def test_wide_viewbox_is_not_stretched(tmp_path):
    out = tmp_path / 'wide'
    generate(WIDE, out, [128])
    with Image.open(out / '128-transparent.png') as pic:
        box = pic.getchannel('A').getbbox()
        width, height = box[2] - box[0], box[3] - box[1]
        assert 4.4 < width / height < 5.0  # source painted bounds 190/40 = 4.75
        assert box[1] > 40  # centered in square, with top padding


def test_deterministic_png_output_and_source_preservation(tmp_path):
    before = SAMPLE.read_bytes()
    generate(SAMPLE, tmp_path / 'a', [24])
    generate(SAMPLE, tmp_path / 'b', [24])
    assert (tmp_path / 'a/24-transparent.png').read_bytes() == (tmp_path / 'b/24-transparent.png').read_bytes()
    assert SAMPLE.read_bytes() == before


def test_existing_output_is_never_overwritten(tmp_path):
    out = tmp_path / 'existing'
    out.mkdir()
    sentinel = out / 'important.txt'
    sentinel.write_text('preserve')
    with pytest.raises(ProfileError, match='already exists'):
        generate(SAMPLE, out, [16])
    assert sentinel.read_text() == 'preserve'


def test_unsafe_input_rejected_before_worker(tmp_path, monkeypatch):
    source = tmp_path / 'unsafe.svg'
    source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><image href="https://example.org"/></svg>')
    def forbidden(*args, **kwargs):
        pytest.fail('Worker should not start for rejected input')
    monkeypatch.setattr(render_tests.subprocess, 'run', forbidden)
    with pytest.raises(ProfileError):
        generate(source, tmp_path / 'out', [16])
    assert not (tmp_path / 'out').exists()


def test_empty_render_is_not_a_success(tmp_path):
    source = tmp_path / 'empty.svg'
    source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle r="0"/></svg>')
    with pytest.raises(ProfileError, match='empty'):
        generate(source, tmp_path / 'out', [16])
    assert not (tmp_path / 'out').exists()


def test_timeout_propagates_without_success_output(tmp_path, monkeypatch):
    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired('renderer', 1)
    monkeypatch.setattr(render_tests.subprocess, 'run', timed_out)
    with pytest.raises(subprocess.TimeoutExpired):
        generate(SAMPLE, tmp_path / 'out', [16], timeout=1)
    assert not (tmp_path / 'out').exists()


@pytest.mark.parametrize('bad', ['0', '16,16', '8,2048', 'abc', '', ',16', ','.join(map(str, range(8, 22)))])
def test_size_limits(bad):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_sizes(bad)


def test_cli_creates_diagnostics(tmp_path):
    out = tmp_path / 'cli'
    process = subprocess.run([sys.executable, str(ROOT / 'scripts/render_tests.py'),
                              str(SAMPLE), '--out', str(out), '--sizes', '16,32'],
                             capture_output=True, text=True)
    assert process.returncode == 0, process.stderr
    assert (out / 'results.json').exists()


def test_cli_failure_is_nonzero(tmp_path):
    process = subprocess.run([sys.executable, str(ROOT / 'scripts/render_tests.py'),
                              str(tmp_path / 'missing.svg'), '--out', str(tmp_path / 'out')],
                             capture_output=True, text=True)
    assert process.returncode == 1
    assert not (tmp_path / 'out').exists()

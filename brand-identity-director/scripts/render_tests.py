#!/usr/bin/env python3
"""Render bounded, aspect-preserving size/background diagnostics from flat SVG."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFilter, ImageOps
import resvg_py

from validate_svg import ProfileError, inspect_svg, read_svg

DEFAULT_SIZES = [16, 24, 32, 48, 64, 128, 256]
BACKGROUNDS = {'light': '#FFFFFF', 'dark': '#111827', 'neutral': '#D1D5DB'}


def parse_sizes(text):
    try:
        sizes = [int(value) for value in text.split(',')]
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Sizes must be comma-separated integers') from exc
    if not sizes or len(sizes) > 12 or len(set(sizes)) != len(sizes) or any(s < 8 or s > 1024 for s in sizes):
        raise argparse.ArgumentTypeError('Choose 1–12 unique sizes in [8,1024]')
    return sizes


def worker(source: Path, target: Path, sizes: list[int]):
    report, root = inspect_svg(read_svg(source))
    if not report['ok']:
        raise ProfileError('; '.join(report['errors']))
    _, _, width, height = report['viewBox']
    for size in sizes:
        # Fit the full viewBox into a square; no stretching or cropping.
        out_width = max(1, round(size * width / max(width, height)))
        out_height = max(1, round(size * height / max(width, height)))
        root.set('width', str(out_width))
        root.set('height', str(out_height))
        root.set('preserveAspectRatio', 'xMidYMid meet')
        data = resvg_py.svg_to_bytes(svg_string=ET.tostring(root, encoding='unicode'),
                                     width=out_width, height=out_height, skip_system_fonts=True)
        picture = Image.open(io.BytesIO(data)).convert('RGBA')
        picture.load()
        canvas = Image.new('RGBA', (size, size))
        canvas.alpha_composite(picture, ((size - picture.width) // 2, (size - picture.height) // 2))
        canvas.save(target / f'raw-{size}.png')


def composite(picture, background):
    base = Image.new('RGBA', picture.size, background)
    base.alpha_composite(picture)
    return base.convert('RGB')


def generate(source: Path, out: Path, sizes: list[int], timeout=30):
    data = read_svg(source)
    report, _ = inspect_svg(data)
    if not report['ok']:
        raise ProfileError('; '.join(report['errors']))
    if out.exists():
        raise ProfileError('Output path already exists; choose a new directory to preserve previous tests')
    # Parent receives only PNGs from a bounded child. No browser or external SVG resources.
    with tempfile.TemporaryDirectory(prefix='brand-render-') as temporary:
        scratch = Path(temporary)
        snapshot = scratch / 'input.svg'
        snapshot.write_bytes(data)
        process = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker',
                                  str(snapshot), str(scratch), '--sizes', ','.join(map(str, sizes))],
                                 capture_output=True, text=True, timeout=timeout)
        if process.returncode:
            raise ProfileError('Renderer worker failed: ' + process.stderr[-1500:])
        images = {}
        observations = []
        for size in sizes:
            with Image.open(scratch / f'raw-{size}.png') as image:
                picture = image.convert('RGBA')
                picture.load()
            alpha = picture.getchannel('A')
            bbox = alpha.getbbox()
            if bbox is None:
                raise ProfileError(f'Render is empty at {size}px')
            images[size] = picture
            observations.append({'size': size, 'canvas': [size, size], 'alpha_bbox': list(bbox),
                                 'touches_canvas_edge': bbox[0] == 0 or bbox[1] == 0 or bbox[2] == size or bbox[3] == size,
                                 'note': 'Bounds are diagnostic; touching an edge is not automatically clipping'})
        out.mkdir(parents=True, exist_ok=False)
        cell = max(sizes) + 24
        labels = ['light', 'dark', 'neutral', 'gray', 'mono-black', 'mono-white', 'blur']
        sheet = Image.new('RGB', (cell * len(labels), (cell + 20) * len(sizes)), '#F3F4F6')
        draw = ImageDraw.Draw(sheet)
        records = []
        for row, size in enumerate(sizes):
            picture = images[size]
            picture.save(out / f'{size}-transparent.png')
            records.append({'path': f'{size}-transparent.png', 'size': size, 'variant': 'transparent'})
            gray = ImageOps.grayscale(picture.convert('RGB')).convert('RGBA')
            gray.putalpha(picture.getchannel('A'))
            mono_black = Image.new('RGBA', picture.size, '#000000')
            mono_black.putalpha(picture.getchannel('A'))
            mono_white = Image.new('RGBA', picture.size, '#FFFFFF')
            mono_white.putalpha(picture.getchannel('A'))
            radius = max(0.5, size / 32)
            variants = {name: composite(picture, bg) for name, bg in BACKGROUNDS.items()}
            variants.update({'gray': composite(gray, '#FFFFFF'),
                             'mono-black': composite(mono_black, '#FFFFFF'),
                             'mono-white': composite(mono_white, '#111827'),
                             'blur': composite(picture.filter(ImageFilter.GaussianBlur(radius)), '#FFFFFF')})
            for col, name in enumerate(labels):
                rendered = variants[name]
                filename = f'{size}-{name}.png'
                rendered.save(out / filename)
                # Native-pixel-size viewing in each contact-sheet cell.
                x = col * cell + (cell - size) // 2
                y = row * (cell + 20) + 20 + (cell - size) // 2
                sheet.paste(rendered, (x, y))
                draw.text((col * cell + 6, row * (cell + 20) + 5), f'{size}px {name}', fill='#111827')
                records.append({'path': filename, 'size': size, 'variant': name})
        sheet.save(out / 'contact-sheet.png')
        records.append({'path': 'contact-sheet.png', 'variant': 'contact-sheet'})
        result = {'input_name': source.name, 'input_sha256': hashlib.sha256(data).hexdigest(),
                  'renderer': f'resvg-py {resvg_py.__version__}', 'pillow': Image.__version__,
                  'sizes_longest_edge': sizes, 'preserve_aspect_ratio': True,
                  'backgrounds': BACKGROUNDS, 'observations': observations,
                  'blur_radius': 'max(0.5,size/32) pixels',
                  'limitations': ['Monochrome uses rendered alpha, not semantic vector flattening',
                                  'Internal opaque white details merge with the silhouette',
                                  'No automated legibility, recall, contrast-conformance, legal, or print verdict',
                                  'Visual inspection is still required; contact sheet shows native pixel sizes'],
                  'files': records, 'validation': report}
        (out / 'results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('worker_out', type=Path, nargs='?', help=argparse.SUPPRESS)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--out', type=Path, default=Path('visual-tests'))
    parser.add_argument('--sizes', type=parse_sizes, default=DEFAULT_SIZES)
    parser.add_argument('--timeout', type=int, default=30, help='Worker time limit in seconds (1–60)')
    args = parser.parse_args(argv)
    if not 1 <= args.timeout <= 60:
        parser.error('--timeout must be in [1,60]')
    try:
        if args.worker:
            if args.worker_out is None:
                parser.error('Internal worker requires output directory')
            worker(args.source, args.worker_out, args.sizes)
        else:
            if args.worker_out is not None:
                parser.error('Unexpected second positional argument')
            generate(args.source, args.out, args.sizes, args.timeout)
            print(f'Wrote diagnostics: {args.out}')
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f'Render failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

from pathlib import Path
import shutil

from check_package import check, inside

ROOT = Path(__file__).resolve().parents[1]


def test_package_paths_and_sources():
    assert check(ROOT)['ok'], check(ROOT)


def test_path_containment(tmp_path):
    root = tmp_path / 'root'
    root.mkdir()
    assert inside(root, root / 'references/type.md')
    assert not inside(root, root / '../outside.md')


def test_broken_link_and_modified_source_detected(tmp_path):
    copy = tmp_path / 'brand-identity-director'
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache', 'MANIFEST.sha256'))
    (copy / 'README.md').write_text('[broken](references/missing.md)', encoding='utf-8')
    (copy / 'references/source-reports/decoding-visual-meaning.txt').write_text('changed', encoding='utf-8')
    result = check(copy)
    assert not result['ok']
    assert any('Broken/escaping' in item for item in result['errors'])
    assert any('Source hash mismatch' in item for item in result['errors'])

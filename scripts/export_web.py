#!/usr/bin/env python3
"""Export the reviewed isekai-live bundle into the existing Farmcan site."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'index.html', 'style.css', 'app.js', 'live-pair.js', 'favicon.svg', 'sources.html',
    'media/sources.json', 'media/oiia.jpg', 'media/oiia.mp4',
    'media/banana-cat.jpg', 'media/banana-cat.mp4',
    'vendor/ffmpeg.js', 'vendor/814.ffmpeg.js', 'vendor/ffmpeg-core.js',
    'vendor/ffmpeg-core.wasm.part0', 'vendor/ffmpeg-core.wasm.part1',
    'vendor/fflate.js', 'vendor/THIRD-PARTY.txt', 'vendor/COPYING.GPLv2',
    'vendor/COPYING.GPLv3', 'vendor/ffmpeg-wasm-MIT.txt', 'vendor/fflate-MIT.txt',
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', required=True, type=Path)
    args = parser.parse_args()
    source = ROOT / 'web'
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    if actual != FILES:
        raise ValueError(f'Unexpected or missing web files: {actual ^ FILES}')
    files = {}
    for name in sorted(FILES):
        path = source / name
        if path.is_symlink() or path.stat().st_size >= 25 * 1024 * 1024:
            raise ValueError(f'Unsafe web export: {name}')
        raw = path.read_bytes()
        if path.suffix in {'.html', '.js', '.json', '.css'} and 'vendor/' not in name:
            if any(marker in raw for marker in (b'/Users/', b'/home/', b'file://', b'Bearer ', b'api_key=')):
                raise ValueError(f'Private reference: {name}')
        files[name] = hashlib.sha256(raw).hexdigest()
    args.target.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        target = args.target / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
    manifest = {'source_repository': 'https://github.com/farmcan/isekai-gate',
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'reviewed_for_publication': True, 'updated': '2026-10-31', 'files': files}
    (args.target / 'build-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Exported {len(files)} reviewed files to {args.target}')

if __name__ == '__main__':
    main()

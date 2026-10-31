#!/usr/bin/env python3
"""Build the independent isekai-live Pages site from a reviewed file allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'index.html', 'style.css', 'app.js', 'live-pair.js', 'favicon.svg', 'sources.html',
    'media/public-sources.json', 'media/open-cat.mp4', 'media/open-cat.jpg',
    'media/open-cat-detail.jpg', 'media/open-cat-source.json',
    'vendor/ffmpeg.js', 'vendor/814.ffmpeg.js', 'vendor/ffmpeg-core.js',
    'vendor/ffmpeg-core.wasm.part0', 'vendor/ffmpeg-core.wasm.part1',
    'vendor/fflate.js', 'vendor/THIRD-PARTY.txt', 'vendor/COPYING.GPLv2',
    'vendor/COPYING.GPLv3', 'vendor/ffmpeg-wasm-MIT.txt', 'vendor/fflate-MIT.txt',
}
CSP = "default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; worker-src 'self' blob:; connect-src 'self' blob:; img-src 'self' blob: data:; media-src 'self' blob:; style-src 'self' 'unsafe-inline'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/standalone')
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT / 'dist' not in output.parents:
        raise ValueError('Output must be an isolated directory inside this repository dist/')
    files = {}
    for name in sorted(FILES):
        path = ROOT / 'web' / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size >= 25 * 1024 * 1024:
            raise ValueError(f'Unsafe or missing file: {name}')
        raw = path.read_bytes()
        if path.suffix in {'.html', '.js', '.json', '.css'} and not name.startswith('vendor/'):
            if any(marker in raw for marker in (b'/Users/', b'/home/', b'file://', b'Bearer ', b'api_key=')):
                raise ValueError(f'Private reference in {name}')
        files[name] = hashlib.sha256(raw).hexdigest()
    if output.exists():
        if not (output / 'build-manifest.json').exists():
            raise ValueError('Refusing to replace an unrelated output directory')
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for name in FILES:
        target = output / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / 'web' / name, target)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    manifest = {'source_repository': 'https://github.com/farmcan/isekai-gate', 'source_commit': commit,
                'site_url': 'https://isekai-live.pages.dev/', 'access': 'public',
                'reviewed_for_publication': True, 'files': files}
    (output / 'build-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (output / 'release.json').write_text(json.dumps({'git_commit': commit, 'index_sha256': files['index.html'], 'access': 'public'}) + '\n')
    (output / '_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  X-Frame-Options: DENY\n  Cache-Control: no-cache\n  Content-Security-Policy: " + CSP + "\n\n/vendor/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\n')
    print(f'Built {len(files)} reviewed assets for independent public site at {output}')

if __name__ == '__main__':
    main()

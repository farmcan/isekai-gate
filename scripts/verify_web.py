#!/usr/bin/env python3
"""Verify exact protected isekai-live production bytes and anonymous denial."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base', default='https://farmcan.pages.dev')
parser.add_argument('--dist', type=Path, default=Path('dist'))
args = parser.parse_args()
assert re.fullmatch(r'https://(?:[a-f0-9]+\.)?farmcan\.pages\.dev', args.base)
token = os.environ['SITE_ACCESS_TOKEN']
manifest = json.loads((args.dist / 'isekai-live/build-manifest.json').read_text())

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def get(route, authenticated=False, etag=None):
    headers = {'User-Agent': 'Mozilla/5.0 isekai-live-verification', 'Cache-Control': 'no-cache'}
    if authenticated:
        headers['Authorization'] = 'Bearer ' + token
    if etag:
        headers['If-None-Match'] = etag
    request = urllib.request.Request(args.base + route, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.build_opener(NoRedirect()).open(request, timeout=40) as response:
                return response.status, response.read(), response.headers
        except urllib.error.HTTPError as response:
            return response.code, response.read(), response.headers
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)

def verify(name):
    route = '/isekai-live/' + name.removesuffix('index.html').removesuffix('.html')
    code, body, headers = get(route)
    if args.base != 'https://farmcan.pages.dev' and code == 302:
        assert '.cloudflareaccess.com/' in headers.get('Location', ''), route
        return 'edge_protected'
    assert code == 401 and b'type="password"' in body, (route, 'anonymous', code)
    assert 'no-store' in headers.get('Cache-Control', ''), route
    code, body, headers = get(route, True)
    assert code == 200, (route, 'authenticated', code)
    expected = (args.dist / 'isekai-live' / name).read_bytes()
    if name.endswith('.html'):
        body = body.replace(b'<script data-site-access src="/__auth/share.js" defer></script>', b'')
    assert hashlib.sha256(body).digest() == hashlib.sha256(expected).digest(), (name, 'hash')
    if name == 'index.html':
        csp = headers.get('Content-Security-Policy', '')
        assert "'wasm-unsafe-eval'" in csp and "worker-src 'self' blob:" in csp
    if name == 'app.js':
        assert headers.get('ETag')
        assert get(route, True, headers['ETag'])[0] == 304
        assert get(route, False, headers['ETag'])[0] == 401
    return 'verified'

with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(verify, [*manifest['files'], 'build-manifest.json']))
if args.base == 'https://farmcan.pages.dev':
    code, home, _ = get('/', True)
    assert code == 200 and b'https://farmcan.pages.dev/isekai-live/' in home
    code, raw, _ = get('/release.json', True)
    release = json.loads(raw)
    assert release == json.loads((args.dist / 'release.json').read_text())
    clean = home.replace(b'<script data-site-access src="/__auth/share.js" defer></script>', b'')
    assert hashlib.sha256(clean).hexdigest() == release['index_sha256']
    code, review, _ = get('/reviews/isekai-live/', True)
    assert code == 200 and 'PHLivePhoto'.encode() in review
print(json.dumps({'site': args.base, 'source_commit': manifest['source_commit'],
                  'authenticated_hashes': results.count('verified'),
                  'anonymous_denied': results.count('verified'),
                  'edge_protected': results.count('edge_protected')}, ensure_ascii=False))

#!/usr/bin/env python3
"""Verify independent production bytes, access policy, and explicit public scope."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import ssl
import time
import urllib.error
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base', default='https://isekai-live.pages.dev')
parser.add_argument('--dist', type=Path, default=Path('dist/standalone'))
args = parser.parse_args()
assert re.fullmatch(r'https://(?:[a-f0-9]+\.)?isekai-live\.pages\.dev', args.base)
manifest = json.loads((args.dist / 'build-manifest.json').read_text())
private = manifest['access'] == 'private'
token = os.environ.get('SITE_ACCESS_TOKEN')
if private and not token:
    raise RuntimeError('Verification credential required for private publication')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def get(route, authenticated=False, etag=None):
    headers = {'User-Agent': 'Mozilla/5.0 isekai-live-production-verification', 'Cache-Control': 'no-cache'}
    if authenticated and private:
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
        except (urllib.error.URLError, ssl.SSLError, TimeoutError, ConnectionError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)

def verify(name):
    route = '/' + name.removesuffix('index.html').removesuffix('.html')
    code, body, headers = get(route)
    if code == 302 and args.base != 'https://isekai-live.pages.dev':
        assert '.cloudflareaccess.com/' in headers.get('Location', '')
        return 'edge_protected'
    if private:
        assert code == (200 if route == '/' else 401) and b'type="password"' in body, (route, 'anonymous', code)
        code, body, headers = get(route, True)
    assert code == 200, (route, code)
    expected = (args.dist / name).read_bytes()
    if private and name.endswith('.html'):
        body = body.replace(b'<script data-site-access src="/__auth/share.js" defer></script>', b'')
    assert hashlib.sha256(body).digest() == hashlib.sha256(expected).digest(), (name, 'hash')
    if name == 'index.html':
        assert "'wasm-unsafe-eval'" in headers.get('Content-Security-Policy', '')
        assert b'farmcan.pages.dev' not in body and b'/tasks/' not in body
    return 'verified'

with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(verify, [*manifest['files'], 'build-manifest.json', 'release.json']))
if args.base == 'https://isekai-live.pages.dev':
    code, raw, _ = get('/release.json', private)
    assert code == 200 and json.loads(raw) == json.loads((args.dist / 'release.json').read_text())
    code, raw, headers = get('/app.js', private)
    if headers.get('ETag'):
        assert get('/app.js', private, headers['ETag'])[0] == 304
        if private:
            assert get('/app.js', False, headers['ETag'])[0] == 401
    assert not any('oiia' in name or 'banana-cat' in name for name in manifest['files'])
print(json.dumps({'site': args.base, 'commit': manifest['source_commit'], 'access': manifest['access'],
                  'verified_asset_hashes': results.count('verified'), 'edge_protected': results.count('edge_protected'),
                  'private_navigation_absent': True, 'sample_scope': 'explicit CC0 demonstration only'}, ensure_ascii=False))

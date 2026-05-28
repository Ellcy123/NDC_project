#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AVG Editor server — Phase 0
读取 d:/NDC/Assets/table/*.json，提供 HTTP 接口给前端。
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

# 复用 preview_new2 的 fix_json
HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.normpath(os.path.join(HERE, '..', 'preview_new2'))
sys.path.insert(0, PREVIEW_DIR)
from state_to_preview import fix_json  # noqa: E402

TABLE_DIR = r"D:\NDC\Assets\table"
STATIC_DIR = os.path.join(HERE, 'static')
PORT = 9528

TABLES = {}


def load_all_tables():
    if not os.path.isdir(TABLE_DIR):
        print(f"[ERR] TABLE_DIR not found: {TABLE_DIR}", file=sys.stderr)
        sys.exit(1)
    for fn in sorted(os.listdir(TABLE_DIR)):
        if not fn.endswith('.json'):
            continue
        if fn.endswith('.bak.json') or '.bak.' in fn:
            continue
        name = fn[:-5]
        path = os.path.join(TABLE_DIR, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                raw = f.read()
            data = json.loads(fix_json(raw))
            TABLES[name] = data
            n = len(data) if isinstance(data, list) else 'obj'
            print(f"  loaded {name}: {n}")
        except Exception as e:
            print(f"  [WARN] failed {name}: {e}")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write(f"  {self.command} {self.path}\n")

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        if not os.path.isfile(path):
            self.send_response(404)
            self.end_headers()
            return
        with open(path, 'rb') as f:
            body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)

        if path == '/api/tables':
            return self._send_json(sorted(TABLES.keys()))

        if path.startswith('/api/table/'):
            name = path[len('/api/table/'):]
            if name in TABLES:
                return self._send_json(TABLES[name])
            return self._send_json({'error': f'table {name} not found'}, 404)

        if path == '/' or path == '/index.html':
            return self._send_file(os.path.join(STATIC_DIR, 'index.html'),
                                   'text/html; charset=utf-8')

        if path.startswith('/static/'):
            rel = path[len('/static/'):]
            fp = os.path.normpath(os.path.join(STATIC_DIR, rel))
            if not fp.startswith(STATIC_DIR):
                self.send_response(403)
                self.end_headers()
                return
            ext = os.path.splitext(fp)[1].lower()
            ct = {
                '.html': 'text/html; charset=utf-8',
                '.js': 'application/javascript; charset=utf-8',
                '.css': 'text/css; charset=utf-8',
                '.json': 'application/json; charset=utf-8',
                '.svg': 'image/svg+xml',
                '.png': 'image/png',
            }.get(ext, 'application/octet-stream')
            return self._send_file(fp, ct)

        self.send_response(404)
        self.end_headers()


def main():
    print(f"[avg_editor] loading tables from {TABLE_DIR}")
    load_all_tables()
    print(f"[avg_editor] {len(TABLES)} tables loaded")
    print(f"[avg_editor] serving on http://localhost:{PORT}")
    srv = ThreadingHTTPServer(('localhost', PORT), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[avg_editor] shutting down")


if __name__ == '__main__':
    main()

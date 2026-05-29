#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AVG Editor server — Phase 0
读取 d:/NDC/Assets/table/*.json，提供 HTTP 接口给前端。
"""

import json
import os
import shutil
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

# 每张表的主键字段（默认 'id'）
TABLE_PK = {
    'SceneConfig': 'sceneId',
}

# 允许编辑的字段白名单
EDITABLE_FIELDS = {
    'SceneConfig':    {'ArtRequirement', 'openInLoops', 'sceneCategory', 'note'},
    'NPCStaticData':  {'ArtRequirement', 'Name', 'role', 'Chapter'},
    'ItemStaticData': {'ArtRequirement', 'Name', 'itemType', 'description', 'itemUseDes',
                       'canAnalyzed', 'canCombined', 'iconPath', 'folderPath', 'ActionParam'},
    'MapConfig':      {'ArtRequirement', 'Name'},
    'ChapterConfig':  {'ArtRequirement', 'chapterTitle', 'chapterBrief', 'chapterGoal',
                       'summaryTitle', 'summaryContent', 'newDoubtTitle', 'newDoubtContent'},
    'DoubtConfig':    {'text', 'isFragment'},
    'TestimonyItem':  {'testimony', 'truth', 'shortDesc', 'shortTruth',
                       'testimonyType', 'triggerType', 'triggerParam'},
    'Testimony':      {'words', 'chapter'},
    'ArtAssetConfig': {'ArtRequirement', 'displayName'},
}

# 复用 preview_new2 的 fix_json
HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.normpath(os.path.join(HERE, '..', 'preview_new2'))
sys.path.insert(0, PREVIEW_DIR)
from state_to_preview import fix_json  # noqa: E402

TABLE_DIR = os.path.join(HERE, 'data', 'table')
STATIC_DIR = os.path.join(HERE, 'static')
PORT = 9528

TABLES = {}


def load_all_tables():
    if not os.path.isdir(TABLE_DIR):
        print(f"[ERR] TABLE_DIR not found: {TABLE_DIR}", file=sys.stderr)
        print(f"[ERR] 先跑 seed.py 生成数据：python seed.py", file=sys.stderr)
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
                # 我们自己写出来的 JSON 是标准格式，不需要 fix_json
                data = json.load(f)
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

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        if path != '/api/save':
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length).decode('utf-8'))
        except Exception as e:
            return self._send_json({'error': f'invalid JSON: {e}'}, 400)

        name = body.get('table')
        entry_id = body.get('id')
        changes = body.get('changes') or {}

        if name not in TABLES:
            return self._send_json({'error': f'unknown table: {name}'}, 404)
        if name not in EDITABLE_FIELDS:
            return self._send_json({'error': f'table {name} not editable'}, 403)

        pk = TABLE_PK.get(name, 'id')
        allowed = EDITABLE_FIELDS[name]
        bad = [k for k in changes.keys() if k not in allowed]
        if bad:
            return self._send_json({'error': f'fields not editable: {bad}'}, 403)

        # 找到条目
        data = TABLES[name]
        target = None
        for entry in data:
            if str(entry.get(pk)) == str(entry_id):
                target = entry
                break
        if target is None:
            return self._send_json({'error': f'entry {entry_id} not found'}, 404)

        # 备份
        src = os.path.join(TABLE_DIR, name + '.json')
        if os.path.exists(src):
            bak = src + f'.bak.{time.strftime("%Y%m%d_%H%M%S")}'
            shutil.copy2(src, bak)

        # 应用变更
        for k, v in changes.items():
            target[k] = v

        # 写回
        with open(src, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return self._send_json({'ok': True, 'id': entry_id, 'updated': list(changes.keys())})


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

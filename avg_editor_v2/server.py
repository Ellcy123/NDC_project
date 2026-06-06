#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AVG Editor v2 — fork of preview_new2 with edit capability.

服务：
  GET /                  → index.html
  GET /js-yaml.min.js    → 同目录依赖
  GET /data/*            → ./data/*
  GET /Assets/*          → D:/NDC/Assets/* （Unity 美术资源）
  GET /AVG/*             → D:/NDC_project/AVG/* （对话文件）
  GET /api/tables        → 配表列表
  GET /api/table/<name>  → 配表内容
  POST /api/save         → 写回单条配表条目（设计期字段编辑入口）
"""

import json
import os
import shutil
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE_DIR = os.path.join(HERE, 'data', 'table')
NDC_ASSETS_DIR = r"D:\NDC\Assets"
AVG_DIR = os.path.join(HERE, '..', 'AVG')
PORT = 9529

TABLES = {}

# 每张表的主键字段（默认 'id'）
TABLE_PK = {
    'SceneConfig': 'sceneId',
}

# 允许编辑的字段白名单
EDITABLE_FIELDS = {
    'SceneConfig':    {'isOpen', 'loop', 'note'},
    'NPCStaticData':  {'ArtRequirement', 'Name', 'role', 'Chapter'},
    'ItemStaticData': {'ArtRequirement', 'Name', 'itemType', 'description', 'itemUseDes',
                       'canAnalyzed', 'canCombined', 'iconPath', 'folderPath', 'ActionParam',
                       'obtainMethod'},
    'MapConfig':      {'ArtRequirement', 'Name'},
    'ChapterConfig':  {'ArtRequirement', 'chapterTitle', 'chapterBrief', 'chapterGoal',
                       'openingBrief', 'summaryTitle', 'summaryContent',
                       'newDoubtTitle', 'newDoubtContent', 'postExposeSegments'},
    'DoubtConfig':    {'text', 'isFragment'},
    'TestimonyItem':  {'testimony', 'truth', 'shortDesc', 'shortTruth',
                       'testimonyType', 'triggerType', 'triggerParam'},
    'Testimony':      {'words', 'chapter'},
    'ArtAssetConfig': {'ArtRequirement', 'displayName', 'Name', 'sceneKind', 'exposeReuseLoops'},
}


def load_all_tables():
    if not os.path.isdir(TABLE_DIR):
        print(f"[ERR] TABLE_DIR 不存在: {TABLE_DIR}", file=sys.stderr)
        print("[ERR] 先到 avg_editor/ 跑 python seed.py 生成数据，然后把数据复制到这里", file=sys.stderr)
        sys.exit(1)
    for fn in sorted(os.listdir(TABLE_DIR)):
        if not fn.endswith('.json') or '.bak.' in fn:
            continue
        name = fn[:-5]
        path = os.path.join(TABLE_DIR, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            TABLES[name] = data
            n = len(data) if isinstance(data, list) else 'obj'
            print(f"  loaded {name}: {n}")
        except Exception as e:
            print(f"  [WARN] failed {name}: {e}")


def _resolve_mount(path):
    """把 URL path 解析成 (file_path, content_type) 或 None。"""
    # /Assets/* → D:/NDC/Assets/*
    if path.startswith('/Assets/'):
        rel = path[len('/Assets/'):]
        fp = os.path.normpath(os.path.join(NDC_ASSETS_DIR, rel))
        if not fp.startswith(NDC_ASSETS_DIR):
            return None
        return fp
    # /AVG/* → ../AVG/*
    if path.startswith('/AVG/'):
        rel = path[len('/AVG/'):]
        fp = os.path.normpath(os.path.join(AVG_DIR, rel))
        avg_root = os.path.normpath(AVG_DIR)
        if not fp.startswith(avg_root):
            return None
        return fp
    # 其他：相对 HERE 的静态文件
    fp = os.path.normpath(os.path.join(HERE, path.lstrip('/')))
    if not fp.startswith(HERE):
        return None
    return fp


def _content_type(path):
    ext = os.path.splitext(path)[1].lower()
    return {
        '.html': 'text/html; charset=utf-8',
        '.js':   'application/javascript; charset=utf-8',
        '.css':  'text/css; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
        '.yaml': 'text/yaml; charset=utf-8',
        '.yml':  'text/yaml; charset=utf-8',
        '.md':   'text/markdown; charset=utf-8',
        '.png':  'image/png',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg':  'image/svg+xml',
        '.webp': 'image/webp',
    }.get(ext, 'application/octet-stream')


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
            self.send_response(404); self.end_headers(); return
        with open(path, 'rb') as f:
            body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)

        # API
        if path == '/api/tables':
            return self._send_json(sorted(TABLES.keys()))
        if path.startswith('/api/table/'):
            name = path[len('/api/table/'):]
            if name in TABLES:
                return self._send_json(TABLES[name])
            return self._send_json({'error': f'table {name} not found'}, 404)

        # Root → index.html
        if path == '/' or path == '':
            return self._send_file(os.path.join(HERE, 'index.html'),
                                   'text/html; charset=utf-8')

        # 普通静态文件 / 挂载点
        fp = _resolve_mount(path)
        if fp is None:
            self.send_response(403); self.end_headers(); return
        return self._send_file(fp, _content_type(fp))

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

        data = TABLES[name]
        target = None
        for entry in data:
            if str(entry.get(pk)) == str(entry_id):
                target = entry; break
        if target is None:
            return self._send_json({'error': f'entry {entry_id} not found'}, 404)

        src = os.path.join(TABLE_DIR, name + '.json')
        if os.path.exists(src):
            bak = src + f'.bak.{time.strftime("%Y%m%d_%H%M%S")}'
            shutil.copy2(src, bak)

        for k, v in changes.items():
            target[k] = v

        with open(src, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return self._send_json({'ok': True, 'id': entry_id, 'updated': list(changes.keys())})


def main():
    print(f"[avg_editor_v2] table dir: {TABLE_DIR}")
    load_all_tables()
    print(f"[avg_editor_v2] {len(TABLES)} tables loaded")
    print(f"[avg_editor_v2] mount /Assets → {NDC_ASSETS_DIR}")
    print(f"[avg_editor_v2] mount /AVG → {os.path.normpath(AVG_DIR)}")
    print(f"[avg_editor_v2] serving on http://localhost:{PORT}")
    srv = ThreadingHTTPServer(('localhost', PORT), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[avg_editor_v2] shutting down")


if __name__ == '__main__':
    main()

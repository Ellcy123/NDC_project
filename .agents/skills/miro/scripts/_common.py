"""Shared Miro API helpers."""
import os, sys, time, json, urllib.parse
import requests

def load_env():
    """Load .env from skill directory. Returns dict."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if not os.path.exists(env_path):
        print(f'ERROR: .env not found at {env_path}', file=sys.stderr)
        print('Create it with:', file=sys.stderr)
        print('  MIRO_API_TOKEN=...', file=sys.stderr)
        print('  MIRO_BOARD_ID=...', file=sys.stderr)
        sys.exit(1)
    env = {}
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    if 'MIRO_API_TOKEN' not in env or 'MIRO_BOARD_ID' not in env:
        print('ERROR: .env must contain MIRO_API_TOKEN and MIRO_BOARD_ID', file=sys.stderr)
        sys.exit(1)
    return env

ENV = load_env()
TOKEN = ENV['MIRO_API_TOKEN']
BOARD_ID = ENV['MIRO_BOARD_ID']
BOARD_ENC = urllib.parse.quote(BOARD_ID, safe='')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}
MINDMAP_BASE = f'https://api.miro.com/v2-experimental/boards/{BOARD_ENC}/mindmap_nodes'

# 全局 session 复用连接
SESSION = requests.Session()

def api(method, url, json_body=None, max_retries=5, timeout=20):
    """Call Miro API with retry on 429 / transient errors. Returns (status, data_or_text)."""
    for attempt in range(max_retries):
        try:
            r = SESSION.request(method, url, headers=HEADERS, json=json_body, timeout=timeout)
            if r.status_code in (200, 201, 204):
                try: return r.status_code, r.json() if r.text else {}
                except: return r.status_code, r.text
            if r.status_code == 429:
                wait = min(60, 2 ** attempt)
                print(f'  429 rate limit, sleep {wait}s', flush=True)
                time.sleep(wait)
                continue
            if r.status_code == 404:
                return 404, r.text
            if attempt == max_retries - 1:
                return r.status_code, r.text
            time.sleep(2 ** attempt)
        except Exception as e:
            if attempt == max_retries - 1:
                return -1, f'{type(e).__name__}: {e}'
            time.sleep(2 ** attempt)
    return -1, 'max retries exceeded'

def fetch_all_mindmap_nodes():
    """Paginate through all mindmap nodes on the board."""
    all_nodes = []
    cursor = None
    for page in range(50):
        u = MINDMAP_BASE + (f'?limit=50&cursor={cursor}' if cursor else '?limit=50')
        status, data = api('GET', u)
        if status != 200:
            print(f'page {page+1} failed: {status}')
            break
        items = data.get('data', [])
        all_nodes.extend(items)
        cursor = data.get('cursor')
        if not cursor or not items: break
        time.sleep(0.2)
    return all_nodes

def node_content(n):
    """Extract plain text from a mindmap node dict."""
    c = n.get('data', {}).get('nodeView', {}).get('data', {}).get('content', '')
    return c.replace('<p>', '').replace('</p>', '').strip()

def build_children_map(nodes):
    """Returns dict: parent_id -> [child_id, ...]."""
    m = {}
    for n in nodes:
        pid = n.get('parent', {}).get('id')
        if pid: m.setdefault(pid, []).append(n['id'])
    return m

def collect_subtree_ids(root_id, children_of):
    """BFS from root_id, return list of all descendant IDs (including root)."""
    result = [root_id]
    stack = [root_id]
    while stack:
        cur = stack.pop()
        for cid in children_of.get(cur, []):
            result.append(cid)
            stack.append(cid)
    return result

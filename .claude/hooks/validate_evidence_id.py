"""
写入证据相关文件时，检查新增的 4 位证据 ID 是否与已有 ItemStaticData 冲突
级别: ERROR（硬拦截——ID冲突是严重问题）

关键设计: 只检查"新增"的 ID（diff-aware）
  - Edit 操作: 对比 new_string vs old_string，只检查 new_string 中新出现的 ID
  - Write 操作: 对比新内容 vs 已有文件内容，只检查新增的 ID
"""
import json, re, os, sys

# 读取 stdin JSON
try:
    stdin_data = json.loads(sys.stdin.buffer.read().decode('utf-8'))
except Exception:
    sys.exit(0)

file_path = stdin_data.get('file_path', '')
if not file_path:
    sys.exit(0)

# 只检查证据相关文件
if not any(kw in file_path for kw in ['ItemStaticData', '证据设计', '证据美术']):
    sys.exit(0)

# 如果修改的就是 ItemStaticData.json 本身，跳过
if os.path.basename(file_path) == 'ItemStaticData.json':
    sys.exit(0)

# 项目根目录 = hook文件所在目录的上两级
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 读取已有的证据 ID 库
item_json = os.path.join(project_dir, 'preview_new2', 'data', 'table', 'ItemStaticData.json')
if not os.path.exists(item_json):
    sys.exit(0)

try:
    with open(item_json, encoding='utf-8') as f:
        items = json.load(f)
    existing_ids = {str(item['id']) for item in items if 'id' in item}
except Exception:
    sys.exit(0)


def extract_ids(text):
    """提取文本中的 4 位证据 ID"""
    patterns = [
        r'证据编号[：:]\s*(\d{4})',
        r'\|\s*(\d{4})\s*\|',
        r'(?:^|\s)id[：:\s]+["\']?(\d{4})["\']?',
        r'-\s*id:\s*(\d{4})',
    ]
    ids = set()
    for pat in patterns:
        ids.update(re.findall(pat, text, re.MULTILINE))
    return ids


# 判断操作类型并提取"新增"ID
new_string = stdin_data.get('new_string', '')
old_string = stdin_data.get('old_string', '')
content = stdin_data.get('content', '')

if new_string:
    # Edit 操作: 只检查 new_string 中新出现的 ID
    new_ids = extract_ids(new_string) - extract_ids(old_string)
elif content:
    # Write 操作: 对比新内容与已有文件
    new_ids = extract_ids(content)
    if os.path.exists(file_path):
        try:
            with open(file_path, encoding='utf-8') as f:
                old_content = f.read()
            new_ids -= extract_ids(old_content)
        except Exception:
            pass
else:
    sys.exit(0)

if not new_ids:
    sys.exit(0)

# 检查新增 ID 是否与已有证据冲突
conflicts = new_ids & existing_ids
if conflicts:
    sorted_conflicts = sorted(conflicts)
    print(f'ERROR: 证据 ID 冲突！新增的以下 ID 已存在于 ItemStaticData: {sorted_conflicts}')
    print(f'  请分配新的 ID（参考编码规则: EPI01=1xxx, EPI02=2xxx, EPI03=3xxx）')
    sys.exit(1)

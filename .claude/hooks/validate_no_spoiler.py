"""
检测 Zack 台词中的结论性语言（违反"悬疑感优先"原则）
级别: WARNING（不阻断——指证击破后 Zack 可能合理地说出结论）
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

# 只检查对话草稿和生成草稿
if not any(kw in file_path for kw in ['对话草稿', '生成草稿']):
    sys.exit(0)

# 新文件跳过
if not os.path.exists(file_path):
    sys.exit(0)

with open(file_path, encoding='utf-8') as f:
    lines = f.readlines()

# 结论性短语黑名单
spoiler_phrases = [
    r'所以这说明',
    r'由此可见',
    r'这证明了',
    r'这意味着',
    r'换句话说',
    r'也就是说',
    r'真相是',
    r'答案很明显',
    r'不难看出',
    r'可以确定',
    r'一切都指向',
    r'显而易见',
    r'这就解释了',
    r'事实上就是',
    r'毫无疑问',
    r'很明显就是',
    r'肯定是.*的',
    r'必定是',
    r'说白了就是',
]
pattern = '|'.join(spoiler_phrases)

# 提取 Zack 台词
# 格式: **扎克·布伦南** [...] 下一行 > 台词
found = []
for i, line in enumerate(lines):
    if re.match(r'\*\*扎克', line):
        for j in range(i + 1, min(i + 5, len(lines))):
            if lines[j].startswith('>'):
                dialogue = lines[j][1:].strip()
                m = re.search(pattern, dialogue)
                if m:
                    line_num = j + 1
                    preview = dialogue[:60] + ('...' if len(dialogue) > 60 else '')
                    found.append(f'  L{line_num}: "{preview}" (触发词: {m.group()})')
            elif lines[j].strip() and not lines[j].startswith('>'):
                break

if found:
    print('WARNING [悬疑感] Zack台词中检测到结论性语言:')
    for f in found:
        print(f)

# 永远 exit 0（WARNING 不阻断）
sys.exit(0)

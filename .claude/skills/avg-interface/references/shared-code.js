// =============================================================
//  NDC AVG Interface — 公用代码片段
//  新页面必须内联以下代码（因为是独立 HTML，无法 import）
//  从 index.html 提取，保持同步
// =============================================================

// ===== 路径配置（自动区分 local / deploy）=====
const Config = {
    get mode() {
        const h = location.hostname;
        return (h === 'localhost' || h === '127.0.0.1' || location.protocol === 'file:') ? 'local' : 'deploy';
    },
    get paths() {
        if (this.mode === 'deploy') {
            return {
                tableData: '/preview_new2/data/table',
                loopConfig: '/preview_new2/data',
                assets: '/Assets/Resources',
                avgData: '/AVG'
            };
        }
        return {
            tableData: '/NDC_project/preview_new2/data/table',
            loopConfig: '/NDC_project/preview_new2/data',
            assets: '/NDC/Assets/Resources',
            avgData: '/NDC_project/AVG'
        };
    },
    getAssetUrl(configPath) {
        if (!configPath) return '';
        return `${this.paths.assets}/${configPath.replace(/\\/g, '/')}.png`;
    }
};

// ===== JSON 修复器（处理游戏导出的非标准 JSON）=====
function fixJson(text) {
    let out = '';
    let inStr = false;
    for (let i = 0; i < text.length; i++) {
        const c = text.charAt(i);
        if (!inStr) {
            out += c;
            if (c === '"') inStr = true;
            continue;
        }
        if (c === '\\') {
            const nx = text.charAt(i + 1);
            if ('"\\\/bfnrt'.includes(nx)) {
                out += c + nx; i++;
            } else if (nx === 'u' && /^[0-9a-fA-F]{4}$/.test(text.substring(i + 2, i + 6))) {
                out += text.substring(i, i + 6); i += 5;
            } else {
                out += '\\\\';
            }
        } else if (c === '"') {
            const nx = text.charAt(i + 1);
            if (nx === '' || ',:]}'.includes(nx)) {
                out += c; inStr = false;
            } else if (' \t\r\n'.includes(nx)) {
                let j = i + 1;
                while (j < text.length && ' \t\r\n'.includes(text.charAt(j))) j++;
                const after = text.charAt(j);
                if (after === '' || ',:]}'.includes(after)) {
                    out += c; inStr = false;
                } else {
                    out += '\\"';
                }
            } else {
                out += '\\"';
            }
        } else if (c === '\n') {
            out += '\\n';
        } else if (c === '\r') {
            // skip CR
        } else {
            out += c;
        }
    }
    return out;
}

// ===== 数据加载器 =====
async function loadJSON(path) {
    const resp = await fetch(path);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${path}`);
    const text = await resp.text();
    return JSON.parse(fixJson(text));
}

async function loadYAML(path) {
    const resp = await fetch(`${path}?t=${Date.now()}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${path}`);
    return jsyaml.load(await resp.text());
}

// ===== 通用工具 =====
function cn(field) {
    if (Array.isArray(field)) return field[0] || '';
    return field || '';
}

function stripPrefix(id) {
    if (id == null) return '';
    id = String(id);
    if (id.startsWith('EV')) return id.slice(2);
    if (id.startsWith('SC')) return id.slice(2);
    if (id.startsWith('NPC')) return id.slice(3);
    return id;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}

// ===== 对话链解析 =====
function getDialogueChain(startId, talksMap) {
    const chain = [];
    let current = talksMap.get(String(startId));
    const visited = new Set();
    while (current && !visited.has(current.id)) {
        visited.add(current.id);
        chain.push(current);
        if (!current.next) break;
        current = talksMap.get(String(current.next));
    }
    return chain;
}

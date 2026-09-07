// Refresh art entries from the canonical source registry, preserving unrelated entries.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
const target = path.join(root, 'skill_dashboard/skills-data.js');
const source = JSON.parse(fs.readFileSync(path.join(root, 'production/art_pipeline/skill_sources.json'), 'utf8'));
if (source.schema !== 'ndc-art-skill-sources/v2') throw new Error('Expected portable skill registry v2');
const localFile = path.join(root, 'ndc.local.json');
const local = fs.existsSync(localFile) ? JSON.parse(fs.readFileSync(localFile, 'utf8').replace(/^\uFEFF/, '')) : {};
const roots = { planning: root, engine: process.env.NDC_ENGINE_ROOT || local.engine_root };
if (!roots.engine || !path.isAbsolute(roots.engine)) {
  throw new Error('Configure repository paths first: python scripts/art_pipeline/ndc_art.py configure --help');
}
const context = { window: {} };
vm.runInNewContext(fs.readFileSync(target, 'utf8'), context, { timeout: 1000 });
const catalog = context.window.SKILL_CATALOG;
// Convert the original offline catalog once; persist only logical repository locators.
for (const skill of catalog.skills) {
  if (!['planning', 'engine'].includes(skill.project)) {
    const oldRoot = skill.project.replace(/\\/g, '/').replace(/\/$/, '');
    const oldPath = skill.path.replace(/\\/g, '/');
    if (!oldPath.startsWith(oldRoot + '/')) throw new Error(`Invalid original catalog path: ${skill.name}`);
    skill.project = oldRoot.endsWith('/NDC_project') ? 'planning' : 'engine';
    skill.path = oldPath.slice(oldRoot.length + 1);
  }
}
const retiredNames = new Set((source.retired_skills || []).map(entry => entry.name));
catalog.skills = catalog.skills.filter(entry => !retiredNames.has(entry.name));
const descriptions = {
  'ndc-generate-characters': ['角色与表情', '角色设计', '制作角色卡和所需肖像；已有角色按明确版本锁定身份。'],
  'ndc-generate-expressions': ['角色与表情', '表情制作', '从已确认肖像制作可复用表情套图和透明/绿幕素材。'],
  'ndc-character-scene-integration': ['场景出图', '人物入景', '依据实际台词、站位和对话框遮挡，把已确定角色放入固定场景。'],
  'ndc-multichar-avg-production': ['场景出图', '多人编排', '用站位白盒编排两人及以上 AVG 场景，再逐角色制作与验收。'],
  'ndc-avg-character-scene-art': ['场景出图', 'AVG 人物层', '制作固定机位 AVG 人物透明层、场景合成和工程所需分层包。'],
  'ndc-free-exploration-character-art': ['场景出图', '探索人物层', '制作探索场景人物两态和按角色轮廓打包的透明素材。'],
  'ndc-coordinate-image-edit': ['场景出图', '局部修图', '在授权区域内进行像素坐标锁定的修图、合成与边界校验。'],
  'ndc-scene-to-mj-prompt': ['场景出图', '提示词设计', '按 v3 无人物场景流程生成 MJ 提示词与生产交接包。'],
  'ndc-midjourney-operator': ['场景出图', 'MJ 执行', '执行 v3 场景交接包，并按需求审核候选和规划后处理。'],
  'ndc-scene-evidence-placement': ['道具出图', '美术同学维护', '道具制作主入口：场景点击图、容器、Big/Icon 与完整交付检查。机器路径按公共工作区规则。'],
  'ndc-evidence-scene-placement': ['道具出图', '旧接口待同步', '旧场景子流程；与新版主流程的打包参数不兼容，暂不独立执行。'],
  'ndc-evidence-container': ['道具出图', '旧接口待同步', '旧容器子流程；接口与发布合同待美术同学同步，暂不独立执行。'],
  'ndc-evidence-detail-art': ['道具出图', '旧接口待同步', '旧细节子流程；文字处理规则与新版冲突，暂不独立执行。'],
  'generate-ndc-emergency-art': ['场景出图', '突发事件', '按剧情事件要求制作突发事件与闪回所需画面。'],
  'runninghub-h3-greenscreen-avatar': ['数字人与语音', '数字人制作', '工程侧维护：按正式对白、语音与策划角色参考生成并检查 H3 绿幕数字人。'],
  'runninghub-h3-ref2va-audio': ['数字人与语音', 'H3 双音频', '调用指定的 H3 双阶段音频参考应用；输出目录必须显式指定。'],
  'ndc-h3-avatar-delivery': ['数字人与语音', 'H3 后处理', '对用户已选定的 H3 候选做确定性后处理，在当前任务中准备交付包。']
};
const byName = new Map(catalog.skills.map(s => [s.name, s]));
for (const entry of source.skills) {
  if (!roots[entry.owner_scope] || path.isAbsolute(entry.path) || entry.path.split(/[\\/]/).includes('..')) {
    throw new Error(`Invalid canonical locator: ${entry.name}`);
  }
  const relativeFile = entry.path.replace(/\\/g, '/') + '/SKILL.md';
  const file = path.join(roots[entry.owner_scope], relativeFile);
  if (!fs.existsSync(file)) throw new Error(`Missing canonical skill: ${file}`);
  const info = descriptions[entry.name];
  if (!info) throw new Error(`Missing catalog description: ${entry.name}`);
  let skill = byName.get(entry.name);
  if (!skill) {
    skill = { name: entry.name, inputs: ['明确的制作需求及已指定素材', '项目外任务的 payload 路径', '具体 Skill 要求的台词、源图或交接包'],
      rating: null, ratingNote: '未评分：本次仅核对入口与维护状态。' };
    catalog.skills.push(skill);
  }
  Object.assign(skill, { category: info[0], kind: info[1], purpose: info[2],
    project: entry.owner_scope, path: relativeFile,
    modified: source.updated_at, maintenanceStatus: entry.status });
}
catalog.generatedAt = source.updated_at + ' · 美术入口与跨机器路径整理';
catalog.scanRules = '静态美术 Skill 列策划库主入口，H3 视频 Skill 列工程库主入口；其他同名目录仅为兼容入口。道具主流程由美术同学维护，三个旧子接口待同步。图片和视频过程文件在项目外，用户确认后交付工程。已删除的 Skill 不列入入口。';
if (new Set(catalog.skills.map(s => s.name)).size !== catalog.skills.length) throw new Error('Duplicate skill names');
fs.writeFileSync(target, 'window.SKILL_CATALOG = ' + JSON.stringify(catalog, null, 2) + ';\n');
console.log(JSON.stringify({ artEntries: source.skills.length, totalEntries: catalog.skills.length, output: target }));

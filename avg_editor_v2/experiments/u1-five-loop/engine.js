export const STORAGE_KEY = 'ndc:experiment:u1-five-loop-test:l2:v1';
export function freshState(m) {
  return {unit:m.unitKey,version:m.version,mode:'start',scene:'lobby',inventory:[...m.initialItems],flags:[],met:[],topics:[],npc:null,round:0,selected:[],reason:'',dialogue:null,log:[],startedAt:null};
}
export function ready(m,s) { return m.expose.required.every(k=>s.inventory.includes(k)) && m.doubts.every(d=>d.requires.every(k=>s.inventory.includes(k))); }
export function visibleTopics(m,s,id) {return m.npcs[id].topics.filter(t=>!t.requiresAny || t.requiresAny.some(k=>s.inventory.includes(k)));}
export function exactSet(a,b) {return a.length===b.length && new Set(b).size===b.length && a.every(k=>b.includes(k));}
export function restoreState(m,dialogues,raw) {
  const s=JSON.parse(raw);
  if(!s || s.unit!==m.unitKey || s.version!==m.version) throw Error('存档版本不匹配');
  if(!['start','explore','npc','dialogue','expose','complete'].includes(s.mode)) throw Error('进度阶段无效');
  for(const k of ['inventory','flags','met','topics','selected','log']) if(!Array.isArray(s[k])) throw Error('进度记录损坏');
  if(!m.scenes.some(c=>c.id===s.scene) || s.inventory.some(k=>!m.items[k]) || new Set(s.inventory).size!==s.inventory.length) throw Error('记录引用失效');
  if(s.met.some(k=>!m.npcs[k]) || s.topics.some(k=>!Object.values(m.npcs).some(n=>n.topics.some(t=>t.id===k)))) throw Error('谈话记录失效');
  if(!Number.isInteger(s.round) || s.round<0 || s.round>=m.expose.rounds.length) throw Error('指证阶段失效');
  if(s.selected.some(k=>!s.inventory.includes(k))) throw Error('选证记录失效');
  if(s.mode==='npc' && !m.npcs[s.npc]) throw Error('人物记录失效');
  if(s.mode==='dialogue') {
    const d=s.dialogue;
    if(!d || !dialogues[d.key]?.length || !Number.isInteger(d.index) || d.index<0 || d.index>=dialogues[d.key].length || !d.after?.type) throw Error('对白进度失效');
  }
  if(typeof s.reason!=='string') s.reason='';
  return s;
}
export class Game {
  constructor(m,dialogues,state=null){this.m=m;this.d=dialogues;this.s=state||freshState(m);}
  record(type,data={}) {this.s.log.push({at:new Date().toISOString(),type,...data});}
  start(){if(this.s.mode!=='start')return;this.s.startedAt=new Date().toISOString();this.record('start');this.say(this.m.opening,{type:'enter',scene:'lobby'});}
  say(key,after){if(!this.d[key]?.length)throw Error('缺少对白：'+key);this.s.mode='dialogue';this.s.dialogue={key,index:0,after};this.applyNode();}
  applyNode(){const d=this.s.dialogue,n=this.d[d.key][d.index];this.record('line',{dialogue:d.key,index:d.index,speaker:n.speaker,text:n.text});for(const key of n.grants||[])this.grant(key);}
  grant(key){if(!this.m.items[key])throw Error('缺少证据：'+key);if(key==='photo_amounts')this.s.inventory=this.s.inventory.filter(k=>k!=='photo_raw');if(!this.s.inventory.includes(key)){this.s.inventory.push(key);this.record('acquire',{item:key});}}
  advance(){if(this.s.mode!=='dialogue')return;const d=this.s.dialogue;if(d.index+1<this.d[d.key].length){d.index++;this.applyNode();return;}const after=d.after;this.s.dialogue=null;this.finish(after);}
  finish(a){
    if(a.type==='enter'){this.enter(a.scene,true);return;}
    if(a.type==='npc'){this.s.npc=a.npc;this.s.mode='npc';return;}
    if(a.type==='topic'){if(!this.s.topics.includes(a.key))this.s.topics.push(a.key);this.record('topic_complete',{topic:a.key});this.s.npc=a.npc;this.s.mode='npc';return;}
    if(a.type==='lie'){this.say(this.m.expose.rounds[this.s.round].lie,{type:'select'});return;}
    if(a.type==='select'){this.s.mode='expose';return;}
    if(a.type==='success'){
      this.s.selected=[];this.s.reason='';
      if(this.s.round+1<this.m.expose.rounds.length){this.s.round++;this.finish({type:'lie'});}else this.say(this.m.expose.ending,{type:'complete'});
      return;
    }
    if(a.type==='complete'){this.s.mode='complete';this.record('complete');return;}
    this.s.mode='explore';this.s.npc=null;
  }
  enter(id,forced=false){if(!forced && !['explore','npc'].includes(this.s.mode))return;const scene=this.m.scenes.find(c=>c.id===id);if(!scene)throw Error('场景不存在');this.s.scene=id;this.s.npc=null;this.s.mode='explore';this.record('scene',{scene:id});if(scene.entry&&!this.s.flags.includes('entry:'+id)){this.s.flags.push('entry:'+id);this.say(scene.entry,{type:'explore'});}}
  meet(id){if(this.s.mode!=='explore')return;const scene=this.m.scenes.find(c=>c.id===this.s.scene);if(!scene.npcs.includes(id))return;const n=this.m.npcs[id];const returning=this.s.met.includes(id);if(!returning)this.s.met.push(id);this.s.npc=id;this.say(returning?n.repeat:n.intro,{type:'npc',npc:id});}
  topic(key){if(this.s.mode!=='npc')return;const npc=this.s.npc;if(!visibleTopics(this.m,this.s,npc).some(t=>t.id===key))return;this.record('topic',{topic:key,npc});this.say(key,{type:'topic',key,npc});}
  exit(){if(this.s.mode==='npc'){this.s.mode='explore';this.s.npc=null;}}
  inspect(id){if(this.s.mode!=='explore')return;const o=this.m.scenes.find(c=>c.id===this.s.scene).objects.find(o=>o.id===id);if(!o)return;if(this.s.inventory.includes(o.item)||(o.replacement&&this.s.inventory.includes(o.replacement)))return;this.record('inspect',{object:id});this.say(o.dialogue,{type:'explore'});}
  analyze(){if(!['explore','npc'].includes(this.s.mode)||!this.s.inventory.includes('photo_raw'))return;this.s.scene='booth';this.s.npc=null;const a={type:'explore'};this.record('analysis',{item:'photo_raw'});this.say('photo_analyze',a);}
  beginExpose(){if(!['explore','npc'].includes(this.s.mode)||!ready(this.m,this.s))return;this.s.scene='tommy';this.s.npc=null;this.s.round=0;this.s.selected=[];this.s.reason='';this.record('expose_start',{inventory:[...this.s.inventory]});this.say(this.m.expose.opening,{type:'lie'});}
  toggle(key){if(this.s.mode!=='expose'||!this.s.inventory.includes(key))return;this.s.selected=this.s.selected.includes(key)?this.s.selected.filter(k=>k!==key):[...this.s.selected,key];}
  submit(){if(this.s.mode!=='expose'||!this.s.selected.length)return false;const r=this.m.expose.rounds[this.s.round];const correct=exactSet(r.answer,this.s.selected);this.record('attempt',{round:this.s.round+1,selected:[...this.s.selected],available:[...this.s.inventory],reason:this.s.reason.trim().slice(0,3000),correct});if(!correct && r.answer.every(k=>this.s.selected.includes(k))){this.s.feedback='这些材料已经包含有效反驳，但还混入了无关材料。请保留直接针对当前说法的材料后再出示。';return false;}this.s.feedback='';this.say(correct?r.success:r.wrong,{type:correct?'success':'select'});return correct;}
}

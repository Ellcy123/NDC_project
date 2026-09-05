import assert from 'node:assert/strict';
import fs from 'node:fs';
import {Game,ready,visibleTopics,restoreState} from './engine.js';
const m=JSON.parse(fs.readFileSync(new URL('./manifest.json',import.meta.url)));
const d=JSON.parse(fs.readFileSync(new URL('./dialogue.json',import.meta.url)));
const g=new Game(m,d), drain=()=>{let n=0;while(g.s.mode==='dialogue'){assert.ok(n++<400);g.advance();}};
assert.equal(ready(m,g.s),false);g.start();drain();
for(const scene of m.scenes){g.enter(scene.id);drain();for(const o of scene.objects){g.inspect(o.id);drain();}for(const npc of scene.npcs){g.meet(npc);drain();for(const t of visibleTopics(m,g.s,npc)){g.topic(t.id);drain();}g.exit();}}
assert.equal(g.s.topics.length,13);assert.equal(ready(m,g.s),true);
const incomplete=structuredClone(g.s);incomplete.inventory=incomplete.inventory.filter(k=>k!=='signature_statement');assert.equal(ready(m,incomplete),false);
g.enter('tommy');g.analyze();assert.equal(g.s.scene,'booth');drain();
assert.ok(!g.s.inventory.includes('photo_raw'));assert.ok(g.s.inventory.includes('photo_amounts'));assert.equal(visibleTopics(m,g.s,'emma').length,3);
const owned=g.s.inventory.length;g.inspect('camera');assert.equal(g.s.mode,'explore');assert.equal(g.s.inventory.length,owned);
g.beginExpose();drain();const pool=[...g.s.inventory];
for(const selected of [['private_ledger'],['public_ledger'],['demand_letter']]){g.s.selected=selected;assert.equal(g.submit(),false);drain();assert.equal(g.s.round,0);}
g.s.selected=['private_ledger','public_ledger','demand_letter'];assert.equal(g.submit(),false);assert.equal(g.s.mode,'expose');assert.match(g.s.feedback,/有效反驳/);
g.s.selected=['private_ledger','public_ledger'];g.s.reason='同范围两月合计不一致';assert.equal(g.submit(),true);
const recovered=restoreState(m,d,JSON.stringify(g.s));assert.deepEqual(recovered,g.s);drain();assert.equal(g.s.round,1);assert.deepEqual(g.s.inventory,pool);
g.s.selected=['private_ledger','public_ledger'];assert.equal(g.submit(),false);drain();g.s.selected=['demand_letter'];assert.equal(g.submit(),true);drain();assert.equal(g.s.mode,'complete');
assert.ok(g.s.log.some(e=>e.type==='attempt'&&e.reason==='同范围两月合计不一致'));
assert.equal(g.s.log.filter(e=>e.type==='acquire').length,12);
assert.throws(()=>restoreState(m,d,JSON.stringify({...g.s,version:'bad'})));
console.log('PASS: gates, 13 topics, analysis replacement, shared pool, wrong/subset/superset, two successes, resume, completion');

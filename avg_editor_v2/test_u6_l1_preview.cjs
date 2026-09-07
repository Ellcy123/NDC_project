// Exercise L1 through the original editor, including skipping both Emma topics.
const {createRequire}=require('node:module');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const {chromium}=createRequire('C:/Users/Ellcy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json')('playwright');

(async()=>{
 const report=JSON.parse(fs.readFileSync(__dirname+'/data/_table_drafts/Unit6/integration_report_l1.json','utf8'));
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 try {
  await page.goto('http://localhost:9529/index.html?unit=Unit6&loop=loop1');
  await page.waitForFunction(n=>AppState.currentUnit==='Unit6'&&AppState.currentLoop==='loop1'&&AppState.talksMap.size===n,report.counts.Talk);
  assert.equal(await page.locator('#loopSelect').inputValue(),'loop1');
  const info=await page.evaluate(()=>({
   chapter:DataManager.getChapterConfig('Unit6','loop1').id,
   flow:AppState.unitFlow.loops.map(l=>l.id),
   opening:FlowView.resolveOpeningItems(AppState.loopData),
   sceneIds:DataManager.scenesForLoop('Unit6','loop1').map(s=>s.sceneId)
  }));
  assert.equal(info.chapter,'601');
  assert.deepEqual(info.flow,['loop1','loop2']);
  assert.deepEqual(info.sceneIds,['6103']);
  assert.deepEqual(info.opening.map(x=>x.firstId),['entrance','lobby_intro','gunshot','discovery'].map(k=>report.dialogues[k]));
  assert.deepEqual(info.opening.map(x=>x.id),['6100','6101','6101','6102']);

  // A player may leave Emma's menu immediately; the fixed cooperation close
  // must still lead through the gunshot and discovery to free investigation.
  await page.evaluate(id=>UI.playTalkInDrawer(id,'TALK','L1 开场',''),report.dialogues.entrance);
  await page.waitForFunction(id=>DialogController._state.chain[0]?.talk.id===id,report.dialogues.entrance);
  const initial=await page.evaluate(()=>DialogController._state.chain.map(n=>n.talk.id));
  assert.equal(initial.at(-1),report.menus.emma);
  await page.evaluate(id=>DialogController.selectBranch(id),report.dialogues.cooperation_close);
  const skipped=await page.evaluate(()=>DialogController._state.chain.map(n=>n.talk.id));
  for(const key of ['cooperation_close','gunshot','discovery'])assert.ok(skipped.includes(report.dialogues[key]),key);
  assert.equal(skipped.at(-1),report.blockTalkIds.discovery.at(-1));
  await page.evaluate(()=>UI.closeModal());

  // All eight topics return to their own menu; exits work independently.
  for(const [npc,menu] of Object.entries(report.menus)){
   await page.evaluate(id=>UI.playTalkInDrawer(id,'TALK','L1 菜单',''),menu);
   await page.waitForFunction(()=>document.querySelectorAll('.avg-branch-btn').length===3);
   const options=await page.evaluate(id=>DataManager.getTalk(id).Parameters.map(p=>p.ParameterInt),menu);
   for(const topic of options.slice(0,2)){
    await page.evaluate(id=>DialogController.selectBranch(id),topic);
    const chain=await page.evaluate(()=>DialogController._state.chain.map(n=>n.talk.id));
    assert.equal(chain[0],topic,npc);
    assert.equal(chain.at(-1),menu,npc);
   }
   await page.evaluate(id=>DialogController.selectBranch(id),options.at(-1));
   const last=await page.evaluate(()=>DialogController._state.chain.at(-1).talk);
   assert.equal(last.script,'2',npc);
   await page.evaluate(()=>UI.closeModal());
  }
  await page.evaluate(()=>FlowView.showScene('6103'));
  const sceneText=await page.locator('#content').innerText();
  for(const label of ['Rosa','Vivian','Morrison','检查小手枪','查看委托协议','指证错误回应'])assert.ok(sceneText.includes(label),label);
  await page.evaluate(id=>UI.playTalkInDrawer(id,'TALK','枪检',''),report.dialogues.analyze_gun);
  await page.waitForFunction(id=>DialogController._state.chain[0]?.talk.id===id,report.dialogues.analyze_gun);
  const analysis=await page.evaluate(()=>DialogController._state.chain.map(n=>n.talk));
  assert.equal(analysis.filter(t=>t.script==='3'&&t.Parameters[0].ParameterInt==='6208').length,1);
  await page.evaluate(()=>UI.closeModal());
  await page.evaluate(()=>FlowView.showPhase('expose'));
  assert.match(await page.locator('#content').innerText(),/小手枪/);
  await page.evaluate(id=>UI.playTalkInDrawer(id,'TALK','L1 指证与收尾',''),report.dialogues.expose_open);
  await page.waitForFunction(id=>DialogController._state.chain[0]?.talk.id===id,report.dialogues.expose_open);
  const expose=await page.evaluate(()=>DialogController._state.chain.map(n=>n.talk));
  assert.equal(expose.filter(t=>t.script==='7').length,1);
  assert.equal(expose.at(-1).script,'15');
  assert.ok(expose.some(t=>t.id===report.dialogues.negotiation));
  assert.ok(expose.some(t=>t.id===report.dialogues.ending));
  assert.ok(!expose.some(t=>t.script==='3'));
  await page.evaluate(()=>UI.closeModal());
  await page.evaluate(()=>FlowView.showPhase('opening'));
  await page.screenshot({path:__dirname+'/data/_table_drafts/Unit6/preview_l1.png',fullPage:true});

  await page.locator('.loop-chip[data-loop="loop2"]').click();
  await page.waitForFunction(()=>AppState.currentLoop==='loop2'&&AppState.talksMap.size===253);
  assert.equal(await page.evaluate(()=>DataManager.getChapterConfig('Unit6','loop2').id),'602');
  await page.selectOption('#unitSelect','Unit1');
  await page.locator('.loop-chip[data-loop="loop1"]').click();
  await page.waitForFunction(()=>AppState.currentUnit==='Unit1'&&AppState.currentLoop==='loop1'&&document.querySelector('#statusBar').textContent.includes('Unit1 loop1'));
  assert.equal(await page.evaluate(()=>DataManager.getChapterConfig('Unit1','loop1').id),'101');
  assert.deepEqual(errors,[]);
  fs.writeFileSync(__dirname+'/data/_table_drafts/Unit6/browser_report_l1.json',JSON.stringify({pass:true,info,checks:['four opening entries','skip both optional Emma topics','eight topics return to menus','scene inspection entries','one gun analysis grant','single accusation through ending','L2 and formal Unit1 still load'],errors},null,2));
  console.log('PASS: L1 opening, optional topics, three NPCs, gun analysis, single accusation, ending, preserved L2 and U1');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

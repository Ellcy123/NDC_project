const { createRequire } = require('node:module');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const {chromium}=createRequire('C:/Users/Ellcy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json')('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[],requests=[];page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push(r.url()));
 try {
  await page.goto('http://localhost:9529/index.html?unit=Unit6&loop=loop2');
  await page.waitForFunction(()=>AppState.currentUnit==='Unit6'&&AppState.talksMap.size===253&&document.querySelector('#statusBar').textContent.includes('对话:'));
  assert.ok(!page.url().includes('experiments'));
  assert.equal(await page.locator('#loopSelect').inputValue(),'loop2');
  const info=await page.evaluate(()=>({chapter:DataManager.getChapterConfig('Unit6','loop2').id,scenes:DataManager.scenesForLoop('Unit6','loop2').length,flow:AppState.unitFlow.loops.map(x=>x.id),items:DataManager.itemsByChapter('EPI06').length}));
  const hasL1=fs.existsSync(__dirname+'/data/_table_drafts/Unit6/integration_report_l1.json');
  assert.deepEqual(info,{chapter:'602',scenes:6,flow:hasL1?['loop1','loop2']:['loop2'],items:hasL1?10:8});
  const report=JSON.parse(fs.readFileSync(__dirname+'/data/_table_drafts/Unit6/integration_report.json','utf8'));
  for(const [npc,menu] of Object.entries(report.menus)){
   await page.evaluate(id=>UI.playTalkInDrawer(id,'TALK','菜单验证',''),menu);
   await page.waitForFunction(()=>document.querySelectorAll('.avg-branch-btn').length>0);
   const count=await page.locator('.avg-branch-btn').count(); assert.ok(count>=2&&count<=4,npc);
   if(npc==='emma')assert.match(await page.locator('.avg-branches').innerText(),/包厢合影.*显出金额.*任一/);
   await page.locator('.avg-branch-btn').first().click();
   assert.ok(await page.evaluate(()=>DialogController._state.chain.length>0));
   await page.evaluate(()=>UI.closeModal());
  }
  await page.evaluate(()=>FlowView.showScene('6205'));
  assert.match(await page.locator('#content').innerText(),/照片分析对白/);
  await page.evaluate(()=>FlowView.showPhase('expose'));
  const exposeText=await page.locator('#content').innerText();assert.match(exposeText,/Webb 留存的收款账/);assert.match(exposeText,/八月催款函存根/);
  await page.evaluate(()=>GameController.switchView('flow'));
  await page.screenshot({path:__dirname+'/data/_table_drafts/Unit6/preview.png',fullPage:true});
  assert.ok(!requests.some(x=>/experiments\/u1-five-loop\/(manifest|engine|app|dialogue)/.test(x)));
  await page.selectOption('#unitSelect','Unit1');await page.locator('.loop-chip[data-loop="loop2"]').click();
  await page.waitForFunction(()=>AppState.currentUnit==='Unit1'&&document.querySelector('#statusBar').textContent.includes('Unit1 loop2'));
  assert.equal(await page.evaluate(()=>DataManager.getChapterConfig('Unit1','loop2').id),'102');
  assert.deepEqual(errors,[]);
  fs.writeFileSync(__dirname+'/data/_table_drafts/Unit6/browser_report.json',JSON.stringify({pass:true,info,checks:['same editor URL','shared table requests only','all NPC menus','Emma condition annotation','inspection playback entry','two expose configurations','original Unit1 reload'],errors},null,2));
  console.log('PASS: shared-table preview, 6 NPC menus, conditional annotation, expose data, old Unit1');
 } catch(e) { console.error(await page.evaluate(()=>({status:document.querySelector('#statusBar')?.textContent,unit:AppState.currentUnit,talks:AppState.talksMap.size}))); throw e; } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});

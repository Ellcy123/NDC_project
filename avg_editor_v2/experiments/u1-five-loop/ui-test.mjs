import {createRequire} from 'node:module';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const require=createRequire('C:/Users/Ellcy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json');
const {chromium}=require('playwright');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
const root=new URL('./',import.meta.url);fs.mkdirSync(new URL('qa/',root),{recursive:true});
const shot=async name=>{await page.locator('.scene img').evaluateAll(async imgs=>{await Promise.all(imgs.map(i=>i.decode()));});return page.screenshot({path:new URL('qa/'+name+'.png',root).pathname.replace(/^\/(\w:)/,'$1'),fullPage:true});};
const state=()=>page.evaluate(()=>JSON.parse(localStorage.getItem('ndc:experiment:u1-five-loop-test:l2:v1')));
const drain=async()=>{let count=0;while(await page.locator('[data-next]').count()){assert.ok(count++<400);await page.locator('[data-next]').click();}};
try{
 await page.goto('http://localhost:9529/experiments/u1-five-loop/index.html');await page.locator('#startButton').waitFor();await shot('start');await page.locator('#startButton').click();await drain();
 const m=JSON.parse(fs.readFileSync(new URL('manifest.json',root)));
 for(const scene of m.scenes){await page.locator(`[data-scene="${scene.id}"]`).click();await drain();for(const o of scene.objects){await page.locator(`[data-object="${o.id}"]`).click();await drain();}for(const npc of scene.npcs){await page.locator(`[data-npc="${npc}"]`).click();await drain();for(const t of m.npcs[npc].topics){if(await page.locator(`[data-topic="${t.id}"]`).count()){await page.locator(`[data-topic="${t.id}"]`).click();await drain();}}await page.locator('[data-exit]').click();}}
 assert.equal((await state()).topics.length,13);await shot('exploration');await page.reload();await page.locator('[data-scene="booth"]').waitFor();assert.equal((await state()).topics.length,13);
 await page.locator('#journalButton').click();await page.locator('[data-analyze]').click();await drain();assert.equal((await state()).scene,'booth');
 await page.locator('[data-scene="tommy"]').click();await page.locator('[data-expose]').click();await drain();const candidates=await page.locator('[data-evidence]').count();await shot('expose');await page.setViewportSize({width:390,height:844});await shot('mobile-expose');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.setViewportSize({width:1440,height:1000});
 await page.locator('[data-evidence="demand_letter"]').check();await page.locator('#reason').fill('测试：八月存根能否反驳九十月总额');await page.locator('[data-submit]').click();await drain();assert.equal((await state()).round,0);
 await page.locator('[data-evidence="demand_letter"]').uncheck();for(const k of ['private_ledger','public_ledger'])await page.locator(`[data-evidence="${k}"]`).check();await page.locator('[data-submit]').click();await page.reload();await page.locator('[data-next]').waitFor();await drain();assert.equal((await state()).round,1);assert.equal(await page.locator('[data-evidence]').count(),candidates);
 await page.locator('[data-evidence="demand_letter"]').check();await page.locator('[data-submit]').click();await drain();assert.equal((await state()).mode,'complete');await shot('complete');
 const download=page.waitForEvent('download');await page.locator('[data-export]').click();await (await download).saveAs(new URL('qa/playthrough.json',root).pathname.replace(/^\/(\w:)/,'$1'));
 await page.setViewportSize({width:390,height:844});await shot('mobile');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.goto('http://localhost:9529/index.html');await page.locator('#unitSelect').waitFor();assert.ok(await page.locator('#unitSelect option[value="Unit1"]').count());await page.locator('#unitSelect').selectOption('Unit1FiveLoopTest');await page.waitForURL('**/experiments/u1-five-loop/index.html');await page.locator('[data-export]').waitFor();
 assert.deepEqual(errors,[]);fs.writeFileSync(new URL('qa/ui-report.json',root),JSON.stringify({pass:true,topics:13,candidatesBothRounds:candidates,checks:['full DOM playthrough','wrong retry','mid-dialogue reload','export','mobile overflow','editor selector'],pageErrors:errors},null,2));console.log('PASS: browser playthrough, reload, export, mobile, editor isolation entry');
}finally{await browser.close();}

// Actual Chromium UI checks. Developer dependency only; PHP runtime needs no Node.
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
process.env.PLAYWRIGHT_BROWSERS_PATH ??= path.join(root,'.local/ms-playwright');
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.SLG_PLAYWRIGHT_PATH || path.join(root,'.local/browser/node_modules/playwright'));
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:1440,height:1050}});
const page=await context.newPage();
const base=process.env.SLG_BASE_URL || 'http://127.0.0.1:8055/team05/';
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
fs.mkdirSync(path.join(root,'docs/evidence/screenshots'),{recursive:true});
const shots=[];let id=null;
async function shot(name){await page.screenshot({path:path.join(root,'docs/evidence/screenshots',name+'.png'),fullPage:true});shots.push(name+'.png');}
async function filters(start,end,ids){await page.locator('[name=start_date]').fill(start);await page.locator('[name=end_date]').fill(end);for(let i=1;i<=5;i++)await page.locator(`[name="location_ids[]"][value="${i}"]`).setChecked(ids.includes(i));await page.locator('[name=max_temp_threshold]').fill('28.00');await page.locator('[name=max_temp_range]').fill('10.00');}
async function apply(){await page.getByRole('button',{name:/Apply filters/}).click();await page.waitForLoadState('networkidle');}
try{
    await page.goto(base);assert.match(await page.title(),/Every season/);assert.match(await page.locator('.metrics').innerText(),/5,480/);await shot('01-home');
    await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Temperature Comparison',exact:true}).click();
    await filters('2024-08-01','2024-08-31',[2,3]);await apply();assert.equal(await page.locator('tbody tr').count(),2);assert.match(await page.locator('tbody').innerText(),/Busan/);await shot('02-comparison');
    await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Find My Season',exact:true}).click();assert.equal(await page.locator('[name=start_date]').inputValue(),'2024-08-01');
    await page.locator('[name=top_rank]').selectOption('1');await apply();assert.equal(await page.locator('tbody tr').count(),2);assert.equal((await page.locator('tbody').innerText()).split('6.45%').length-1,2);await shot('03-ranking');
    await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Temperature Explorer',exact:true}).click();
    await page.getByRole('link',{name:'2024 ↘',exact:true}).click();assert.match(page.url(),/level=month/);
    await page.getByRole('link',{name:'2024-8 ↘',exact:true}).click();assert.match(page.url(),/level=day/);assert.equal(await page.locator('.table-wrap').first().locator('tbody tr').count(),62);
    await page.getByRole('navigation',{name:'Exploration path'}).getByRole('link',{name:'2024',exact:true}).click();assert.match(page.url(),/level=month/);
    await page.getByRole('link',{name:'All selected years',exact:true}).click();assert.match(page.url(),/level=year/);
    await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Temperature Trends',exact:true}).click();await filters('2024-01-01','2024-01-01',[1]);await apply();
    assert.match(await page.locator('tbody').innerText(),/1\.14/);assert.match(await page.locator('tbody').innerText(),/0\.30/);
    await page.locator('[name=window_days]').selectOption('30');await apply();assert.equal(await page.locator('[name=window_days]').inputValue(),'30');await shot('04-trends');
    await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Seasonal Information',exact:true}).click();await page.locator('[name=year]').selectOption('2025');await page.locator('[name=month]').selectOption('2');await page.getByRole('button',{name:/Explore month/}).click();assert.match(await page.locator('main').innerText(),/2025-02-03/);
    await page.goto(base+'plan_form.php');await page.locator('[name=plan_name]').fill('Browser verified plan');await page.locator('[name=memo]').fill('<b>literal text</b>');await page.getByRole('button',{name:/Save plan/}).click();id=Number(new URL(page.url()).searchParams.get('id'));assert.ok(id>0);assert.equal(await page.locator('.memo').innerText(),'<b>literal text</b>');
    await page.getByRole('link',{name:'Edit plan',exact:true}).click();await page.locator('[name=plan_name]').fill('Browser updated plan');await page.locator('[name="location_ids[]"][value="1"]').uncheck();await page.locator('[name="location_ids[]"][value="5"]').check();await page.getByRole('button',{name:/Save changes/}).click();assert.match(await page.locator('.detail-grid').innerText(),/Jeju/);
    await page.locator('[name=target]').selectOption('ranking');await page.getByRole('button',{name:/Apply this plan/}).click();assert.match(page.url(),/ranking\.php/);assert.equal(await page.locator('tbody tr').count(),1);assert.match(await page.locator('tbody').innerText(),/Jeju/);
    await page.goto(base+'plan_detail.php?id='+id);page.once('dialog',dialog=>dialog.accept());await page.getByRole('button',{name:'Delete this plan',exact:true}).click();assert.match(page.url(),/plans\.php/);assert.ok(!(await page.locator('main').innerText()).includes('Browser updated plan'));id=null;
    const mobile=await context.newPage();await mobile.setViewportSize({width:390,height:844});
    for(const route of ['','aggregate.php','olap.php','ranking.php','window.php','seasonal.php','plans.php','plan_form.php']){await mobile.goto(base+route);const widths=await mobile.evaluate(()=>({body:document.documentElement.scrollWidth,viewport:innerWidth}));assert.ok(widths.body<=widths.viewport+1,route+JSON.stringify(widths));}
    await mobile.close();assert.deepEqual(errors,[]);
    const result={result:'PASS',browser:browser.version(),desktop:'1440×1050',mobile:'390×844, eight routes, no document overflow',flows:['dynamic aggregate','cross-page Session','Top1 ties','OLAP year→month→day→month→year','both moving-average focus options','year-specific seasonal date','plan create/read/edit/apply/delete','escaped HTML memo'],console_errors:errors,screenshots:shots};
    fs.writeFileSync(path.join(root,'docs/evidence/browser-tests.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{
    if(id!==null){try{await page.goto(base+'plan_detail.php?id='+id);const token=await page.locator('[name=csrf_token]').first().inputValue();await page.request.post(base+'plan_actions.php',{form:{action:'delete',plan_id:String(id),csrf_token:token}});}catch{}}
    await browser.close();
}

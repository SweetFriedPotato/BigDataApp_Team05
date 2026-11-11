// Actual silent browser recording for rehearsal; no spoken presentation is claimed.
import {createRequire} from 'node:module';import {fileURLToPath} from 'node:url';import path from 'node:path';import fs from 'node:fs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');process.env.PLAYWRIGHT_BROWSERS_PATH ??=path.join(root,'.local/ms-playwright');
const {chromium}=createRequire(import.meta.url)(process.env.SLG_PLAYWRIGHT_PATH||path.join(root,'.local/browser/node_modules/playwright'));
const browser=await chromium.launch();const context=await browser.newContext({viewport:{width:1280,height:860},recordVideo:{dir:path.join(root,'.local/demo-recording'),size:{width:1280,height:860}}});
const page=await context.newPage();const base='http://127.0.0.1:8055/team05/';let id=null;
const pause=()=>page.waitForTimeout(900);const params=new URLSearchParams({apply_filters:'1',start_date:'2024-08-01',end_date:'2024-08-31',max_temp_threshold:'28.00',max_temp_range:'10.00'});[1,2,3,4,5].forEach(i=>params.append('location_ids[]',i));
try{
 await page.goto(base);await pause();await page.locator('.cards').scrollIntoViewIfNeeded();await pause();
 await page.goto(base+'aggregate.php?'+params);await pause();await page.locator('.table-wrap').scrollIntoViewIfNeeded();await pause();
 await page.goto(base+'olap.php?level=year');await page.getByRole('link',{name:'2024 ↘',exact:true}).click();await pause();await page.getByRole('link',{name:'2024-8 ↘',exact:true}).click();await page.locator('.table-wrap').first().scrollIntoViewIfNeeded();await pause();
 await page.goto(base+'ranking.php?'+params+'&top_rank=1');await page.locator('.table-wrap').scrollIntoViewIfNeeded();await pause();
 const wp=new URLSearchParams({apply_filters:'1',start_date:'2024-01-01',end_date:'2024-01-03',max_temp_threshold:'28.00',max_temp_range:'10.00',metric:'mean',window_days:'30'});wp.append('location_ids[]','1');
 await page.goto(base+'window.php?'+wp);await page.locator('.table-wrap').scrollIntoViewIfNeeded();await pause();
 await page.goto(base+'plan_form.php');await page.locator('[name=plan_name]').fill('Seasonal comparison demo');await page.locator('[name=memo]').fill('A rehearsal plan created in the real database.');await page.getByRole('button',{name:/Save plan/}).click();id=Number(new URL(page.url()).searchParams.get('id'));if(!id)throw new Error('Plan creation failed');await pause();
 await page.getByRole('link',{name:'Edit plan',exact:true}).click();await page.locator('[name=plan_name]').fill('Updated seasonal comparison');await page.getByRole('button',{name:/Save changes/}).click();await pause();
 await page.locator('[name=target]').selectOption('ranking');await page.getByRole('button',{name:/Apply this plan/}).click();await page.locator('.table-wrap').scrollIntoViewIfNeeded();await pause();
 await page.goto(base+'plan_detail.php?id='+id);page.once('dialog',d=>d.accept());await page.getByRole('button',{name:'Delete this plan',exact:true}).click();id=null;await pause();
 await page.goto(base+'seasonal.php?year=2024&month=10');await page.locator('.two-column').scrollIntoViewIfNeeded();await pause();await page.goto(base);await pause();
}finally{
 if(id!==null){try{await page.goto(base+'plan_detail.php?id='+id);const token=await page.locator('[name=csrf_token]').first().inputValue();await page.request.post(base+'plan_actions.php',{form:{action:'delete',plan_id:String(id),csrf_token:token}});}catch{}}
 const video=page.video();await context.close();await video.saveAs(path.join(root,'docs/rendered/demo-preview.webm'));await browser.close();
}
const result={result:'PASS',file:'docs/rendered/demo-preview.webm',bytes:fs.statSync(path.join(root,'docs/rendered/demo-preview.webm')).size,recording:'Actual Chromium interactions with Apache/PHP/MariaDB',audio:'none; silent rehearsal preview',final_course_video:'NOT_SUBMITTED',test_plan:'deleted'};
fs.writeFileSync(path.join(root,'docs/evidence/demo-recording.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));

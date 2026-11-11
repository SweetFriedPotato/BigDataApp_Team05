// Actual current SQL-result captures from the verified committed-source document root.
import {createRequire} from 'node:module';import {fileURLToPath,pathToFileURL} from 'node:url';import path from 'node:path';import fs from 'node:fs';
import {verifyDeployment,writeEvidence,sha} from './media_metadata.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');process.env.PLAYWRIGHT_BROWSERS_PATH??=path.join(root,'.local/ms-playwright');
const {chromium}=createRequire(import.meta.url)(process.env.SLG_PLAYWRIGHT_PATH||path.join(root,'.local/browser/node_modules/playwright'));
const identity=verifyDeployment(),base=process.env.SLG_BASE_URL||identity.url;if(base!==identity.url)throw new Error('Unverified capture URL');
const browser=await chromium.launch(),files=[];
try{const page=await browser.newPage({viewport:{width:1000,height:900}});
for(const [kind,start,end,ids,file,selector] of [
 ['aggregate','2024-01-01','2024-02-29',[1,2,3,4,5],'comparison-results','.primary-statistics'],
 ['ranking','2024-08-01','2024-08-31',[1,2,3,4,5],'ranking-results','.table-wrap'],
 ['window','2024-01-01','2024-01-01',[1],'window-results','.table-wrap'],
 ['window','2024-01-01','2024-01-31',[1,2],'trend-chart','.trend-panel']]){
 const params=new URLSearchParams({apply_filters:'1',start_date:start,end_date:end,max_temp_threshold:'28.00',max_temp_range:'10.00',metric:'mean',window_days:'30',group_mode:'location_year'});ids.forEach(id=>params.append('location_ids[]',String(id)));
 const r=await page.goto(base+kind+'.php?'+params);if(r.status()!==200)throw new Error('Figure page failed');await page.evaluate(()=>document.fonts.ready);
 const relative='docs/figures/'+file+'.png';const target=page.locator(selector).first();await target.screenshot({path:path.join(root,relative)});files.push({file:relative,url:page.url(),sha256:sha(path.join(root,relative))});
}
for(const diagram of ['erd','php-structure','erd-slide']){
 await page.goto(pathToFileURL(path.join(root,'docs/diagrams',diagram+'.svg')).href);const relative='docs/figures/'+diagram+'.png';await page.locator('svg').screenshot({path:path.join(root,relative)});files.push({file:relative,source:'docs/diagrams/'+diagram+'.svg',sha256:sha(path.join(root,relative))});
}
writeEvidence('figure-capture.json',{result:'PASS',captured_at:new Date().toISOString(),deployment_identity:identity,browser:browser.version(),figures:files,credentials_in_capture:false},['tools/capture_figures.mjs','tools/media_metadata.mjs',...files.map(f=>f.file)],{...identity,browser:browser.version()});console.log('Captured '+files.length+' actual figures');
}finally{await browser.close();}

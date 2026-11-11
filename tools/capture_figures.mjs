// Capture original live result tables for the report/paper; does not edit raster images.
import {createRequire} from 'node:module';import {fileURLToPath} from 'node:url';import path from 'node:path';import fs from 'node:fs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');process.env.PLAYWRIGHT_BROWSERS_PATH ??= path.join(root,'.local/ms-playwright');
const {chromium}=createRequire(import.meta.url)(process.env.SLG_PLAYWRIGHT_PATH || path.join(root,'.local/browser/node_modules/playwright'));
const browser=await chromium.launch();
try{const page=await browser.newPage({viewport:{width:1440,height:1050}});const base='http://127.0.0.1:8055/team05/';
for(const [kind,start,end,ids,file] of [['ranking','2024-08-01','2024-08-31',[1,2,3,4,5],'ranking-results'],['window','2024-01-01','2024-01-01',[1],'window-results']]){
 const params=new URLSearchParams({apply_filters:'1',start_date:start,end_date:end,max_temp_threshold:'28.00',max_temp_range:'10.00'});ids.forEach(id=>params.append('location_ids[]',String(id)));
 const response=await page.goto(base+kind+'.php?'+params);if(response.status()!==200)throw new Error('Figure page failed');await page.evaluate(()=>document.fonts.ready);await page.locator('.table-wrap').screenshot({path:path.join(root,'docs/figures',file+'.png')});
}
fs.writeFileSync(path.join(root,'docs/evidence/figure-capture.json'),JSON.stringify({result:'PASS',source:'Actual Apache/PHP result tables',browser:browser.version(),figures:['ranking-results.png','window-results.png'],credentials_in_capture:false},null,2)+'\n');}finally{await browser.close();}

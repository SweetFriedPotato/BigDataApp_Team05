#!/usr/bin/env python3
"""Generate twelve English slides with bounded aspect-fit images and honest responsibility notes."""
import json,sys
from pathlib import Path
from evidence_support import ROOT,write_evidence,digest
sys.path.insert(0,str(ROOT/'.local/python'))
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
P=Presentation();P.slide_width=Inches(13.333);P.slide_height=Inches(7.5)
INK='172033';BLUE='2563EB';MUTED='475569'
roles=json.loads((ROOT/'tools/team-responsibilities.json').read_text(encoding='utf-8'))
identity=json.loads((ROOT/'docs/evidence/revision-2026-11-12/app-source.json').read_text(encoding='utf-8'))
regions=[]
def text(slide,x,y,w,h,value,size=22,color=INK):
 b=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=b.text_frame;tf.word_wrap=True
 tf.margin_left=tf.margin_right=Inches(.02);tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(value.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(12)
 return b

def contain(slide,file,x,y,w,h):
 with Image.open(file) as im:iw,ih=im.size
 scale=min(w/iw,h/ih);fw,fh=iw*scale,ih*scale
 b=slide.shapes.add_picture(str(file),Inches(x+(w-fw)/2),Inches(y+(h-fh)/2),width=Inches(fw),height=Inches(fh))
 assert b.left>=Inches(x)-1 and b.top>=Inches(y)-1 and b.left+b.width<=Inches(x+w)+1 and b.top+b.height<=Inches(y+h)+1
 return b
slides=[
 ('Seasonal Living Guide','Shared opening',[
  'Historical temperature comparison + seasonal references',
  'Four SQL analyses. Persistent plans. Reproducible installation.',
  'Team 05 · Review draft · November 12, 2026',
  '20% responsibility each; actual member review / oral delivery pending.'],None,
  'Application '+identity['source_commit'][:12]+' · documents and package identity recorded separately'),
 ('A bounded question; reproducible data','Nunnalin Heimvichit · 2371001 · slides 2–3',[
  'Which location most often met both chosen limits?',
  'Five points × 1,096 dates = 5,480 NASA rows (2023–2025).',
  '72 KASI dates + 12 RDA monthly editorial items.',
  'Raw hashes match; no missing dates; all five leap days present.'],None,
  'Historical gridded reanalysis · NASA LST dates · calendar/editorial references'),
 ('Six tables; four reproducible SQL files','Nunnalin Heimvichit · 2371001 · 20% responsibility',[
  'Three physical FKs; independent calendar / monthly lookups.'], 'erd.png',
  'create + insert; project-only drop; actual dump-only restoration passed in fresh XAMPP.'),
 ('Validated web inputs and common Session','Jieun Hwang · 2376329 · slides 4–5',[
  'Nine screens; four distinct analysis menus; native PDO prepares.',
  'Real dates, strict IDs, finite decimal limits and option whitelists.',
  'Save conditions submits the current form, even before Apply.',
  'Invalid input keeps prior Session; core forms work without JS.'],None,
  'Original compact blue/white UI · local sun/cloud SVG · all nine screens at four sizes'),
 ('Seasonal context stays independent','Jieun Hwang · 2376329 · 20% responsibility',[
  'Calendar uses actual year/month dates; ingredients use month only.',
  '2025 February begins with the February 3 reference date.',
  'An extra food item leaves weather summaries/ranks/windows identical.',
  'No weather-food join, forecast or health/safety score.'],None,
  'KASI / RDA supplied snapshots · final official-almanac cross-check NOT_RUN'),
 ('Persistent plans: create, read, edit, delete','Sumin Cho · 2376274 · slides 6–7',[
  'saved_plans parent + plan_locations association table.',
  'POST + CSRF; validated input; escaped output; 303 redirects.',
  'Region-only updates explicitly advance updated_at and list order.',
  'Memo "0" stays "0"; empty memo alone gets the fallback.'],None,
  'Real web CRUD, apply-to-Session and long Korean name/memo regressions passed.'),
 ('Transactions: prove the failing middle step','Sumin Cho · 2376274 · 20% responsibility',[
  'CREATE: parent INSERT → first child → bad FK → ROLLBACK.',
  'Observed: zero residual parent and association rows.',
  'UPDATE: body/timestamp + child replacement → bad FK → ROLLBACK.',
  'Observed: exact original body, locations and timestamp restored.'],None,
  'CLI-only disposable fixtures; no public failure switch. Same-value saves also passed.'),
 ('Complex grouping preserves valid-day weights','Koo Daon · 2476009 · slides 8–9',[
  'Jan–Feb 2024: 60 valid days per point; means from daily rows.',
  'Seven primary columns; every extra SQL metric remains in More statistics.'], 'comparison-results.png',
  'Seoul weighted mean 0.018667°C · thresholds classify days without removing denominators'),
 ('OLAP: year → month → day → up','Koo Daon · 2476009 · 20% responsibility',[
  'Drill changes real SQL dimensions and intersects the selected dates.',
  'Jan–Feb: 5 year groups, 10 month groups; January: 155 daily rows.',
  'WITH ROLLUP returns year, location and grand totals.',
  'Five points × 60 days = 300 location-days; raw-day weighted means.'],None,
  'A partial Seoul Jan 15–31 drill returns 17 rows; no widened comparison dates.'),
 ('Dense ranks keep every real tie','Jihee Choi · 2276337 · slides 10–11',[
  'August 2024 · max ≤28°C · range ≤10°C · minimum valid days 1.',
  'Busan and Daegu: 2/31 each, 6.45%, shared rank 1.'], 'ranking-results.png',
  'Top 1 returns both ties. Unrounded DECIMAL rates rank; display rounding happens afterward.'),
 ('Continuous history; direct SQL-value graph','Jihee Choi · 2276337 · 20% responsibility',[
  'Seoul Jan 1: SQL 7-day 1.141429°C; 30-day 0.301333°C.',
  'Scan 29 prior days; graph selector keeps the global locations.'], 'trend-chart.png',
  'No recomputation; NULL/gaps break lines; one-day points stay finite; both focus options tested.'),
 ('Demonstrate the verified application version','Shared closing / references',[
  'Fresh Apache/MariaDB and official XAMPP offline restore passed.',
  'Evidence rejects missing, failing, incomplete and stale test inputs.',
  'ZIP → actual document-root hashes → screenshots / captioned video.',
  'Each member: 20% technical/report/paper/presentation; time T/5.'],None,
  'NASA POWER · MariaDB SQL docs · PHP PDO/Session · KASI/RDA snapshots · actual human review/upload NOT_RUN')]
images=[]
for index,(title,owner,points,image,caption) in enumerate(slides,1):
 slide=P.slides.add_slide(P.slide_layouts[6]);slide.background.fill.solid();slide.background.fill.fore_color.rgb=RGBColor.from_string('F6F8FB')
 text(slide,.6,.3,12,.3,'SEASONAL LIVING GUIDE  /  TEAM 05  /  REVIEW DRAFT',11,BLUE)
 text(slide,.6,1,12,.7,title,31);text(slide,.65,1.8,12,.3,owner+' · assigned responsibility; actual sign-off pending',13,MUTED)
 if image:
  if index==3:
   text(slide,.7,2.25,12,.45,points[0],20);file=ROOT/'docs/figures/erd-slide.png';contain(slide,file,.65,2.9,12,3.0)
  else:
   text(slide,.7,2.25,12,.9,'\n'.join(points),20);file=ROOT/'docs/figures'/image;contain(slide,file,.65,3.2,12,2.9)
  images.append(str(file.relative_to(ROOT)))
 else:text(slide,.75,2.5,11.8,3.6,'\n'.join(points),24 if index==1 else 23)
 text(slide,.7,6.2,12,.65,caption,16,MUTED)
 text(slide,.6,7.08,11.7,.23,'Source '+identity['source_commit'][:12]+' · Historical LST data · See docs/test-results.md for actual scope',10,MUTED)
 text(slide,12.3,7.02,.45,.3,str(index),13,BLUE)
 slide.notes_slide.notes_text_frame.text='Assigned presenter: '+owner+'. Content responsibility is 20% each; slides 1/12 shared. Actual member review and oral presentation NOT_RUN. English script: docs/demo-script.md. All application captures use source '+identity['source_commit']+'.'
 for shape in slide.shapes:
  assert shape.left>=0 and shape.top>=0 and shape.left+shape.width<=P.slide_width and shape.top+shape.height<=P.slide_height
path=ROOT/'docs/rendered/slides-draft.pptx';P.save(path)
assert len(Presentation(path).slides)==12
write_evidence('slides-draft.json',{'result':'PASS','file':str(path.relative_to(ROOT)),'slides':12,'generation':'python-pptx; image width AND height constrained with aspect ratio preserved','actual_render':'separately verified by tools/render_slides.py; generation alone is not rendering','images':images,'source_commit':identity['source_commit'],'draft':True},['python3','tools/make_slides.py'],extra=['tools/make_slides.py','tools/team-responsibilities.json',*images])
print('Generated 12 slides; actual rendering remains separate')

#!/usr/bin/env python3
"""Developer-only English PPTX draft. Does not claim a PowerPoint application render."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
P=Presentation();P.slide_width=Inches(13.333);P.slide_height=Inches(7.5)
INK='233B37';GREEN='2C6155';PAPER='F7F5EF';ORANGE='B45B3B'
def textbox(slide,x,y,w,h,text,size=21,color=INK):
    box=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h));tf=box.text_frame;tf.word_wrap=True
    for i,line in enumerate(text.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(14)
    return box
slides=[
('Seasonal Living Guide',['Regional temperature comparison and seasonal reference information','Team 05 · Weather Data Analysis','Evidence-based draft · November 11, 2026','One sequential Codex implementation; human contribution review pending']),
('A historical question, made explicit',['Which requested location most often met both of my limits?','Same dates. Known valid-day denominator. Separate analysis menus.','Five locations: Seoul, Busan, Daegu, Gwangju and Jeju.','Historical gridded reanalysis; LST dates; preferences rather than safety scores.']),
('Data you can reproduce',['5,480 NASA daily records · 2023–2025 · 1,096 dates per point','Five raw hashes match the supplied source version. Zero missing/duplicate dates.','72 KASI calendar-reference dates; 12 RDA monthly editorial items.','Reference snapshots adopted from supplied appendices; final almanac cross-check not performed.']),
('Six tables, deliberate relationships',['Composite weather key: location_id + weather_date','Plans and selected locations are a normalized parent/association pair.','InnoDB FKs and pairwise CHECKs protect valid records.','Calendar and food guides are separate lookups, without artificial weather FKs.']),
('Complex grouping',['Group by location × year × month, or location × year.','Valid-day means, ranges, extremes, matching and exceedance counts.','Thresholds classify days; they never remove the denominator.','Jan–Feb 2024: 60 valid days per point; raw-day weighted means.']),
('OLAP: details and the bigger picture',['Year → month → day → month → year uses real SQL changes.','Drill dates intersect the common comparison period.','WITH ROLLUP creates annual, location and grand totals.','Five points × 60 days = 300 location-days, not 300 distinct dates.']),
('Dense ranks preserve ties',['August 2024 · maximum ≤28°C · daily range ≤10°C','Busan and Daegu: 2/31 = 6.45%, shared rank 1.','Top 1 returns both tied first-place regions.','Unrounded DECIMAL rates determine ranks; display values round afterward.']),
('Windows preserve continuous history',['Seoul · January 1, 2024 · daily mean metric','7-day mean 1.14°C · 30-day mean 0.30°C','Scan 29 days before display start, partition only by location.','Incomplete/invalid/discontinuous frames stay NULL.']),
('Plans, Session and complete writes',['Real web create, list/detail, edit, apply and delete.','Parent and all selected links commit together.','Saved common conditions are validated before applying to Session.','Shared demonstration records; no private per-user ownership claim.']),
('Show actual failure evidence',['Create: parent INSERT succeeds, later child FK fails, no residues remain.','Update: body and old links change, later child fails, original snapshot restored.','CLI-only failure boundary; no web failure switch.','Native binding, escaped script, CSRF, strict dates/IDs and Unicode limits tested.']),
('Install from delivered SQL + PHP',['Actual official XAMPP: PHP 8.2.12 / Apache 2.4.58 / MariaDB 10.4.32','htdocs/team05 · unchanged team05 defaults · network mode none','Create/insert, reset, all nine screens, CRUD and rollback suites passed.','Actual dump restored by bundled mysql client; data and keys match.']),
('Demonstrate the same version',['Review package records COMMIT_SHA and verifies every archive member.','Report/paper PDFs and result captures reflect executed tests.','No performance benchmark or user study was performed.','Human contribution confirmation, English rehearsal and course upload remain pending.'])]
for index,(title,points) in enumerate(slides,1):
    slide=P.slides.add_slide(P.slide_layouts[6]);slide.background.fill.solid();slide.background.fill.fore_color.rgb=RGBColor.from_string(PAPER)
    textbox(slide,.55,.3,12,.4,'SEASONAL LIVING GUIDE   /   TEAM 05   /   REVIEW DRAFT',11,GREEN)
    textbox(slide,.6,1.0,12,1.1,title,34)
    image=None
    if index==4:image=ROOT/'docs/diagrams/erd.svg'
    if index in (7,8):
        image=ROOT/'docs/figures'/('ranking-results.png' if index==7 else 'window-results.png')
        textbox(slide,.65,2.05,12,1.3,'\n'.join(points[:2]),18)
        slide.shapes.add_picture(str(image),Inches(.7),Inches(3.25),width=Inches(11.8))
        textbox(slide,.65,6.0,12,.65,' '.join(points[2:]),15)
    else:textbox(slide,.7,2.3,11.8,4.2,'\n'.join(points),23 if index!=1 else 24)
    textbox(slide,.6,7.0,11,.25,'Historical grid data · LST dates · Results and limits in docs/test-results.md',10)
    textbox(slide,12.1,6.95,.6,.3,str(index),12,ORANGE)
    slide.notes_slide.notes_text_frame.text='English rehearsal draft. Follow docs/demo-script.md. No personal speaking role is assigned. Verify the source package commit before final demonstration.'
path=ROOT/'docs/rendered/slides-draft.pptx';P.save(path)
opened=Presentation(path);assert len(opened.slides)==12
result={'result':'PASS','file':str(path.relative_to(ROOT)),'slides':len(opened.slides),'validation':'PPTX reopened with python-pptx; text/package verified','powerpoint_application_render':'NOT_RUN','draft':True}
(ROOT/'docs/evidence/slides-draft.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

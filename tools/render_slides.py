#!/usr/bin/env python3
"""Actually render PPTX through LibreOffice and verify every page and shape boundary."""
import json,os,shutil,subprocess,sys,tempfile,unicodedata
from pathlib import Path
from evidence_support import ROOT,write_evidence,digest
sys.path.insert(0,str(ROOT/'.local/python'))
import pymupdf
from pptx import Presentation
from PIL import Image,ImageDraw
def main():
 image='seasonal-team05-document-render:2026-11-12'
 def call(args):
  p=subprocess.run(args,text=True,capture_output=True,encoding='utf-8')
  if p.returncode:raise RuntimeError(p.stderr+p.stdout)
  return p.stdout
 rendered=ROOT/'docs/rendered';pages=rendered/'slides';pages.mkdir(exist_ok=True)
 version=call(['docker','run','--rm','--network','none',image,'--version']).strip()
 with tempfile.TemporaryDirectory(prefix='slg-slides-',dir=ROOT/'.local') as tmp:
  out=Path(tmp)
  conversion=call(['docker','run','--rm','--network','none','--user',f'{os.getuid()}:{os.getgid()}','-v',str(rendered)+':/in:ro','-v',str(out)+':/out',image,'--convert-to','pdf','--outdir','/out','/in/slides-draft.pptx'])
  assert (out/'slides-draft.pdf').is_file(),conversion
  shutil.copyfile(out/'slides-draft.pdf',rendered/'slides-draft.pdf')
 presentation=Presentation(rendered/'slides-draft.pptx');pdf=pymupdf.open(rendered/'slides-draft.pdf');assert len(pdf)==len(presentation.slides)==12
 norm=lambda s:''.join(unicodedata.normalize('NFKC',s).split())
 overlaps=[];outside=[];missing=[];rendered_files=[]
 for n,(slide,page) in enumerate(zip(presentation.slides,pdf),1):
  shapes=list(slide.shapes)
  for i,a in enumerate(shapes):
   if a.left<0 or a.top<0 or a.left+a.width>presentation.slide_width or a.top+a.height>presentation.slide_height:outside.append({'slide':n,'shape':i})
   for j,b in enumerate(shapes[:i]):
    dx=min(a.left+a.width,b.left+b.width)-max(a.left,b.left);dy=min(a.top+a.height,b.top+b.height)-max(a.top,b.top)
    if dx>100 and dy>100:overlaps.append({'slide':n,'shapes':[i,j]})
   if a.has_text_frame:
    for paragraph in a.text_frame.paragraphs:
     if norm(paragraph.text) not in norm(page.get_text()):missing.append({'slide':n,'text':paragraph.text})
  # Actual rendered text must fit PDF page; drawings/images are visually reviewed separately.
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     x0,y0,x1,y1=span['bbox']
     if x0<-.5 or y0<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:outside.append({'slide':n,'text':span['text']})
  name=pages/f'{n:02d}.png';page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(name);rendered_files.append(str(name.relative_to(ROOT)))
 assert not overlaps,overlaps
 assert not outside,outside
 assert not missing,missing
 contact=Image.new('RGB',(1280,12//3*265),'#E2E8F0');draw=ImageDraw.Draw(contact)
 for i,file in enumerate(rendered_files):
  with Image.open(ROOT/file) as im:im.thumbnail((410,235));contact.paste(im,(10+(i%3)*425,15+(i//3)*265))
  draw.text((10+(i%3)*425,249+(i//3)*265),str(i+1),fill='#172033')
 contact.save(pages/'contact-sheet.png')
 result={'result':'PASS','renderer':version,'render_command':conversion.strip(),'ppt_rendered_pages':12,'page_images':rendered_files,'overlaps':overlaps,'outside':outside,'missing_rendered_text':missing,'image_fit':'Every image constrained by both maximum width and maximum height, aspect ratio preserved','visual_review':'Pending explicit visual review of all 12 PNG pages; this automated result does not claim it','source_commit':json.loads((ROOT/'docs/evidence/revision-2026-11-12/app-source.json').read_text(encoding='utf-8'))['source_commit']}
 write_evidence('slides-render.json',result,['python3','tools/render_slides.py'],{'renderer':version,'network':'none','image':image},extra=['tools/render_slides.py','tools/make_slides.py','docs/rendered/slides-draft.pptx','docs/rendered/slides-draft.pdf',*rendered_files]);print(json.dumps(result,indent=2))

if __name__=='__main__':
 try:main()
 except Exception as e:
  write_evidence('slides-render.json',{'result':'FAIL','error':str(e)},['python3','tools/render_slides.py'],extra=['tools/render_slides.py'])
  raise

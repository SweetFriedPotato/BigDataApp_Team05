#!/usr/bin/env python3
"""Check actual source excerpts, rendered artifacts, reviewed slide hashes and equal assignments."""
import json,re,sys
from evidence_support import ROOT,evidence_dir,digest,write_evidence
sys.path.insert(0,str(ROOT/'.local/python'))
import pymupdf
from pptx import Presentation
def main():
 report=(ROOT/'docs/report.md').read_text(encoding='utf-8');paper=(ROOT/'docs/paper.md').read_text(encoding='utf-8')
 excerpts=json.loads((evidence_dir()/'source-excerpts.json').read_text(encoding='utf-8'))
 for row in excerpts['excerpts']:
  file=ROOT/row['file'];assert digest(file)==row['file_sha256'];assert '\n'.join(file.read_text(encoding='utf-8').splitlines()[row['first_line']-1:row['last_line']])==row['excerpt'];assert row['excerpt'] in report
 roles=json.loads((ROOT/'tools/team-responsibilities.json').read_text(encoding='utf-8'))
 assert len(roles['members'])==5
 for person in roles['members']:
  for k in ['technical_share','report_share','paper_share','presentation_share']:assert person[k]==20
  for file in ['docs/report.md','docs/paper.md','docs/demo-script.md','docs/contributions.md','docs/team-responsibilities.md','docs/slides.md']:
   assert person['id'] in (ROOT/file).read_text(encoding='utf-8'),(person['id'],file)
  deck=Presentation(ROOT/'docs/rendered/slides-draft.pptx')
  for n in person['slides']:assert person['name'] in '\n'.join(s.text for s in deck.slides[n-1].shapes if s.has_text_frame)
 review=json.loads((evidence_dir()/'visual-review.json').read_text(encoding='utf-8'));assert review['reviewed_slides']==list(range(1,13))
 for file,expected in review['reviewed_file_sha256'].items():assert digest(ROOT/file)==expected,file
 render=json.loads((evidence_dir()/'slides-render.json').read_text(encoding='utf-8'));assert render['result']=='PASS' and render['ppt_rendered_pages']==12 and render['overlaps']==[] and render['outside']==[] and render['missing_rendered_text']==[]
 for file,d in render['_meta']['source_files'].items():assert digest(ROOT/file)==d,file
 rp=pymupdf.open(ROOT/'docs/rendered/report-draft.pdf');pp=pymupdf.open(ROOT/'docs/rendered/paper-draft.pdf');assert len(rp)>=10 and len(pp)>=4
 text=''.join(p.get_text() for p in pp);assert 'Figure 1. Actual August' in text and 'Figure 2. Seoul January' in text
 features={
  'erd':'Actual six-table ERD' in report and (ROOT/'docs/diagrams/erd.svg').is_file(),
  'php_structure':'Actual PHP request flow' in report and (ROOT/'docs/diagrams/php-structure.svg').is_file(),
  'ddl_keys_indexes':all(x in report for x in ['PRIMARY KEY','FOREIGN KEY','CHECK','idx_weather_date_location']),
  'seed_drop':'INSERT INTO locations' in report and 'DROP TABLE IF EXISTS plan_locations' in report,
  'pdo':all(x in report for x in ['->prepare($sql)','->bindValue(','->execute()']),
  'session':'session_start(' in report and "$_SESSION['analysis_filters']" in report,
  'crud':all(x in report for x in ['INSERT INTO saved_plans','SELECT * FROM saved_plans','UPDATE saved_plans SET','DELETE FROM saved_plans']),
  'transaction':all(x in report for x in ['beginTransaction()','->commit()','->rollBack()','T35']),
  'input_controls':all(x in report for x in ['type="date"','type="number"','type="checkbox"','select_control(','Save conditions']),
  'four_analyses':all(x in report for x in ['function aggregate_query','function olap_query','WITH ROLLUP','DENSE_RANK()','ROWS BETWEEN 29 PRECEDING']),
  'timeline':'Actual development sequence' in report and 'Revision stage' in report,
  'responsibility_results':'verified responsibility results' in report and report.count('NOT_RUN')>=5}
 assert all(features.values()),features
 result={'result':'PASS','report_pages':len(rp),'paper_pages':len(pp),'ppt_rendered_pages':12,'overlaps':render['overlaps'],'source_excerpts_match':True,'source_excerpt_count':len(excerpts['excerpts']),'equal_responsibilities':True,'visual_reviewed_slides':review['reviewed_slides'],'visual_review_actor':review['review_actor'],'report_features':features,'visible_paper_figure_captions':2,'human_member_reviews':'NOT_RUN','human_oral_presentation':'NOT_RUN','course_upload':'NOT_RUN','scope':'Technical artifact construction/verification; equal assignment does not establish completed human work'}
 extras=['tools/check_submission.py','docs/report.md','docs/paper.md','docs/demo-script.md','docs/contributions.md','docs/team-responsibilities.md','docs/slides.md','tools/team-responsibilities.json','docs/rendered/report-draft.pdf','docs/rendered/paper-draft.pdf','docs/rendered/slides-draft.pptx','docs/rendered/slides-draft.pdf','docs/evidence/revision-2026-11-12/visual-review.json']
 write_evidence('submission-docs.json',result,['python3','tools/check_submission.py'],{'PDF':'PyMuPDF','PPT_render':render['renderer'],'visual_review':'Codex inspected all 12 actual PNG pages'},extra=extras)
 print(json.dumps(result,indent=2))

if __name__=='__main__':
 try:main()
 except Exception as e:
  write_evidence('submission-docs.json',{'result':'FAIL','error':str(e)},['python3','tools/check_submission.py'],extra=['tools/check_submission.py'])
  raise

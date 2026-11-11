#!/usr/bin/env python3
"""Guard text I/O while regenerating the real seed offline; no Windows runtime claim."""
import contextlib,hashlib,io,json,locale,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from evidence_support import write_evidence
paths=[p for p in (ROOT/'data').rglob('*') if p.is_file()]+[ROOT/'sql/dbinsert.sql']
before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
original=Path.open;seen=[]
def guarded(self,mode='r',buffering=-1,encoding=None,errors=None,newline=None):
 if 'b' not in mode:
  if encoding not in ('utf-8','utf-8-sig'):raise AssertionError('Text encoding not explicit UTF-8: '+str(self))
  seen.append({'path':str(self.relative_to(ROOT)) if self.is_relative_to(ROOT) else str(self),'encoding':encoding,'mode':mode})
 return original(self,mode,buffering,encoding,errors,newline)
Path.open=guarded
try:
 with contextlib.redirect_stdout(io.StringIO()):runpy.run_path(str(ROOT/'tools/build_seed.py'),run_name='__main__')
finally:Path.open=original
after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert before==after,'Source/processed/seed bytes changed unexpectedly'
assert any(x['path'].endswith('rda_curated.csv') for x in seen)
write_evidence('utf8-seed.json',{'result':'PASS','seed_content_unchanged':True,'data_files_unchanged':True,'explicit_utf8':True,'checked_file_hashes':after,'text_operations':seen,'scope':'Path text I/O guarded to require explicit UTF-8; not a Windows/XAMPP runtime test'},['python3','tests/utf8_regression.py'],group='data',extra=['tools/validate_data.py','tools/build_seed.py','tools/data_common.py','tests/utf8_regression.py'])
print('UTF-8 text operations explicit; data and seed bytes unchanged')

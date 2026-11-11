"""Standard library HTTP client used only by developer tests."""
import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error
import re
import os
class Client:
    def __init__(self, base=None):
        self.base=base or os.environ.get('SLG_BASE_URL','http://127.0.0.1:8055/team05/')
        self.jar=http.cookiejar.CookieJar()
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
    def request(self, page, params=None, post=False):
        encoded=urllib.parse.urlencode(params or {}, doseq=True)
        req=urllib.request.Request(self.base+page+('?' + encoded if encoded and not post else ''),
             data=encoded.encode() if post else None)
        try:
            with self.opener.open(req,timeout=30) as r:return r.status,r.read().decode(),dict(r.headers)
        except urllib.error.HTTPError as e:return e.code,e.read().decode(),dict(e.headers)
    def token(self, body):
        match=re.search(r'name="csrf_token" value="([a-f0-9]{64})"',body)
        assert match, 'CSRF field missing'
        return match.group(1)
DEFAULT={'apply_filters':'1','start_date':'2025-01-01','end_date':'2025-12-31',
         'max_temp_threshold':'28.00','max_temp_range':'10.00','location_ids[]':[1,2,3,4,5]}

import os
from urllib.parse import urlparse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
ALLOWED={'http://127.0.0.1:8765','http://localhost:8765','http://127.0.0.1:5173','http://localhost:5173'}
desktop_origin=os.environ.get('MOODBOARD_DESKTOP_ORIGIN','')
p=urlparse(desktop_origin)
if p.scheme=='http' and p.hostname=='127.0.0.1' and p.port and p.path in ('','/'):
    ALLOWED.add(desktop_origin.rstrip('/'))
class LocalOnlyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request,call_next):
        if request.headers.get('host','').split(':')[0] not in ('127.0.0.1','localhost','testserver'):
            return JSONResponse({'detail':'Invalid host'},400)
        try:length=int(request.headers.get('content-length','0'))
        except ValueError:return JSONResponse({'detail':'Invalid content length'},400)
        if length<0:return JSONResponse({'detail':'Invalid content length'},400)
        if length>16*1024*1024:return JSONResponse({'detail':'请求体超过 16MB'},413)
        origin=request.headers.get('origin')
        if origin and origin not in ALLOWED:return JSONResponse({'detail':'Origin rejected'},403)
        if request.method not in ('GET','HEAD','OPTIONS') and request.headers.get('x-moodboard-request')!='1':
            return JSONResponse({'detail':'Missing local request header'},403)
        response=await call_next(request);response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='no-referrer';return response

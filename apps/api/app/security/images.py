import asyncio,ipaddress,socket,warnings
from io import BytesIO
from urllib.parse import urlparse
import httpx
from PIL import Image
MAX_BYTES=12*1024*1024
MAX_PIXELS=24_000_000
HOSTS={'www.artic.edu','images.metmuseum.org','images.unsplash.com','cdn.pixabay.com','pixabay.com'}
def validate_url(url):
    p=urlparse(url)
    if p.scheme!='https' or p.hostname not in HOSTS or p.username or p.password or p.port not in (None,443):raise ValueError('图片 URL 不在可信来源白名单')
    return p.hostname
async def fetch_bytes(url,max_bytes=MAX_BYTES,verify_pixels=True):
    host=validate_url(url)
    addresses=await asyncio.to_thread(socket.getaddrinfo,host,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):raise ValueError('禁止非公网图片地址')
    async with httpx.AsyncClient(timeout=20,follow_redirects=False,trust_env=False) as client:
        # Pin connection to the validated public IP; retain TLS SNI and Host.
        p=urlparse(url);ip=addresses[0][4][0];authority='['+ip+']' if ':' in ip else ip
        pinned='https://'+authority+(p.path or '/')+('?' + p.query if p.query else '')
        async with client.stream('GET',pinned,headers={'Host':host},extensions={'sni_hostname':host}) as response:
            if response.status_code!=200:raise ValueError(f'图片服务器 HTTP {response.status_code}，请求已停止')
            if response.headers.get('content-type','').split(';')[0] not in ('image/jpeg','image/png','image/webp'):raise ValueError('不支持的图片 MIME')
            data=bytearray()
            async for chunk in response.aiter_bytes():
                data.extend(chunk)
                if len(data)>max_bytes:raise ValueError(f'图片超过 {max_bytes//1024//1024}MB 限制')
    result=bytes(data)
    if verify_pixels:
        checked=decode(result);checked.close()
    elif not (result.startswith(b'\xff\xd8\xff') or result.startswith(b'\x89PNG\r\n\x1a\n') or (result.startswith(b'RIFF') and result[8:12]==b'WEBP')):
        raise ValueError('无效的图片文件')
    return result

async def fetch_image(url):
    return await fetch_bytes(url)

async def fetch_download(url):
    # Manual download is bounded without decoding a full-resolution original.
    return await fetch_bytes(url,max_bytes=40*1024*1024,verify_pixels=False)
def decode(data):
    with warnings.catch_warnings():
        warnings.simplefilter('error',Image.DecompressionBombWarning)
        with Image.open(BytesIO(data)) as im:
            if im.width*im.height>MAX_PIXELS or im.format not in ('JPEG','PNG','WEBP'):raise ValueError('图片像素或格式不允许')
            im.load();return im.convert('RGB')

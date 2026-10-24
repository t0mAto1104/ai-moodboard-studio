import json,zipfile,uuid
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
from app.db import store
from app.schemas.models import ImageAsset
from app.pipeline.license_filter import policy
from app.routers.assets import image_bytes
from app.security.images import decode
from app.core.config import DATA
from app.layout.engine import RATIOS,validate_items
async def export_project(p,format):
    items=validate_items(p['items'],p['ratio'],p['asset_ids'])
    if not items:raise ValueError('画布为空')
    w,h=RATIOS[p['ratio']];canvas=Image.new('RGBA',(w,h),'#ffffff');manifest=[];loaded={}
    # Verify every linked source before producing any output file.
    for item in items:
        if item['kind']=='image' and item['asset_id'] not in loaded:
            raw=store.get('image_assets',item['asset_id'])
            if not raw:raise ValueError('素材不存在')
            a=policy.require_export(ImageAsset(**raw),p.get('commercial',True))
            loaded[a.id]=decode(await image_bytes(a))
            manifest.append({'id':a.id,'title':a.title,'author':a.creator_name,'source':a.source_page_url,'license':a.license_type,'license_url':a.license_url,'evidence':a.license_evidence,'verified_at':a.license_verified_at,'attribution':a.attribution_text,'modification':'scaled/cropped/arranged in mood board'})
    for item in sorted(items,key=lambda a:a['z_index']):
        iw,ih=max(1,round(item['width'])),max(1,round(item['height']));layer=Image.new('RGBA',(iw,ih),(0,0,0,0))
        if item['kind']=='image':
            im=loaded[item['asset_id']]
            im=ImageOps.fit(im,(iw,ih)) if item['crop']['mode']=='cover' else ImageOps.contain(im,(iw,ih))
            layer.paste(im,((iw-im.width)//2,(ih-im.height)//2))
        elif item['kind']=='color':layer.paste(item['fill'],(0,0,iw,ih))
        else:
            font=ImageFont.load_default(size=24)
            # macOS CJK font when available.
            from pathlib import Path
            for f in ('/System/Library/Fonts/PingFang.ttc','/System/Library/Fonts/STHeiti Light.ttc'):
                if Path(f).exists():font=ImageFont.truetype(f,24);break
            ImageDraw.Draw(layer).text((2,2),item['text'],font=font,fill=item['fill'])
        layer.putalpha(layer.getchannel('A').point(lambda v:round(v*item['opacity'])))
        layer=layer.rotate(-item['rotation'],expand=True,resample=Image.Resampling.BICUBIC)
        canvas.alpha_composite(layer,(round(item['x']+iw/2-layer.width/2),round(item['y']+ih/2-layer.height/2)))
    # Bundle both artifact and required attribution sidecars; never export a bare uncredited CC BY file.
    b=BytesIO();canvas.convert('RGB').save(b,'PDF' if format=='pdf' else 'PNG',resolution=150)
    id=str(uuid.uuid4());path=DATA/'exports'/(id+'.zip')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('moodboard.'+format,b.getvalue());z.writestr('license-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2));z.writestr('attribution.txt','\n\n'.join(m['attribution']+'\n'+m['source']+'\n'+m['license_url']+'\nModified: '+m['modification'] for m in manifest))
    store.put('export_records',id,{'id':id,'project_id':p['id'],'format':format,'filename':path.name})
    return {'id':id,'url':'/api/exports/'+id,'format':format}

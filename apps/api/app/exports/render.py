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
    w,h=RATIOS[p['ratio']];canvas=Image.new('RGBA',(w,h),p.get('background','#ffffff'));manifest=[];loaded={}
    # Verify every linked source before producing any output file.
    # Validate all permissions before any network event or fetch.
    checked={}
    for item in items:
        if item['kind']=='image' and item['asset_id'] not in checked:
            raw=store.get('image_assets',item['asset_id'])
            if not raw:raise ValueError('素材不存在')
            checked[item['asset_id']]=policy.require_export(ImageAsset(**raw),p.get('commercial',True))
    if any(a.provider=='pixabay' for a in checked.values()) and len(items)<2:
        raise ValueError('Pixabay 单图仅缩放或裁切不属于组合创作；请添加其他图片、文字或色卡后导出。')
    for item in items:
        if item['kind']=='image' and item['asset_id'] not in loaded:
            raw=store.get('image_assets',item['asset_id'])
            if not raw:raise ValueError('素材不存在')
            a=checked[item['asset_id']]
            if a.provider=='unsplash':
                from app.providers.registry import PROVIDERS
                await PROVIDERS['unsplash'].track_selection(a)
            loaded[a.id]=decode(await image_bytes(a,cache=False,commercial=p.get('commercial',True),purpose='export'))
            manifest.append({'id':a.id,'title':a.title,'author':a.creator_name,'author_url':a.creator_url,'source':a.source_page_url,'license':a.license_type,'license_url':a.license_url,'evidence':a.license_evidence,'verified_at':a.license_verified_at,'attribution':a.attribution_text,'modification':'scaled/cropped/arranged in mood board'})
    for item in sorted(items,key=lambda a:a['z_index']):
        iw,ih=max(1,round(item['width'])),max(1,round(item['height']));layer=Image.new('RGBA',(iw,ih),(0,0,0,0))
        if item['kind']=='image':
            im=loaded[item['asset_id']]
            im=ImageOps.fit(im,(iw,ih)) if item['crop']['mode']=='cover' else ImageOps.contain(im,(iw,ih))
            layer.paste(im,((iw-im.width)//2,(ih-im.height)//2))
        elif item['kind']=='color':
            if item['shape']=='ellipse':ImageDraw.Draw(layer).ellipse((0,0,iw-1,ih-1),fill=item['fill'])
            else:layer.paste(item['fill'],(0,0,iw,ih))
        else:
            font=editor_font(item)
            draw=ImageDraw.Draw(layer)
            lines=[]
            # Wrap by glyph width, supporting both CJK and Latin text without external fonts.
            for paragraph in item['text'].split('\n'):
                line=''
                for char in paragraph:
                    if line and draw.textlength(line+char,font=font)>iw:
                        lines.append(line);line=''
                    line+=char
                lines.append(line)
            visible_rows=int(ih/(item['font_size']*item['line_height']))
            for row,line in enumerate(lines[:visible_rows]):
                length=draw.textlength(line,font=font)
                x={'left':0,'center':(iw-length)/2,'right':iw-length}[item['text_align']]
                draw.text((x,row*item['font_size']*item['line_height']),line,font=font,fill=item['fill'],anchor='lt',stroke_width=1 if item['font_weight']=='bold' and any(ord(c)>0x2e80 for c in line) else 0)
        layer.putalpha(layer.getchannel('A').point(lambda v:round(v*item['opacity'])))
        layer=layer.rotate(-item['rotation'],expand=True,resample=Image.Resampling.BICUBIC)
        canvas.alpha_composite(layer,(round(item['x']+iw/2-layer.width/2),round(item['y']+ih/2-layer.height/2)))
    # Bundle both artifact and required attribution sidecars; never export a bare uncredited CC BY file.
    b=BytesIO();canvas.convert('RGB').save(b,'PDF' if format=='pdf' else 'PNG',resolution=150)
    id=str(uuid.uuid4());path=DATA/'exports'/(id+'.zip')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('moodboard.'+format,b.getvalue());z.writestr('license-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2));z.writestr('attribution.txt','\n\n'.join(m['attribution']+'\n'+m['author_url']+'\n'+m['source']+'\n'+m['license_url']+'\nModified: '+m['modification'] for m in manifest))
    store.put('export_records',id,{'id':id,'project_id':p['id'],'format':format,'filename':path.name})
    return {'id':id,'url':'/api/exports/'+id,'format':format}


def editor_font(item):
    size=round(item['font_size'])
    bold=item['font_weight']=='bold'
    families={
        'sans':['/System/Library/Fonts/Helvetica.ttc','DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'],
        'serif':['/System/Library/Fonts/Times.ttc','DejaVuSerif-Bold.ttf' if bold else 'DejaVuSerif.ttf'],
        'mono':['/System/Library/Fonts/Menlo.ttc','DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf'],
    }
    paths=families[item['font_family']]
    if any(ord(c)>0x2e80 for c in item['text']):
        paths=['/System/Library/Fonts/PingFang.ttc','/System/Library/Fonts/STHeiti Light.ttc']+paths
    for path in paths:
        try:return ImageFont.truetype(path,size,index=1 if bold and path.endswith('Helvetica.ttc') else 0)
        except (OSError,ValueError):continue
    return ImageFont.load_default(size=size)

import math
from app.schemas.models import LayoutItem
RATIOS={'16:9':(1200,675),'4:3':(1200,900),'1:1':(1000,1000),'A4':(848,1200)}
def layout(assets,style='editorial',ratio='16:9',palette=None):
    w,h=RATIOS[ratio];margin=32;gap=16;n=len(assets);items=[]
    if not n:return items
    footer=72 if style=='material' else 0
    if style=='editorial' and n>2:
        hero_w=(w-2*margin-gap)*.48
        items.append(LayoutItem(id='image-0',asset_id=assets[0].id,x=margin,y=margin,width=hero_w,height=h-2*margin,attribution_reference=assets[0].id).model_dump())
        remaining=assets[1:];x0=margin+hero_w+gap;area_w=w-margin-x0
    else:remaining=assets;x0=margin;area_w=w-2*margin
    cols=max(1,math.ceil(math.sqrt(len(remaining)*area_w/(h-2*margin-footer))));rows=math.ceil(len(remaining)/cols)
    cw=(area_w-gap*(cols-1))/cols;ch=(h-2*margin-footer-gap*(rows-1))/rows
    for i,a in enumerate(remaining):
        x=x0+(i%cols)*(cw+gap);y=margin+(i//cols)*(ch+gap)
        inset=8 if style=='collage' and i%2 else 0
        items.append(LayoutItem(id='image-'+str(len(items)),asset_id=a.id,x=x+inset,y=y+inset,width=cw-inset*2,height=ch-inset*2,z_index=i,attribution_reference=a.id).model_dump())
    if style=='material':
        for i,c in enumerate((palette or ['#BFC9D3','#7B91A8','#DCE5EC'])[:8]):items.append(LayoutItem(id='color-'+str(i),kind='color',x=margin+i*80,y=h-70,width=64,height=38,fill=c,z_index=100+i).model_dump())
    return items

def validate_items(items,ratio,asset_ids):
    from PIL import ImageColor
    w,h=RATIOS[ratio]
    if len(items)>100:raise ValueError('最多 100 个画布元素')
    result=[];ids=set()
    for raw in items:
        a=LayoutItem.model_validate(raw)
        if a.id in ids:raise ValueError('元素 ID 重复')
        ids.add(a.id)
        # Rotation around element center, same convention used by canvas/export.
        r=math.radians(a.rotation);bw=abs(a.width*math.cos(r))+abs(a.height*math.sin(r));bh=abs(a.width*math.sin(r))+abs(a.height*math.cos(r));cx=a.x+a.width/2;cy=a.y+a.height/2
        if cx-bw/2<-.1 or cy-bh/2<-.1 or cx+bw/2>w+.1 or cy+bh/2>h+.1:raise ValueError('画布元素超出边界')
        if a.kind=='image' and a.asset_id not in asset_ids:raise ValueError('未知素材关联')
        if a.crop not in ({'mode':'contain'},{'mode':'cover'}):raise ValueError('不支持的裁切方式')
        ImageColor.getrgb(a.fill)
        a.attribution_reference=a.asset_id or '';result.append(a.model_dump())
    return result

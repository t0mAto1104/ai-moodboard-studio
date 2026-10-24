import type {Item} from '../types/models';
export const sizes:Record<string,[number,number]>={'16:9':[1200,675],'4:3':[1200,900],'1:1':[1000,1000],A4:[848,1200]};
export function fitItem(item:Item,ratio:string):Item {
 const [w,h]=sizes[ratio];const rotation=((item.rotation+180)%360+360)%360-180;
 const r=rotation*Math.PI/180,c=Math.abs(Math.cos(r)),s=Math.abs(Math.sin(r));
 let width=Math.max(8,item.width),height=Math.max(8,item.height);
 const shrink=Math.min(1,w/(width*c+height*s),h/(width*s+height*c));width*=shrink;height*=shrink;
 const bw=width*c+height*s,bh=width*s+height*c;
 const cx=Math.max(bw/2,Math.min(w-bw/2,item.x+width/2));const cy=Math.max(bh/2,Math.min(h-bh/2,item.y+height/2));
 return {...item,rotation,width,height,x:cx-width/2,y:cy-height/2};
}
export function newItem(kind:Item['kind'],index:number,asset_id:string|null=null):Item {
 return {id:crypto.randomUUID(),kind,asset_id,x:64,y:64,width:kind==='text'?360:kind==='image'?300:120,height:kind==='image'?240:kind==='text'?100:120,rotation:0,crop:{mode:'contain'},opacity:1,z_index:index,locked:false,text:kind==='text'?'写下你的灵感':'',fill:kind==='text'?'#222222':'#BFC9D3',attribution_reference:asset_id||'',font_size:32,font_family:'sans',font_weight:'normal',text_align:'left',line_height:1.2,shape:'rectangle'};
}

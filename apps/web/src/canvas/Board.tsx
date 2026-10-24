import {assetImage} from '../api';
import {useEffect,useRef,useState} from 'react';
import {Stage,Layer,Group,Image as KImage,Rect,Ellipse,Text,Transformer} from 'react-konva';
import type Konva from 'konva';
import {useEditor} from '../store/editor';
import {sizes,fitItem} from '../editor/geometry';
import type {Asset,Item} from '../types/models';
export {sizes} from '../editor/geometry';
function ImageNode({item,assets}:{item:Item;assets:Asset[]}){
 const [image,setImage]=useState<HTMLImageElement>();
 useEffect(()=>{setImage(undefined);const im=new window.Image();im.onload=()=>setImage(im);const a=assets.find(a=>a.id===item.asset_id);im.src=a?assetImage(a)||'':'';return()=>{im.onload=null}},[item.asset_id,assets]);
 if(!image)return <Rect x={-item.width/2} y={-item.height/2} width={item.width} height={item.height} fill="#eeeeee"/>;
 const iw=image.width,ih=image.height,scale=Math.min(item.width/iw,item.height/ih);
 if(item.crop.mode==='contain')return <KImage image={image} x={-iw*scale/2} y={-ih*scale/2} width={iw*scale} height={ih*scale}/>;
 const s=Math.max(item.width/iw,item.height/ih),cw=item.width/s,ch=item.height/s;
 return <KImage image={image} x={-item.width/2} y={-item.height/2} width={item.width} height={item.height} crop={{x:(iw-cw)/2,y:(ih-ch)/2,width:cw,height:ch}}/>;
}
function Element({item,ratio,assets}:{item:Item;ratio:string;assets:Asset[]}){
 const ref=useRef<Konva.Group>(null),tr=useRef<Konva.Transformer>(null);const {selection,select,edit}=useEditor();const chosen=selection.includes(item.id),single=chosen&&selection.length===1;
 useEffect(()=>{if(single&&ref.current&&tr.current)tr.current.nodes([ref.current])},[single,item]);
 return <><Group ref={ref} x={item.x+item.width/2} y={item.y+item.height/2} rotation={item.rotation} opacity={item.opacity} draggable={!item.locked}
 onClick={e=>{e.cancelBubble=true;select(item.id,e.evt.shiftKey||e.evt.metaKey||e.evt.ctrlKey)}} onTap={e=>{e.cancelBubble=true;select(item.id)}}
 onDragStart={()=>{if(!chosen)select(item.id)}}
 onDragEnd={e=>{const next=fitItem({...item,x:e.target.x()-item.width/2,y:e.target.y()-item.height/2},ratio);e.target.position({x:next.x+next.width/2,y:next.y+next.height/2});edit(item.id,next)}}
 onTransformEnd={()=>{const n=ref.current!;const next=fitItem({...item,width:Math.max(8,item.width*n.scaleX()),height:Math.max(8,item.height*n.scaleY()),rotation:n.rotation(),x:n.x()-item.width*n.scaleX()/2,y:n.y()-item.height*n.scaleY()/2},ratio);n.scale({x:1,y:1});n.position({x:next.x+next.width/2,y:next.y+next.height/2});n.rotation(next.rotation);edit(item.id,next)}}>
 <Rect x={-item.width/2} y={-item.height/2} width={item.width} height={item.height} fill="rgba(0,0,0,0)" stroke={chosen?'#555555':undefined} strokeWidth={1}/>
 {item.kind==='image'?<ImageNode item={item} assets={assets}/>:item.kind==='text'?<Text x={-item.width/2} y={-item.height/2} text={item.text} width={item.width} height={item.height} wrap="char" fontSize={item.font_size||24} fontFamily={item.font_family==='serif'?'Times New Roman,serif':item.font_family==='mono'?'Menlo,monospace':'Helvetica,PingFang SC,sans-serif'} fontStyle={item.font_weight||'normal'} align={item.text_align||'left'} lineHeight={item.line_height||1.2} fill={item.fill}/>:item.shape==='ellipse'?<Ellipse radiusX={item.width/2} radiusY={item.height/2} fill={item.fill}/>:<Rect x={-item.width/2} y={-item.height/2} width={item.width} height={item.height} fill={item.fill}/>}
 </Group>{single&&!item.locked&&<Transformer ref={tr} rotateEnabled flipEnabled={false} keepRatio={item.kind==='image'} anchorSize={9} borderStroke="#555" anchorStroke="#555" boundBoxFunc={(old,b)=>Math.abs(b.width)<8||Math.abs(b.height)<8?old:b}/>}</>;
}
export default function Board({ratio,assets,zoom=1}:{ratio:string;assets:Asset[];zoom?:number}){
 const {items,select,background}=useEditor();const [viewport,setViewport]=useState<[number,number]>([700,600]);const ref=useRef<HTMLDivElement>(null);const [w,h]=sizes[ratio];
 useEffect(()=>{const ob=new ResizeObserver(entries=>setViewport([Math.max(180,entries[0].contentRect.width),Math.max(200,entries[0].contentRect.height)]));if(ref.current?.parentElement)ob.observe(ref.current.parentElement);return()=>ob.disconnect()},[]);
 const s=Math.min(1,viewport[0]/w,viewport[1]/h)*zoom;
 return <div ref={ref} className="canvas-viewport"><div className="canvas-wrap" style={{width:w*s,height:h*s}} role="img" aria-label="可编辑 Mood Board 画布"><Stage width={w*s} height={h*s} scaleX={s} scaleY={s} onMouseDown={e=>{if(e.target===e.target.getStage())select(null)}}><Layer><Rect width={w} height={h} fill={background} listening={false}/>{[...items].sort((a,b)=>a.z_index-b.z_index).map(item=><Element key={item.id} item={item} ratio={ratio} assets={assets}/>)}</Layer></Stage></div></div>;
}

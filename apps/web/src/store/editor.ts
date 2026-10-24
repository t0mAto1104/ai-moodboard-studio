import {create} from 'zustand';
import type {Item,Project} from '../types/models';
import {fitItem,sizes} from '../editor/geometry';
type Document={items:Item[];background:string;ratio:string;name:string};
type State=Document & {
 selected:string|null;selection:string[];dirty:boolean;past:Document[];future:Document[];saved:string;
 load:(p:Project)=>void;setItems:(items:Item[])=>void;markSaved:(doc:Document)=>void;
 select:(id:string|null,extend?:boolean)=>void;selectAll:()=>void;
 edit:(id:string,changes:Partial<Item>)=>void;remove:(id?:string)=>void;add:(item:Item)=>void;
 change:(changes:Partial<Document>)=>void;undo:()=>void;redo:()=>void;
 duplicate:()=>void;move:(dx:number,dy:number)=>void;reorder:(id:string,direction:'up'|'down'|'front'|'back')=>void;
 align:(direction:'left'|'center'|'right'|'top'|'middle'|'bottom')=>void;resize:(ratio:string)=>void;
};
export const documentOf=(s:Document):Document=>({items:s.items,background:s.background,ratio:s.ratio,name:s.name});
export const useEditor=create<State>((set,get)=>{
 const commit=(changes:Partial<Document>)=>set(s=>{
  const next={...documentOf(s),...changes};if(JSON.stringify(next)===JSON.stringify(documentOf(s)))return {};
  return {...next,past:[...s.past,documentOf(s)].slice(-80),future:[],dirty:JSON.stringify(next)!==s.saved};
 });
 return {
 items:[],background:'#ffffff',ratio:'16:9',name:'未命名画板',selected:null,selection:[],dirty:false,past:[],future:[],saved:'',
 load:p=>{const doc={items:p.items,background:p.background||'#ffffff',ratio:p.ratio,name:p.name};set({...doc,selected:null,selection:[],dirty:false,past:[],future:[],saved:JSON.stringify(doc)})},
 setItems:items=>{const doc={...documentOf(get()),items};set({...doc,selected:null,selection:[],dirty:false,past:[],future:[],saved:JSON.stringify(doc)})},
 markSaved:doc=>set(s=>({saved:JSON.stringify(doc),dirty:JSON.stringify(documentOf(s))!==JSON.stringify(doc)})),
 select:(id,extend=false)=>set(s=>{const selection=!id?[]:extend?s.selection.includes(id)?s.selection.filter(x=>x!==id):[...s.selection,id]:[id];return {selection,selected:selection.at(-1)||null}}),
 selectAll:()=>set(s=>({selection:s.items.map(i=>i.id),selected:s.items.at(-1)?.id||null})),
 change:commit,
 edit:(id,changes)=>{const s=get();commit({items:s.items.map(i=>i.id===id?fitItem({...i,...changes},s.ratio):i)})},
 add:item=>{const s=get();if(s.items.length>=100)return;commit({items:[...s.items,fitItem(item,s.ratio)]});set({selected:item.id,selection:[item.id]})},
 remove:id=>{const s=get();const ids=id?[id]:s.selection;commit({items:s.items.filter(i=>!ids.includes(i.id)||i.locked)});set({selected:null,selection:[]})},
 undo:()=>{const s=get();if(!s.past.length)return;const doc=s.past.at(-1)!;set({...doc,past:s.past.slice(0,-1),future:[documentOf(s),...s.future],selected:null,selection:[],dirty:JSON.stringify(doc)!==s.saved})},
 redo:()=>{const s=get();if(!s.future.length)return;const doc=s.future[0];set({...doc,past:[...s.past,documentOf(s)],future:s.future.slice(1),selected:null,selection:[],dirty:JSON.stringify(doc)!==s.saved})},
 duplicate:()=>{const s=get();const copies=s.items.filter(i=>s.selection.includes(i.id)&&!i.locked).map((i,n)=>fitItem({...i,id:crypto.randomUUID(),x:i.x+24,y:i.y+24,z_index:Math.max(0,...s.items.map(x=>x.z_index))+n+1},s.ratio));if(s.items.length+copies.length>100)return;commit({items:[...s.items,...copies]});set({selection:copies.map(i=>i.id),selected:copies.at(-1)?.id||null})},
 move:(dx,dy)=>{const s=get();commit({items:s.items.map(i=>s.selection.includes(i.id)&&!i.locked?fitItem({...i,x:i.x+dx,y:i.y+dy},s.ratio):i)})},
 reorder:(id,direction)=>{const s=get();if(s.items.find(i=>i.id===id)?.locked)return;const ordered=[...s.items].sort((a,b)=>a.z_index-b.z_index);const index=ordered.findIndex(i=>i.id===id);if(index<0)return;const [item]=ordered.splice(index,1);const target=direction==='front'?ordered.length:direction==='back'?0:Math.max(0,Math.min(ordered.length,index+(direction==='up'?1:-1)));ordered.splice(target,0,item);commit({items:ordered.map((i,n)=>({...i,z_index:n}))})},
 align:direction=>{const s=get();const [w,h]=sizes[s.ratio];commit({items:s.items.map(i=>{if(!s.selection.includes(i.id)||i.locked)return i;const changes=direction==='left'?{x:0}:direction==='center'?{x:(w-i.width)/2}:direction==='right'?{x:w-i.width}:direction==='top'?{y:0}:direction==='middle'?{y:(h-i.height)/2}:{y:h-i.height};return fitItem({...i,...changes},s.ratio)})})},
 resize:ratio=>{const s=get(),[ow,oh]=sizes[s.ratio],[w,h]=sizes[ratio];commit({ratio,items:s.items.map(i=>fitItem({...i,x:i.x*w/ow,y:i.y*h/oh,width:i.width*w/ow,height:i.height*h/oh},ratio))})},
 };
});

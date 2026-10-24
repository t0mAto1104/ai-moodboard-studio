import {beforeEach,expect,it} from 'vitest';
import {useEditor,documentOf} from '../store/editor';
import {newItem,fitItem,sizes} from './geometry';
import type {Project} from '../types/models';
const p={id:'p',name:'Board',ratio:'16:9',background:'#ffffff',items:[],assets:[]} as unknown as Project;
beforeEach(()=>useEditor.getState().load(p));
it('undo/redo restores the document and compares with the last saved state',()=>{
 const s=useEditor.getState();s.add(newItem('text',1));const first=documentOf(useEditor.getState());s.markSaved(first);s.change({background:'#123456',name:'New title'});
 expect(useEditor.getState().dirty).toBe(true);s.undo();expect(documentOf(useEditor.getState())).toEqual(first);expect(useEditor.getState().dirty).toBe(false);s.redo();expect(useEditor.getState().background).toBe('#123456');expect(useEditor.getState().dirty).toBe(true);
});
it('duplicates maintain attribution and locked elements resist delete, nudge and duplication',()=>{
 const s=useEditor.getState();const a=newItem('image',1,'source:1');s.add(a);s.duplicate();const copy=useEditor.getState().items[1];expect(copy.asset_id).toBe('source:1');expect(copy.attribution_reference).toBe('source:1');expect(copy.id).not.toBe(a.id);
 s.edit(copy.id,{locked:true});const before=documentOf(useEditor.getState());s.move(10,10);s.duplicate();s.select(copy.id);s.remove();expect(documentOf(useEditor.getState())).toEqual(before);
});
it('selection actions undo as one operation and resize preserves rotated boundaries',()=>{
 const s=useEditor.getState();s.add(newItem('image',1,'source:1'));s.add(newItem('text',2));s.selectAll();s.move(10,10);const after=documentOf(useEditor.getState());s.remove();expect(useEditor.getState().items).toHaveLength(0);s.undo();expect(documentOf(useEditor.getState())).toEqual(after);
 s.resize('A4');for(const i of useEditor.getState().items)expect(fitItem(i,'A4')).toEqual(i);
});
it('clamps rotated rectangles to the actual canvas bounds',()=>{
 for(const ratio of Object.keys(sizes))for(const rotation of [-175,-90,45,179]){
  const i=fitItem({...newItem('image',1),x:-200,y:3000,width:4000,height:1500,rotation},ratio),r=i.rotation*Math.PI/180,[w,h]=sizes[ratio];
  const bw=Math.abs(i.width*Math.cos(r))+Math.abs(i.height*Math.sin(r)),bh=Math.abs(i.width*Math.sin(r))+Math.abs(i.height*Math.cos(r));
  expect(i.x+i.width/2-bw/2).toBeGreaterThanOrEqual(-.0001);expect(i.y+i.height/2-bh/2).toBeGreaterThanOrEqual(-.0001);expect(i.x+i.width/2+bw/2).toBeLessThanOrEqual(w+.0001);expect(i.y+i.height/2+bh/2).toBeLessThanOrEqual(h+.0001);
 }
});
it('layer order can be reversed through undo',()=>{
 const s=useEditor.getState(),a=newItem('color',1),b=newItem('text',2);s.add(a);s.add(b);s.reorder(a.id,'front');expect(useEditor.getState().items.at(-1)?.id).toBe(a.id);s.undo();expect(useEditor.getState().items.at(-1)?.id).toBe(b.id);
});

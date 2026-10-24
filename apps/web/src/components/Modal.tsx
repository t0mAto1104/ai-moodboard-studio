import {useEffect,useId,useRef,type ReactNode} from 'react';
import {X} from 'lucide-react';
export default function Modal({title,children,onClose}:{title:string;children:ReactNode;onClose:()=>void}){
 const ref=useRef<HTMLElement>(null);const titleId=useId();
 useEffect(()=>{const previous=document.activeElement as HTMLElement;ref.current?.focus();return()=>previous?.focus()},[]);
 return <div className="modal-backdrop" onClick={e=>{if(e.target===e.currentTarget)onClose()}}><section ref={ref} className="panel modal library-modal" role="dialog" aria-modal="true" aria-labelledby={titleId} tabIndex={-1} onKeyDown={e=>{
  if(e.key==='Escape'){e.stopPropagation();onClose()}
  if(e.key==='Tab'){
   const nodes=ref.current?.querySelectorAll<HTMLElement>('button:not([disabled]),input:not([disabled]),select:not([disabled]),a[href]');
   if(!nodes?.length)return;
   const first=nodes[0],last=nodes[nodes.length-1];
   if(e.shiftKey&&(document.activeElement===first||document.activeElement===ref.current)){e.preventDefault();last.focus()}
   else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
  }
 }}><div className="modal-title"><h2 id={titleId}>{title}</h2><button className="ghost icon-button" aria-label="关闭" onClick={onClose}><X size={20}/></button></div>{children}</section></div>
}

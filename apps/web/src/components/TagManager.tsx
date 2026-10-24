import {useState} from 'react';
import {Check,Trash2} from 'lucide-react';
import Modal from './Modal';
import {useLibrary} from '../hooks/useLibrary';
export default function TagManager({onClose}:{onClose:()=>void}){
 const library=useLibrary();const [name,setName]=useState('');const [drafts,setDrafts]=useState<Record<string,string>>({});const [error,setError]=useState('');const [busy,setBusy]=useState(false);
 async function act(fn:()=>Promise<unknown>){setBusy(true);setError('');try{await fn()}catch(e){setError(String(e))}finally{setBusy(false)}}
 return <Modal title="标签" onClose={onClose}><div className="tag-manager-list">{library.tags.map(t=><div className="tag-row" key={t.id}><input aria-label={'标签名称：'+t.name} value={drafts[t.id]??t.name} maxLength={40} onChange={e=>setDrafts({...drafts,[t.id]:e.target.value})}/><button className="ghost icon-button" aria-label={'保存标签：'+t.name} disabled={busy||!drafts[t.id]?.trim()} onClick={()=>act(()=>library.renameTag(t.id,drafts[t.id].trim()))}><Check size={18}/></button><button className="ghost icon-button" aria-label={'删除标签：'+t.name} disabled={busy} onClick={()=>{if(window.confirm('删除标签“'+t.name+'”？收藏的图片会保留。'))act(()=>library.deleteTag(t.id))}}><Trash2 size={18}/></button></div>)}</div><form className="tag-create" onSubmit={e=>{e.preventDefault();act(async()=>{await library.createTag(name.trim());setName('')})}}><input aria-label="新标签名称" placeholder="新建标签" maxLength={40} value={name} onChange={e=>setName(e.target.value)}/><button disabled={busy||!name.trim()}>创建</button></form>{error&&<p role="alert">{error}</p>}</Modal>
}

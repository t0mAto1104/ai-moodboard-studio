import {useState} from 'react';
import Modal from './Modal';
import {useLibrary} from '../hooks/useLibrary';
import type {Asset} from '../types/models';
export default function TagPicker({asset,onClose,onNotify}:{asset:Asset;onClose:()=>void;onNotify:(message:string)=>void}){
 const library=useLibrary();const favorite=library.favorites.find(f=>f.asset_id===asset.id);
 const [ids,setIds]=useState(favorite?.tag_ids||[]);const [name,setName]=useState('');const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 async function create(){if(!name.trim())return;setBusy(true);try{const tag=await library.createTag(name.trim());setIds([...ids,tag.id]);setName('')}catch(e){setError(String(e))}finally{setBusy(false)}}
 return <Modal title="收藏到" onClose={onClose}><div className="tag-picker-list">{library.tags.map(t=><label className="check" key={t.id}><input type="checkbox" checked={ids.includes(t.id)} onChange={e=>setIds(e.target.checked?[...ids,t.id]:ids.filter(id=>id!==t.id))}/>{t.name}</label>)}</div><form className="tag-create" onSubmit={e=>{e.preventDefault();create()}}><input aria-label="新标签名称" placeholder="新建标签" value={name} maxLength={40} onChange={e=>setName(e.target.value)}/><button className="secondary" disabled={busy||!name.trim()}>创建</button></form>{error&&<p role="alert">{error}</p>}<div className="actions"><button disabled={busy} onClick={async()=>{setBusy(true);try{await library.save(asset.id,ids);onNotify('已收藏');onClose()}catch(e){setError(String(e));setBusy(false)}}}>保存</button><button className="ghost" disabled={busy} onClick={onClose}>取消</button></div></Modal>
}

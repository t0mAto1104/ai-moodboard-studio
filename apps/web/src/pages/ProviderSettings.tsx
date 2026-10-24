import {useState} from 'react';
import {useQuery} from '@tanstack/react-query';
import {api} from '../api';
type Provider={id:string;enabled:boolean;configured:boolean;status:string;analysis_enabled?:boolean;diagnostics?:{http_status:number;quota?:{remaining?:string;limit?:string}}};
const names:Record<string,string>={artic:'Art Institute of Chicago',metmuseum:'The Met',openverse:'Openverse',pixabay:'Pixabay',unsplash:'Unsplash',mock:'演示素材'};
export default function ProviderSettings(){
 const providers=useQuery({queryKey:['providers'],queryFn:()=>api<Provider[]>('/providers')});
 const [keys,setKeys]=useState<Record<string,string>>({});
 const [message,setMessage]=useState('');
 const [busy,setBusy]=useState(false);
 async function save(p:Provider,enabled:boolean,remove=false){
  setBusy(true);setMessage('');
  try{await api('/providers/'+p.id+'/settings',{enabled,...(remove?{api_key:''}:keys[p.id]?{api_key:keys[p.id]}:{})},'PUT');setKeys(k=>({...k,[p.id]:''}));await providers.refetch();setMessage('已保存')}
  catch(e){setMessage(String(e))}finally{setBusy(false)}
 }
 return <section className="panel"><h2>图片来源</h2>{providers.data?.map(p=><div key={p.id}>
  <label className="check"><input type="checkbox" checked={p.enabled} disabled={busy} onChange={e=>save(p,e.target.checked)}/>{names[p.id]||p.id}</label><div className="actions"><button className="ghost" disabled={busy||!p.configured} onClick={async()=>{setBusy(true);try{const r=await api('/providers/'+p.id+'/health',{});setMessage((names[p.id]||p.id)+'：'+(r.status==='ok'?'连接成功':r.error||'暂不可用'));await providers.refetch()}catch(e){setMessage(String(e))}finally{setBusy(false)}}}>测试连接</button>{p.diagnostics?.quota?.remaining&&<small>剩余 {p.diagnostics.quota.remaining} / {p.diagnostics.quota.limit}</small>}</div>
  {['pixabay','unsplash'].includes(p.id)&&<div className="actions"><input aria-label={names[p.id]+' API Key'} type="password" autoComplete="off" value={keys[p.id]||''} placeholder={p.configured?'已配置密钥':'API Key'} onChange={e=>setKeys({...keys,[p.id]:e.target.value})}/><button className="secondary" disabled={busy||!keys[p.id]} onClick={()=>save(p,p.enabled)}>保存</button>{p.configured&&<button className="ghost" disabled={busy} onClick={()=>save(p,p.enabled,true)}>删除密钥</button>}</div>}
 {p.id==='unsplash'&&<label className="check" title="需已获得本地图片编码与排序授权；图片只在内存处理"><input type="checkbox" checked={!!p.analysis_enabled} disabled={busy||!p.configured} onChange={async e=>{setBusy(true);try{await api('/providers/unsplash/settings',{enabled:p.enabled,analysis_enabled:e.target.checked,analysis_rights_confirmed:e.target.checked},'PUT');await providers.refetch();setMessage('已更新本地分析设置')}catch(error){setMessage(String(error))}finally{setBusy(false)}}}/>本地视觉分析（已获授权）</label>}
 </div>)}{message&&<p role="status">{message}</p>}</section>
}

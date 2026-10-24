export async function api<T=any>(path:string,body?:unknown,method?:string):Promise<T>{const r=await fetch('/api'+path,{method:method||(body===undefined?'GET':'POST'),headers:{'Content-Type':'application/json','X-Moodboard-Request':'1'},body:body===undefined?undefined:JSON.stringify(body)});if(!r.ok){const d=await r.json().catch(()=>({detail:'请求失败'}));throw Error(typeof d.detail==='string'?d.detail:JSON.stringify(d.detail))}return r.json()}
export async function waitJob(id:string,progress:(j:any)=>void){for(;;){const j=await api('/jobs/'+id);progress(j);if(j.status==='completed')return j.result;if(['failed','cancelled'].includes(j.status))throw Error(j.error||'任务已取消');await new Promise(r=>setTimeout(r,600))}}
export function sourceLink(url:string){try{const u=new URL(url);return ['https:','http:'].includes(u.protocol)?url:undefined}catch{return undefined}}

export function assetImage(a:import('./types/models').Asset){return a.display_url|| (a.allowed_temporary_analysis?'/api/assets/'+encodeURIComponent(a.id)+'/image':undefined)}

export async function downloadAsset(id:string){
 const response=await fetch('/api/assets/'+encodeURIComponent(id)+'/download',{method:'POST',headers:{'X-Moodboard-Request':'1'}});
 if(!response.ok){const data=await response.json().catch(()=>({detail:'下载失败'}));throw Error(data.detail||'下载失败')}
 const blob=await response.blob();const url=URL.createObjectURL(blob);
 const disposition=response.headers.get('content-disposition')||'';
 const filename=disposition.match(/filename="([^"]+)"/)?.[1]||'image.jpg';
 const link=document.createElement('a');link.href=url;link.download=filename;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

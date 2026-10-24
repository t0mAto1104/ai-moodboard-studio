import {useEffect,useState} from 'react';
import {Bookmark,Plus} from 'lucide-react';
import {useLibrary} from '../hooks/useLibrary';
import AssetCard from '../components/AssetCard';
import TagManager from '../components/TagManager';
import type {Asset} from '../types/models';
export default function Home({onDetails,onGroup,onNotify,onSearch}:{onDetails:(asset:Asset)=>void;onGroup:(asset:Asset)=>void;onNotify:(message:string)=>void;onSearch:()=>void}){
 const library=useLibrary();const [filter,setFilter]=useState('all');const [manage,setManage]=useState(false);
 useEffect(()=>{if(filter!=='all'&&filter!=='untagged'&&!library.tags.some(t=>t.id===filter))setFilter('all')},[library.tags,filter]);
 const rows=library.favorites.filter(f=>filter==='all'||(filter==='untagged'?!f.tag_ids.length:f.tag_ids.includes(filter)));
 return <><div className="library-toolbar"><div className="gallery-tabs" role="tablist" aria-label="收藏标签"><button role="tab" aria-selected={filter==='all'} className={'tab '+(filter==='all'?'active':'')} onClick={()=>setFilter('all')}>全部</button><button role="tab" aria-selected={filter==='untagged'} className={'tab '+(filter==='untagged'?'active':'')} onClick={()=>setFilter('untagged')}>未分组</button>{library.tags.map(t=><button role="tab" aria-selected={filter===t.id} className={'tab '+(filter===t.id?'active':'')} key={t.id} onClick={()=>setFilter(t.id)}>{t.name}</button>)}</div><button className="icon-button" aria-label="管理标签" title="管理标签" onClick={()=>setManage(true)}><Plus size={22}/></button></div>{library.isLoading?<div className="empty" role="status">加载收藏…</div>:library.error?<p role="alert">收藏加载失败，请稍后重试</p>:rows.length?<div className="grid masonry">{rows.map(f=><AssetCard key={f.asset_id} asset={f.asset} saved onSave={()=>library.remove(f.asset_id)} onGroup={()=>onGroup(f.asset)} onDetails={()=>onDetails(f.asset)} onNotify={onNotify}/>)}</div>:<div className="empty"><Bookmark size={30}/><h2>{library.favorites.length?'这个标签还没有收藏':'收藏喜欢的图片'}</h2><button className="secondary" onClick={onSearch}>去搜索</button></div>}{manage&&<TagManager onClose={()=>setManage(false)}/>}</>
}

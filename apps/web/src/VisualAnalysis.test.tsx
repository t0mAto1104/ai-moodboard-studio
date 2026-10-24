import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import App from './App';
vi.mock('./canvas/Board',()=>({default:()=>null}));
it('runs a separate visual analysis job after authorized search and displays actual device',async()=>{
 const calls:Array<{url:string;body:any}>=[];
 const photo={id:'unsplash:granted',provider:'unsplash',title:'Kitten',creator_name:'Artist',source_page_url:'https://unsplash.com/photos/granted',display_url:'https://images.unsplash.com/photo-granted',allowed_temporary_analysis:true,allowed_export:false,final_score:.8};
 vi.stubGlobal('fetch',vi.fn(async(url:string,options?:RequestInit)=>{
  calls.push({url,body:options?.body?JSON.parse(options.body as string):null});
  const data=url==='/api/providers'?[{id:'unsplash',enabled:true,configured:true,analysis_enabled:true}]:url==='/api/projects'?[]:url==='/api/intent/parse'?{mode:'rules',intent:{subject:'kitty',search_queries:['kitty'],target_palette:[]}}:url==='/api/search'?{job_id:'retrieval'}:url==='/api/search/rank'?{job_id:'vision'}:url==='/api/jobs/retrieval'?{status:'completed',progress:100,result:{assets:[photo],errors:[]}}:url==='/api/jobs/vision'?{status:'completed',progress:100,result:{assets:[photo],stats:{ranking_mode:'siglip2',device:'mps',analyzed_count:1,warnings:[]}}}:{};
  return {ok:true,json:async()=>data};
 }));
 render(<QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}><App/></QueryClientProvider>);
 await waitFor(()=>expect(calls.some(c=>c.url==='/api/providers')).toBe(true));
 fireEvent.change(screen.getByLabelText('搜索灵感'),{target:{value:'kitty'}});
 fireEvent.click(screen.getByRole('button',{name:'开始搜索'}));
 expect(await screen.findByText(/SigLIP 2 · MPS · 已分析 1 张/)).toBeInTheDocument();
 expect(calls.find(c=>c.url==='/api/search/rank')?.body.asset_ids).toEqual(['unsplash:granted']);
});

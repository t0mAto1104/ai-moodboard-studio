import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import App from './App';
vi.mock('./canvas/Board',()=>({default:()=>null}));
it('search uses enabled configured provider instead of disabled defaults and displays remote preview',async()=>{
 const requests:Array<{url:string;body:any}>=[];
 vi.stubGlobal('fetch',vi.fn(async(url:string,options?:RequestInit)=>{
  const body=options?.body?JSON.parse(options.body as string):null;requests.push({url,body});
  const data=url==='/api/providers'?[{id:'unsplash',enabled:true,configured:true},{id:'artic',enabled:false,configured:true}]:url==='/api/projects'?[]:url==='/api/intent/parse'?{mode:'rules',intent:{search_queries:['kitty'],target_palette:[],subject:'kitty'}}:url==='/api/search'?{job_id:'search-job'}:url==='/api/jobs/search-job'?{status:'completed',progress:100,result:{assets:[{id:'unsplash:cat',provider:'unsplash',title:'Cat',creator_name:'Artist',creator_url:'https://unsplash.com/@artist',source_page_url:'https://unsplash.com/photos/cat',display_url:'https://images.unsplash.com/photo-cat?ixid=test',allowed_reference_board:true,allowed_temporary_analysis:false,final_score:0}],errors:[]}}:{};
  return {ok:true,json:async()=>data};
 }));
 render(<QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}><App/></QueryClientProvider>);
 await waitFor(()=>expect(requests.some(r=>r.url==='/api/providers')).toBe(true));
 fireEvent.change(screen.getByLabelText('搜索灵感'),{target:{value:'kitty'}});
 fireEvent.click(screen.getByRole('button',{name:'开始搜索'}));
 const image=await screen.findByRole('img',{name:'Cat'});
 expect(image).toHaveAttribute('src','https://images.unsplash.com/photo-cat?ixid=test');
 expect(requests.find(r=>r.url==='/api/search')?.body.providers).toEqual(['unsplash']);
 expect(screen.getByRole('link',{name:'Artist'})).toHaveAttribute('href','https://unsplash.com/@artist');
});

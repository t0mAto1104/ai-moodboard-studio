import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import App from './App';
vi.mock('./canvas/Board',()=>({default:()=>null}));
it('saves a search image to home, creates a tag, assigns it and reopens the grouped library',async()=>{
 const photo={id:'unsplash:library-cat',provider:'unsplash',title:'Library kitten',creator_name:'Artist',creator_url:'https://unsplash.com/@artist',source_page_url:'https://unsplash.com/photos/library-cat',display_url:'https://images.unsplash.com/photo-cat',allowed_temporary_analysis:false,allowed_download:true,final_score:0};
 const library:{tags:Array<{id:string;name:string;created_at:number}>;favorites:Array<any>}={tags:[],favorites:[]};
 vi.stubGlobal('fetch',vi.fn(async(url:string,options?:RequestInit)=>{
  const body=options?.body?JSON.parse(options.body as string):null;let data:any={};
  if(url==='/api/library')data=structuredClone(library);
  else if(url==='/api/library/tags'&&body){const tag={id:'tag-1',name:body.name,created_at:1};library.tags.push(tag);data=tag}
  else if(url==='/api/library/favorites/unsplash%3Alibrary-cat'&&body){const value={asset_id:photo.id,tag_ids:body.tag_ids,saved_at:1,asset:photo};library.favorites=[value];data=value}
  else if(url==='/api/providers')data=[{id:'unsplash',enabled:true,configured:true}];
  else if(url==='/api/projects')data=[];
  else if(url==='/api/intent/parse')data={mode:'rules',intent:{subject:'cat',search_queries:['cat'],target_palette:[]}};
  else if(url==='/api/search')data={job_id:'library-search'};
  else if(url==='/api/jobs/library-search')data={status:'completed',progress:100,result:{assets:[photo],errors:[]}};
  return {ok:true,json:async()=>data};
 }));
 function app(){return render(<QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}><App/></QueryClientProvider>)}
 const first=app();
 expect(await screen.findByText('收藏喜欢的图片')).toBeInTheDocument();
 fireEvent.change(screen.getByLabelText('搜索灵感'),{target:{value:'cat'}});
 fireEvent.click(screen.getByRole('button',{name:'开始搜索'}));
 await screen.findByRole('img',{name:photo.title});
 fireEvent.click(screen.getByRole('button',{name:'收藏：'+photo.title}));
 await waitFor(()=>expect(library.favorites).toHaveLength(1));
 fireEvent.click(screen.getByRole('button',{name:'主页'}));
 await screen.findByRole('img',{name:photo.title});
 fireEvent.click(screen.getByRole('tab',{name:'未分组'}));
 fireEvent.click(screen.getByRole('button',{name:'管理标签'}));
 fireEvent.change(screen.getByLabelText('新标签名称'),{target:{value:'材质'}});
 fireEvent.click(screen.getByRole('button',{name:'创建'}));
 await screen.findByLabelText('标签名称：材质');
 fireEvent.click(screen.getByRole('button',{name:'关闭'}));
 fireEvent.click(screen.getByRole('button',{name:'设置标签：'+photo.title}));
 fireEvent.click(screen.getByRole('checkbox',{name:'材质'}));
 fireEvent.click(screen.getByRole('button',{name:'保存'}));
 await waitFor(()=>expect(library.favorites[0].tag_ids).toEqual(['tag-1']));
 await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
 fireEvent.click(screen.getByRole('tab',{name:'材质'}));
 expect(screen.getByRole('img',{name:photo.title})).toBeInTheDocument();
 first.unmount();app();
 fireEvent.click(await screen.findByRole('tab',{name:'材质'}));
 expect(screen.getByRole('img',{name:photo.title})).toBeInTheDocument();
});

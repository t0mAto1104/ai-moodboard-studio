import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import AssetCard from './AssetCard';
import {downloadAsset} from '../api';
vi.mock('../api',()=>({assetImage:()=>undefined,sourceLink:(url:string)=>url,downloadAsset:vi.fn().mockResolvedValue(undefined)}));
const photo:any={id:'test',provider:'openverse',title:'Test image',creator_name:'Artist',source_page_url:'https://example.org/photo',allowed_download:false,download_reason:'许可未核实'};
it('unknown download permission offers the source instead of downloading',()=>{
 render(<AssetCard asset={photo} onSave={vi.fn()} onGroup={vi.fn()} onDetails={vi.fn()} onNotify={vi.fn()}/>);
 expect(screen.queryByRole('button',{name:'下载：Test image'})).not.toBeInTheDocument();
 expect(screen.getByRole('link',{name:'到来源下载：Test image'})).toHaveAttribute('href','https://example.org/photo');
});
it('explicit authorized download invokes a separate manual download',async()=>{
 const notify=vi.fn();render(<AssetCard asset={{...photo,allowed_download:true}} onSave={vi.fn()} onGroup={vi.fn()} onDetails={vi.fn()} onNotify={notify}/>);
 fireEvent.click(screen.getByRole('button',{name:'下载：Test image'}));
 await waitFor(()=>expect(downloadAsset).toHaveBeenCalledWith('test'));
 expect(notify).toHaveBeenCalledWith('下载已开始');
});

import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import ProviderSettings from './ProviderSettings';
import {api} from '../api';
vi.mock('../api',()=>({api:vi.fn()}));
it('saves provider key then clears the input',async()=>{
 vi.mocked(api).mockImplementation(async(path)=>path==='/providers'?[{id:'pixabay',enabled:false,configured:false,status:'reference-only'}]:{saved:true});
 render(<QueryClientProvider client={new QueryClient()}><ProviderSettings/></QueryClientProvider>);
 const input=await screen.findByLabelText('Pixabay API Key');
 fireEvent.change(input,{target:{value:'test-only-key'}});
 fireEvent.click(screen.getByRole('button',{name:'保存'}));
 await waitFor(()=>expect(api).toHaveBeenCalledWith('/providers/pixabay/settings',{enabled:false,api_key:'test-only-key'},'PUT'));
 await waitFor(()=>expect(input).toHaveValue(''));
});

import {useQuery,useQueryClient} from '@tanstack/react-query';
import {api} from '../api';
import type {Asset} from '../types/models';
export type LibraryTag={id:string;name:string;created_at:number};
export type Favorite={asset_id:string;tag_ids:string[];saved_at:number;asset:Asset};
export type LibraryData={tags:LibraryTag[];favorites:Favorite[]};
const EMPTY_TAGS:LibraryTag[]=[];
const EMPTY_FAVORITES:Favorite[]=[];
export function useLibrary(){
 const client=useQueryClient();
 const query=useQuery({queryKey:['library'],queryFn:()=>api<LibraryData>('/library')});
 const refresh=()=>client.invalidateQueries({queryKey:['library']});
 return {...query,tags:query.data?.tags||EMPTY_TAGS,favorites:query.data?.favorites||EMPTY_FAVORITES,
  async save(assetId:string,tagIds:string[]=[]){await api('/library/favorites/'+encodeURIComponent(assetId),{tag_ids:tagIds},'PUT');await refresh()},
  async remove(assetId:string){await api('/library/favorites/'+encodeURIComponent(assetId),undefined,'DELETE');await refresh()},
  async createTag(name:string){const tag=await api<LibraryTag>('/library/tags',{name});await refresh();return tag},
  async renameTag(id:string,name:string){await api('/library/tags/'+id,{name},'PATCH');await refresh()},
  async deleteTag(id:string){await api('/library/tags/'+id,undefined,'DELETE');await refresh()},
 };
}

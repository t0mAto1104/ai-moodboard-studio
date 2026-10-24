from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
import time
class SearchIntent(BaseModel):
    model_config=ConfigDict(extra='forbid')
    raw_prompt:str=''
    subject:str=Field(min_length=1,max_length=300)
    style_keywords:list[str]=[]
    materials:list[str]=[]
    color_keywords:list[str]=[]
    target_palette:list[str]=Field(default=['#BFC9D3','#7B91A8','#DCE5EC'],max_length=8)
    mood_keywords:list[str]=[]
    search_queries:list[str]=Field(min_length=1,max_length=4)
    negative_keywords:list[str]=[]
    preferred_orientation:Literal['mixed','landscape','portrait','square']='mixed'
    layout_style:Literal['editorial','material','collage']='editorial'
    target_image_count:int=Field(default=8,ge=1,le=24)
    search_language:str='en'
    optional_subject_categories:list[str]=[]
    @field_validator('target_palette')
    @classmethod
    def valid_palette(cls, values):
        import re
        if any(not re.fullmatch(r'#[0-9a-fA-F]{6}', v) for v in values):
            raise ValueError('颜色必须为 #RRGGBB 格式')
        return values
class ImageAsset(BaseModel):
    id:str
    provider:str
    provider_asset_id:str
    title:str='Untitled'
    description:str=''
    creator_name:str='Unknown'
    creator_url:str=''
    source_page_url:str=''
    thumbnail_url:str=''
    image_url:str=''
    local_file_path:str|None=None
    width:int=0
    height:int=0
    license_type:str='Unknown'
    license_url:str=''
    license_evidence:dict={}
    license_verified_at:float|None=None
    attribution_text:str=''
    display_url:str=''
    allowed_reference_board:bool=False
    allowed_download:bool=False
    download_url:str=''
    download_reason:str='许可未核实，请到来源页面确认' 
    allowed_display:bool=False
    allowed_temporary_analysis:bool=False
    allowed_store:bool=False
    allowed_transform:bool=False
    allowed_export:bool=False
    copyright_review_status:str='unknown'
    query_origin:str=''
    semantic_score:float=0
    palette_score:float=0
    quality_score:float=0
    composition_score:float=0
    final_score:float=0
    embedding_model_id:str|None=None
    embedding_model_revision:str|None=None
    embedding_vector_reference:str|None=None
    perceptual_hash:str|None=None
    content_hash:str|None=None
    selected:bool=False
    created_at:float=Field(default_factory=time.time)
class SearchRequest(BaseModel):
    queries:list[str]=Field(min_length=1,max_length=4)
    providers:list[Literal['openverse','artic','metmuseum','mock','pixabay','unsplash']]=['artic','metmuseum','openverse']
    page:int=Field(default=1,ge=1,le=10)
    per_page:int=Field(default=8,ge=1,le=20)
    commercial:bool=True
class LayoutItem(BaseModel):
    id:str
    asset_id:str|None=None
    kind:Literal['image','color','text']='image'
    x:float=Field(ge=0)
    y:float=Field(ge=0)
    width:float=Field(gt=0)
    height:float=Field(gt=0)
    rotation:float=Field(default=0,ge=-180,le=180)
    crop:dict=Field(default={'mode':'contain'})
    z_index:int=0
    opacity:float=Field(default=1,ge=0,le=1)
    attribution_reference:str=''
    locked:bool=False
    text:str=''
    fill:str='#BFC9D3'

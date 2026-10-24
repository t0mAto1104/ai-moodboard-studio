import {describe,it,expect} from 'vitest';
import {assetImage} from './api';
import type {Asset} from './types/models';
describe('board image source',()=>{
 it('uses local Pixabay copies for saved boards',()=>{
  const a={id:'pixabay:1',provider:'pixabay',allowed_export:true,allowed_temporary_analysis:false,display_url:''} as Asset;
  expect(assetImage(a)).toBe('/api/assets/pixabay%3A1/image');
 });
 it('keeps Unsplash official hotlinks',()=>{
  const a={id:'unsplash:1',provider:'unsplash',allowed_export:true,display_url:'https://images.unsplash.com/photo-test?ixid=keep'} as Asset;
  expect(assetImage(a)).toBe(a.display_url);
 });
});

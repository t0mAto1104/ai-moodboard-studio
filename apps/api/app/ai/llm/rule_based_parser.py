from app.schemas.models import SearchIntent
class RuleBasedIntentParser:
    def parse(self,prompt):
        p=prompt.lower()
        mappings={'style_keywords':{'简约':'minimalist','极简':'minimalist','未来':'futuristic','工业':'industrial','北欧':'scandinavian','复古':'vintage','自然':'organic','minimal':'minimalist'},'materials':{'金属':'brushed metal','银':'silver metal','玻璃':'frosted glass','木':'natural wood','陶':'ceramic','布':'linen','metal':'brushed metal','glass':'frosted glass'},'mood_keywords':{'高级':'premium','干净':'clean','安静':'quiet','温暖':'warm','冷':'cool'},'color_keywords':{'蓝':'slate blue','灰':'gray','银':'silver','绿':'green','米':'beige','红':'red','冷':'cool tones','暖':'warm tones'}}
        fields={k:list(dict.fromkeys(v for word,v in m.items() if word in p)) for k,m in mappings.items()}
        subject='industrial product design' if any(w in p for w in ('产品','工业','product')) else 'interior design' if any(w in p for w in ('室内','客厅','interior','room')) else 'visual design'
        if not any(fields.values()):subject=prompt[:180]
        palette=['#BFC9D3','#7B91A8','#DCE5EC']
        if any(w in p for w in ('温暖','木','米色','warm','wood')):palette=['#CBB99F','#E5DDCB','#86715D']
        if any(w in p for w in ('绿色','森林','green','forest')):palette=['#567367','#AAB79B','#DFE5D5']
        queries=[' '.join([*fields['style_keywords'][:1],subject]),*[f'{m} material texture' for m in fields['materials'][:2]]]
        if fields['color_keywords']:queries.append(' '.join(fields['color_keywords'][:2])+' design photography')
        return SearchIntent(raw_prompt=prompt,subject=subject,search_queries=list(dict.fromkeys(queries))[:4],target_palette=palette,**fields)

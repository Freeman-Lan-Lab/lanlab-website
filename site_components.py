"""Standalone replacements for components that otherwise need the Wix runtime."""
from bs4 import BeautifulSoup
import re

def gallery(s, host, items, mode='carousel', label='Photo gallery'):
    host.clear()
    host['class'] = [host.get('id',''), 'static-gallery', mode]
    host.attrs.pop('style',None)
    host['aria-label']=label
    host['data-gallery']=''
    seen=set()
    for item in items:
        url=item.get('src','')
        key=url.split('/v1/')[0]
        if not url or (key in seen and 'hero-gallery' not in mode): continue
        seen.add(key)
        fig=s.new_tag('figure')
        button=s.new_tag('button',type='button',attrs={'class':'enlarge','aria-label':'Enlarge '+(item.get('title') or 'photo')})
        button.append(s.new_tag('img',src=url,alt=item.get('title',''),loading='eager',decoding='async'))
        fig.append(button)
        if item.get('title') or item.get('description'):
            cap=s.new_tag('figcaption')
            for key in ['title','description']:
                if item.get(key):
                    line=s.new_tag('p');line.string=item[key];cap.append(line)
            fig.append(cap)
        host.append(fig)

def prepare(s,model,route):
    props=model.get('props',{}).get('render',{}).get('compProps',{})
    components=model.get('structure',{}).get('components',{})
    if route == '/team':
        profile=s.find(id='comp-m65a7vbx')
        target=s.find(id='comp-mj1qnihv')
        if profile and target:
            from copy import deepcopy
            grid=target.select_one('[data-mesh-id$="gridContainer"]')
            photo_src=profile.select_one('img')['src']
            for source_id,new_id,label in [
                ('comp-mtw8qlkd','tien-alumni-photo',None),
                ('comp-mtw8rkka','tien-alumni-name','Tien Nguyen'),
                ('comp-mtw8s8z7','tien-alumni-role','Engineer at Sanofi'),
            ]:
                node=deepcopy(s.find(id=source_id))
                node['id']=new_id
                if label is None:
                    img=node.find('img');img['src']=photo_src;img['alt']='Tien Nguyen'
                    img.attrs.pop('srcset',None);img.attrs.pop('id',None)
                else:
                    paragraph=deepcopy(node.find('p'));paragraph.clear();paragraph.string=label
                    node.clear();node.append(paragraph)
                grid.append(node)
            s.find(id='comp-m65a7vb1').decompose()
    for text in list(s.find_all(string=True)):
        updated=str(text).replace('Microbiomes (such as the human gut microbiome) contains','Microbiomes (such as the human gut microbiome) contain').replace('Grad students','Graduate Students')
        if updated != str(text): text.replace_with(updated)
    if route=='/':
        news=s.find(id='comp-mho3qn5e')
        if news:
            news_items=[
                'Henrique joins us as a 4th year thesis student!',
                'Ryu Kawajiri and Kenny Man join us as new graduate students!',
                'We received a visit from clinical microbiologists of Institut Kesihatan Negara of Malaysia interested in adopting our microfluidics technologies!',
                'Jann receives Ontario Graduate Scholarship! Congratulations!',
                'We hosted a visit by MP Kardim Bardeesy, the Parliamentary Secretary of Industry and Technology of Canada.',
                'We are awarded an exploration grant from the New Frontiers in Research Fund to develop a new clinical diagnostic!',
                'Tereza secures a PhD position at UNC Chapel Hill! Congratulations!',
                'We are awarded a Discovery grant from Natural Science and Engineering Research Council to develop new single-cell sequencing technologies!',
                'Welcome summer students Julianna, Mark, Ethan, Candice!',
                'We are awarded a grant from the New Frontiers in Research Fund',
            ]
            news_list=news.find('ul')
            template=news_list.find('li') if news_list else None
            if template:
                template=str(template)
                news_list.clear()
                for item in news_items:
                    entry=BeautifulSoup(template,'html.parser').find('li')
                    text=entry.find('p').find('span')
                    text.clear()
                    text.string=item
                    news_list.append(entry)
            for year in ('2026','2025','2024'):
                heading=next((p for p in news.find_all('p',recursive=False) if p.get_text(strip=True)==year),None)
                if heading:
                    heading['class']=heading.get('class',[])+['news-year']
                    heading['data-year']=year
                    following=heading.find_next_sibling('ul')
                    if following:
                        following['class']=following.get('class',[])+['news-year-list']
                        following['data-year']=year
    if route=='/join-us':
        for item in s.select('[id^="comp-lo6me7m71__item"]'):
            mail=item.select_one('a[href^="mailto:"]')
            grid=item.select_one('[data-mesh-id$="gridContainer"]')
            if mail and grid:
                action=s.new_tag('a',href=mail.get('href'),attrs={'class':'email-lab'})
                action.string='Email the lab'
                grid.append(action)
    for cid,prop in props.items():
        if not isinstance(prop,dict): continue
        host=s.find(id=cid)
        if host and components.get(cid,{}).get('componentType')=='VideoPlayer' and prop.get('src'):
            host.clear()
            video=s.new_tag('video',attrs={
                'class':'standalone-video',
                'src':prop['src'],
                'controls':'',
                'playsinline':'',
                'preload':'metadata',
            })
            description=prop.get('playableConfig',{}).get('description','').strip()
            video['aria-label']=description or prop.get('title') or 'Lab research video'
            poster=prop.get('playableConfig',{}).get('poster',{}).get('uri')
            if poster:
                video['poster']='https://static.wixstatic.com/media/'+poster
            if prop.get('autoplay'):
                video['autoplay']=''
            if prop.get('muted'):
                video['muted']=''
            if prop.get('loop'):
                video['loop']=''
            host.append(video)
        items=prop.get('items',[])
        photos=[{'src':'https://static.wixstatic.com/media/'+v['image']['uri'],'title':v.get('title',''),'description':v.get('description','')} for v in items if isinstance(v,dict) and v.get('image',{}).get('uri')]
        if host and photos: gallery(s,host,photos,'events-grid' if route=='/events' else 'carousel')
        slides=prop.get('slidesProps',[])
        if host and slides:
            photos=[]
            for slide in slides:
                img=props.get(slide['id'],{}).get('fillLayers',{}).get('image',{})
                if img.get('uri'): photos.append({'src':'https://static.wixstatic.com/media/'+img['uri'],'title':slide.get('title','')})
            if photos:
                gallery(s,host,photos,'carousel hero-gallery','Lab slideshow')
                host['data-autoplay']='true'
    for host in s.select('[id^="pro-gallery-container-"]'):
        height=re.search(r'(?:^|;)height:([^;]+)',host.get('style',''))
        photos=[{'src':img.get('src',''),'title':img.get('alt','')} for img in host.select('img')]
        if route == '/join-us':
            mode = 'photo-strip'
        elif route == '/team' and host.get('id') == 'pro-gallery-container-comp-mhxwlqzi':
            mode = 'team-join-collage'
        else:
            mode = 'carousel'
        gallery(s,host,photos,mode)
        if height:
            host['style']='height:'+height[1]
            host.parent['style']='width:100%;height:'+height[1]+';margin:0'
    for cid,comp in components.items():
        if comp.get('componentType')!='GoogleMap': continue
        host=s.find(id=cid)
        if host:
            host.clear();host['class']=[cid,'location-map']
            frame=s.new_tag('iframe',src='https://maps.google.com/maps?q=170%20College%20Street%2C%20Toronto&output=embed',title='Lan Lab — 170 College Street, Toronto',loading='lazy',referrerpolicy='no-referrer-when-downgrade')
            host.append(frame)
            a=s.new_tag('a',href='https://www.google.com/maps/search/?api=1&query=170+College+Street+Toronto',target='_blank',rel='noopener');a.string='View 170 College Street on Google Maps';host.append(a)

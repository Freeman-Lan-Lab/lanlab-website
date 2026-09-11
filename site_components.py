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
        button.append(s.new_tag('img',src=url,alt=item.get('title',''),loading='lazy'))
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
    if route=='/':
        news=s.find(id='comp-mho3qn5e')
        if news:
            for text in news.find_all(string=lambda value: value and 'Ryu joins our lab as a new graduate student!' in value):
                text.replace_with('Ryu Kawajiri and Kenny Man join us as new graduate students!')
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
        gallery(s,host,photos,'photo-strip' if route=='/join-us' else 'carousel')
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

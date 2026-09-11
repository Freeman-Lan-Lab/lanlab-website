"""Create a standalone snapshot of the public Lan Lab Wix site."""
import sys
sys.path.insert(0, '.tools')
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlsplit, unquote
import hashlib, json, re, concurrent.futures

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
ARCHIVE = ROOT / 'source'
OUT.mkdir(exist_ok=True)
ARCHIVE.mkdir(exist_ok=True)
(OUT/'assets').mkdir(exist_ok=True)
BASE = 'https://www.lanlab.ca'
pages, assets, failures = {}, {}, []

def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=50) as r:
                return r.read(), r.headers.get_content_type()
        except Exception:
            if attempt == 2: raise

def internal(url):
    p = urlsplit(urljoin(BASE, url))
    return p.hostname in ('lanlab.ca', 'www.lanlab.ca') and not p.path.startswith('/_files') and not Path(p.path).suffix

queue = ['/']
while queue:
    route = queue.pop(0)
    if route in pages: continue
    cached = ARCHIVE/((route.strip('/') or 'index')+'.html')
    raw = cached.read_bytes() if cached.exists() else ((ROOT/'source-home.html').read_bytes() if route == '/' else fetch(BASE+route)[0])
    soup = BeautifulSoup(raw, 'html.parser')
    pages[route] = soup
    (ARCHIVE/((route.strip('/') or 'index')+'.html')).write_bytes(raw)
    for a in soup.select('a[href]'):
        href = a['href']
        if internal(href):
            path = urlsplit(urljoin(BASE, href)).path.rstrip('/') or '/'
            if path not in pages and path not in queue: queue.append(path)
    print('Captured', route, flush=True)

def register(url, original=False):
    url = url.replace('&amp;', '&')
    if url.startswith('//'): url = 'https:'+url
    if not url.startswith('https://'): return url
    if original and 'static.wixstatic.com/media/' in url:
        url = url.split('/v1/')[0]
    if url not in assets:
        ext = Path(unquote(urlsplit(url).path)).suffix.lower()
        if ext not in ('.jpg','.jpeg','.png','.gif','.svg','.webp','.avif','.mp4','.pdf','.woff','.woff2','.ttf','.css','.ico'): ext = '.bin'
        assets[url] = 'assets/'+hashlib.sha256(url.encode()).hexdigest()[:20]+ext
    return assets[url]

def css_urls(text):
    text = re.sub(r'url\([\'"]?media/emptystate[^)]+\)', 'none', text)
    return re.sub(r'url\([\'"]?((?:https:)?//[^)\s\'"]+)[\'"]?\)', lambda m:'url("'+register(m[1])+'")', text)

nav_items = [('Home','/'),('Microfluidics','/microfluidics'),('Microbiome','/microbiome'),('Publications','/publications'),('The PI','/the-pi'),('Team','/team'),('Events','/events'),('Contact','/join-us')]
def local_link(href, prefix):
    full = urljoin(BASE, href)
    p = urlsplit(full)
    if internal(full):
        route = p.path.rstrip('/') or '/'
        return prefix + ('' if route=='/' else route.strip('/')+'/') + ('#'+p.fragment if p.fragment else '')
    if '/_files/' in full: return prefix+register(full)
    return href

for route,s in pages.items():
    prefix = './' if route=='/' else '../'
    data_path = ARCHIVE/((route.strip('/') or 'index')+'-data.json')
    links = [x for x in s.select('link[rel=prefetch]') if x.get('id','').startswith('features_')]
    if not data_path.exists() and links:
        data_path.write_bytes(fetch(links[-1]['href'].replace('\u00aeistry','&registry'))[0])
    model = json.loads(data_path.read_bytes()) if data_path.exists() else {}
    props = model.get('props',{}).get('render',{}).get('compProps',{})
    from site_components import prepare
    prepare(s, model, route)
    for el in s.select('script, noscript, base'): el.decompose()
    for link in list(s.select('link')):
        rel = link.get('rel',[])
        if 'stylesheet' in rel:
            link['href'] = prefix+register(link['href'])
        elif 'icon' in rel or 'apple-touch-icon' in rel:
            link['href'] = prefix+register(link['href'])
        else: link.decompose()
    for el in s.find_all(True):
        for attr in list(el.attrs):
            if attr.startswith('on'): del el[attr]
        if el.get('style'): el['style'] = css_urls(el['style']).replace('url("assets/', 'url("'+prefix+'assets/')
    for style in s.select('style'):
        style.string = css_urls(style.get_text()).replace('url("assets/', 'url("'+prefix+'assets/')
    for img in s.select('img[src]'):
        preserve_crop = img.get('id') in {
            'img_comp-mhql58lk',  # PI portrait
            'img_comp-mhppm2cn',  # Home microbiome circle
            'img_comp-mi0mbq72',  # Home microfluidics circle
        }
        img['src'] = prefix+register(img['src'], original=not preserve_crop)
        img.attrs.pop('srcset', None)
        img['loading'] = 'lazy'
        img['decoding'] = 'async'
    for container in s.select('[data-video-info]'):
        info = json.loads(container['data-video-info'])
        qualities = info.get('qualities',[])
        video = container.select_one('video')
        if video and qualities:
            video['src'] = prefix+register(urljoin('https://video.wixstatic.com/',qualities[-1]['url']))
            video['autoplay'] = ''
            video['controls'] = ''
            video['style'] = 'width:100%;height:100%;object-fit:contain;opacity:1'
            poster = container.select_one('img')
            if poster:
                video['poster'] = poster['src']
                poster.decompose()
    for a in s.select('a[href]'):
        a['href'] = local_link(a['href'],prefix)
        if a.get('target') == '_blank': a['rel'] = 'noopener noreferrer'
    # Keep the original desktop artwork and layout. Supply a semantic mobile reading view.
    main = s.select_one('main')
    mobile = s.new_tag('main', attrs={'class':'mobile-content', 'id':'mobile-content', 'tabindex':'-1'})
    if main:
        main['class'] = main.get('class',[])+['desktop-content']
        seen = set()
        for section in main.select('section') or [main]:
            block = s.new_tag('section', attrs={'class':'mobile-section'})
            for el in section.select('.wixui-rich-text, .static-gallery, .location-map, img, video, a[href]'):
                if el.find_parent(class_='wixui-rich-text'): continue
                if el.find_parent(class_='static-gallery') or el.find_parent(class_='location-map'): continue
                if el.name=='a' and (el.select_one('img') or el.select_one('.wixui-rich-text')): continue
                if 'static-gallery' in el.get('class',[]) or 'location-map' in el.get('class',[]):
                    component_key = 'component:' + el.get('id','')
                    if component_key in seen: continue
                    seen.add(component_key)
                    fresh = BeautifulSoup(str(el),'html.parser').find()
                    fresh.attrs = {k:v for k,v in el.attrs.items() if k in ('class','data-gallery','data-autoplay','aria-label')}
                    for child in fresh.select('[id]'): del child['id']
                    block.append(fresh)
                elif el.name=='video':
                    fresh = BeautifulSoup(str(el),'html.parser').find()
                    fresh.attrs.pop('id',None)
                    fresh.attrs.pop('class',None)
                    block.append(fresh)
                elif el.name=='img':
                    key = el.get('src')
                    if key in seen: continue
                    seen.add(key)
                    fresh = s.new_tag('img', src=key, alt=el.get('alt',''), loading='lazy')
                    block.append(fresh)
                else:
                    key = el.get_text(' ',strip=True).replace('\u200b','').strip()
                    if not key or key in seen: continue
                    seen.add(key)
                    clone = BeautifulSoup(str(el),'html.parser').find()
                    for child in [clone]+list(clone.find_all(True)):
                        child.attrs = {k:v for k,v in child.attrs.items() if k in ('href','target','rel')}
                    block.append(clone)
            if block.contents: mobile.append(block)
        main.insert_after(mobile)
    header = s.select_one('header')
    if header:
        original_logo = header.select_one('img')
        logo_src = original_logo.get('src') if original_logo else None
        header.clear()
        header['class'] = ['static-header']
        logo = s.new_tag('a', href=prefix, attrs={'class':'lab-brand'})
        if logo_src:
            logo.append(s.new_tag('img',src=logo_src,alt='Lan Lab'))
        else: logo.string = 'LAN LAB'
        header.append(logo)
        nav = s.new_tag('nav',attrs={'aria-label':'Main navigation'})
        for label,path in nav_items:
            if path not in pages or path=='/microbiome': continue
            if path=='/microfluidics':
                group=s.new_tag('details',attrs={'class':'research-menu'})
                summary=s.new_tag('summary');summary.string='Research';group.append(summary)
                links=s.new_tag('div',attrs={'class':'research-links'})
                for title,url in [('Microfluidics','/microfluidics'),('Microbiome','/microbiome')]:
                    a=s.new_tag('a',href=local_link(BASE+url,prefix));a.string=title;links.append(a)
                group.append(links);nav.append(group)
                continue
            a = s.new_tag('a',href=local_link(BASE+path,prefix))
            a.string = label
            if path==route: a['aria-current']='page'
            nav.append(a)
        header.append(nav)
    for control in s.select('[data-testid=prevButton], [data-testid=nextButton]'):
        # Wix only includes one slide in server HTML; avoid nonworking slideshow controls.
        control.decompose()
    s.html['lang']='en'
    skip=s.new_tag('a',href='#PAGES_CONTAINER',attrs={'class':'skip-link'});skip.string='Skip to main content';s.body.insert(0,skip)
    style = s.new_tag('link',rel='stylesheet',href=prefix+'migration.css?v=9')
    s.head.append(style)
    script=s.new_tag('script',src=prefix+'site.js?v=9',defer='');s.head.append(script)
    dest = OUT / route.strip('/')
    dest.mkdir(exist_ok=True,parents=True)
    (dest/'index.html').write_text(str(s),encoding='utf-8')

done = set()
while set(assets)-done:
    batch = list(set(assets)-done)
    def download(url):
        path = OUT/assets[url]
        if path.exists(): return url,None,None
        try:
            data,ctype = fetch(url)
            return url,data,ctype
        except Exception as e: return url,None,str(e)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for url,data,ctype in pool.map(download,batch):
            done.add(url)
            if data is None:
                if ctype: failures.append({'url':url,'error':ctype})
                continue
            if ctype=='text/css' or assets[url].endswith('.css'):
                text = css_urls(data.decode()).replace('url("assets/','url("')
                data = text.encode()
            (OUT/assets[url]).write_bytes(data)
    print('Downloaded',len(done),'assets',flush=True)
try:
    from PIL import Image, ImageOps
    for path in (OUT/'assets').iterdir():
        if path.suffix.lower() not in ('.jpg','.jpeg','.png'): continue
        with Image.open(path) as original:
            if getattr(original,'is_animated',False) or max(original.size)<=1920: continue
            image = ImageOps.exif_transpose(original)
            image.thumbnail((1920,1920))
            if path.suffix.lower() in ('.jpg','.jpeg'):
                image.convert('RGB').save(path,quality=88,optimize=True)
            else: image.save(path,optimize=True)
except ImportError:
    print('Pillow unavailable; keeping original-size photos.')
(ROOT/'migration-report.json').write_text(json.dumps({'pages':list(pages),'assets':assets,'failures':failures},indent=2),encoding='utf-8')
print('Complete:',len(pages),'pages;',len(assets),'assets;',len(failures),'failures')

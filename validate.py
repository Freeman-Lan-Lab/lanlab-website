"""Validate the static site without loading Wix or running a browser."""
import sys
sys.path.insert(0, '.tools')
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlsplit,unquote
import re

root = Path(__file__).resolve().parent/'dist'
errors=[]
def check(value,path,allow_remote=False):
    value=value.strip('\"\' ')
    if value.startswith(('data:','#')): return
    parsed=urlsplit(value)
    if parsed.scheme or value.startswith('//'):
        if not allow_remote: errors.append(f'{path.name}: external resource {value}')
        return
    if not parsed.path: return
    target=(path.parent/unquote(parsed.path)).resolve()
    if not target.exists(): errors.append(f'{path.relative_to(root)}: missing {value}')
    elif target.is_dir() and not (target/'index.html').exists(): errors.append(f'Missing page entrypoint: {value}')

pages=list(root.rglob('*.html'))
for path in pages:
    soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    if soup.select('form'): errors.append(f'{path}: unexpected form')
    for script in soup.select('script'):
        if not script.get('src','').split('?')[0].endswith('/site.js'): errors.append(f'{path}: unexpected script')
    for frame in soup.select('iframe'):
        if not frame.get('src','').startswith('https://maps.google.com/maps?'): errors.append(f'{path}: unexpected embed')
    for el in soup.select('[src],link[href],a[href]'):
        check(el.get('src') or el.get('href',''),path,el.name in ('a','iframe'))
    for style in soup.select('style'):
        for value in re.findall(r'url\(([^)]+)\)',style.get_text()): check(value,path)
    for el in soup.select('[style]'):
        for value in re.findall(r'url\(([^)]+)\)',el['style']): check(value,path)
for path in root.rglob('*.css'):
    for value in re.findall(r'url\(([^)]+)\)',path.read_text()): check(value,path)
for path in root.rglob('*'):
    if path.is_file() and path.stat().st_size>=100*1024*1024: errors.append(f'File too large for GitHub: {path}')
print(f'Checked {len(pages)} pages; {sum(p.stat().st_size for p in root.rglob("*") if p.is_file())/1e6:.1f} MB total.')
print('\n'.join(errors) if errors else 'PASS: local links and assets exist; only the approved map embed and local script; no oversized files.')
sys.exit(bool(errors))

// Accessible standalone navigation and galleries. No Wix runtime required.
const menuToggle = document.querySelector('.mobile-menu-toggle');
const siteNav = document.querySelector('#site-navigation');
if (menuToggle && siteNav) {
  menuToggle.addEventListener('click', () => {
    const open = menuToggle.getAttribute('aria-expanded') === 'true';
    menuToggle.setAttribute('aria-expanded', String(!open));
    menuToggle.setAttribute('aria-label', open ? 'Open navigation menu' : 'Close navigation menu');
    siteNav.toggleAttribute('data-open', !open);
  });
}
document.querySelectorAll('[data-gallery]').forEach(gallery => {
  const figures = [...gallery.querySelectorAll(':scope > figure')];
  if (!figures.length) return;
  let current = 0;
  if (gallery.classList.contains('team-join-collage')) {
    return;
  } else if (gallery.classList.contains('photo-strip')) {
    const track=document.createElement('div');track.className='photo-track';track.tabIndex=0;
    track.setAttribute('aria-label','Lab photographs; scroll horizontally for more');
    figures.forEach(f=>track.append(f));gallery.append(track);
    const prev=document.createElement('button'),next=document.createElement('button');
    prev.type=next.type='button';prev.className='strip-prev';next.className='strip-next';
    prev.textContent='‹';next.textContent='›';prev.setAttribute('aria-label','Previous photo');next.setAttribute('aria-label','Next photo');
    prev.addEventListener('click',()=>track.scrollBy({left:-figures[0].getBoundingClientRect().width,behavior:'smooth'}));
    next.addEventListener('click',()=>track.scrollBy({left:figures[0].getBoundingClientRect().width,behavior:'smooth'}));
    gallery.append(prev,next);
  } else if (gallery.classList.contains('events-grid')) {
    let shown = 9;
    const more = document.createElement('button');
    more.type = 'button'; more.className = 'show-more'; more.textContent = 'Show More';
    const render = () => { figures.forEach((f,i) => f.hidden = i >= shown); more.hidden = shown >= figures.length; };
    more.addEventListener('click', () => { shown += 6; render(); });
    gallery.append(more); render();
  } else {
    const controls = document.createElement('div'); controls.className = 'gallery-controls';
    const prev = document.createElement('button'), next = document.createElement('button'), counter = document.createElement('span');
    prev.type = next.type = 'button'; prev.textContent = '‹'; next.textContent = '›';
    prev.setAttribute('aria-label','Previous photo'); next.setAttribute('aria-label','Next photo');
    counter.setAttribute('aria-live','polite');
    const render = () => { figures.forEach((f,i) => f.hidden = i !== current); counter.textContent = `${current + 1} / ${figures.length}`; };
    let timer;
    const stop = () => { clearInterval(timer); if (pause) { pause.textContent='▶'; pause.setAttribute('aria-label','Play slideshow'); } };
    const step = n => { current=(current+n+figures.length)%figures.length; render(); };
    prev.addEventListener('click',()=>{stop();step(-1)}); next.addEventListener('click',()=>{stop();step(1)});
    controls.append(prev,counter,next);gallery.append(controls);
    let pause;
    if(gallery.dataset.autoplay && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      pause=document.createElement('button');pause.type='button';pause.className='slideshow-toggle';pause.textContent='⏸';pause.setAttribute('aria-label','Pause slideshow');
      const start=()=>{timer=setInterval(()=>{if(!document.hidden && gallery.getClientRects().length)step(1)},4000);pause.textContent='⏸';pause.setAttribute('aria-label','Pause slideshow')};
      pause.addEventListener('click',()=>pause.getAttribute('aria-label').startsWith('Pause')?stop():start());controls.append(pause);start();
      gallery.addEventListener('focusin',stop);gallery.addEventListener('pointerenter',stop);
    }
    render();
  }
});
const dialog = document.createElement('dialog'); dialog.className='photo-dialog';
const close = document.createElement('button');close.type='button';close.textContent='Close';
const image=document.createElement('img');image.alt='';
dialog.append(close,image);document.body.append(dialog);
close.addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
document.querySelectorAll('.enlarge').forEach(button=>button.addEventListener('click',()=>{
 const img=button.querySelector('img');image.src=img.src;image.alt=img.alt;dialog.showModal();
}));
document.querySelectorAll('.skip-link').forEach(link=>link.addEventListener('click',e=>{
 e.preventDefault();const main=document.querySelector('.responsive-content');
 if(main){main.tabIndex=-1;main.focus();main.scrollIntoView();}
}));

// Keep older news available without making the phone homepage excessively long.
const mobileLayout = matchMedia('(max-width: 980px)');
function syncMobileDisclosure() {
  document.querySelectorAll('.news-toggle,.alumni-toggle').forEach(button=>button.remove());
  document.querySelectorAll('.news-year-list,.alumni-detail').forEach(part=>part.hidden=false);
  if (!mobileLayout.matches) return;
  document.querySelectorAll('#comp-mho3qn5e .news-year[data-year="2025"],#comp-mho3qn5e .news-year[data-year="2024"]').forEach(heading => {
    const list=document.querySelector(`#comp-mho3qn5e .news-year-list[data-year="${heading.dataset.year}"]`);
    if(!list) return;
    const button=document.createElement('button');button.type='button';button.className='news-toggle';button.textContent=`Show ${heading.dataset.year} news`;button.setAttribute('aria-expanded','false');
    list.hidden=true;heading.insertAdjacentElement('afterend',button);
    button.addEventListener('click',()=>{const open=button.getAttribute('aria-expanded')==='true';button.setAttribute('aria-expanded',String(!open));button.textContent=`${open?'Show':'Hide'} ${heading.dataset.year} news`;list.hidden=open;});
  });
  const alumniParts=['comp-mj1qnih9','comp-mj1qnihb','comp-mj1qniin','comp-mj1qniik1','comp-mj1qnijj','comp-mtw9m99r','comp-mphcly2u'].map(id=>document.getElementById(id)).filter(Boolean);
  const alumniHeading=document.getElementById('comp-mj1qnih6');
  if(alumniParts.length && alumniHeading){
    alumniParts.forEach(part=>{part.classList.add('alumni-detail');part.hidden=true});
    const button=document.createElement('button');button.type='button';button.className='alumni-toggle';button.textContent='Show alumni';button.setAttribute('aria-expanded','false');
    alumniHeading.insertAdjacentElement('afterend',button);
    button.addEventListener('click',()=>{const open=button.getAttribute('aria-expanded')==='true';button.setAttribute('aria-expanded',String(!open));button.textContent=open?'Show alumni':'Hide alumni';alumniParts.forEach(part=>part.hidden=open);});
  }
}

syncMobileDisclosure();
mobileLayout.addEventListener('change', syncMobileDisclosure);

// Reuse the original identity paragraph and restore its place on desktop.
const piBiography = document.getElementById('comp-mhql58m2');
if (piBiography) {
 const identity = piBiography.querySelector(':scope > p');
 const marker = document.createComment('PI identity original position');
 identity.before(marker);
 const slot = document.createElement('div'); slot.className='pi-mobile-identity';
 const sync = () => {
  if (mobileLayout.matches) { piBiography.parentElement.append(slot); slot.append(identity); }
  else { marker.after(identity); slot.remove(); }
 };
 sync(); mobileLayout.addEventListener('change',sync);
}
const profileIds=['comp-m3emvxd01','comp-luioupgi','comp-lxhwwdqr','comp-m65a7vbx','comp-mn8xq2fn','comp-mmus012g','comp-m659yg6s3','comp-mhvhiy0o'];
profileIds.forEach(id=>{
 const paragraph=document.querySelector('#'+id+' .wixui-rich-text p');
 if(!paragraph)return;
 const walker=document.createTreeWalker(paragraph,NodeFilter.SHOW_TEXT);
 while(walker.nextNode()){
  const node=walker.currentNode;
  if(node.textContent.trim()) { const label=document.createElement('span');label.className='profile-name';node.replaceWith(label);label.append(node);break; }
 }
});

document.querySelectorAll('#comp-loz3zzza1 > p').forEach(p=>{if(/^\d{4}$/.test(p.textContent.trim()))p.classList.add('publication-year');});

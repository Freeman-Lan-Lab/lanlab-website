// Accessible standalone navigation and galleries. No Wix runtime required.
document.querySelectorAll('[data-gallery]').forEach(gallery => {
  const figures = [...gallery.querySelectorAll(':scope > figure')];
  if (!figures.length) return;
  let current = 0;
  if (gallery.classList.contains('photo-strip')) {
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
    const stop = () => { clearInterval(timer); if (pause) pause.textContent='Play slideshow'; };
    const step = n => { current=(current+n+figures.length)%figures.length; render(); };
    prev.addEventListener('click',()=>{stop();step(-1)}); next.addEventListener('click',()=>{stop();step(1)});
    controls.append(prev,counter,next);gallery.append(controls);
    let pause;
    if(gallery.dataset.autoplay && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      pause=document.createElement('button');pause.type='button';pause.textContent='Pause slideshow';
      const start=()=>{timer=setInterval(()=>{if(!document.hidden && gallery.getClientRects().length)step(1)},4000);pause.textContent='Pause slideshow'};
      pause.addEventListener('click',()=>pause.textContent.startsWith('Pause')?stop():start());controls.append(pause);start();
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
 e.preventDefault();const main=matchMedia('(max-width: 980px)').matches?document.querySelector('.mobile-content'):document.querySelector('.desktop-content');
 main.focus();main.scrollIntoView();
}));

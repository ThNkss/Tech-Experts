/* Decorative, pointer-responsive 3D contours. No library, tracking or live data. */
(() => {
  'use strict';
  const canvas = document.getElementById('ambient-canvas');
  const context = canvas?.getContext('2d', { alpha:true });
  if (!context) return;
  document.body.classList.add('ambient-ready');
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover:hover) and (pointer:fine)');
  const home = document.body.classList.contains('page-home');
  const company = document.body.classList.contains('page-company');
  const detail = /^\/(?:products|projects)\/[^/]+\/?$/.test(location.pathname);
  const pathSeed = Array.from(location.pathname).reduce((sum,char) => sum + char.charCodeAt(0), 0) % 7;
  const pointer = { x:0,y:0,active:false };
  let width=1, height=1, small=false, rings=[], slices=[], blue='', teal='', alpha=.3;
  let time=0, last=0, frame=0, disposed=false, headerHeight=130;
  const colors = () => {
    const style = getComputedStyle(root);
    blue = style.getPropertyValue('--field-blue').trim();
    teal = style.getPropertyValue('--field-teal').trim();
    alpha = parseFloat(style.getPropertyValue('--field-alpha')) || .3;
  };
  const resize = () => {
    width = canvas.clientWidth; height = canvas.clientHeight;
    small = width < 701;
    headerHeight = document.querySelector('.header')?.getBoundingClientRect().height || 130;
    // Match Retina phone density; control animation cost with frame rate, not a soft bitmap.
    const ratio = Math.min(devicePixelRatio || 1, small ? 3 : 2);
    canvas.width = Math.round(width*ratio); canvas.height = Math.round(height*ratio);
    context.setTransform(ratio,0,0,ratio,0,0);
    const ringCount = small ? 48 : 58;
    const sliceCount = 112;
    rings = Array.from({length:ringCount},(_,i) => {
      const phi = ((i+.5)/ringCount)*Math.PI;
      return { phi, sin:Math.sin(phi), cos:Math.cos(phi), progress:i/ringCount };
    });
    slices = Array.from({length:sliceCount+1},(_,i) => {
      const theta=i/sliceCount*Math.PI*2;
      return {theta,sin:Math.sin(theta),cos:Math.cos(theta)};
    });
    colors();
    if (reduce.matches || document.hidden) draw();
  };
  const core = (cx,cy,radius,phase,strength) => {
    strength *= detail ? .42 : 1;
    const dark=root.dataset.theme==='dark';
    const aura=context.createRadialGradient(cx,cy,radius*.35,cx,cy,radius*1.45);
    aura.addColorStop(0,`rgba(${teal},${strength*(dark ? .045 : .025)})`);
    aura.addColorStop(.65,`rgba(${blue},${strength*(dark ? .035 : .018)})`);
    aura.addColorStop(1,`rgba(${teal},0)`);
    context.fillStyle=aura;
    context.fillRect(cx-radius*1.45,cy-radius*1.45,radius*2.9,radius*2.9);
    const rotateY=time*.11+phase;
    const rotateX=.5+Math.sin(time*.12+phase)*.18;
    const sy=Math.sin(rotateY),cyy=Math.cos(rotateY),sx=Math.sin(rotateX),cxx=Math.cos(rotateX);
    for (const ring of rings) {
      context.beginPath();
      let depth=0;
      // Latitude-dependent twist and depth ripples produce woven, lobed contours.
      const twist=.28*Math.sin(ring.phi*3+time*.24+phase);
      const st=Math.sin(twist),ct=Math.cos(twist);
      slices.forEach((slice,index) => {
        const wave = 1 + .12*Math.sin(slice.theta*3 + time*.52 + ring.phi*4 + phase)
          + .065*Math.cos(slice.theta*5 - time*.32 + ring.phi*3);
        const radial = radius*ring.sin*wave;
        const x=radial*(slice.cos*ct-slice.sin*st);
        const y=radial*(slice.sin*ct+slice.cos*st);
        const z=radius*(ring.cos+.14*ring.sin*Math.sin(slice.theta*4+ring.phi*2-time*.38));
        const rx=x*cyy+z*sy, rz=-x*sy+z*cyy;
        const ry=y*cxx-rz*sx, zz=y*sx+rz*cxx;
        const perspective=650/(650+zz);
        let px=cx+rx*perspective, py=cy+ry*perspective;
        if (pointer.active && !reduce.matches && fine.matches) {
          const dx=px-pointer.x,dy=py-pointer.y,dist=Math.hypot(dx,dy);
          if (dist>0.01 && dist<180) {
            const push=Math.pow(1-dist/180,2)*22;
            px+=dx/dist*push; py+=dy/dist*push;
          }
        }
        depth+=zz;
        if (index===0) context.moveTo(px,py); else context.lineTo(px,py);
      });
      const depthAlpha=.4+.6*(1-(depth/slices.length/radius+1)/2);
      const color=ring.progress>.48 ? teal : blue;
      const intensity=Math.min(1,alpha*strength*depthAlpha);
      // Layered light falloff gives the contours a bloom without costly per-ring blur.
      context.strokeStyle=`rgba(${color},${intensity*(dark ? .08 : .04)})`;
      context.lineWidth=small ? 7 : 10;
      context.stroke();
      context.strokeStyle=`rgba(${color},${intensity*(dark ? .24 : .12)})`;
      context.lineWidth=small ? 3.4 : 4.5;
      context.stroke();
      context.strokeStyle=`rgba(${color},${intensity})`;
      context.lineWidth=small ? 1.15 : dark ? 1.55 : 1.15;
      context.stroke();
      if (dark && Math.round(ring.progress*rings.length)%4===0) {
        context.strokeStyle=`rgba(177,255,252,${intensity*.3})`;
        context.lineWidth=.65;
        context.stroke();
      }
    }
  };
  function draw() {
    context.clearRect(0,0,width,height);
    const rtl=root.dir==='rtl';
    const visualX=rtl ? .215 : .785;
    const dark=root.dataset.theme==='dark';
    const shortScreenLimit=height<540 ? Math.max(48,(height-headerHeight-40)/2.8) : 204;
    const radius=small ? Math.min(width*.29,124) : Math.min(width*.15,204,shortScreenLimit);
    context.globalCompositeOperation=dark ? 'lighter' : 'source-over';
    if (small) {
      // A single viewport-anchored form: scrolling never moves it off the phone screen.
      const cy=height*.44;
      const strength=home ? (dark ? 1.05 : 1.85) : (dark ? .38 : .78);
      core(width*.5,cy,radius,time*.025+pathSeed*.2,strength);
    } else {
      const cx=width*visualX;
      const preferredY=home ? 310 : company ? 325 : 285+pathSeed*18;
      const cy=height<540 ? Math.max(headerHeight+radius*1.1,
        Math.min(preferredY,height-radius*1.1-20)) : preferredY;
      core(cx,cy,radius,time*.025+pathSeed*.2,home ? 1 : company ? .78 : .38);
      const inset=38;
      core(width*(rtl ? .93 : .07)+(rtl ? -inset : inset),
        height*.89-inset,radius*.66,2.2+pathSeed,dark ? .55 : 1.15);
    }
    context.globalCompositeOperation='source-over';
  }
  const loop = stamp => {
    frame=0;
    if (disposed || document.hidden || reduce.matches) return;
    const elapsed=stamp-last;
    if (elapsed >= (small ? 42 : 32)) {
      time += Math.min(elapsed,80)/1000;
      last=stamp; draw();
    }
    frame=requestAnimationFrame(loop);
  };
  const sync = () => {
    cancelAnimationFrame(frame); frame=0; last=performance.now();
    if (!document.hidden && !reduce.matches && !disposed) frame=requestAnimationFrame(loop);
    else draw();
  };
  let resizeFrame=0;
  window.addEventListener('resize',() => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame=requestAnimationFrame(resize);
  },{passive:true});
  window.addEventListener('pointermove',event => {
    if (!fine.matches || event.pointerType==='touch' || reduce.matches) return;
    pointer.x=event.clientX; pointer.y=event.clientY; pointer.active=true;
  },{passive:true});
  document.documentElement.addEventListener('pointerleave',() => {pointer.active=false;});
  window.addEventListener('blur',() => {pointer.active=false;});
  document.addEventListener('visibilitychange',sync);
  reduce.addEventListener?.('change',sync);
  new MutationObserver(() => { colors(); if (reduce.matches) draw(); })
    .observe(root,{attributes:true,attributeFilter:['data-theme']});
  window.addEventListener('pagehide',() => { disposed=true; cancelAnimationFrame(frame); cancelAnimationFrame(resizeFrame); });
  window.addEventListener('pageshow',() => { disposed=false; sync(); });
  resize(); draw(); sync();
})();

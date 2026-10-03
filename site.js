(() => {
  const root=document.getElementById('pion-soft-on-page');
  const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
  const clamp=x=>Math.max(0,Math.min(1,x));
  const ease=x=>{const t=clamp(x);return t*t*t*(t*(t*6-15)+10);};
  const step=(t,a,b)=>ease((t-a)/(b-a));
  const lerp=(a,b,t)=>a+(b-a)*t;
  const mix=(a,b,t)=>[lerp(a[0],b[0],t),lerp(a[1],b[1],t)];
  const f=n=>Math.round(n*100)/100;
  const slots=[
    {x:.68,y:-.82,right:true},{x:-.68,y:-.82,right:false},
    {x:-1,y:0,right:false},{x:-.68,y:.82,right:false},
    {x:.68,y:.82,right:true},{x:1,y:0,right:true}
  ];
  const channels=[{shift:-1,name:'123'},{shift:0,name:'234'},{shift:1,name:'345'},{shift:0,name:'contact'}];
  const components=[...root.querySelectorAll('[data-variant]')].map(section=>({
    section,name:section.dataset.variant,coloured:section.dataset.variant==='Colour',
    component:section.querySelector('.op-component'),box:section.querySelector('.op-size'),
    svg:section.querySelector('.op-diagram'),drawing:section.querySelector('.op-drawing'),
    design:{width:460,duration:11/3},width:460,phase:0
  }));
  let previous=0,frame=0,inView=true;
  function line(a,b,color,opacity,stroke=1.75,erase=0) {
    if(opacity<.002||erase>.999)return '';
    return `<path d="M${f(a[0])},${f(a[1])} L${f(b[0])},${f(b[1])}" fill="none" stroke="${color}" stroke-width="${stroke}" opacity="${f(opacity)}" stroke-linecap="round" pathLength="100" stroke-dasharray="${f(100*(1-erase))} 100" stroke-dashoffset="${f(-100*erase)}"/>`;
  }
  function dot(p,color,opacity,r=2.15) {
    if(opacity<.002||r<.02)return '';
    return `<circle cx="${f(p[0])}" cy="${f(p[1])}" r="${f(r)}" fill="${color}" opacity="${f(opacity)}"/>`;
  }
  function numeral(p,n,opacity,scale=1) {
    if(opacity<.002)return '';
    return `<text class="op-number ${n===6?'op-soft-number':''}" transform="translate(${f(p[0])},${f(p[1])}) scale(${f(scale)})" text-anchor="middle" dominant-baseline="central" opacity="${f(opacity)}">${n}</text>`;
  }
  function direction(slot,identity,align) {
    const target=slots[identity-1];
    const start=Math.atan2(slot.y,slot.x),end=Math.atan2(target.y,target.x);
    const delta=Math.atan2(Math.sin(end-start),Math.cos(end-start));
    const angle=start+delta*align;
    const radius=lerp(Math.hypot(slot.x,slot.y),Math.hypot(target.x,target.y),align);
    return [Math.cos(angle)*radius,Math.sin(angle)*radius];
  }
  function diagram(c,center,radius,channel,state) {
    const {soft,pinch,align,erase,alpha,labelAlpha,morph,evaporate}=state;
    const contact=channel.name==='contact';
    const half=contact?0:radius*.43*(1-pinch);
    const left=[center[0]-half,center[1]],right=[center[0]+half,center[1]];
    let output=contact?'':line(left,right,'var(--op-ink)',alpha,2,erase);
    slots.forEach((slot,index)=>{
      const identity=((index+channel.shift+6)%6)+1;
      const start=slot.right?right:left;
      const vector=direction(slot,identity,align);
      const endPoint=[center[0]+vector[0]*radius,center[1]+vector[1]*radius];
      const label=[center[0]+vector[0]*(radius+12),center[1]+vector[1]*(radius+12)];
      const isSoft=identity===6;
      const end=isSoft?mix(endPoint,start,soft):endPoint;
      const color=isSoft?'var(--op-soft)':(c.coloured?`var(--op-leg-${identity})`:'var(--op-ink)');
      output+=line(start,end,color,alpha*(isSoft?1-soft:1),isSoft?2.65:1.75,erase);
      if(isSoft) {
        if(!c.coloured)output+=numeral(label,6,alpha*(1-morph),lerp(1,.25,morph));
        const bead=c.coloured?end:mix(label,end,morph);
        bead[1]-=evaporate*2.5;
        output+=dot(bead,'var(--op-soft)',alpha*(c.coloured?1:morph)*(1-evaporate),3.0*(1-evaporate));
      } else if(!c.coloured)output+=numeral(label,identity,alpha*labelAlpha*(1-erase));
    });
    const nodeAlpha=alpha*(1-step(erase,0,.25));
    output+=dot(left,'var(--op-ink)',nodeAlpha,2.25);
    if(!contact)output+=dot(right,'var(--op-ink)',nodeAlpha*(1-pinch),2.25);
    return `<g data-channel="${channel.name}" data-center="${f(center[0])},${f(center[1])}">${output}</g>`;
  }
  function draw(c) {
    const stacked=c.width<370;
    const height=stacked?224:134;
    const cellWidth=stacked?c.width/2:c.width/4;
    const radius=Math.min(30,cellWidth*.275);
    const centers=stacked?
      [[c.width*.25,54],[c.width*.75,54],[c.width*.25,168],[c.width*.75,168]]:
      [[c.width*.125,67],[c.width*.375,67],[c.width*.625,67],[c.width*.875,67]];
    const middle=[c.width/2,height/2];
    const returning=c.phase>.91;
    const t=returning?0:c.phase;
    const state={
      soft:step(t,.23,.61),pinch:step(t,.31,.65),align:step(t,.36,.65),
      erase:step(t,.72,.85),alpha:returning?step(c.phase,.92,.993):1,
      labelAlpha:1-step(t,.29,.41),morph:step(t,.25,.37),evaporate:step(t,.46,.64)
    };
    const gather=step(t,.26,.70);
    // A common contraction preserves the order and spacing of all four centres.
    // No channel disappears ahead of the common visual sum.
    c.drawing.innerHTML=channels.map((channel,index)=>diagram(c,mix(centers[index],middle,gather),radius,channel,state)).join('');
    c.svg.setAttribute('viewBox',`0 0 ${c.width} ${height}`);
    c.svg.style.height=`${height}px`;
    c.svg.dataset.phase=c.phase.toFixed(3);
    c.svg.dataset.gather=gather.toFixed(3);
  }
  function layout(c) {c.box.style.width=`${c.design.width}px`;draw(c);}
  function tick(time) {
    frame=0;
    if(!root.isConnected||!inView||document.hidden||motion.matches){previous=0;return;}
    const elapsed=previous?Math.min(time-previous,80):0;previous=time;
    components.forEach(c=>{c.phase=(c.phase+elapsed/(c.design.duration*1000))%1;if(!c.section.hidden)draw(c);});
    frame=requestAnimationFrame(tick);
  }
  function resume() {if(!frame&&inView&&!document.hidden&&!motion.matches){previous=0;frame=requestAnimationFrame(tick);}}
  components.forEach(c=>{
    layout(c);
    new ResizeObserver(entries=>{const measured=entries[0].contentRect.width;if(measured>0){c.width=Math.round(measured);draw(c);}}).observe(c.box);
  });
  new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;if(inView)resume();else{cancelAnimationFrame(frame);frame=0;previous=0;}}).observe(root);
  document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0;previous=0;}else resume();});
  motion.addEventListener('change',()=>{cancelAnimationFrame(frame);frame=0;previous=0;components.forEach(c=>{c.phase=0;draw(c);});resume();});
  resume();
})();


(() => {
  const page=document.getElementById('jonah-airy-numbered-page');
  const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
  page.querySelectorAll('a[href^="#"]').forEach(link=>link.addEventListener('click',event=>{
    const target=page.querySelector(link.getAttribute('href'));
    if(!target)return;
    event.preventDefault();
    target.scrollIntoView({behavior:motion.matches?'instant':'smooth',block:'start'});
  }));
})();

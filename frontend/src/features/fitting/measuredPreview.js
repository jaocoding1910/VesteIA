// Measurements come from the normalized catalog API, never from image pixels.
const positive = value => Number.isFinite(Number(value)) && Number(value)>0 ? Number(value) : null;
export const supportedCategories = ['camiseta','camisa','blusa','regata','casaco','jaqueta','calca','short','bermuda','saia','vestido','calcado','bone'];
export function measurementValue(size, category, axis) {
 const m=size?.medidas||{};
 const fields=axis==='width' ? (['calca','short','bermuda','saia'].includes(category)?[['largura_cm',1],['quadril_cm',.5],['cintura_cm',.5]]:category==='bone'?[['largura_cm',1]]:[['largura_cm',1],['torax_cm',.5]]) : axis==='length'?(category==='calcado'?[['pe_cm',1],['comprimento_cm',1]]:[['comprimento_cm',1]]):axis==='sleeve'?[['manga_cm',1]]:[['ombros_cm',1]];
 for(const [field,factor] of fields){const value=positive(m[field]);if(value)return {value:value*factor,field};}return null;
}
export function measuredRatios(reference, selected, category) {
 const result={valid:true,missing:[],ratios:{},measurements:{}};
 for(const axis of ['width','length','sleeve','shoulder']){
  const a=measurementValue(reference,category,axis),b=measurementValue(selected,category,axis);
  // Different semantics cannot silently be compared (flat width vs circumference).
  const usable=a&&b&&a.field===b.field;
  result.ratios[axis]=usable?b.value/a.value:1;
  result.measurements[axis]={reference:a,selected:b};
  if(!usable&&['width','length'].includes(axis))result.missing.push(axis);
 }
 result.valid=result.missing.length===0;
 result.outOfRange=Object.values(result.ratios).some(r=>r<.65||r>1.5);
 return result;
}
export function defaultOutline(category){
 if(['calca','short','bermuda'].includes(category))return [[.40,.49],[.60,.49],[.62,.83],[.53,.83],[.50,.62],[.47,.83],[.38,.83]];
 if(category==='saia')return [[.40,.49],[.60,.49],[.67,.79],[.33,.79]];
 if(category==='vestido')return [[.44,.21],[.56,.21],[.63,.36],[.59,.48],[.70,.83],[.30,.83],[.41,.48],[.37,.36]];
 if(category==='bone')return [[.41,.055],[.59,.055],[.62,.13],[.38,.13]];
 if(category==='calcado')return [[.36,.88],[.64,.88],[.67,.98],[.33,.98]];
 return [[.44,.20],[.56,.20],[.68,.25],[.72,.35],[.62,.37],[.60,.49],[.40,.49],[.38,.37],[.28,.35],[.32,.25]];
}
export function bounds(points){return {left:Math.min(...points.map(p=>p[0])),right:Math.max(...points.map(p=>p[0])),top:Math.min(...points.map(p=>p[1])),bottom:Math.max(...points.map(p=>p[1]))};}
export function warpPoint(point,box,ratios,upper){
 const center=(box.left+box.right)/2, height=box.bottom-box.top;
 const t=height>0?Math.max(0,Math.min(1,(point[1]-box.top)/height)):0;
 // Shoulder line remains anchored. Sleeve/shoulder control is independent of torso width.
 const shoulder=upper?ratios.shoulder:ratios.width;
 const width=shoulder+(ratios.width-shoulder)*Math.min(1,t*3);
 const side=upper?Math.max(0,Math.min(1,(Math.abs(point[0]-center)/(Math.max(.001,box.right-box.left)/2)-.55)/.45)):0;
 const length=ratios.length+(ratios.sleeve-ratios.length)*side;
 return [center+(point[0]-center)*width,box.top+(point[1]-box.top)*length];
}
function triangle(ctx,image,src,dst){
 const [a,b,c]=src,[d,e,f]=dst;
 const det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);if(Math.abs(det)<1e-8)return;
 const aa=((e[0]-d[0])*(c[1]-a[1])-(f[0]-d[0])*(b[1]-a[1]))/det;
 const cc=((f[0]-d[0])*(b[0]-a[0])-(e[0]-d[0])*(c[0]-a[0]))/det;
 const bb=((e[1]-d[1])*(c[1]-a[1])-(f[1]-d[1])*(b[1]-a[1]))/det;
 const dd=((f[1]-d[1])*(b[0]-a[0])-(e[1]-d[1])*(c[0]-a[0]))/det;
 const center=[(d[0]+e[0]+f[0])/3,(d[1]+e[1]+f[1])/3];const edge=[d,e,f].map(p=>{const distance=Math.hypot(p[0]-center[0],p[1]-center[1]);return distance?[p[0]+(p[0]-center[0])*.65/distance,p[1]+(p[1]-center[1])*.65/distance]:p;});
 ctx.save();ctx.beginPath();ctx.moveTo(...edge[0]);ctx.lineTo(...edge[1]);ctx.lineTo(...edge[2]);ctx.closePath();ctx.clip();ctx.setTransform(aa,bb,cc,dd,d[0]-aa*a[0]-cc*a[1],d[1]-bb*a[0]-dd*a[1]);ctx.drawImage(image,0,0);ctx.restore();
}
export function renderMeasured(canvas,base,dressed,points,ratios,category){
 const w=canvas.width,h=canvas.height,ctx=canvas.getContext('2d');ctx.clearRect(0,0,w,h);ctx.drawImage(base,0,0,w,h);
 const layer=document.createElement('canvas');layer.width=w;layer.height=h;const lc=layer.getContext('2d');
 lc.beginPath();points.forEach((p,i)=>i?lc.lineTo(p[0]*w,p[1]*h):lc.moveTo(p[0]*w,p[1]*h));lc.closePath();lc.clip();lc.drawImage(dressed,0,0,w,h);
 const box=bounds(points),upper=['camiseta','camisa','blusa','regata','casaco','jaqueta'].includes(category);
 const n=24,point=(x,y)=>[x*w/n,y*h/n],destination=(x,y)=>{const p=warpPoint([x/n,y/n],box,ratios,upper);return [p[0]*w,p[1]*h];};
 for(let y=0;y<n;y++)for(let x=0;x<n;x++){
  triangle(ctx,layer,[point(x,y),point(x+1,y),point(x+1,y+1)],[destination(x,y),destination(x+1,y),destination(x+1,y+1)]);
  triangle(ctx,layer,[point(x,y),point(x+1,y+1),point(x,y+1)],[destination(x,y),destination(x+1,y+1),destination(x,y+1)]);
 }
}

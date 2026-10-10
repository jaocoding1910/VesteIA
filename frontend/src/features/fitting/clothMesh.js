// Malha frontal determinística. Não infere centímetros de pixels nem altera a tabela.
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
export function affineTriangle(source,target){
 const [p,q,r]=source,[u,v,w]=target;
 const det=(q[0]-p[0])*(r[1]-p[1])-(r[0]-p[0])*(q[1]-p[1]);
 if(Math.abs(det)<1e-8)throw new Error('Triângulo degenerado');
 const a=((v[0]-u[0])*(r[1]-p[1])-(w[0]-u[0])*(q[1]-p[1]))/det;
 const c=((w[0]-u[0])*(q[0]-p[0])-(v[0]-u[0])*(r[0]-p[0]))/det;
 const b=((v[1]-u[1])*(r[1]-p[1])-(w[1]-u[1])*(q[1]-p[1]))/det;
 const d=((w[1]-u[1])*(q[0]-p[0])-(v[1]-u[1])*(r[0]-p[0]))/det;
 return [a,b,c,d,u[0]-a*p[0]-c*p[1],u[1]-b*p[0]-d*p[1]];
}
function interpolate(stops,t){
 for(let i=1;i<stops.length;i++)if(t<=stops[i][0]){
  const [x0,y0]=stops[i-1],[x1,y1]=stops[i];return y0+(y1-y0)*(t-x0)/(x1-x0);
 }
 return stops.at(-1)[1];
}
export function clothMesh(model,box){
 const [x,y,w,h]=box,d=model.dimensions,c=model.category;
 const upper=['camiseta','camisa','blusa','jaqueta','casaco','regata'].includes(c),pants=['calca','short','bermuda'].includes(c);
 const xs=[0,.18,.34,.5,.66,.82,1],ys=[0,.12,.32,.5,.72,1];
 const map=([px,py])=>{
  const nx=(px-x)/w,ny=(py-y)/h,edge=Math.abs(nx-.5)*2;
  let factor=1,dy=0;
  if(upper){
   // Gola central mantém sua abertura entre grades; ombros/mangas usam suas próprias medidas.
   const collar=(1-clamp(ny/.22,0,1))*(1-clamp(edge/.5,0,1));
   factor=interpolate([[0,1],[.32,1],[.65,.95],[1,clamp(d.hem,.8,1.3)]],ny);
   factor*=1+clamp((d.shoulder-1)*.55,-.2,.25)*(1-clamp(ny/.5,0,1))*edge;
   const shoulderContact=Math.max(0,1-Math.abs(ny-.12)/.2)*clamp(edge*1.8,0,1);
   factor=factor*(1-shoulderContact)+(1.04*d.shoulder/d.x)*shoulderContact;
   factor=factor*(1-collar)+(1/d.x)*collar;
   dy=clamp((d.sleeve-1)*h*.26,-h*.1,h*.25)*edge*Math.max(0,1-Math.abs(ny-.34)/.34)-20*edge*Math.max(0,1-ny/.4);
  }else if(pants){
   factor=interpolate([[0,clamp(d.waist,.75,1.3)],[.27,clamp(d.hip,.8,1.35)],[.55,1],[1,clamp(d.hem,.75,1.35)]],ny);
  }else if(['saia','vestido'].includes(c)){
   factor=interpolate([[0,clamp(d.waist,.8,1.25)],[.3,clamp(d.hip,.85,1.3)],[1,clamp(d.hem,.8,1.4)]],ny);
  }
  return [x+w/2+(px-x-w/2)*factor,py+dy];
 };
 const nodes=ys.map(v=>xs.map(u=>[x+u*w,y+v*h])),triangles=[];
 for(let j=0;j<ys.length-1;j++)for(let i=0;i<xs.length-1;i++){
  const a=nodes[j][i],b=nodes[j][i+1],c=nodes[j+1][i],e=nodes[j+1][i+1];
  for(const source of [[a,b,e],[a,e,c]]){const target=source.map(map);triangles.push({source,target,matrix:affineTriangle(source,target)});}
 }
 return triangles;
}

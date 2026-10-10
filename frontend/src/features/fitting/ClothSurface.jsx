import {useId,useMemo} from 'react';
import {clothMesh} from './clothMesh';
// Une image, estampa e cor antes de deformar, preservando a identidade da variante.
export default function ClothSurface({model,box,children}){
 const id=useId().replaceAll(':',''),[bx,by,bw,bh]=box,{category,dimensions:{x,y,sleeve,shoulder,hem,waist,hip}}=model;
 const mesh=useMemo(()=>clothMesh({category,dimensions:{x,y,sleeve,shoulder,hem,waist,hip}},[bx,by,bw,bh]),[category,x,y,sleeve,shoulder,hem,waist,hip,bx,by,bw,bh]);
 const expanded=points=>{const cx=points.reduce((n,p)=>n+p[0],0)/3,cy=points.reduce((n,p)=>n+p[1],0)/3;return points.map(([x,y])=>{const d=Math.hypot(x-cx,y-cy),f=(d+5)/d;return [cx+(x-cx)*f,cy+(y-cy)*f];});};
 return <g data-visual="cloth-surface" data-mesh-triangles={mesh.length}>
 <defs><g id={`${id}art`}>{children}</g>{mesh.map((t,i)=><clipPath key={i} id={`${id}t${i}`} clipPathUnits="userSpaceOnUse"><path d={`M${expanded(t.target).map(p=>p.join(' ')).join('L')}Z`}/></clipPath>)}<filter id={`${id}contact`} x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="3" stdDeviation="2.2" floodColor="#111827" floodOpacity=".3"/></filter></defs>
 <g filter={`url(#${id}contact)`}>{mesh.map((t,i)=><g key={i} clipPath={`url(#${id}t${i})`}><use href={`#${id}art`} transform={`matrix(${t.matrix.join(' ')})`}/></g>)}</g>
 </g>;
}

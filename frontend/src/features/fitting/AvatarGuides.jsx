import {useId} from 'react';
// Referências gráficas do molde, não landmarks detectados nem medidas em centímetros.
export default function AvatarGuides({female}){
 const id=useId().replaceAll(':',''),shoulder=female?375:363,hip=female?402:410;
 const points=[[512,35],[512,225],[shoulder,290],[1024-shoulder,290],[512,290],[420,425],[604,425],[512,425],[365,565],[659,565],[415,600],[512,600],[609,600],[hip,710],[512,710],[1024-hip,710],[445,1060],[579,1060],[435,1425],[589,1425],[348,780],[676,780]];
 return <g data-layer="avatar-guides" aria-hidden="true" pointerEvents="none"><defs><filter id={`${id}glow`} x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="5"/></filter></defs><g stroke="#b7edff" strokeWidth="2.5" strokeOpacity=".65" fill="none"><path d={`M512 35V710M${shoulder} 290H${1024-shoulder}M${shoulder} 290 365 565 348 780M${1024-shoulder} 290 659 565 676 780M${hip} 710 445 1060 435 1425M${1024-hip} 710 579 1060 589 1425`}/><ellipse cx="512" cy="425" rx="92" ry="11" strokeDasharray="7 6"/><ellipse cx="512" cy="600" rx="97" ry="10" strokeDasharray="7 6"/><ellipse cx="512" cy="710" rx={512-hip} ry="12" strokeDasharray="7 6"/></g>{points.map(([x,y],i)=><g key={i}><circle cx={x} cy={y} r="12" fill="#62caff" opacity=".9" filter={`url(#${id}glow)`}/><circle cx={x} cy={y} r="4.8" fill="#f0fbff"/></g>)}</g>;
}

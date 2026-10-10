import {useId} from 'react';
export default function AvatarVisualTabs({value,onChange}){
 const id=useId().replaceAll(':','');
 return <div className="avatar-visual-tabs" role="tablist" aria-label="Visualização do avatar">{[['natural','Visual natural'],['points','Pontos e proporções']].map(([key,label])=><button type="button" role="tab" key={key} id={`${id}-${key}`} tabIndex={value===key?0:-1} onKeyDown={e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const next=e.key==='Home'?'natural':e.key==='End'?'points':key==='natural'?'points':'natural';onChange(next);document.getElementById(`${id}-${next}`)?.focus();}} aria-selected={value===key} className={value===key?'active':''} onClick={()=>onChange(key)}>{label}</button>)}</div>;
}

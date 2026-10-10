import {useEffect} from 'react';
// Um observador por página; nenhuma escuta contínua de scroll ou mouse.
export default function useMotion(page,revision){
 useEffect(()=>{
  const elements=[...document.querySelectorAll('[data-reveal]')];
  if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches){elements.forEach(n=>n.classList.add('revealed'));return;}
  const observer=new IntersectionObserver(entries=>{entries.forEach(({isIntersecting,target})=>{if(isIntersecting){target.classList.remove('motion-pending');target.classList.add('revealed');observer.unobserve(target);}});},{threshold:.08});
  elements.forEach(n=>{if(n.getBoundingClientRect().top>innerHeight)n.classList.add('motion-pending');observer.observe(n);});return()=>observer.disconnect();
 },[page,revision]);
}

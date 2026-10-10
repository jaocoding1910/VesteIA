// Cabeça recortada do PNG de referência; não inclui roupas do exemplo.
import {useId} from 'react'
export default function HumanHead({female,customTone,filterId}){
 const id=useId().replaceAll(':',''),source=female?[389,7,238,253]:[423,13,183,240]
 const target=female?[410,18,201,232]:[439,12,146,222]
 return <svg data-layer="human-head" x={target[0]} y={target[1]} width={target[2]} height={target[3]} viewBox={source.join(' ')} preserveAspectRatio="none" style={{overflow:'hidden'}}><defs><clipPath id={`${id}head`}><rect x={source[0]} y={source[1]} width={source[2]} height={source[3]}/></clipPath></defs><image href={`/assets/referencia-humana-${female?'feminino':'masculino'}.png`} width="1024" height="1536" clipPath={`url(#${id}head)`} filter={customTone?`url(#${filterId})`:undefined}/></svg>
}

import {definitionFor} from '../../renderers/garments/registry.js';
export const overlaps=(a,b)=>!!definitionFor(a.product?.categoria)?.regions.some(region=>definitionFor(b.product?.categoria)?.regions.includes(region));
export function addToLook(look,item){return [...look.filter(old=>old.product.id!==item.product.id&&!(item.ativo&&old.ativo&&overlaps(old,item))),item];}
export function toggleLook(look,id){const target=look.find(i=>i.product.id===id);if(!target)return look;return look.map(item=>item.product.id===id?{...item,ativo:!item.ativo}:!target.ativo&&overlaps(item,target)?{...item,ativo:false}:item);}

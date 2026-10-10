export const PROTOCOL='vesteia.tryon.v1';
export function parseEmbed(hash){
 const match=hash.match(/^#embed\/(\d+)(?:\?(.*))?$/);if(!match)return null;
 const params=new URLSearchParams(match[2]||'');
 return {productId:Number(match[1]),variantId:Number(params.get('variant'))||null,sizeId:Number(params.get('size'))||null,channel:params.get('channel')||''};
}
export function validSelection(data,product,channel){
 if(!data||data.protocol!==PROTOCOL||data.type!=='selection'||data.channel!==channel||data.productId!==product.id)return null;
 const variant=product.variantes.find(v=>v.id===data.variantId),size=variant?.tamanhos.find(s=>s.id===data.sizeId);
 return size&&size.estoque!==0?{variant,size}:null;
}
export function embedUrl(product,variant,size,channel){
 const url=new URL(location.href);url.hash=`embed/${product.id}?${new URLSearchParams({variant:String(variant.id),size:size?String(size.id):'',channel})}`;return url.href;
}

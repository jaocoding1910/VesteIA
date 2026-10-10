import { useId, useState } from 'react';
import { garmentColor } from './catalogModel';
export default function ProductImage({
  product,
  variant,
  large = false
}) {
  const id = useId().replaceAll(':', '');
  const [failedSource, setFailedSource] = useState(null);
  if (variant?.imagem_url && failedSource!==variant.imagem_url) return <img className={`product-image ${large ? 'large' : ''}`} src={variant.imagem_url} alt={product.nome} onError={() => setFailedSource(variant.imagem_url)} loading="lazy" />;
  const category = {camisa:'camiseta',blusa:'camiseta',casaco:'camiseta',jaqueta:'camiseta',regata:'camiseta',bermuda:'short'}[product.categoria] || product.categoria,
    color = garmentColor(variant);
  return <svg className={`product-image ${large ? 'large' : ''}`} viewBox="0 0 300 300" role="img" aria-label={`${product.nome} — ilustração da peça`}><defs><linearGradient id={id} x2="1" y2="1"><stop stopColor={color} /><stop offset=".5" stopColor={color} /><stop offset="1" stopColor="#070a10" /></linearGradient></defs><ellipse cx="150" cy="264" rx="94" ry="11" fill="#000" opacity=".28" /><g fill={`url(#${id})`} stroke="#ffffff" strokeOpacity=".13" strokeWidth="1.5">
 {category === 'bone' && <path d="M81 151Q81 63 150 63 220 63 220 151L250 187Q150 223 51 187L81 151ZM87 150Q150 136 214 150M150 68V138"/>}
 {category === 'camiseta' && <><path d="m100 60-48 34 23 44 25-14v125h100V124l25 14 23-44-48-34-24-8h-52Z" /><path d="M126 53q24 25 48 0" fill="none" strokeOpacity=".35" /><path d="M104 239h91M72 128l13-10M215 118l13 10" fill="none" /></>}
 {category === 'calca' && <path d="M105 48h90l10 211h-45l-10-137-10 137H95Zm0 22h89M150 72v43" />}
 {category === 'short' && <path d="M100 78h100l13 143h-53l-10-70-10 70H87Zm0 19h100" />}
 {category === 'saia' && <path d="M116 58h68l45 193H71Zm0 20h68M128 88l-24 153M173 88l22 153" />}
 {category === 'vestido' && <path d="m115 43 12-8q23 24 46 0l12 8 16 56-23 29 46 132H76l46-132-23-29Zm10 86h50" />}
 {category === 'calcado' && <><path d="m75 139 45 24 42-51 29 31 16 52 36 15 8 30H55l-5-37Zm-20 83h196" /><path d="m139 153 39 9m-47 1 38 10m-44 0 34 10" strokeOpacity=".5" fill="none" /></>}
 </g></svg>;
}

import { useId, useState } from 'react';
import { garmentVisualModel } from './garmentModel';
import { definitionFor } from '../../renderers/garments/registry';
import ClothSurface from './ClothSurface';
import { geometryFor } from '../../renderers/garments/geometry';
export default function GarmentLayer({
  item
}) {
  const uid = useId().replaceAll(':', ''),
    [failed, setFailed] = useState({}),
    category = item.product.categoria,
    base = definitionFor(category)?.geometry;
  if (!base) return null;
  const model = garmentVisualModel(item),
    dims = model.dimensions,
    appearance = model.appearance,
    color = model.color,
    rawLayout = geometryFor(base, model),
    // Registro do asset vem do catálogo, sem identificar produtos por ID ou nome.
    waistOffset = item.avatarStyle==='humano' && Number.isFinite(Number(appearance.bodyRegistration.subir_cintura_px)) ? Math.max(-120,Math.min(120,Number(appearance.bodyRegistration.subir_cintura_px))) : 0,
    layout = waistOffset ? {...rawLayout,box:[rawLayout.box[0],rawLayout.box[1]-waistOffset,rawLayout.box[2],rawLayout.box[3]+waistOffset],anchor:[rawLayout.anchor[0],rawLayout.anchor[1]-waistOffset]} : rawLayout;
  const [bx, by, bw, bh] = layout.box,
    [ax, ay] = layout.anchor,
    crop = appearance.textureCrop,
    p = appearance.printPosition;
  // Cada fonte pode falhar isoladamente; nunca mantém a imagem de uma variante anterior.
  const unavailable = url => !!failed[url],
    onError = url => setFailed(old => ({
      ...old,
      [url]: true
    }));
  const bounded = (value, fallback) => Number.isFinite(Number(value)) ? Math.max(0, Math.min(1, Number(value))) : fallback;
  const px = bounded(p.x, .5),
    py = bounded(p.y, .38),
    pw = bounded(p.w, .5),
    ph = bounded(p.h, .18);
  const garmentContour = item.avatarStyle==='humano' && category==='camiseta' ? layout.path.replace('Q512 313','Q512 350') : layout.path;
  const imageAsset = appearance.garmentUrl && !unavailable(appearance.garmentUrl);
  const preparedDemo = imageAsset && appearance.garmentUrl.includes('roupa-real-');
  const recolor = imageAsset && appearance.garmentUrl.includes('roupa-real-') && !['#18191b','#191b1f','#202124','#17191c','#16191d'].includes(color.toLowerCase()) && !item.variant?.cor?.toLowerCase().includes('preto');
  const rgb = /^#[0-9a-f]{6}$/i.test(color) ? [1,3,5].map(i=>parseInt(color.slice(i,i+2),16)/255) : [.5,.5,.5];
  const fabricMatrix = rgb.map(c=>`${.2126*c*4} ${.7152*c*4} ${.0722*c*4} 0 ${c*.18}`).join(' ')+' 0 0 0 1 0';
  const texture = appearance.textureUrl && crop && !unavailable(appearance.textureUrl) && crop.w > 0 && crop.h > 0;
  return <g data-layer={`garment-${category}`} data-product-id={model.productId} data-sku={model.sku} data-fit={model.fit} data-width-cm={dims.width} data-length-cm={dims.length} data-scale-x={dims.x} data-scale-y={dims.y} data-sleeve={dims.sleeve} data-waist={dims.waist} data-hip={dims.hip} data-hem={dims.hem} transform={`translate(${ax} ${ay}) scale(${dims.x} ${dims.y}) translate(${-ax} ${-ay})`}>
 <defs><filter id={`${uid}recolor`} colorInterpolationFilters="sRGB">{preparedDemo&&<feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 -12 10 2 1 0"/>}{recolor&&<feColorMatrix type="matrix" values={fabricMatrix} />}</filter><clipPath id={`${uid}clip`}><path d={garmentContour} /></clipPath><linearGradient id={`${uid}fabric`}><stop stopColor={color} /><stop offset=".48" stopColor={color} /><stop offset="1" stopColor={color} /></linearGradient><linearGradient id={`${uid}shade`}><stop stopColor="#000" stopOpacity=".24" /><stop offset=".42" stopColor="#fff" stopOpacity=".06" /><stop offset="1" stopColor="#000" stopOpacity=".28" /></linearGradient></defs>
 <ClothSurface model={model} box={layout.box}>
 <path data-visual="opaque-garment-base" d={garmentContour} fill={`url(#${uid}fabric)`} stroke={color} strokeWidth="8" strokeLinejoin="round" />
 {imageAsset ? <g clipPath={`url(#${uid}clip)`}>{appearance.garmentCrop?<svg x={bx} y={by} width={bw} height={bh} viewBox={appearance.garmentCrop.join(' ')} preserveAspectRatio="none"><image data-visual="garment-asset" href={appearance.garmentUrl} width={appearance.garmentImageSize[0]} height={appearance.garmentImageSize[1]} onError={()=>onError(appearance.garmentUrl)}/></svg>:<image data-visual="garment-asset" filter={preparedDemo?`url(#${uid}recolor)`:undefined} href={appearance.garmentUrl} x={bx} y={by} width={bw} height={bh} preserveAspectRatio="none" onError={()=>onError(appearance.garmentUrl)}/>}</g> : <g clipPath={`url(#${uid}clip)`}>
 {texture && <svg data-visual="product-texture" x={bx} y={by} width={bw} height={bh} viewBox={`${crop.x || 0} ${crop.y || 0} ${crop.w} ${crop.h}`} preserveAspectRatio="none"><image href={appearance.textureUrl} width="1" height="1" preserveAspectRatio="none" onError={() => onError(appearance.textureUrl)} /></svg>}
 <path d={layout.path} fill={`url(#${uid}shade)`} />
 <path d={layout.seams} stroke="#fff" strokeOpacity=".16" strokeWidth="3" fill="none" /><path d={layout.path} stroke="#000" strokeOpacity=".22" strokeWidth="2" fill="none" />
 </g>}
 <g clipPath={`url(#${uid}clip)`}>
 {appearance.printUrl && !unavailable(appearance.printUrl) && <image data-visual="print-image" href={appearance.printUrl} x={bx + bw * (px - pw / 2)} y={by + bh * (py - ph / 2)} width={bw * pw} height={bh * ph} preserveAspectRatio="xMidYMid meet" onError={() => onError(appearance.printUrl)} />}
 {appearance.printText && <text data-visual="print-text" x={bx + bw * px} y={by + bh * py} fill={appearance.printColor} fontFamily="Arial,sans-serif" fontSize={bw * Math.min(.12, pw / Math.max(appearance.printText.length * .6, 1))} textAnchor="middle" dominantBaseline="middle">{appearance.printText}</text>}
 </g>
 </ClothSurface>
 </g>;
}

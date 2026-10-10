import { useId } from 'react';
import GarmentLayer from './GarmentLayer';
import { selectedGarments } from './garmentModel';
// Renderer frontal 2D. Aparência visual e geometria da roupa são camadas independentes.
export default function AvatarIllustration({
  profile,
  product,
  variant,
  size,
  look = [],
  showProduct = true,
  frame = null
}) {
  const id = useId().replaceAll(':', '');
  const skin = profile?.tom_pele || '#b87d57',
    hair = profile?.cabelo || '#292018',
    female = profile?.genero === 'feminino';
  const width = {
    estreito: .9,
    medio: 1,
    largo: 1.13
  }[profile?.porte_corporal] || 1;
  const bodyWidth = width * Math.max(.84, Math.min(1.2, profile?.medidas?.torax_cm ? profile.medidas.torax_cm / 100 : 1 + ((profile?.peso_aproximado_kg || 75) - 75) * .002));
  const height = Math.max(.9, Math.min(1.08, (profile?.altura_aproximada_cm || 175) / 175));
  const layers = selectedGarments({
    product,
    variant,
    size,
    look,
    showProduct
  });
  return <svg className="avatar-illustration" viewBox={frame ? [frame[0] * .234375, frame[1] * .3 + 27, frame[2] * .234375, frame[3] * .3].join(' ') : '0 0 240 490'} role="img" aria-label={`Ilustração 2D ${female ? 'feminina' : 'masculina'}${size ? `, tamanho ${size.label}` : ''}`}><defs>
 <linearGradient id={`${id}s`} x1="0" x2="1"><stop stopColor={skin} /><stop offset=".55" stopColor={skin} /><stop offset="1" stopColor="#51352b" /></linearGradient>
 <radialGradient id={`${id}halo`}><stop stopColor="#1d6075" stopOpacity=".24" /><stop offset="1" stopColor="#152431" stopOpacity="0" /></radialGradient>
 </defs><ellipse cx="120" cy="291" rx="115" ry="185" fill={`url(#${id}halo)`} /><ellipse cx="120" cy="463" rx="66" ry="9" fill="#000" opacity=".48" />
 <g transform={`translate(120 454) scale(${bodyWidth} ${height}) translate(-120 -454)`}>
 {(profile?.estilo_cabelo === 'longo' || female && !profile?.estilo_cabelo) && <path d="M93 46q-12-18-2-31 30-31 55 4 9 18 3 39l5 57H88Z" fill={hair} />}
 <path d="M107 71h26v28l20 10-34 26-31-26 19-10Z" fill={`url(#${id}s)`} />
 <path d="M105 76q15 15 28-2v13q-18 11-28-11" fill="#342017" opacity=".18" />
 <ellipse cx="95" cy="48" rx="5" ry="11" fill={skin} /><ellipse cx="145" cy="48" rx="5" ry="11" fill={skin} />
 <path d="M96 30q24-23 48 0l-1 32q-7 22-23 23-17-3-23-24Z" fill={`url(#${id}s)`} />
 {profile?.estilo_cabelo !== 'raspado' && <path d="M94 44V26q0-22 25-23 27 0 28 27l-3 16-5-17q-16 8-27-3l-14 10Z" fill={hair} />}
 <path d="m103 43 10-1m14 0 10 1" stroke={hair} strokeWidth="2" strokeLinecap="round" /><ellipse cx="108" cy="48" rx="2" ry="1.7" fill="#1d1715" /><ellipse cx="132" cy="48" rx="2" ry="1.7" fill="#1d1715" />
 <path d="m120 48-3 12h6m-12 10q9 4 18-1" stroke="#684332" fill="none" strokeWidth="1.3" />
 <path d="M91 103 72 116 66 183l-8 93 13 5 18-95 11-58M149 103l19 13 6 67 8 93-13 5-18-95-11-58" fill={`url(#${id}s)`} />
 <path d="M58 272q-8 18-3 28l6 5 3-15 4 12 5-4-2-23m111-3q8 18 3 28l-6 5-3-15-4 12-5-4 2-23" fill={skin} />
 <path d={female ? 'M94 105q26 7 52 0l-6 70 12 51H88l12-51Z' : 'M92 105h56l-6 121H98Z'} fill={`url(#${id}s)`} />
 {female && <path data-layer="neutral-chest-cover" d="M94 126q26 8 52 0l-3 29q-23 7-46 0Z" fill="#b5bcc6" />}
 <path d="M94 222h52l7 72-10 153h-21l-2-136-2 136H97L87 294Z" fill={`url(#${id}s)`} />
 <path data-layer="neutral-intimate-cover" d="M92 221h56l4 35-30 8-2-16-2 16-30-8Z" fill="#b5bcc6" />
 <path data-layer="neutral-feet" d="M97 441h21v18H89q-8-9 8-18m26 0h20q16 9 8 18h-28Z" fill={`url(#${id}s)`} />
 <g transform="translate(0 27) scale(.234375 .3)">{layers.map(item => <GarmentLayer key={`${item.product.id}-${item.variant?.id}-${item.size?.id}`} item={item} />)}</g>
 </g></svg>;
}

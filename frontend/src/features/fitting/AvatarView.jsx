import { useId } from 'react';
import SmoothAvatarBody from './SmoothAvatarBody';
import HumanAvatarBody from './HumanAvatarBody';
import AvatarGuides from './AvatarGuides';
import GarmentLayer from './GarmentLayer';
import { selectedGarments } from './garmentModel';
import {definitionFor} from '../../renderers/garments/registry';
import { avatarGeometry, neutralProfile } from './avatarModel';
// Um único avatar: a foto configura proporções e a edição manual continua disponível.
export default function AvatarView({
  profile: given,
  ...props
}) {
  const id = useId().replaceAll(':', ''),
    profile = {
      ...neutralProfile,
      ...given
    },
    female = profile.genero === 'feminino',
    layers = selectedGarments(props),
    human = profile.estilo_avatar === 'humano',
    cleanBase = layers.length>0 || props.cleanPreview,
    covered = new Set(layers.flatMap(item=>definitionFor(item.product.categoria)?.regions||[])),
    g = avatarGeometry(profile),
    hip = 290 + 370 * g.torso;
  const skin = human && profile.tom_pele === '#a7a5a1' ? '#d3a079' : profile.tom_pele,
    channels = /^#[0-9a-f]{6}$/i.test(skin) ? [1, 3, 5].map(i => parseInt(skin.slice(i, i + 2), 16) / 255) : [.65, .65, .65];
  const matrix = channels.map(c => `${.2126 * c * 1.42} ${.7152 * c * 1.42} ${.0722 * c * 1.42} 0 0`).join(' ') + ' 0 0 0 1 0';
  const baseUrl = human ? `/assets/avatar-humano-${female ? 'feminino' : 'masculino'}-v2.png` : `/assets/manequim-${female ? 'feminino' : 'masculino'}-base.png`;
  const base = <>{human?<HumanAvatarBody profile={profile} cleanBase={cleanBase}/>:cleanBase?<SmoothAvatarBody gender={profile.genero}/>:<image data-layer="neutral-mannequin" data-avatar-gender={profile.genero} data-base-clothes="neutral" href={baseUrl} width="1024" height="1536" preserveAspectRatio="none"/>}
 {!human && skin !== '#a7a5a1' && (cleanBase?<SmoothAvatarBody gender={profile.genero} tint filter={`url(#${id}skin)`} mask={`url(#${id}skinMask)`}/>:<image data-layer="skin-tint" href={`/assets/manequim-${female ? 'feminino' : 'masculino'}-base.png`} width="1024" height="1536" filter={`url(#${id}skin)`} mask={`url(#${id}skinMask)`}/>)}
 {cleanBase&&<g data-layer="neutral-privacy" fill="#b4b5b0">{!covered.has('lower')&&<path d="M403 700Q512 720 621 700L615 755Q567 770 512 814Q457 770 409 755Z"/>}{female&&!covered.has('upper')&&!covered.has('outer')&&<path d="M413 378Q512 363 611 378L604 455Q512 440 420 455Z"/>}</g>}
 {(!human && profile.estilo_cabelo === 'longo') && <path data-layer="hair" d="M444 70Q438 20 511 19 584 19 580 70L565 75Q532 79 500 62L461 79 465 279 421 257ZM580 74 603 257 559 279 566 79Z" fill={profile.cabelo} />}
 {(!human && profile.estilo_cabelo === 'curto') && <path data-layer="hair" d="M443 104Q436 17 510 18 585 13 581 106L565 73Q530 82 499 63L462 77Z" fill={profile.cabelo} />}
 {(!human && profile.estilo_cabelo === 'crespo') && <g data-layer="hair" fill={profile.cabelo}>{Array.from({length:13},(_,i)=><circle key={i} cx={450+(i%7)*20} cy={i<7?58:32} r={24}/>)}</g>}
 {layers.map(item => <GarmentLayer key={`${item.product.id}-${item.variant?.id}-${item.size?.id}`} item={{...item,avatarGender:profile.genero,avatarStyle:profile.estilo_avatar}} />)}
 {props.visualMode==='points'&&<AvatarGuides female={female}/> }
 </>;
  return <svg className="avatar-natural" viewBox={props.frame ? props.frame.join(' ') : '30 -190 964 1900'} role="img" aria-label={`Avatar VesteIA ${female ? 'feminino' : 'masculino'} — ${layers.length ? layers.map(i => `${i.product.nome}, ${i.size?.label || ''}`).join(' + ') : 'base neutra'}`}>
 <defs><g id={`${id}base`}>{base}</g><filter id={`${id}skin`} colorInterpolationFilters="sRGB"><feColorMatrix type="matrix" values={matrix} /></filter><mask id={`${id}skinMask`}><rect width="1024" height="1536" fill="white" />{!cleanBase&&<rect x="350" y="646" width="325" height="224" fill="black" />}{female&&!cleanBase && <rect x="390" y="350" width="245" height="132" fill="black" />}</mask><clipPath id={`${id}head`}><rect x="-200" y="-200" width="1500" height="490" /></clipPath><clipPath id={`${id}body`}><rect x="-200" y="290" width="1500" height="1500" /></clipPath><clipPath id={`${id}upper`}><rect x="-200" y="-200" width="1500" height="861" /></clipPath><clipPath id={`${id}lower`}><rect x="-200" y="659.5" width="1500" height="1100" /></clipPath></defs>
 <g data-body-transform={g.bodyTransform} transform={g.bodyTransform}>
 <g data-physique={profile.porte_corporal} clipPath={`url(#${id}head)`}><use href={`#${id}base`}/></g><g clipPath={`url(#${id}body)`} transform={`translate(512 0) scale(${g.width} 1) translate(-512 0)`}><g transform={`translate(0 290) scale(1 ${g.torso}) translate(0 -290)`}><g clipPath={`url(#${id}upper)`}><use href={`#${id}base`}/></g></g>
 <g transform={`translate(0 ${hip}) scale(1 ${g.legs}) translate(0 -660)`}><g clipPath={`url(#${id}lower)`}><use href={`#${id}base`}/></g></g>
 </g></g></svg>;
}

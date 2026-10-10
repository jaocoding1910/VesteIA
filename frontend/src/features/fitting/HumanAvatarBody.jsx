import {smoothBody} from './smoothAvatarSource';
import {useEffect,useState} from 'react';
// A paleta altera somente pixels de pele; vestimentas são camadas separadas.
const renderedBodies=new Map();
const atlases=new Map();
function loadAtlas(source){if(!atlases.has(source))atlases.set(source,new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>{atlases.delete(source);reject(new Error('Não foi possível carregar o avatar'));};image.src=source;}));return atlases.get(source);}
const hairstyles={raspado:0,curto:1,crespo:2,longo:3};
const validColor=(value,fallback)=>/^#[0-9a-f]{6}$/i.test(value||'')?value:fallback;
const rgb=value=>[1,3,5].map(i=>parseInt(value.slice(i,i+2),16));
const clamp=value=>Math.max(0,Math.min(255,value));
export default function HumanAvatarBody({profile,cleanBase=false}){
 const female=profile.genero==='feminino',gender=female?'feminino':'masculino',style=profile.estilo_cabelo in hairstyles?profile.estilo_cabelo:'curto',skin=validColor(profile.tom_pele==='#a7a5a1'?'#d3a079':profile.tom_pele,'#d3a079'),hair=validColor(profile.cabelo,'#353536');
 const source=`/assets/avatar-humano-${gender}-personalizavel.png`,key=[source,style,skin,hair,cleanBase].join('|'),[result,setResult]=useState(null);
 useEffect(()=>{
  let cancelled=false;const render=async img=>{
   if(cancelled)return;
   if(renderedBodies.has(key)){setResult({key,url:renderedBodies.get(key)});return;}
   const index=hairstyles[style],canvas=document.createElement('canvas');canvas.width=1024;canvas.height=1536;const ctx=canvas.getContext('2d',{willReadFrequently:true});
   const split=img.height*(female?784/1536:750/1536),second=index>=2;
   ctx.drawImage(img,(index%2)*img.width/2,second?split:0,img.width/2,second?img.height-split:split,0,0,1024,1536);
   // Centraliza cada célula pelo recorte opaco, sem usar o fundo RGB transparente.
   const scan=ctx.getImageData(0,0,1024,1536).data;let minX=1024,maxX=0;
   for(let y=350;y<1300;y++)for(let x=0;x<1024;x++)if(scan[(y*1024+x)*4+3]>220){minX=Math.min(minX,x);maxX=Math.max(maxX,x);}
   const shift=512-(minX+maxX)/2;if(maxX>minX&&Math.abs(shift)>1){const copy=document.createElement('canvas');copy.width=1024;copy.height=1536;copy.getContext('2d').drawImage(canvas,0,0);ctx.clearRect(0,0,1024,1536);ctx.drawImage(copy,shift,0);}
   let smoothPixels=null;
   if(cleanBase){
    try{
     const donor=await smoothBody(gender);if(cancelled)return;smoothPixels=donor.canvas.getContext('2d',{willReadFrequently:true}).getImageData(0,0,1024,1536).data;
    }catch{if(!cancelled)setResult({key,url:`/assets/manequim-${gender}-base.png`,failed:true});return;}
   }
   const pixels=ctx.getImageData(0,0,1024,1536),target=rgb(skin),hairTarget=rgb(hair),data=pixels.data;
   for(let i=0;i<data.length;i+=4){
    if(data[i+3]===0)continue;
    const r=data[i],g=data[i+1],b=data[i+2],l=.2126*r+.7152*g+.0722*b,y=Math.floor(i/4/1024)/1536,x=(i/4%1024)/1024;
    const skinWeight=Math.max(0,Math.min(1,(r-g-5)/12))*Math.max(0,Math.min(1,(g-b-3)/10))*Math.max(0,Math.min(1,(l-55)/30));
    if(skinWeight>0){for(let c=0;c<3;c++)data[i+c]=clamp(data[i+c]*(1-skinWeight)+target[c]*(l/170)*skinWeight);}
    // Cabelo escuro acima dos ombros; evita olhos e roupas.
    const eyeRegion=y>.066&&y<.14&&x>.405&&x<.595;
    if(style!=='raspado'&&y<.205&&!eyeRegion&&l<100){const weight=Math.min(1,(100-l)/30);for(let c=0;c<3;c++)data[i+c]=clamp(data[i+c]*(1-weight)+(hairTarget[c]*(.65+l/100)+l*.22)*weight);}
   }
   ctx.putImageData(pixels,0,0);
   if(cleanBase&&smoothPixels){
    // Corpo liso completo evita emendas nas regiões onde havia tecido na foto.
    const head=document.createElement('canvas');head.width=1024;head.height=1536;const headCtx=head.getContext('2d');
    headCtx.drawImage(canvas,female?112:82,0,female?800:860,1536);
    headCtx.globalCompositeOperation='destination-in';const fade=headCtx.createLinearGradient(0,240,0,305);fade.addColorStop(0,'white');fade.addColorStop(1,'transparent');headCtx.fillStyle=fade;headCtx.fillRect(0,0,1024,305);headCtx.clearRect(0,305,1024,1231);
    const donor=document.createElement('canvas');donor.width=1024;donor.height=1536;const donorCtx=donor.getContext('2d');const smoothData=new ImageData(new Uint8ClampedArray(smoothPixels),1024,1536);
    for(let i=0;i<smoothData.data.length;i+=4){const l=(.2126*smoothData.data[i]+.7152*smoothData.data[i+1]+.0722*smoothData.data[i+2])/190;for(let c=0;c<3;c++)smoothData.data[i+c]=clamp(target[c]*l);}
    donorCtx.putImageData(smoothData,0,0);donorCtx.clearRect(0,0,1024,248);
    ctx.clearRect(0,0,1024,1536);ctx.drawImage(donor,51.2,0,921.6,1536);ctx.drawImage(head,0,0);
   }
   const url=canvas.toDataURL('image/png');renderedBodies.set(key,url);if(renderedBodies.size>12)renderedBodies.delete(renderedBodies.keys().next().value);if(!cancelled)setResult({key,url});
  };loadAtlas(source).then(render).catch(()=>{if(!cancelled)setResult({key,url:`/assets/avatar-humano-${gender}-v2.png`,failed:true});});
  return()=>{cancelled=true;};
 },[source,style,skin,hair,key,gender,female,cleanBase]);
 const ready=result?.key===key,compatible=result?.key?.startsWith(source)&&result.key.endsWith('|'+cleanBase);
 return <image data-layer="neutral-mannequin" data-realistic-body="true" data-avatar-gender={gender} data-base-clothes={cleanBase?'removed':'neutral'} opacity={cleanBase&&!ready&&!compatible?0:1} data-skin-tone={skin} data-hair-style={style} data-hair-color={hair} data-personalization-ready={ready&&!result.failed?'true':'false'} href={ready||compatible?result.url:`/assets/avatar-humano-${gender}-v2.png`} x={cleanBase?0:female?112:82} width={cleanBase?1024:female?800:860} height="1536" preserveAspectRatio="none"/>;
}

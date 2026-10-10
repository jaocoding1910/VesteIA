import {useEffect,useState} from 'react';
import {smoothBody} from './smoothAvatarSource';
export default function SmoothAvatarBody({gender,filter,mask,tint=false}){
 const [result,setResult]=useState(null);
 useEffect(()=>{let alive=true;smoothBody(gender).then(body=>{if(alive)setResult({gender,url:body.url});}).catch(()=>{if(alive)setResult({gender,failed:true});});return()=>{alive=false;};},[gender]);
 if(result?.gender!==gender||result.failed)return null;
 return <image data-layer={tint?'skin-tint':'neutral-mannequin'} data-avatar-gender={gender} data-base-clothes="removed" data-personalization-ready="true" href={result.url} x="0" y="0" width="1024" height="1536" filter={filter} mask={mask} preserveAspectRatio="none"/>;
}

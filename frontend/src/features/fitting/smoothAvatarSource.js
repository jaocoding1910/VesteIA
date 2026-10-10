let imagePromise;
const bodies=new Map();
function loadAtlas(){return imagePromise||(imagePromise=new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=reject;img.src='/assets/manequins-base-lisa.png';}));}
export function smoothBody(gender){
 if(bodies.has(gender))return bodies.get(gender);
 const promise=loadAtlas().then(img=>{
  const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=1536;const ctx=canvas.getContext('2d',{willReadFrequently:true});
  ctx.drawImage(img,gender==='feminino'?img.width/2:0,0,img.width/2,img.height,0,0,1024,1536);
  const scan=ctx.getImageData(0,0,1024,1536).data;let left=1024,right=0;
  for(let y=350;y<1300;y++)for(let x=0;x<1024;x++)if(scan[(y*1024+x)*4+3]>220){left=Math.min(left,x);right=Math.max(right,x);}
  const offset=512-(left+right)/2,copy=document.createElement('canvas');copy.width=1024;copy.height=1536;copy.getContext('2d').drawImage(canvas,0,0);ctx.clearRect(0,0,1024,1536);ctx.drawImage(copy,offset,0);
  return {canvas,url:canvas.toDataURL('image/png')};
 });bodies.set(gender,promise);return promise;
}

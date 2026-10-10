import assert from 'node:assert/strict';
import {affineTriangle,clothMesh} from '../src/features/fitting/clothMesh.js';
const src=[[1,2],[6,2],[1,9]],dst=[[3,5],[15,7],[-1,20]],matrix=affineTriangle(src,dst);
for(let i=0;i<3;i++){const [x,y]=src[i],[a,b,c,d,e,f]=matrix;assert.ok(Math.abs(a*x+c*y+e-dst[i][0])<1e-9);assert.ok(Math.abs(b*x+d*y+f-dst[i][1])<1e-9);}
const dimensions={x:1,y:1,sleeve:1,shoulder:1,hem:1,waist:1,hip:1},box=[288,270,448,425];
const model={category:'camiseta',dimensions},a=clothMesh(model,box),b=clothMesh({...model,dimensions:{...dimensions,sleeve:1.4}},box);
assert.equal(a.length,60);assert.notDeepEqual(a,b);assert.deepEqual(a[0].source,b[0].source);
for(const t of b){assert.ok(t.matrix.every(Number.isFinite));for(let i=0;i<3;i++){const [x,y]=t.source[i],[a,b,c,d,e,f]=t.matrix;assert.ok(Math.abs(a*x+c*y+e-t.target[i][0])<1e-7);assert.ok(Math.abs(b*x+d*y+f-t.target[i][1])<1e-7);}}
const pants={category:'calca',dimensions};assert.notDeepEqual(clothMesh(pants,box),clothMesh({...pants,dimensions:{...dimensions,waist:1.2,hip:1.3,hem:.8}},box));
assert.deepEqual(dimensions,{x:1,y:1,sleeve:1,shoulder:1,hem:1,waist:1,hip:1});
console.log('PASS malha: transformação exata dos vértices, manga/cintura/quadril/barra independentes, dados preservados.');

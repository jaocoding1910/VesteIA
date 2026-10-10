import assert from 'node:assert/strict';
import {addToLook,toggleLook} from '../src/features/fitting/lookRules.js';
const item=c=>({product:{id:c,categoria:c},ativo:true});
let look=[];for(const c of ['camiseta','short','calcado','bone'])look=addToLook(look,item(c));assert.equal(look.length,4);
look=addToLook(look,item('calca'));assert.deepEqual(look.map(i=>i.product.categoria),['camiseta','calcado','bone','calca']);
look=addToLook(look,item('vestido'));assert.deepEqual(look.map(i=>i.product.categoria),['calcado','bone','vestido']);
look=addToLook(look,{...item('saia'),ativo:false});look=toggleLook(look,'saia');assert.equal(look.find(i=>i.product.id==='vestido').ativo,false);assert.equal(look.find(i=>i.product.id==='bone').ativo,true);
console.log('PASS: look completo, substituição de regiões e preservação de calçado/boné.');

let layered=addToLook([item('camiseta'),item('calca')],item('casaco'));assert.equal(layered.length,3);layered=addToLook(layered,item('jaqueta'));assert.deepEqual(layered.map(i=>i.product.categoria),['camiseta','calca','jaqueta']);

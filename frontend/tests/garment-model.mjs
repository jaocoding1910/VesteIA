import assert from 'node:assert/strict'
import {garmentDimensions,garmentVisualModel,selectedGarments} from '../src/features/fitting/garmentModel.js'
const make=(category='camiseta',m={largura_cm:52,comprimento_cm:70})=>({product:{id:category,categoria:category,metadata:{visual:{estampa_texto:'VesteIA'}}},variant:{id:2,sku:'fabricante-sku',metadata:{cor_hex:'#234567',visual:{estampa_url:'/assets/vsi.svg'}}},size:{label:'grade própria',medidas:m}})
const item=make(),fixed=structuredClone(item),tight=garmentDimensions({...item,fit:'justo'}),large=garmentDimensions({...item,fit:'oversized'})
assert.ok(large.x>tight.x*1.2);assert.ok(large.y>tight.y);assert.deepEqual(item,fixed)
const model=garmentVisualModel(item);assert.equal(model.sku,'fabricante-sku');assert.equal(model.appearance.printText,'VesteIA');assert.equal(model.appearance.printUrl,'/assets/vsi.svg');assert.equal(model.size,'grade própria')
assert.equal(garmentDimensions(make('calca',{cintura_cm:80,quadril_cm:100,comprimento_cm:105})).width,50)
assert.deepEqual(selectedGarments({...make('vestido'),look:[{...item,ativo:true},{...make('calca'),ativo:true}]}).map(i=>i.product.categoria),['vestido'])
assert.equal(selectedGarments({...item,showProduct:false,look:[]}).length,0)
assert.deepEqual(selectedGarments({...make('calcado'),look:[{...item,ativo:true},{...make('calca'),ativo:true}]}).map(i=>i.product.categoria),['calcado','calca','camiseta'])
console.log('PASS modelo visual: caimento, SKU, estampas mescladas, medidas, famílias/regiões e grades independentes.')

// Calibração do asset é independente da etiqueta e pertence ao produto/variante.
const calibrated=make('camiseta',{largura_cm:60,comprimento_cm:80});calibrated.variant.metadata.visual.medidas_referencia={largura_cm:60,comprimento_cm:80};assert.equal(garmentDimensions(calibrated).x,1);assert.equal(garmentDimensions(calibrated).y,1);

import assert from 'node:assert/strict'
import {createServer} from 'vite'
import {chromium} from 'playwright'
import {mkdir} from 'node:fs/promises'
import {garmentDimensions,selectedGarments,garmentAppearance} from '../src/features/fitting/garmentModel.js'
const categories=['camiseta','calca','short','saia','vestido','calcado','bone']
const table={camiseta:[[48,68],[52,70],[56,72],[60,74]],calca:[[38,100],[40,102],[42,104],[46,108]],short:[[36,44],[39,46],[42,48],[45,50]],saia:[[32,70],[35,72],[38,74],[44,78]],vestido:[[44,105],[48,108],[52,111],[56,114]],calcado:[[8.5,23],[9,25],[9.5,26.5],[10,27.9]],bone:[[17,11],[18,12],[19,13],[20,14]]}
const products=categories.map((categoria,n)=>({id:101+n,nome:`Teste ${categoria}`,categoria,metadata:{publico:['saia','vestido'].includes(categoria)?'feminino':'unissex'},variantes:['Preto','Violeta'].map((cor,v)=>({id:201+n*10+v,cor,preco:100,modelagem:'regular',imagem_url:categoria==='camiseta'&&v===0?'/assets/camiseta-oversized.jpeg':null,metadata:{cor_hex:v?'#9659bd':'#23252b',...(v===1&&categoria==='camiseta'?{visual:{roupa_png_url:'/assets/roupa-inexistente-teste.png',estampa_texto:'VSI',estampa_cor:'#ffffff',estampa_url:'/assets/estampa-inexistente-teste.png'}}:{})},tamanhos:table[categoria].map(([largura,comprimento],i)=>({id:1000+n*100+v*10+i,label:['P','M','G','GG'][i],sort_order:i,estoque:12,medidas:categoria==='calcado'?{pe_cm:comprimento,largura_cm:largura}:{largura_cm:largura,comprimento_cm:comprimento}}))}))}))
for(const product of products){const variant=product.variantes[0],small=garmentDimensions({product,variant,size:variant.tamanhos[0]}),big=garmentDimensions({product,variant,size:variant.tamanhos[3]});assert.ok(big.x>small.x);assert.ok(big.y>small.y)}
const item=(n)=>({ativo:true,product:products[n],variant:products[n].variantes[0],size:products[n].variantes[0].tamanhos[0]})
assert.deepEqual(selectedGarments({...item(4),look:[item(0),item(1)]}).map(i=>i.product.categoria),['vestido'])
assert.equal(garmentAppearance(item(0)).textureUrl,'/assets/camiseta-oversized.jpeg')
const server=await createServer({server:{port:5193,strictPort:true,host:'127.0.0.1'}});let browser
await server.listen();await mkdir('../docs/screenshots',{recursive:true})
try{
 browser=await chromium.launch({headless:true,...(process.env.TEST_BROWSER_EXECUTABLE?{executablePath:process.env.TEST_BROWSER_EXECUTABLE}:{}),args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1440,height:1100}});const errors=[];page.on('pageerror',e=>errors.push(e.message))
 await page.route('http://127.0.0.1:8000/**',route=>route.fulfill({status:200,contentType:'application/json',headers:{'Access-Control-Allow-Origin':'*'},body:JSON.stringify({produtos:products})}))
 await page.goto('http://127.0.0.1:5193/#produto/101');await page.locator('.size-card').first().waitFor()
 const assertLayers=async expected=>{const actual=await page.locator('.size-card').first().locator('[data-layer^="garment-"]').evaluateAll(nodes=>[...new Set(nodes.map(n=>n.dataset.layer.replace('garment-','')))].sort());assert.deepEqual(actual,[...expected].sort())}
 for(const [n,category] of categories.entries()){
  await page.goto(`http://127.0.0.1:5193/#produto/${101+n}`);await page.locator('.size-card').first().waitFor();await assertLayers([category]);
  for(const gender of ['masculino','feminino']){await page.getByLabel('Modelo do avatar').selectOption(gender);await assertLayers([category]);assert.equal(await page.locator('.size-card').first().locator('[data-layer="neutral-mannequin"]').first().getAttribute('data-avatar-gender'),gender)}
  const widths=await page.locator('.size-card').evaluateAll(cards=>cards.map(c=>Number(c.querySelector('[data-layer^="garment-"]').dataset.scaleX)));assert.ok(widths[3]>widths[0]*1.08,`${category}: largura visível varia`)
  assert.ok(await page.locator('.avatar-stage').first().evaluate(stage=>stage.querySelector('svg').getBoundingClientRect().height<=stage.clientHeight+1),'Manequim inteiro cabe no quadro')
  const base=await page.locator('.size-card [data-layer="neutral-mannequin"]').evaluateAll(nodes=>nodes.map(n=>n.getBoundingClientRect().width));assert.ok(base.every(w=>Math.abs(w-base[0])<.1))

 }
 await page.goto('http://127.0.0.1:5193/#produto/101');await page.locator('.size-card').first().waitFor();assert.equal(await page.locator('.size-card').filter({has:page.locator('[data-visual="product-texture"]')}).count(),4)
 await page.screenshot({path:'../docs/screenshots/camiseta-estampa-tamanhos.png',fullPage:true})
 await page.getByLabel('Enquadramento').selectOption('detail');assert.equal(new Set(await page.locator('.size-card .avatar-stage>svg').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('viewBox')))).size,1);await page.screenshot({path:'../docs/screenshots/camiseta-detalhe.png',fullPage:true});await page.getByLabel('Enquadramento').selectOption('full')
 await page.getByRole('button',{name:'Cor Violeta',exact:true}).click();assert.equal(await page.locator('[data-visual="product-texture"]').count(),0);assert.equal(await page.locator('[data-visual="print-text"]').first().textContent(),'VSI');assert.equal(await page.locator('.size-card').filter({has:page.locator('[data-visual="print-text"]')}).count(),4);await page.waitForFunction(()=>document.querySelectorAll('[data-visual="print-image"]').length===0)
 await page.getByRole('button',{name:'Adicionar ao look',exact:true}).click()
 await page.goto('http://127.0.0.1:5193/#produto/103');await page.locator('.size-card').first().waitFor();await assertLayers(['short'])
 await page.getByRole('button',{name:'Look completo',exact:true}).click();await assertLayers(['camiseta','short'])
 await page.getByRole('button',{name:'Base neutra',exact:true}).click();await assertLayers([])
 await page.getByRole('button',{name:'Peça isolada',exact:true}).click();await assertLayers(['short'])
 await page.getByLabel('Modelo do avatar').selectOption('feminino');await page.screenshot({path:'../docs/screenshots/bermuda-peca-unica.png',fullPage:true})
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:'../docs/screenshots/peca-unica-mobile.png',fullPage:true})
 await page.getByRole('tab',{name:'Pontos e proporções',exact:true}).click();assert.ok(await page.locator('[data-layer="avatar-guides"]').count());await assertLayers(['short']);await page.screenshot({path:'../docs/screenshots/final-mobile-pontos.png',fullPage:true});await page.getByRole('tab',{name:'Visual natural',exact:true}).click();assert.equal(await page.locator('[data-layer="avatar-guides"]').count(),0);
 assert.deepEqual(errors,[]);console.log('PASS: sete categorias isoladas, largura por SKU, corpo fixo, foto com estampa, VSI/cor por variante, look, base neutra, gênero, e mobile sem overflow. API simulada para testar apenas frontend.')
}finally{await browser?.close();await server.close()}

import {chromium} from 'playwright';
import {createServer} from 'vite';
import assert from 'node:assert/strict';
const server=await createServer({server:{port:5173,strictPort:true,host:'127.0.0.1'}});await server.listen();
const browser=await chromium.launch({headless:true,executablePath:process.env.TEST_BROWSER_EXECUTABLE,args:['--no-sandbox']});
const page=await browser.newPage({viewport:{width:1500,height:1100}});page.setDefaultTimeout(15000);
const errors=[];page.on('pageerror',e=>errors.push(e.message));
const output='../docs/screenshots/';
try{
 const {produtos}=await(await fetch('http://127.0.0.1:8000/mvp/catalogo')).json();assert.ok(produtos.length>=7);
 const product=category=>produtos.find(p=>p.categoria===category);
 for(const category of ['camiseta','short','calcado','bone']){await page.goto(`http://127.0.0.1:5173/#produto/${product(category).id}`);await page.locator('.size-card').first().waitFor();await page.getByRole('button',{name:'Adicionar ao look',exact:true}).click();}
 await page.goto(`http://127.0.0.1:5173/#produto/${product('camiseta').id}`);await page.locator('.size-card').first().waitFor();await page.getByRole('button',{name:'Look completo',exact:true}).click();
 const layers=()=>page.locator('.size-card').first().locator('[data-layer^="garment-"]').evaluateAll(nodes=>[...new Set(nodes.map(n=>n.dataset.layer))].sort());
 assert.deepEqual(await layers(),['garment-bone','garment-calcado','garment-camiseta','garment-short']);
 await page.screenshot({path:output+'final-look-natural.png',fullPage:true});
 const body=await page.locator('[data-body-transform]').first().getAttribute('data-body-transform');await page.getByRole('tab',{name:'Pontos e proporções',exact:true}).click();assert.equal(await page.locator('[data-body-transform]').first().getAttribute('data-body-transform'),body);assert.ok(await page.locator('[data-layer="avatar-guides"]').count());assert.equal((await layers()).length,4);
 await page.screenshot({path:output+'final-look-pontos.png',fullPage:true});await page.locator('.comparison-grid').screenshot({path:output+'final-look-pontos-detalhe.png'});
 await page.getByRole('tab',{name:'Visual natural',exact:true}).click();await page.locator('.comparison-grid').screenshot({path:output+'final-look-natural-detalhe.png'});
 await page.goto(`http://127.0.0.1:5173/#produto/${product('saia').id}`);await page.locator('.size-card').first().waitFor();await page.getByLabel('Modelo do avatar').selectOption('feminino');assert.deepEqual(await layers(),['garment-saia']);await page.screenshot({path:output+'final-saia-isolada.png',fullPage:true});
 await page.getByRole('tab',{name:'Pontos e proporções',exact:true}).click();await page.getByRole('button',{name:'Criar meu avatar',exact:true}).click();await page.locator('dialog').getByRole('tab',{name:'Pontos e proporções',exact:true}).click();assert.ok(await page.locator('dialog [data-layer="avatar-guides"]').count());await page.locator('dialog').screenshot({path:output+'final-editor-pontos.png'});await page.keyboard.press('Escape');
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:output+'final-mobile.png',fullPage:true});assert.deepEqual(errors,[]);
 console.log('PASS catálogo real com sete categorias, look camiseta/bermuda/tênis/boné, abas sem trocar corpo/roupas, saia isolada, editor e mobile.');
}finally{await browser.close();await server.close();}

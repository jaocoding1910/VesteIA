import assert from 'node:assert/strict';
import {createServer} from 'vite';
import {chromium} from 'playwright';
import {mkdir} from 'node:fs/promises';
const product={id:301,nome:'Camiseta VesteIA',categoria:'camiseta',metadata:{},variantes:[{id:302,cor:'Preto',preco:100,modelagem:'regular',metadata:{cor_hex:'#18191b',visual:{roupa_genero_urls:{masculino:'/assets/roupa-real-camiseta-masculino.svg',feminino:'/assets/roupa-real-camiseta-feminino.svg'},textura_url:false}},tamanhos:[{id:303,label:'M',sort_order:0,estoque:10,medidas:{largura_cm:52,comprimento_cm:70}}]}]};
const server=await createServer({server:{port:5195,host:'127.0.0.1'}});await server.listen();let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));let saved;
 await page.route('http://127.0.0.1:8000/**',async r=>{const req=r.request();if(req.method()==='PUT')saved=req.postDataJSON();await r.fulfill({contentType:'application/json',headers:{'Access-Control-Allow-Origin':'*'},body:JSON.stringify(req.method()==='PUT'?{ok:true}:req.method()==='POST'?{tamanhos:[],recomendacao:null}:{produtos:[product]})});});
 await page.goto('http://127.0.0.1:5195/#produto/301');await page.locator('.size-card').waitFor();await page.getByRole('button',{name:'Criar meu avatar',exact:true}).click();const dialog=page.locator('dialog');
 const ready=()=>page.waitForFunction(()=>[...document.querySelectorAll('dialog [data-realistic-body="true"]')].every(n=>n.dataset.personalizationReady==='true'));
 const image=()=>dialog.locator('[data-realistic-body="true"]').first().getAttribute('href');
 await ready();const before=await image();await dialog.getByRole('button',{name:'Tom de pele #4f3025',exact:true}).click();await ready();assert.notEqual(await image(),before);
 for(const gender of ['Masculino','Feminino']){
  await dialog.getByRole('button',{name:gender,exact:true}).click();const hashes=new Set();
  for(const style of ['raspado','curto','crespo','longo']){await dialog.getByLabel('Cabelo',{exact:true}).selectOption(style);await ready();hashes.add(await image());assert.equal(await dialog.locator('[data-realistic-body="true"]').first().getAttribute('data-hair-style'),style);}
  assert.equal(hashes.size,4);
 }
 await dialog.getByLabel('Cabelo',{exact:true}).selectOption('crespo');await ready();const dark=await image();await dialog.getByLabel('Cor do cabelo',{exact:true}).fill('#a04a26');await ready();assert.notEqual(await image(),dark);await dialog.getByLabel('Cor do cabelo',{exact:true}).fill('#292018');await ready();
 await mkdir('../docs/screenshots',{recursive:true});await dialog.screenshot({path:'../docs/screenshots/personalizacao-feminino-crespo.png'});
 await dialog.getByRole('button',{name:'Salvar meu avatar',exact:true}).click();await page.locator('dialog').waitFor({state:'hidden'});assert.equal(saved.estilo_cabelo,'crespo');assert.equal(saved.tom_pele,'#4f3025');
 await page.reload();await page.locator('.size-card').waitFor();await page.waitForFunction(()=>document.querySelector('[data-realistic-body="true"]')?.dataset.personalizationReady==='true');assert.equal(await page.locator('[data-realistic-body="true"]').first().getAttribute('data-hair-style'),'crespo');
 await page.locator('.comparison-grid').screenshot({path:'../docs/screenshots/personalizacao-caimento.png'});
 await page.getByRole('button',{name:'Editar meu avatar',exact:true}).click();await dialog.getByRole('button',{name:'Masculino',exact:true}).click();await dialog.getByRole('button',{name:'Tom de pele #b87d57',exact:true}).click();await dialog.getByLabel('Cabelo',{exact:true}).selectOption('curto');await ready();await dialog.screenshot({path:'../docs/screenshots/personalizacao-masculino-curto.png'});
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[]);
 console.log('PASS: ambos gêneros, quatro cabelos, paleta pele/cabelo visivelmente diferente, salvar payload e recarregar, peça e mobile. API simulada.');
}finally{await browser?.close();await server.close();}

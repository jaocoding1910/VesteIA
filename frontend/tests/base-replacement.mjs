import assert from 'node:assert/strict';
import {createServer} from 'vite';
import {chromium} from 'playwright';
const cats=['camiseta','calca','short','saia','vestido','calcado','bone'];
const products=cats.map((categoria,i)=>({id:400+i,nome:`Peça ${categoria}`,categoria,metadata:{},variantes:[{id:500+i,cor:'Preto',preco:100,modelagem:'regular',metadata:{cor_hex:'#18191b',visual:{roupa_genero_urls:['camiseta','calca'].includes(categoria)?{masculino:`/assets/roupa-real-${categoria}-masculino.svg`,feminino:`/assets/roupa-real-${categoria}-feminino.svg`}:{},textura_url:false}},tamanhos:[{id:600+i,label:'M',estoque:10,sort_order:0,medidas:{largura_cm:categoria==='calca'?40:52,comprimento_cm:{camiseta:70,calca:104,short:46,saia:74,vestido:108,calcado:26,bone:12}[categoria]}}]}]}));
const server=await createServer({server:{port:5196,host:'127.0.0.1'}});await server.listen();let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://127.0.0.1:8000/**',r=>r.fulfill({contentType:'application/json',headers:{'Access-Control-Allow-Origin':'*'},body:JSON.stringify(r.request().method()==='PUT'?{ok:true}:r.request().method()==='POST'?{tamanhos:[],recomendacao:null}:{produtos:products})}));
 const ready=()=>page.waitForFunction(()=>[...document.querySelectorAll('.size-card [data-realistic-body="true"]')].length>0&&[...document.querySelectorAll('.size-card [data-realistic-body="true"]')].every(n=>n.dataset.personalizationReady==='true'));
 for(const gender of ['masculino','feminino'])for(const [i,category]of cats.entries()){
  await page.goto(`http://127.0.0.1:5196/#produto/${400+i}`);await page.locator('.size-card').waitFor();await page.getByLabel('Modelo do avatar').selectOption(gender);await ready();
  assert.equal(await page.locator('[data-realistic-body="true"]').first().getAttribute('data-base-clothes'),'removed');
  const layers=await page.locator('.size-card [data-layer^="garment-"]').evaluateAll(nodes=>[...new Set(nodes.map(n=>n.dataset.layer))]);assert.deepEqual(layers,[`garment-${category}`]);
  if(['camiseta','calca'].includes(category))await page.locator('.size-card .avatar-natural').screenshot({path:`../docs/screenshots/base-limpa-${gender}-${category}.png`});
 }
 await page.goto('http://127.0.0.1:5196/#produto/400');await ready();await page.getByRole('button',{name:'Base neutra',exact:true}).click();await ready();assert.equal(await page.locator('[data-realistic-body="true"]').first().getAttribute('data-base-clothes'),'neutral');assert.equal(await page.locator('[data-layer^="garment-"]').count(),0);
 await page.getByRole('button',{name:'Peça isolada',exact:true}).click();await ready();assert.equal(await page.locator('[data-realistic-body="true"]').first().getAttribute('data-base-clothes'),'removed');
 await page.getByRole('button',{name:'Adicionar ao look',exact:true}).click();await page.goto('http://127.0.0.1:5196/#produto/401');await ready();await page.getByRole('button',{name:'Look completo',exact:true}).click();assert.equal(await page.locator('[data-layer^="garment-"]').evaluateAll(nodes=>new Set(nodes.map(n=>n.dataset.layer)).size),2);
 await page.getByRole('button',{name:'Criar meu avatar',exact:true}).click();await page.getByLabel('Acabamento do avatar').selectOption('manequim');await page.getByRole('button',{name:'Salvar meu avatar',exact:true}).click();await page.locator('dialog').waitFor({state:'hidden'});await page.waitForFunction(()=>document.querySelector('.size-card [data-layer="neutral-mannequin"]')?.dataset.baseClothes==='removed');await page.locator('.size-card .avatar-natural').screenshot({path:'../docs/screenshots/base-limpa-manequim.png'});
 assert.deepEqual(errors,[]);console.log('PASS: sete categorias x dois gêneros, base sem roupa esportiva, peça isolada, restauração da base e look explícito. API simulada.');
}finally{await browser?.close();await server.close();}

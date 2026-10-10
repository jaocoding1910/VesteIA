import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createServer} from 'vite';
import {chromium} from 'playwright';
import {validSelection,PROTOCOL,parseEmbed} from '../src/features/integration/embedProtocol.js';
const products=JSON.parse(await readFile('../docs/catalogo-loja-forma.json')).produtos.map((p,i)=>({...p,id:100+i,variantes:p.variantes.map((v,j)=>({...v,id:200+i*10+j,tamanhos:v.tamanhos.map((s,k)=>({...s,id:300+i*10+k}))}))}));
const p=products[0],v=p.variantes[0],s=v.tamanhos[0],message={protocol:PROTOCOL,type:'selection',channel:'test',productId:p.id,variantId:v.id,sizeId:s.id};
assert.ok(validSelection(message,p,'test'));assert.equal(validSelection(message,p,'other'),null);assert.equal(validSelection({...message,sizeId:99999},p,'test'),null);assert.equal(parseEmbed('#inicio'),null);
const server=await createServer({server:{port:5200,strictPort:true,host:'127.0.0.1'}});await server.listen();let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});const context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await context.route('http://127.0.0.1:8000/**',r=>r.fulfill({contentType:'application/json',headers:{'Access-Control-Allow-Origin':'*'},body:JSON.stringify(r.request().method==='POST'?{tamanhos:[],recomendacao:null}:{produtos:products})}));
 await mkdir('../docs/screenshots',{recursive:true});await page.goto('http://127.0.0.1:5200/#loja');await page.locator('.demo-store-grid article').first().waitFor();assert.equal(await page.locator('.demo-store-grid article').count(),4);await page.screenshot({path:'../docs/screenshots/loja-colecao.png',fullPage:true});
 for(const product of products){
  await page.getByRole('button',{name:`Abrir ${product.nome} na loja`,exact:true}).click();await page.getByRole('button',{name:'Escolher tamanho M',exact:true}).click();await page.getByRole('button',{name:'Experimentar com VesteIA',exact:true}).click();const frame=page.frameLocator('iframe');await frame.getByRole('button',{name:'Usar este tamanho na loja',exact:true}).waitFor();
  await frame.getByRole('button',{name:'Selecionar tamanho G',exact:true}).click();
  if(product===products[0]){await page.waitForTimeout(700);await page.screenshot({path:'../docs/screenshots/loja-provador.png',fullPage:true});}
  await frame.getByRole('button',{name:'Usar este tamanho na loja',exact:true}).click();await page.locator('iframe').waitFor({state:'detached'});assert.equal(await page.getByRole('button',{name:'Escolher tamanho G',exact:true}).getAttribute('aria-pressed'),'true');await page.getByRole('status').filter({hasText:'Escolha aplicada: G'}).waitFor();await page.getByRole('button',{name:'Voltar à coleção',exact:false}).click();
 }
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:'../docs/screenshots/loja-mobile.png',fullPage:true});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.getByRole('button',{name:`Abrir ${products[3].nome} na loja`,exact:true}).click();await page.getByRole('button',{name:'Experimentar com VesteIA',exact:true}).click();await page.frameLocator('iframe').getByRole('button',{name:'Usar este tamanho na loja',exact:true}).waitFor();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[]);console.log('PASS: quatro produtos, iframe, seleção G retornada, protocolo, layout móvel. API simulada.');
}finally{await browser?.close();await server.close();}

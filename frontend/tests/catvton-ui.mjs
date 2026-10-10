import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createServer} from 'vite';
import {chromium} from 'playwright';
const products=JSON.parse(await readFile('../docs/catalogo-loja-forma.json')).produtos.map((p,i)=>({...p,id:100+i,variantes:p.variantes.map((v,j)=>({...v,id:200+i*10+j,tamanhos:v.tamanhos.map((s,k)=>({...s,id:300+i*10+k}))}))}));
const male=await readFile('public/assets/tryon/base-masculino.jpg'),female=await readFile('public/assets/tryon/base-feminino.jpg');
const server=await createServer({server:{port:5206,strictPort:true,host:'127.0.0.1'}});await server.listen();let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1300,height:1100}});let ready=false,calls=0,errors=[],payloads=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://127.0.0.1:8000/**',async route=>{const url=route.request().url();let body;
 if(url.endsWith('/ia/status'))body={configured:ready,provider:'catvton',categories:['camiseta','calca','short','vestido'],message:ready?'Pronto para solicitar uma prévia.':'Abra INICIAR_IA_LOCAL.bat e aguarde o CatVTON ficar pronto.'};
 else if(url.endsWith('/ia/previa')){calls++;payloads.push(route.request().postDataBuffer());body={image:'data:image/jpeg;base64,'+male.toString('base64'),provider:'catvton'};}
 else body=route.request().method()==='POST'?{tamanhos:[],recomendacao:null}:{produtos:products};
 await route.fulfill({contentType:'application/json',headers:{'Access-Control-Allow-Origin':'*'},body:JSON.stringify(body)});
 });
 await page.goto('http://127.0.0.1:5206/#produto/100');await page.locator('.ai-tryon summary').click();
 assert.equal(await page.getByRole('button',{name:'Gerar prévia realista',exact:true}).isDisabled(),true);
 assert.ok(await page.getByRole('radio',{name:'Base fotográfica',exact:true}).isChecked());
 ready=true;await page.reload();await page.locator('.ai-tryon summary').click();await page.getByText('Pronto para solicitar uma prévia.',{exact:true}).waitFor();
 await page.locator('.ai-photo-base select').selectOption('feminino');assert.match(await page.locator('.ai-photo-base img').getAttribute('src'),/feminino/);
 assert.equal(await page.getByRole('button',{name:'Gerar prévia realista',exact:true}).isDisabled(),true);
 await mkdir('../docs/screenshots',{recursive:true});await page.addStyleTag({content:'.site-header{visibility:hidden}'});await page.locator('.ai-tryon').screenshot({path:'../docs/screenshots/catvton-interface.png'});
 await page.getByRole('checkbox',{name:/Autorizo processar/}).check();await page.getByRole('button',{name:'Gerar prévia realista',exact:true}).click();await page.locator('.ai-result img').waitFor();assert.equal(calls,1);
 assert.ok(payloads[0].length>female.length/2);assert.ok(payloads[0].includes(Buffer.from('name="product_id"')));assert.ok(payloads[0].includes(Buffer.from('name="garment"')));
 await page.getByRole('button',{name:'Selecionar tamanho G',exact:true}).click();assert.equal(calls,1);
 await page.locator('.ai-photo-base select').selectOption('masculino');assert.equal(await page.locator('.ai-result').count(),0);
 assert.equal(await page.getByRole('checkbox',{name:/Autorizo processar/}).isChecked(),false);
 await page.getByRole('radio',{name:'Minha foto',exact:true}).check();await page.locator('.ai-inputs input[type=file]').first().setInputFiles({name:'foto.jpg',mimeType:'image/jpeg',buffer:male});await page.getByRole('checkbox',{name:/Autorizo processar/}).check();await page.getByRole('button',{name:'Gerar prévia realista',exact:true}).click();await page.locator('.ai-result img').waitFor();assert.equal(calls,2);
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[]);
 console.log('PASS CatVTON UI: readiness, two photo bases, catalog multipart, consent, photo upload, invalidation, sizes without regeneration, mobile. Inference response mocked. Screenshot contains input base only.');
}finally{await browser?.close();await server.close();}

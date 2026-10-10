// Teste de ponta a ponta do provador com RESPOSTAS SIMULADAS (sem custo).
// Pré-requisitos: backend com AVATAR_PROVIDER=mock e TRYON_PROVIDER=mock; frontend em VESTEIA_URL.
//   PowerShell:  $env:VESTEIA_URL="http://127.0.0.1:5173"; npm run test:studio
// Variáveis opcionais: CHROMIUM_PATH (executável do Chromium), SHOTS_DIR (pasta para capturas de tela).
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const URL_BASE = process.env.VESTEIA_URL || 'http://127.0.0.1:5173';
const SHOTS = process.env.SHOTS_DIR || '';
const asset = name => join(here, '..', 'public', 'assets', 'experience', name);
const fixture = name => join(here, 'fixtures', name);
if (SHOTS) mkdirSync(SHOTS, { recursive: true });

let failures = 0;
const check = (ok, message) => { console.log(`${ok ? '✔' : '✘'} ${message}`); if (!ok) failures += 1; };
const shot = async (page, name) => { if (SHOTS) await page.screenshot({ path: join(SHOTS, `${name}.png`), fullPage: true }); };
const noHorizontalScroll = page => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
try {
  // ---------- Homepage ----------
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 900 } });
  const page = await ctx.newPage();
  const requests = [];
  page.on('request', r => requests.push(`${r.method()} ${new URL(r.url()).pathname}`));
  const consoleErrors = [];
  page.on('pageerror', e => consoleErrors.push(e.message));
  await page.goto(URL_BASE + '/#inicio');
  await page.waitForSelector('h1#hero-title');
  check(await page.locator('h1#hero-title').innerText().then(t => t.includes('Veja a roupa')), 'homepage abre sem banco de dados');
  const video = page.locator('#apresentacao-video');
  check(await video.getAttribute('controls') !== null, 'vídeo tem controles');
  check(await video.getAttribute('autoplay') === null, 'vídeo não inicia sozinho');
  check(Boolean(await video.getAttribute('poster')), 'vídeo tem imagem de capa');
  check(await page.locator('text=Exemplo ilustrativo').count() >= 2, 'exemplos estáticos identificados como ilustrativos');
  check(await page.locator('a:has-text("Experimentar com IA")').count() >= 2, 'botão principal "Experimentar com IA"');
  check(await noHorizontalScroll(page), 'homepage sem rolagem horizontal (desktop)');
  await page.locator('#como-funciona').scrollIntoViewIfNeeded();
  await page.waitForTimeout(900);
  await shot(page, '01-home-desktop');
  check(!requests.some(r => r.includes('/mvp/')), 'nenhuma chamada ao catálogo antigo');

  // ---------- Provador ----------
  await page.click('header >> text=Experimentar com IA');
  await page.waitForSelector('#step-title');
  check(await page.locator('text=respostas simuladas').count() > 0, 'modo simulado sinalizado na interface');
  await page.locator('label:has-text("Escolher foto") input[type=file]').setInputFiles(fixture('nao-imagem.jpg'));
  await page.waitForSelector('.notice-error');
  check((await page.locator('.notice-error').innerText()).includes('JPEG, PNG ou WEBP'), 'arquivo inválido recusado com orientação');
  await page.locator('label:has-text("Meio corpo")').click();
  check(await page.locator('text=serão estimadas').count() > 0, 'aviso de regiões estimadas para foto parcial');
  await page.locator('label:has-text("Sem camiseta")').click();
  await page.locator('label:has-text("Escolher foto") input[type=file]').setInputFiles(asset('avatar-base.webp'));
  await page.waitForSelector('.frame__box img');
  await page.waitForFunction(() => !document.querySelector('.spinner'));
  await shot(page, '02-etapa1-foto');
  await page.click('.panel-nav >> text=Continuar');

  await page.locator('label:has-text("Adicionar peças") input[type=file]').setInputFiles([asset('camiseta-preta.webp'), fixture('calca-teste.png')]);
  await page.waitForFunction(() => document.querySelectorAll('.garment-card').length === 2);
  await page.locator('.garment-card input').first().fill('Camiseta preta básica');
  await page.click('.panel-nav >> text=Continuar');

  check(await page.locator('.panel-nav button:has-text("Continuar")').isDisabled(), 'categoria obrigatória antes de continuar');
  const selects = page.locator('.detail-card select');
  await selects.nth(0).selectOption('camiseta');
  await selects.nth(1).selectOption('calca');
  await page.locator('.detail-card').first().locator('.segmented label').filter({ hasText: /^M$/ }).click();
  await page.locator('.detail-card').first().locator('summary:has-text("Medidas da peça")').click();
  const fill = (label, size, value) => page.locator('.detail-card').first().locator(`input[aria-label="${label}, tamanho ${size}"]`).fill(value);
  await fill('Largura do tórax (peça plana)', 'P', '48'); await fill('Largura do tórax (peça plana)', 'M', '52'); await fill('Largura do tórax (peça plana)', 'G', '57');
  await fill('Comprimento', 'P', '68'); await fill('Comprimento', 'M', '71'); await fill('Comprimento', 'G', '74');
  await shot(page, '03-etapa3-categorias');
  await page.click('.panel-nav >> text=Continuar');

  // Etapa 4: consentimento, contagem e bloqueio de clique duplicado.
  const generate = page.locator('button:has-text("Gerar avatar base")');
  check(await generate.isDisabled(), 'geração bloqueada sem consentimento');
  check((await page.locator('.calls').innerText()).includes('1 geração'), 'informa quantas gerações serão solicitadas');
  await page.locator('.consent input').check();
  const before = requests.filter(r => r === 'POST /api/studio/avatar').length;
  await generate.evaluate(button => { button.click(); button.click(); button.click(); });
  await page.waitForSelector('button:has-text("Aprovar este avatar")');
  check(requests.filter(r => r === 'POST /api/studio/avatar').length - before === 1, 'clique triplo gera uma única chamada');
  check(await page.locator('.frame__badge:has-text("SIMULADO")').count() > 0, 'resultado simulado identificado');
  check(await page.locator('text=estimadas').count() > 0, 'avatar informa regiões estimadas');
  await page.waitForTimeout(700);
  await shot(page, '04-etapa4-avatar');
  await page.click('button:has-text("Aprovar este avatar")');

  // Etapa 5
  await page.waitForSelector('text=Peças para vestir');
  check(await page.locator('.look-list li.is-on').count() === 2, 'camiseta e calça no look');
  await page.click('button:has-text("Gerar imagem com as peças")');
  await page.waitForSelector('#tab-before');
  check(await page.locator('figcaption:has-text("Avatar base")').count() === 1 && await page.locator('figcaption:has-text("Com a peça escolhida")').count() === 1, 'antes e depois lado a lado');
  await shot(page, '05-etapa6-antes-depois');

  // Aba de tamanhos não gera nada sozinha.
  const generations = () => requests.filter(r => /POST \/api\/studio\/(avatar|tryon|size-previews)/.test(r)).length;
  const count = generations();
  await page.click('#tab-sizes');
  await page.waitForSelector('.size-card');
  check(generations() === count, 'trocar de aba não dispara geração');
  check(await page.locator('text=Faltam medidas da peça em').count() > 0, 'estado sem medidas sinalizado (GG)');
  await page.locator('summary:has-text("Editar suas medidas")').click();
  await page.locator('.body-grid input').first().fill('100');
  await page.waitForSelector('.readings li');
  check(await page.locator('.readings li').count() >= 3, 'leitura de folga com medidas do cliente');
  await page.click('button:has-text("Gerar prévias de")');
  await page.waitForSelector('dialog.confirm[open]');
  check((await page.locator('dialog.confirm[open]').innerText()).includes('3 gerações'), 'confirmação informa o número de gerações');
  await page.click('dialog.confirm[open] >> text=Cancelar');
  check(generations() === count, 'cancelar não gera');
  await page.click('button:has-text("Gerar prévias de")');
  await page.click('dialog.confirm[open] >> button:has-text("Gerar 3 prévias")');
  await page.waitForFunction(() => document.querySelectorAll('.preview-grid .preview-item').length === 3);
  check(generations() === count + 1, 'prévias de tamanho em uma ação explícita');
  check((await page.locator('.size-head').innerText()).includes('Tamanho escolhido: M'), 'tamanho escolhido respeitado na comparação');
  await page.waitForTimeout(700);
  await shot(page, '06-comparar-tamanhos');

  // Look: remover peça não gera automaticamente.
  await page.click('#tab-before');
  await page.locator('.look-list li.is-on button:has-text("Remover")').first().click();
  check(await page.locator('text=O look mudou').count() > 0, 'look alterado marcado como desatualizado');
  check(generations() === count + 1, 'remover peça não gera automaticamente');

  // Falha do serviço mostrada com clareza (simulada por interceptação).
  await page.route('**/api/studio/tryon', route => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ detail: 'Serviço de teste indisponível.', inconclusive: false, charged_calls: 0 }) }));
  await page.locator('.look-panel .consent input').check().catch(() => {});
  await page.click('button:has-text("Gerar com o look atual")');
  await page.waitForSelector('.notice-error');
  check((await page.locator('.notice-error').innerText()).includes('Serviço de teste indisponível'), 'erro do serviço exibido sem repetição automática');
  await page.unroute('**/api/studio/tryon');

  // Limpar sessão.
  await page.click('button:has-text("Limpar sessão")');
  await page.click('dialog.confirm[open] >> text=Limpar tudo');
  await page.waitForSelector('text=Etapa 1 de 6');
  check(requests.includes('DELETE /api/studio/session'), 'limpar sessão encerra a sessão no servidor');
  check(await page.locator('.frame__box img').count() === 0, 'imagens descartadas');
  check(consoleErrors.length === 0, `sem erros de JavaScript (${consoleErrors.join(' | ')})`);
  await ctx.close();

  // ---------- Celular ----------
  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
  const m = await mobile.newPage();
  await m.goto(URL_BASE + '/#inicio');
  await m.waitForSelector('h1#hero-title');
  check(await noHorizontalScroll(m), 'homepage sem rolagem horizontal (390 px)');
  const hidden = await m.evaluate(() => [...document.querySelectorAll('[data-reveal]')].filter(n => getComputedStyle(n).opacity !== '1').length);
  check(hidden === 0, 'movimento reduzido: conteúdo visível sem animação');
  await shot(m, '07-home-celular');
  await m.goto(URL_BASE + '/#provador');
  await m.waitForSelector('#step-title');
  check(await noHorizontalScroll(m), 'provador sem rolagem horizontal (390 px)');
  await shot(m, '08-provador-celular');
  await mobile.close();

  // ---------- Serviço indisponível ----------
  const off = await browser.newContext();
  const o = await off.newPage();
  await o.route('**/api/studio/status', route => route.abort());
  await o.goto(URL_BASE + '/#provador');
  await o.waitForSelector('text=Serviço indisponível');
  check(true, 'estado de serviço indisponível com opção de tentar novamente');
  await off.close();
} finally {
  await browser.close();
}
console.log(failures ? `\n${failures} verificação(ões) falharam.` : '\nTodas as verificações passaram (respostas simuladas; não avaliam a qualidade real da IA).');
process.exit(failures ? 1 : 0);

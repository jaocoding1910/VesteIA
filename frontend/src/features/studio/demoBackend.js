// Backend SIMULADO que roda no navegador (VITE_DEMO_MODE=true). Usado na prévia navegável.
// Não usa IA nem rede: monta colagens e carimba "SIMULAÇÃO" em todas as imagens.
import { ApiError } from './errors';
import { CATEGORIES, SLOT_FIELDS, composeLook, num, slotOf } from './sizeModel';

const W = 1024, H = 1536;
const REGIONS = { upper: [0.5, 0.2, 0.44, 0.31], outer: [0.5, 0.19, 0.5, 0.36], lower: [0.5, 0.48, 0.34, 0.42], full: [0.5, 0.2, 0.46, 0.6] };
const WIDTH_KEY = { upper: 'largura_cm', outer: 'largura_cm', lower: 'quadril_cm', full: 'busto_cm' };
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

function canvas(w = W, h = H) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}

async function bitmap(blob) {
  return createImageBitmap(blob, { imageOrientation: 'from-image' });
}

function contain(srcW, srcH, boxW, boxH) {
  const r = Math.min(boxW / srcW, boxH / srcH);
  return [srcW * r, srcH * r];
}

function fit(image) {
  const c = canvas(), ctx = c.getContext('2d');
  ctx.fillStyle = '#eef1f8';
  ctx.fillRect(0, 0, W, H);
  const [w, h] = contain(image.width, image.height, W, H);
  ctx.drawImage(image, (W - w) / 2, (H - h) / 2, w, h);
  return c;
}

function cutout(image) {
  const [w, h] = contain(image.width, image.height, 512, 512);
  const c = canvas(Math.round(w), Math.round(h)), ctx = c.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(image, 0, 0, c.width, c.height);
  const data = ctx.getImageData(0, 0, c.width, c.height);
  const px = (x, y) => { const i = (y * c.width + x) * 4; return [data.data[i], data.data[i + 1], data.data[i + 2]]; };
  const corners = [px(2, 2), px(c.width - 3, 2), px(2, c.height - 3), px(c.width - 3, c.height - 3)];
  const bg = [0, 1, 2].map(i => corners.map(p => p[i]).sort((a, b) => a - b)[1]);
  let minX = c.width, minY = c.height, maxX = 0, maxY = 0;
  for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) {
    const i = (y * c.width + x) * 4;
    const d = Math.max(Math.abs(data.data[i] - bg[0]), Math.abs(data.data[i + 1] - bg[1]), Math.abs(data.data[i + 2] - bg[2]));
    if (d > 28) { minX = Math.min(minX, x); minY = Math.min(minY, y); maxX = Math.max(maxX, x); maxY = Math.max(maxY, y); }
    else data.data[i + 3] = 0;
  }
  ctx.putImageData(data, 0, 0);
  if (maxX <= minX || maxY <= minY) return c;
  const out = canvas(maxX - minX + 1, maxY - minY + 1);
  out.getContext('2d').drawImage(c, -minX, -minY);
  return out;
}

function paste(ctx, piece, slot, sx = 1, sy = 1) {
  const [cx, top, rw, rh] = REGIONS[slot];
  const [w, h] = contain(piece.width, piece.height, W * rw, H * rh);
  const fw = w * sx, fh = h * sy, x = W * cx - fw / 2, y = H * top;
  ctx.save();
  ctx.shadowColor = 'rgba(20,20,40,.28)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 8;
  ctx.drawImage(piece, x, y, fw, fh);
  ctx.restore();
}

function stamp(c, title) {
  const ctx = c.getContext('2d'), band = 64;
  ctx.fillStyle = 'rgba(17,24,64,.9)'; ctx.fillRect(0, 0, W, band);
  ctx.fillStyle = 'rgba(124,58,237,.86)'; ctx.fillRect(0, H - band, W, band);
  ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = '600 30px system-ui, sans-serif'; ctx.fillText(title, W / 2, band / 2);
  ctx.font = '500 24px system-ui, sans-serif'; ctx.fillText('Imagem de teste · não representa caimento real', W / 2, H - band / 2);
  return c.toDataURL('image/jpeg', 0.88);
}

export function createDemoBackend() {
  let session = null;
  const LIMIT = 12;
  const caps = {
    avatar: { id: 'mock', label: 'Simulação no navegador (sem IA)', kind: 'simulated', paid: false, ready: true, generates: true, multi_garment: true, size_previews: true, accepts_partial_photo: true, model: null, message: 'Demonstração: respostas SIMULADAS no navegador. Nenhuma foto sai do seu dispositivo.' },
  };
  caps.tryon = { ...caps.avatar };
  const usage = () => ({ sessao: session?.used || 0, limite_sessao: LIMIT, locais_hoje: session?.used || 0, limite_locais_dia: 200, pagas_hoje: 0, limite_pagas_dia: 0, pagas_total: 0, limite_pagas_total: 0 });

  function guard(fields, planned) {
    if (!session) throw new ApiError('Sessão expirada. Recarregue a página.', { status: 401 });
    if (fields.consent !== 'true' && fields.consent !== true) throw new ApiError('É preciso autorizar o processamento das imagens antes de gerar.', { status: 422 });
    if (Number(fields.expected_calls) !== planned) throw new ApiError(`Esta ação solicitará ${planned} geração(ões). Confirme novamente.`, { status: 409 });
    if (session.ids.has(fields.request_id)) throw new ApiError('Solicitação repetida ignorada (clique duplicado).', { status: 409 });
    if (session.busy) throw new ApiError('Já existe uma geração em andamento nesta sessão.', { status: 409 });
    if (session.used + planned > LIMIT) throw new ApiError(`Limite desta sessão atingido (${LIMIT} gerações). Limpe a sessão para recomeçar.`, { status: 429 });
    session.ids.add(fields.request_id);
    session.used += planned;
    session.busy = true;
  }
  const done = () => { if (session) session.busy = false; };

  return {
    demo: true,
    async status() {
      return {
        database_enabled: false, avatar: caps.avatar, tryon: caps.tryon, usage: usage(), max_upload_mb: 8, max_garments: 4, max_sizes: 4,
        access_code_required: false, categories: CATEGORIES.map(([id, label, slot]) => ({ id, label, slot })),
        privacy: 'Demonstração: as imagens ficam apenas na memória desta aba.',
      };
    },
    async startSession() { session = { used: 0, ids: new Set(), busy: false }; return { token: 'demo', usage: usage() }; },
    hasSession: () => Boolean(session),
    async endSession() { session = null; },
    async checkPhoto(photo, framing) {
      const image = await bitmap(photo);
      const warnings = [];
      if (Math.min(image.width, image.height) < 640) warnings.push('Resolução baixa: o rosto e os detalhes podem perder nitidez.');
      if (framing === 'corpo_inteiro' && image.width > image.height * 1.05) warnings.push('Foto horizontal: para corpo inteiro, uma foto vertical costuma enquadrar melhor.');
      return { ok: true, width: image.width, height: image.height, warnings };
    },
    async avatar(fields) {
      guard(fields, 1);
      try {
        await wait(900);
        const image = await bitmap(fields.photo);
        const c = fit(image);
        return { image: stamp(c, 'SIMULAÇÃO · avatar base'), provider: 'mock', simulated: true, calls: 1, width: W, height: H,
          estimated_regions: fields.framing !== 'corpo_inteiro', warnings: [], usage: usage(),
          notes: ['Simulação: a foto foi apenas centralizada, sem gerar corpo.'] };
      } finally { done(); }
    },
    async tryon(fields) {
      const meta = fields.garments_meta;
      const items = meta.map((m, i) => ({ ...m, index: i }));
      if (composeLook(items).length !== items.length) throw new ApiError('Há peças disputando a mesma região do corpo.', { status: 422 });
      guard(fields, 1);
      try {
        await wait(1200);
        const c = fit(await bitmap(fields.base)), ctx = c.getContext('2d');
        for (const item of composeLook(items)) paste(ctx, cutout(await bitmap(fields.garments[item.index][0])), slotOf(item.category));
        return { image: stamp(c, 'SIMULAÇÃO · peça aplicada'), provider: 'mock', simulated: true, calls: 1, width: W, height: H, usage: usage(),
          notes: ['Colagem simulada: não há ajuste ao corpo, sombras ou tecido reais.'],
          garments: composeLook(items).map(item => ({ category: item.category, slot: slotOf(item.category), size_label: item.size_label })) };
      } finally { done(); }
    },
    async sizePreviews(fields) {
      const slot = slotOf(fields.category), key = (SLOT_FIELDS[slot] || [])[0]?.[0];
      for (const size of fields.sizes) if (num(size.measures?.[key]) === null) throw new ApiError(`Faltam medidas da peça no tamanho ${size.label}.`, { status: 422 });
      guard(fields, fields.sizes.length);
      try {
        const base = await bitmap(fields.base), piece = cutout(await bitmap(fields.garment[0][0]));
        const selected = fields.sizes.find(s => s.label === fields.selected_label)?.measures || {};
        const previews = [], seen = [];
        for (const size of fields.sizes) {
          await wait(500);
          const wk = WIDTH_KEY[slot];
          const sx = Math.max(0.7, Math.min(1.4, (num(size.measures[wk]) || 1) / (num(selected[wk]) || num(size.measures[wk]) || 1)));
          const sy = num(size.measures.comprimento_cm) && num(selected.comprimento_cm) ? Math.max(0.7, Math.min(1.4, size.measures.comprimento_cm / selected.comprimento_cm)) : 1;
          const c = fit(base), ctx = c.getContext('2d');
          paste(ctx, piece, slot, sx, sy);
          const signature = `${sx.toFixed(3)}x${sy.toFixed(3)}`;
          const repeated = seen.find(s => s.signature === signature);
          previews.push({ label: size.label, image: stamp(c, `SIMULAÇÃO · tamanho ${size.label}`), simulated: true, repeated_of: repeated?.label || null, notes: [] });
          seen.push({ label: size.label, signature });
        }
        return { previews, selected_label: fields.selected_label, illustrative: true, usage: usage() };
      } finally { done(); }
    },
  };
}

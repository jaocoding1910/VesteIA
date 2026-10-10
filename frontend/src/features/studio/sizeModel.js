// Comparação de tamanhos SOMENTE com medidas informadas (peça e, se houver, cliente).
// Nada é estimado a partir da imagem. Mesma lógica de backend/app/studio/sizes.py.

export const SLOT_FIELDS = {
  upper: [['largura_cm', 'Largura do tórax (peça plana)'], ['comprimento_cm', 'Comprimento'], ['manga_cm', 'Manga'], ['ombro_cm', 'Ombro a ombro']],
  outer: [['largura_cm', 'Largura do tórax (peça plana)'], ['comprimento_cm', 'Comprimento'], ['manga_cm', 'Manga'], ['ombro_cm', 'Ombro a ombro']],
  lower: [['cintura_cm', 'Cintura (peça plana)'], ['quadril_cm', 'Quadril (peça plana)'], ['comprimento_cm', 'Comprimento lateral'], ['entreperna_cm', 'Entrepernas']],
  full: [['busto_cm', 'Busto (peça plana)'], ['cintura_cm', 'Cintura (peça plana)'], ['quadril_cm', 'Quadril (peça plana)'], ['comprimento_cm', 'Comprimento']],
};

export const BODY_FIELDS = [
  ['torax_cm', 'Tórax / busto (circunferência)'], ['cintura_cm', 'Cintura (circunferência)'], ['quadril_cm', 'Quadril (circunferência)'],
  ['ombros_cm', 'Largura dos ombros'], ['entreperna_cm', 'Entrepernas'], ['altura_cm', 'Altura'],
];

export const CATEGORIES = [
  ['camiseta', 'Camiseta', 'upper'], ['camisa', 'Camisa', 'upper'], ['blusa', 'Blusa', 'upper'], ['regata', 'Regata', 'upper'],
  ['moletom', 'Moletom', 'upper'], ['casaco', 'Casaco', 'outer'], ['jaqueta', 'Jaqueta', 'outer'], ['calca', 'Calça', 'lower'],
  ['short', 'Short', 'lower'], ['bermuda', 'Bermuda', 'lower'], ['saia', 'Saia', 'lower'], ['vestido', 'Vestido', 'full'],
  ['macacao', 'Macacão', 'full'],
];
export const SLOT_LABEL = { upper: 'Parte de cima', outer: 'Sobreposição', lower: 'Parte de baixo', full: 'Peça inteira' };
const SLOT_ORDER = { full: 0, lower: 1, upper: 2, outer: 3 };

export const slotOf = category => CATEGORIES.find(c => c[0] === category)?.[2] || null;
export const categoryLabel = category => CATEGORIES.find(c => c[0] === category)?.[1] || 'Sem categoria';

const BANDS = {
  torax: [[-Infinity, 0, 'menor que o corpo (tende a apertar)', 'tight'], [0, 5, 'justa', 'snug'], [5, 12, 'regular', 'regular'], [12, 20, 'folgada', 'loose'], [20, Infinity, 'bem ampla', 'wide']],
  cintura: [[-Infinity, -1, 'menor que o corpo (tende a apertar)', 'tight'], [-1, 2, 'justa', 'snug'], [2, 6, 'regular', 'regular'], [6, Infinity, 'folgada', 'loose']],
  quadril: [[-Infinity, 0, 'menor que o corpo (tende a apertar)', 'tight'], [0, 4, 'justa', 'snug'], [4, 10, 'regular', 'regular'], [10, 18, 'folgada', 'loose'], [18, Infinity, 'bem ampla', 'wide']],
};

export function num(value) {
  if (value === '' || value === null || value === undefined) return null;
  const n = Number(String(value).replace(',', '.'));
  return Number.isFinite(n) && n >= 1 && n <= 300 ? Math.round(n * 10) / 10 : null;
}

function band(kind, ease) {
  const found = BANDS[kind].find(([lo, hi]) => ease >= lo && ease < hi);
  return { text: found[2], tone: found[3] };
}

/** Leituras de caimento para um tamanho. Só compara campos informados nos dois lados. */
export function fitReadings(slot, garment = {}, body = {}) {
  const g = Object.fromEntries(Object.entries(garment).map(([k, v]) => [k, num(v)]).filter(([, v]) => v !== null));
  const b = Object.fromEntries(Object.entries(body).map(([k, v]) => [k, num(v)]).filter(([, v]) => v !== null));
  const pairs = slot === 'upper' || slot === 'outer' ? [['largura_cm', 'torax_cm', 'torax', 'Tórax']]
    : slot === 'lower' ? [['cintura_cm', 'cintura_cm', 'cintura', 'Cintura'], ['quadril_cm', 'quadril_cm', 'quadril', 'Quadril']]
    : slot === 'full' ? [['busto_cm', 'torax_cm', 'torax', 'Busto'], ['cintura_cm', 'cintura_cm', 'cintura', 'Cintura'], ['quadril_cm', 'quadril_cm', 'quadril', 'Quadril']] : [];
  const out = [];
  for (const [gk, bk, kind, label] of pairs) {
    if (g[gk] != null && b[bk] != null) {
      const ease = Math.round((g[gk] * 2 - b[bk]) * 10) / 10;
      out.push({ label, value: ease, unit: 'folga', ...band(kind, ease) });
    }
  }
  if ((slot === 'upper' || slot === 'outer') && g.ombro_cm != null && b.ombros_cm != null) {
    const d = Math.round((g.ombro_cm - b.ombros_cm) * 10) / 10;
    out.push({ label: 'Ombros', value: d, unit: 'diferença', text: d < -2 ? 'ombro mais estreito que o corpo' : d <= 2 ? 'costura na linha do ombro' : d <= 6 ? 'ombro levemente caído' : 'ombro caído (modelagem ampla)', tone: d < -2 ? 'tight' : d <= 2 ? 'regular' : 'loose' });
  }
  if (slot === 'lower' && g.entreperna_cm != null && b.entreperna_cm != null) {
    const d = Math.round((g.entreperna_cm - b.entreperna_cm) * 10) / 10;
    out.push({ label: 'Entrepernas', value: d, unit: 'diferença', text: d < -3 ? 'mais curta que a perna' : d <= 3 ? 'na medida da perna' : 'mais longa (pode sobrar na barra)', tone: d < -3 ? 'tight' : d <= 3 ? 'regular' : 'loose' });
  }
  return out;
}

/** Diferenças de cada tamanho em relação ao escolhido, campo a campo. */
export function compareSizes(slot, sizes, measures, selected, body) {
  const fields = SLOT_FIELDS[slot] || [];
  const base = measures[selected] || {};
  const hasBody = Object.values(body || {}).some(v => num(v) !== null);
  return sizes.map(label => {
    const m = measures[label] || {};
    const filled = fields.filter(([k]) => num(m[k]) !== null).length;
    const diffs = fields.map(([key, name]) => {
      const a = num(m[key]), s = num(base[key]);
      return { key, name, value: a, delta: a !== null && s !== null && label !== selected ? Math.round((a - s) * 10) / 10 : null };
    });
    return { label, selected: label === selected, filled, total: fields.length, diffs, readings: hasBody ? fitReadings(slot, m, body) : [] };
  });
}

export function missingSummary(slot, sizes, measures, body) {
  const fields = SLOT_FIELDS[slot] || [];
  const sizesWithout = sizes.filter(label => !fields.some(([k]) => num((measures[label] || {})[k]) !== null));
  const hasBody = Object.values(body || {}).some(v => num(v) !== null);
  return { sizesWithout, hasBody, firstField: fields[0]?.[0] };
}

/** Mesma regra do backend: uma peça por região; peça inteira substitui cima e baixo. */
export function composeLook(items) {
  const kept = new Map();
  for (const item of items) {
    const slot = slotOf(item.category);
    if (!slot) continue;
    if (slot === 'full') { kept.delete('upper'); kept.delete('lower'); }
    if (slot === 'upper' || slot === 'lower') kept.delete('full');
    kept.set(slot, item);
  }
  return [...kept.entries()].sort((a, b) => SLOT_ORDER[a[0]] - SLOT_ORDER[b[0]]).map(([, item]) => item);
}

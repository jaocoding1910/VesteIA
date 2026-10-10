import { definitionFor } from '../../renderers/garments/registry.js';
import { garmentColor } from '../catalog/catalogModel.js';
const positive = (value, fallback) => Number.isFinite(Number(value)) && Number(value) > 0 ? Number(value) : fallback;
const clamp = (value, min = .55, max = 1.8) => Math.max(min, Math.min(max, value));
export const fitOptions = [['justo', 'Justo'], ['slim','Slim'], ['padrao', 'Padrão'], ['solto', 'Solto'], ['largo','Amplo'], ['oversized', 'Oversized']];
// Estilização visual explícita, não uma alteração das medidas cadastradas nem simulação física.
const fitFactors = {
  justo: [.93, .98],
  slim: [.97,.99],
  padrao: [1, 1],
  solto: [1.08, 1.025],
  largo: [1.13,1.04],
  oversized: [1.18, 1.065]
};
export function garmentDimensions(item) {
  const reference = {...item.product.metadata?.visual?.medidas_referencia,...item.variant?.metadata?.visual?.medidas_referencia};
  const category = item.product.categoria,
    m = item.size?.medidas || {},
    lower = definitionFor(category)?.regions.includes('lower'),
    foot = category === 'calcado',
    head = category === 'bone';
  const referenceWidth = positive(reference.largura_cm, head ? 18 : foot ? 9 : lower && category !== 'vestido' ? 40 : category === 'vestido' ? 48 : 52);
  const referenceLength = positive(reference.comprimento_cm, head ? 12 : foot ? 26 : {
    camiseta: 70,
    calca: 104,
    short: 46,
    saia: 74,
    vestido: 108
  }[category] || 70);
  const width = positive(m.largura_cm, lower ? positive(m.quadril_cm, positive(m.cintura_cm, referenceWidth * 2)) / 2 : positive(m.torax_cm, referenceWidth * 2) / 2);
  const length = positive(foot ? m.pe_cm || m.comprimento_cm : m.comprimento_cm, referenceLength);
  const [fx, fy] = foot || head ? [1, 1] : fitFactors[item.fit] || fitFactors.padrao;
  // Razões locais independentes: as dimensões declaradas permanecem disponíveis no modelo.
  return {
    width,
    length,
    x: clamp(width / referenceWidth) * fx,
    y: clamp(length / referenceLength) * fy,
    sleeve: clamp(positive(m.manga_cm, positive(reference.manga_cm,22)) / positive(reference.manga_cm,22)),
    shoulder: clamp(positive(m.ombros_cm, positive(reference.ombros_cm,46)) / positive(reference.ombros_cm,46)),
    waist: clamp(positive(m.cintura_cm, width * 2) / (width * 2)),
    hip: clamp(positive(m.quadril_cm, width * 2 + 20) / (width * 2 + 20)),
    hem: clamp(positive(m.barra_cm, category === 'calca' ? 20 : width) / (category === 'calca' ? 20 : width)),
    hasWidth: !!(m.largura_cm || m.torax_cm || m.quadril_cm || m.cintura_cm),
    hasLength: !!(m.comprimento_cm || m.pe_cm)
  };
}
export function selectedGarments({
  product,
  variant,
  size,
  look = [],
  showProduct = true,
  fit = 'padrao'
}) {
  const incoming = [...look.filter(i => i.ativo && (!showProduct || i.product?.id !== product?.id)), ...(showProduct && product ? [{
    product,
    variant,
    size,
    fit
  }] : [])];
  const result = [];
  for (const item of incoming) {
    const area = definitionFor(item.product.categoria)?.regions;
    if (!area) continue;
    for (let n = result.length - 1; n >= 0; n--) if (definitionFor(result[n].product.categoria).regions.some(r => area.includes(r))) result.splice(n, 1);
    result.push(item);
  }
  return result.sort((a, b) => definitionFor(a.product.categoria).order - definitionFor(b.product.categoria).order);
}
export function garmentAppearance(item) {
  const metadata = {
      ...item.product.metadata,
      ...item.variant?.metadata
    },
    visual = {
      ...item.product.metadata?.visual,
      ...item.variant?.metadata?.visual
    },
    knownPhoto = item.variant?.imagem_url === '/assets/camiseta-oversized.jpeg';
  return {
    garmentImageSize: visual.roupa_image_size,
    garmentCrop: Array.isArray(visual.roupa_crop)&&visual.roupa_crop.length===4&&Array.isArray(visual.roupa_image_size)&&visual.roupa_image_size.length===2&&visual.roupa_image_size.every(n=>Number.isFinite(n)&&n>0)&&visual.roupa_crop.every(Number.isFinite)&&visual.roupa_crop[2]>0&&visual.roupa_crop[3]>0?visual.roupa_crop:null,
    garmentUrl: visual.roupa_genero_urls?.[item.avatarGender] || visual.roupa_png_url || null,
    bodyRegistration: visual.encaixe_humano?.[item.avatarGender] || visual.encaixe_humano || {},
    printUrl: visual.estampa_url || metadata.estampa_url || null,
    printText: visual.estampa_texto || metadata.estampa_texto || null,
    printColor: visual.estampa_cor || '#f5f5f5',
    textureUrl: visual.textura_url === false ? null : visual.textura_url || item.variant?.imagem_url || null,
    textureCrop: visual.textura_crop || (knownPhoto ? {
      x: .25,
      y: .24,
      w: .5,
      h: .64
    } : {
      x: .25,
      y: .2,
      w: .5,
      h: .65
    }),
    printPosition: visual.estampa_posicao || {
      x: .5,
      y: .38,
      w: .5,
      h: .18
    }
  };
}
// Fronteira entre catálogo normalizado e renderer. Nenhum renderer consulta PostgreSQL ou regra de grade.
export function garmentVisualModel(item) {
  return {
    productId: item.product.id,
    variantId: item.variant?.id,
    sku: item.variant?.sku,
    category: item.product.categoria,
    size: item.size?.label,
    fit: item.fit || 'padrao',
    measurements: item.size?.medidas || {},
    modeling: item.variant?.modelagem || 'regular',
    color: garmentColor(item.variant),
    imageUrl: item.variant?.imagem_url,
    material: item.variant?.metadata?.tecido,
    metadata: item.variant?.metadata || {},
    appearance: garmentAppearance(item),
    dimensions: garmentDimensions(item)
  };
}
export function focusFrame(product, variant) {
  const layout = definitionFor(product?.categoria)?.geometry;
  if (!layout) return null;
  const [x, y, w, h] = layout.box,
    [ax, ay] = layout.anchor,
    dimensions = (variant?.tamanhos || []).map(size => garmentDimensions({
      product,
      variant,
      size,
      fit: 'oversized'
    }));
  const mx = Math.max(1, ...dimensions.map(d => d.x)),
    my = Math.max(1, ...dimensions.map(d => d.y)),
    margin = 70;
  return [ax + (x - ax) * mx - margin, ay + (y - ay) * my - margin, w * mx + margin * 2, h * my + margin * 2];
}

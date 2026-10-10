export const categories = [['todos', 'Todos'], ['camiseta', 'Camisetas'], ['calca', 'Calças'], ['short', 'Bermudas'], ['saia', 'Saias'], ['vestido', 'Vestidos'], ['calcado', 'Calçados'], ['bone','Bonés']];
export const money = value => new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
}).format(value || 0);
export const orderedSizes = variant => [...(variant?.tamanhos || [])].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id);
export const measureLabels = {
  largura_cm: 'Largura',
  comprimento_cm: 'Comprimento',
  torax_cm: 'Tórax',
  ombros_cm: 'Ombros',
  manga_cm: 'Manga',
  cintura_cm: 'Cintura',
  quadril_cm: 'Quadril',
  pe_cm: 'Pé',
  barra_cm: 'Barra'
};
export function garmentColor(variant) {
  const declared = variant?.metadata?.cor_hex;
  if (typeof declared === 'string' && /^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i.test(declared)) return declared;
  const colors = {
    preto: '#24252c',
    branco: '#f0f0ec',
    'off-white': '#e5e1d7',
    azul: '#35576d',
    violeta: '#695682',
    roxo: '#695682',
    vermelho: '#b3333b',
    verde: '#42745c',
    amarelo: '#dab548',
    rosa: '#ca7b9c',
    areia: '#bba98c',
    bege: '#bba98c',
    cinza: '#858c96',
    marrom: '#75533d',
    laranja: '#d47a37'
  };
  return colors[variant?.cor?.toLocaleLowerCase().trim()] || '#858c96';
}

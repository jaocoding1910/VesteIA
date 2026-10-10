export function supportsNatural({
  profile,
  product,
  variant,
  look = []
}) {
  const customized = profile && (profile.tom_pele !== '#b87d57' || profile.cabelo !== '#292018' || profile.estilo_cabelo !== 'curto');
  return !customized && product?.categoria === 'camiseta' && variant?.cor === 'Preto' && !look.some(i => i.ativo && i.product.id !== product?.id);
}

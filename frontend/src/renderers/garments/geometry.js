// Ajustes locais: a manga não escala junto ao tronco; cintura, quadril e barra têm eixos próprios.
export function geometryFor(base, model) {
  const d = model.dimensions,
    c = model.category;
  if (c === 'camiseta') {
    const sleeve = Math.max(-30, Math.min(80, (d.sleeve - 1) * 150)),
      shoulder = Math.max(-30, Math.min(30, (d.shoulder - 1) * 90)),
      hem = Math.max(-24, Math.min(40, (d.hem - 1) * 140));
    return {
      ...base,
      path: `M438 274Q512 313 586 274L${675 + shoulder} 307 ${739 + shoulder} ${464 + sleeve} ${653 + shoulder} ${500 + sleeve} 633 439 ${651 + hem} 692Q512 715 ${373 - hem} 692L391 439 ${371 - shoulder} ${500 + sleeve} ${285 - shoulder} ${464 + sleeve} ${349 - shoulder} 307Z`,
      seams: `M438 277Q512 344 586 277M${386 - hem} 674Q512 690 ${638 + hem} 674M${303 - shoulder} ${449 + sleeve} ${366 - shoulder} ${475 + sleeve}M${658 + shoulder} ${475 + sleeve} ${721 + shoulder} ${449 + sleeve}`
    };
  }
  if (c === 'calca') {
    const w = 136 * d.waist,
      h = 156 * d.hip,
      b = 49 * d.hem;
    return {
      ...base,
      path: `M${512 - w} 651Q512 677 ${512 + w} 651L${512 + h} 864 ${580 + b} 1400H${580 - b}L512 899 ${444 + b} 1400H${444 - b}L${512 - h} 864Z`,
      seams: `M${512 - w} 680Q512 701 ${512 + w} 680M512 690V849M${512 - w + 20} 760 ${512 - w + 48} 726M${512 + w - 20} 760 ${512 + w - 48} 726M${444 - b + 10} 1382H${444 + b - 10}M${580 - b + 10} 1382H${580 + b - 10}`
    };
  }
  return base;
}

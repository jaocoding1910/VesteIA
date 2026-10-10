import bone from './bone.js';
import camiseta from './camiseta.js';
import calca from './calca.js';
import short from './short.js';
import saia from './saia.js';
import vestido from './vestido.js';
import calcado from './calcado.js';
// Famílias e regiões independem dos IDs e das grades da loja.
export const garmentRegistry = {
  bone:{geometry:bone,regions:['head'],order:4},
  camiseta: {
    geometry: camiseta,
    regions: ['upper'],
    order: 2
  },
  camisa: {
    geometry: camiseta,
    regions: ['upper'],
    order: 2,
    approximate: true
  },
  blusa: {
    geometry: camiseta,
    regions: ['upper'],
    order: 2,
    approximate: true
  },
  jaqueta: {
    geometry: camiseta,
    regions: ['outer'],
    order: 3,
    approximate: true
  },
  casaco: {
    geometry: camiseta,
    regions: ['outer'],
    order: 3,
    approximate: true
  },
  regata: {
    geometry: camiseta,
    regions: ['upper'],
    order: 2,
    approximate: true
  },
  calca: {
    geometry: calca,
    regions: ['lower'],
    order: 1
  },
  short: {
    geometry: short,
    regions: ['lower'],
    order: 1
  },
  bermuda: {
    geometry: short,
    regions: ['lower'],
    order: 1
  },
  saia: {
    geometry: saia,
    regions: ['lower'],
    order: 1
  },
  vestido: {
    geometry: vestido,
    regions: ['upper', 'lower'],
    order: 2
  },
  calcado: {
    geometry: calcado,
    regions: ['feet'],
    order: 0
  }
};
export const definitionFor = category => garmentRegistry[category] || null;

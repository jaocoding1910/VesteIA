export const neutralProfile = {
  apelido: 'Você',
  estilo_avatar: 'humano',
  genero: 'masculino',
  altura_aproximada_cm: null,
  peso_aproximado_kg: null,
  porte_corporal: 'medio',
  proporcao_tronco: 'media',
  proporcao_pernas: 'media',
  tom_pele: '#a7a5a1',
  cabelo: '#353536',
  estilo_cabelo: 'curto',
  medidas: {}
};
export function avatarGeometry(profile = {}) {
  const height = 1; // Altura informada alimenta recomendação, não escala automática da imagem.
  const width = {
    estreito: .95,
    medio: 1,
    largo: 1.06
  }[profile.porte_corporal] || 1;
  const torso = {
    curto: .92,
    media: 1,
    longo: 1.08
  }[profile.proporcao_tronco] || 1;
  const legs = {
    curtas: .92,
    media: 1,
    longas: 1.08
  }[profile.proporcao_pernas] || 1;
  return {
    width,
    height,
    torso,
    legs,
    bodyTransform: `translate(512 1495) scale(1 ${height}) translate(-512 -1495)`
  };
}

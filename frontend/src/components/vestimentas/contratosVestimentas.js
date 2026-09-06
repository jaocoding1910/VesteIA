/*
 * VesteIA
 * Sprint 52 — Contratos Geométricos de Vestimenta
 *
 * Este arquivo descreve quais pontos visuais
 * cada família de vestimenta precisa fornecer
 * ao renderer.
 *
 * IMPORTANTE:
 * - coordenadas são visuais/normalizadas;
 * - não representam centímetros corporais;
 * - não inferem altura, peso ou circunferência;
 * - cada renderer continua responsável
 *   apenas pela representação visual da peça.
 */

export const FAMILIAS_VESTIMENTA = {
  SUPERIOR: "superior",
  INFERIOR: "inferior",
  CORPO_LONGO: "corpo_longo",
  SOBREPOSICAO: "sobreposicao",
  CALCADO: "calcado",
  ACESSORIO_CORPORAL: "acessorio_corporal",
}


/*
 * Categorias comerciais → categoria interna.
 *
 * Aqui podemos ampliar o vocabulário sem
 * alterar os renderers.
 */

export const CATEGORIAS_VESTIMENTA = {
  camiseta: {
    familia: FAMILIAS_VESTIMENTA.SUPERIOR,
    renderer: "camiseta",
  },

  camisetas: {
    familia: FAMILIAS_VESTIMENTA.SUPERIOR,
    renderer: "camiseta",
  },

  camisa: {
    familia: FAMILIAS_VESTIMENTA.SUPERIOR,
    renderer: "camisa",
  },

  camisas: {
    familia: FAMILIAS_VESTIMENTA.SUPERIOR,
    renderer: "camisa",
  },

  regata: {
    familia: FAMILIAS_VESTIMENTA.SUPERIOR,
    renderer: "regata",
  },

  regatas: {
    familia: FAMILIAS_VESTIMENTA.SUPERIOR,
    renderer: "regata",
  },

  calca: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,
    renderer: "calca",
  },

  calcas: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,
    renderer: "calca",
  },

  short: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,
    renderer: "short",
  },

  shorts: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,
    renderer: "short",
  },

  bermuda: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,
    renderer: "bermuda",
  },

  bermudas: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,
    renderer: "bermuda",
  },

  saia: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,
    renderer: "saia",
  },

  saias: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,
    renderer: "saia",
  },

  vestido: {
    familia: FAMILIAS_VESTIMENTA.CORPO_LONGO,
    renderer: "vestido",
  },

  vestidos: {
    familia: FAMILIAS_VESTIMENTA.CORPO_LONGO,
    renderer: "vestido",
  },

  macacao: {
    familia: FAMILIAS_VESTIMENTA.CORPO_LONGO,
    renderer: "macacao",
  },

  macacoes: {
    familia: FAMILIAS_VESTIMENTA.CORPO_LONGO,
    renderer: "macacao",
  },

  jaqueta: {
    familia: FAMILIAS_VESTIMENTA.SOBREPOSICAO,
    renderer: "jaqueta",
  },

  jaquetas: {
    familia: FAMILIAS_VESTIMENTA.SOBREPOSICAO,
    renderer: "jaqueta",
  },

  casaco: {
    familia: FAMILIAS_VESTIMENTA.SOBREPOSICAO,
    renderer: "casaco",
  },

  casacos: {
    familia: FAMILIAS_VESTIMENTA.SOBREPOSICAO,
    renderer: "casaco",
  },

  tenis: {
    familia: FAMILIAS_VESTIMENTA.CALCADO,
    renderer: "tenis",
  },

  sapato: {
    familia: FAMILIAS_VESTIMENTA.CALCADO,
    renderer: "sapato",
  },

  sapatos: {
    familia: FAMILIAS_VESTIMENTA.CALCADO,
    renderer: "sapato",
  },

  bota: {
    familia: FAMILIAS_VESTIMENTA.CALCADO,
    renderer: "bota",
  },

  botas: {
    familia: FAMILIAS_VESTIMENTA.CALCADO,
    renderer: "bota",
  },

  calcado: {
    familia: FAMILIAS_VESTIMENTA.CALCADO,
    renderer: "calcado",
  },

  calcados: {
    familia: FAMILIAS_VESTIMENTA.CALCADO,
    renderer: "calcado",
  },

  meia: {
    familia: FAMILIAS_VESTIMENTA.ACESSORIO_CORPORAL,
    renderer: "meia",
  },

  meias: {
    familia: FAMILIAS_VESTIMENTA.ACESSORIO_CORPORAL,
    renderer: "meia",
  },
}


/*
 * Contratos geométricos.
 *
 * Estes são nomes de pontos que o pipeline
 * de vestimenta deverá disponibilizar para
 * cada família/renderização.
 */

export const CONTRATOS_GEOMETRICOS = {
  camiseta: {
    familia: FAMILIAS_VESTIMENTA.SUPERIOR,

    pontosObrigatorios: [
      "gola_esquerda",
      "gola_direita",

      "ombro_esquerdo",
      "ombro_direito",

      "manga_esquerda_externa",
      "manga_direita_externa",

      "axila_esquerda",
      "axila_direita",

      "barra_esquerda",
      "barra_direita",
    ],
  },


  /*
   * Calça será nossa próxima implementação real.
   */

  calca: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,

    pontosObrigatorios: [
      "cintura_esquerda",
      "cintura_direita",

      "quadril_esquerdo",
      "quadril_direito",

      "entrepernas",

      "joelho_esquerdo_externo",
      "joelho_esquerdo_interno",

      "joelho_direito_externo",
      "joelho_direito_interno",

      "barra_esquerda_externa",
      "barra_esquerda_interna",

      "barra_direita_externa",
      "barra_direita_interna",
    ],
  },


  short: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,

    pontosObrigatorios: [
      "cintura_esquerda",
      "cintura_direita",

      "quadril_esquerdo",
      "quadril_direito",

      "entrepernas",

      "barra_esquerda_externa",
      "barra_esquerda_interna",

      "barra_direita_externa",
      "barra_direita_interna",
    ],
  },


  bermuda: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,

    pontosObrigatorios: [
      "cintura_esquerda",
      "cintura_direita",

      "quadril_esquerdo",
      "quadril_direito",

      "entrepernas",

      "barra_esquerda_externa",
      "barra_esquerda_interna",

      "barra_direita_externa",
      "barra_direita_interna",
    ],
  },


  saia: {
    familia: FAMILIAS_VESTIMENTA.INFERIOR,

    pontosObrigatorios: [
      "cintura_esquerda",
      "cintura_direita",

      "quadril_esquerdo",
      "quadril_direito",

      "barra_esquerda",
      "barra_direita",
    ],
  },


  vestido: {
    familia: FAMILIAS_VESTIMENTA.CORPO_LONGO,

    pontosObrigatorios: [
      "gola_esquerda",
      "gola_direita",

      "ombro_esquerdo",
      "ombro_direito",

      "axila_esquerda",
      "axila_direita",

      "cintura_esquerda",
      "cintura_direita",

      "quadril_esquerdo",
      "quadril_direito",

      "barra_esquerda",
      "barra_direita",
    ],
  },


  macacao: {
    familia: FAMILIAS_VESTIMENTA.CORPO_LONGO,

    pontosObrigatorios: [
      "ombro_esquerdo",
      "ombro_direito",

      "axila_esquerda",
      "axila_direita",

      "cintura_esquerda",
      "cintura_direita",

      "quadril_esquerdo",
      "quadril_direito",

      "entrepernas",

      "barra_esquerda",
      "barra_direita",
    ],
  },


  jaqueta: {
    familia: FAMILIAS_VESTIMENTA.SOBREPOSICAO,

    pontosObrigatorios: [
      "gola_esquerda",
      "gola_direita",

      "ombro_esquerdo",
      "ombro_direito",

      "punho_esquerdo",
      "punho_direito",

      "axila_esquerda",
      "axila_direita",

      "barra_esquerda",
      "barra_direita",
    ],
  },


  tenis: {
    familia: FAMILIAS_VESTIMENTA.CALCADO,

    pontosObrigatorios: [
      "tornozelo",

      "calcanhar",

      "ponta_pe",

      "lateral_interna",
      "lateral_externa",
    ],
  },


  meia: {
    familia: FAMILIAS_VESTIMENTA.ACESSORIO_CORPORAL,

    pontosObrigatorios: [
      "topo",

      "tornozelo",

      "calcanhar",

      "ponta_pe",
    ],
  },
}


/*
 * Normalização única para categorias.
 */

export function normalizarCategoriaVestimenta(
  categoria
) {
  return String(
    categoria ?? ""
  )
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(
      /[\u0300-\u036f]/g,
      ""
    )
}


/*
 * Descobre qual renderer deve tratar
 * determinada categoria.
 */

export function obterConfiguracaoVestimenta(
  categoria
) {
  const categoriaNormalizada =
    normalizarCategoriaVestimenta(
      categoria
    )

  return (
    CATEGORIAS_VESTIMENTA[
      categoriaNormalizada
    ] ?? null
  )
}


/*
 * Retorna o contrato geométrico
 * correspondente ao renderer.
 */

export function obterContratoGeometrico(
  categoria
) {
  const configuracao =
    obterConfiguracaoVestimenta(
      categoria
    )

  if (!configuracao) {
    return null
  }

  return (
    CONTRATOS_GEOMETRICOS[
      configuracao.renderer
    ] ?? null
  )
}


/*
 * Validação genérica dos pontos da peça.
 *
 * Por enquanto pode ser usada somente
 * como infraestrutura. Não precisamos
 * bloquear o renderer existente ainda.
 */

export function validarContratoGeometrico(
  categoria,
  pontos
) {
  const contrato =
    obterContratoGeometrico(
      categoria
    )

  if (!contrato) {
    return {
      valido: false,
      motivo:
        "categoria_sem_contrato",
      pontosFaltantes: [],
    }
  }

  const pontosDisponiveis =
    pontos ?? {}

  const pontosFaltantes =
    contrato
      .pontosObrigatorios
      .filter(
        (nome) => {
          const ponto =
            pontosDisponiveis[
              nome
            ]

          return !(
            ponto &&
            typeof ponto.x ===
              "number" &&
            typeof ponto.y ===
              "number"
          )
        }
      )

  return {
    valido:
      pontosFaltantes
        .length === 0,

    motivo:
      pontosFaltantes
        .length === 0
        ? "contrato_atendido"
        : "pontos_insuficientes",

    familia:
      contrato.familia,

    pontosObrigatorios:
      contrato
        .pontosObrigatorios,

    pontosFaltantes,
  }
}
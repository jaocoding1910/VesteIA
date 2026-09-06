function CalcaRenderer2D({
  pontos,
  obterPontoRoupa,
  disponivel = true,
}) {
  if (
    !disponivel ||
    !pontos ||
    typeof obterPontoRoupa !== "function"
  ) {
    return null
  }

  /*
   * VesteIA
   * Sprint 52 — Renderer de Calça V1
   *
   * Este componente renderiza apenas
   * a representação visual da calça.
   *
   * IMPORTANTE:
   * - trabalha com geometria normalizada;
   * - não representa centímetros corporais;
   * - não estima altura;
   * - não estima peso;
   * - não estima circunferências;
   * - não altera a geometria corporal.
   */

  const cinturaEsquerda =
    obterPontoRoupa(
      "cintura_esquerda"
    )

  const cinturaDireita =
    obterPontoRoupa(
      "cintura_direita"
    )

  const quadrilEsquerdo =
    obterPontoRoupa(
      "quadril_esquerdo"
    )

  const quadrilDireito =
    obterPontoRoupa(
      "quadril_direito"
    )

  const entrepernas =
    obterPontoRoupa(
      "entrepernas"
    )

  const joelhoEsquerdoExterno =
    obterPontoRoupa(
      "joelho_esquerdo_externo"
    )

  const joelhoEsquerdoInterno =
    obterPontoRoupa(
      "joelho_esquerdo_interno"
    )

  const joelhoDireitoExterno =
    obterPontoRoupa(
      "joelho_direito_externo"
    )

  const joelhoDireitoInterno =
    obterPontoRoupa(
      "joelho_direito_interno"
    )

  const barraEsquerdaExterna =
    obterPontoRoupa(
      "barra_esquerda_externa"
    )

  const barraEsquerdaInterna =
    obterPontoRoupa(
      "barra_esquerda_interna"
    )

  const barraDireitaExterna =
    obterPontoRoupa(
      "barra_direita_externa"
    )

  const barraDireitaInterna =
    obterPontoRoupa(
      "barra_direita_interna"
    )

  /*
   * Só desenhamos quando o contrato
   * geométrico da calça estiver completo.
   */

  const geometriaCompleta =
    cinturaEsquerda &&
    cinturaDireita &&
    quadrilEsquerdo &&
    quadrilDireito &&
    entrepernas &&
    joelhoEsquerdoExterno &&
    joelhoEsquerdoInterno &&
    joelhoDireitoExterno &&
    joelhoDireitoInterno &&
    barraEsquerdaExterna &&
    barraEsquerdaInterna &&
    barraDireitaExterna &&
    barraDireitaInterna

  if (!geometriaCompleta) {
    return null
  }

  /*
   * A calça é construída em três regiões:
   *
   * 1. cintura/quadril;
   * 2. perna esquerda;
   * 3. perna direita.
   *
   * Os pontos vêm do pipeline.
   * As curvas abaixo são apenas
   * acabamento visual do renderer.
   */

  return (
    <g
      data-vesteia-vestimenta="calca"
      data-vesteia-renderer="calca-v1"
    >

      {/* CORPO CENTRAL DA CALÇA */}

      <path
        d={`
          M
          ${cinturaEsquerda.x}
          ${cinturaEsquerda.y}

          Q
          ${
            (
              cinturaEsquerda.x +
              cinturaDireita.x
            ) / 2
          }
          ${
            (
              cinturaEsquerda.y +
              cinturaDireita.y
            ) / 2 - 3
          }

          ${cinturaDireita.x}
          ${cinturaDireita.y}

          L
          ${quadrilDireito.x}
          ${quadrilDireito.y}

          Q
          ${
            (
              quadrilDireito.x +
              entrepernas.x
            ) / 2
          }
          ${
            (
              quadrilDireito.y +
              entrepernas.y
            ) / 2
          }

          ${entrepernas.x}
          ${entrepernas.y}

          Q
          ${
            (
              quadrilEsquerdo.x +
              entrepernas.x
            ) / 2
          }
          ${
            (
              quadrilEsquerdo.y +
              entrepernas.y
            ) / 2
          }

          ${quadrilEsquerdo.x}
          ${quadrilEsquerdo.y}

          Z
        `}
        fill="#242b63"
        stroke="#7584ff"
        strokeWidth="3"
        strokeLinejoin="round"
        opacity="0.96"
      />

      {/* PERNA ESQUERDA */}

      <path
        d={`
          M
          ${quadrilEsquerdo.x}
          ${quadrilEsquerdo.y}

          Q
          ${joelhoEsquerdoExterno.x}
          ${joelhoEsquerdoExterno.y}

          ${barraEsquerdaExterna.x}
          ${barraEsquerdaExterna.y}

          Q
          ${
            (
              barraEsquerdaExterna.x +
              barraEsquerdaInterna.x
            ) / 2
          }
          ${
            (
              barraEsquerdaExterna.y +
              barraEsquerdaInterna.y
            ) / 2 + 2
          }

          ${barraEsquerdaInterna.x}
          ${barraEsquerdaInterna.y}

          Q
          ${joelhoEsquerdoInterno.x}
          ${joelhoEsquerdoInterno.y}

          ${entrepernas.x}
          ${entrepernas.y}

          Q
          ${
            (
              quadrilEsquerdo.x +
              entrepernas.x
            ) / 2
          }
          ${
            (
              quadrilEsquerdo.y +
              entrepernas.y
            ) / 2
          }

          ${quadrilEsquerdo.x}
          ${quadrilEsquerdo.y}

          Z
        `}
        fill="#303a82"
        stroke="#7584ff"
        strokeWidth="3"
        strokeLinejoin="round"
        opacity="0.96"
      />

      {/* PERNA DIREITA */}

      <path
        d={`
          M
          ${quadrilDireito.x}
          ${quadrilDireito.y}

          Q
          ${joelhoDireitoExterno.x}
          ${joelhoDireitoExterno.y}

          ${barraDireitaExterna.x}
          ${barraDireitaExterna.y}

          Q
          ${
            (
              barraDireitaExterna.x +
              barraDireitaInterna.x
            ) / 2
          }
          ${
            (
              barraDireitaExterna.y +
              barraDireitaInterna.y
            ) / 2 + 2
          }

          ${barraDireitaInterna.x}
          ${barraDireitaInterna.y}

          Q
          ${joelhoDireitoInterno.x}
          ${joelhoDireitoInterno.y}

          ${entrepernas.x}
          ${entrepernas.y}

          Q
          ${
            (
              quadrilDireito.x +
              entrepernas.x
            ) / 2
          }
          ${
            (
              quadrilDireito.y +
              entrepernas.y
            ) / 2
          }

          ${quadrilDireito.x}
          ${quadrilDireito.y}

          Z
        `}
        fill="#303a82"
        stroke="#7584ff"
        strokeWidth="3"
        strokeLinejoin="round"
        opacity="0.96"
      />

      {/* CÓS */}

      <path
        d={`
          M
          ${cinturaEsquerda.x}
          ${cinturaEsquerda.y}

          Q
          ${
            (
              cinturaEsquerda.x +
              cinturaDireita.x
            ) / 2
          }
          ${
            (
              cinturaEsquerda.y +
              cinturaDireita.y
            ) / 2 + 2
          }

          ${cinturaDireita.x}
          ${cinturaDireita.y}
        `}
        fill="none"
        stroke="#a8b2ff"
        strokeWidth="4"
        strokeLinecap="round"
      />

      {/* LINHA CENTRAL */}

      <path
        d={`
          M
          ${
            (
              cinturaEsquerda.x +
              cinturaDireita.x
            ) / 2
          }
          ${
            (
              cinturaEsquerda.y +
              cinturaDireita.y
            ) / 2
          }

          Q
          ${entrepernas.x}
          ${
            (
              cinturaEsquerda.y +
              entrepernas.y
            ) / 2
          }

          ${entrepernas.x}
          ${entrepernas.y}
        `}
        fill="none"
        stroke="#a8b2ff"
        strokeWidth="1.5"
        opacity="0.65"
      />

    </g>
  )
}

export default CalcaRenderer2D
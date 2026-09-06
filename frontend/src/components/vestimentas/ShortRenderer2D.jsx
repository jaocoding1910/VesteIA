function ShortRenderer2D({
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
   * Sprint 52 — Renderer de Short V1
   *
   * Este componente renderiza apenas
   * a representação visual do short.
   *
   * IMPORTANTE:
   * - trabalha com geometria normalizada;
   * - não representa centímetros corporais;
   * - não estima medidas do corpo;
   * - não recomenda tamanho;
   * - não altera a geometria corporal.
   *
   * O contrato geométrico é fornecido
   * pelo pipeline multivestimenta.
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
   * O backend fornece o mesmo contrato
   * estrutural utilizado pelas peças
   * inferiores com pernas independentes.
   *
   * Para o short, a barra termina antes
   * da região dos joelhos corporais.
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

  return (
    <g
      data-vesteia-vestimenta="short"
      data-vesteia-renderer="short-v1"
    >

      {/* CORPO CENTRAL */}

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

      {/* COSTURA CENTRAL */}

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

      {/* BARRA ESQUERDA */}

      <path
        d={`
          M
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
            ) / 2 + 1
          }

          ${barraEsquerdaInterna.x}
          ${barraEsquerdaInterna.y}
        `}
        fill="none"
        stroke="#a8b2ff"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.8"
      />

      {/* BARRA DIREITA */}

      <path
        d={`
          M
          ${barraDireitaInterna.x}
          ${barraDireitaInterna.y}

          Q
          ${
            (
              barraDireitaInterna.x +
              barraDireitaExterna.x
            ) / 2
          }
          ${
            (
              barraDireitaInterna.y +
              barraDireitaExterna.y
            ) / 2 + 1
          }

          ${barraDireitaExterna.x}
          ${barraDireitaExterna.y}
        `}
        fill="none"
        stroke="#a8b2ff"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.8"
      />

    </g>
  )
}

export default ShortRenderer2D
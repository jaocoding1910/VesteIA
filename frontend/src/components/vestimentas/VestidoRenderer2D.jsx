function VestidoRenderer2D({
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
   * Sprint 52 — Renderer de Vestido V1
   *
   * Renderiza uma peça de corpo integrado
   * utilizando a geometria calculada
   * pelo backend.
   *
   * IMPORTANTE:
   * - geometria exclusivamente visual;
   * - não representa medidas corporais em cm;
   * - não estima altura;
   * - não recomenda tamanho;
   * - não altera o corpo detectado.
   */

  const golaEsquerda =
    obterPontoRoupa(
      "gola_esquerda"
    )

  const golaDireita =
    obterPontoRoupa(
      "gola_direita"
    )

  const ombroEsquerdo =
    obterPontoRoupa(
      "ombro_esquerdo"
    )

  const ombroDireito =
    obterPontoRoupa(
      "ombro_direito"
    )

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

  const barraEsquerda =
    obterPontoRoupa(
      "barra_esquerda"
    )

  const barraDireita =
    obterPontoRoupa(
      "barra_direita"
    )

  const geometriaCompleta =
    golaEsquerda &&
    golaDireita &&
    ombroEsquerdo &&
    ombroDireito &&
    cinturaEsquerda &&
    cinturaDireita &&
    quadrilEsquerdo &&
    quadrilDireito &&
    barraEsquerda &&
    barraDireita

  if (!geometriaCompleta) {
    return null
  }

  const centroGolaX =
    (
      golaEsquerda.x +
      golaDireita.x
    ) / 2

  const centroGolaY =
    (
      golaEsquerda.y +
      golaDireita.y
    ) / 2

  const centroCinturaX =
    (
      cinturaEsquerda.x +
      cinturaDireita.x
    ) / 2

  return (
    <g
      data-vesteia-vestimenta="vestido"
      data-vesteia-renderer="vestido-v1"
    >

      {/* CORPO PRINCIPAL */}

      <path
        d={`
          M
          ${ombroEsquerdo.x}
          ${ombroEsquerdo.y}

          Q
          ${
            (
              ombroEsquerdo.x +
              cinturaEsquerda.x
            ) / 2 - 3
          }
          ${
            (
              ombroEsquerdo.y +
              cinturaEsquerda.y
            ) / 2
          }

          ${cinturaEsquerda.x}
          ${cinturaEsquerda.y}

          Q
          ${
            (
              cinturaEsquerda.x +
              quadrilEsquerdo.x
            ) / 2 - 2
          }
          ${
            (
              cinturaEsquerda.y +
              quadrilEsquerdo.y
            ) / 2
          }

          ${quadrilEsquerdo.x}
          ${quadrilEsquerdo.y}

          Q
          ${
            (
              quadrilEsquerdo.x +
              barraEsquerda.x
            ) / 2 - 4
          }
          ${
            (
              quadrilEsquerdo.y +
              barraEsquerda.y
            ) / 2
          }

          ${barraEsquerda.x}
          ${barraEsquerda.y}

          Q
          ${centroCinturaX}
          ${barraEsquerda.y + 4}

          ${barraDireita.x}
          ${barraDireita.y}

          Q
          ${
            (
              quadrilDireito.x +
              barraDireita.x
            ) / 2 + 4
          }
          ${
            (
              quadrilDireito.y +
              barraDireita.y
            ) / 2
          }

          ${quadrilDireito.x}
          ${quadrilDireito.y}

          Q
          ${
            (
              cinturaDireita.x +
              quadrilDireito.x
            ) / 2 + 2
          }
          ${
            (
              cinturaDireita.y +
              quadrilDireito.y
            ) / 2
          }

          ${cinturaDireita.x}
          ${cinturaDireita.y}

          Q
          ${
            (
              ombroDireito.x +
              cinturaDireita.x
            ) / 2 + 3
          }
          ${
            (
              ombroDireito.y +
              cinturaDireita.y
            ) / 2
          }

          ${ombroDireito.x}
          ${ombroDireito.y}

          Q
          ${golaDireita.x}
          ${golaDireita.y}

          ${centroGolaX}
          ${centroGolaY + 8}

          Q
          ${golaEsquerda.x}
          ${golaEsquerda.y}

          ${ombroEsquerdo.x}
          ${ombroEsquerdo.y}

          Z
        `}
        fill="#4b3fa8"
        stroke="#8b7cff"
        strokeWidth="3"
        strokeLinejoin="round"
        opacity="0.96"
      />

      {/* REGIÃO SUPERIOR */}

      <path
        d={`
          M
          ${ombroEsquerdo.x}
          ${ombroEsquerdo.y}

          Q
          ${centroGolaX}
          ${centroGolaY + 7}

          ${ombroDireito.x}
          ${ombroDireito.y}

          L
          ${cinturaDireita.x}
          ${cinturaDireita.y}

          Q
          ${centroCinturaX}
          ${cinturaDireita.y + 3}

          ${cinturaEsquerda.x}
          ${cinturaEsquerda.y}

          Z
        `}
        fill="#5548bd"
        stroke="none"
        opacity="0.72"
      />

      {/* LINHA DA CINTURA */}

      <path
        d={`
          M
          ${cinturaEsquerda.x}
          ${cinturaEsquerda.y}

          Q
          ${centroCinturaX}
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
        stroke="#aaa0ff"
        strokeWidth="2"
        opacity="0.72"
      />

      {/* GOLA */}

      <path
        d={`
          M
          ${golaEsquerda.x}
          ${golaEsquerda.y}

          Q
          ${centroGolaX}
          ${centroGolaY + 9}

          ${golaDireita.x}
          ${golaDireita.y}
        `}
        fill="none"
        stroke="#bbb3ff"
        strokeWidth="2"
        strokeLinecap="round"
      />

      {/* LINHA DA BARRA */}

      <path
        d={`
          M
          ${barraEsquerda.x}
          ${barraEsquerda.y}

          Q
          ${
            (
              barraEsquerda.x +
              barraDireita.x
            ) / 2
          }
          ${
            (
              barraEsquerda.y +
              barraDireita.y
            ) / 2 + 4
          }

          ${barraDireita.x}
          ${barraDireita.y}
        `}
        fill="none"
        stroke="#aaa0ff"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

    </g>
  )
}

export default VestidoRenderer2D
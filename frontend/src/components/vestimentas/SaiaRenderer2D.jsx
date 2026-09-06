function SaiaRenderer2D({
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
   * Sprint 52 — Renderer de Saia V1
   *
   * Renderiza uma peça inferior contínua,
   * sem divisão entre pernas.
   *
   * IMPORTANTE:
   * - utiliza geometria visual normalizada;
   * - não representa medidas corporais em cm;
   * - não estima circunferências;
   * - não recomenda tamanho;
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

  const barraEsquerda =
    obterPontoRoupa(
      "barra_esquerda"
    )

  const barraDireita =
    obterPontoRoupa(
      "barra_direita"
    )

  const geometriaCompleta =
    cinturaEsquerda &&
    cinturaDireita &&
    quadrilEsquerdo &&
    quadrilDireito &&
    barraEsquerda &&
    barraDireita

  if (!geometriaCompleta) {
    return null
  }

  const centroCinturaX =
    (
      cinturaEsquerda.x +
      cinturaDireita.x
    ) / 2

  const centroBarraX =
    (
      barraEsquerda.x +
      barraDireita.x
    ) / 2

  const centroBarraY =
    (
      barraEsquerda.y +
      barraDireita.y
    ) / 2

  return (
    <g
      data-vesteia-vestimenta="saia"
      data-vesteia-renderer="saia-v1"
    >

      {/* CORPO PRINCIPAL */}

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
            ) / 2 - 2
          }

          ${cinturaDireita.x}
          ${cinturaDireita.y}

          Q
          ${
            quadrilDireito.x + 3
          }
          ${quadrilDireito.y}

          ${quadrilDireito.x}
          ${quadrilDireito.y}

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

          ${barraDireita.x}
          ${barraDireita.y}

          Q
          ${centroBarraX}
          ${centroBarraY + 4}

          ${barraEsquerda.x}
          ${barraEsquerda.y}

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

          ${quadrilEsquerdo.x}
          ${quadrilEsquerdo.y}

          Q
          ${
            quadrilEsquerdo.x - 3
          }
          ${quadrilEsquerdo.y}

          ${cinturaEsquerda.x}
          ${cinturaEsquerda.y}

          Z
        `}
        fill="#4338a8"
        stroke="#7c6cff"
        strokeWidth="3"
        strokeLinejoin="round"
        opacity="0.96"
      />

      {/* REGIÃO DO QUADRIL */}

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

          L
          ${quadrilDireito.x}
          ${quadrilDireito.y}

          Q
          ${
            (
              quadrilEsquerdo.x +
              quadrilDireito.x
            ) / 2
          }
          ${
            (
              quadrilEsquerdo.y +
              quadrilDireito.y
            ) / 2 + 2
          }

          ${quadrilEsquerdo.x}
          ${quadrilEsquerdo.y}

          Z
        `}
        fill="#5145bd"
        stroke="none"
        opacity="0.74"
      />

      {/* CÓS */}

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
        strokeWidth="4"
        strokeLinecap="round"
      />

      {/* LINHA DA BARRA */}

      <path
        d={`
          M
          ${barraEsquerda.x}
          ${barraEsquerda.y}

          Q
          ${centroBarraX}
          ${centroBarraY + 4}

          ${barraDireita.x}
          ${barraDireita.y}
        `}
        fill="none"
        stroke="#aaa0ff"
        strokeWidth="2.5"
        strokeLinecap="round"
        opacity="0.85"
      />

      {/* COSTURA CENTRAL VISUAL */}

      <path
        d={`
          M
          ${centroCinturaX}
          ${
            (
              cinturaEsquerda.y +
              cinturaDireita.y
            ) / 2
          }

          Q
          ${centroBarraX}
          ${
            (
              quadrilEsquerdo.y +
              barraEsquerda.y
            ) / 2
          }

          ${centroBarraX}
          ${centroBarraY}
        `}
        fill="none"
        stroke="#9f96ff"
        strokeWidth="1.3"
        opacity="0.35"
      />

    </g>
  )
}

export default SaiaRenderer2D
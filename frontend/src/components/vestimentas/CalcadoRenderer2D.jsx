function CalcadoRenderer2D({
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
   * Sprint 52 — Renderer de Calçado V1
   *
   * Renderiza os dois calçados
   * posicionados sobre os pés do avatar.
   *
   * IMPORTANTE:
   * - geometria exclusivamente visual;
   * - não representa comprimento real do pé;
   * - não determina número de calçado;
   * - não utiliza centímetros corporais;
   * - não altera a geometria corporal.
   */

  const peEsquerdoCalcanharExterno =
    obterPontoRoupa(
      "pe_esquerdo_calcanhar_externo"
    )

  const peEsquerdoCalcanharInterno =
    obterPontoRoupa(
      "pe_esquerdo_calcanhar_interno"
    )

  const peEsquerdoPontaInterna =
    obterPontoRoupa(
      "pe_esquerdo_ponta_interna"
    )

  const peEsquerdoPontaExterna =
    obterPontoRoupa(
      "pe_esquerdo_ponta_externa"
    )


  const peDireitoCalcanharExterno =
    obterPontoRoupa(
      "pe_direito_calcanhar_externo"
    )

  const peDireitoCalcanharInterno =
    obterPontoRoupa(
      "pe_direito_calcanhar_interno"
    )

  const peDireitoPontaInterna =
    obterPontoRoupa(
      "pe_direito_ponta_interna"
    )

  const peDireitoPontaExterna =
    obterPontoRoupa(
      "pe_direito_ponta_externa"
    )


  const peEsquerdoCompleto =
    peEsquerdoCalcanharExterno &&
    peEsquerdoCalcanharInterno &&
    peEsquerdoPontaInterna &&
    peEsquerdoPontaExterna


  const peDireitoCompleto =
    peDireitoCalcanharExterno &&
    peDireitoCalcanharInterno &&
    peDireitoPontaInterna &&
    peDireitoPontaExterna


  if (
    !peEsquerdoCompleto &&
    !peDireitoCompleto
  ) {
    return null
  }


  return (
    <g
      data-vesteia-vestimenta="calcado"
      data-vesteia-renderer="calcado-v1"
    >

      {/* CALÇADO ESQUERDO */}

      {peEsquerdoCompleto && (
        <>
          <path
            d={`
              M
              ${peEsquerdoCalcanharExterno.x}
              ${peEsquerdoCalcanharExterno.y}

              Q
              ${
                (
                  peEsquerdoCalcanharExterno.x +
                  peEsquerdoPontaExterna.x
                ) / 2
              }
              ${
                (
                  peEsquerdoCalcanharExterno.y +
                  peEsquerdoPontaExterna.y
                ) / 2 + 3
              }

              ${peEsquerdoPontaExterna.x}
              ${peEsquerdoPontaExterna.y}

              Q
              ${
                (
                  peEsquerdoPontaExterna.x +
                  peEsquerdoPontaInterna.x
                ) / 2
              }
              ${
                (
                  peEsquerdoPontaExterna.y +
                  peEsquerdoPontaInterna.y
                ) / 2 + 4
              }

              ${peEsquerdoPontaInterna.x}
              ${peEsquerdoPontaInterna.y}

              Q
              ${
                (
                  peEsquerdoPontaInterna.x +
                  peEsquerdoCalcanharInterno.x
                ) / 2
              }
              ${
                (
                  peEsquerdoPontaInterna.y +
                  peEsquerdoCalcanharInterno.y
                ) / 2
              }

              ${peEsquerdoCalcanharInterno.x}
              ${peEsquerdoCalcanharInterno.y}

              Q
              ${
                (
                  peEsquerdoCalcanharInterno.x +
                  peEsquerdoCalcanharExterno.x
                ) / 2
              }
              ${
                (
                  peEsquerdoCalcanharInterno.y +
                  peEsquerdoCalcanharExterno.y
                ) / 2 - 2
              }

              ${peEsquerdoCalcanharExterno.x}
              ${peEsquerdoCalcanharExterno.y}

              Z
            `}
            fill="#242b63"
            stroke="#7584ff"
            strokeWidth="3"
            strokeLinejoin="round"
            opacity="0.98"
          />

          {/* SOLADO ESQUERDO */}

          <path
            d={`
              M
              ${peEsquerdoPontaExterna.x}
              ${peEsquerdoPontaExterna.y}

              Q
              ${
                (
                  peEsquerdoPontaExterna.x +
                  peEsquerdoPontaInterna.x
                ) / 2
              }
              ${
                Math.max(
                  peEsquerdoPontaExterna.y,
                  peEsquerdoPontaInterna.y
                ) + 4
              }

              ${peEsquerdoPontaInterna.x}
              ${peEsquerdoPontaInterna.y}
            `}
            fill="none"
            stroke="#a8b2ff"
            strokeWidth="3"
            strokeLinecap="round"
          />
        </>
      )}


      {/* CALÇADO DIREITO */}

      {peDireitoCompleto && (
        <>
          <path
            d={`
              M
              ${peDireitoCalcanharExterno.x}
              ${peDireitoCalcanharExterno.y}

              Q
              ${
                (
                  peDireitoCalcanharExterno.x +
                  peDireitoPontaExterna.x
                ) / 2
              }
              ${
                (
                  peDireitoCalcanharExterno.y +
                  peDireitoPontaExterna.y
                ) / 2 + 3
              }

              ${peDireitoPontaExterna.x}
              ${peDireitoPontaExterna.y}

              Q
              ${
                (
                  peDireitoPontaExterna.x +
                  peDireitoPontaInterna.x
                ) / 2
              }
              ${
                (
                  peDireitoPontaExterna.y +
                  peDireitoPontaInterna.y
                ) / 2 + 4
              }

              ${peDireitoPontaInterna.x}
              ${peDireitoPontaInterna.y}

              Q
              ${
                (
                  peDireitoPontaInterna.x +
                  peDireitoCalcanharInterno.x
                ) / 2
              }
              ${
                (
                  peDireitoPontaInterna.y +
                  peDireitoCalcanharInterno.y
                ) / 2
              }

              ${peDireitoCalcanharInterno.x}
              ${peDireitoCalcanharInterno.y}

              Q
              ${
                (
                  peDireitoCalcanharInterno.x +
                  peDireitoCalcanharExterno.x
                ) / 2
              }
              ${
                (
                  peDireitoCalcanharInterno.y +
                  peDireitoCalcanharExterno.y
                ) / 2 - 2
              }

              ${peDireitoCalcanharExterno.x}
              ${peDireitoCalcanharExterno.y}

              Z
            `}
            fill="#242b63"
            stroke="#7584ff"
            strokeWidth="3"
            strokeLinejoin="round"
            opacity="0.98"
          />

          {/* SOLADO DIREITO */}

          <path
            d={`
              M
              ${peDireitoPontaExterna.x}
              ${peDireitoPontaExterna.y}

              Q
              ${
                (
                  peDireitoPontaExterna.x +
                  peDireitoPontaInterna.x
                ) / 2
              }
              ${
                Math.max(
                  peDireitoPontaExterna.y,
                  peDireitoPontaInterna.y
                ) + 4
              }

              ${peDireitoPontaInterna.x}
              ${peDireitoPontaInterna.y}
            `}
            fill="none"
            stroke="#a8b2ff"
            strokeWidth="3"
            strokeLinecap="round"
          />
        </>
      )}

    </g>
  )
}

export default CalcadoRenderer2D
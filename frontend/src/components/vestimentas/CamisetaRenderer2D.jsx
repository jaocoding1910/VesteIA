function CamisetaRenderer2D({
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

  const roupaOmbroEsquerdo =
    obterPontoRoupa(
      "ombro_esquerdo"
    )

  const roupaOmbroDireito =
    obterPontoRoupa(
      "ombro_direito"
    )

  const roupaAxilaEsquerda =
    obterPontoRoupa(
      "axila_esquerda"
    )

  const roupaAxilaDireita =
    obterPontoRoupa(
      "axila_direita"
    )

  const roupaBarraEsquerda =
    obterPontoRoupa(
      "barra_esquerda"
    )

  const roupaBarraDireita =
    obterPontoRoupa(
      "barra_direita"
    )

  const roupaGolaEsquerda =
    obterPontoRoupa(
      "gola_esquerda"
    )

  const roupaGolaDireita =
    obterPontoRoupa(
      "gola_direita"
    )

  const mangaEsquerdaExterna =
    obterPontoRoupa(
      "manga_esquerda_externa"
    )

  const mangaDireitaExterna =
    obterPontoRoupa(
      "manga_direita_externa"
    )

  const camisetaDisponivel =
    Boolean(
      roupaOmbroEsquerdo &&
      roupaOmbroDireito &&
      roupaAxilaEsquerda &&
      roupaAxilaDireita &&
      roupaBarraEsquerda &&
      roupaBarraDireita &&
      roupaGolaEsquerda &&
      roupaGolaDireita &&
      mangaEsquerdaExterna &&
      mangaDireitaExterna
    )

  if (!camisetaDisponivel) {
    return null
  }

  return (
    <g
      data-vesteia-vestimenta="camiseta"
      data-vesteia-renderer="camiseta-v1"
    >
      <path
        d={`
          M
          ${roupaGolaEsquerda.x}
          ${roupaGolaEsquerda.y}

          Q
          ${
            (
              roupaGolaEsquerda.x +
              roupaOmbroEsquerdo.x
            ) / 2
          }
          ${
            roupaGolaEsquerda.y - 3
          }

          ${roupaOmbroEsquerdo.x}
          ${roupaOmbroEsquerdo.y}

          Q
          ${
            (
              roupaOmbroEsquerdo.x +
              mangaEsquerdaExterna.x
            ) / 2
          }
          ${
            (
              roupaOmbroEsquerdo.y +
              mangaEsquerdaExterna.y
            ) / 2 - 2
          }

          ${mangaEsquerdaExterna.x}
          ${mangaEsquerdaExterna.y}

          Q
          ${
            (
              mangaEsquerdaExterna.x +
              roupaAxilaEsquerda.x
            ) / 2 - 2
          }
          ${
            (
              mangaEsquerdaExterna.y +
              roupaAxilaEsquerda.y
            ) / 2 + 8
          }

          ${roupaAxilaEsquerda.x}
          ${roupaAxilaEsquerda.y}

          C
          ${
            roupaAxilaEsquerda.x - 2
          }
          ${
            roupaAxilaEsquerda.y + 28
          }

          ${
            roupaBarraEsquerda.x - 4
          }
          ${
            roupaBarraEsquerda.y - 28
          }

          ${roupaBarraEsquerda.x}
          ${roupaBarraEsquerda.y}

          Q
          ${
            (
              roupaBarraEsquerda.x +
              roupaBarraDireita.x
            ) / 2
          }
          ${
            (
              roupaBarraEsquerda.y +
              roupaBarraDireita.y
            ) / 2 + 7
          }

          ${roupaBarraDireita.x}
          ${roupaBarraDireita.y}

          C
          ${
            roupaBarraDireita.x + 4
          }
          ${
            roupaBarraDireita.y - 28
          }

          ${
            roupaAxilaDireita.x + 2
          }
          ${
            roupaAxilaDireita.y + 28
          }

          ${roupaAxilaDireita.x}
          ${roupaAxilaDireita.y}

          Q
          ${
            (
              mangaDireitaExterna.x +
              roupaAxilaDireita.x
            ) / 2 + 2
          }
          ${
            (
              mangaDireitaExterna.y +
              roupaAxilaDireita.y
            ) / 2 + 8
          }

          ${mangaDireitaExterna.x}
          ${mangaDireitaExterna.y}

          Q
          ${
            (
              roupaOmbroDireito.x +
              mangaDireitaExterna.x
            ) / 2
          }
          ${
            (
              roupaOmbroDireito.y +
              mangaDireitaExterna.y
            ) / 2 - 2
          }

          ${roupaOmbroDireito.x}
          ${roupaOmbroDireito.y}

          Q
          ${
            (
              roupaGolaDireita.x +
              roupaOmbroDireito.x
            ) / 2
          }
          ${
            roupaGolaDireita.y - 3
          }

          ${roupaGolaDireita.x}
          ${roupaGolaDireita.y}

          Q
          ${
            (
              roupaGolaDireita.x +
              roupaGolaEsquerda.x
            ) / 2
          }
          ${
            (
              roupaGolaDireita.y +
              roupaGolaEsquerda.y
            ) / 2 + 18
          }

          ${roupaGolaEsquerda.x}
          ${roupaGolaEsquerda.y}

          Z
        `}
        fill="#16c8b4"
        stroke="#7fffea"
        strokeWidth="3"
        strokeLinejoin="round"
        opacity="0.94"
      />
    </g>
  )
}

export default CamisetaRenderer2D
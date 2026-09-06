import CalcaRenderer2D from "./vestimentas/CalcaRenderer2D"
import CalcadoRenderer2D from "./vestimentas/CalcadoRenderer2D"
import CamisetaRenderer2D from "./vestimentas/CamisetaRenderer2D"
import SaiaRenderer2D from "./vestimentas/SaiaRenderer2D"
import ShortRenderer2D from "./vestimentas/ShortRenderer2D"
import VestidoRenderer2D from "./vestimentas/VestidoRenderer2D"



function AvatarRenderer2D({
  renderer,
  vestimenta,
  caimento,
}) {
  if (
    !renderer ||
    !renderer.pronto ||
    !renderer.pontos
  ) {
    return (
      <div>
        <h2>
          VesteIA — Avatar Renderer 2D
        </h2>

        <p>
          Aguardando geometria corporal...
        </p>
      </div>
    )
  }

  const pontos =
    renderer.pontos

  const pontosRoupaBase =
    vestimenta
      ?.pontos_roupa_no_avatar ??
    {}

  const pontosCaimento =
    caimento
      ?.pontos_caimento ??
    {}

  const usarCaimento =
    caimento
      ?.caimento_simulado === true &&
    caimento
      ?.disponivel === true &&
    Object.keys(
      pontosCaimento
    ).length > 0

  const pontosRoupa =
    usarCaimento
      ? pontosCaimento
      : pontosRoupaBase

  const largura = 500
  const altura = 700

  const margemVisual = 0.08

  const escalaVisual =
    1 - margemVisual * 2

  function ajustarCoordenada(
    valor,
    dimensao
  ) {
    return (
      margemVisual *
        dimensao +
      valor *
        dimensao *
        escalaVisual
    )
  }

  function obterPonto(
    nome
  ) {
    const ponto =
      pontos[nome]

    if (
      !ponto ||
      typeof ponto.x !== "number" ||
      typeof ponto.y !== "number"
    ) {
      return null
    }

    return {
      x:
        ajustarCoordenada(
          ponto.x,
          largura
        ),

      y:
        ajustarCoordenada(
          ponto.y,
          altura
        ),
    }
  }

  function obterPontoRoupa(
    nome
  ) {
    const ponto =
      pontosRoupa[nome]

    if (
      !ponto ||
      typeof ponto.x !== "number" ||
      typeof ponto.y !== "number"
    ) {
      return null
    }

    return {
      x:
        ajustarCoordenada(
          ponto.x,
          largura
        ),

      y:
        ajustarCoordenada(
          ponto.y,
          altura
        ),
    }
  }

  function distancia(
    pontoA,
    pontoB
  ) {
    if (
      !pontoA ||
      !pontoB
    ) {
      return 0
    }

    const dx =
      pontoB.x -
      pontoA.x

    const dy =
      pontoB.y -
      pontoA.y

    return Math.sqrt(
      dx * dx +
      dy * dy
    )
  }

  function pontoIntermediario(
    pontoA,
    pontoB,
    percentual
  ) {
    if (
      !pontoA ||
      !pontoB
    ) {
      return null
    }

    return {
      x:
        pontoA.x +
        (
          pontoB.x -
          pontoA.x
        ) *
          percentual,

      y:
        pontoA.y +
        (
          pontoB.y -
          pontoA.y
        ) *
          percentual,
    }
  }

  function desenharMembro(
    nomeA,
    nomeB,
    espessuraInicial,
    espessuraFinal,
    chave
  ) {
    const pontoA =
      obterPonto(
        nomeA
      )

    const pontoB =
      obterPonto(
        nomeB
      )

    if (
      !pontoA ||
      !pontoB
    ) {
      return null
    }

    const dx =
      pontoB.x -
      pontoA.x

    const dy =
      pontoB.y -
      pontoA.y

    const comprimento =
      Math.sqrt(
        dx * dx +
        dy * dy
      )

    if (
      comprimento === 0
    ) {
      return null
    }

    const normalX =
      -dy /
      comprimento

    const normalY =
      dx /
      comprimento

    const inicioEsquerda = {
      x:
        pontoA.x +
        normalX *
          espessuraInicial /
          2,

      y:
        pontoA.y +
        normalY *
          espessuraInicial /
          2,
    }

    const inicioDireita = {
      x:
        pontoA.x -
        normalX *
          espessuraInicial /
          2,

      y:
        pontoA.y -
        normalY *
          espessuraInicial /
          2,
    }

    const fimEsquerda = {
      x:
        pontoB.x +
        normalX *
          espessuraFinal /
          2,

      y:
        pontoB.y +
        normalY *
          espessuraFinal /
          2,
    }

    const fimDireita = {
      x:
        pontoB.x -
        normalX *
          espessuraFinal /
          2,

      y:
        pontoB.y -
        normalY *
          espessuraFinal /
          2,
    }

    const meioX =
      (
        pontoA.x +
        pontoB.x
      ) /
      2

    const meioY =
      (
        pontoA.y +
        pontoB.y
      ) /
      2

    return (
      <path
        key={chave}
        d={`
          M
          ${inicioEsquerda.x}
          ${inicioEsquerda.y}

          Q
          ${
            meioX +
            normalX *
              espessuraInicial *
              0.12
          }
          ${
            meioY +
            normalY *
              espessuraInicial *
              0.12
          }

          ${fimEsquerda.x}
          ${fimEsquerda.y}

          Q
          ${pontoB.x}
          ${pontoB.y}

          ${fimDireita.x}
          ${fimDireita.y}

          Q
          ${
            meioX -
            normalX *
              espessuraInicial *
              0.12
          }
          ${
            meioY -
            normalY *
              espessuraInicial *
              0.12
          }

          ${inicioDireita.x}
          ${inicioDireita.y}

          Q
          ${pontoA.x}
          ${pontoA.y}

          ${inicioEsquerda.x}
          ${inicioEsquerda.y}

          Z
        `}
        fill="#5b55e8"
        stroke="#8b5cf6"
        strokeWidth="2"
        strokeLinejoin="round"
        opacity="0.96"
      />
    )
  }

  /*
   * PONTOS DO CORPO
   */

  const ombroEsquerdo =
    obterPonto(
      "ombro_esquerdo"
    )

  const ombroDireito =
    obterPonto(
      "ombro_direito"
    )

  const quadrilEsquerdo =
    obterPonto(
      "quadril_esquerdo"
    )

  const quadrilDireito =
    obterPonto(
      "quadril_direito"
    )

  const nariz =
    obterPonto(
      "nariz"
    )

  const orelhaEsquerda =
    obterPonto(
      "orelha_esquerda"
    )

  const orelhaDireita =
    obterPonto(
      "orelha_direita"
    )

  const punhoEsquerdo =
    obterPonto(
      "punho_esquerdo"
    )

  const punhoDireito =
    obterPonto(
      "punho_direito"
    )

  const tornozeloEsquerdo =
    obterPonto(
      "tornozelo_esquerdo"
    )

  const tornozeloDireito =
    obterPonto(
      "tornozelo_direito"
    )

  const calcanharEsquerdo =
    obterPonto(
      "calcanhar_esquerdo"
    )

  const calcanharDireito =
    obterPonto(
      "calcanhar_direito"
    )

  const pontaPeEsquerdo =
    obterPonto(
      "ponta_pe_esquerdo"
    )

  const pontaPeDireito =
    obterPonto(
      "ponta_pe_direito"
    )

  /*
   * PONTOS DA CAMISETA
   */

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

  /*
   * DISPONIBILIDADE GENÉRICA DA ROUPA
   *
   * Agora não depende mais
   * especificamente dos pontos
   * da camiseta.
   */

  const roupaDisponivel =
    vestimenta?.disponivel === true &&
    vestimenta?.vestida_no_avatar === true &&
    Object.keys(
      pontosRoupa
    ).length > 0

  /*
   * CONTRATO ESPECÍFICO DA CAMISETA
   */

  const camisetaDisponivel =
    roupaDisponivel &&
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

  /*
   * GEOMETRIA DO CORPO
   */

  const troncoDisponivel =
    ombroEsquerdo &&
    ombroDireito &&
    quadrilEsquerdo &&
    quadrilDireito

  const larguraOmbros =
    distancia(
      ombroEsquerdo,
      ombroDireito
    )

  const larguraQuadril =
    distancia(
      quadrilEsquerdo,
      quadrilDireito
    )

  const centroOmbros =
    troncoDisponivel
      ? {
          x:
            (
              ombroEsquerdo.x +
              ombroDireito.x
            ) /
            2,

          y:
            (
              ombroEsquerdo.y +
              ombroDireito.y
            ) /
            2,
        }
      : null

  const centroQuadril =
    troncoDisponivel
      ? {
          x:
            (
              quadrilEsquerdo.x +
              quadrilDireito.x
            ) /
            2,

          y:
            (
              quadrilEsquerdo.y +
              quadrilDireito.y
            ) /
            2,
        }
      : null

  const cinturaEsquerda =
    troncoDisponivel
      ? pontoIntermediario(
          ombroEsquerdo,
          quadrilEsquerdo,
          0.64
        )
      : null

  const cinturaDireita =
    troncoDisponivel
      ? pontoIntermediario(
          ombroDireito,
          quadrilDireito,
          0.64
        )
      : null

  /*
   * CABEÇA E PESCOÇO
   */

  const larguraCabeca =
    orelhaEsquerda &&
    orelhaDireita
      ? Math.max(
          42,
          Math.abs(
            orelhaEsquerda.x -
            orelhaDireita.x
          ) *
            1.65
        )
      : 60

  const alturaCabeca =
    larguraCabeca *
    1.28

  const centroCabecaX =
    orelhaEsquerda &&
    orelhaDireita
      ? (
          orelhaEsquerda.x +
          orelhaDireita.x
        ) /
        2
      : nariz?.x ??
        largura / 2

  const centroCabecaY =
    nariz
      ? nariz.y -
        alturaCabeca *
          0.08
      : 70

  const baseCabecaY =
    centroCabecaY +
    alturaCabeca /
      2

  const larguraPescoco =
    larguraOmbros
      ? Math.max(
          22,
          larguraOmbros *
            0.2
        )
      : 28

  const topoPescocoY =
    baseCabecaY -
    2

  const basePescocoY =
    centroOmbros
      ? centroOmbros.y +
        larguraOmbros *
          0.035
      : topoPescocoY +
        28

  const centroPescocoX =
    centroOmbros?.x ??
    centroCabecaX

  const larguraMao =
    Math.max(
      10,
      larguraOmbros *
        0.075
    )

  const larguraPe =
    Math.max(
      16,
      larguraQuadril *
        0.18
    )

  const deslocamentoOmbro =
    larguraOmbros *
    0.07

  /*
   * RENDERER DA CAMISETA
   */

  function renderizarCamiseta() {
    if (
      !camisetaDisponivel
    ) {
      return null
    }

    return (
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
    )
  }

  /*
   * NORMALIZAÇÃO DA CATEGORIA
   */

  function normalizarCategoria(
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
   * ROTEADOR DE VESTIMENTA
   *
   * Sprint 52:
   *
   * camiseta → renderer existente
   * calça → CalcaRenderer2D
   *
   * Demais categorias serão
   * adicionadas progressivamente.
   */

  function renderizarVestimenta() {
    const categoriaNormalizada =
      normalizarCategoria(
        vestimenta
          ?.produto
          ?.categoria ??
        vestimenta
          ?.categoria
      )

    switch (
      categoriaNormalizada
    ) {
      case "camiseta":
      case "camisetas":
        return (
          <CamisetaRenderer2D
            pontos={
              pontosRoupa
            }
            obterPontoRoupa={
              obterPontoRoupa
            }
            disponivel={
              roupaDisponivel
            }
          />
        )

      case "camisa":
      case "camisas":
        return null

      case "regata":
      case "regatas":
        return null

      case "calca":
      case "calcas":
        return (
          <CalcaRenderer2D
            pontos={
              pontosRoupa
            }
            obterPontoRoupa={
              obterPontoRoupa
            }
            disponivel={
              roupaDisponivel
            }
          />
        )

      case "short":
      case "shorts":
      case "bermuda":
      case "bermudas":
        return null

      case "saia":
      case "saias":
        return (
          <SaiaRenderer2D
            pontos={
              pontosRoupa
            }
            obterPontoRoupa={
              obterPontoRoupa
            }
            disponivel={
              roupaDisponivel
            }
          />
        )

      case "vestido":
      case "vestidos":
        return null

      case "macacao":
      case "macacoes":
        return null

      case "jaqueta":
      case "jaquetas":
      case "casaco":
      case "casacos":
        return null

      case "tenis":
      case "sapato":
      case "sapatos":
      case "bota":
      case "botas":
      case "calcado":
      case "calcados":
        return null

      case "meia":
      case "meias":
        return null

      default:
        return null
    }
  }

  /*
   * CONTAGEM DINÂMICA DOS
   * PONTOS DA VESTIMENTA
   */

  const quantidadePontosRoupa =
    Object.values(
      pontosRoupa
    ).filter(
      ponto =>
        ponto &&
        typeof ponto.x === "number" &&
        typeof ponto.y === "number"
    ).length

  const totalPontosRoupa =
    vestimenta
      ?.qualidade
      ?.total_pontos ??
    quantidadePontosRoupa

  return (
    <div>

      <h2>
        VesteIA — Avatar Renderer 2D
      </h2>

      <svg
        viewBox="0 0 500 700"
        width="500"
        height="700"
        role="img"
        aria-label="Avatar corporal vestido pelo VesteIA"
      >

        <rect
          x="0"
          y="0"
          width="500"
          height="700"
          fill="#111318"
        />

        {/* BRAÇOS */}

        {desenharMembro(
          "ombro_esquerdo",
          "cotovelo_esquerdo",
          31,
          24,
          "braco-esquerdo-superior"
        )}

        {desenharMembro(
          "cotovelo_esquerdo",
          "punho_esquerdo",
          24,
          16,
          "braco-esquerdo-inferior"
        )}

        {desenharMembro(
          "ombro_direito",
          "cotovelo_direito",
          31,
          24,
          "braco-direito-superior"
        )}

        {desenharMembro(
          "cotovelo_direito",
          "punho_direito",
          24,
          16,
          "braco-direito-inferior"
        )}

        {/* PERNAS */}

        {desenharMembro(
          "quadril_esquerdo",
          "joelho_esquerdo",
          39,
          30,
          "coxa-esquerda"
        )}

        {desenharMembro(
          "joelho_esquerdo",
          "tornozelo_esquerdo",
          30,
          19,
          "perna-esquerda"
        )}

        {desenharMembro(
          "quadril_direito",
          "joelho_direito",
          39,
          30,
          "coxa-direita"
        )}

        {desenharMembro(
          "joelho_direito",
          "tornozelo_direito",
          30,
          19,
          "perna-direita"
        )}

        {/* CORPO */}

        {troncoDisponivel && (
          <path
            d={`
              M
              ${
                ombroEsquerdo.x +
                deslocamentoOmbro
              }
              ${
                ombroEsquerdo.y -
                deslocamentoOmbro *
                  0.18
              }

              C
              ${
                ombroEsquerdo.x +
                larguraOmbros *
                  0.02
              }
              ${
                ombroEsquerdo.y +
                larguraOmbros *
                  0.08
              }

              ${
                cinturaEsquerda.x -
                larguraOmbros *
                  0.045
              }
              ${
                cinturaEsquerda.y -
                larguraOmbros *
                  0.06
              }

              ${cinturaEsquerda.x}
              ${cinturaEsquerda.y}

              C
              ${
                cinturaEsquerda.x +
                larguraQuadril *
                  0.02
              }
              ${
                cinturaEsquerda.y +
                larguraQuadril *
                  0.12
              }

              ${
                quadrilEsquerdo.x -
                larguraQuadril *
                  0.025
              }
              ${
                quadrilEsquerdo.y -
                larguraQuadril *
                  0.06
              }

              ${quadrilEsquerdo.x}
              ${quadrilEsquerdo.y}

              C
              ${
                quadrilEsquerdo.x +
                larguraQuadril *
                  0.18
              }
              ${
                quadrilEsquerdo.y +
                larguraQuadril *
                  0.07
              }

              ${
                quadrilDireito.x -
                larguraQuadril *
                  0.18
              }
              ${
                quadrilDireito.y +
                larguraQuadril *
                  0.07
              }

              ${quadrilDireito.x}
              ${quadrilDireito.y}

              C
              ${
                quadrilDireito.x +
                larguraQuadril *
                  0.025
              }
              ${
                quadrilDireito.y -
                larguraQuadril *
                  0.06
              }

              ${
                cinturaDireita.x -
                larguraQuadril *
                  0.02
              }
              ${
                cinturaDireita.y +
                larguraQuadril *
                  0.12
              }

              ${cinturaDireita.x}
              ${cinturaDireita.y}

              C
              ${
                cinturaDireita.x +
                larguraOmbros *
                  0.045
              }
              ${
                cinturaDireita.y -
                larguraOmbros *
                  0.06
              }

              ${
                ombroDireito.x -
                larguraOmbros *
                  0.02
              }
              ${
                ombroDireito.y +
                larguraOmbros *
                  0.08
              }

              ${
                ombroDireito.x -
                deslocamentoOmbro
              }
              ${
                ombroDireito.y -
                deslocamentoOmbro *
                  0.18
              }

              C
              ${
                centroOmbros.x +
                larguraPescoco /
                  2
              }
              ${
                centroOmbros.y -
                larguraOmbros *
                  0.02
              }

              ${
                centroPescocoX +
                larguraPescoco /
                  2
              }
              ${basePescocoY}

              ${centroPescocoX}
              ${basePescocoY}

              C
              ${
                centroPescocoX -
                larguraPescoco /
                  2
              }
              ${basePescocoY}

              ${
                centroOmbros.x -
                larguraPescoco /
                  2
              }
              ${
                centroOmbros.y -
                larguraOmbros *
                  0.02
              }

              ${
                ombroEsquerdo.x +
                deslocamentoOmbro
              }
              ${
                ombroEsquerdo.y -
                deslocamentoOmbro *
                  0.18
              }

              Z
            `}
            fill="#4f46e5"
            stroke="#8b5cf6"
            strokeWidth="3"
            opacity="0.92"
          />
        )}

        {/* VESTIMENTA */}

        {renderizarVestimenta()}

        {/* PESCOÇO */}

        <path
          d={`
            M
            ${
              centroPescocoX -
              larguraPescoco /
                2
            }
            ${topoPescocoY}

            L
            ${
              centroPescocoX -
              larguraPescoco /
                2
            }
            ${basePescocoY}

            L
            ${
              centroPescocoX +
              larguraPescoco /
                2
            }
            ${basePescocoY}

            L
            ${
              centroPescocoX +
              larguraPescoco /
                2
            }
            ${topoPescocoY}

            Z
          `}
          fill="#5750df"
          stroke="#8b5cf6"
          strokeWidth="2"
        />

        {/* CABEÇA */}

        <ellipse
          cx={centroCabecaX}
          cy={centroCabecaY}
          rx={
            larguraCabeca /
            2
          }
          ry={
            alturaCabeca /
            2
          }
          fill="#5750df"
          stroke="#8b5cf6"
          strokeWidth="3"
        />

        {/* MÃOS */}

        {punhoEsquerdo && (
          <ellipse
            cx={
              punhoEsquerdo.x
            }
            cy={
              punhoEsquerdo.y +
              larguraMao *
                0.32
            }
            rx={
              larguraMao *
              0.5
            }
            ry={
              larguraMao *
              0.9
            }
            fill="#5b55e8"
            stroke="#8b5cf6"
            strokeWidth="2"
          />
        )}

        {punhoDireito && (
          <ellipse
            cx={
              punhoDireito.x
            }
            cy={
              punhoDireito.y +
              larguraMao *
                0.32
            }
            rx={
              larguraMao *
              0.5
            }
            ry={
              larguraMao *
              0.9
            }
            fill="#5b55e8"
            stroke="#8b5cf6"
            strokeWidth="2"
          />
        )}

        {/* PÉS */}

        {tornozeloEsquerdo &&
          calcanharEsquerdo &&
          pontaPeEsquerdo && (
          <path
            d={`
              M
              ${
                tornozeloEsquerdo.x -
                larguraPe *
                  0.4
              }
              ${tornozeloEsquerdo.y}

              C
              ${calcanharEsquerdo.x}
              ${
                calcanharEsquerdo.y +
                3
              }

              ${
                pontaPeEsquerdo.x -
                larguraPe *
                  0.25
              }
              ${pontaPeEsquerdo.y}

              ${pontaPeEsquerdo.x}
              ${pontaPeEsquerdo.y}

              C
              ${
                pontaPeEsquerdo.x +
                larguraPe *
                  0.32
              }
              ${
                pontaPeEsquerdo.y -
                2
              }

              ${
                tornozeloEsquerdo.x +
                larguraPe *
                  0.42
              }
              ${
                tornozeloEsquerdo.y +
                9
              }

              ${
                tornozeloEsquerdo.x +
                larguraPe *
                  0.35
              }
              ${tornozeloEsquerdo.y}

              Z
            `}
            fill="#5b55e8"
            stroke="#8b5cf6"
            strokeWidth="2"
          />
        )}

        {tornozeloDireito &&
          calcanharDireito &&
          pontaPeDireito && (
          <path
            d={`
              M
              ${
                tornozeloDireito.x -
                larguraPe *
                  0.4
              }
              ${tornozeloDireito.y}

              C
              ${calcanharDireito.x}
              ${
                calcanharDireito.y +
                3
              }

              ${
                pontaPeDireito.x -
                larguraPe *
                  0.25
              }
              ${pontaPeDireito.y}

              ${pontaPeDireito.x}
              ${pontaPeDireito.y}

              C
              ${
                pontaPeDireito.x +
                larguraPe *
                  0.32
              }
              ${
                pontaPeDireito.y -
                2
              }

              ${
                tornozeloDireito.x +
                larguraPe *
                  0.42
              }
              ${
                tornozeloDireito.y +
                9
              }

              ${
                tornozeloDireito.x +
                larguraPe *
                  0.35
              }
              ${tornozeloDireito.y}

              Z
            `}
            fill="#5b55e8"
            stroke="#8b5cf6"
            strokeWidth="2"
          />
        )}

        {/* LANDMARKS DO CORPO */}

        {Object.entries(
          pontos
        ).map(
          ([
            nome,
            ponto,
          ]) => {
            if (
              typeof ponto?.x !==
                "number" ||
              typeof ponto?.y !==
                "number"
            ) {
              return null
            }

            return (
              <circle
                key={nome}
                cx={
                  ajustarCoordenada(
                    ponto.x,
                    largura
                  )
                }
                cy={
                  ajustarCoordenada(
                    ponto.y,
                    altura
                  )
                }
                r="2.2"
                fill="#ffffff"
                opacity="0.30"
              />
            )
          }
        )}

        {/* PONTOS DA ROUPA */}

        {roupaDisponivel &&
          Object.entries(
            pontosRoupa
          ).map(
            ([
              nome,
              ponto,
            ]) => {
              if (
                typeof ponto?.x !==
                  "number" ||
                typeof ponto?.y !==
                  "number"
              ) {
                return null
              }

              return (
                <circle
                  key={`roupa-${nome}`}
                  cx={
                    ajustarCoordenada(
                      ponto.x,
                      largura
                    )
                  }
                  cy={
                    ajustarCoordenada(
                      ponto.y,
                      altura
                    )
                  }
                  r="3"
                  fill="#ffffff"
                  stroke="#16c8b4"
                  strokeWidth="1.5"
                />
              )
            }
          )}

      </svg>

      <p>
        Avatar corporal 2D
        construído a partir da
        geometria detectada na foto.
      </p>

      <small>
        {
          renderer
            ?.qualidade
            ?.pontos_disponiveis ??
          0
        }
        {" / "}
        {
          renderer
            ?.qualidade
            ?.total_pontos ??
          0
        }
        {" pontos corporais disponíveis"}
      </small>

      <br />

      <small>
        {roupaDisponivel
          ? usarCaimento
            ? `${quantidadePontosRoupa} / ${totalPontosRoupa} pontos da roupa — caimento visual aplicado (${caimento?.modelagem ?? "modelagem padrão"} / ${caimento?.preferencia_caimento ?? "padrão"})`
            : `${quantidadePontosRoupa} / ${totalPontosRoupa} pontos da roupa — vestimenta posicionada no avatar`
          : "Vestimenta visual ainda não disponível"}
      </small>

    </div>
  )
}

export default AvatarRenderer2D

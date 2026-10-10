import { useMemo } from "react"


function AvatarRenderer3D({
  avatar,
  produto = null,
  tamanhoSelecionado = null,
  vestibilidade = null,
}) {
  /*
   * VesteIA
   * Sprint 53 — Avatar Humanoide + Vestibilidade Dinâmica V4
   *
   * Responsabilidades:
   *
   * - representar o perfil aproximado criado no AvatarBuilder;
   * - suportar avatar masculino e feminino;
   * - responder a altura, peso, porte, tronco e pernas;
   * - receber produto e tamanho;
   * - receber a vestibilidade calculada pelo backend;
   * - modificar a geometria visual da roupa;
   * - manter o fluxo por avatar separado do AvatarRenderer2D;
   *
   * IMPORTANTE:
   *
   * Esta representação continua aproximada.
   * Não utiliza medidas corporais reais,
   * colisão física, gravidade ou simulação real de tecido.
   */


  const perfil = avatar ?? {
    modo: "avatar",
    origem: "estimativa_usuario",

    genero: "masculino",

    altura_aproximada_cm: 175,
    peso_aproximado_kg: 75,

    porte_corporal: "medio",

    proporcao_tronco: "media",
    proporcao_pernas: "media",
  }


  const genero =
    perfil.genero === "feminino"
      ? "feminino"
      : "masculino"


  // =========================================================
  // UTILITÁRIOS
  // =========================================================

  function limitar(
    valor,
    minimo,
    maximo
  ) {
    return Math.min(
      maximo,
      Math.max(
        minimo,
        valor
      )
    )
  }


  // =========================================================
  // SPRINT 53
  // VESTIBILIDADE RECEBIDA DO BACKEND
  // =========================================================

  const classificacaoVestibilidade =
    vestibilidade
      ?.classificacao ??
    vestibilidade
      ?.vestibilidadeVisual
      ?.classificacao ??
    vestibilidade
      ?.respostaCompleta
      ?.vestibilidade_visual
      ?.classificacao ??
    "equilibrado"


  /*
   * O backend atualmente devolve valores como:
   *
   * amplo:
   * horizontal 1.12
   * vertical   0.96
   *
   * equilibrado:
   * horizontal 1.00
   * vertical   1.00
   *
   * mais_justo:
   * horizontal 0.88
   * vertical   1.04
   */


  const fatorVestibilidadeHorizontal =
    useMemo(() => {
      const valor =
        Number(
          vestibilidade
            ?.multiplicadorHorizontal ??
          vestibilidade
            ?.fatorHorizontal ??
          vestibilidade
            ?.integracaoCaimentoVisual
            ?.multiplicador_horizontal_avatar ??
          vestibilidade
            ?.vestibilidadeVisual
            ?.fator_horizontal_relativo ??
          1
        ) || 1

      return limitar(
        valor,
        0.82,
        1.18
      )
    }, [
      vestibilidade,
    ])


  const fatorVestibilidadeVertical =
    useMemo(() => {
      const valor =
        Number(
          vestibilidade
            ?.multiplicadorVertical ??
          vestibilidade
            ?.fatorVertical ??
          vestibilidade
            ?.integracaoCaimentoVisual
            ?.multiplicador_vertical_avatar ??
          vestibilidade
            ?.vestibilidadeVisual
            ?.fator_vertical_relativo ??
          1
        ) || 1

      return limitar(
        valor,
        0.9,
        1.1
      )
    }, [
      vestibilidade,
    ])




  /*
   * Além da escala geral da roupa,
   * criamos parâmetros geométricos.
   *
   * Isso permitirá que a camiseta não pareça
   * apenas uma imagem esticada.
   */


  // =========================================================
  // ALTURA DO AVATAR
  // =========================================================

  const escalaAltura =
    useMemo(() => {
      const altura =
        Number(
          perfil
            .altura_aproximada_cm
        ) || 175

      return Math.min(
        1.16,
        Math.max(
          0.84,
          altura / 175
        )
      )
    }, [
      perfil
        .altura_aproximada_cm,
    ])


  // =========================================================
  // PESO + PORTE
  // =========================================================

  const escalaLargura =
    useMemo(() => {
      const peso =
        Number(
          perfil
            .peso_aproximado_kg
        ) || 75

      let escalaPeso =
        1 +
        (
          peso -
          75
        ) *
          0.0032


      escalaPeso =
        Math.min(
          1.23,
          Math.max(
            0.82,
            escalaPeso
          )
        )


      const portes = {
        estreito: 0.9,
        medio: 1,
        largo: 1.1,
      }


      return (
        escalaPeso *
        (
          portes[
            perfil
              .porte_corporal
          ] ?? 1
        )
      )
    }, [
      perfil
        .peso_aproximado_kg,

      perfil
        .porte_corporal,
    ])


  // =========================================================
  // OMBROS
  // =========================================================

  const escalaOmbros =
    useMemo(() => {
      const portes = {
        estreito: 0.9,
        medio: 1,
        largo: 1.12,
      }


      const base =
        portes[
          perfil
            .porte_corporal
        ] ?? 1


      return genero ===
        "feminino"
        ? base * 0.94
        : base
    }, [
      perfil
        .porte_corporal,

      genero,
    ])


  // =========================================================
  // QUADRIL
  // =========================================================

  const escalaQuadril =
    useMemo(() => {
      const base =
        perfil
          .porte_corporal ===
        "estreito"
          ? 0.94
          : perfil
                .porte_corporal ===
              "largo"
            ? 1.08
            : 1


      return genero ===
        "feminino"
        ? base * 1.1
        : base
    }, [
      perfil
        .porte_corporal,

      genero,
    ])


  // =========================================================
  // TRONCO
  // =========================================================

  const escalaTronco =
    useMemo(() => {
      const proporcoes = {
        curto: 0.9,
        media: 1,
        longo: 1.1,
      }


      return (
        proporcoes[
          perfil
            .proporcao_tronco
        ] ?? 1
      )
    }, [
      perfil
        .proporcao_tronco,
    ])


  // =========================================================
  // PERNAS
  // =========================================================

  const escalaPernas =
    useMemo(() => {
      const proporcoes = {
        curtas: 0.9,
        media: 1,
        longas: 1.1,
      }


      return (
        proporcoes[
          perfil
            .proporcao_pernas
        ] ?? 1
      )
    }, [
      perfil
        .proporcao_pernas,
    ])


  // =========================================================
  // TIPO DA ROUPA
  // =========================================================

  const categoriaProduto =
    produto
      ?.categoria
      ?.toLowerCase()
      ?.trim() ?? ""


  const tipoRoupa =
    useMemo(() => {
      if (
        categoriaProduto
          .includes(
            "camiseta"
          ) ||
        categoriaProduto
          .includes(
            "camisa"
          )
      ) {
        return "superior"
      }


      if (
        categoriaProduto
          .includes(
            "calça"
          ) ||
        categoriaProduto
          .includes(
            "calca"
          )
      ) {
        return "calca"
      }


      if (
        categoriaProduto
          .includes(
            "short"
          ) ||
        categoriaProduto
          .includes(
            "bermuda"
          )
      ) {
        return "short"
      }


      if (
        categoriaProduto
          .includes(
            "saia"
          )
      ) {
        return "saia"
      }


      if (
        categoriaProduto
          .includes(
            "vestido"
          )
      ) {
        return "vestido"
      }


      return "generica"
    }, [
      categoriaProduto,
    ])


  // =========================================================
  // SPRINT 53 V3
  // TAMANHO VISUAL DA VARIANTE REAL DO PRODUTO
  // =========================================================
  /*
   * A troca P/M/G/GG já muda a variante real do catálogo.
   * Agora usamos as dimensões DA PEÇA selecionada para que
   * a geometria visual também mude no mesmo avatar.
   *
   * IMPORTANTE:
   * - largura_cm/comprimento_cm continuam sendo metadados
   *   físicos da PEÇA, nunca medidas do corpo;
   * - os fatores abaixo são apenas uma normalização visual;
   * - não existe conversão universal P/M/G;
   * - se a variante não trouxer dimensões, o fator fica 1.
   */

  const dimensoesProduto =
    useMemo(() => {
      const largura =
        Number(
          produto?.largura_cm ??
          produto?.dimensoes?.largura_cm ??
          produto?.dimensoes?.largura ??
          produto?.medidas?.largura_cm ??
          produto?.medidas?.largura
        )

      const comprimento =
        Number(
          produto?.comprimento_cm ??
          produto?.dimensoes?.comprimento_cm ??
          produto?.dimensoes?.comprimento ??
          produto?.medidas?.comprimento_cm ??
          produto?.medidas?.comprimento
        )

      return {
        largura:
          Number.isFinite(largura) &&
          largura > 0
            ? largura
            : null,

        comprimento:
          Number.isFinite(comprimento) &&
          comprimento > 0
            ? comprimento
            : null,
      }
    }, [
      produto,
    ])


  const escalaVisualTamanhoProduto =
    useMemo(() => {
      /*
       * Sprint 53 V4
       *
       * A normalização visual agora respeita a família da peça.
       *
       * IMPORTANTE:
       * - as referências abaixo são âncoras VISUAIS do renderer;
       * - não representam medidas do corpo;
       * - não convertem grade (P/M/G, 34/36/38 etc.);
       * - a fonte continua sendo a dimensão real da VARIANTE;
       * - se a variante não trouxer dimensões, o fator fica 1.
       */

      if (
        tipoRoupa === "superior"
      ) {
        const referenciaVisualLargura = 55
        const referenciaVisualComprimento = 70

        return {
          horizontal:
            dimensoesProduto.largura
              ? limitar(
                  1 +
                    (
                      dimensoesProduto.largura -
                      referenciaVisualLargura
                    ) /
                      85,
                  0.88,
                  1.14
                )
              : 1,

          vertical:
            dimensoesProduto.comprimento
              ? limitar(
                  1 +
                    (
                      dimensoesProduto.comprimento -
                      referenciaVisualComprimento
                    ) /
                      120,
                  0.92,
                  1.1
                )
              : 1,
        }
      }


      if (
        tipoRoupa === "calca"
      ) {
        /*
         * Para calça a largura atua principalmente em
         * cintura/quadril/pernas, enquanto o comprimento
         * atua no eixo vertical da peça.
         *
         * São fatores visuais suaves: não há equivalência
         * métrica entre a peça e o corpo do avatar.
         */

        const referenciaVisualLarguraCalca = 42
        const referenciaVisualComprimentoCalca = 104

        return {
          horizontal:
            dimensoesProduto.largura
              ? limitar(
                  1 +
                    (
                      dimensoesProduto.largura -
                      referenciaVisualLarguraCalca
                    ) /
                      70,
                  0.86,
                  1.16
                )
              : 1,

          vertical:
            dimensoesProduto.comprimento
              ? limitar(
                  1 +
                    (
                      dimensoesProduto.comprimento -
                      referenciaVisualComprimentoCalca
                    ) /
                      150,
                  0.9,
                  1.12
                )
              : 1,
        }
      }


      return {
        horizontal: 1,
        vertical: 1,
      }
    }, [
      tipoRoupa,
      dimensoesProduto,
    ])

  const fatorRoupaHorizontal =
    useMemo(
      () =>
        limitar(
          fatorVestibilidadeHorizontal *
            escalaVisualTamanhoProduto
              .horizontal,
          0.78,
          1.24
        ),
      [
        fatorVestibilidadeHorizontal,
        escalaVisualTamanhoProduto,
      ]
    )


  const fatorRoupaVertical =
    useMemo(
      () =>
        limitar(
          fatorVestibilidadeVertical *
            escalaVisualTamanhoProduto
              .vertical,
          0.86,
          1.18
        ),
      [
        fatorVestibilidadeVertical,
        escalaVisualTamanhoProduto,
      ]
    )


  const geometriaVestibilidade =
    useMemo(() => {
      const diferencaHorizontal =
        fatorRoupaHorizontal - 1

      const diferencaVertical =
        fatorRoupaVertical - 1


      /*
       * Folga lateral:
       *
       * amplo       → positivo
       * equilibrado → próximo de zero
       * mais_justo  → negativo
       */

      const folgaLateralPx =
        limitar(
          diferencaHorizontal * 46,
          -8,
          8
        )


      /*
       * Afastamento das mangas.
       */

      const afastamentoMangaPx =
        limitar(
          diferencaHorizontal * 25,
          -5,
          5
        )


      /*
       * Abertura da barra.
       */

      const aberturaBarraPx =
        limitar(
          diferencaHorizontal * 38,
          -7,
          7
        )


      /*
       * Comprimento adicional/reduzido.
       */

      const ajusteComprimentoPx =
        limitar(
          diferencaVertical * 55,
          -6,
          6
        )


      /*
       * Intensidade visual de tensão.
       *
       * 0 = folgado/neutro
       * próximo de 1 = mais justo
       */

      const tensao =
        limitar(
          (1 -
            fatorRoupaHorizontal) *
            5,
          0,
          1
        )


      /*
       * Intensidade visual de folga.
       */

      const folga =
        limitar(
          (
            fatorRoupaHorizontal -
            1
          ) * 5,
          0,
          1
        )


      return {
        folgaLateralPx,

        afastamentoMangaPx,

        aberturaBarraPx,

        ajusteComprimentoPx,

        tensao,

        folga,
      }
    }, [
      fatorRoupaHorizontal,
      fatorRoupaVertical,
    ])





  // =========================================================
  // SPRINT 53 V4
  // GEOMETRIA DINÂMICA DA CALÇA
  // =========================================================

  const geometriaCalca =
    useMemo(() => {
      if (
        tipoRoupa !== "calca"
      ) {
        return {
          larguraContainerPx: 76,
          alturaContainerPx: 178,
          larguraPernaPx: 31,
          alturaPernaPx: 150,
          afastamentoPernaPx: 5,
          aberturaBarraPx: 0,
        }
      }

      const diferencaHorizontal =
        fatorRoupaHorizontal - 1

      const diferencaVertical =
        fatorRoupaVertical - 1

      /*
       * A cintura/quadril cresce de maneira suave.
       */
      const larguraContainerPx =
        limitar(
          76 *
            (
              1 +
              diferencaHorizontal * 0.72
            ),
          66,
          90
        )

      /*
       * O comprimento da calça acompanha a variante,
       * sem alterar o comprimento das pernas do avatar.
       */
      const alturaContainerPx =
        limitar(
          178 *
            (
              1 +
              diferencaVertical * 0.72
            ),
          160,
          198
        )

      /*
       * Folga das pernas.
       */
      const larguraPernaPx =
        limitar(
          31 *
            (
              1 +
              diferencaHorizontal * 0.82
            ),
          26,
          37
        )

      const alturaPernaPx =
        limitar(
          150 *
            (
              1 +
              diferencaVertical * 0.72
            ),
          136,
          168
        )

      /*
       * Quanto mais ampla a peça, mais as duas pernas
       * podem se afastar visualmente. Em peça mais justa,
       * aproximam-se levemente.
       */
      const afastamentoPernaPx =
        limitar(
          5 +
            diferencaHorizontal * 18,
          2,
          8
        )

      /*
       * Gancho para a próxima evolução de barra/modelagem.
       */
      const aberturaBarraPx =
        limitar(
          diferencaHorizontal * 18,
          -3,
          3
        )

      return {
        larguraContainerPx,
        alturaContainerPx,
        larguraPernaPx,
        alturaPernaPx,
        afastamentoPernaPx,
        aberturaBarraPx,
      }
    }, [
      tipoRoupa,
      fatorRoupaHorizontal,
      fatorRoupaVertical,
    ])


  // =========================================================
  // VARIÁVEIS VISUAIS
  // =========================================================

  const estiloAvatar = {
    /*
     * Corpo
     */

    "--avatar-altura":
      escalaAltura,

    "--avatar-largura":
      escalaLargura,

    "--avatar-ombros":
      escalaOmbros,

    "--avatar-quadril":
      escalaQuadril,

    "--avatar-tronco":
      escalaTronco,

    "--avatar-pernas":
      escalaPernas,


    /*
     * Sprint 53
     * Escala da vestimenta.
     */

    "--roupa-vestibilidade-x":
      fatorRoupaHorizontal,

    "--roupa-vestibilidade-y":
      fatorRoupaVertical,

    /*
     * Sprint 53 V3
     * Fatores isolados da variante para debug/inspeção.
     */
    "--roupa-tamanho-x":
      escalaVisualTamanhoProduto
        .horizontal,

    "--roupa-tamanho-y":
      escalaVisualTamanhoProduto
        .vertical,


    /*
     * Sprint 53 V4 — calça.
     * Valores em px são apenas geometria de renderização.
     */
    "--calca-largura":
      `${geometriaCalca.larguraContainerPx}px`,

    "--calca-altura":
      `${geometriaCalca.alturaContainerPx}px`,

    "--calca-perna-largura":
      `${geometriaCalca.larguraPernaPx}px`,

    "--calca-perna-altura":
      `${geometriaCalca.alturaPernaPx}px`,

    "--calca-perna-afastamento":
      `${geometriaCalca.afastamentoPernaPx}px`,

    "--calca-barra-abertura":
      `${geometriaCalca.aberturaBarraPx}px`,


    /*
     * Sprint 53 V2
     * Geometria do caimento.
     */

    "--roupa-folga-lateral":
      `${geometriaVestibilidade
        .folgaLateralPx}px`,

    "--roupa-manga-afastamento":
      `${geometriaVestibilidade
        .afastamentoMangaPx}px`,

    "--roupa-barra-abertura":
      `${geometriaVestibilidade
        .aberturaBarraPx}px`,

    "--roupa-ajuste-comprimento":
      `${geometriaVestibilidade
        .ajusteComprimentoPx}px`,

    "--roupa-tensao":
      geometriaVestibilidade
        .tensao,

    "--roupa-folga":
      geometriaVestibilidade
        .folga,
  }


  return (
    <section
      className="vesteia-avatar-renderer3d"
      data-vesteia-componente="avatar-renderer-3d"
    >

      {/* =====================================================
          CABEÇALHO
          ===================================================== */}

      <div className="vesteia-avatar-renderer3d__cabecalho">

        <span>
          AVATAR INTERATIVO
        </span>

        <h2>
          Seu avatar VesteIA
        </h2>

        <p>
          Ajuste seu corpo e visualize
          o caimento da peça em tempo real.
        </p>

      </div>


      {/* =====================================================
          PALCO
          ===================================================== */}

      <div className="vesteia-avatar-renderer3d__palco">

        <div
          className={[
            "vesteia-avatar-renderer3d__avatar",

            `vesteia-avatar-renderer3d__avatar--${genero}`,
          ].join(" ")}
          data-genero={
            genero
          }
          data-vestibilidade={
            classificacaoVestibilidade
          }
          data-tipo-roupa={
            tipoRoupa
          }
          data-tamanho-roupa={
            tamanhoSelecionado ?? ""
          }
          data-largura-peca={
            dimensoesProduto.largura ?? ""
          }
          data-comprimento-peca={
            dimensoesProduto.comprimento ?? ""
          }
          style={
            estiloAvatar
          }
        >

          {/* =================================================
              CABEÇA
              ================================================= */}

          <div className="vesteia-avatar-renderer3d__cabeca">

            <div className="vesteia-avatar-renderer3d__cabelo" />

            <div className="vesteia-avatar-renderer3d__orelha vesteia-avatar-renderer3d__orelha--esquerda" />

            <div className="vesteia-avatar-renderer3d__orelha vesteia-avatar-renderer3d__orelha--direita" />

            <div className="vesteia-avatar-renderer3d__sobrancelhas">
              <i />
              <i />
            </div>

            <div className="vesteia-avatar-renderer3d__olhos">
              <i />
              <i />
            </div>

            <div className="vesteia-avatar-renderer3d__nariz" />

            <div className="vesteia-avatar-renderer3d__boca" />

            <div className="vesteia-avatar-renderer3d__maxilar" />

          </div>


          {/* =================================================
              PESCOÇO
              ================================================= */}

          <div className="vesteia-avatar-renderer3d__pescoco" />


          {/* =================================================
              OMBROS
              ================================================= */}

          <div className="vesteia-avatar-renderer3d__ombros" />


          {/* =================================================
              CORPO SUPERIOR
              ================================================= */}

          <div className="vesteia-avatar-renderer3d__corpo">

            {/* BRAÇO ESQUERDO */}

            <div className="vesteia-avatar-renderer3d__membro-superior vesteia-avatar-renderer3d__membro-superior--esquerdo">

              <div className="vesteia-avatar-renderer3d__deltoide" />

              <div className="vesteia-avatar-renderer3d__braco" />

              <div className="vesteia-avatar-renderer3d__cotovelo" />

              <div className="vesteia-avatar-renderer3d__antebraco" />

              <div className="vesteia-avatar-renderer3d__pulso" />

              <div className="vesteia-avatar-renderer3d__mao" />

            </div>


            {/* =================================================
                TRONCO
                ================================================= */}

            <div className="vesteia-avatar-renderer3d__tronco">

              <div className="vesteia-avatar-renderer3d__peitoral" />


              {genero ===
                "feminino" && (
                <div className="vesteia-avatar-renderer3d__busto" />
              )}


              <div className="vesteia-avatar-renderer3d__torax" />

              <div className="vesteia-avatar-renderer3d__abdomen" />

              <div className="vesteia-avatar-renderer3d__cintura" />


              {/* ===============================================
                  CAMISETA
                  =============================================== */}

              {produto &&
                tipoRoupa ===
                  "superior" && (

                <div
                  className="vesteia-avatar-renderer3d__camiseta"

                  data-caimento={
                    classificacaoVestibilidade
                  }
                  data-fator-tamanho-x={
                    escalaVisualTamanhoProduto
                      .horizontal
                      .toFixed(3)
                  }
                  data-fator-tamanho-y={
                    escalaVisualTamanhoProduto
                      .vertical
                      .toFixed(3)
                  }
                >

                  <div className="vesteia-avatar-renderer3d__gola" />


                  <div className="vesteia-avatar-renderer3d__manga vesteia-avatar-renderer3d__manga--esquerda" />


                  <div className="vesteia-avatar-renderer3d__manga vesteia-avatar-renderer3d__manga--direita" />


                  <div className="vesteia-avatar-renderer3d__camiseta-corpo">

                    {tamanhoSelecionado && (
                      <span>
                        {
                          tamanhoSelecionado
                        }
                      </span>
                    )}

                  </div>

                </div>
              )}


              {/* ===============================================
                  VESTIDO
                  =============================================== */}

              {produto &&
                tipoRoupa ===
                  "vestido" && (

                <div
                  className="vesteia-avatar-renderer3d__vestido"

                  data-caimento={
                    classificacaoVestibilidade
                  }
                >

                  {tamanhoSelecionado && (
                    <span>
                      {
                        tamanhoSelecionado
                      }
                    </span>
                  )}

                </div>
              )}

            </div>


            {/* BRAÇO DIREITO */}

            <div className="vesteia-avatar-renderer3d__membro-superior vesteia-avatar-renderer3d__membro-superior--direito">

              <div className="vesteia-avatar-renderer3d__deltoide" />

              <div className="vesteia-avatar-renderer3d__braco" />

              <div className="vesteia-avatar-renderer3d__cotovelo" />

              <div className="vesteia-avatar-renderer3d__antebraco" />

              <div className="vesteia-avatar-renderer3d__pulso" />

              <div className="vesteia-avatar-renderer3d__mao" />

            </div>

          </div>


          {/* =================================================
              QUADRIL
              ================================================= */}

          <div className="vesteia-avatar-renderer3d__quadril">

            <div className="vesteia-avatar-renderer3d__pelve" />


            {/* SHORT */}

            {produto &&
              tipoRoupa ===
                "short" && (

              <div
                className="vesteia-avatar-renderer3d__short"

                data-caimento={
                  classificacaoVestibilidade
                }
              >
                {
                  tamanhoSelecionado
                }
              </div>
            )}


            {/* SAIA */}

            {produto &&
              tipoRoupa ===
                "saia" && (

              <div
                className="vesteia-avatar-renderer3d__saia"

                data-caimento={
                  classificacaoVestibilidade
                }
              >
                {
                  tamanhoSelecionado
                }
              </div>
            )}

          </div>


          {/* =================================================
              PERNAS
              ================================================= */}

          <div className="vesteia-avatar-renderer3d__pernas">

            {/* PERNA ESQUERDA */}

            <div className="vesteia-avatar-renderer3d__membro-inferior vesteia-avatar-renderer3d__membro-inferior--esquerdo">

              <div className="vesteia-avatar-renderer3d__coxa" />

              <div className="vesteia-avatar-renderer3d__joelho" />

              <div className="vesteia-avatar-renderer3d__panturrilha" />

              <div className="vesteia-avatar-renderer3d__tornozelo" />

              <div className="vesteia-avatar-renderer3d__pe" />

            </div>


            {/* PERNA DIREITA */}

            <div className="vesteia-avatar-renderer3d__membro-inferior vesteia-avatar-renderer3d__membro-inferior--direito">

              <div className="vesteia-avatar-renderer3d__coxa" />

              <div className="vesteia-avatar-renderer3d__joelho" />

              <div className="vesteia-avatar-renderer3d__panturrilha" />

              <div className="vesteia-avatar-renderer3d__tornozelo" />

              <div className="vesteia-avatar-renderer3d__pe" />

            </div>


            {/* =================================================
                CALÇA
                ================================================= */}

            {produto &&
              tipoRoupa ===
                "calca" && (

              <div
                className="vesteia-avatar-renderer3d__calca"

                data-caimento={
                  classificacaoVestibilidade
                }

                data-fator-tamanho-x={
                  escalaVisualTamanhoProduto
                    .horizontal
                    .toFixed(3)
                }

                data-fator-tamanho-y={
                  escalaVisualTamanhoProduto
                    .vertical
                    .toFixed(3)
                }

                style={{
                  width:
                    `${geometriaCalca.larguraContainerPx}px`,

                  height:
                    `${geometriaCalca.alturaContainerPx}px`,

                  transition:
                    "width 280ms ease, height 280ms ease",
                }}
              >

                <div
                  className="vesteia-avatar-renderer3d__calca-perna vesteia-avatar-renderer3d__calca-perna--esquerda"

                  style={{
                    left:
                      `${geometriaCalca.afastamentoPernaPx}px`,

                    width:
                      `${geometriaCalca.larguraPernaPx}px`,

                    height:
                      `${geometriaCalca.alturaPernaPx}px`,

                    transition:
                      "left 280ms ease, width 280ms ease, height 280ms ease",
                  }}
                />

                <div
                  className="vesteia-avatar-renderer3d__calca-perna vesteia-avatar-renderer3d__calca-perna--direita"

                  style={{
                    right:
                      `${geometriaCalca.afastamentoPernaPx}px`,

                    width:
                      `${geometriaCalca.larguraPernaPx}px`,

                    height:
                      `${geometriaCalca.alturaPernaPx}px`,

                    transition:
                      "right 280ms ease, width 280ms ease, height 280ms ease",
                  }}
                />


                {tamanhoSelecionado && (
                  <span>
                    {
                      tamanhoSelecionado
                    }
                  </span>
                )}

              </div>
            )}

          </div>

        </div>


        {/* =====================================================
            SOMBRA
            ===================================================== */}

        <div className="vesteia-avatar-renderer3d__sombra" />


        {/* =====================================================
            BASE
            ===================================================== */}

        <div className="vesteia-avatar-renderer3d__base" />


        {/* =====================================================
            STATUS
            ===================================================== */}

        <div className="vesteia-avatar-renderer3d__status">

          <span>
            Avatar ativo
          </span>

          <small>
            {genero ===
              "feminino"
              ? "Avatar feminino aproximado"
              : "Avatar masculino aproximado"}
          </small>

        </div>

      </div>


      {/* =====================================================
          INFORMAÇÕES
          ===================================================== */}

      <div className="vesteia-avatar-renderer3d__informacoes">

        <div>
          <span>
            Gênero
          </span>

          <strong>
            {genero}
          </strong>
        </div>


        <div>
          <span>
            Altura
          </span>

          <strong>
            {
              perfil
                .altura_aproximada_cm
            } cm
          </strong>
        </div>


        <div>
          <span>
            Peso
          </span>

          <strong>
            {
              perfil
                .peso_aproximado_kg
            } kg
          </strong>
        </div>


        <div>
          <span>
            Porte
          </span>

          <strong>
            {
              perfil
                .porte_corporal
            }
          </strong>
        </div>


        <div>
          <span>
            Tronco
          </span>

          <strong>
            {
              perfil
                .proporcao_tronco
            }
          </strong>
        </div>


        <div>
          <span>
            Pernas
          </span>

          <strong>
            {
              perfil
                .proporcao_pernas
            }
          </strong>
        </div>

      </div>


      {/* =====================================================
          PRODUTO
          ===================================================== */}

      {produto && (

        <div className="vesteia-avatar-renderer3d__produto">

          <span>
            Experimentando
          </span>

          <strong>
            {
              produto.nome
            }
          </strong>


          {tamanhoSelecionado && (

            <small>
              Tamanho selecionado:{" "}
              {
                tamanhoSelecionado
              }
            </small>

          )}

        </div>
      )}

    </section>
  )
}


export default AvatarRenderer3D
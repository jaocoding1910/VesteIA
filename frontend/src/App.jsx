import camisetaOversized from "./assets/produtos/camiseta-oversized.jpeg"

import {
  useEffect,
  useRef,
  useState,
} from "react"

import {
  analisarCapturaProvador,
} from "./services/provadorService"

import "./App.css"


function App() {
  const [
    altura,
    setAltura,
  ] = useState("")

  const [
    peso,
    setPeso,
  ] = useState("")

  const [
    cintura,
    setCintura,
  ] = useState("")

  const [
    preferencia,
    setPreferencia,
  ] = useState("padrao")

  const [
    resultado,
    setResultado,
  ] = useState(null)

  const [
    produtoSelecionado,
    setProdutoSelecionado,
  ] = useState(null)

  const [
    provadorIniciado,
    setProvadorIniciado,
  ] = useState(false)

  const [
    modoExperimentacao,
    setModoExperimentacao,
  ] = useState(null)

  const [
    fotoUsuario,
    setFotoUsuario,
  ] = useState(null)

  const [
    fotoPreview,
    setFotoPreview,
  ] = useState(null)

  const [
    sessaoProvador,
    setSessaoProvador,
  ] = useState(null)

  const [
    enviandoSessao,
    setEnviandoSessao,
  ] = useState(false)

  const [
    analiseCaptura,
    setAnaliseCaptura,
  ] = useState(null)

  const [
    analisandoCaptura,
    setAnalisandoCaptura,
  ] = useState(false)

  const [
    tamanhoVisualSelecionado,
    setTamanhoVisualSelecionado,
  ] = useState(null)

  const [
    alturaVisualSelecionada,
    setAlturaVisualSelecionada,
  ] = useState(null)

  const [
    alturaVisualIncerta,
    setAlturaVisualIncerta,
  ] = useState(false)

  const [
    avatarPreparacaoConcluida,
    setAvatarPreparacaoConcluida,
  ] = useState(false)

  const [
    erro,
    setErro,
  ] = useState("")

  const inputFotoRef =
    useRef(null)


  /*
   * =========================================================
   * CONTRATO PROVADOR V1
   * =========================================================
   */

  const contratoProvador =
    analiseCaptura
      ?.contratoProvador ??
    null

  const produtoProvador =
    contratoProvador
      ?.produto ??
    null

  const analiseProvador =
    contratoProvador
      ?.analise ??
    null

  const recomendacaoProvador =
    contratoProvador
      ?.recomendacao ??
    null

  const caimentoProvador =
    contratoProvador
      ?.caimento ??
    null

  const tamanhosProvador =
    contratoProvador
      ?.tamanhos ??
    []

  const variacoesProvador =
    contratoProvador
      ?.variacoes ??
    []

  const referenciaCorporal =
    contratoProvador
      ?.referencia_corporal ??
    null

  const avatarProvador =
    contratoProvador
      ?.avatar ??
    null

  const comunicacaoProvador =
    contratoProvador
      ?.comunicacao ??
    null


  /*
   * =========================================================
   * SELEÇÃO VISUAL DE TAMANHO
   * =========================================================
   */

  const tamanhoRecomendado =
    recomendacaoProvador
      ?.tamanho ??
    null

  const tamanhoAtivo =
    tamanhoVisualSelecionado ??
    tamanhoRecomendado

  const rankingAtivo =
    tamanhosProvador
      .find(
        (item) =>
          item?.tamanho ===
          tamanhoAtivo
      ) ??
    null

  const variacaoAtiva =
    variacoesProvador
      .find(
        (item) =>
          item?.tamanho ===
          tamanhoAtivo
      ) ??
    null


  /*
   * =========================================================
   * PREPARAÇÃO VISUAL DO AVATAR
   * =========================================================
   */

  const selecaoVisualAltura =
    avatarProvador
      ?.selecao_visual_altura ??
    null

  const candidatosAltura =
    selecaoVisualAltura
      ?.candidatos ??
    []

  const alturaCentralReferencia =
    selecaoVisualAltura
      ?.altura_central_referencia_cm ??
    null

  const referenciaAvatarPronta =
    Boolean(
      alturaVisualSelecionada ||
      alturaVisualIncerta
    )


  /*
   * =========================================================
   * EFEITOS
   * =========================================================
   */

  useEffect(() => {
    return () => {
      if (fotoPreview) {
        URL.revokeObjectURL(
          fotoPreview
        )
      }
    }
  }, [fotoPreview])


  useEffect(() => {
    if (
      modoExperimentacao ===
        "foto" &&
      fotoUsuario &&
      produtoSelecionado &&
      !sessaoProvador &&
      !enviandoSessao
    ) {
      prepararExperiencia()
    }
  }, [fotoUsuario])


  useEffect(() => {
    if (
      recomendacaoProvador
        ?.tamanho
    ) {
      setTamanhoVisualSelecionado(
        recomendacaoProvador
          .tamanho
      )
    }
  }, [
    recomendacaoProvador
      ?.tamanho,
  ])


  /*
   * =========================================================
   * FORMATAÇÕES
   * =========================================================
   */

  function normalizarPreferencia(
    valor
  ) {
    if (!valor) {
      return "padrao"
    }

    const preferenciaNormalizada =
      String(
        valor
      )
        .trim()
        .toLowerCase()

    const mapa = {
      justo: "justo",
      ajustado: "justo",
      slim: "justo",

      padrao: "padrao",
      padrão: "padrao",
      normal: "padrao",
      regular: "padrao",

      solto: "solto",
      amplo: "solto",
      oversized: "solto",
    }

    return (
      mapa[
        preferenciaNormalizada
      ] ?? "padrao"
    )
  }


  function formatarPreferencia(
    valor
  ) {
    const traducoes = {
      justo:
        "Mais justo",

      padrao:
        "Padrão",

      solto:
        "Mais solto",
    }

    return (
      traducoes[
        normalizarPreferencia(
          valor
        )
      ] ?? "Padrão"
    )
  }


  function formatarQualidade(
    nivel
  ) {
    const traducoes = {
      excelente:
        "Excelente",

      boa:
        "Boa",

      moderada:
        "Moderada",

      baixa:
        "Baixa",

      insuficiente:
        "Insuficiente",
    }

    return (
      traducoes[nivel] ||
      nivel ||
      "-"
    )
  }


  function formatarConfianca(
    nivel
  ) {
    const traducoes = {
      alta:
        "Alta",

      media:
        "Média",

      média:
        "Média",

      baixa:
        "Baixa",
    }

    return (
      traducoes[nivel] ||
      nivel ||
      "-"
    )
  }


  function formatarResultadoRanking(
    resultadoRanking
  ) {
    const traducoes = {
      melhor_equilibrio:
        "Melhor equilíbrio",

      alternativa:
        "Alternativa",

      alternativa_mais_ampla:
        "Mais amplo",

      alternativa_mais_ajustada:
        "Mais ajustado",
    }

    return (
      traducoes[
        resultadoRanking
      ] ||
      resultadoRanking ||
      "-"
    )
  }


  function formatarCaimento(
    valor
  ) {
    const traducoes = {
      ajustado:
        "Ajustado",

      mais_ajustado_que_alvo:
        "Mais ajustado",

      equilibrado:
        "Equilibrado",

      amplo:
        "Amplo",

      mais_amplo_que_alvo:
        "Mais amplo",

      curto:
        "Curto",

      alongado:
        "Alongado",

      indisponivel:
        "Indisponível",
    }

    return (
      traducoes[valor] ||
      valor ||
      "-"
    )
  }


  function obterVariacaoPorTamanho(
    tamanho
  ) {
    return (
      variacoesProvador
        .find(
          (variacao) =>
            variacao
              ?.tamanho ===
            tamanho
        ) ??
      null
    )
  }


  /*
   * =========================================================
   * AVATAR — SELEÇÃO DE REFERÊNCIA
   * =========================================================
   */

  function selecionarReferenciaAltura(
    alturaReferencia
  ) {
    setAlturaVisualSelecionada(
      alturaReferencia
    )

    setAlturaVisualIncerta(
      false
    )

    setAvatarPreparacaoConcluida(
      false
    )
  }


  function selecionarAlturaIncerta() {
    setAlturaVisualSelecionada(
      null
    )

    setAlturaVisualIncerta(
      true
    )

    setAvatarPreparacaoConcluida(
      false
    )
  }


  function prepararReferenciaAvatar() {
    if (
      !referenciaAvatarPronta
    ) {
      return
    }

    setAvatarPreparacaoConcluida(
      true
    )
  }


  /*
   * =========================================================
   * LIMPEZA
   * =========================================================
   */

  function limparAnaliseCaptura() {
    setAnaliseCaptura(
      null
    )

    setAnalisandoCaptura(
      false
    )

    setTamanhoVisualSelecionado(
      null
    )

    setAlturaVisualSelecionada(
      null
    )

    setAlturaVisualIncerta(
      false
    )

    setAvatarPreparacaoConcluida(
      false
    )
  }


  /*
   * =========================================================
   * RECOMENDAÇÃO INICIAL
   * =========================================================
   */

  async function buscarRecomendacao() {
    if (
      !altura ||
      !peso
    ) {
      setErro(
        "Informe altura e peso para gerar a recomendação."
      )

      setResultado(
        null
      )

      setProdutoSelecionado(
        null
      )

      return
    }

    const preferenciaNormalizada =
      normalizarPreferencia(
        preferencia
      )

    const parametros =
      new URLSearchParams({
        altura_cm:
          altura,

        peso_kg:
          peso,

        preferencia_caimento:
          preferenciaNormalizada,
      })

    if (cintura) {
      parametros.append(
        "cintura_cm",
        cintura
      )
    }

    try {
      setErro("")

      setProdutoSelecionado(
        null
      )

      setProvadorIniciado(
        false
      )

      setModoExperimentacao(
        null
      )

      setFotoUsuario(
        null
      )

      if (fotoPreview) {
        URL.revokeObjectURL(
          fotoPreview
        )
      }

      setFotoPreview(
        null
      )

      setSessaoProvador(
        null
      )

      limparAnaliseCaptura()

      const resposta =
        await fetch(
          `http://127.0.0.1:8000/recomendar-produtos?${parametros.toString()}`
        )

      if (!resposta.ok) {
        throw new Error(
          "Não foi possível obter a recomendação."
        )
      }

      const dados =
        await resposta.json()

      setResultado(
        dados
      )
    } catch (erro) {
      setResultado(
        null
      )

      setProdutoSelecionado(
        null
      )

      setErro(
        erro.message ||
          "Não foi possível gerar a recomendação."
      )
    }
  }


  /*
   * =========================================================
   * PRODUTO / PROVADOR
   * =========================================================
   */

  function experimentarProduto(
    produto
  ) {
    setProdutoSelecionado(
      produto
    )

    setProvadorIniciado(
      false
    )

    setModoExperimentacao(
      null
    )

    setFotoUsuario(
      null
    )

    if (fotoPreview) {
      URL.revokeObjectURL(
        fotoPreview
      )
    }

    setFotoPreview(
      null
    )

    setSessaoProvador(
      null
    )

    limparAnaliseCaptura()

    setErro("")
  }


  function iniciarProvador() {
    setProvadorIniciado(
      true
    )

    setModoExperimentacao(
      null
    )

    setFotoUsuario(
      null
    )

    if (fotoPreview) {
      URL.revokeObjectURL(
        fotoPreview
      )
    }

    setFotoPreview(
      null
    )

    setSessaoProvador(
      null
    )

    limparAnaliseCaptura()

    setErro("")
  }


  function escolherFoto() {
    setModoExperimentacao(
      "foto"
    )

    setSessaoProvador(
      null
    )

    limparAnaliseCaptura()

    setErro("")

    inputFotoRef.current
      ?.click()
  }


  function receberFoto(
    event
  ) {
    const arquivo =
      event.target
        .files?.[0]

    if (!arquivo) {
      return
    }

    if (
      !arquivo.type
        .startsWith(
          "image/"
        )
    ) {
      setErro(
        "Selecione um arquivo de imagem válido."
      )

      event.target.value = ""

      return
    }

    if (
      arquivo.size >
      10 * 1024 * 1024
    ) {
      setErro(
        "A imagem deve ter no máximo 10 MB."
      )

      event.target.value = ""

      return
    }

    setErro("")

    setSessaoProvador(
      null
    )

    limparAnaliseCaptura()

    if (fotoPreview) {
      URL.revokeObjectURL(
        fotoPreview
      )
    }

    setFotoUsuario(
      arquivo
    )

    const preview =
      URL.createObjectURL(
        arquivo
      )

    setFotoPreview(
      preview
    )

    event.target.value = ""
  }


  function escolherAvatar() {
    setModoExperimentacao(
      "avatar"
    )

    setFotoUsuario(
      null
    )

    if (fotoPreview) {
      URL.revokeObjectURL(
        fotoPreview
      )
    }

    setFotoPreview(
      null
    )

    setSessaoProvador(
      null
    )

    limparAnaliseCaptura()

    setErro("")
  }


  /*
   * =========================================================
   * ANÁLISE AUTOMÁTICA
   * =========================================================
   */

  async function executarAnaliseAutomatica(
    sessaoId
  ) {
    if (!sessaoId) {
      return
    }

    try {
      setErro("")

      setAnalisandoCaptura(
        true
      )

      setAnaliseCaptura(
        null
      )

      setTamanhoVisualSelecionado(
        null
      )

      setAlturaVisualSelecionada(
        null
      )

      setAlturaVisualIncerta(
        false
      )

      setAvatarPreparacaoConcluida(
        false
      )

      const preferenciaNormalizada =
        normalizarPreferencia(
          preferencia
        )

      const analise =
        await analisarCapturaProvador(
          sessaoId,
          preferenciaNormalizada
        )

      setAnaliseCaptura(
        analise
      )
    } catch (erro) {
      limparAnaliseCaptura()

      setErro(
        erro.message ||
          "Não foi possível analisar a captura."
      )
    } finally {
      setAnalisandoCaptura(
        false
      )
    }
  }


  /*
   * =========================================================
   * PREPARAÇÃO DA EXPERIÊNCIA
   * =========================================================
   */

  async function prepararExperiencia() {
    if (!fotoUsuario) {
      setErro(
        "Escolha uma foto antes de preparar a experiência."
      )

      return
    }

    if (!produtoSelecionado) {
      setErro(
        "Nenhum produto foi selecionado."
      )

      return
    }

    const formData =
      new FormData()

    formData.append(
      "foto",
      fotoUsuario
    )

    formData.append(
      "produto_id",
      produtoSelecionado.id
    )

    formData.append(
      "produto_nome",
      produtoSelecionado.nome
    )

    formData.append(
      "tamanho",
      produtoSelecionado.tamanho
    )

    formData.append(
      "modo",
      "foto"
    )

    try {
      setErro("")

      setSessaoProvador(
        null
      )

      limparAnaliseCaptura()

      setEnviandoSessao(
        true
      )

      const resposta =
        await fetch(
          "http://127.0.0.1:8000/provador/preparar",
          {
            method: "POST",
            body: formData,
          }
        )

      const dados =
        await resposta.json()

      if (!resposta.ok) {
        throw new Error(
          dados.detail ||
            "Não foi possível registrar a experiência."
        )
      }

      setSessaoProvador(
        dados
      )

      await executarAnaliseAutomatica(
        dados.sessao_id
      )
    } catch (erro) {
      setErro(
        erro.message ||
          "Não foi possível preparar a experiência."
      )

      setSessaoProvador(
        null
      )

      limparAnaliseCaptura()
    } finally {
      setEnviandoSessao(
        false
      )
    }
  }


  function voltarAosProdutos() {
    setProdutoSelecionado(
      null
    )

    setProvadorIniciado(
      false
    )

    setModoExperimentacao(
      null
    )

    setFotoUsuario(
      null
    )

    if (fotoPreview) {
      URL.revokeObjectURL(
        fotoPreview
      )
    }

    setFotoPreview(
      null
    )

    setSessaoProvador(
      null
    )

    limparAnaliseCaptura()

    setErro("")
  }


  /*
   * =========================================================
   * RENDER
   * =========================================================
   */

  return (
    <main className="container">
      <h1>
        VesteIA
      </h1>

      <p>
        Descubra o tamanho ideal para você
        com uma recomendação personalizada.
      </p>


      <div className="formulario">
        <input
          type="number"
          placeholder="Altura (cm)"
          value={altura}
          onChange={
            (event) =>
              setAltura(
                event.target.value
              )
          }
        />

        <input
          type="number"
          placeholder="Peso (kg)"
          value={peso}
          onChange={
            (event) =>
              setPeso(
                event.target.value
              )
          }
        />

        <input
          type="number"
          placeholder="Cintura (cm)"
          value={cintura}
          onChange={
            (event) =>
              setCintura(
                event.target.value
              )
          }
        />

        <select
          value={preferencia}
          onChange={
            (event) =>
              setPreferencia(
                event.target.value
              )
          }
        >
          <option value="padrao">
            Caimento padrão
          </option>

          <option value="justo">
            Mais justo
          </option>

          <option value="solto">
            Mais solto
          </option>
        </select>

        <button
          type="button"
          onClick={
            buscarRecomendacao
          }
        >
          Descobrir meu tamanho
        </button>
      </div>


      {resultado && (
        <section className="resultado">
          <h2>
            Resultado
          </h2>

          <p>
            Tamanho recomendado:{" "}
            <strong>
              {
                resultado
                  .tamanho_recomendado
              }
            </strong>
          </p>

          <p>
            Confiança:{" "}
            <strong>
              {
                resultado
                  .confianca
              }
            </strong>
          </p>

          <p>
            Preferência:{" "}
            <strong>
              {formatarPreferencia(
                preferencia
              )}
            </strong>
          </p>


          {resultado
            .explicacao
            ?.motivos
            ?.map(
              (
                motivo,
                index
              ) => (
                <p
                  key={
                    index
                  }
                >
                  {motivo}
                </p>
              )
            )}


          <p>
            {
              resultado
                .mensagem
            }
          </p>


          {resultado
            .produtos
            ?.length >
            0 && (
            <div className="produtos">
              <h3>
                Produtos compatíveis
              </h3>

              {resultado
                .produtos
                .map(
                  (
                    produto
                  ) => (
                    <article
                      className="produto-card"
                      key={
                        produto.id
                      }
                    >
                      <div className="produto-imagem">
                        <img
                          src={
                            camisetaOversized
                          }
                          alt={
                            produto.nome
                          }
                        />
                      </div>

                      <h4>
                        {
                          produto.nome
                        }
                      </h4>

                      <p className="preco">
                        R${" "}
                        {Number(
                          produto.preco
                        )
                          .toFixed(
                            2
                          )
                          .replace(
                            ".",
                            ","
                          )}
                      </p>

                      <div className="produto-detalhes">
                        <span>
                          Tamanho recomendado:{" "}
                          {
                            produto
                              .tamanho
                          }
                        </span>

                        <span>
                          Cor:{" "}
                          {
                            produto
                              .cor
                          }
                        </span>

                        <span>
                          Categoria:{" "}
                          {
                            produto
                              .categoria
                          }
                        </span>

                        <span>
                          Modelagem:{" "}
                          {
                            produto
                              .modelagem
                          }
                        </span>
                      </div>


                      {produto
                        .tamanhos_disponiveis
                        ?.length >
                        0 && (
                        <div className="observacoes">
                          <span>
                            Tamanhos disponíveis:{" "}
                            {
                              produto
                                .tamanhos_disponiveis
                                .join(" • ")
                            }
                          </span>
                        </div>
                      )}


                      <button
                        type="button"
                        className="botao-experimentar"
                        onClick={
                          () =>
                            experimentarProduto(
                              produto
                            )
                        }
                      >
                        Experimentar com VesteIA
                      </button>
                    </article>
                  )
                )}
            </div>
          )}
        </section>
      )}


      {produtoSelecionado && (
        <section className="provador">

          <p className="provador-etapa">
            PROVADOR VESTEIA
          </p>

          <h2>
            Produto selecionado
          </h2>


          <div className="provador-conteudo">
            <div className="provador-imagem">
              <img
                src={
                  camisetaOversized
                }
                alt={
                  produtoSelecionado
                    .nome
                }
              />
            </div>


            <div className="provador-informacoes">
              <h3>
                {
                  produtoSelecionado
                    .nome
                }
              </h3>

              <p>
                Tamanho analisado:{" "}
                <strong>
                  {
                    produtoSelecionado
                      .tamanho
                  }
                </strong>
              </p>

              <p>
                Cor:{" "}
                <strong>
                  {
                    produtoSelecionado
                      .cor
                  }
                </strong>
              </p>

              <p>
                Modelagem:{" "}
                <strong>
                  {
                    produtoSelecionado
                      .modelagem
                  }
                </strong>
              </p>

              <p>
                Preferência:{" "}
                <strong>
                  {formatarPreferencia(
                    preferencia
                  )}
                </strong>
              </p>
            </div>
          </div>


          {!provadorIniciado && (
            <button
              type="button"
              className="botao-iniciar-provador"
              onClick={
                iniciarProvador
              }
            >
              Iniciar provador
            </button>
          )}


          {provadorIniciado &&
            !fotoUsuario &&
            modoExperimentacao !==
              "avatar" && (
              <div className="escolha-provador">
                <h3>
                  Como você deseja experimentar?
                </h3>

                <p>
                  Escolha a forma de entrada
                  para continuar no Provador
                  VesteIA.
                </p>

                <div className="opcoes-provador">
                  <button
                    type="button"
                    onClick={
                      escolherFoto
                    }
                  >
                    Usar minha foto
                  </button>

                  <button
                    type="button"
                    onClick={
                      escolherAvatar
                    }
                  >
                    Usar avatar
                  </button>
                </div>
              </div>
            )}


          <input
            ref={
              inputFotoRef
            }
            className="input-foto-oculto"
            type="file"
            accept="image/png, image/jpeg, image/webp"
            onChange={
              receberFoto
            }
          />


          {modoExperimentacao ===
            "foto" &&
            fotoPreview && (
              <div className="modo-selecionado">

                <h3>
                  Sua foto
                </h3>

                <div className="foto-preview">
                  <img
                    src={
                      fotoPreview
                    }
                    alt="Prévia do usuário"
                  />
                </div>

                {!enviandoSessao &&
                  !analisandoCaptura && (
                    <button
                      type="button"
                      className="trocar-foto"
                      onClick={
                        escolherFoto
                      }
                    >
                      Escolher outra foto
                    </button>
                  )}
              </div>
            )}


          {(enviandoSessao ||
            analisandoCaptura) && (
            <div className="modo-selecionado">

              <h3>
                ✨ VesteIA analisando sua foto
              </h3>

              <p>
                Estamos analisando sua foto,
                a peça selecionada e sua
                preferência de caimento.
              </p>

              <p>
                Isso pode levar alguns
                instantes.
              </p>
            </div>
          )}


          {contratoProvador &&
            analiseCaptura
              ?.podeContinuar && (
              <div className="modo-selecionado">

                <p className="provador-etapa">
                  VESTEIA — SEU RESULTADO
                </p>


                <h3>
                  {
                    comunicacaoProvador
                      ?.titulo ??
                    "Análise concluída"
                  }
                </h3>


                <p>
                  {
                    comunicacaoProvador
                      ?.descricao
                  }
                </p>


                {recomendacaoProvador
                  ?.disponivel && (
                  <>
                    <div className="tamanho-sugerido-card">

                      <p className="provador-etapa">
                        TAMANHO SUGERIDO
                      </p>

                      <div className="tamanho-sugerido-bolha">
                        {
                          recomendacaoProvador
                            .tamanho
                        }
                      </div>

                      <h3>
                        Melhor ajuste para
                        sua preferência
                      </h3>


                      <p>
                        Preferência de caimento:{" "}
                        <strong>
                          {formatarPreferencia(
                            recomendacaoProvador
                              .preferencia_caimento
                          )}
                        </strong>
                      </p>


                      <p>
                        Compatibilidade com sua preferência:{" "}
                        <strong>
                          {Math.round(
                            (
                              recomendacaoProvador
                                .pontuacao ||
                              0
                            ) *
                              100
                          )}
                          %
                        </strong>
                      </p>


                      <p>
                        <small>
                          Sugestão experimental VesteIA
                        </small>
                      </p>


                      {recomendacaoProvador
                        ?.tamanho_alternativo && (
                        <p>
                          Alternativa relevante:{" "}
                          <strong>
                            {
                              recomendacaoProvador
                                .tamanho_alternativo
                            }
                          </strong>
                        </p>
                      )}


                      <div className="produto-detalhes">

                        <span>
                          Você selecionou:{" "}
                          <strong>
                            {
                              produtoSelecionado
                                ?.tamanho
                            }
                          </strong>
                        </span>

                        <span>
                          Sugestão VesteIA:{" "}
                          <strong>
                            {
                              recomendacaoProvador
                                .tamanho
                            }
                          </strong>
                        </span>

                        {recomendacaoProvador
                          ?.alternativa_forte && (
                          <span>
                            <strong>
                              Alternativa forte:
                            </strong>{" "}
                            {
                              recomendacaoProvador
                                .tamanho_alternativo
                            }
                          </span>
                        )}

                      </div>

                    </div>


                    {tamanhosProvador
                      .length >
                      0 && (
                      <div className="ranking-tamanhos">

                        <h3>
                          Compare os tamanhos
                        </h3>

                        <p>
                          Clique em P, M, G ou GG
                          para comparar cada opção.
                          A recomendação principal
                          continua destacada.
                        </p>


                        {tamanhosProvador
                          .map(
                            (
                              item
                            ) => {
                              const variacao =
                                obterVariacaoPorTamanho(
                                  item.tamanho
                                )

                              const estaSelecionado =
                                item.tamanho ===
                                tamanhoAtivo

                              return (
                                <button
                                  type="button"
                                  className={
                                    [
                                      "ranking-item",
                                      item.posicao ===
                                      1
                                        ? "ranking-item-melhor"
                                        : "",
                                      estaSelecionado
                                        ? "ranking-item-selecionado"
                                        : "",
                                    ]
                                      .filter(Boolean)
                                      .join(" ")
                                  }
                                  key={
                                    item
                                      .produto_id
                                  }
                                  onClick={
                                    () =>
                                      setTamanhoVisualSelecionado(
                                        item.tamanho
                                      )
                                  }
                                >

                                  <span>
                                    <strong>
                                      {
                                        item
                                          .posicao
                                      }
                                      º
                                    </strong>
                                  </span>

                                  <span>
                                    <strong>
                                      {
                                        item
                                          .tamanho
                                      }
                                    </strong>
                                  </span>

                                  <span>
                                    <strong>
                                      {Math.round(
                                        (
                                          item
                                            .pontuacao ||
                                          0
                                        ) *
                                          100
                                      )}
                                      /100
                                    </strong>
                                  </span>

                                  <span>
                                    {formatarResultadoRanking(
                                      item
                                        .resultado
                                    )}

                                    {item
                                      .tamanho ===
                                      tamanhoRecomendado && (
                                      <small>
                                        Recomendado pelo VesteIA
                                      </small>
                                    )}

                                    {estaSelecionado &&
                                      item
                                        .tamanho !==
                                        tamanhoRecomendado && (
                                        <small>
                                          Visualizando agora
                                        </small>
                                      )}
                                  </span>

                                  {variacao && (
                                    <span>
                                      {variacao
                                        .largura_cm}
                                      {" × "}
                                      {variacao
                                        .comprimento_cm}
                                      {" cm"}
                                    </span>
                                  )}

                                  {item.posicao ===
                                    1 && (
                                    <span>
                                      ⭐
                                    </span>
                                  )}

                                </button>
                              )
                            }
                          )}

                      </div>
                    )}


                    {rankingAtivo &&
                      variacaoAtiva && (
                      <div className="tamanho-comparacao-card">

                        <p className="provador-etapa">
                          TAMANHO EM VISUALIZAÇÃO
                        </p>

                        <div className="tamanho-comparacao-topo">

                          <div className="tamanho-comparacao-bolha">
                            {
                              tamanhoAtivo
                            }
                          </div>

                          <div className="tamanho-comparacao-resumo">

                            <h3>
                              {tamanhoAtivo ===
                              tamanhoRecomendado
                                ? "Recomendação principal"
                                : "Comparando outra opção"}
                            </h3>

                            <p>
                              Compatibilidade com sua preferência:{" "}
                              <strong>
                                {Math.round(
                                  (
                                    rankingAtivo
                                      ?.pontuacao ||
                                    0
                                  ) *
                                    100
                                )}
                                %
                              </strong>
                            </p>

                            <p>
                              {formatarResultadoRanking(
                                rankingAtivo
                                  ?.resultado
                              )}
                            </p>

                          </div>

                        </div>


                        <div className="produto-detalhes">

                          <span>
                            <strong>
                              Largura da peça:
                            </strong>{" "}
                            {
                              variacaoAtiva
                                .largura_cm
                            }{" "}
                            cm
                          </span>

                          <span>
                            <strong>
                              Comprimento da peça:
                            </strong>{" "}
                            {
                              variacaoAtiva
                                .comprimento_cm
                            }{" "}
                            cm
                          </span>

                          <span>
                            <strong>
                              Caimento na largura:
                            </strong>{" "}
                            {formatarCaimento(
                              rankingAtivo
                                ?.caimento_largura
                            )}
                          </span>

                          <span>
                            <strong>
                              Caimento no comprimento:
                            </strong>{" "}
                            {formatarCaimento(
                              rankingAtivo
                                ?.caimento_comprimento
                            )}
                          </span>

                        </div>


                        {tamanhoAtivo ===
                          tamanhoRecomendado ? (
                          <p className="tamanho-comparacao-status">
                            ⭐ Este é o tamanho
                            recomendado pelo VesteIA
                            para sua preferência atual.
                          </p>
                        ) : (
                          <>
                            <p className="tamanho-comparacao-status">
                              Você está apenas
                              comparando o tamanho{" "}
                              <strong>
                                {tamanhoAtivo}
                              </strong>
                              . A recomendação principal
                              continua sendo{" "}
                              <strong>
                                {tamanhoRecomendado}
                              </strong>
                              .
                            </p>

                            <button
                              type="button"
                              className="botao-iniciar-provador"
                              onClick={
                                () =>
                                  setTamanhoVisualSelecionado(
                                    tamanhoRecomendado
                                  )
                              }
                            >
                              Voltar para o recomendado
                            </button>
                          </>
                        )}

                      </div>
                    )}


                    {tamanhosProvador
                      ?.length >
                      0 && (
                      <div className="produto-detalhes">

                        <span>
                          <strong>
                            Caimento recomendado na largura:
                          </strong>{" "}
                          {formatarCaimento(
                            tamanhosProvador[0]
                              ?.caimento_largura
                          )}
                        </span>

                        <span>
                          <strong>
                            Caimento recomendado no comprimento:
                          </strong>{" "}
                          {formatarCaimento(
                            tamanhosProvador[0]
                              ?.caimento_comprimento
                          )}
                        </span>

                        {obterVariacaoPorTamanho(
                          recomendacaoProvador
                            ?.tamanho
                        ) && (
                          <>
                            <span>
                              <strong>
                                Largura recomendada:
                              </strong>{" "}
                              {
                                obterVariacaoPorTamanho(
                                  recomendacaoProvador
                                    ?.tamanho
                                )
                                  ?.largura_cm
                              }{" "}
                              cm
                            </span>

                            <span>
                              <strong>
                                Comprimento recomendado:
                              </strong>{" "}
                              {
                                obterVariacaoPorTamanho(
                                  recomendacaoProvador
                                    ?.tamanho
                                )
                                  ?.comprimento_cm
                              }{" "}
                              cm
                            </span>
                          </>
                        )}

                      </div>
                    )}

                  </>
                )}


                {caimentoProvador
                  ?.destaques
                  ?.length >
                  0 && (
                  <div className="observacoes">

                    {caimentoProvador
                      .destaques
                      .map(
                        (
                          destaque,
                          index
                        ) => (
                          <span
                            key={
                              index
                            }
                          >
                            ✓{" "}
                            {
                              destaque
                            }
                          </span>
                        )
                      )}

                  </div>
                )}


                <div className="produto-detalhes">

                  <span>
                    <strong>
                      Peça:
                    </strong>{" "}
                    {
                      produtoProvador
                        ?.nome ??
                      produtoSelecionado
                        ?.nome
                    }
                  </span>

                  <span>
                    <strong>
                      Sugestão:
                    </strong>{" "}
                    {
                      recomendacaoProvador
                        ?.tamanho ??
                      "-"
                    }
                  </span>

                  <span>
                    <strong>
                      Qualidade da foto:
                    </strong>{" "}
                    {formatarQualidade(
                      analiseProvador
                        ?.qualidade_foto
                    )}
                  </span>

                  <span>
                    <strong>
                      Confiança visual:
                    </strong>{" "}
                    {formatarConfianca(
                      analiseProvador
                        ?.confianca_visual
                    )}
                  </span>

                  <span>
                    <strong>
                      Confiança do ranking:
                    </strong>{" "}
                    {formatarConfianca(
                      recomendacaoProvador
                        ?.confianca
                        ?.nivel
                    )}
                  </span>

                </div>


                {referenciaCorporal
                  ?.disponivel && (
                  <div className="produto-detalhes">

                    <span>
                      <strong>
                        Referência corporal:
                      </strong>{" "}
                      disponível
                    </span>

                    <span>
                      <strong>
                        Origem:
                      </strong>{" "}
                      {
                        referenciaCorporal
                          .origem_corporal ===
                        "foto"
                          ? "Foto"
                          : referenciaCorporal
                              .origem_corporal
                      }
                    </span>

                    <span>
                      <strong>
                        Confiança métrica:
                      </strong>{" "}
                      {formatarConfianca(
                        referenciaCorporal
                          .confianca_metrica
                      )}
                    </span>

                  </div>
                )}


                {avatarProvador
                  ?.preparavel &&
                  selecaoVisualAltura
                    ?.suportada_no_contrato &&
                  candidatosAltura
                    .length >
                    0 && (
                    <section className="avatar-preparacao">

                      <p className="provador-etapa">
                        PREPARAR REFERÊNCIA DO AVATAR
                      </p>

                      <h3>
                        Qual referência visual
                        mais se aproxima de você?
                      </h3>

                      <p className="avatar-preparacao-intro">
                        Escolha uma das referências
                        abaixo. Elas ajudam a preparar
                        a futura representação visual
                        do VesteIA.
                      </p>


                      <div className="avatar-referencia-resumo">

                        <span>
                          <strong>
                            Origem corporal:
                          </strong>{" "}
                          {
                            referenciaCorporal
                              ?.origem_corporal ===
                            "foto"
                              ? "Foto"
                              : referenciaCorporal
                                  ?.origem_corporal ||
                                "-"
                          }
                        </span>

                        <span>
                          <strong>
                            Confiança:
                          </strong>{" "}
                          {formatarConfianca(
                            referenciaCorporal
                              ?.confianca_metrica
                          )}
                        </span>

                        <span>
                          <strong>
                            Tamanho em visualização:
                          </strong>{" "}
                          {
                            tamanhoAtivo ||
                            tamanhoRecomendado ||
                            "-"
                          }
                        </span>

                      </div>


                      <div className="avatar-alturas-grid">

                        {candidatosAltura
                          .map(
                            (
                              candidato
                            ) => {
                              const selecionado =
                                alturaVisualSelecionada ===
                                candidato
                                  .altura_referencia_cm

                              return (
                                <button
                                  type="button"
                                  key={
                                    candidato.id
                                  }
                                  className={
                                    [
                                      "avatar-altura-card",
                                      candidato
                                        .referencia_central
                                        ? "avatar-altura-central"
                                        : "",
                                      selecionado
                                        ? "avatar-altura-selecionada"
                                        : "",
                                    ]
                                      .filter(Boolean)
                                      .join(" ")
                                  }
                                  onClick={
                                    () =>
                                      selecionarReferenciaAltura(
                                        candidato
                                          .altura_referencia_cm
                                      )
                                  }
                                >

                                  <span className="avatar-altura-numero">
                                    {
                                      candidato
                                        .altura_referencia_cm
                                    }
                                  </span>

                                  <span className="avatar-altura-unidade">
                                    cm
                                  </span>

                                  {candidato
                                    .referencia_central && (
                                    <small>
                                      Referência central
                                    </small>
                                  )}

                                  {selecionado && (
                                    <strong>
                                      ✓ Selecionado
                                    </strong>
                                  )}

                                </button>
                              )
                            }
                          )}

                      </div>


                      <button
                        type="button"
                        className={
                          alturaVisualIncerta
                            ? "avatar-incerteza avatar-incerteza-selecionada"
                            : "avatar-incerteza"
                        }
                        onClick={
                          selecionarAlturaIncerta
                        }
                      >
                        <strong>
                          Não tenho certeza
                        </strong>

                        <span>
                          Continuar sem escolher
                          uma única referência.
                        </span>
                      </button>


                      <div className="avatar-selecao-status">

                        {!referenciaAvatarPronta && (
                          <p>
                            Selecione uma referência
                            ou escolha “Não tenho certeza”.
                          </p>
                        )}


                        {alturaVisualSelecionada && (
                          <p>
                            Referência selecionada:{" "}
                            <strong>
                              {
                                alturaVisualSelecionada
                              }{" "}
                              cm
                            </strong>
                          </p>
                        )}


                        {alturaVisualIncerta && (
                          <p>
                            <strong>
                              Referência aberta.
                            </strong>{" "}
                            O VesteIA manterá a incerteza
                            em vez de assumir uma altura
                            específica.
                          </p>
                        )}

                      </div>


                      <div className="avatar-aviso">
                        <strong>
                          Importante:
                        </strong>{" "}
                        essas opções são referências
                        para personalização visual.
                        Elas não representam uma
                        medição anatômica exata da
                        sua altura.
                      </div>


                      <button
                        type="button"
                        className="botao-preparar-avatar"
                        disabled={
                          !referenciaAvatarPronta
                        }
                        onClick={
                          prepararReferenciaAvatar
                        }
                      >
                        Preparar referência do Avatar
                      </button>


                      {avatarPreparacaoConcluida && (
                        <div className="avatar-pronto">

                          <strong>
                            ✓ Referência visual preparada
                          </strong>

                          <p>
                            {alturaVisualSelecionada
                              ? `O Avatar poderá utilizar ${alturaVisualSelecionada} cm como referência visual selecionada pelo usuário.`
                              : "O Avatar foi preparado mantendo a incerteza de altura informada pelo usuário."}
                          </p>

                          <p>
                            Tamanho atualmente em
                            visualização:{" "}
                            <strong>
                              {
                                tamanhoAtivo
                              }
                            </strong>
                          </p>

                          <small>
                            A geração do Avatar ainda
                            não acontece nesta Sprint.
                          </small>

                        </div>
                      )}

                    </section>
                  )}


                <p>
                  ✨ Análise personalizada
                  pelo VesteIA.
                </p>


                {comunicacaoProvador
                  ?.transparencia && (
                  <p>
                    {
                      comunicacaoProvador
                        .transparencia
                    }
                  </p>
                )}

              </div>
            )}


          {!contratoProvador &&
            analiseCaptura &&
            analiseCaptura
              .novaFotoNecessaria && (
              <div className="modo-selecionado">

                <p className="provador-etapa">
                  VESTEIA — NOVA FOTO
                </p>

                <h3>
                  {
                    analiseCaptura
                      .titulo ??
                    "Precisamos de outra foto"
                  }
                </h3>

                <p>
                  {
                    analiseCaptura
                      .mensagem
                  }
                </p>


                {analiseCaptura
                  ?.orientacoes
                  ?.length >
                  0 && (
                  <div className="observacoes">

                    {analiseCaptura
                      .orientacoes
                      .map(
                        (
                          orientacao,
                          index
                        ) => (
                          <span
                            key={
                              index
                            }
                          >
                            {
                              orientacao
                            }
                          </span>
                        )
                      )}

                  </div>
                )}


                <button
                  type="button"
                  className="botao-iniciar-provador"
                  onClick={
                    escolherFoto
                  }
                >
                  Escolher outra foto
                </button>

              </div>
            )}


          {modoExperimentacao ===
            "avatar" && (
              <div className="modo-selecionado">

                <h3>
                  Avatar selecionado
                </h3>

                <p>
                  A estrutura do VesteIA
                  está sendo preparada para
                  a futura experiência visual
                  com Avatar.
                </p>

                <p>
                  Nesta versão, a geração
                  visual do Avatar ainda
                  não está ativa.
                </p>

              </div>
            )}


          <button
            type="button"
            className="fechar-provador"
            onClick={
              voltarAosProdutos
            }
          >
            Voltar aos produtos
          </button>

        </section>
      )}


      {erro && (
        <p className="erro">
          {erro}
        </p>
      )}
    </main>
  )
}


export default App
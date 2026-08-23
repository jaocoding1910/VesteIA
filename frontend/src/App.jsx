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
    compatibilidadeProduto,
    setCompatibilidadeProduto,
  ] = useState(null)

  const [
    resultadoDimensional,
    setResultadoDimensional,
  ] = useState(null)

  const [
    recomendacaoTamanho,
    setRecomendacaoTamanho,
  ] = useState(null)

  const [
    decisaoProvador,
    setDecisaoProvador,
  ] = useState(null)

  const [
    erro,
    setErro,
  ] = useState("")

  const inputFotoRef =
    useRef(null)


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


  function limparAnaliseCaptura() {
    setAnaliseCaptura(
      null
    )

    setAnalisandoCaptura(
      false
    )

    setCompatibilidadeProduto(
      null
    )

    setResultadoDimensional(
      null
    )

    setRecomendacaoTamanho(
      null
    )

    setDecisaoProvador(
      null
    )
  }


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

      setCompatibilidadeProduto(
        null
      )

      setResultadoDimensional(
        null
      )

      setRecomendacaoTamanho(
        null
      )

      setDecisaoProvador(
        null
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

      const respostaCompleta =
        analise
          ?.respostaCompleta

      setCompatibilidadeProduto(
        respostaCompleta
          ?.compatibilidade_corpo_produto ??
          null
      )

      setResultadoDimensional(
        respostaCompleta
          ?.resultado_dimensional ??
          null
      )

      setRecomendacaoTamanho(
        respostaCompleta
          ?.recomendacao_tamanho_provador ??
          null
      )

      setDecisaoProvador(
        respostaCompleta
          ?.decisao_provador ??
          null
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

      equilibrado:
        "Equilibrado",

      amplo:
        "Amplo",

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


                      {produto
                        .observacoes
                        ?.length >
                        0 && (
                        <div className="observacoes">
                          {produto
                            .observacoes
                            .map(
                              (
                                observacao,
                                index
                              ) => (
                                <span
                                  key={
                                    index
                                  }
                                >
                                  {
                                    observacao
                                  }
                                </span>
                              )
                            )}
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


          {decisaoProvador &&
            decisaoProvador.status ===
              "analise_consolidada" && (
              <div className="modo-selecionado">

                <p className="provador-etapa">
                  VESTEIA — SEU RESULTADO
                </p>

                <h3>
                  {
                    decisaoProvador
                      .titulo
                  }
                </h3>

                <p>
                  {
                    decisaoProvador
                      .descricao
                  }
                </p>


                {recomendacaoTamanho
                  ?.disponivel && (
                  <>

                    <div className="tamanho-sugerido-card">

                      <p className="provador-etapa">
                        TAMANHO SUGERIDO
                      </p>

                      <div className="tamanho-sugerido-bolha">
                        {
                          recomendacaoTamanho
                            .tamanho_sugerido
                        }
                      </div>

                      <h3>
                        Melhor equilíbrio
                        para seu perfil
                      </h3>

                      <p>
                        Preferência:{" "}
                        <strong>
                          {formatarPreferencia(
                            recomendacaoTamanho
                              .preferencia_caimento
                          )}
                        </strong>
                      </p>

                      <p>
                        Pontuação de ajuste experimental:{" "}
                        <strong>
                          {Math.round(
                            (
                              recomendacaoTamanho
                                .pontuacao_melhor_tamanho ||
                              0
                            ) *
                              100
                          )}
                          /100
                        </strong>
                      </p>


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
                              recomendacaoTamanho
                                .tamanho_sugerido
                            }
                          </strong>
                        </span>

                      </div>

                    </div>


                    {recomendacaoTamanho
                      ?.ranking
                      ?.length >
                      0 && (
                      <div className="ranking-tamanhos">

                        <h3>
                          Comparação entre tamanhos
                        </h3>

                        <p>
                          Veja como cada tamanho
                          se posiciona para o seu perfil.
                        </p>


                        {recomendacaoTamanho
                          .ranking
                          .map(
                            (
                              item
                            ) => (
                              <div
                                className={
                                  item.posicao ===
                                  1
                                    ? "ranking-item ranking-item-melhor"
                                    : "ranking-item"
                                }
                                key={
                                  item
                                    .produto_id
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
                                    produtoSelecionado
                                      ?.tamanho && (
                                    <small>
                                      Seu tamanho selecionado
                                    </small>
                                  )}
                                </span>

                                {item.posicao ===
                                  1 && (
                                  <span>
                                    ⭐
                                  </span>
                                )}

                              </div>
                            )
                          )}

                      </div>
                    )}


                    {recomendacaoTamanho
                      ?.ranking?.[0] && (
                      <div className="produto-detalhes">

                        <span>
                          <strong>
                            Largura sugerida:
                          </strong>{" "}
                          {
                            recomendacaoTamanho
                              .ranking[0]
                              .largura_peca_cm
                          }{" "}
                          cm
                        </span>

                        <span>
                          <strong>
                            Comprimento sugerido:
                          </strong>{" "}
                          {
                            recomendacaoTamanho
                              .ranking[0]
                              .comprimento_peca_cm
                          }{" "}
                          cm
                        </span>

                        <span>
                          <strong>
                            Caimento na largura:
                          </strong>{" "}
                          {formatarCaimento(
                            recomendacaoTamanho
                              .ranking[0]
                              .caimento_largura
                          )}
                        </span>

                        <span>
                          <strong>
                            Caimento no comprimento:
                          </strong>{" "}
                          {formatarCaimento(
                            recomendacaoTamanho
                              .ranking[0]
                              .caimento_comprimento
                          )}
                        </span>

                      </div>
                    )}

                  </>
                )}


                {decisaoProvador
                  .destaques
                  ?.length >
                  0 && (
                  <div className="observacoes">

                    {decisaoProvador
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
                      produtoSelecionado
                        ?.nome
                    }
                  </span>

                  <span>
                    <strong>
                      Tamanho analisado:
                    </strong>{" "}
                    {
                      produtoSelecionado
                        ?.tamanho
                    }
                  </span>

                  <span>
                    <strong>
                      Qualidade da foto:
                    </strong>{" "}
                    {formatarQualidade(
                      decisaoProvador
                        .qualidade_foto
                    )}
                  </span>

                  <span>
                    <strong>
                      Confiança visual:
                    </strong>{" "}
                    {
                      decisaoProvador
                        .confianca_visual ||
                      "-"
                    }
                  </span>

                </div>


                <p>
                  ✨ Análise personalizada
                  pelo VesteIA.
                </p>


                {recomendacaoTamanho
                  ?.mensagem && (
                  <p>
                    {
                      recomendacaoTamanho
                        .mensagem
                    }
                  </p>
                )}


                {recomendacaoTamanho
                  ?.mensagem_transparencia && (
                  <p>
                    {
                      recomendacaoTamanho
                        .mensagem_transparencia
                    }
                  </p>
                )}

              </div>
            )}


          {decisaoProvador &&
            decisaoProvador.status ===
              "analise_visual_disponivel" && (
              <div className="modo-selecionado">

                <p className="provador-etapa">
                  VESTEIA — SEU RESULTADO
                </p>

                <h3>
                  {
                    decisaoProvador
                      .titulo
                  }
                </h3>

                <p>
                  {
                    decisaoProvador
                      .descricao
                  }
                </p>

                <p>
                  ✨ O VesteIA conseguiu
                  realizar uma análise
                  visual da peça.
                </p>

              </div>
            )}


          {decisaoProvador &&
            decisaoProvador.status ===
              "analise_parcial" && (
              <div className="modo-selecionado">

                <p className="provador-etapa">
                  VESTEIA — ANÁLISE PARCIAL
                </p>

                <h3>
                  {
                    decisaoProvador
                      .titulo
                  }
                </h3>

                <p>
                  {
                    decisaoProvador
                      .descricao
                  }
                </p>

              </div>
            )}


          {decisaoProvador &&
            decisaoProvador.status ===
              "nova_foto_necessaria" && (
              <div className="modo-selecionado">

                <p className="provador-etapa">
                  VESTEIA — NOVA FOTO
                </p>

                <h3>
                  {
                    decisaoProvador
                      .titulo
                  }
                </h3>

                <p>
                  {
                    decisaoProvador
                      .descricao
                  }
                </p>


                {decisaoProvador
                  .destaques
                  ?.length >
                  0 && (
                  <div className="observacoes">

                    {decisaoProvador
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
                            {
                              destaque
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


          {!decisaoProvador &&
            analiseCaptura &&
            analiseCaptura
              .novaFotoNecessaria && (
              <div className="modo-selecionado">

                <h3>
                  Precisamos de outra foto
                </h3>

                <p>
                  {
                    analiseCaptura
                      .mensagem
                  }
                </p>

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
                  Na próxima etapa,
                  você poderá utilizar
                  uma representação virtual
                  para experimentar esta peça.
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
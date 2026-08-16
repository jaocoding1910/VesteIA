import camisetaOversized from "./assets/produtos/camiseta-oversized.jpeg"
import { useEffect, useRef, useState } from "react"
import "./App.css"

function App() {
  const [altura, setAltura] = useState("")
  const [peso, setPeso] = useState("")
  const [cintura, setCintura] = useState("")
  const [preferencia, setPreferencia] = useState("")

  const [resultado, setResultado] = useState(null)
  const [produtoSelecionado, setProdutoSelecionado] = useState(null)

  const [provadorIniciado, setProvadorIniciado] = useState(false)
  const [modoExperimentacao, setModoExperimentacao] = useState(null)

  const [fotoUsuario, setFotoUsuario] = useState(null)
  const [fotoPreview, setFotoPreview] = useState(null)

  // Guarda a sessão devolvida pelo FastAPI após o registro no PostgreSQL.
  const [sessaoProvador, setSessaoProvador] = useState(null)

  const [enviandoSessao, setEnviandoSessao] = useState(false)

  const [erro, setErro] = useState("")

  const inputFotoRef = useRef(null)

  // Libera da memória a URL temporária da foto.
  useEffect(() => {
    return () => {
      if (fotoPreview) {
        URL.revokeObjectURL(fotoPreview)
      }
    }
  }, [fotoPreview])

  // Formata a data retornada pelo PostgreSQL para leitura no frontend.
  function formatarData(data) {
    if (!data) {
      return "-"
    }

    return new Date(data).toLocaleString("pt-BR")
  }

  // Busca recomendação de tamanho e produtos no backend.
  async function buscarRecomendacao() {
    if (!altura || !peso) {
      setErro("Informe altura e peso para gerar a recomendação.")
      setResultado(null)
      setProdutoSelecionado(null)
      return
    }

    const parametros = new URLSearchParams({
      altura_cm: altura,
      peso_kg: peso,
    })

    if (cintura) {
      parametros.append("cintura_cm", cintura)
    }

    if (preferencia) {
      parametros.append(
        "preferencia_caimento",
        preferencia
      )
    }

    try {
      setErro("")
      setProdutoSelecionado(null)
      setProvadorIniciado(false)
      setModoExperimentacao(null)
      setFotoUsuario(null)
      setFotoPreview(null)
      setSessaoProvador(null)

      const resposta = await fetch(
        `http://127.0.0.1:8000/recomendar-produtos?${parametros}`
      )

      if (!resposta.ok) {
        throw new Error(
          "Não foi possível obter a recomendação."
        )
      }

      const dados = await resposta.json()

      setResultado(dados)
    } catch (erro) {
      setResultado(null)
      setProdutoSelecionado(null)
      setErro(erro.message)
    }
  }

  // Envia o produto escolhido para o Provador VesteIA.
  function experimentarProduto(produto) {
    setProdutoSelecionado(produto)

    setProvadorIniciado(false)
    setModoExperimentacao(null)

    setFotoUsuario(null)
    setFotoPreview(null)

    setSessaoProvador(null)
  }

  // Inicia o fluxo do provador.
  function iniciarProvador() {
    setProvadorIniciado(true)

    setModoExperimentacao(null)

    setFotoUsuario(null)
    setFotoPreview(null)

    setSessaoProvador(null)
  }

  // Abre o seletor de arquivos do sistema.
  function escolherFoto() {
    setModoExperimentacao("foto")
    setSessaoProvador(null)

    inputFotoRef.current?.click()
  }

  // Recebe e valida a foto escolhida.
  function receberFoto(event) {
    const arquivo = event.target.files?.[0]

    if (!arquivo) {
      return
    }

    if (!arquivo.type.startsWith("image/")) {
      setErro(
        "Selecione um arquivo de imagem válido."
      )

      event.target.value = ""
      return
    }

    if (arquivo.size > 10 * 1024 * 1024) {
      setErro(
        "A imagem deve ter no máximo 10 MB."
      )

      event.target.value = ""
      return
    }

    setErro("")
    setFotoUsuario(arquivo)
    setSessaoProvador(null)

    const preview = URL.createObjectURL(arquivo)

    setFotoPreview(preview)

    // Permite selecionar novamente o mesmo arquivo.
    event.target.value = ""
  }

  // Seleciona a alternativa de avatar.
  function escolherAvatar() {
    setModoExperimentacao("avatar")

    setFotoUsuario(null)
    setFotoPreview(null)

    setSessaoProvador(null)
  }

  // Envia os dados da experiência para o FastAPI.
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

    const formData = new FormData()

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
      setSessaoProvador(null)
      setEnviandoSessao(true)

      const resposta = await fetch(
        "http://127.0.0.1:8000/provador/preparar",
        {
          method: "POST",
          body: formData,
        }
      )

      const dados = await resposta.json()

      if (!resposta.ok) {
        throw new Error(
          dados.detail ||
            "Não foi possível registrar a experiência."
        )
      }

      setSessaoProvador(dados)
    } catch (erro) {
      setErro(erro.message)
      setSessaoProvador(null)
    } finally {
      setEnviandoSessao(false)
    }
  }

  // Fecha o provador e retorna aos produtos.
  function voltarAosProdutos() {
    setProdutoSelecionado(null)

    setProvadorIniciado(false)
    setModoExperimentacao(null)

    setFotoUsuario(null)
    setFotoPreview(null)

    setSessaoProvador(null)
  }

  return (
    <main className="container">
      <h1>VesteIA</h1>

      <p>
        Descubra o tamanho ideal para você com uma recomendação
        personalizada.
      </p>

      <div className="formulario">
        <input
          type="number"
          placeholder="Altura (cm)"
          value={altura}
          onChange={(event) =>
            setAltura(event.target.value)
          }
        />

        <input
          type="number"
          placeholder="Peso (kg)"
          value={peso}
          onChange={(event) =>
            setPeso(event.target.value)
          }
        />

        <input
          type="number"
          placeholder="Cintura (cm)"
          value={cintura}
          onChange={(event) =>
            setCintura(event.target.value)
          }
        />

        <select
          value={preferencia}
          onChange={(event) =>
            setPreferencia(event.target.value)
          }
        >
          <option value="">
            Caimento padrão
          </option>

          <option value="justo">
            Justo
          </option>

          <option value="solto">
            Solto
          </option>
        </select>

        <button
          type="button"
          onClick={buscarRecomendacao}
        >
          Descobrir meu tamanho
        </button>
      </div>

      {resultado && (
        <section className="resultado">
          <h2>Resultado</h2>

          <p>
            Tamanho recomendado:{" "}
            <strong>
              {resultado.tamanho_recomendado}
            </strong>
          </p>

          <p>
            Confiança:{" "}
            <strong>
              {resultado.confianca}
            </strong>
          </p>

          {resultado.explicacao?.motivos?.map(
            (motivo, index) => (
              <p key={index}>
                {motivo}
              </p>
            )
          )}

          <p>
            {resultado.mensagem}
          </p>

          {resultado.produtos?.length > 0 && (
            <div className="produtos">
              <h3>Produtos compatíveis</h3>

              {resultado.produtos.map(
                (produto) => (
                  <article
                    className="produto-card"
                    key={produto.id}
                  >
                    <div className="produto-imagem">
                      <img
                        src={camisetaOversized}
                        alt={produto.nome}
                      />
                    </div>

                    <h4>
                      {produto.nome}
                    </h4>

                    <p className="preco">
                      R${" "}
                      {Number(produto.preco)
                        .toFixed(2)
                        .replace(".", ",")}
                    </p>

                    <div className="produto-detalhes">
                      <span>
                        Tamanho: {produto.tamanho}
                      </span>

                      <span>
                        Cor: {produto.cor}
                      </span>

                      <span>
                        Categoria: {produto.categoria}
                      </span>

                      <span>
                        Modelagem: {produto.modelagem}
                      </span>
                    </div>

                    {produto.observacoes?.length > 0 && (
                      <div className="observacoes">
                        {produto.observacoes.map(
                          (observacao, index) => (
                            <span key={index}>
                              {observacao}
                            </span>
                          )
                        )}
                      </div>
                    )}

                    <button
                      type="button"
                      className="botao-experimentar"
                      onClick={() =>
                        experimentarProduto(produto)
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
                src={camisetaOversized}
                alt={produtoSelecionado.nome}
              />
            </div>

            <div className="provador-informacoes">
              <h3>
                {produtoSelecionado.nome}
              </h3>

              <p>
                Tamanho recomendado:{" "}
                <strong>
                  {produtoSelecionado.tamanho}
                </strong>
              </p>

              <p>
                Cor:{" "}
                <strong>
                  {produtoSelecionado.cor}
                </strong>
              </p>

              <p>
                Modelagem:{" "}
                <strong>
                  {produtoSelecionado.modelagem}
                </strong>
              </p>
            </div>
          </div>

          {!provadorIniciado && (
            <button
              type="button"
              className="botao-iniciar-provador"
              onClick={iniciarProvador}
            >
              Iniciar provador
            </button>
          )}

          {provadorIniciado && (
            <div className="escolha-provador">
              <h3>
                Como você deseja experimentar?
              </h3>

              <p>
                Escolha a forma de entrada para continuar
                no Provador VesteIA.
              </p>

              <div className="opcoes-provador">
                <button
                  type="button"
                  onClick={escolherFoto}
                >
                  Usar minha foto
                </button>

                <button
                  type="button"
                  onClick={escolherAvatar}
                >
                  Usar avatar
                </button>
              </div>

              <input
                ref={inputFotoRef}
                className="input-foto-oculto"
                type="file"
                accept="image/png, image/jpeg, image/webp"
                onChange={receberFoto}
              />
            </div>
          )}

          {modoExperimentacao === "foto" &&
            fotoPreview && (
              <div className="modo-selecionado">
                <h3>
                  Foto selecionada
                </h3>

                <div className="foto-preview">
                  <img
                    src={fotoPreview}
                    alt="Prévia do usuário"
                  />
                </div>

                <p className="nome-arquivo">
                  {fotoUsuario?.name}
                </p>

                <p>
                  Foto carregada localmente e pronta
                  para entrar no fluxo de experimentação.
                </p>

                <button
                  type="button"
                  className="trocar-foto"
                  onClick={escolherFoto}
                >
                  Escolher outra foto
                </button>

                {!sessaoProvador && (
                  <button
                    type="button"
                    className="botao-iniciar-provador"
                    onClick={prepararExperiencia}
                    disabled={enviandoSessao}
                  >
                    {enviandoSessao
                      ? "Registrando experiência..."
                      : "✨ Preparar experiência VesteIA"}
                  </button>
                )}
              </div>
            )}

          {sessaoProvador && (
            <div className="modo-selecionado">
              <h3>
                ✅ Experiência registrada
              </h3>

              <p>
                <strong>
                  Sessão VesteIA:
                </strong>{" "}
                #{sessaoProvador.sessao_id}
              </p>

              <p>
                <strong>
                  Status da requisição:
                </strong>{" "}
                {sessaoProvador.status}
              </p>

              <p>
                <strong>
                  Status do processamento:
                </strong>{" "}
                {sessaoProvador.status_processamento}
              </p>

              <p>
                <strong>
                  Pronto para processar:
                </strong>{" "}
                {sessaoProvador.pronto_para_processar
                  ? "Sim"
                  : "Não"}
              </p>

              <p>
                <strong>
                  Produto:
                </strong>{" "}
                {sessaoProvador.produto.nome}
              </p>

              <p>
                <strong>
                  Tamanho:
                </strong>{" "}
                {sessaoProvador.produto.tamanho}
              </p>

              <p>
                <strong>
                  Modo:
                </strong>{" "}
                {sessaoProvador.modo}
              </p>

              <p>
                <strong>
                  Arquivo:
                </strong>{" "}
                {sessaoProvador.arquivo.nome}
              </p>

              <p>
                <strong>
                  Formato:
                </strong>{" "}
                {sessaoProvador.arquivo.tipo}
              </p>

              <p>
                <strong>
                  Tamanho do arquivo:
                </strong>{" "}
                {sessaoProvador.arquivo.tamanho_bytes} bytes
              </p>

              <p>
                <strong>
                  Registrada em:
                </strong>{" "}
                {formatarData(
                  sessaoProvador.criado_em
                )}
              </p>

              <p>
                {sessaoProvador.mensagem}
              </p>
            </div>
          )}

          {modoExperimentacao === "avatar" && (
            <div className="modo-selecionado">
              <h3>
                Avatar selecionado
              </h3>

              <p>
                Na próxima etapa, o usuário poderá
                utilizar uma representação virtual para
                experimentar esta peça.
              </p>
            </div>
          )}

          <button
            type="button"
            className="fechar-provador"
            onClick={voltarAosProdutos}
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
import { useState } from "react"
import "./App.css"

function App() {
  const [altura, setAltura] = useState("")
  const [peso, setPeso] = useState("")
  const [cintura, setCintura] = useState("")
  const [preferencia, setPreferencia] = useState("")
  const [resultado, setResultado] = useState(null)
  const [erro, setErro] = useState("")

  // Envia os dados preenchidos para o backend do VesteIA.
  async function buscarRecomendacao() {
    if (!altura || !peso) {
      setErro("Informe altura e peso para gerar a recomendação.")
      setResultado(null)
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
      parametros.append("preferencia_caimento", preferencia)
    }

    try {
      setErro("")

      const resposta = await fetch(
        `http://127.0.0.1:8000/recomendar-produtos?${parametros}`
      )

      if (!resposta.ok) {
        throw new Error("Não foi possível obter a recomendação.")
      }

      const dados = await resposta.json()

      setResultado(dados)
    } catch (erro) {
      setResultado(null)
      setErro(erro.message)
    }
  }

  return (
    <main className="container">
      <h1>VesteIA</h1>

      <p>
        Descubra o tamanho ideal para você com uma recomendação personalizada.
      </p>

      <div className="formulario">
        <input
          type="number"
          placeholder="Altura (cm)"
          value={altura}
          onChange={(e) => setAltura(e.target.value)}
        />

        <input
          type="number"
          placeholder="Peso (kg)"
          value={peso}
          onChange={(e) => setPeso(e.target.value)}
        />

        <input
          type="number"
          placeholder="Cintura (cm)"
          value={cintura}
          onChange={(e) => setCintura(e.target.value)}
        />

        <select
          value={preferencia}
          onChange={(e) => setPreferencia(e.target.value)}
        >
          <option value="">Caimento padrão</option>
          <option value="justo">Justo</option>
          <option value="solto">Solto</option>
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
            <strong>{resultado.tamanho_recomendado}</strong>
          </p>

          <p>
            Confiança: <strong>{resultado.confianca}</strong>
          </p>

          {resultado.explicacao?.motivos?.map((motivo, index) => (
            <p key={index}>{motivo}</p>
          ))}

          <p>{resultado.mensagem}</p>

          {/* Exibe os produtos compatíveis encontrados pelo backend. */}
          {resultado.produtos?.length > 0 && (
            <div className="produtos">
              <h3>Produtos compatíveis</h3>

              {resultado.produtos.map((produto) => (
                <article
                  className="produto-card"
                  key={produto.id}
                >
                  <h4>{produto.nome}</h4>

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
                </article>
              ))}
            </div>
          )}
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
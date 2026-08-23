const API_BASE_URL = "http://127.0.0.1:8000"


export async function executarProvador(sessaoId) {
  if (!sessaoId) {
    throw new Error("sessaoId é obrigatório.")
  }

  const resposta = await fetch(
    `${API_BASE_URL}/provador/sessoes/${sessaoId}/executar`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
    }
  )

  let dados = null

  try {
    dados = await resposta.json()
  } catch {
    dados = null
  }

  if (!resposta.ok) {
    throw new Error(
      dados?.detail ||
        `Erro ao executar o Provador VesteIA. HTTP ${resposta.status}`
    )
  }

  return dados
}


export async function analisarCapturaProvador(sessaoId) {
  const dados = await executarProvador(sessaoId)

  const resumoProvador = dados?.resumo_provador

  if (!resumoProvador) {
    throw new Error(
      "O backend não retornou o resumo do provador."
    )
  }

  return {
    sessaoId: dados?.sessao_id ?? sessaoId,

    estado:
      resumoProvador?.estado ?? "erro_avaliacao",

    podeContinuar:
      resumoProvador?.pode_continuar ?? false,

    novaFotoNecessaria:
      resumoProvador?.nova_foto_necessaria ?? true,

    titulo:
      resumoProvador?.titulo ??
      "Não foi possível avaliar a captura",

    mensagem:
      resumoProvador?.mensagem ?? null,

    orientacoes:
      resumoProvador?.orientacoes ?? [],

    qualidade:
      resumoProvador?.qualidade ?? {
        nivel: null,
        pontuacao: null,
      },

    pipeline:
      dados?.pipeline ?? null,

    resultadoCaptura:
      dados?.resultado_captura ?? null,

    controleFluxo:
      dados?.controle_fluxo_provador ?? null,

    respostaCompleta: dados,
  }
}
const API_BASE_URL = "http://127.0.0.1:8000"


async function tratarResposta(resposta) {
  let dados = null

  try {
    dados = await resposta.json()
  } catch {
    dados = null
  }

  if (!resposta.ok) {
    throw new Error(
      dados?.detail ||
        `Erro na comunicação com o VesteIA. HTTP ${resposta.status}`
    )
  }

  return dados
}


export async function normalizarImagemSessao(sessaoId) {
  if (!sessaoId) {
    throw new Error("sessaoId é obrigatório.")
  }

  const resposta = await fetch(
    `${API_BASE_URL}/provador/sessoes/${sessaoId}/normalizar-imagem`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
    }
  )

  return tratarResposta(resposta)
}


export async function detectarPessoaSessao(sessaoId) {
  if (!sessaoId) {
    throw new Error("sessaoId é obrigatório.")
  }

  const resposta = await fetch(
    `${API_BASE_URL}/provador/sessoes/${sessaoId}/detectar-pessoa`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    }
  )

  return tratarResposta(resposta)
}


export async function obterResumoProvador(sessaoId) {
  const dados = await detectarPessoaSessao(sessaoId)

  const resumo =
    dados?.deteccao_humana?.resumo_provador

  if (!resumo) {
    throw new Error(
      "O backend não retornou resumo_provador."
    )
  }

  return resumo
}


export async function analisarCapturaProvador(sessaoId) {
  if (!sessaoId) {
    throw new Error("sessaoId é obrigatório.")
  }

  // =====================================================
  // ETAPA 1 — NORMALIZAÇÃO
  // =====================================================

  const normalizacao =
    await normalizarImagemSessao(sessaoId)

  // =====================================================
  // ETAPA 2 — DETECÇÃO E PIPELINE VISUAL
  // =====================================================

  const dados =
    await detectarPessoaSessao(sessaoId)

  const deteccaoHumana =
    dados?.deteccao_humana

  if (!deteccaoHumana) {
    throw new Error(
      "Resposta do pipeline visual indisponível."
    )
  }

  const resultadoCaptura =
    deteccaoHumana?.resultado_captura

  const resumoProvador =
    deteccaoHumana?.resumo_provador

  const controleFluxo =
    deteccaoHumana?.controle_fluxo_provador

  if (!resumoProvador) {
    throw new Error(
      "Resumo do provador não encontrado."
    )
  }

  return {
    sessaoId:
      dados?.sessao_id ?? sessaoId,

    produto:
      dados?.produto ?? null,

    pessoaDetectada:
      deteccaoHumana?.pessoa_detectada ?? false,

    normalizacao,

    resultadoCaptura:
      resultadoCaptura ?? null,

    resumoProvador,

    controleFluxo:
      controleFluxo ?? null,

    podeContinuar:
      resumoProvador?.pode_continuar ?? false,

    novaFotoNecessaria:
      resumoProvador?.nova_foto_necessaria ?? true,

    estado:
      resumoProvador?.estado ?? "erro_avaliacao",

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

    respostaCompleta:
      dados,
  }
}
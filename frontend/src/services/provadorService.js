const API_BASE_URL =
  "http://127.0.0.1:8000"


function normalizarPreferenciaCaimento(
  preferenciaCaimento
) {
  if (!preferenciaCaimento) {
    return "padrao"
  }

  const preferencia =
    String(
      preferenciaCaimento
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
    mapa[preferencia] ??
    "padrao"
  )
}


export async function executarProvador(
  sessaoId,
  preferenciaCaimento = "padrao"
) {
  if (!sessaoId) {
    throw new Error(
      "sessaoId é obrigatório."
    )
  }

  const preferenciaNormalizada =
    normalizarPreferenciaCaimento(
      preferenciaCaimento
    )

  const parametros =
    new URLSearchParams({
      preferencia_caimento:
        preferenciaNormalizada,
    })

  const resposta =
    await fetch(
      `${API_BASE_URL}/provador/sessoes/${sessaoId}/executar?${parametros.toString()}`,
      {
        method: "POST",

        headers: {
          Accept:
            "application/json",
        },
      }
    )

  let dados = null

  try {
    dados =
      await resposta.json()
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


export async function analisarCapturaProvador(
  sessaoId,
  preferenciaCaimento = "padrao"
) {
  const preferenciaNormalizada =
    normalizarPreferenciaCaimento(
      preferenciaCaimento
    )

  const dados =
    await executarProvador(
      sessaoId,
      preferenciaNormalizada
    )

  const resumoProvador =
    dados?.resumo_provador

  if (!resumoProvador) {
    throw new Error(
      "O backend não retornou o resumo do provador."
    )
  }

  return {
    sessaoId:
      dados?.sessao_id ??
      sessaoId,

    estado:
      resumoProvador?.estado ??
      "erro_avaliacao",

    podeContinuar:
      resumoProvador
        ?.pode_continuar ??
      false,

    novaFotoNecessaria:
      resumoProvador
        ?.nova_foto_necessaria ??
      true,

    titulo:
      resumoProvador?.titulo ??
      "Não foi possível avaliar a captura",

    mensagem:
      resumoProvador?.mensagem ??
      null,

    orientacoes:
      resumoProvador
        ?.orientacoes ??
      [],

    qualidade:
      resumoProvador?.qualidade ??
      {
        nivel: null,
        pontuacao: null,
      },

    preferenciaCaimento:
      dados
        ?.preferencia_caimento ??
      preferenciaNormalizada,

    pipeline:
      dados?.pipeline ??
      null,

    resultadoCaptura:
      dados
        ?.resultado_captura ??
      null,

    controleFluxo:
      dados
        ?.controle_fluxo_provador ??
      null,

    compatibilidadeProduto:
      dados
        ?.compatibilidade_corpo_produto ??
      null,

    compatibilidadeDimensional:
      dados
        ?.compatibilidade_dimensional ??
      null,

    resultadoDimensional:
      dados
        ?.resultado_dimensional ??
      null,

    recomendacaoTamanho:
      dados
        ?.recomendacao_tamanho_provador ??
      null,

    decisaoProvador:
      dados
        ?.decisao_provador ??
      null,

    variacoesProduto:
      dados
        ?.variacoes_produto ??
      [],

    respostaCompleta:
      dados,
  }
}
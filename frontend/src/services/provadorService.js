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


async function extrairRespostaJson(
  resposta
) {
  try {
    return await resposta.json()
  } catch {
    return null
  }
}


function gerarErroHttp(
  dados,
  resposta,
  mensagemPadrao
) {
  return new Error(
    dados?.detail ||
      `${mensagemPadrao} HTTP ${resposta.status}`
  )
}


// ==========================================================
// EXECUTAR MOTOR COMPLETO
// ==========================================================

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

  const dados =
    await extrairRespostaJson(
      resposta
    )

  if (!resposta.ok) {
    throw gerarErroHttp(
      dados,
      resposta,
      "Erro ao executar o Provador VesteIA."
    )
  }

  return dados
}


// ==========================================================
// OBTER RESULTADO ENXUTO
// ==========================================================

export async function obterResultadoProvador(
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
      `${API_BASE_URL}/provador/sessoes/${sessaoId}/resultado?${parametros.toString()}`,
      {
        method: "POST",

        headers: {
          Accept:
            "application/json",
        },
      }
    )

  const dados =
    await extrairRespostaJson(
      resposta
    )

  if (!resposta.ok) {
    throw gerarErroHttp(
      dados,
      resposta,
      "Erro ao obter o resultado do Provador VesteIA."
    )
  }

  const contratoProvador =
    dados?.contrato_provador

  if (!contratoProvador) {
    throw new Error(
      "O backend não retornou o contrato Provador V1."
    )
  }

  return {
    sessaoId:
      dados?.sessao_id ??
      sessaoId,

    preferenciaCaimento:
      dados
        ?.preferencia_caimento ??
      preferenciaNormalizada,

    versaoContrato:
      dados
        ?.versao_contrato ??
      contratoProvador
        ?.versao_contrato ??
      null,

    status:
      dados?.status ??
      contratoProvador?.status ??
      null,

    podeContinuar:
      dados
        ?.pode_continuar ??
      contratoProvador
        ?.pode_continuar ??
      false,

    contratoProvador,

    produto:
      contratoProvador
        ?.produto ??
      null,

    analise:
      contratoProvador
        ?.analise ??
      null,

    recomendacao:
      contratoProvador
        ?.recomendacao ??
      null,

    caimento:
      contratoProvador
        ?.caimento ??
      null,

    tamanhos:
      contratoProvador
        ?.tamanhos ??
      [],

    variacoes:
      contratoProvador
        ?.variacoes ??
      [],

    referenciaCorporal:
      contratoProvador
        ?.referencia_corporal ??
      null,

    avatar:
      contratoProvador
        ?.avatar ??
      null,

    comunicacao:
      contratoProvador
        ?.comunicacao ??
      null,

    mensagem:
      dados?.mensagem ??
      null,

    respostaCompleta:
      dados,
  }
}


// ==========================================================
// FLUXO PRINCIPAL DO FRONTEND
// ==========================================================

export async function analisarCapturaProvador(
  sessaoId,
  preferenciaCaimento = "padrao"
) {
  const preferenciaNormalizada =
    normalizarPreferenciaCaimento(
      preferenciaCaimento
    )

  /*
   * 1. Executa o motor completo.
   *
   * O retorno técnico permanece disponível
   * somente dentro deste service para
   * validação do fluxo da captura.
   */
  const dadosExecucao =
    await executarProvador(
      sessaoId,
      preferenciaNormalizada
    )

  const resumoProvador =
    dadosExecucao
      ?.resumo_provador

  if (!resumoProvador) {
    throw new Error(
      "O backend não retornou o resumo do provador."
    )
  }

  /*
   * Se a captura não puder continuar,
   * não há necessidade de buscar o
   * contrato final de produto.
   */
  if (
    !resumoProvador
      ?.pode_continuar
  ) {
    return {
      sessaoId:
        dadosExecucao
          ?.sessao_id ??
        sessaoId,

      estado:
        resumoProvador
          ?.estado ??
        "erro_avaliacao",

      podeContinuar: false,

      novaFotoNecessaria:
        resumoProvador
          ?.nova_foto_necessaria ??
        true,

      titulo:
        resumoProvador
          ?.titulo ??
        "Não foi possível avaliar a captura",

      mensagem:
        resumoProvador
          ?.mensagem ??
        null,

      orientacoes:
        resumoProvador
          ?.orientacoes ??
        [],

      qualidade:
        resumoProvador
          ?.qualidade ??
        {
          nivel: null,
          pontuacao: null,
        },

      preferenciaCaimento:
        dadosExecucao
          ?.preferencia_caimento ??
        preferenciaNormalizada,

      contratoProvador: null,

      produto: null,
      analise: null,
      recomendacao: null,
      caimento: null,
      tamanhos: [],
      variacoes: [],
      referenciaCorporal: null,
      avatar: null,
      comunicacao: null,

      respostaTecnica:
        dadosExecucao,
    }
  }

  /*
   * 2. Com a captura aprovada,
   * busca o contrato enxuto destinado
   * ao produto/frontend.
   */
  const resultado =
    await obterResultadoProvador(
      sessaoId,
      preferenciaNormalizada
    )

  return {
    sessaoId:
      resultado
        ?.sessaoId ??
      sessaoId,

    estado:
      resumoProvador
        ?.estado ??
      "avancar",

    podeContinuar:
      resultado
        ?.podeContinuar ??
      true,

    novaFotoNecessaria:
      resumoProvador
        ?.nova_foto_necessaria ??
      false,

    titulo:
      resultado
        ?.comunicacao
        ?.titulo ??
      resumoProvador
        ?.titulo ??
      "Análise concluída",

    mensagem:
      resultado
        ?.comunicacao
        ?.descricao ??
      resumoProvador
        ?.mensagem ??
      null,

    orientacoes:
      resumoProvador
        ?.orientacoes ??
      [],

    qualidade:
      resumoProvador
        ?.qualidade ??
      {
        nivel: null,
        pontuacao: null,
      },

    preferenciaCaimento:
      resultado
        ?.preferenciaCaimento ??
      preferenciaNormalizada,

    versaoContrato:
      resultado
        ?.versaoContrato ??
      null,

    statusContrato:
      resultado
        ?.status ??
      null,

    contratoProvador:
      resultado
        ?.contratoProvador ??
      null,

    produto:
      resultado
        ?.produto ??
      null,

    analise:
      resultado
        ?.analise ??
      null,

    recomendacao:
      resultado
        ?.recomendacao ??
      null,

    caimento:
      resultado
        ?.caimento ??
      null,

    tamanhos:
      resultado
        ?.tamanhos ??
      [],

    variacoes:
      resultado
        ?.variacoes ??
      [],

    referenciaCorporal:
      resultado
        ?.referenciaCorporal ??
      null,

    avatar:
      resultado
        ?.avatar ??
      null,

    comunicacao:
      resultado
        ?.comunicacao ??
      null,

    /*
     * Mantemos temporariamente o retorno
     * técnico para diagnóstico durante
     * a Sprint 50.
     *
     * O App.jsx não deverá depender dele.
     */
    respostaTecnica:
      dadosExecucao,

    respostaCompleta:
      resultado
        ?.respostaCompleta ??
      null,
  }
}
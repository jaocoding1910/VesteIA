import {captureHeaders} from "./mvpApi"
import { API_BASE_URL } from "./apiConfig"


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


/*
 * Transforma erros do FastAPI em texto legível.
 *
 * Isso também evita aparecer:
 *
 * [object Object]
 *
 * na interface.
 */
function extrairMensagemErro(
  dados,
  mensagemPadrao,
  status
) {
  const detail =
    dados?.detail

  if (
    typeof detail === "string" &&
    detail.trim()
  ) {
    return detail
  }

  if (
    Array.isArray(detail) &&
    detail.length > 0
  ) {
    return detail
      .map((erro) => {
        const campo =
          Array.isArray(
            erro?.loc
          )
            ? erro.loc
                .filter(
                  (item) =>
                    item !== "body"
                )
                .join(".")
            : ""

        const mensagem =
          erro?.msg ??
          "Dados inválidos"

        return campo
          ? `${campo}: ${mensagem}`
          : mensagem
      })
      .join(" | ")
  }

  return (
    `${mensagemPadrao} HTTP ${status}`
  )
}


function gerarErroHttp(
  dados,
  resposta,
  mensagemPadrao
) {
  return new Error(
    extrairMensagemErro(
      dados,
      mensagemPadrao,
      resposta.status
    )
  )
}


// ==========================================================
// VESTIBILIDADE DINÂMICA DO AVATAR — SPRINT 53
// ==========================================================

export async function calcularVestibilidadeAvatar(
  perfilAvatar,
  produto,
  tamanhoSelecionado = ""
) {
  if (!perfilAvatar) {
    throw new Error(
      "perfilAvatar é obrigatório para calcular a vestibilidade."
    )
  }

  if (!produto) {
    throw new Error(
      "produto é obrigatório para calcular a vestibilidade."
    )
  }


  /*
   * O backend espera produto_id
   * diretamente no body.
   *
   * Aceitamos alguns formatos diferentes
   * vindos do frontend para não deixar
   * a integração frágil.
   */
  const produtoId =
    Number(
      produto.id ??
      produto.produto_id ??
      produto.produtoId
    )


  if (
    !Number.isFinite(
      produtoId
    ) ||
    produtoId <= 0
  ) {
    throw new Error(
      "O produto selecionado não possui um produto_id válido."
    )
  }


  const tamanhoFinal =
    String(
      tamanhoSelecionado ||
      produto.tamanho ||
      produto.tamanho_selecionado ||
      "M"
    ).trim()


  /*
   * IMPORTANTE:
   *
   * Contrato atual esperado por:
   *
   * POST /avatar/vestibilidade
   *
   * produto_id fica NA RAIZ.
   *
   * Não enviamos:
   *
   * produto: {
   *   id: ...
   * }
   *
   * porque isso provocava HTTP 422.
   */
  const payload = {
    genero:
      perfilAvatar.genero ??
      "masculino",

    altura_aproximada_cm:
      Number(
        perfilAvatar
          .altura_aproximada_cm ??
        perfilAvatar.altura ??
        175
      ),

    peso_aproximado_kg:
      Number(
        perfilAvatar
          .peso_aproximado_kg ??
        perfilAvatar.peso ??
        75
      ),

    porte_corporal:
      perfilAvatar
        .porte_corporal ??
      perfilAvatar.porte ??
      "medio",

    proporcao_tronco:
      perfilAvatar
        .proporcao_tronco ??
      perfilAvatar.tronco ??
      "media",

    proporcao_pernas:
      perfilAvatar
        .proporcao_pernas ??
      perfilAvatar.pernas ??
      "media",

    produto_id:
      produtoId,

    tamanho_selecionado:
      tamanhoFinal,
  }


  const resposta =
    await fetch(
      `${API_BASE_URL}/avatar/vestibilidade`,
      {
        method: "POST",

        headers: {
          Accept:
            "application/json",

          "Content-Type":
            "application/json",
        },

        body:
          JSON.stringify(
            payload
          ),
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
      "Erro ao calcular a vestibilidade dinâmica do avatar."
    )
  }


  return {
    disponivel:
      dados?.disponivel ??
      false,

    status:
      dados?.status ??
      null,

    classificacao:
      dados
        ?.vestibilidade_visual
        ?.classificacao ??
      null,

    fatorHorizontal:
      dados
        ?.vestibilidade_visual
        ?.fator_horizontal_relativo ??
      1,

    fatorVertical:
      dados
        ?.vestibilidade_visual
        ?.fator_vertical_relativo ??
      1,

    multiplicadorHorizontal:
      dados
        ?.integracao_caimento_visual
        ?.multiplicador_horizontal_avatar ??
      1,

    multiplicadorVertical:
      dados
        ?.integracao_caimento_visual
        ?.multiplicador_vertical_avatar ??
      1,

    prontoParaIntegracao:
      dados
        ?.integracao_caimento_visual
        ?.pronto_para_integracao ??
      false,

    perfilAvatar:
      dados
        ?.perfil_avatar ??
      null,

    produto:
      dados
        ?.produto ??
      null,

    vestibilidadeVisual:
      dados
        ?.vestibilidade_visual ??
      null,

    integracaoCaimentoVisual:
      dados
        ?.integracao_caimento_visual ??
      null,

    respostaCompleta:
      dados,
  }
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
          ...captureHeaders(sessaoId),
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
          ...captureHeaders(sessaoId),
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
      contratoProvador
        ?.status ??
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

      podeContinuar:
        false,

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

      contratoProvador:
        null,

      produto:
        null,

      analise:
        null,

      recomendacao:
        null,

      caimento:
        null,

      tamanhos:
        [],

      variacoes:
        [],

      referenciaCorporal:
        null,

      avatar:
        null,

      comunicacao:
        null,

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
     * técnico para diagnóstico.
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
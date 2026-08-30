def _obter_dict(
    valor,
):
    """
    Retorna o valor apenas quando
    ele for um dicionário válido.
    """

    if isinstance(
        valor,
        dict,
    ):
        return valor

    return {}


def _booleano(
    valor,
):
    """
    Normaliza valores booleanos.
    """

    return bool(
        valor
    )


def gerar_integracao_final_provador_v1(
    renderer_avatar_2d: dict,
    representacao_roupa: dict,
    vestimenta_avatar_2d: dict,
    simulacao_caimento_visual: dict,
):
    """
    Consolida as camadas visuais finais
    do Provador VesteIA.

    ETAPA 11 DA SPRINT 50.

    Esta função recebe estruturas que
    já foram processadas anteriormente:

    - Renderer do Avatar 2D;
    - Representação da Roupa;
    - Vestimenta do Avatar;
    - Simulação Visual de Caimento.

    Seu objetivo é gerar um contrato
    visual consolidado e simples para
    consumo pelo frontend.

    IMPORTANTE:

    Esta função NÃO:
    - detecta pessoa;
    - calcula landmarks;
    - calcula centímetros corporais;
    - estima altura física;
    - estima peso;
    - estima circunferências;
    - recomenda tamanho;
    - recalcula caimento;
    - simula física de tecido;
    - altera anatomia;
    - altera Sprint 48;
    - altera Sprint 49.

    Ela apenas integra resultados
    já produzidos pelo pipeline.
    """

    # ======================================================
    # NORMALIZAÇÃO DAS ENTRADAS
    # ======================================================

    renderer_avatar_2d = (
        _obter_dict(
            renderer_avatar_2d
        )
    )

    representacao_roupa = (
        _obter_dict(
            representacao_roupa
        )
    )

    vestimenta_avatar_2d = (
        _obter_dict(
            vestimenta_avatar_2d
        )
    )

    simulacao_caimento_visual = (
        _obter_dict(
            simulacao_caimento_visual
        )
    )

    # ======================================================
    # ESTADO DAS CAMADAS
    # ======================================================

    renderer_pronto = (
        _booleano(
            renderer_avatar_2d.get(
                "pronto",
                False,
            )
        )
    )

    roupa_pronta = (
        _booleano(
            representacao_roupa.get(
                "pronta_para_vestir_avatar",
                False,
            )
        )
    )

    roupa_vestida = (
        _booleano(
            vestimenta_avatar_2d.get(
                "vestida_no_avatar",
                False,
            )
        )
    )

    caimento_simulado = (
        _booleano(
            simulacao_caimento_visual.get(
                "caimento_simulado",
                False,
            )
        )
    )

    pronta_renderizacao_final = (
        _booleano(
            simulacao_caimento_visual.get(
                "pronta_para_renderizacao_final",
                False,
            )
        )
    )

    # ======================================================
    # PRODUTO
    # ======================================================

    produto = (
        simulacao_caimento_visual.get(
            "produto"
        )
        or vestimenta_avatar_2d.get(
            "produto"
        )
        or representacao_roupa.get(
            "produto"
        )
        or {}
    )

    # ======================================================
    # AVATAR
    # ======================================================

    avatar_pontos = (
        renderer_avatar_2d.get(
            "pontos"
        )
        or {}
    )

    avatar_segmentos = (
        renderer_avatar_2d.get(
            "segmentos"
        )
        or []
    )

    avatar_formas = (
        renderer_avatar_2d.get(
            "formas"
        )
        or {}
    )

    canvas = (
        renderer_avatar_2d.get(
            "canvas_normalizado"
        )
        or {}
    )

    centros_estruturais = (
        renderer_avatar_2d.get(
            "centros_estruturais"
        )
        or {}
    )

    # ======================================================
    # ROUPA
    #
    # Para o frontend, damos prioridade
    # à geometria pós-caimento.
    #
    # Caso ela não esteja disponível,
    # usamos a roupa apenas posicionada.
    # ======================================================

    pontos_caimento = (
        simulacao_caimento_visual.get(
            "pontos_caimento"
        )
        or {}
    )

    pontos_vestimenta = (
        vestimenta_avatar_2d.get(
            "pontos_roupa_no_avatar"
        )
        or {}
    )

    if pontos_caimento:
        pontos_roupa_final = (
            pontos_caimento
        )

        origem_geometria_roupa = (
            "simulacao_caimento_visual_v1"
        )

    else:
        pontos_roupa_final = (
            pontos_vestimenta
        )

        origem_geometria_roupa = (
            "vestimenta_avatar_2d_v1"
        )

    regioes_caimento = (
        simulacao_caimento_visual.get(
            "regioes"
        )
        or {}
    )

    regioes_vestimenta = (
        vestimenta_avatar_2d.get(
            "regioes"
        )
        or {}
    )

    regioes_roupa_final = (
        regioes_caimento
        if regioes_caimento
        else regioes_vestimenta
    )

    # ======================================================
    # INTERPRETAÇÃO VISUAL
    # ======================================================

    interpretacao_caimento = (
        simulacao_caimento_visual.get(
            "interpretacao"
        )
        or {}
    )

    parametros_visuais = (
        simulacao_caimento_visual.get(
            "parametros_visuais"
        )
        or {}
    )

    preferencia_caimento = (
        simulacao_caimento_visual.get(
            "preferencia_caimento"
        )
    )

    modelagem = (
        simulacao_caimento_visual.get(
            "modelagem"
        )
        or produto.get(
            "modelagem"
        )
    )

    # ======================================================
    # QUALIDADE DAS CAMADAS
    # ======================================================

    qualidade_renderer = (
        renderer_avatar_2d.get(
            "qualidade"
        )
        or {}
    )

    qualidade_vestimenta = (
        vestimenta_avatar_2d.get(
            "qualidade"
        )
        or {}
    )

    qualidade_caimento = (
        simulacao_caimento_visual.get(
            "qualidade"
        )
        or {}
    )

    # ======================================================
    # VALIDAÇÃO GLOBAL
    # ======================================================

    etapas_visuais = {
        "renderer_avatar_2d": (
            renderer_pronto
        ),

        "representacao_roupa": (
            roupa_pronta
        ),

        "vestimenta_avatar_2d": (
            roupa_vestida
        ),

        "simulacao_caimento_visual": (
            caimento_simulado
        ),
    }

    quantidade_etapas = len(
        etapas_visuais
    )

    etapas_concluidas = sum(
        etapas_visuais.values()
    )

    percentual_integracao = (
        etapas_concluidas
        / quantidade_etapas
        if quantidade_etapas
        else 0
    )

    integracao_completa = (
        renderer_pronto
        and roupa_pronta
        and roupa_vestida
        and caimento_simulado
        and pronta_renderizacao_final
    )

    if integracao_completa:
        status = (
            "provador_visual_integrado"
        )

    elif etapas_concluidas > 0:
        status = (
            "provador_visual_parcial"
        )

    else:
        status = (
            "provador_visual_indisponivel"
        )

    # ======================================================
    # PRÓXIMA CAMADA
    #
    # "pronto_para_frontend" significa:
    # existem dados estruturados para que
    # o frontend desenhe o resultado.
    #
    # NÃO significa que uma imagem PNG,
    # foto realista ou render físico
    # tenha sido gerado no backend.
    # ======================================================

    pronto_para_frontend = (
        integracao_completa
        and bool(
            avatar_pontos
        )
        and bool(
            pontos_roupa_final
        )
    )

    # ======================================================
    # SAÍDA FINAL
    # ======================================================

    return {
        "versao": (
            "integracao_final_provador_v1"
        ),

        "status": (
            status
        ),

        "disponivel": (
            etapas_concluidas > 0
        ),

        "pipeline_visual": {
            "renderer_avatar_2d": (
                renderer_pronto
            ),

            "representacao_roupa": (
                roupa_pronta
            ),

            "vestimenta_avatar_2d": (
                roupa_vestida
            ),

            "simulacao_caimento_visual": (
                caimento_simulado
            ),

            "etapas_concluidas": (
                etapas_concluidas
            ),

            "total_etapas": (
                quantidade_etapas
            ),

            "percentual_integracao": (
                round(
                    percentual_integracao,
                    4,
                )
            ),

            "completo": (
                integracao_completa
            ),
        },

        "produto": (
            produto
        ),

        "preferencia_caimento": (
            preferencia_caimento
        ),

        "modelagem": (
            modelagem
        ),

        "visualizacao": {
            "canvas": (
                canvas
            ),

            "avatar": {
                "origem": (
                    "renderer_avatar_2d_v1"
                ),

                "pontos": (
                    avatar_pontos
                ),

                "segmentos": (
                    avatar_segmentos
                ),

                "formas": (
                    avatar_formas
                ),

                "centros_estruturais": (
                    centros_estruturais
                ),
            },

            "roupa": {
                "origem": (
                    origem_geometria_roupa
                ),

                "pontos": (
                    pontos_roupa_final
                ),

                "regioes": (
                    regioes_roupa_final
                ),

                "vestida_no_avatar": (
                    roupa_vestida
                ),

                "caimento_visual_aplicado": (
                    caimento_simulado
                ),
            },
        },

        "caimento": {
            "simulado": (
                caimento_simulado
            ),

            "tipo": (
                "tendencia_visual"
            ),

            "preferencia": (
                preferencia_caimento
            ),

            "modelagem": (
                modelagem
            ),

            "interpretacao": (
                interpretacao_caimento
            ),

            "parametros_visuais": (
                parametros_visuais
            ),

            "simulacao_fisica": False,
        },

        "qualidade": {
            "renderer": (
                qualidade_renderer
            ),

            "vestimenta": (
                qualidade_vestimenta
            ),

            "caimento": (
                qualidade_caimento
            ),
        },

        "frontend": {
            "pronto_para_consumo": (
                pronto_para_frontend
            ),

            "avatar_desenhavel": (
                renderer_pronto
            ),

            "roupa_desenhavel": (
                roupa_vestida
            ),

            "caimento_visual_disponivel": (
                caimento_simulado
            ),

            "imagem_backend_gerada": False,

            "tipo_renderizacao_prevista": (
                "frontend_2d"
            ),
        },

        "restricoes": {
            "usa_centimetros_corpo": False,

            "estima_altura_fisica": False,

            "estima_peso": False,

            "estima_circunferencias": False,

            "compara_cm_roupa_corpo": False,

            "recomenda_tamanho": False,

            "simula_fisica_tecido": False,

            "representa_ajuste_fisico_exato": False,

            "gera_foto_realista_backend": False,
        },

        "integracao_completa": (
            integracao_completa
        ),

        "pronto_para_frontend": (
            pronto_para_frontend
        ),

        "imagem_final_gerada": False,

        "experimental": True,

        "mensagem": (
            "Integração Final do Provador V1 concluída. "
            "Avatar, roupa posicionada e tendência visual "
            "de caimento foram consolidados em uma estrutura "
            "única pronta para consumo pelo frontend 2D."
            if integracao_completa
            else
            "A Integração Final do Provador V1 foi gerada "
            "parcialmente porque uma ou mais camadas visuais "
            "anteriores ainda não estão disponíveis."
        ),
    }
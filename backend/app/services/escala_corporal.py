def calcular_escala_corporal(
    altura_usuario_cm,
    altura_corpo_relativa,
):
    """
    Calcula uma escala visual aproximada entre
    coordenadas normalizadas e centímetros.

    IMPORTANTE:
    A referência corporal obtida atualmente pelo
    VesteIA representa a extensão visual observável
    do corpo na imagem e não necessariamente a
    altura anatômica completa.

    Portanto, esta escala deve ser considerada
    provisória e não uma medição física exata.
    """

    if altura_usuario_cm is None:
        return {
            "status": "altura_usuario_indisponivel",
            "escala_cm_por_unidade": None,
            "conversao_disponivel": False,
        }

    if altura_usuario_cm <= 0:
        return {
            "status": "altura_usuario_invalida",
            "escala_cm_por_unidade": None,
            "conversao_disponivel": False,
        }

    if altura_corpo_relativa is None:
        return {
            "status": (
                "altura_corporal_relativa_indisponivel"
            ),
            "escala_cm_por_unidade": None,
            "conversao_disponivel": False,
        }

    if altura_corpo_relativa <= 0:
        return {
            "status": (
                "altura_corporal_relativa_invalida"
            ),
            "escala_cm_por_unidade": None,
            "conversao_disponivel": False,
        }

    escala = (
        altura_usuario_cm
        / altura_corpo_relativa
    )

    return {
        "status": "escala_visual_calculada",

        "altura_usuario_cm": round(
            altura_usuario_cm,
            2,
        ),

        "altura_corpo_relativa": round(
            altura_corpo_relativa,
            4,
        ),

        "escala_cm_por_unidade": round(
            escala,
            4,
        ),

        "conversao_disponivel": True,

        "tipo_escala": (
            "estimativa_visual_provisoria"
        ),

        "precisao_metrica": (
            "nao_calibrada_anatomicamente"
        ),

        "mensagem": (
            "Escala visual aproximada calculada. "
            "Os valores em centímetros ainda "
            "não representam medidas anatômicas "
            "de precisão."
        ),
    }


def converter_medida_relativa_para_cm(
    medida_relativa,
    escala_cm_por_unidade,
):
    """
    Converte uma distância relativa para uma
    estimativa visual em centímetros.

    A função somente realiza a transformação
    matemática. A confiabilidade da medida depende
    da qualidade da calibração utilizada.
    """

    if medida_relativa is None:
        return None

    if escala_cm_por_unidade is None:
        return None

    if medida_relativa < 0:
        return None

    if escala_cm_por_unidade <= 0:
        return None

    medida_cm = (
        medida_relativa
        * escala_cm_por_unidade
    )

    return round(
        medida_cm,
        2,
    )


def estimar_medidas_corporais(
    geometria_corporal,
    escala_cm_por_unidade,
):
    """
    Converte a geometria corporal relativa do
    VesteIA em estimativas visuais de centímetros.

    Nesta fase do projeto essas medidas servem para
    experimentação e validação do pipeline.

    Elas ainda não devem ser tratadas como medidas
    antropométricas exatas nem usadas isoladamente
    para recomendar tamanho.
    """

    if not geometria_corporal:
        return {
            "status": "geometria_indisponivel",
            "largura_ombros_cm": None,
            "largura_quadril_cm": None,
        }

    if (
        escala_cm_por_unidade is None
        or escala_cm_por_unidade <= 0
    ):
        return {
            "status": "escala_indisponivel",
            "largura_ombros_cm": None,
            "largura_quadril_cm": None,
        }

    largura_ombros_relativa = (
        geometria_corporal.get(
            "largura_ombros"
        )
    )

    largura_quadril_relativa = (
        geometria_corporal.get(
            "largura_quadril"
        )
    )

    largura_ombros_cm = (
        converter_medida_relativa_para_cm(
            largura_ombros_relativa,
            escala_cm_por_unidade,
        )
    )

    largura_quadril_cm = (
        converter_medida_relativa_para_cm(
            largura_quadril_relativa,
            escala_cm_por_unidade,
        )
    )

    if (
        largura_ombros_cm is None
        and largura_quadril_cm is None
    ):
        status = "medidas_indisponiveis"

    elif (
        largura_ombros_cm is None
        or largura_quadril_cm is None
    ):
        status = "estimativa_parcial"

    else:
        status = "estimativa_visual_calculada"

    return {
        "status": status,

        "largura_ombros_cm": (
            largura_ombros_cm
        ),

        "largura_quadril_cm": (
            largura_quadril_cm
        ),

        "unidade": "cm",

        "tipo_medida": (
            "estimativa_visual_provisoria"
        ),

        "uso_para_recomendacao_tamanho": False,

        "mensagem": (
            "Medidas visuais estimadas em "
            "centímetros. A calibração anatômica "
            "de precisão ainda está pendente."
        ),
    }
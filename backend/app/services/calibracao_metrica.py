def calcular_fator_correcao_anatomica(
    altura_usuario_cm,
    altura_corpo_relativa,
    consistencia_geometrica,
):
    """
    Calcula o fator base necessário para transformar
    medidas relativas da imagem em estimativas métricas.

    A função somente libera a calibração quando:
    - existe altura real do usuário;
    - existe referência corporal relativa;
    - a geometria da imagem foi validada.

    Importante:
    este fator ainda representa uma calibração visual
    baseada em uma única imagem 2D.
    """

    if altura_usuario_cm is None:
        return {
            "status": "altura_usuario_indisponivel",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

    if altura_usuario_cm <= 0:
        return {
            "status": "altura_usuario_invalida",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

    if altura_corpo_relativa is None:
        return {
            "status": "referencia_corporal_indisponivel",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

    if altura_corpo_relativa <= 0:
        return {
            "status": "referencia_corporal_invalida",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

    if not consistencia_geometrica:
        return {
            "status": "geometria_nao_validada",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

    geometria_consistente = consistencia_geometrica.get(
        "consistente",
        False,
    )

    if not geometria_consistente:
        return {
            "status": "geometria_inconsistente",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

    fator = (
        altura_usuario_cm
        / altura_corpo_relativa
    )

    return {
        "status": "fator_calibracao_calculado",
        "calibracao_liberada": True,
        "altura_usuario_cm": round(
            altura_usuario_cm,
            2,
        ),
        "altura_corpo_relativa": round(
            altura_corpo_relativa,
            4,
        ),
        "fator_cm_por_unidade": round(
            fator,
            4,
        ),
        "tipo_calibracao": "visual_2d_por_altura",
        "precisao": "experimental",
        "mensagem": (
            "Fator de calibração visual calculado. "
            "As medidas resultantes continuam sendo "
            "estimativas e devem passar por correções "
            "anatômicas antes da recomendação de tamanho."
        ),
    }
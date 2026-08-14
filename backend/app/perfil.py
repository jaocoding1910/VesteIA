# Perfil temporário utilizado pelo MVP do VesteIA.
#
# Esses dados são atualizados pela rota PUT /perfil
# e utilizados pelo sistema de recomendação quando
# altura e peso não são enviados diretamente na requisição.
#
# IMPORTANTE:
# Atualmente os dados ficam somente na memória da aplicação.
# Ao reiniciar o servidor, eles voltam para None.
#
# Futuramente, o perfil poderá ser persistido no PostgreSQL
# e associado a um usuário autenticado.

perfil_usuario = {
    "altura_cm": None,
    "peso_kg": None,
    "cintura_cm": None
}
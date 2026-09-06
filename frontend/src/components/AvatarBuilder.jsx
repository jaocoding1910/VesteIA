import { useMemo, useState } from "react"


function AvatarBuilder({
  onAvatarChange,
  alturaInicial = 175,
  pesoInicial = 75,
}) {
  /*
   * VesteIA
   * Sprint 52 — Avatar Builder V2
   *
   * O usuário monta uma representação aproximada.
   * Esses valores NÃO são medidas extraídas da fotografia.
   */

  const [genero, setGenero] =
    useState("masculino")

  const [alturaCm, setAlturaCm] =
    useState(alturaInicial)

  const [pesoKg, setPesoKg] =
    useState(pesoInicial)

  const [porteCorporal, setPorteCorporal] =
    useState("medio")

  const [proporcaoTronco, setProporcaoTronco] =
    useState("media")

  const [proporcaoPernas, setProporcaoPernas] =
    useState("media")


  const perfilAvatar = useMemo(
    () => ({
      modo: "avatar",
      origem: "estimativa_usuario",

      genero,

      altura_aproximada_cm:
        Number(alturaCm),

      peso_aproximado_kg:
        Number(pesoKg),

      porte_corporal:
        porteCorporal,

      proporcao_tronco:
        proporcaoTronco,

      proporcao_pernas:
        proporcaoPernas,
    }),
    [
      genero,
      alturaCm,
      pesoKg,
      porteCorporal,
      proporcaoTronco,
      proporcaoPernas,
    ]
  )


  function atualizarAvatar(
    alteracoes = {}
  ) {
    if (
      typeof onAvatarChange !== "function"
    ) {
      return
    }

    onAvatarChange({
      ...perfilAvatar,
      ...alteracoes,
    })
  }


  function alterarGenero(
    novoGenero
  ) {
    setGenero(novoGenero)

    atualizarAvatar({
      genero:
        novoGenero,
    })
  }


  function alterarAltura(event) {
    const novaAltura =
      Number(event.target.value)

    setAlturaCm(novaAltura)

    atualizarAvatar({
      altura_aproximada_cm:
        novaAltura,
    })
  }


  function alterarPeso(event) {
    const novoPeso =
      Number(event.target.value)

    setPesoKg(novoPeso)

    atualizarAvatar({
      peso_aproximado_kg:
        novoPeso,
    })
  }


  function alterarPorte(novoPorte) {
    setPorteCorporal(novoPorte)

    atualizarAvatar({
      porte_corporal:
        novoPorte,
    })
  }


  function alterarTronco(
    novaProporcao
  ) {
    setProporcaoTronco(
      novaProporcao
    )

    atualizarAvatar({
      proporcao_tronco:
        novaProporcao,
    })
  }


  function alterarPernas(
    novaProporcao
  ) {
    setProporcaoPernas(
      novaProporcao
    )

    atualizarAvatar({
      proporcao_pernas:
        novaProporcao,
    })
  }


  return (
    <section
      className="vesteia-avatar-builder"
      data-vesteia-componente="avatar-builder"
    >

      <div className="vesteia-avatar-builder__cabecalho">

        <span>
          Avatar VesteIA
        </span>

        <h2>
          Monte seu avatar
        </h2>

        <p>
          Não precisa saber suas medidas
          exatas. Faça uma aproximação de
          como você se enxerga.
        </p>

      </div>


      {/* GÊNERO DO AVATAR */}

      <div className="vesteia-avatar-builder__grupo">

        <strong>
          Modelo do avatar
        </strong>

        <div className="vesteia-avatar-builder__opcoes vesteia-avatar-builder__opcoes--duas">

          <button
            type="button"
            data-ativo={
              genero ===
              "masculino"
            }
            onClick={() =>
              alterarGenero(
                "masculino"
              )
            }
          >
            Masculino
          </button>

          <button
            type="button"
            data-ativo={
              genero ===
              "feminino"
            }
            onClick={() =>
              alterarGenero(
                "feminino"
              )
            }
          >
            Feminino
          </button>

        </div>

      </div>


      {/* ALTURA */}

      <div className="vesteia-avatar-builder__controle">

        <div>
          <strong>
            Altura aproximada
          </strong>

          <span>
            {alturaCm} cm
          </span>
        </div>

        <input
          type="range"
          min="140"
          max="210"
          step="1"
          value={alturaCm}
          onChange={alterarAltura}
          aria-label="Altura aproximada"
        />

        <small>
          Não precisa ser exato.
        </small>

      </div>


      {/* PESO */}

      <div className="vesteia-avatar-builder__controle">

        <div>
          <strong>
            Peso aproximado
          </strong>

          <span>
            {pesoKg} kg
          </span>
        </div>

        <input
          type="range"
          min="40"
          max="160"
          step="1"
          value={pesoKg}
          onChange={alterarPeso}
          aria-label="Peso aproximado"
        />

        <small>
          Use apenas uma estimativa.
        </small>

      </div>


      {/* PORTE */}

      <div className="vesteia-avatar-builder__grupo">

        <strong>
          Como você descreveria seu corpo?
        </strong>

        <div className="vesteia-avatar-builder__opcoes">

          <button
            type="button"
            data-ativo={
              porteCorporal ===
              "estreito"
            }
            onClick={() =>
              alterarPorte(
                "estreito"
              )
            }
          >
            Estreito
          </button>

          <button
            type="button"
            data-ativo={
              porteCorporal ===
              "medio"
            }
            onClick={() =>
              alterarPorte(
                "medio"
              )
            }
          >
            Médio
          </button>

          <button
            type="button"
            data-ativo={
              porteCorporal ===
              "largo"
            }
            onClick={() =>
              alterarPorte(
                "largo"
              )
            }
          >
            Largo
          </button>

        </div>

      </div>


      {/* TRONCO */}

      <div className="vesteia-avatar-builder__grupo">

        <strong>
          Proporção do tronco
        </strong>

        <div className="vesteia-avatar-builder__opcoes">

          <button
            type="button"
            data-ativo={
              proporcaoTronco ===
              "curto"
            }
            onClick={() =>
              alterarTronco(
                "curto"
              )
            }
          >
            Curto
          </button>

          <button
            type="button"
            data-ativo={
              proporcaoTronco ===
              "media"
            }
            onClick={() =>
              alterarTronco(
                "media"
              )
            }
          >
            Médio
          </button>

          <button
            type="button"
            data-ativo={
              proporcaoTronco ===
              "longo"
            }
            onClick={() =>
              alterarTronco(
                "longo"
              )
            }
          >
            Longo
          </button>

        </div>

      </div>


      {/* PERNAS */}

      <div className="vesteia-avatar-builder__grupo">

        <strong>
          Proporção das pernas
        </strong>

        <div className="vesteia-avatar-builder__opcoes">

          <button
            type="button"
            data-ativo={
              proporcaoPernas ===
              "curtas"
            }
            onClick={() =>
              alterarPernas(
                "curtas"
              )
            }
          >
            Curtas
          </button>

          <button
            type="button"
            data-ativo={
              proporcaoPernas ===
              "media"
            }
            onClick={() =>
              alterarPernas(
                "media"
              )
            }
          >
            Médias
          </button>

          <button
            type="button"
            data-ativo={
              proporcaoPernas ===
              "longas"
            }
            onClick={() =>
              alterarPernas(
                "longas"
              )
            }
          >
            Longas
          </button>

        </div>

      </div>


      <details className="vesteia-avatar-builder__debug">

        <summary>
          Perfil do avatar
        </summary>

        <pre>
          {JSON.stringify(
            perfilAvatar,
            null,
            2
          )}
        </pre>

      </details>

    </section>
  )
}


export default AvatarBuilder

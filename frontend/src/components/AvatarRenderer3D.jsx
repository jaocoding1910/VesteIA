import { useMemo } from "react"


function AvatarRenderer3D({
  avatar,
  produto = null,
  tamanhoSelecionado = null,
}) {
  /*
   * VesteIA
   * Sprint 52 — Avatar Humanoide V3
   *
   * Objetivos:
   * - silhueta mais humana;
   * - suporte visual masculino e feminino;
   * - responder ao AvatarBuilder;
   * - representar altura, peso, porte, tronco e pernas;
   * - receber produto e tamanho;
   * - manter separado do AvatarRenderer2D baseado em foto.
   *
   * IMPORTANTE:
   * Este preview usa dados aproximados informados pelo usuário.
   * Não representa medidas físicas extraídas automaticamente da foto.
   */

  const perfil = avatar ?? {
    modo: "avatar",
    origem: "estimativa_usuario",
    genero: "masculino",
    altura_aproximada_cm: 175,
    peso_aproximado_kg: 75,
    porte_corporal: "medio",
    proporcao_tronco: "media",
    proporcao_pernas: "media",
  }

  const genero =
    perfil.genero === "feminino"
      ? "feminino"
      : "masculino"


  // =========================================================
  // ALTURA
  // =========================================================

  const escalaAltura = useMemo(() => {
    const altura =
      Number(perfil.altura_aproximada_cm) || 175

    return Math.min(
      1.16,
      Math.max(
        0.84,
        altura / 175
      )
    )
  }, [
    perfil.altura_aproximada_cm,
  ])


  // =========================================================
  // PESO + PORTE
  // =========================================================

  const escalaLargura = useMemo(() => {
    const peso =
      Number(perfil.peso_aproximado_kg) || 75

    let escalaPeso =
      1 + (peso - 75) * 0.0032

    escalaPeso = Math.min(
      1.23,
      Math.max(
        0.82,
        escalaPeso
      )
    )

    const portes = {
      estreito: 0.9,
      medio: 1,
      largo: 1.1,
    }

    return (
      escalaPeso *
      (portes[perfil.porte_corporal] ?? 1)
    )
  }, [
    perfil.peso_aproximado_kg,
    perfil.porte_corporal,
  ])


  // =========================================================
  // OMBROS
  // =========================================================

  const escalaOmbros = useMemo(() => {
    const portes = {
      estreito: 0.9,
      medio: 1,
      largo: 1.12,
    }

    const base =
      portes[perfil.porte_corporal] ?? 1

    return genero === "feminino"
      ? base * 0.94
      : base
  }, [
    perfil.porte_corporal,
    genero,
  ])


  // =========================================================
  // QUADRIL
  // =========================================================

  const escalaQuadril = useMemo(() => {
    const base =
      perfil.porte_corporal === "estreito"
        ? 0.94
        : perfil.porte_corporal === "largo"
          ? 1.08
          : 1

    return genero === "feminino"
      ? base * 1.1
      : base
  }, [
    perfil.porte_corporal,
    genero,
  ])


  // =========================================================
  // TRONCO
  // =========================================================

  const escalaTronco = useMemo(() => {
    const proporcoes = {
      curto: 0.9,
      media: 1,
      longo: 1.1,
    }

    return (
      proporcoes[
        perfil.proporcao_tronco
      ] ?? 1
    )
  }, [
    perfil.proporcao_tronco,
  ])


  // =========================================================
  // PERNAS
  // =========================================================

  const escalaPernas = useMemo(() => {
    const proporcoes = {
      curtas: 0.9,
      media: 1,
      longas: 1.1,
    }

    return (
      proporcoes[
        perfil.proporcao_pernas
      ] ?? 1
    )
  }, [
    perfil.proporcao_pernas,
  ])


  // =========================================================
  // TIPO DE ROUPA
  // =========================================================

  const categoriaProduto =
    produto?.categoria
      ?.toLowerCase()
      ?.trim() ?? ""


  const tipoRoupa = useMemo(() => {
    if (
      categoriaProduto.includes("camiseta") ||
      categoriaProduto.includes("camisa")
    ) {
      return "superior"
    }

    if (
      categoriaProduto.includes("calça") ||
      categoriaProduto.includes("calca")
    ) {
      return "calca"
    }

    if (
      categoriaProduto.includes("short") ||
      categoriaProduto.includes("bermuda")
    ) {
      return "short"
    }

    if (
      categoriaProduto.includes("saia")
    ) {
      return "saia"
    }

    if (
      categoriaProduto.includes("vestido")
    ) {
      return "vestido"
    }

    return "generica"
  }, [
    categoriaProduto,
  ])


  const estiloAvatar = {
    "--avatar-altura":
      escalaAltura,

    "--avatar-largura":
      escalaLargura,

    "--avatar-ombros":
      escalaOmbros,

    "--avatar-quadril":
      escalaQuadril,

    "--avatar-tronco":
      escalaTronco,

    "--avatar-pernas":
      escalaPernas,
  }


  return (
    <section
      className="vesteia-avatar-renderer3d"
      data-vesteia-componente="avatar-renderer-3d"
    >

      <div className="vesteia-avatar-renderer3d__cabecalho">

        <span>
          AVATAR INTERATIVO
        </span>

        <h2>
          Seu avatar VesteIA
        </h2>

        <p>
          Ajuste seu corpo e visualize
          o caimento da peça em tempo real.
        </p>

      </div>


      <div className="vesteia-avatar-renderer3d__palco">

        <div
          className={[
            "vesteia-avatar-renderer3d__avatar",
            `vesteia-avatar-renderer3d__avatar--${genero}`,
          ].join(" ")}
          data-genero={genero}
          style={estiloAvatar}
        >

          {/* CABEÇA */}

          <div className="vesteia-avatar-renderer3d__cabeca">

            <div className="vesteia-avatar-renderer3d__cabelo" />

            <div className="vesteia-avatar-renderer3d__orelha vesteia-avatar-renderer3d__orelha--esquerda" />

            <div className="vesteia-avatar-renderer3d__orelha vesteia-avatar-renderer3d__orelha--direita" />

            <div className="vesteia-avatar-renderer3d__sobrancelhas">
              <i />
              <i />
            </div>

            <div className="vesteia-avatar-renderer3d__olhos">
              <i />
              <i />
            </div>

            <div className="vesteia-avatar-renderer3d__nariz" />

            <div className="vesteia-avatar-renderer3d__boca" />

            <div className="vesteia-avatar-renderer3d__maxilar" />

          </div>


          {/* PESCOÇO */}

          <div className="vesteia-avatar-renderer3d__pescoco" />


          {/* OMBROS */}

          <div className="vesteia-avatar-renderer3d__ombros" />


          {/* CORPO SUPERIOR */}

          <div className="vesteia-avatar-renderer3d__corpo">

            <div className="vesteia-avatar-renderer3d__membro-superior vesteia-avatar-renderer3d__membro-superior--esquerdo">

              <div className="vesteia-avatar-renderer3d__deltoide" />

              <div className="vesteia-avatar-renderer3d__braco" />

              <div className="vesteia-avatar-renderer3d__cotovelo" />

              <div className="vesteia-avatar-renderer3d__antebraco" />

              <div className="vesteia-avatar-renderer3d__pulso" />

              <div className="vesteia-avatar-renderer3d__mao" />

            </div>


            <div className="vesteia-avatar-renderer3d__tronco">

              <div className="vesteia-avatar-renderer3d__peitoral" />

              {genero === "feminino" && (
                <div className="vesteia-avatar-renderer3d__busto" />
              )}

              <div className="vesteia-avatar-renderer3d__torax" />

              <div className="vesteia-avatar-renderer3d__abdomen" />

              <div className="vesteia-avatar-renderer3d__cintura" />


              {produto &&
                tipoRoupa === "superior" && (

                <div className="vesteia-avatar-renderer3d__camiseta">

                  <div className="vesteia-avatar-renderer3d__gola" />

                  <div className="vesteia-avatar-renderer3d__manga vesteia-avatar-renderer3d__manga--esquerda" />

                  <div className="vesteia-avatar-renderer3d__manga vesteia-avatar-renderer3d__manga--direita" />

                  <div className="vesteia-avatar-renderer3d__camiseta-corpo">

                    {tamanhoSelecionado && (
                      <span>
                        {tamanhoSelecionado}
                      </span>
                    )}

                  </div>

                </div>
              )}


              {produto &&
                tipoRoupa === "vestido" && (

                <div className="vesteia-avatar-renderer3d__vestido">

                  {tamanhoSelecionado && (
                    <span>
                      {tamanhoSelecionado}
                    </span>
                  )}

                </div>
              )}

            </div>


            <div className="vesteia-avatar-renderer3d__membro-superior vesteia-avatar-renderer3d__membro-superior--direito">

              <div className="vesteia-avatar-renderer3d__deltoide" />

              <div className="vesteia-avatar-renderer3d__braco" />

              <div className="vesteia-avatar-renderer3d__cotovelo" />

              <div className="vesteia-avatar-renderer3d__antebraco" />

              <div className="vesteia-avatar-renderer3d__pulso" />

              <div className="vesteia-avatar-renderer3d__mao" />

            </div>

          </div>


          {/* QUADRIL */}

          <div className="vesteia-avatar-renderer3d__quadril">

            <div className="vesteia-avatar-renderer3d__pelve" />

            {produto &&
              tipoRoupa === "short" && (

              <div className="vesteia-avatar-renderer3d__short">
                {tamanhoSelecionado}
              </div>
            )}

            {produto &&
              tipoRoupa === "saia" && (

              <div className="vesteia-avatar-renderer3d__saia">
                {tamanhoSelecionado}
              </div>
            )}

          </div>


          {/* PERNAS */}

          <div className="vesteia-avatar-renderer3d__pernas">

            <div className="vesteia-avatar-renderer3d__membro-inferior vesteia-avatar-renderer3d__membro-inferior--esquerdo">

              <div className="vesteia-avatar-renderer3d__coxa" />

              <div className="vesteia-avatar-renderer3d__joelho" />

              <div className="vesteia-avatar-renderer3d__panturrilha" />

              <div className="vesteia-avatar-renderer3d__tornozelo" />

              <div className="vesteia-avatar-renderer3d__pe" />

            </div>


            <div className="vesteia-avatar-renderer3d__membro-inferior vesteia-avatar-renderer3d__membro-inferior--direito">

              <div className="vesteia-avatar-renderer3d__coxa" />

              <div className="vesteia-avatar-renderer3d__joelho" />

              <div className="vesteia-avatar-renderer3d__panturrilha" />

              <div className="vesteia-avatar-renderer3d__tornozelo" />

              <div className="vesteia-avatar-renderer3d__pe" />

            </div>


            {produto &&
              tipoRoupa === "calca" && (

              <div className="vesteia-avatar-renderer3d__calca">

                <div className="vesteia-avatar-renderer3d__calca-perna vesteia-avatar-renderer3d__calca-perna--esquerda" />

                <div className="vesteia-avatar-renderer3d__calca-perna vesteia-avatar-renderer3d__calca-perna--direita" />

                {tamanhoSelecionado && (
                  <span>
                    {tamanhoSelecionado}
                  </span>
                )}

              </div>
            )}

          </div>

        </div>


        <div className="vesteia-avatar-renderer3d__sombra" />

        <div className="vesteia-avatar-renderer3d__base" />


        <div className="vesteia-avatar-renderer3d__status">

          <span>
            Avatar ativo
          </span>

          <small>
            {genero === "feminino"
              ? "Avatar feminino aproximado"
              : "Avatar masculino aproximado"}
          </small>

        </div>

      </div>


      <div className="vesteia-avatar-renderer3d__informacoes">

        <div>
          <span>Gênero</span>
          <strong>
            {genero}
          </strong>
        </div>

        <div>
          <span>Altura</span>
          <strong>
            {perfil.altura_aproximada_cm} cm
          </strong>
        </div>

        <div>
          <span>Peso</span>
          <strong>
            {perfil.peso_aproximado_kg} kg
          </strong>
        </div>

        <div>
          <span>Porte</span>
          <strong>
            {perfil.porte_corporal}
          </strong>
        </div>

        <div>
          <span>Tronco</span>
          <strong>
            {perfil.proporcao_tronco}
          </strong>
        </div>

        <div>
          <span>Pernas</span>
          <strong>
            {perfil.proporcao_pernas}
          </strong>
        </div>

      </div>


      {produto && (

        <div className="vesteia-avatar-renderer3d__produto">

          <span>
            Experimentando
          </span>

          <strong>
            {produto.nome}
          </strong>

          {tamanhoSelecionado && (

            <small>
              Tamanho selecionado:{" "}
              {tamanhoSelecionado}
            </small>

          )}

        </div>
      )}

    </section>
  )
}


export default AvatarRenderer3D

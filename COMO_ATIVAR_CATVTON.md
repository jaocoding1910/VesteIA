# VesteIA 1.5.8 — CatVTON local e bases fotográficas

## Atualizar seu projeto sem trocar de site

Este pacote usa o VesteIA 1.5.7 como base. Para atualizar essa versão já aberta:

1. Faça uma cópia de segurança da pasta do seu projeto.
2. Descompacte **VesteIA_Atualizacao_CatVTON_1_5_8.zip** numa pasta temporária.
3. Abra a pasta `vesteia` da atualização e copie seu conteúdo para dentro da pasta `vesteia` do projeto atual. Aceite substituir os arquivos de mesmo nome. O pacote contém somente os arquivos alterados e adicionados; seu `backend/.env` e o banco não estão nele.
4. Na raiz `vesteia`, execute **CONFIGURAR_IA_LOCAL.bat** com dois cliques. Ele modifica somente `TRYON_ENABLED`, `TRYON_PROVIDER` e `TRYON_CATVTON_URL` no seu `.env` existente. A senha do PostgreSQL permanece como está.
5. No terminal do CatVTON antigo, que abre `127.0.0.1:7860`, pressione **Ctrl+C**. Isso libera a GPU. Não rode as duas instâncias juntas.
6. Na raiz do VesteIA, abra **INICIAR_IA_LOCAL.bat**. Espere aparecer **“VesteIA: CatVTON pronto em http://127.0.0.1:7861”**. Mantenha essa janela aberta.
7. Reinicie o backend atual: **Ctrl+C**, depois `python -m uvicorn app.main:app --reload`, dentro de `backend` e usando o mesmo ambiente virtual que você já usa. Se você abre por **INICIAR_BACKEND.bat**, feche a janela antiga e abra esse arquivo novamente.
8. Mantenha o frontend aberto com `npm run dev`. Atualize a página do VesteIA; se necessário reinicie esse terminal também. Não há dependência nova do frontend/backend para instalar.

Para abrir o projeto completo em outra pasta, use **VesteIA_1_5_8_CatVTON_Completo.zip**, configure `backend/.env` e inicie backend/frontend pelos arquivos BAT habituais. Depois siga os passos 4 a 8 acima.

## Fazer a primeira prova

1. Abra um produto da loja demo e seu provador.
2. Expanda **Prévia realista com IA**.
3. Deixe **Base fotográfica** e escolha **Masculino** ou **Feminino**. Também é possível enviar **Minha foto**.
4. A imagem da peça vem da variante selecionada no catálogo. Caso a imagem do catálogo seja uma pessoa vestida, um desenho ou esteja incompleta, envie uma foto frontal da peça inteira em **Foto da peça**. A frente da peça deve estar visível.
5. Marque a autorização para processamento local e clique **Gerar prévia realista**.
6. Aguarde. São 30 passos em 384 × 512 para começar na sua GPU de 6 GB. Não clique novamente durante a geração. O botão habilita após o serviço local ficar pronto; a página verifica o estado a cada 10 segundos.

Camisetas, camisas, blusas, regatas, casacos e jaquetas usam máscara superior; calças, shorts, bermudas e saias usam máscara inferior; vestidos usam máscara do corpo inteiro. Bonés e calçados permanecem no 2D e não são enviados ao CatVTON. O modo IA gera uma peça por vez, não um look completo em uma chamada.

## O que foi preservado e o que muda

O provador 2D, personalização, catálogo, medidas, recomendação e prévia calibrada continuam funcionando. O CatVTON é uma opção adicional no mesmo provador. Não há migração de banco. Para imagens específicas de prova, pode-se manter `variante.metadata.visual.tryon_image_url`; senão usa a imagem normal da variante.

As bases são fotografias sintéticas de adultos fictícios, sem acessórios, com braços afastados e roupa neutra. São referências fixas: a personalização de cabelo, pele e corpo do 2D não modifica essas duas fotografias. Para uma referência do próprio cliente, envie sua foto. A roupa neutra da região selecionada é substituída; a roupa de outras regiões fica na foto. O CatVTON ainda pode alterar estampa, proporção e detalhes dentro da máscara. As medidas do banco continuam orientando a comparação de tamanhos, mas este modelo não simula caimento exato em centímetros nem troca automaticamente a imagem ao selecionar P/M/G/GG.

A ponte aplica a imagem gerada somente dentro da máscara da roupa, preservando os pixels originais de rosto, corpo e fundo fora dela. Não há garantia de zero deformação nas áreas mascaradas. Mantivemos os filtros de segurança originais do modelo.

## Onde roda e solução de problemas

O iniciador procura `C:\Users\jaolu\VesteIA-IA-Local\CatVTON` e o ambiente `.venv` que você já instalou na pasta acima. Ele copia **somente** `vesteia_worker.py` para perto do `app.py`, sem substituir esse arquivo ou reinstalar o ambiente. Se seu caminho mudar, ajuste `CAT_ROOT` e `CAT_PY` em `INICIAR_IA_LOCAL.bat`.

A ponte usa os modelos carregados pelo `app.py` oficial, recebe imagens em memória e não executa a função Gradio que salva montagens. Só escuta em `127.0.0.1:7861`, sem túnel público. Entradas e resultados não são gravados por essa ponte. Os pesos já baixados continuam no cache; se faltarem pesos, o CatVTON pode baixá-los novamente na inicialização.

- **Botão desabilitado:** confira o `.env`, reinicie o backend e aguarde a mensagem de pronto da IA. Abra `http://127.0.0.1:7861/health` no navegador: deve mostrar `ready: true`.
- **Memória insuficiente:** feche a demo antiga em 7860 e programas que usam GPU. Reinicie a ponte. O 2D continua disponível.
- **Resultado estranho:** tente uma fotografia frontal bem iluminada e uma foto limpa da roupa. Avatares desenhados/3D são mantidos como opção experimental e podem deformar.
- **Porta em uso:** feche a ponte antiga antes de abrir outra. Não abra dois iniciadores juntos.
- **Falha ao carregar modelos:** confira o erro no terminal da IA; este pacote depende do CatVTON instalado e funcionando, como no teste anterior.

## Testes e licença

Build e lint do frontend; testes do fluxo no navegador; validação de imagens, configuração, indisponibilidade, concorrência, envio das categorias e HTTP entre backend e ponte. A inferência foi simulada nesses testes: este ambiente não tem sua GPU nem os pesos locais para validar um novo resultado real. O primeiro teste real será na máquina em que seu CatVTON já gerou imagens.

CatVTON oficial: https://github.com/Zheng-Chong/CatVTON. Código e pesos são disponibilizados sob CC BY-NC-SA 4.0, para uso não comercial; esta integração é para o protótipo/MVP de demonstração. Não inclui pesos ou cobrança por API e não altera essa licença. Para oferecer comercialmente à loja, será preciso um modelo/serviço com autorização de uso comercial.

Bases criadas com a ferramenta de imagens integrada. Prompt: fotografia de adulto fictício de corpo inteiro, frente, proporções naturais, camiseta cinza e bermuda neutras, braços afastados, fundo de estúdio claro e iluminação uniforme; masculino com cabelo curto crespo e feminino com cabelo crespo preso.

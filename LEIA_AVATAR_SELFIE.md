# VesteIA — Avatar por selfie: experimento local

## O que este pacote entrega

- Novo modo Selfie → avatar experimental → aprovação → CatVTON → antes/depois.
- Avatar aprovado reutilizável entre produtos durante a mesma aba aberta. Recarregar a página apaga o avatar da memória.
- IP-Adapter Plus Face + Stable Diffusion 1.5 Inpainting: regenera rosto/cabelo em um corpo de referência fotográfico. Não é reconstrução das medidas ou da anatomia do cliente. O corpo de referência mantém suas próprias proporções e tom de pele fora da região da cabeça. A semelhança pode variar; descarte qualquer resultado inadequado.
- Comparação dimensional ilustrativa: contornos em escala comum para largura/comprimento cadastrados e diferenças entre circunferências da peça e medidas informadas. NÃO são quatro fotos de caimento geradas. O CatVTON atual não aceita medidas físicas de tamanhos como controle.
- Provador 2D antigo preservado, recolhido em uma seção opcional.
- Homepage, vídeo, catálogo, perfil, favoritos e sacola preservados.

## Aplicar no projeto existente

1. Pare backend e frontend com Ctrl+C. Pare também a IA CatVTON antes de configurar o avatar.
2. Extraia este ZIP em uma pasta separada. Não apague nenhuma pasta do projeto.
3. Abra APLICAR_ATUALIZACAO.bat dentro do pacote extraído.
4. Cole o caminho completo da pasta **vesteia** que está aberta no VS Code, sem acrescentar frontend/backend.
5. O aplicador copia um backup dos arquivos que serão alterados e mescla os arquivos. Não toca no .env, banco, .venv, node_modules nem no worker CatVTON personalizado.
6. Se preferir copiar manualmente, copie o conteúdo das pastas frontend, backend e integracao sobre as correspondentes, substituindo arquivos repetidos SEM excluir as pastas existentes. Copie também os dois novos BATs para a raiz vesteia. O frontend está completo (inclui package.json). O backend neste pacote é uma atualização parcial.

## Configurar uma única vez

Na pasta principal vesteia, no terminal PowerShell:

```powershell
.\CONFIGURAR_AVATAR_LOCAL.bat
```

É uma instalação nova e separada em %USERPROFILE%\VesteIA-Avatar-Local\.venv. Não atualiza dependências do CatVTON nem do backend existente. Requer Python 3.12 e GPU NVIDIA com CUDA. Instala PyTorch 2.5.1 CUDA 12.1 e dependências fixadas, e baixa modelos públicos do Hugging Face (vários GB). Não pede cartão nem chave de API. Fotos não são enviadas a esses repositórios; somente os modelos são baixados.

A instalação e o download podem demorar. Espere a mensagem “Configuracao concluida”. Se falhar, não continue às cegas: copie o erro do terminal. A necessidade real de RAM/VRAM e a qualidade deste modelo ainda precisam ser validadas no notebook do usuário. Feche a IA CatVTON antes desta etapa, pois os modelos não devem competir pela GPU/RAM.

## Iniciar os serviços

Três terminais na raiz vesteia:

```powershell
.\INICIAR_BACKEND.bat
```

```powershell
.\INICIAR_FRONTEND.bat
```

```powershell
.\INICIAR_AVATAR_LOCAL.bat
```

O novo serviço usa http://127.0.0.1:7862. O backend fala com ele automaticamente; não precisa alterar .env, senha ou banco. O CatVTON mantém a configuração anterior em 7861.

## Primeiro teste real

1. Abra um produto no site e escolha “Minha selfie → avatar”.
2. Envie uma selfie frontal ou 3×4, com exatamente um rosto visível, sem filtro e com boa iluminação. Não é necessário corpo inteiro nessa etapa.
3. Escolha o corpo de referência, autorize e clique “Gerar meu avatar experimental”.
4. O terminal CatVTON precisa estar parado durante a geração. O gerador rejeita a solicitação se detectar o CatVTON ativo, para evitar disputa de memória. O modelo do avatar carrega em um processo separado e é liberado ao terminar; cada novo avatar recarrega os modelos do cache.
5. Confira rosto/cabelo, pose e resultado. Não aprove se a identidade ficou inadequada. A aprovação é manual, sem reconhecimento biométrico.
6. Aprove o avatar. Só agora abra outro terminal na raiz vesteia e execute:

```powershell
.\INICIAR_IA_LOCAL.bat
```

7. Aguarde a IA ficar pronta. Escolha a foto da peça, autorize o processamento e clique “Gerar prévia realista”. A referência enviada ao CatVTON será o avatar aprovado, não a selfie pequena.
8. Confira antes/depois. Na aba Comparar tamanhos, informe suas circunferências e compare o guia da tabela. Selecionar P/M/G/GG não altera a imagem fotográfica nesta versão.
9. Você pode mudar de produto sem gerar outro avatar enquanto permanecer nesta aba do navegador. Recarregar a página ou descartar remove a referência da memória. Salvar avatar/resultado só grava no disco quando você clicar em baixar.

## Limites e validação

Não é a perfeição do vídeo. Este é um primeiro pipeline local experimental. O IP-Adapter orienta aparência facial, sem garantir identidade exata. O corpo é de referência. O CatVTON ainda pode inventar detalhes da peça; este pacote não treina nem substitui seus pesos e não modifica seus ajustes JSON. Para esse motor, calçados e bonés continuam fora das categorias de geração.

Verificado neste ambiente: build frontend; lint sem erros (2 avisos antigos); 20 testes backend/contratos/validação/isolamento; teste das unidades de medidas; navegador com APIs de geração simuladas para validar upload, bloqueio de memória, aprovação, envio do avatar, antes/depois, seleção de tamanho, descarte e layout móvel. Não há GPU neste ambiente: pesos/modelos e qualidade fotográfica NÃO foram executados aqui. A captura de interface fornecida usa imagens de referência em respostas simuladas, não prova de geração deste modelo.

## Referências técnicas

- https://huggingface.co/docs/diffusers/using-diffusers/ip_adapter
- https://huggingface.co/h94/IP-Adapter (Apache 2.0)
- https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-inpainting (CreativeML OpenRAIL M)

O código integra pesos existentes; não é treinamento de uma IA própria. Baixe os modelos somente pelo configurador/URLs oficiais. Os termos dos modelos continuam aplicáveis.

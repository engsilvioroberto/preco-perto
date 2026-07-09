# PreçoPerto — Especificação Funcional

> **Versão:** 1.0  
> **Data:** 2026-07-09  
> **Status:** Draft  

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [User Stories](#user-stories)
3. [Requisitos Funcionais](#requisitos-funcionais)
4. [Tabela de Prioridades](#tabela-de-prioridades)
5. [Glossário](#glossário)

---

## Visão Geral

O **PreçoPerto** é um aplicativo mobile (Android/iOS) que permite ao consumidor comparar preços de produtos de supermercado a partir de notas fiscais escaneadas, ofertas de jornal e contribuições da comunidade, exibindo os resultados em um mapa interativo.

**Objetivo principal:** ajudar o usuário a encontrar o menor preço para cada produto nos mercados mais próximos da sua localização.

---

## User Stories

### US1 — Escaneamento de Nota Fiscal

> **Como** usuário,  
> **quero** escanear uma nota fiscal (foto ou PDF),  
> **para que** eu possa ver os preços dos produtos comprados registrados no app.

**Contexto:** O usuário acabou de fazer compras e deseja contribuir com a base de preços ou simplesmente registrar seus gastos.

---

### US2 — Mapa de Preços

> **Como** usuário,  
> **quero** ver no mapa onde cada produto está mais barato,  
> **para que** eu possa decidir em qual mercado ir com base na proximidade e no preço.

**Contexto:** O usuário está planejando suas compras da semana e quer otimizar o custo total.

---

### US3 — Busca de Produto

> **Como** usuário,  
> **quero** buscar um produto e ver preços nos mercados próximos,  
> **para que** eu possa encontrar rapidamente a melhor oferta para um item específico.

**Contexto:** O usuário precisa de um produto específico (ex: leite integral 1L) e quer saber onde está mais barato perto dele.

---

### US4 — Histórico de Preços

> **Como** usuário,  
> **quero** ver o histórico de preços de um produto,  
> **para que** eu possa identificar se o preço atual é uma boa oportunidade ou se está subindo.

**Contexto:** O usuário quer acompanhar a variação de preço ao longo do tempo para tomar decisões de compra mais inteligentes.

---

### US5 — Contribuição com Ofertas de Jornal

> **Como** usuário,  
> **quero** contribuir com fotos de encartes/ofertas de jornal,  
> **para que** a comunidade tenha acesso a promoções que não estão em notas fiscais.

**Contexto:** Muitos mercados divulgam ofertas em encartes impressos. O usuário fotografa o encarte e o sistema extrai os preços.

---

### US6 — Compartilhamento de Achados

> **Como** usuário,  
> **quero** compartilhar um achado de preço baixo,  
> **para que** meus amigos e familiares possam se beneficiar da oferta.

**Contexto:** O usuário encontrou uma promoção imperdível e quer enviar para o grupo da família no WhatsApp.

---

## Requisitos Funcionais

### FR1 — Upload e Processamento de Nota Fiscal (US1)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve aceitar upload de imagem (JPG/PNG) ou PDF de uma nota fiscal e extrair automaticamente os itens (nome, quantidade, preço unitário, preço total) via OCR. |
| **Entrada** | Arquivo de imagem (máx. 10MB) ou PDF de até 5 páginas. |
| **Saída** | Lista estruturada de produtos com nome, quantidade, preço unitário e preço total. |
| **Regras** | - O sistema deve permitir que o usuário confirme/corrija os itens extraídos antes de salvar.<br>- Notas fiscais eletrônicas (XML) também são aceitas como entrada alternativa.<br>- Dados de localização (GPS) são capturados no momento do upload. |
| **Prioridade** | **P0** (MVP) |

**Critérios de Aceitação:**
- [ ] AC1.1: O upload de uma imagem de NF retorna uma lista de itens em até 30 segundos.
- [ ] AC1.2: O usuário pode editar nome, quantidade e preço de cada item antes de confirmar.
- [ ] AC1.3: Após confirmação, os dados são persistidos e associados à localização GPS do dispositivo.
- [ ] AC1.4: Upload de XML de NF-e é processado sem perda de informação.

---

### FR2 — Extração de Dados via OCR (US1)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve utilizar OCR para extrair texto de imagens de notas fiscais e encartes, identificando padrões de preço, nome de produto e quantidade. |
| **Entrada** | Imagem (JPG/PNG/HEIC) com resolução mínima de 720p. |
| **Saída** | Texto estruturado com campos: produto, quantidade, preço unitário, preço total, data. |
| **Regras** | - Taxa de acerto mínima esperada: 85% dos campos extraídos corretamente.<br>- O sistema deve sinalizar campos com baixa confiança para revisão manual. |
| **Prioridade** | **P0** (MVP) |

**Critérios de Aceitação:**
- [ ] AC2.1: Campos com confiança < 80% são marcados visualmente para o usuário revisar.
- [ ] AC2.2: O OCR suporta notas fiscais de ao menos 5 formatos diferentes (cupom térmico, NF-e impressa, etc.).
- [ ] AC2.3: Preços são normalizados para o formato brasileiro (R$ X,XX).

---

### FR3 — Exibição em Mapa Interativo (US2)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve exibir em um mapa interativo os mercados com seus respectivos preços para um produto selecionado, com marcadores coloridos por faixa de preço. |
| **Entrada** | Produto selecionado + localização do usuário (GPS ou endereço manual). |
| **Saída** | Mapa com marcadores dos mercados, cada um mostrando o preço do produto e a distância até o usuário. |
| **Regras** | - Marcadores verdes = preço mais baixo (até 10% acima do mínimo); amarelos = médio; vermelhos = mais alto.<br>- Raio padrão de busca: 5 km (ajustável pelo usuário).<br>- Mapa deve permitir zoom e pan. |
| **Prioridade** | **P0** (MVP) |

**Critérios de Aceitação:**
- [ ] AC3.1: O mapa carrega em até 3 segundos com conexão 4G.
- [ ] AC3.2: Cada marcador exibe nome do mercado, preço do produto e distância.
- [ ] AC3.3: O usuário pode alterar o raio de busca (1km, 5km, 10km, 20km).
- [ ] AC3.4: A legenda de cores é exibida no canto do mapa.

---

### FR4 — Geolocalização e Permissão de Localização (US2)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve solicitar permissão de localização ao usuário e utilizar GPS ou rede para determinar sua posição atual. |
| **Entrada** | Permissão do usuário para acesso à localização. |
| **Saída** | Coordenadas (latitude, longitude) utilizadas para filtrar mercados próximos. |
| **Regras** | - Se o usuário negar a permissão, deve ser possível inserir um endereço/CEP manualmente.<br>- A localização é usada apenas para filtrar resultados, nunca compartilhada sem consentimento. |
| **Prioridade** | **P0** (MVP) |

**Critérios de Aceitação:**
- [ ] AC4.1: Na primeira abertura, o app solicita permissão de localização de forma clara.
- [ ] AC4.2: Se negada, um campo de busca por endereço/CEP é exibido como alternativa.
- [ ] AC4.3: A localização não é enviada a terceiros sem consentimento explícito.

---

### FR5 — Busca de Produto por Nome ou Código de Barras (US3)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve permitir buscar um produto por nome (texto livre) ou por código de barras (scanner da câmera), retornando preços nos mercados próximos. |
| **Entrada** | Texto de busca OU código de barras escaneado via câmera. |
| **Saída** | Lista de resultados com nome do produto, mercados onde está disponível e respectivos preços. |
| **Regras** | - Busca por nome deve suportar busca parcial e tolerante a erros de digitação (fuzzy).<br>- Scanner de código de barras deve suportar EAN-13 e Code 128.<br>- Resultados ordenados por preço (menor → maior) por padrão. |
| **Prioridade** | **P0** (MVP) |

**Critérios de Aceitação:**
- [ ] AC5.1: Busca por "leite integral" retorna resultados em até 2 segundos.
- [ ] AC5.2: Scanner de código de barras identifica o produto em até 5 segundos.
- [ ] AC5.3: Resultados incluem ao menos nome, preço, mercado e distância.
- [ ] AC5.4: Busca fuzzy encontra "lacte" quando o usuário digita errado "leite".

---

### FR6 — Filtros e Ordenação de Resultados (US3)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve permitir filtrar resultados por distância, faixa de preço, e ordenar por preço ou distância. |
| **Entrada** | Preferências do usuário (filtros e ordenação). |
| **Saída** | Lista de resultados filtrada e ordenada conforme seleção. |
| **Regras** | - Filtros disponíveis: distância máxima, faixa de preço, tipo de estabelecimento (supermercado, atacado, feira).<br>- Ordenação: por preço (menor→maior), por distância (mais perto→mais longe), por data de atualização (mais recente). |
| **Prioridade** | **P1** (pós-MVP) |

**Critérios de Aceitação:**
- [ ] AC6.1: O usuário pode combinar múltiplos filtros simultaneamente.
- [ ] AC6.2: A lista atualiza instantaneamente ao alterar filtros.
- [ ] AC6.3: Os filtros selecionados são visíveis e podem ser limpos com um toque.

---

### FR7 — Gráfico de Histórico de Preços (US4)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve exibir um gráfico de linha com a variação do preço de um produto ao longo do tempo, por mercado. |
| **Entrada** | Produto selecionado + período (7 dias, 30 dias, 90 dias, 1 ano). |
| **Saída** | Gráfico de linha com eixo X = tempo e eixo Y = preço, uma linha por mercado. |
| **Regras** | - O gráfico deve destacar o preço mínimo e máximo do período.<br>- Indicador visual de tendência (seta ↑↓→).<br>- Dados disponíveis a partir do primeiro registro do produto. |
| **Prioridade** | **P1** (pós-MVP) |

**Critérios de Aceitação:**
- [ ] AC7.1: O gráfico renderiza em até 2 segundos para períodos de até 1 ano.
- [ ] AC7.2: O usuário pode alternar entre períodos (7d, 30d, 90d, 1a).
- [ ] AC7.3: Preços mínimos e máximos são destacados visualmente.
- [ ] AC7.4: Uma seta de tendência é exibida ao lado do nome do produto.

---

### FR8 — Alerta de Preço (US4)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve permitir que o usuário configure alertas para quando o preço de um produto cair abaixo de um valor definido. |
| **Entrada** | Produto + preço-alvo + canal de notificação (push, e-mail). |
| **Saída** | Notificação enviada quando o preço atingir o valor-alvo. |
| **Regras** | - O usuário pode criar até 20 alertas ativos.<br>- Alertas podem ser pausados ou excluídos.<br>- Notificação push é o canal padrão; e-mail como opcional. |
| **Prioridade** | **P2** (futuro) |

**Critérios de Aceitação:**
- [ ] AC8.1: O usuário recebe push notification quando o preço atinge o valor-alvo.
- [ ] AC8.2: O alerta é desativado automaticamente após ser disparado (re-ativação manual).
- [ ] AC8.3: A lista de alertas ativos é visível em uma tela dedicada.

---

### FR9 — Upload de Encarte/Oferta de Jornal (US5)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve permitir que o usuário fotografe ou faça upload de encartes promocionais, extraindo produtos e preços via OCR. |
| **Entrada** | Imagem do encarte (foto ou screenshot) + nome do mercado (opcional, sugerido por geolocalização). |
| **Saída** | Lista de produtos com preços extraídos, associada ao mercado identificado. |
| **Regras** | - O OCR deve identificar padrões de encarte (preços em destaque, "de/por").<br>- O usuário confirma os itens antes de publicar.<br>- Encartes têm validade temporal (data de início e fim da promoção). |
| **Prioridade** | **P1** (pós-MVP) |

**Critérios de Aceitação:**
- [ ] AC9.1: Upload de encarte retorna itens extraídos em até 30 segundos.
- [ ] AC9.2: O sistema identifica preços "DE → POR" e registra o preço promocional.
- [ ] AC9.3: O usuário pode definir data de validade da promoção.
- [ ] AC9.4: Após confirmação, os dados aparecem no mapa e nas buscas.

---

### FR10 — Validação Comunitária de Preços (US5)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve permitir que outros usuários confirmem ou reportem preços enviados pela comunidade, aumentando a confiabilidade dos dados. |
| **Entrada** | Ação do usuário: "Confirmar preço" ou "Reportar preço incorreto" em um registro. |
| **Saída** | Score de confiabilidade atualizado para o registro de preço. |
| **Regras** | - 3 confirmações = preço verificado (selo verde).<br>- 2 reportes = preço em revisão (oculto até validação).<br>- Usuários que contribuem com validações ganham pontos/badges. |
| **Prioridade** | **P2** (futuro) |

**Critérios de Aceitação:**
- [ ] AC10.1: Após 3 confirmações, o preço exibe selo "Verificado pela comunidade".
- [ ] AC10.2: Após 2 reportes, o preço é ocultado e marcado como "Em revisão".
- [ ] AC10.3: O perfil do usuário exibe badge/pontuação por contribuições de validação.

---

### FR11 — Compartilhamento via Redes Sociais e Messaging (US6)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve gerar um card visual com o achado de preço (produto, preço, mercado, distância) e permitir compartilhamento via WhatsApp, Instagram Stories, Telegram, ou link público. |
| **Entrada** | Produto + preço + mercado selecionados pelo usuário. |
| **Saída** | Card visual (imagem) + link compartilhável + texto formatado para envio. |
| **Regras** | - Card gerado automaticamente com logo do PreçoPerto, nome do produto, preço em destaque, nome do mercado e distância.<br>- Link público abre uma página web com os detalhes (não requer app instalado).<br>- Compartilhamento via native share sheet (Android/iOS). |
| **Prioridade** | **P1** (pós-MVP) |

**Critérios de Aceitação:**
- [ ] AC11.1: O card é gerado em até 2 segundos.
- [ ] AC11.2: O link compartilhável funciona em qualquer navegador sem login.
- [ ] AC11.3: O card inclui QR code que leva ao produto no app.
- [ ] AC11.4: O native share sheet exibe ao menos WhatsApp, Instagram e opções de salvar imagem.

---

### FR12 — Gamificação e Ranking de Contribuidores (US6)

| Campo | Descrição |
|-------|-----------|
| **Descrição** | O sistema deve pontuar contribuições (uploads de NF, encartes, validações, compartilhamentos) e exibir um ranking de contribuidores. |
| **Entrada** | Ações do usuário no app (upload, validação, share). |
| **Saída** | Pontuação acumulada, badges desbloqueados e posição no ranking. |
| **Regras** | - Pontuação: NF = 10pts, Encarte = 15pts, Validação = 2pts, Share = 5pts.<br>- Badges: "Explorador" (1ª NF), "Caçador de Ofertas" (10 encartes), "Verificador" (50 validações).<br>- Ranking semanal e mensal por região (cidade/bairro). |
| **Prioridade** | **P2** (futuro) |

**Critérios de Aceitação:**
- [ ] AC12.1: A pontuação é atualizada em tempo real após cada ação.
- [ ] AC12.2: Badges são exibidos no perfil do usuário com data de conquista.
- [ ] AC12.3: O ranking exibe top 50 contribuidores da região do usuário.
- [ ] AC12.4: Notificação push parabeniza o usuário ao desbloquear um badge.

---

## Tabela de Prioridades

| ID | Requisito | User Story | Prioridade | Fase |
|----|-----------|------------|------------|------|
| FR1 | Upload e Processamento de NF | US1 | **P0** | MVP |
| FR2 | Extração de Dados via OCR | US1 | **P0** | MVP |
| FR3 | Exibição em Mapa Interativo | US2 | **P0** | MVP |
| FR4 | Geolocalização e Permissão | US2 | **P0** | MVP |
| FR5 | Busca por Nome/Código de Barras | US3 | **P0** | MVP |
| FR6 | Filtros e Ordenação | US3 | **P1** | Pós-MVP |
| FR7 | Gráfico de Histórico de Preços | US4 | **P1** | Pós-MVP |
| FR8 | Alerta de Preço | US4 | **P2** | Futuro |
| FR9 | Upload de Encarte/Oferta | US5 | **P1** | Pós-MVP |
| FR10 | Validação Comunitária | US5 | **P2** | Futuro |
| FR11 | Compartilhamento via Redes Sociais | US6 | **P1** | Pós-MVP |
| FR12 | Gamificação e Ranking | US6 | **P2** | Futuro |

### Resumo por Fase

| Fase | FRs | User Stories Cobertas |
|------|-----|----------------------|
| **MVP (P0)** | FR1, FR2, FR3, FR4, FR5 | US1, US2, US3 |
| **Pós-MVP (P1)** | FR6, FR7, FR9, FR11 | US3, US4, US5, US6 |
| **Futuro (P2)** | FR8, FR10, FR12 | US4, US5, US6 |

---

## Glossário

| Termo | Definição |
|-------|-----------|
| **NF** | Nota Fiscal — documento que registra uma compra com itens e preços. |
| **NF-e** | Nota Fiscal Eletrônica — versão digital da NF, disponível em XML. |
| **OCR** | Optical Character Recognition — tecnologia de extração de texto de imagens. |
| **Encarte** | Folheto promocional de supermercado com ofertas da semana. |
| **EAN-13** | Código de barras padrão para produtos de varejo (13 dígitos). |
| **Fuzzy search** | Busca tolerante a erros de digitação e variações ortográficas. |
| **Push notification** | Notificação enviada ao dispositivo mesmo com o app fechado. |
| **Native share sheet** | Menu nativo do sistema operacional para compartilhar conteúdo. |
| **P0 / P1 / P2** | Prioridade: P0 = essencial para MVP; P1 = importante pós-lançamento; P2 = desejável no futuro. |

---

*Documento gerado como parte da especificação funcional do projeto PreçoPerto.*

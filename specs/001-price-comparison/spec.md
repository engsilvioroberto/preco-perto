# Especificação Funcional — PreçoPerto MVP

## Visão Geral

PWA colaborativo de comparação de preços onde usuários escaneiam notas fiscais ou admin faz upload de jornais de ofertas. O sistema extrai preços (OCR), geolocaliza mercados, e mostra no mapa onde cada produto está mais barato perto do usuário, com cálculo de custo-benefício do deslocamento.

**Região inicial**: Ribeirão Preto - SP  
**População de dados**: Jornais de ofertas dos mercados (Fase 1) + notas fiscais de usuários (Fase 2)

---

## User Scenarios

### US1 — Buscar Preço de Produto (P1 - Core)

**Como** consumidor, **quero** buscar um produto e ver onde está mais barato perto de mim, **para** decidir qual mercado ir.

**Acceptance Scenarios:**

- **Given** estou na tela principal **When** digito "leite desnatado" na busca **Then** vejo lista de mercados ordenados por preço, com distância e economia vs mercado mais caro
- **Given** busquei um produto **When** clico em "Ver no mapa" **Then** vejo pin dos mercados com preço, ordenados visualmente por custo-benefício
- **Given** estou vendo um mercado no mapa **When** clico no pin **Then** vejo card com: nome do mercado, preço do produto, distância, tempo estimado de deslocamento, e economia vs alternativa mais cara
- **Given** vi que um mercado a 5km tem leite a R$3,50 (vs R$5,00 na esquina) **When** vejo o cálculo de custo-benefício **Then** o sistema mostra: "Economia: R$1,50 | Custo deslocamento: R$X (ônibus) ou R$Y (gasolina) | Vale a pena? Sim/Não"

### US2 — Escanear Nota Fiscal (P1 - Core)

**Como** usuário, **quero** escanear minha nota fiscal após uma compra, **para** contribuir com preços reais e atualizados.

**Acceptance Scenarios:**

- **Given** estou logado **When** clico em "Escanear nota" **Then** abre câmera com overlay guiando enquadramento da nota
- **Given** fotografei a nota fiscal **When** o sistema processa (OCR) **Then** em <10s vejo lista de produtos extraídos com preços, posso editar/corrigir antes de confirmar
- **Given** confirmei os produtos **When** envio **Then** preços são adicionados ao banco com timestamp, localização do mercado (extraída da nota ou GPS do usuário), e meu usuário como fonte
- **Given** a nota fiscal tem formato NFC-e padrão **When** faço upload **Then** sistema extrai >80% dos campos: CNPJ do mercado, produtos, quantidades, preços unitários, data/hora

### US3 — Upload de Jornal de Ofertas (P1 - Admin)

**Como** admin, **quero** fazer upload de jornais de ofertas dos mercados, **para** popular o sistema com dados verificados antes do lançamento.

**Acceptance Scenarios:**

- **Given** estou na área admin **When** faço upload de PDF/imagem de jornal de ofertas **Then** sistema processa OCR e extrai produtos + preços
- **Given** extraí dados do jornal **When** reviso **Then** posso associar cada produto ao mercado correto, editar preços, e confirmar importação
- **Given** importei jornal de ofertas **When** dados entram no sistema **Then** preços ficam disponíveis imediatamente na busca e mapa, com tag "Oferta válida até [data]"

### US4 — Cadastrar Mercado (P2)

**Como** admin, **quero** cadastrar novos mercados com endereço e coordenadas, **para** expandir a cobertura geográfica.

**Acceptance Scenarios:**

- **Given** estou na área admin **When** cadastro um mercado **Then** informo: nome, endereço (geocoding automático para lat/lng), horário de funcionamento, e categorias de produtos
- **Given** mercado está cadastrado **When** preços são associados a ele **Then** aparece automaticamente no mapa e nas buscas

### US5 — Cadastro e Login de Usuário (P2)

**Como** usuário, **quero** me cadastrar com email ou Google, **para** contribuir com notas fiscais e acompanhar minhas economias.

**Acceptance Scenarios:**

- **Given** abri o app pela primeira vez **When** clico em "Entrar" **Then** vejo opções: email/senha ou Google OAuth
- **Given** me cadastrei com email **When** confirmo o link de verificação **Then** posso escanear notas e ver histórico de contribuições
- **Given** estou logado **When** escaneio uma nota **Then** minha contribuição é creditada ao meu perfil (gamificação futura)

### US6 — Filtrar por Raio de Distância (P2)

**Como** usuário, **quero** filtrar resultados por raio de distância (ex: 1km, 5km, 10km), **para** ver apenas opções que posso alcançar a pé ou de carro.

**Acceptance Scenarios:**

- **Given** estou na tela de resultados **When** ajusto filtro de distância **Then** lista e mapa atualizam mostrando apenas mercados dentro do raio selecionado
- **Given** selecionei "1km (a pé)" **When** vejo resultados **Then** só aparecem mercados caminháveis, com tempo estimado a pé

---

## Edge Cases e Cenários de Erro

- **Nota fiscal ilegível**: sistema mostra mensagem "Não conseguimos ler sua nota. Tente melhor iluminação ou digite manualmente."
- **Produto não encontrado na busca**: mostra "Nenhum preço encontrado para [produto]. Seja o primeiro a escanear uma nota!"
- **Mercado sem coordenadas precisas**: sistema usa geocoding do endereço; se falhar, admin é notificado para ajustar manualmente
- **Preço desatualizado (>30 dias)**: mostra aviso "Preço de [data] — pode ter mudado" e ordena para baixo
- **Sem permissão de localização**: app funciona, mas mostra mensagem "Ative a localização para ver preços perto de você" e permite buscar por bairro/CEP manualmente
- **OCR falha parcialmente**: mostra produtos extraídos com confiança alta, marca outros como "Verificar" para usuário revisar

---

## Functional Requirements

### FR-001 — Scanner de Nota Fiscal
O sistema deve permitir escanear nota fiscal via câmera do dispositivo, processar via OCR, extrair produtos + preços + CNPJ do mercado + data/hora, e permitir revisão antes de confirmar.

### FR-002 — Upload de Jornal de Ofertas
Admin deve poder fazer upload de PDF/imagem de jornal de ofertas, sistema extrai produtos + preços via OCR, admin revisa e associa ao mercado correto.

### FR-003 — Busca de Produto
Usuário deve poder buscar produto por nome (autocomplete) e ver lista de mercados ordenados por preço, com distância e economia vs alternativa mais cara.

### FR-004 — Mapa Interativo
Sistema deve mostrar mapa com pins de mercados, cada pin mostrando preço do produto buscado. Clique no pin abre card com detalhes: nome, preço, distância, tempo de deslocamento, custo-benefício.

### FR-005 — Cálculo de Custo-Benefício
Sistema deve calcular: economia vs mercado mais caro, custo de deslocamento (a pé, carro, ônibus) baseado em distância, e mostrar recomendação "Vale a pena? Sim/Não".

### FR-006 — Geolocalização
Sistema deve usar GPS do dispositivo para determinar localização do usuário, ou permitir busca manual por bairro/CEP.

### FR-007 — Cadastro de Mercado
Admin deve poder cadastrar mercado com: nome, endereço (geocoding automático), horário de funcionamento, categorias.

### FR-008 — Autenticação
Usuário deve poder se cadastrar com email/senha ou Google OAuth. Sessão persistente (não perde login ao fechar app).

### FR-009 — Timestamp de Preços
Todo preço deve ter: data/hora de captura, origem (jornal de ofertas ou nota fiscal), e validade (ofertas têm data de expiração; notas fiscais são "preço recente").

### FR-010 — Filtro de Distância
Usuário deve poder filtrar resultados por raio: 1km, 5km, 10km, 20km, ou "todos".

### FR-011 — Modo Offline
App deve funcionar parcialmente offline: cache de última busca, dados essenciais disponíveis. Upload de nota fiscal requer conexão.

### FR-012 — Responsividade
PWA deve ser responsivo: mobile-first, mas funcional em tablet e desktop.

---

## Key Entities

- **Produto**: nome, categoria (laticínios, higiene, etc), unidade (kg, L, un)
- **Preço**: valor, produto_id, mercado_id, data_captura, origem (oferta/nota_fiscal), validade, usuario_id (se crowdsourced)
- **Mercado**: nome, endereco, latitude, longitude, horario_funcionamento, categorias
- **Usuario**: email, nome, data_cadastro, contribuicoes (contagem)
- **NotaFiscal**: imagem_url, usuario_id, data_captura, mercado_id (extraído ou confirmado), produtos_extraidos (JSON)
- **JornalOfertas**: imagem_url, admin_id, data_upload, data_validade, mercado_id, produtos_extraidos (JSON)

---

## Success Criteria

- **Usabilidade**: Usuário consegue comparar preço de um produto em <10 segundos
- **Precisão OCR**: >80% de acerto na extração de notas fiscais NFC-e
- **Cobertura inicial**: 100+ produtos, 5+ mercados em Ribeirão Preto
- **Performance**: PWA carrega em <3s em 4G
- **Engajamento**: 50+ usuários ativos no primeiro mês (meta)

---

## Assumptions

- Usuários têm smartphone com câmera funcional e conexão 4G/WiFi
- Jornais de ofertas de Ribeirão Preto estão disponíveis em formato digital (PDF/imagem)
- Nota fiscal brasileira (NFC-e) tem padrão visual consistente que permite OCR confiável
- Google Maps API ou OpenStreetMap podem ser usados para geocoding e mapa (decidir no Plan)
- Usuários estão dispostos a escanear notas fiscais em troca de informação de preços (validar com MVP)

---

## Clarifications Pendentes

- [NEEDS CLARIFICATION] Qual API de mapa usar? Google Maps (pago, mais preciso) vs OpenStreetMap + Leaflet (grátis, menos preciso para endereços brasileiros)?
- [NEEDS CLARIFICATION] Como calcular custo de deslocamento? Usar API de rotas (Google Directions) ou estimativa simples baseada em distância linear?
- [NEEDS CLARIFICATION] Qual serviço de OCR? Tesseract (self-hosted, grátis) vs Google Vision API (pago, mais preciso)?
- [NEEDS CLARIFICATION] Autenticação: apenas email/senha + Google, ou incluir Facebook/Apple Sign In?
- [NEEDS CLARIFICATION] Como lidar com produtos muito similares? Ex: "Leite desnatado 1L" vs "Leite desnatado 1 litro" vs "Leite desnatado Piracanjuba 1L" — normalização de nomes?

---

**Versão**: 1.0  
**Data**: 2026-07-03  
**Autor**: Hermione (com input de Silvio Roberto Filho)

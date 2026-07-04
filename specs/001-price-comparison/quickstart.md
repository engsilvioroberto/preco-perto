# Quickstart — PreçoPerto MVP

**Versão**: 1.0  
**Data**: 2026-07-04  
**Objetivo**: Guia de validação do MVP funcional

---

## Pré-requisitos

- [ ] Supabase configurado (URL + keys)
- [ ] Upstash Redis configurado (URL + token)
- [ ] Backend rodando localmente (`uvicorn app.main:app --reload`)
- [ ] Frontend rodando localmente (`npm run dev`)
- [ ] Dados populados (5+ mercados, 100+ produtos, 500+ preços)

---

## Cenário 1: Buscar Preço de Produto (US1)

### Passo 1: Abrir app no celular
1. Acessar `https://engsilvioroberto.github.io/preco-perto/` no celular
2. App pede permissão de localização → Permitir
3. Tela inicial mostra barra de busca

**Expected**: Tela inicial carregada, barra de busca visível

### Passo 2: Buscar produto
1. Digitar "leite" na barra de busca
2. Aguardar autocomplete (300ms debounce)
3. Lista de produtos aparece: "Leite Integral Piracanjuba 1L", "Leite Desnatado 1L", etc

**Expected**: 5+ produtos na lista, autocomplete funcionando

### Passo 3: Ver comparação de preços
1. Clicar em "Leite Integral Piracanjuba 1L"
2. Tela de comparação abre
3. Lista de mercados ordenados por preço:
   - Carrefour: R$4,99 (0,5km) — "Mais barato"
   - Extra: R$5,29 (1,2km)
   - Dalben: R$5,49 (2,0km)
   - Savegnago: R$5,99 (3,5km)
   - Paulistão: R$6,49 (4,0km) — "Mais caro"
4. Cada mercado mostra:
   - Nome e endereço
   - Preço
   - Distância
   - Custo-benefício: "Economia: R$1,50 | Vale a pena? Sim (a pé)"

**Expected**: Lista de 5+ mercados com preços, distâncias e custo-benefício

### Passo 4: Ver no mapa
1. Clicar em botão "Ver no mapa"
2. Mapa abre com pins dos mercados
3. Cada pin mostra preço do produto
4. Clicar em pin do Carrefour → popup abre:
   - Nome: Carrefour Ribeirão
   - Preço: R$4,99
   - Distância: 0,5km
   - Custo-benefício: "Vale a pena? Sim (a pé)"

**Expected**: Mapa com 5+ pins, popup abre ao clicar

---

## Cenário 2: Escanear Nota Fiscal (US2)

### Passo 1: Abrir scanner
1. Clicar em botão "Escanear nota" (ícone de câmera)
2. App pede permissão de câmera → Permitir
3. Câmera abre com overlay guiando enquadramento

**Expected**: Câmera abre, overlay visível

### Passo 2: Tirar foto da nota fiscal
1. Apontar câmera para nota fiscal real (ex: Carrefour)
2. Tirar foto (botão de captura)
3. Preview da imagem aparece
4. Barra de progresso: "Processando nota fiscal..." (OCR client-side)

**Expected**: Foto tirada, OCR processando (5-10s)

### Passo 3: Revisar produtos extraídos
1. Lista de produtos extraídos aparece:
   - Leite Integral Piracanjuba 1L × 2 = R$9,98 (confiança: 95%)
   - Arroz Tio João 5kg × 1 = R$25,90 (confiança: 92%)
   - Produto não identificado × 1 = R$15,00 (confiança: 45%) — "Verificar"
2. Produtos com baixa confiança (<80%) marcados como "Verificar"
3. Usuário pode editar: quantidade, preço, associar produto

**Expected**: Lista de produtos extraídos, alguns marcados como "Verificar"

### Passo 4: Confirmar e enviar
1. Revisar produtos, editar se necessário
2. Clicar em "Confirmar"
3. Mensagem: "Nota fiscal confirmada. 15 preços adicionados ao sistema."

**Expected**: Produtos confirmados, preços adicionados ao banco

---

## Cenário 3: Upload Jornal de Ofertas (US3 - Admin)

### Passo 1: Login como admin
1. Acessar tela de login
2. Login com credenciais de admin (email: admin@precoperto.com, senha: admin123)
3. Redireciona para painel admin

**Expected**: Login bem-sucedido, painel admin visível

### Passo 2: Upload jornal de ofertas
1. Clicar em "Upload jornal de ofertas"
2. Formulário:
   - Upload de imagem (PDF/imagem do jornal)
   - Seleção de mercado (dropdown: Carrefour, Extra, etc)
   - Data de início da validade
   - Data de fim da validade
3. Clicar em "Enviar"
4. Barra de progresso: "Processando jornal..."

**Expected**: Jornal enviado, OCR processando

### Passo 3: Revisar produtos extraídos
1. Lista de produtos extraídos aparece:
   - Leite Integral Piracanjuba 1L: R$4,99 (de R$5,99) — "Oferta"
   - Arroz Tio João 5kg: R$22,90
   - Feijão Camil Preto 1kg: R$8,49
2. Admin pode editar: preço, associar produto
3. Produtos com baixa confiança marcados como "Verificar"

**Expected**: Lista de produtos extraídos do jornal

### Passo 4: Confirmar e importar
1. Revisar produtos, editar se necessário
2. Clicar em "Confirmar"
3. Mensagem: "Jornal de ofertas confirmado. 50 preços adicionados ao sistema."
4. Preços ficam disponíveis imediatamente na busca

**Expected**: Produtos confirmados, preços adicionados com tag "Oferta válida até [data]"

---

## Cenário 4: Filtrar por Distância (US4)

### Passo 1: Buscar produto
1. Buscar "leite" na barra de busca
2. Clicar em "Leite Integral Piracanjuba 1L"
3. Lista de mercados aparece (5+ mercados)

**Expected**: Lista de mercados visível

### Passo 2: Aplicar filtro de distância
1. Clicar em botão "Filtros" (ícone de funil)
2. Modal abre com opções:
   - 1km (a pé)
   - 5km (carro)
   - 10km (carro)
   - 20km (carro)
   - Todos
3. Selecionar "5km (carro)"
4. Clicar em "Aplicar"
5. Lista atualiza: apenas mercados dentro de 5km (3 mercados)

**Expected**: Lista filtrada, apenas mercados dentro de 5km

### Passo 3: Ver no mapa com filtro
1. Clicar em "Ver no mapa"
2. Mapa abre com pins dos mercados dentro de 5km (3 pins)
3. Mercados fora do raio não aparecem

**Expected**: Mapa com 3 pins (dentro de 5km)

---

## Cenário 5: Modo Offline (US5)

### Passo 1: Buscar produto online
1. Buscar "leite" na barra de busca
2. Ver comparação de preços
3. App cacheia dados (Service Worker)

**Expected**: Dados cacheados

### Passo 2: Desativar internet
1. Ativar modo avião no celular
2. Abrir app novamente
3. Última busca ainda visível (cache)
4. Mensagem: "Você está offline. Mostrando dados em cache."

**Expected**: Última busca visível, mensagem de offline

### Passo 3: Tentar nova busca offline
1. Digitar "arroz" na barra de busca
2. Mensagem: "Você está offline. Conecte-se para buscar novos produtos."

**Expected**: Mensagem de erro amigável

---

## Cenário 6: PWA Installable

### Passo 1: Acessar app no celular
1. Abrir Chrome no celular
2. Acessar `https://engsilvioroberto.github.io/preco-perto/`
3. Banner aparece: "Adicionar à tela inicial?"
4. Clicar em "Adicionar"

**Expected**: Banner de instalação visível

### Passo 2: Verificar instalação
1. Voltar à tela inicial do celular
2. Ícone do PreçoPerto visível
3. Clicar no ícone
4. App abre em modo standalone (sem barra de navegador)

**Expected**: App instalável, abre em modo standalone

---

## Checklist de Validação

### Funcionalidades Core
- [ ] Busca de produto (autocomplete) funcionando
- [ ] Comparação de preços (lista) funcionando
- [ ] Mapa com pins funcionando
- [ ] Custo-benefício calculado corretamente
- [ ] Scanner de nota fiscal (câmera) funcionando
- [ ] OCR extraindo produtos (80%+ precisão)
- [ ] Upload de jornal de ofertas (admin) funcionando
- [ ] Filtro de distância funcionando

### PWA
- [ ] App instalável no celular
- [ ] Funciona offline (cache de última busca)
- [ ] Permissão de câmera solicitada corretamente
- [ ] Permissão de localização solicitada corretamente

### Performance
- [ ] App carrega em <3s em 4G
- [ ] Mapa carrega em <2s com 50 pins
- [ ] API response time <500ms (p95)

### Dados
- [ ] 5+ mercados de Ribeirão Preto cadastrados
- [ ] 100+ produtos cadastrados
- [ ] 500+ preços populados (de jornais de ofertas reais)

### Deploy
- [ ] Backend acessível em https://api.precoperto.app
- [ ] Frontend acessível em https://engsilvioroberto.github.io/preco-perto/
- [ ] HTTPS funcionando (GitHub Pages, Railway)

---

## Troubleshooting

### Problema: Câmera não abre
**Solução**: Verificar permissão de câmera no navegador. Em iOS Safari, requer HTTPS.

### Problema: Mapa não carrega
**Solução**: Verificar se Leaflet CSS está importado. Verificar se tiles do OpenStreetMap estão acessíveis.

### Problema: OCR não extrai produtos
**Solução**: Verificar qualidade da imagem (resolução, iluminação). Tentar imagem com melhor contraste.

### Problema: Geolocalização não funciona
**Solução**: Verificar permissão de localização no navegador. Em iOS, requer HTTPS. Fallback: input manual de CEP.

---

## Sucesso do MVP

**Critérios de sucesso**:
- [ ] Usuário consegue comparar preço de um produto em <10 segundos
- [ ] Scanner OCR funciona em >70% das notas fiscais testadas
- [ ] 100+ produtos com preços mapeados em Ribeirão Preto
- [ ] 5+ mercados cobertos
- [ ] Cálculo de deslocamento mostra economia real vs custo
- [ ] PWA instalável e funcional no celular

---

**Aprovado por**: Hermione (autonomia delegada por Silvio)

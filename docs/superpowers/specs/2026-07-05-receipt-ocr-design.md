# Design: OCR real para scanner de nota fiscal

Data: 2026-07-05

## Contexto

O scanner de nota fiscal (`frontend/src/pages/Scan.tsx`, `ReceiptScanner.tsx`, `backend/app/api/routes/receipts.py`) hoje é só UI de scaffolding:

- A câmera funciona (getUserMedia + canvas), mas a imagem capturada nunca é usada.
- `Scan.tsx` simula o resultado com um `setTimeout` e dados hardcoded.
- `tesseract.js` está no `package.json` mas nunca é importado em nenhum lugar do frontend.
- O endpoint `POST /api/v1/receipts/` é um placeholder: não usa o `db` injetado, não salva nada.

Objetivo deste design: implementar o pipeline real de ponta a ponta — captura → OCR → extração de itens/preços → revisão do usuário → persistência no backend, criando `Product`/`Price` reais a partir da nota escaneada.

## Restrições e decisões já tomadas

- **Não há automação de browser disponível** para quem for verificar este trabalho — câmera e Tesseract.js em runtime real só podem ser testados manualmente pelo usuário no navegador dele.
- **Não há tela de login funcional** no frontend hoje (`Profile.tsx` é placeholder). Para não expandir escopo para "implementar auth", os receipts serão associados a um usuário de teste fixo (seed `joao@gmail.com`), documentado como débito técnico.
- Notas fiscais brasileiras variam muito de formato — o parser é heurístico e "melhor esforço", não uma extração garantidamente correta. O usuário sempre revisa/edita os itens antes de confirmar o envio.
- `Market.cnpj` e `Receipt.cnpj_extracted`/`Receipt.market_id` já existem no schema atual — o design usa o CNPJ extraído da nota para tentar casar automaticamente com um mercado cadastrado.

## Fluxo de dados

```
[Câmera ao vivo OU upload de arquivo de imagem]
        ↓ (imagem)
[Tesseract.js roda no browser, idioma "por"]
        ↓ (texto bruto OCR)
[Parser heurístico extrai: CNPJ, itens (nome+preço), total, data]
        ↓
[Frontend chama GET /api/v1/markets/by-cnpj?cnpj=...]
   ├─ 200 (achou) → usa esse market_id automaticamente
   └─ 404 (não achou) → mostra dropdown de mercados próximos
      (via getNearbyMarkets + geolocalização) para escolha manual
        ↓
[Tela de revisão: lista de itens editável — nome, preço, checkbox incluir/excluir]
        ↓ (usuário clica "Confirmar e Enviar")
[POST /api/v1/receipts/ multipart: imagem + itens finais (JSON) + market_id + lat/lng]
        ↓
[Backend:
   1. Salva imagem em backend/uploads/receipts/{uuid}.jpg
   2. Cria Receipt (user_id = usuário de teste fixo, market_id, image_url,
      ocr_text, cnpj_extracted, status="completed")
   3. Para cada item confirmado:
      - fuzzy_match (product_normalization, threshold >= 85%) contra Products existentes
      - se achou: reusa o Product
      - se não achou: cria Product novo com o nome normalizado
      - cria Price (product_id, market_id, price, source="receipt_scan",
        created_by=user_id, captured_at=now)
]
```

## Frontend

### `ReceiptScanner.tsx` (modificado)
- Adiciona `<input type="file" accept="image/*" capture="environment">` como alternativa à câmera ao vivo — facilita testes (não depende de nota física na frente da webcam) e é o padrão real de PWA mobile (usuário pode escolher foto já tirada).
- `onCapture` passa a receber a imagem capturada como argumento: `onCapture(imageDataUrl: string)`. Hoje a prop não recebe nada, é o bug raiz que impede qualquer processamento real.

### `services/ocr.ts` (novo)
- `extractText(imageDataUrl: string): Promise<string>` — wrapper do Tesseract.js, idioma `por`. Baixa o pacote de treinamento na primeira execução (~2MB, cacheado pelo browser depois).
- `parseReceiptText(text: string): ParsedReceipt` — parser heurístico puro (sem I/O), portanto testável isoladamente:
  - `cnpj`: regex `\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}`
  - `total`: primeira linha contendo "TOTAL" (case-insensitive) seguida de um valor `\d+,\d{2}`
  - `items`: para cada linha, se ela termina em um padrão de preço (`R$ 12,34` ou `12,34`), o valor final vira `price` e o texto restante (limpando códigos numéricos e unidades como "UN", "KG", "X 2" nas pontas) vira `description`. Linhas sem esse padrão são ignoradas.
  - `date`: regex `\d{2}/\d{2}/\d{4}` opcional

### `services/api.ts` (extensão)
- `lookupMarketByCnpj(cnpj: string): Promise<Market | null>` — chama `GET /api/v1/markets/by-cnpj`, retorna `null` em 404 em vez de propagar erro.
- `uploadReceipt(payload): Promise<ReceiptUploadResponse>` — `multipart/form-data` com imagem, `items` (JSON stringificado), `market_id`, `latitude`, `longitude`.

### `Scan.tsx` (reescrito)
Máquina de estados: `idle → capturing → ocr_processing → resolving_market → reviewing → submitting → done | error`.

- `capturing`: `ReceiptScanner` captura a imagem (câmera ou upload).
- `ocr_processing`: chama `extractText` + `parseReceiptText`, mostra spinner com texto "Lendo nota fiscal...".
- `resolving_market`: chama `lookupMarketByCnpj`; se `null`, busca mercados próximos via geolocalização e mostra dropdown.
- `reviewing`: lista editável dos itens parseados (nome, preço, checkbox incluir), com o mercado resolvido/selecionado visível.
- `submitting`: chama `uploadReceipt` com os itens confirmados.
- `done`: mostra resumo do que foi salvo (quantos produtos/preços criados).
- `error`: qualquer falha em OCR, lookup ou upload cai aqui com mensagem clara e opção de tentar de novo.

### Tipos novos (`types/index.ts`)
- `ParsedReceiptItem { description: string; price: number; include: boolean }`
- `ParsedReceipt { cnpj: string | null; total: number | null; date: string | null; items: ParsedReceiptItem[] }`
- `ReceiptUploadResponse { receipt_id: string; products_created: number; prices_created: number }`

## Backend

### `schemas/receipt.py` (novo)
- `ReceiptItemIn { description: str; price: Decimal }`
- `ReceiptUploadResponse { receipt_id: str; products_created: int; prices_created: int }`

### `api/routes/markets.py` (extensão)
- `GET /api/v1/markets/by-cnpj?cnpj=...` — normaliza o CNPJ (remove pontuação) antes de comparar, retorna `MarketResponse` ou 404.

### `api/routes/receipts.py` (reescrito)
`POST /api/v1/receipts/`:
1. Recebe `image: UploadFile`, `market_id: str (Form)`, `items: str (Form, JSON)`, `cnpj: Optional[str] (Form)`, `latitude/longitude: Optional[float] (Form)`.
2. Valida que `market_id` existe.
3. Salva a imagem em `backend/uploads/receipts/{uuid4}.jpg` (pasta criada se não existir, adicionada ao `.gitignore`).
4. Cria `Receipt` com `status="completed"`.
5. Para cada item em `items`: fuzzy-match contra `Product.normalized_name` existentes usando `fuzzy_match` (threshold 85%) — se achar, reusa; senão cria `Product` novo via `normalize_product`. Cria `Price(source="receipt_scan", created_by=<user de teste>, captured_at=now())`.
6. Usuário de teste: constante `TEST_USER_EMAIL = "joao@gmail.com"`, resolvido para `user_id` via query no início do handler.
7. Retorna `ReceiptUploadResponse`.

### `main.py`
- Monta `/uploads` como diretório estático (`StaticFiles`) para os arquivos salvos em `backend/uploads/`.

## Limitações conhecidas (aceitas para este MVP)

- Parser heurístico não cobre todos os formatos de nota fiscal brasileira — erros de extração são esperados e mitigados pela tela de revisão manual.
- Sem autenticação real: todo receipt é atribuído ao usuário seed fixo.
- Imagem salva em disco local (não Supabase Storage) — adequado para SQLite/dev, não para produção.
- Fuzzy-match com threshold fixo (85%) pode criar produtos duplicados ligeiramente diferentes (ex.: "Leite Integral 1L" vindo de OCR ruim) — aceitável para teste inicial.

## Estratégia de verificação

- **Parser** (`parseReceiptText`): testado isoladamente via Node com textos de exemplo simulando saída real do Tesseract para cupons fiscais brasileiros (sem precisar de browser).
- **Backend**: endpoints novos (`/markets/by-cnpj`, `/receipts/`) testados via curl diretamente, confirmando criação correta de `Product`/`Price`/`Receipt` no SQLite.
- **Câmera + Tesseract.js fim a fim**: só pode ser validado manualmente pelo usuário no navegador real (câmera exige hardware e permissão real). Passo a passo de teste será fornecido após a implementação, incluindo o caminho de upload de arquivo (mais fácil de reproduzir que apontar a webcam para uma nota física).

# Tasks — PreçoPerto MVP

> Decomposição executável do MVP em 5 fases.
> **Legenda de responsáveis**: `dev` (backend/frontend), `content` (dados/jornais/seed), `ops` (infra/deploy/monitor).
> **Estimativa total do MVP**: ~38 dias úteis (≈ 7,5 semanas).

---

## Fase 1 — Fundação (repo, specs, constitution, plan)

**Objetivo**: Basear o projeto em artefatos de decisão aprovados e infraestrutura mínima operacional.
**Responsável principal**: `ops` + `dev`
**Depende de**: nada (kickoff)
**Estimativa**: 4 dias

### Tasks

- [x] **1.1** Criar repositório `preco-perto` com estrutura `backend/`, `frontend/`, `specs/`, `docs/`, `scripts/`. *(ops)*
- [x] **1.2** Escrever `constitution.md` (princípios, non-negotiables, governança). *(dev + PO)*
- [x] **1.3** Escrever `spec.md` (user scenarios, FRs, edge cases, entidades). *(dev)*
- [x] **1.4** Escrever `plan.md` (arquitetura SQLite-first, stack FastAPI + React + Vite). *(dev)*
- [ ] **1.5** Resolver clarifications pendentes no `spec.md` (mapa, OCR, auth, normalização). *(dev + PO)*
- [ ] **1.6** Definir `data-model.md` final (Produto, Preço, Mercado, Usuário, NotaFiscal, JornalOfertas). *(dev)*
- [ ] **1.7** Configurar CI básico (lint + typecheck) no `.github/workflows/`. *(ops)*
- [ ] **1.8** Documentar `CONTRIBUTING.md` e `README.md` com quickstart. *(ops)*

**Saída da fase**: specs aprovados, schema decidido, repo pronto para desenvolvimento.

---

## Fase 2 — Backend core (API de produtos, OCR endpoint, SQLite schema)

**Objetivo**: API funcional com persistência, seed de dados e endpoint de OCR preparado.
**Responsável principal**: `dev`
**Depende de**: Fase 1 (1.5, 1.6 concluídos)
**Estimativa**: 8 dias

### Tasks

- [ ] **2.1** Inicializar Alembic no backend e configurar `db_session` (SQLite). *(dev)*
- [ ] **2.2** Implementar modelos SQLAlchemy: `Product`, `Market`, `Price`, `Invoice`, `OfferPaper`, `User`. *(dev)*
- [ ] **2.3** Rodar `alembic init` + primeira migration com todas as tabelas. *(dev)*
- [ ] **2.4** CRUD de `Product` e `Market` no FastAPI (GET/POST/PUT). *(dev)*
- [ ] **2.5** CRUD de `Price` com vínculo produto↔mercado + timestamp + origem. *(dev)*
- [ ] **2.6** Endpoint `POST /ocr/invoice` (recebe imagem, devolve JSON bruto — Tesseract server-side ou stub). *(dev)*
- [ ] **2.7** Endpoint `POST /ocr/offer-paper` (mesmo padrão para jornais de oferta). *(dev)*
- [ ] **2.8** Serviço de Fuzzy Matching (`rapidfuzz`) para normalização de nomes de produtos. *(dev)*
- [ ] **2.9** Criar `scripts/seed_db.py` com 100+ produtos e 5+ mercados de Ribeirão Preto. *(content + dev)*
- [ ] **2.10** Testes unitários dos endpoints críticos (pytest + httpx). *(dev)*

**Saída da fase**: API rodando localmente, seed populando DB, OCR endpoint pronto para plugar provider.

---

## Fase 3 — Frontend core (mapa, busca, upload de NF)

**Objetivo**: PWA React funcional com as 3 telas principais (busca, mapa, scanner).
**Responsável principal**: `dev`
**Depende de**: Fase 2 (2.4, 2.5, 2.6 prontos)
**Estimativa**: 9 dias

### Tasks

- [ ] **3.1** Scaffold do PWA (Vite + React + TS) com manifest, service worker e ícones. *(dev)*
- [ ] **3.2** Configurar Leaflet (`react-leaflet`) + tiles OpenStreetMap. *(dev)*
- [ ] **3.3** Tela de busca com autocomplete (debounce + fuzzy no backend). *(dev)*
- [ ] **3.4** Lista de resultados: mercados ordenados por preço, distância e economia vs. mais caro. *(dev)*
- [ ] **3.5** Mapa com pins de mercados; clique abre card (nome, preço, distância, custo-benefício). *(dev)*
- [ ] **3.6** Componente de câmera com overlay de enquadramento da NF. *(dev)*
- [ ] **3.7** Integração do upload com endpoint `/ocr/invoice` + tela de revisão antes de confirmar. *(dev)*
- [ ] **3.8** Área admin (upload de jornal de oferta + revisão + associação ao mercado). *(dev)*
- [ ] **3.9** Design system mobile-first (tokens, componentes base, acessibilidade WCAG 2.1 AA). *(dev)*
- [ ] **3.10** Testes E2E leves (Playwright) para busca → mapa → scanner. *(dev)*

**Saída da fase**: PWA navegável end-to-end com dados do seed.

---

## Fase 4 — Integração (OCR real, geolocalização, jornais de oferta)

**Objetivo**: Trocar stubs por providers reais e validar com dados de verdade.
**Responsável principal**: `dev` + `content`
**Depende de**: Fase 3 (3.6, 3.7 prontos)
**Estimativa**: 9 dias

### Tasks

- [ ] **4.1** Escolher e integrar provider de OCR (Tesseract self-hosted vs. Google Vision) — decisão do `spec.md`. *(dev)*
- [ ] **4.2** Pipeline de parsing de NFC-e: extrair CNPJ, produtos, quantidades, preços, data/hora. *(dev)*
- [ ] **4.3** Pipeline de parsing de jornal de oferta: detectar blocos produto/preço/validade. *(dev + content)*
- [ ] **4.4** Integrar geocoding (Nominatim/OSM ou Google) para endereços de mercados. *(dev)*
- [ ] **4.5** Cálculo de custo-benefício: distância (OSRM) × custo modal (a pé/carro/ônibus). *(dev)*
- [ ] **4.6** Geolocalização do usuário (browser Geolocation API) + fallback por bairro/CEP. *(dev)*
- [ ] **4.7** Ingestão real de 2–3 jornais de oferta de Ribeirão Preto. *(content)*
- [ ] **4.8** Validação de precisão OCR em ≥10 notas fiscais reais (meta >80%). *(dev + content)*
- [ ] **4.9** Filtro de raio de distância (1/5/10/20 km) no frontend. *(dev)*
- [ ] **4.10** Modo offline parcial (cache de última busca via service worker). *(dev)*

**Saída da fase**: sistema funcional com dados reais, OCR validado, cálculo de deslocamento operante.

---

## Fase 5 — MVP Launch (Ribeirão Preto, onboarding, share)

**Objetivo**: Colocar o MVP em produção, com usuários reais e loop de feedback.
**Responsável principal**: `ops` + `content` + `dev`
**Depende de**: Fase 4 (4.7, 4.8 validados)
**Estimativa**: 8 dias

### Tasks

- [ ] **5.1** Migrar SQLite → Supabase (PostgreSQL) via alteração de `DATABASE_URL` + revisão de migrations. *(ops + dev)*
- [ ] **5.2** Deploy do backend (Railway / Fly.io / Render) com healthcheck e variáveis de ambiente. *(ops)*
- [ ] **5.3** Deploy do frontend (Vercel / Netlify) com PWA + custom domain `precoperto.com.br`. *(ops)*
- [ ] **5.4** Configurar auth (email/senha + Google OAuth) via Supabase Auth. *(dev)*
- [ ] **5.5** Tela de onboarding (3 telas explicando valor do app) + primeiro acesso. *(dev)*
- [ ] **5.6** Fluxo de compartilhamento ("Compartilhar preço encontrado" via Web Share API). *(dev)*
- [ ] **5.7** Painel básico de métricas (usuários ativos, notas escaneadas, produtos mapeados). *(ops)*
- [ ] **5.8** Teste de carga (k6 ou similar) para validar <3s em 4G no cold start. *(ops)*
- [ ] **5.9** LGPD: termos de uso, política de privacidade, tela de consentimento. *(content + dev)*
- [ ] **5.10** Soft-launch em Ribeirão Preto: 50+ usuários beta, canal de feedback (WhatsApp/Telegram). *(content + ops)*
- [ ] **5.11** Post-mortem do MVP e backlog de V2. *(todos)*

**Saída da fase**: MVP no ar, usuários reais usando, feedback loop ativo.

---

## Resumo de estimativas

| Fase | Descrição | Dias | Responsável |
|------|-----------|:----:|-------------|
| 1 | Fundação | 4 | ops + dev |
| 2 | Backend core | 8 | dev |
| 3 | Frontend core | 9 | dev |
| 4 | Integração | 9 | dev + content |
| 5 | MVP Launch | 8 | ops + content + dev |
| **Total** | | **38 dias** | |

> **Buffer recomendado**: +20% para imprevistos → **~46 dias úteis (≈ 9 semanas)**.

---

## Riscos e dependências críticas

- **Dependência externa**: decisão de OCR (Tesseract vs. Google Vision) impacta custo e precisão — resolver na Fase 1 (1.5).
- **Conteúdo**: ingestão de jornais de oferta (4.7) depende de acesso aos materiais dos mercados de Ribeirão Preto — `content` deve iniciar contato na Fase 2.
- **LGPD**: termos e política (5.9) são bloqueantes para o launch — iniciar redação na Fase 3.
- **Geocoding brasileiro**: precisão do OSM em Ribeirão Preto precisa ser validada cedo (spike na Fase 2).

---

**Versão**: 1.0
**Data**: 2026-07-09
**Autor**: Hermes (Ops Agent)

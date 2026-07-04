# Plano de Implementação — PreçoPerto MVP

**Versão**: 1.0  
**Data**: 2026-07-04  
**Status**: ✅ Aprovado

---

## Summary

PWA colaborativo de comparação de preços onde usuários escaneiam notas fiscais ou admin faz upload de jornais de ofertas. Sistema extrai preços via OCR, geolocaliza mercados, e mostra no mapa onde cada produto está mais barato, com cálculo de custo-benefício do deslocamento.

**Região inicial**: Ribeirão Preto - SP  
**Stack**: React + TypeScript (PWA) + Python FastAPI + Supabase + Redis  
**Deploy**: GitHub Pages (frontend) + Railway/Render (backend)

---

## Technical Context

### Linguagens e Frameworks
- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy + Alembic (migrations)
- **Mapa**: Leaflet + react-leaflet
- **OCR**: Tesseract.js (client-side) + pytesseract (server-side fallback)

### Storage
- **Database**: Supabase (PostgreSQL 15 + PostGIS)
- **Cache**: Upstash Redis (free tier)
- **File Storage**: Supabase Storage (imagens de notas fiscais)

### External Services
- **Geocoding**: Nominatim (OpenStreetMap, grátis)
- **Mapa**: OpenStreetMap + Leaflet
- **OCR**: Tesseract (self-hosted ou Tesseract.js)

### Testing
- **Backend**: pytest + httpx (async tests)
- **Frontend**: Vitest + React Testing Library
- **Integration**: Testes com Supabase real (free tier)

### Platform
- **Frontend**: PWA (Progressive Web App)
- **Mobile-first**: Responsivo, touch-friendly
- **Offline**: Service Worker + cache de dados essenciais
- **HTTPS**: Obrigatório (GitHub Pages, Railway)

### Performance Targets
- **Load time**: <3s em 4G
- **Bundle size**: <500KB (gzipped)
- **API response**: <500ms (p95)

---

## Constitution Check

### Artigo I — Mobile-First, PWA-First ✅
- PWA é plataforma primária
- Design mobile-first (max-width: 480px primeiro)
- Service Worker para offline

### Artigo II — Simplicidade Radical ✅
- Fluxos em 3 passos máx (buscar → ver resultados → ver mapa)
- Sem tutoriais, UI auto-explicativa
- OCR com fallback manual (edição)

### Artigo III — Dados Confiáveis ✅
- Todo preço tem timestamp + origem (oferta/nota fiscal)
- Usuário revisa OCR antes de confirmar
- Preços >30 dias marcados como "desatualizados"

### Artigo IV — Geolocalização como Core ✅
- Mapa é tela principal (não secundária)
- GPS do dispositivo + fallback manual (CEP)
- Todo preço vinculado a mercado com lat/lng

### Artigo V — Custo-Benefício Transparente ✅
- Cálculo explícito: economia vs custo deslocamento
- Recomendação "Vale a pena? Sim/Não"
- Sem manipulação, dados brutos visíveis

### Artigo VI — Privacidade e LGPD ✅
- Notas fiscais anonimizadas após extração
- Usuário controla o que compartilha
- Política de privacidade clara

### Artigo VII — População Inicial via Jornais ✅
- 100+ produtos de 5+ mercados de Ribeirão Preto
- Dados de jornais de ofertas reais (extraídos via OCR)
- Resolve chicken-and-egg problem

### Artigo VIII — Open Source ✅
- Repo público no GitHub
- Licença MIT

### Artigo IX — Performance e Acessibilidade ✅
- PWA <3s em 4G
- WCAG 2.1 AA (contraste, alt text, keyboard nav)
- Offline-first (cache de última busca)

---

## Project Structure

```
preco-perto/
├── .specify/
│   └── memory/
│       └── constitution.md
├── specs/
│   └── 001-price-comparison/
│       ├── spec.md
│       ├── clarifications.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── contracts/
│       │   └── api.md
│       ├── quickstart.md
│       └── tasks.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── products.py
│   │   │   │   ├── markets.py
│   │   │   │   ├── prices.py
│   │   │   │   ├── receipts.py
│   │   │   │   └── auth.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── product.py
│   │   │   ├── market.py
│   │   │   ├── price.py
│   │   │   ├── user.py
│   │   │   └── receipt.py
│   │   ├── schemas/
│   │   │   ├── product.py
│   │   │   ├── market.py
│   │   │   ├── price.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── ocr.py
│   │   │   ├── geocoding.py
│   │   │   ├── price_comparison.py
│   │   │   └── product_normalization.py
│   │   └── utils/
│   │       ├── cache.py
│   │       └── distance.py
│   ├── tests/
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── conftest.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductSearch.tsx
│   │   │   ├── PriceList.tsx
│   │   │   ├── PriceMap.tsx
│   │   │   ├── ReceiptScanner.tsx
│   │   │   └── MarketCard.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Search.tsx
│   │   │   ├── Map.tsx
│   │   │   ├── Scan.tsx
│   │   │   └── Profile.tsx
│   │   ├── hooks/
│   │   │   ├── useGeolocation.ts
│   │   │   ├── useProducts.ts
│   │   │   └── usePrices.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── ocr.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   ├── manifest.json
│   │   └── sw.js
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
├── scripts/
│   ├── seed_data.py
│   └── extract_receipts.py
└── README.md
```

---

## Complexity Tracking

### Violações da Constituição (justificadas)

**Nenhuma violação identificada.** Todas as decisões técnicas respeitam os 9 artigos.

### Trade-offs Aceitos

1. **OCR client-side (Tesseract.js)**: Menos preciso que server-side, mas reduz latência e custo de servidor. Aceitável para MVP.

2. **Estimativa linear de deslocamento**: Não considera trânsito/rotas reais, mas suficiente para MVP e evita custo de Google Directions API.

3. **Autenticação simples (email/senha)**: Sem OAuth, menos conveniente para usuário, mas mais simples de implementar e manter.

4. **Fuzzy matching básico**: Pode agrupar produtos diferentes, mas usuário pode refinar busca com nome completo.

---

## Risk Mitigation

### Risco 1: OCR com baixa precisão
**Mitigação**: Permitir edição manual antes de confirmar. Fallback: upload de imagem + extração server-side com pytesseract (mais preciso).

### Risco 2: Geocoding impreciso (Nominatim)
**Mitigação**: Admin pode ajustar lat/lng manualmente no cadastro de mercado. Cache de geocoding no Redis.

### Risco 3: Performance do mapa com muitos pins
**Mitigação**: Clusterização (Leaflet.markercluster). Limitar pins visíveis por zoom level.

### Risco 4: Supabase free tier limitado
**Mitigação**: 500MB DB + 1GB storage suficiente para MVP. Monitorar uso, migrar para paid tier se necessário.

---

## Deployment Strategy

### Fase 1: MVP Local
- Backend: `uvicorn` local
- Frontend: `vite dev` local
- Supabase: cloud (free tier)
- Redis: Upstash (free tier)

### Fase 2: Deploy Produção
- Frontend: GitHub Pages (grátis, estático)
- Backend: Railway ou Render (free tier, auto-deploy via GitHub)
- DB: Supabase (já em cloud)
- Redis: Upstash (já em cloud)

### Fase 3: Testes no Celular
- GitHub Pages: HTTPS automático, acessível via URL pública
- Backend: HTTPS via Railway/Render
- PWA: instalável no celular (manifest.json + service worker)
- Câmera: permissão via `navigator.mediaDevices.getUserMedia()`

---

## Success Criteria (técnico)

- [ ] Backend: 100% dos endpoints testados (pytest)
- [ ] Frontend: PWA instalável no celular
- [ ] OCR: >70% precisão em 10 notas fiscais testadas
- [ ] Mapa: carrega em <2s com 50 pins
- [ ] API: response time <500ms (p95)
- [ ] Deploy: GitHub Pages + Railway funcionando
- [ ] Dados: 100+ produtos, 5+ mercados populados

---

**Aprovado por**: Hermione (autonomia delegada por Silvio)

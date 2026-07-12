# Projeto PreçoPerto

> Comparador de preços colaborativo para Ribeirão Preto — porque o melhor preço é o preço que a gente descobre junto.

---

## 📌 Visão Geral

**PreçoPerto** é um PWA (Progressive Web App) colaborativo de comparação de preços onde usuários escaneiam notas fiscais e admins fazem upload de jornais de ofertas. O sistema extrai preços via OCR, geolocaliza mercados e mostra no mapa onde cada produto está mais barato perto do usuário, com cálculo de custo-benefício do deslocamento.

**Região inicial**: Ribeirão Preto - SP

**Princípios fundamentais** (ver [CONSTITUTION.md](./CONSTITUTION.md)):
- Dados abertos — todo preço escaneado é público
- Gratuito sempre — nunca cobra do usuário final
- Privacidade — localização por bairro, nunca endereço exato
- Build in Public — todo desenvolvimento documentado

---

## 🏗️ Stack e Arquitetura

### Backend
| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy (async) |
| Validação | Pydantic v2 |
| Migrations | Alembic |
| DB (MVP) | SQLite |
| DB (produção) | Supabase (PostgreSQL) |
| OCR | Tesseract / Google Vision (a decidir) |
| Fuzzy matching | rapidfuzz |

### Frontend
| Componente | Tecnologia |
|------------|------------|
| Framework | React 18 |
| Linguagem | TypeScript |
| Build tool | Vite |
| Mapas | Leaflet (react-leaflet) + OpenStreetMap |
| PWA | Service Worker + manifest |
| Auth | Supabase Auth (email + Google OAuth) |

### Arquitetura (SQLite-First)
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Frontend      │────▶│   Backend API    │────▶│  SQLite DB  │
│   React + Vite  │◀────│   FastAPI        │◀────│  (MVP)      │
│   (PWA)         │     │                  │     └─────────────┘
└─────────────────┘     │  - OCR service   │
                        │  - Fuzzy match   │     ┌─────────────┐
                        │  - Geocoding     │────▶│  Supabase   │
                        │  - Cost calc     │     │  (produção) │
                        └──────────────────┘     └─────────────┘
```

### Estrutura do Repositório
```
preco-perto/
├── backend/         # FastAPI backend (código principal)
├── frontend/        # React + Vite frontend (PWA)
├── server/          # Configuração de deploy do servidor
├── web/             # Alternativa frontend
├── specs/           # SDD specs (spec, plan, tasks, data-model)
│   └── 001-price-comparison/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── data-model.md
│       ├── clarifications.md
│       └── quickstart.md
├── docs/            # Documentação do projeto
│   ├── PROJECT.md
│   ├── CONSTITUTION.md
│   ├── TASKS.md
│   └── SPEC_DRIVEN_DEVELOPMENT.md
├── scripts/         # Scripts utilitários (seed, migrations)
└── .github/         # CI/CD workflows
```

---

## 📐 Metodologia: Spec-Driven Development (SDD)

Este projeto segue **Spec-Driven Development** — toda funcionalidade é especificada antes da implementação.

### Princípios SDD
1. **Spec First**: Toda funcionalidade começa com uma especificação
2. **Implementação Segue Spec**: O código implementa exatamente o que a spec define
3. **Spec é Fonte da Verdade**: Em caso de dúvida, a spec prevalece
4. **Evolução via Spec**: Mudanças começam atualizando a spec

### Workflow
```
1. Escrever/atualizar spec → specs/001-price-comparison/spec.md
2. Criar plan de implementação → specs/001-price-comparison/plan.md
3. Decompor em tasks → specs/001-price-comparison/tasks.md
4. Implementar seguindo a spec
5. Validar que implementação atende spec
```

### Artefatos SDD
| Artefato | Descrição | Link |
|----------|-----------|------|
| Spec | User scenarios, FRs, edge cases, entidades | [spec.md](../specs/001-price-comparison/spec.md) |
| Plan | Arquitetura, stack, fases | [plan.md](../specs/001-price-comparison/plan.md) |
| Tasks | Decomposição executável em 5 fases | [tasks.md](./TASKS.md) |
| Data Model | Entidades e relacionamentos | [data-model.md](../specs/001-price-comparison/data-model.md) |
| Constitution | Princípios não-negociáveis | [CONSTITUTION.md](./CONSTITUTION.md) |

---

## 📊 Status Atual do Projeto

### Fase 1 — Fundação ✅ (em andamento)
- [x] Repositório criado com estrutura
- [x] Constitution escrita (9 artigos)
- [x] Spec funcional v1.0
- [x] Plan de arquitetura (SQLite-first)
- [x] Tasks decompostas (5 fases, ~38 dias)
- [ ] Clarifications pendentes resolvidas
- [ ] Data model finalizado
- [ ] CI básico configurado

### Próximos passos
- Fase 2: Backend core (API, OCR endpoint, SQLite schema)
- Fase 3: Frontend core (mapa, busca, scanner)
- Fase 4: Integração (OCR real, geolocalização)
- Fase 5: MVP Launch (deploy, usuários beta)

### Estimativa Total
| Fase | Dias | Responsável |
|------|:----:|-------------|
| 1. Fundação | 4 | ops + dev |
| 2. Backend core | 8 | dev |
| 3. Frontend core | 9 | dev |
| 4. Integração | 9 | dev + content |
| 5. MVP Launch | 8 | ops + content + dev |
| **Total** | **38 dias** | +20% buffer = ~46 dias |

---

## 🔗 Links Úteis

| Recurso | URL |
|---------|-----|
| Repositório GitHub | https://github.com/engsilvioroberto/preco-perto |
| Metodologia SDD | https://github.com/github/spec-kit (inspiração) |
| FastAPI Docs | https://fastapi.tiangolo.com |
| React + Vite | https://vitejs.dev |
| Leaflet Maps | https://leafletjs.com |
| Supabase | https://supabase.com |
| OpenStreetMap | https://www.openstreetmap.org |

---

## 🤝 Como Contribuir

### Para desenvolvedores
1. Leia a [CONSTITUTION.md](./CONSTITUTION.md) — entenda os princípios
2. Leia a [spec](../specs/001-price-comparison/spec.md) — entenda o produto
3. Veja as [TASKS.md](./TASKS.md) — encontre algo para fazer
4. Siga o SDD: spec → plan → implement → validate

### Setup rápido
```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Tipos de contribuição
- **Código**: Backend (FastAPI), Frontend (React/TS), scripts
- **Conteúdo**: Dados de mercados de Ribeirão Preto, jornais de oferta
- **Design**: UX mobile-first, acessibilidade WCAG 2.1 AA
- **Ops**: CI/CD, deploy, monitoramento
- **Divulgação**: Build in public, comunidade local

### Regras
- Toda mudança passa por spec primeiro
- PRs devem referenciar a spec que implementam
- Testes obrigatórios para endpoints críticos
- Mobile-first no frontend

---

## 📄 Licença

Este projeto é open source. Ver arquivo LICENSE no repositório.

---

*PreçoPerto — porque o melhor preço é o preço que a gente descobre junto.*

*Ribeirão Preto, 2026.*

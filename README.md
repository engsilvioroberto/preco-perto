# PreçoPerto

[![Status: Em Desenvolvimento](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)](https://github.com/engsilvioroberto/preco-perto)
[![Metodologia: SDD](https://img.shields.io/badge/Metodologia-Spec--Driven%20Development-blue)](./docs/SPEC_DRIVEN_DEVELOPMENT.md)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://www.python.org)
[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://react.dev)
[![License](https://img.shields.io/badge/License-Open%20Source-lightgrey)](./LICENSE)

> Comparador de preços colaborativo para Ribeirão Preto — porque o melhor preço é o preço que a gente descobre junto.

## 📖 Sobre

**PreçoPerto** é um PWA onde usuários escaneiam notas fiscais e admins fazem upload de jornais de ofertas. O sistema extrai preços via OCR, geolocaliza mercados e mostra no mapa onde cada produto está mais barato perto de você, com cálculo de custo-benefício do deslocamento.

**Princípios:**
- 🆓 Gratuito sempre — nunca cobra do usuário final
- 🔓 Dados abertos — todo preço escaneado é público
- 🔒 Privacidade — localização por bairro, nunca endereço exato
- 🏗️ Build in Public — todo desenvolvimento documentado

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [📋 PROJECT.md](./docs/PROJECT.md) | Visão geral completa do projeto, stack, arquitetura, status |
| [📜 CONSTITUTION.md](./docs/CONSTITUTION.md) | 9 artigos que definem os princípios não-negociáveis |
| [📝 FUNCTIONAL_SPEC](./specs/001-price-comparison/spec.md) | Especificação funcional: user scenarios, FRs, edge cases |
| [🗺️ PLAN.md](./specs/001-price-comparison/plan.md) | Arquitetura SQLite-first, stack, fases de implementação |
| [✅ TASKS.md](./docs/TASKS.md) | Decomposição executável em 5 fases (~38 dias úteis) |
| [🔧 SDD Guide](./docs/SPEC_DRIVEN_DEVELOPMENT.md) | Metodologia Spec-Driven Development |
| [🗄️ Data Model](./specs/001-price-comparison/data-model.md) | Entidades e relacionamentos do banco de dados |

## 🚀 Setup Rápido

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (gerenciador Python)

### Backend (FastAPI)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

O app estará disponível em `http://localhost:5173`

### Seed de Dados (opcional)

```bash
cd scripts
python seed_db.py
```

Popula o banco com 100+ produtos e 5+ mercados de Ribeirão Preto.

## 🏗️ Stack

**Backend:**
- Python 3.11+ · FastAPI · SQLAlchemy (async) · Pydantic v2 · SQLite (MVP)

**Frontend:**
- React 18 · TypeScript · Vite · Leaflet (mapas) · PWA

**Infraestrutura:**
- Supabase (PostgreSQL + Auth) · Railway/Fly.io (deploy backend) · Vercel (deploy frontend)

## 📊 Status Atual

**Fase 1 — Fundação** ✅ (em andamento)

Próximas fases:
- Fase 2: Backend core (API, OCR, SQLite) — 8 dias
- Fase 3: Frontend core (mapa, busca, scanner) — 9 dias
- Fase 4: Integração (OCR real, geolocalização) — 9 dias
- Fase 5: MVP Launch (deploy, usuários beta) — 8 dias

**Estimativa total**: ~38 dias úteis (+20% buffer = ~46 dias)

Ver [TASKS.md](./docs/TASKS.md) para detalhes completos.

## 🤝 Como Contribuir

1. Leia a [CONSTITUTION.md](./docs/CONSTITUTION.md) — entenda os princípios
2. Leia a [spec](./specs/001-price-comparison/spec.md) — entenda o produto
3. Veja as [TASKS.md](./docs/TASKS.md) — encontre algo para fazer
4. Siga o SDD: spec → plan → implement → validate

**Áreas que precisamos:**
- 💻 Código (backend/frontend)
- 📊 Conteúdo (dados de mercados, jornais de oferta)
- 🎨 Design (UX mobile-first, acessibilidade)
- ⚙️ Ops (CI/CD, deploy, monitoramento)
- 📢 Divulgação (build in public, comunidade local)

## 🔗 Links

- **Repositório**: https://github.com/engsilvioroberto/preco-perto
- **Issues**: https://github.com/engsilvioroberto/preco-perto/issues
- **Metodologia**: [Spec-Driven Development](./docs/SPEC_DRIVEN_DEVELOPMENT.md)

## 📄 Licença

Open Source — ver [LICENSE](./LICENSE)

---

*PreçoPerto — porque o melhor preço é o preço que a gente descobre junto.*

*Ribeirão Preto, 2026.*

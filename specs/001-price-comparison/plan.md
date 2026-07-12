# Plan — PreçoPerto MVP (SQLite-First)

**Data**: 2026-07-05  
**Objetivo**: Validar funcionalidades completas localmente antes de migrar para infraestrutura em nuvem.

## 🏗️ Arquitetura SQLite-First

- **DB**: SQLite (`precoperto.db`) gerenciado via `SQLAlchemy` + `Alembic`.
- **Backend**: Python FastAPI (modular, `app/models`, `app/api`, `app/services`).
- **Frontend**: React + Vite (PWA, rodando localmente).
- **Dados**: Migração transparente para Supabase (PostgreSQL) garantida pelo uso estrito de `SQLAlchemy`.

## 📋 Fases do Plano

### Fase 1: Setup e Infraestrutura de Dados
- Inicializar `alembic` no backend.
- Definir modelos SQLAlchemy (`Product`, `Market`, `Price`, `Invoice`).
- Criar script de `seed` (`scripts/seed_db.py`) com dados de teste.

### Fase 2: Foundational (Backend)
- Implementar endpoints REST para consulta e persistência.
- Implementar lógica de Fuzzy Matching (`rapidfuzz`) no backend.

### Fase 3: Funcionalidades MVP (Frontend/OCR)
- Integrar `Tesseract.js` no frontend para captura de notas.
- Implementar busca de produtos e visualização no mapa (`react-leaflet`).

### Fase 4: Validação
- Testes end-to-end com carga de dados via `seed_db.py`.
- Refinamento de UX local.

---

## 💡 Observações para Migração
- Todo o código de acesso a dados está isolado em `app/services/`.
- Mudança para Supabase exigirá apenas alteração no `database_url` (em `.env`) e revisão das migrações (Alembic lida com isso).

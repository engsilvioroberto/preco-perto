# PreçoPerto — Status da Sessão (2026-07-15)

## Onde estamos

Deploy do MVP com **Vercel (frontend) + Railway (backend) + Supabase (banco) + Upstash (Redis)**.

### ✅ Concluído

| Item | Status |
|------|--------|
| Supabase projeto criado | ✅ `acrgptiaqsioezqlbisg.supabase.co` |
| Supabase tabelas criadas | ✅ 8 tabelas (users, markets, products, prices, receipts, receipt_items, offer_flyers, offer_flyer_items) |
| Supabase PostGIS habilitado | ✅ `CREATE EXTENSION postgis` |
| Supabase Storage buckets | ✅ `receipts`, `offer_flyers` |
| Supabase dados populados | ✅ 2 users, 5 markets, 10 products, 15 prices |
| Upstash Redis criado | ✅ Conexão TLS testada |
| `.env.production` backend | ✅ Completo com todos os valores |
| `database.py` fix pgbouncer | ✅ `statement_cache_size=0` para Supabase |
| `requirements.txt` pinned | ✅ Versões testadas e compatíveis |
| `backend/Dockerfile` | ✅ Python 3.11 + Tesseract OCR |
| `railway.json` | ✅ Na raiz do repo, apontando pra `backend/Dockerfile` |
| `frontend/vercel.json` | ✅ SPA rewrites |
| `frontend/.gitignore` | ✅ `node_modules/`, `dist/` |
| Root `.gitignore` | ✅ `.env*`, `__pycache__/`, `*.pyc`, `preco_perto.db` |
| `.env` removidos do git | ✅ (arquivos ainda no disco) |
| `frontend/node_modules/` removido do git | ✅ (~2000 arquivos) |
| Backend testes | ✅ 4/4 passando com Supabase |
| Frontend build (tsc + vite) | ✅ Passando |
| Frontend lint (oxlint) | ✅ Passando |
| `AGENTS.md` atualizado | ✅ Seção de deploy adicionada |
| `CLAUDE.md` atualizado | ✅ Seção de deploy atualizada |

### ✅ Push para GitHub — Resolvido

- Conta `engsilvioroberto` logada com scope `workflow`
- Push force concluído — 20 commits locais no remote
- `.github/workflows/ci.yml` adicionado

### ⏳ Próximos passos

1. **Railway**: Configurar service pra usar Dockerfile (não railpack):
   - Settings → Build → Builder: **Dockerfile**
   - Dockerfile Path: `backend/Dockerfile`
   - Context: `backend`
   - Adicionar env vars do `.env.production` no Railway dashboard

2. **Vercel**: Criar projeto:
   - Root dir: `frontend/`
   - Build command: `npm run build`
   - Output: `dist`
   - Env var: `VITE_API_URL` = URL do Railway backend
   - Framework preset: Vite

3. **Teste end-to-end**: Testar no celular

## Arquivos importantes

- `backend/.env.production` — credenciais reais (Supabase, Upstash, JWT)
- `backend/.env` — dev local (SQLite, não commitado)
- `backend/Dockerfile` — build image Python 3.11
- `railway.json` — config Railway (na raiz do repo)
- `frontend/vercel.json` — SPA rewrites
- `.github/workflows/ci.yml` — CI ✅

## Credenciais (salvas em backend/.env.production)

- **Supabase URL**: `https://acrgptiaqsioezqlbisg.supabase.co`
- **Supabase anon key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **DATABASE_URL**: `postgresql+asyncpg://postgres.acrgptiaqsioezqlbisg:u4fBah5WVf6Muhwb@aws-1-us-west-2.pooler.supabase.com:6543/postgres`
- **Redis URL**: `rediss://default:gQAAAAAAAn9RAAIgcDExOTgwMDU5NzQ3MzM0MTAzYTU4MTQzNDM5Mjg2ZmY4NA@merry-lionfish-163665.upstash.io:6379`
- **JWT Secret**: `b556906b9d39b0a4b915c0350e4c17d7400016de79ba82d492a00d4fe98f4f37`

## Fix do pgbouncer (importante!)

O `database.py` foi modificado pra adicionar `statement_cache_size=0` nas conexões não-SQLite. Sem isso, o Supabase dá erro de `DuplicatePreparedStatement`. Essa mudança JÁ ESTA no commit local.

## Scripts úteis

- `backend/scripts/seed_supabase.py` — popula Supabase com dados demo
- `backend/scripts/migrate_supabase.py` — cria tabelas no Supabase
- `backend/scripts/seed_db.py` — popula SQLite local (dev)
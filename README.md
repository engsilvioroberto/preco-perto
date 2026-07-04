# 🛒 PreçoPerto

**Comparador de preços colaborativo via scanner de notas fiscais**

PWA que permite comparar preços de produtos do dia a dia em mercados próximos. Usuários escaneiam notas fiscais, o sistema extrai preços via OCR, e um mapa interativo mostra onde cada produto está mais barato — com cálculo de custo-benefício do deslocamento.

## 🎯 Problema

João precisa fazer compras mas não sabe qual mercado é mais barato. O mercado a 2km pode ter preços melhores, ou talvez valha a pena ir ao da esquina mesmo sendo mais caro. O PreçoPerto resolve isso com dados colaborativos e visualização em mapa.

## 🚀 MVP Funcionalidades

- **Busca de produtos** com autocomplete
- **Comparação de preços** entre mercados próximos
- **Mapa interativo** com pins de preços
- **Cálculo custo-benefício**: economia vs deslocamento
- **Scanner de nota fiscal** via câmera (OCR)
- **PWA** instalável no celular
- **Geolocalização** automática

## 🏗️ Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | React + TypeScript + Vite (PWA) |
| Backend | Python + FastAPI |
| Banco | Supabase (PostgreSQL) |
| Cache | Redis (Upstash) |
| Mapa | Leaflet + OpenStreetMap |
| OCR | Tesseract.js (client-side) |
| Deploy | GitHub Pages (frontend) + Railway (backend) |

## 📦 Estrutura do Projeto

```
preco-perto/
├── backend/          # FastAPI + SQLAlchemy
├── frontend/         # React + TypeScript + Vite
├── scripts/          # Scripts de setup e seed
├── specs/            # Artefatos SDD
│   └── 001-price-comparison/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── data-model.md
│       ├── contracts/api.md
│       └── quickstart.md
└── .specify/
    └── memory/
        └── constitution.md
```

## 🔧 Setup Local

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- Conta no Supabase (free tier)
- Conta no Upstash Redis (free tier)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais do Supabase

# Rodar setup do banco
python ../scripts/setup_supabase.py

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Configurar variáveis de ambiente
echo "VITE_API_URL=http://localhost:8000" > .env

# Rodar em desenvolvimento
npm run dev
```

### Acessar

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🌐 Deploy

### Frontend (GitHub Pages)

O deploy é automático via GitHub Actions ao fazer push na branch `main`.

URL: https://engsilvioroberto.github.io/preco-perto/

### Backend (Railway/Render)

1. Criar projeto no Railway ou Render
2. Conectar ao repositório GitHub
3. Configurar variáveis de ambiente:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `DATABASE_URL`
   - `REDIS_URL`
   - `JWT_SECRET`

## 📱 Testar no Celular

1. Acesse https://engsilvioroberto.github.io/preco-perto/ no celular
2. Permitir acesso à localização
3. Buscar um produto (ex: "leite")
4. Ver comparação de preços e mapa
5. Para instalar: "Adicionar à tela inicial"

## 📊 Metodologia

Este projeto segue **Spec-Driven Development (SDD)**:

1. **Constitution** → Princípios imutáveis
2. **Spec** → O QUE construir (user stories)
3. **Plan** → COMO construir (tech stack)
4. **Tasks** → Decomposição em tarefas
5. **Implement** → Código com TDD
6. **Converge** → Validação final

Todos os artefatos estão em `specs/001-price-comparison/`.

## 🗺️ Roadmap

### MVP (Atual)
- [x] Constitution e Spec
- [x] Plan técnico
- [x] Tasks e implementação
- [x] Deploy GitHub Pages
- [ ] Setup Supabase (aguardando credenciais)
- [ ] Seed de dados com cupons fiscais reais
- [ ] Testes no celular

### V2 (Futuro)
- [ ] App mobile nativo (Flutter)
- [ ] Gamificação (ranking, badges)
- [ ] Upload de jornais de ofertas (admin)
- [ ] OCR server-side (mais preciso)
- [ ] Lista de compras inteligente

## 🤝 Contribuindo

Este é um projeto open source. Contribuições são bem-vindas!

## 📄 Licença

MIT

---

**Região inicial**: Ribeirão Preto - SP  
**Time**: Hermione (agentes) + Silvio Roberto Filho (PO)

# 🛒 PreçoPerto

**Comparador de preços colaborativo via scanner de notas fiscais**

PWA que permite comparar preços de produtos do dia a dia em mercados próximos. Usuários escaneiam notas fiscais, o sistema extrai preços via OCR, e um mapa interativo mostra onde cada produto está mais barato — com cálculo de custo-benefício do deslocamento.

## 🎯 Problema

João precisa fazer compras mas não sabe qual mercado é mais barato. O mercado a 2km pode ter preços melhores, ou talvez valha a pena ir ao da esquina mesmo sendo mais caro. O PreçoPerto resolve isso com dados colaborativos e visualização em mapa.

## 🚀 MVP

- **Scanner de nota fiscal** via câmera (OCR)
- **Upload de jornais de ofertas** (população inicial de dados)
- **Mapa de preços** por produto com geolocalização
- **Busca inteligente** com comparação de preços
- **Cálculo custo-benefício**: economia vs deslocamento
- **Cadastro/login** de usuário

## 🏗️ Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | React + TypeScript (PWA) |
| Backend | Python (FastAPI) |
| OCR | Tesseract + parser NFC-e |
| Banco | PostgreSQL + PostGIS |
| Mapa | Leaflet + OpenStreetMap |
| Storage | Cloudflare R2 ou S3 |

## 📊 Estratégia de Dados

**Fase 1**: Upload de jornais de ofertas dos mercados de Ribeirão Preto (dados verificados)  
**Fase 2**: Usuários escaneiam notas fiscais e contribuem com preços reais

## 📦 Spec-Driven Development

Este projeto segue metodologia SDD (Spec-Driven Development):

```
.specify/
├── memory/
│   └── constitution.md       # Princípios do projeto
specs/
└── 001-price-comparison/
    ├── spec.md               # Especificação funcional (O QUE)
    ├── plan.md               # Plano técnico (COMO) — próxima sessão
    └── tasks.md              # Lista de tarefas — próxima sessão
```

## 🗺️ Roadmap

### MVP (Atual)
- [x] Constitution e Spec criados
- [ ] Plan técnico
- [ ] Tasks e implementação
- [ ] Deploy em Ribeirão Preto

### V2 (Futuro)
- [ ] App mobile nativo (Flutter)
- [ ] Gamificação (ranking, badges)
- [ ] Anúncios direcionados
- [ ] Assinatura premium (ad-free)
- [ ] Lista de compras inteligente

## 💰 Monetização

1. **Anúncios direcionados** (espaço publicitário para mercados e marcas)
2. **Assinatura premium** para remover anúncios

## 🤝 Contribuindo

Este é um projeto open source. Contribuições são bem-vindas!

## 📄 Licença

A definir.

---

**Região inicial**: Ribeirão Preto - SP  
**Time**: Hermione (agentes) + Silvio Roberto Filho (PO)

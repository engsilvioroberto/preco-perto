# Clarifications — PreçoPerto MVP

**Data**: 2026-07-04  
**Status**: ✅ Resolvido (decisões tomadas pela Hermione para MVP)

---

## Decisões Técnicas para MVP

### 1. API de Mapa
**Decisão**: OpenStreetMap + Leaflet  
**Justificativa**: Gratuito, funciona bem no Brasil, sem limite de uso. Google Maps exige cartão de crédito e pode ter custos imprevisíveis.  
**Trade-off**: Menos preciso para geocoding de endereços brasileiros, mas suficiente para MVP.

### 2. Cálculo de Custo de Deslocamento
**Decisão**: Estimativa linear baseada em distância  
**Fórmula**: 
- A pé: 5 km/h × R$0 (sem custo direto)
- Carro: 30 km/h × R$0,75/km (gasolina + manutenção)
- Ônibus: R$4,40 (tarifa fixa Ribeirão Preto)

**Justificativa**: Simples, sem API paga, suficiente para MVP.  
**Trade-off**: Não considera trânsito, rotas reais, ou custo real de combustível.

### 3. Serviço de OCR
**Decisão**: Tesseract.js (client-side) + pytesseract (server-side fallback)  
**Justificativa**: Custo zero, controle total, funciona offline (client-side).  
**Trade-off**: Precisão menor que Google Vision (~70-80% vs 95%). Para MVP, aceitável. Usuário pode editar/corrigir antes de confirmar.

### 4. Autenticação
**Decisão**: Email/senha simples (sem OAuth para MVP)  
**Justificativa**: Simplicidade radical (Artigo II). OAuth adiciona complexidade desnecessária para MVP.  
**Trade-off**: Usuário precisa criar conta manualmente. Pode adicionar Google OAuth no V2.

### 5. Normalização de Produtos
**Decisão**: Fuzzy matching + normalização básica  
**Estratégia**:
- Lowercase + remover acentos
- Padronizar unidades: "1L" = "1 litro" = "1000ml"
- Remover marcas comuns do nome para comparação genérica
- Fuzzy matching (Levenshtein distance) para produtos similares

**Justificativa**: Simples, funciona para MVP, permite comparação útil.  
**Trade-off**: Pode agrupar produtos diferentes (ex: "Leite Integral" vs "Leite Desnatado"). Usuário pode refinar busca com nome completo.

---

## Decisões Adicionais (não listadas no spec)

### 6. Deploy
**Decisão**: 
- Frontend: GitHub Pages (grátis, estático)
- Backend: Railway ou Render (free tier, Python)
- DB: Supabase (free tier, PostgreSQL + PostGIS)
- Cache: Upstash Redis (free tier, 10k commands/dia)

**Justificativa**: Custo zero para MVP, escala suficiente para testes iniciais.

### 7. Stack Técnica
**Decisão**:
- Frontend: React + TypeScript + Vite (PWA)
- Backend: Python + FastAPI
- ORM: SQLAlchemy + Alembic (migrations)
- Mapa: Leaflet + react-leaflet
- OCR: Tesseract.js (client-side) ou pytesseract (server-side)

**Justificativa**: Stack moderna, boa documentação, comunidade ativa.

### 8. População Inicial de Dados
**Decisão**: 
- Buscar cupons fiscais reais na internet (sites de notas fiscais públicas)
- Extrair dados via OCR
- Popular banco com 100+ produtos de 5+ mercados de Ribeirão Preto

**Justificativa**: Resolve chicken-and-egg problem (Artigo VII), dá valor imediato ao usuário.

---

## Próximos Passos

Com clarifications resolvidos, avançar para:
1. **Plan.md** — plano técnico detalhado
2. **Data-model.md** — schema do banco
3. **Tasks.md** — decomposição em tarefas executáveis
4. **Implement** — código

---

**Aprovado por**: Hermione (autonomia delegada por Silvio)

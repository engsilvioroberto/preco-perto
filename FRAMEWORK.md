# AURA Framework v1 — Agent-Unified Release Architecture

**Autor**: OpenCode (em colaboração com Silvio)  
**Status**: Rascunho para aprovação do Hermes  
**Data**: 2026-07-10

---

## 1. Conceito

O AURA Framework é um conjunto de convenções, templates e protocolos para desenvolvimento de software assistido por múltiplos agentes de IA (OpenCode + Hermes), com rastreamento via **Notion** (specs, tasks, bugs, roadmap) e **GitHub** (código, PRs, issues, deploy).

Funciona para qualquer projeto — monorepo, frontend-only, backend-only, mobile, etc.

---

## 2. Os Agentes

| Agente | Plataforma | Acesso | Papel |
|--------|-----------|--------|-------|
| **OpenCode** | Notebook local (Silvio) | Filesystem, dev server, npm/pip, Git | **Builder principal** — implementa, testa, commita. Trabalha presencialmente com Silvio. |
| **Hermes** | VPS (Telegram) | Notion API, GitHub API, clone do repo, CI/CD | **Builder secundário + Orchestrator** — implementa tasks remotas, revisa PRs, deploya, documenta specs no Notion, monitora. |

Ambos **codam**. Nenhum é só revisor ou só planejador. A diferença é o canal de acesso (local vs remoto/Telegram).

---

## 3. Protocolo Anti-Conflito (Crucial)

Ambos os agentes editam código no mesmo repositório. Para evitar conflito:

### 3.1. Notion é a Fonte da Verdade

Toda task no Notion (database `Tasks`) tem estes campos obrigatórios:

| Campo | Valores |
|-------|---------|
| `Status` | `To Do` / `In Progress` / `Review` / `Done` / `Blocked` |
| `Assignee` | `OpenCode` / `Hermes` / `Anyone` (quem pegar primeiro) |
| `Priority` | `P0` (bloqueante) / `P1` (alta) / `P2` (média) / `P3` (baixa) |
| `Feature` | Link para database `Features` |
| `PR` | URL do Pull Request no GitHub (preenchido ao abrir) |

### 3.2. Regra do Assignee

- **Nunca iniciar uma task sem assignar no Notion primeiro.** Se está `Assignee: Anyone` e você quer pegar, mude para seu nome + `In Progress` antes de escrever uma linha de código.
- **Se uma task tem assignee, não tocar.** Se acha que o assignee não está avançando, marque como `Blocked` e avise no grupo/Telegram.

### 3.3. Branch Ownership

Cada agente usa prefixos próprios para evitar push conflitante:

| Agente | Feature | Fix | Chore/Docs |
|--------|---------|-----|------------|
| **OpenCode** | `feat/nome-da-branch` | `fix/nome-da-branch` | `chore/nome` |
| **Hermes** | `hf/nome-da-branch` | `hfix/nome-da-branch` | `hchore/nome` |

**Nunca fazer push em branch do outro agente.** Se um PR do outro agente está aberto e você precisa daquela mudança, espere mergear, depois rebaseie sua branch em cima da `main`.

### 3.4. Ciclo de Vida de uma Task

```
Notion: To Do → Hermes ou OpenCode: assign + In Progress
  → trabalha na branch (prefixo próprio)
  → abre PR no GitHub (title = task ID)
  → marca reviewer = outro agente
  → Notion: status Review + PR link
  → revisor aprova ou pede mudanças
  → merge → Notion: Done
```

### 3.5. O que fazer em caso de conflito

1. Nunca resolver conflito na branch do outro. Se seu PR tem conflito com `main`, rebaseie **sua** branch.
2. Se dois PRs tocam os mesmos arquivos, combinem a ordem de merge (quem mergeia primeiro).
3. Se houver discordância técnica: PR comentado com argumentos, Silvio (humano) desempata.

---

## 4. Feature Lifecycle

### Fase 1 — IDEA → SPEC (Hermes documenta no Notion)

**Trigger**: Silvio diz "quero fazer X" ou Hermes identifica uma necessidade.

1. Hermes cria entry na database `Features` do Notion com:
   - Nome, descrição, rationale
   - Prioridade (P0/P1/P2/P3)
   - Dependências (se precisar de outra feature primeiro)
2. Hermes cria `Spec` sub-page com campos:
   - Visão geral
   - User stories + acceptance criteria
   - Edge cases
   - Functional requirements (FR-001, FR-002...)
   - Key entities
   - Assumptions
3. Hermes notifica no Telegram: "Nova spec pronta: [link]"
4. Silvio ou OpenCode revisam e aprovam

### Fase 2 — SPEC → PLAN (Hermes documenta no Notion)

A partir da spec aprovada:

1. Hermes cria `Plan` sub-page:
   - Technical context (stack, services, libs)
   - Project structure (árvore de diretórios)
   - Complexity tracking (trade-offs aceitos, riscos)
   - Constitution check (se o projeto tem constituição)
2. Hermes cria `Data Model` sub-page (entidades, relacionamentos, campos, tipos)
3. Hermes cria `Contracts` sub-page (endpoints, request/response, status codes, auth)

### Fase 3 — PLAN → TASKS (Hermes quebra em tarefas no Notion)

1. Hermes cria tasks individuais na database `Tasks` do Notion, numeradas (T-001, T-002...)
2. Cada task deve ser **atômica** — uma task = um PR
3. Tasks organizadas em fases (Phase 1: Setup, Phase 2: Core...)
4. Cada task tem: título, descrição técnica, acceptance criteria, assignee (`Anyone`), prioridade

### Fase 4 — TASKS → IMPLEMENTAÇÃO (OpenCode ou Hermes)

1. Agente (quem pegar a task):
   - Marca `In Progress` + `Assignee`
   - Cria branch com prefixo próprio (`feat/` ou `hf/`)
   - Implementa seguindo spec + contracts
   - Adiciona testes
   - Roda `npm run build` ou equivalente
   - Abre PR com título `T-XXX: descrição` + link pra task no Notion

### Fase 5 — REVISÃO → DEPLOY

1. Outro agente revisa o PR:
   - Código segue a spec?
   - Contratos foram respeitados?
   - Testes passam?
   - Builda?
2. Se aprovado: merge + Notion → `Done`
3. Se pede mudanças: autor ajusta, re-revisa
4. Hermes faz deploy (se aplicável)

---

## 5. Bug Lifecycle

### 5.1. Report

- **Qualquer um** abre uma GitHub Issue com label `bug`
- Template mínimo de issue:
  ```
  **Comportamento esperado**: ...
  **Comportamento atual**: ...
  **Passos para reproduzir**: ...
  **Ambiente**: (URL, navegador, mobile/desktop)
  **Severidade**: S1 (crítico) / S2 (alto) / S3 (médio) / S4 (baixo)
  ```

### 5.2. Triage (Hermes)

1. Hermes identifica a issue (via webhook GitHub → Telegram ou varredura diária)
2. Hermes classifica severidade e cria entry na database `Bugs` do Notion:
   - Link pra issue do GitHub
   - Descrição do bug
   - Impacto
   - Root cause (preenchido após análise)
   - Assignee
3. Se `S1` ou `S2`: Hermes pergunta no Telegram "Bug crítico, Silvio quer RCA documentado ou pode pular pra fix?"
4. Se `S3` ou `S4`: Hermes cria task na `Tasks` como qualquer feature

### 5.3. Root Cause Analysis (opcional)

Para bugs `S1` ou bugs que Silvio pedir RCA:

Hermes cria `specs/_bugs/BUG-XXX/rca.md` no repositório:

```markdown
# BUG-XXX: [título]

## Root Cause
[explicação técnica do porquê aconteceu]

## Impact
[quem afeta, quantos usuários, o que quebra]

## Fix Proposed
[abordagem: o que mudar, em quais arquivos]

## Prevention
[como evitar que esse tipo de bug volte: test, lint, type guard]
```

### 5.4. Fix + Verify

1. Agente assignado implementa o fix em branch `fix/` ou `hfix/`
2. Adiciona teste que captura o bug (regression test)
3. Abre PR com `Closes #ISSUE_NUMBER` no body
4. Outro agente revisa
5. Merge → deploy → Notion: `Done` → GitHub Issue: `Close`

---

## 6. Notion Structure

### Databases

#### `Features`
| Campo | Tipo | Exemplo |
|-------|------|---------|
| `Name` | Title | "Comparação de Preços" |
| `Status` | Select | `Draft` / `Approved` / `In Progress` / `Done` |
| `Priority` | Select | `P0` / `P1` / `P2` / `P3` |
| `Spec` | Rich Text | Visão geral + user stories |
| `Plan` | Rich Text | Stack, riscos, trade-offs |
| `Specs Folder` | Text | `specs/001-price-comparison/` |
| `Created` | Date | |

#### `Tasks`
| Campo | Tipo | Exemplo |
|-------|------|---------|
| `ID` | Title | `T-010` |
| `Description` | Text | "API: Buscar Produtos (autocomplete)" |
| `Status` | Select | `To Do` / `In Progress` / `Review` / `Done` / `Blocked` |
| `Assignee` | Select | `OpenCode` / `Hermes` / `Anyone` |
| `Priority` | Select | `P0` / `P1` / `P2` / `P3` |
| `Feature` | Relation → `Features` | |
| `PR` | URL | Link pro PR no GitHub |
| `Phase` | Select | `Phase 1: Setup` / ... |

#### `Bugs`
| Campo | Tipo | Exemplo |
|-------|------|---------|
| `ID` | Title | `BUG-042` |
| `Severity` | Select | `S1` / `S2` / `S3` / `S4` |
| `Status` | Select | `Reported` / `Triaged` / `In Progress` / `Review` / `Done` |
| `Assignee` | Select | `OpenCode` / `Hermes` |
| `GitHub Issue` | URL | |
| `RCA` | Rich Text | Root cause analysis |
| `Fix PR` | URL | |

#### `Roadmap`
| Campo | Tipo | Exemplo |
|-------|------|---------|
| `Milestone` | Title | `MVP Launch` / `V2` |
| `Features` | Relation → `Features` | |
| `Target Date` | Date | |
| `Status` | Select | `Planning` / `In Progress` / `Shipped` |

---

## 7. Repo Structure (portável)

```
projeto/                        ← qualquer projeto
├── .specify/
│   └── memory/
│       └── constitution.md    ← princípios imutáveis (se o projeto tiver)
├── specs/                      ← specs versionadas junto do código
│   ├── 001-nome-da-feature/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   ├── data-model.md
│   │   ├── clarifications.md
│   │   ├── contracts/
│   │   │   └── api.md
│   │   └── quickstart.md
│   ├── 002-proxima-feature/
│   │   └── ...
│   └── _bugs/
│       └── BUG-042/
│           ├── report.md
│           └── rca.md
├── _templates/                  ← seed pra novos projetos
│   ├── feature/
│   │   └── (spec.md, tasks.md, plan.md...)
│   └── bug/
│       └── (report.md, rca.md)
├── AGENTS.md                    ← instruções dos agentes (comandos, arquitetura)
├── CLAUDE.md                    ← guidance pro Claude Code
└── FRAMEWORK.md                 ← este documento (auto-documentado)
```

---

## 8. Template Files

O pacote `_templates/` contém:

| Template | Para |
|----------|------|
| `feature/spec.md` | Escrever user stories, FRs, edge cases |
| `feature/plan.md` | Stack, estrutura, riscos, trade-offs |
| `feature/tasks.md` | Quebrar spec em tarefas numeradas por fase |
| `feature/data-model.md` | Entidades, relacionamentos, campos |
| `feature/contracts/api.md` | Endpoints, request/response, status codes |
| `feature/clarifications.md` | Perguntas pendentes pro PO |
| `feature/quickstart.md` | Guia de validação/teste manual |
| `bug/report.md` | Template de report (sincronizado com GitHub Issue) |
| `bug/rca.md` | Root cause analysis |
| `AGENTS.md.tpl` | Template de instruções pra agentes |
| `CLAUDE.md.tpl` | Template de guidance pra Claude Code |

Cada template tem placeholders (`{{project_name}}`, `{{feature_name}}`, etc) que podem ser substituídos manualmente ou via script.

---

## 9. Convenções Gerais

### Nomenclatura de Features
- `NNN-nome-em-kebab-case` (ex: `001-price-comparison`, `002-auth-google`)
- Número sequencial global (não reinicia por projeto)

### Nomenclatura de Bugs
- `BUG-NNN` (número sequencial, independente de issues do GitHub)
- Se o bug tem issue no GitHub, manter ambos vinculados

### Commits
- Seguir conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`
- Menção ao ID da task quando aplicável: `feat(T-010): add product search API`
- Para bugs: `fix(BUG-042): guard against null price on cost_benefit`

### PRs
- Título: `[T-XXX] descrição` ou `[BUG-XXX] descrição`
- Body: changelog do que foi feito, screenshots se UI
- Reviewer: o outro agente (ou Silvio humano)
- Label: `feature` / `bug` / `dependencies` / `blocked`

---

## 10. Glossário

| Termo | Significado |
|-------|-------------|
| **AURA** | Agent-Unified Release Architecture |
| **Spec** | Documento de especificação funcional |
| **Plan** | Documento de planejamento técnico |
| **Task** | Unidade atômica de trabalho = 1 PR |
| **RCA** | Root Cause Analysis |
| **Assignee** | Dono atual da task (`OpenCode`, `Hermes`, ou `Anyone`) |
| **P0-P3** | Prioridade (P0 = bloqueante, P3 = nice to have) |
| **S1-S4** | Severidade de bug (S1 = crítico, S4 = cosmético) |

---

## 11. Perguntas Pendentes pra Silvio / Decisões

- [ ] **Hermes, você acessa o repo via clone Git na VPS ou só via GitHub web (criar/edit PR sem checkout)?** (Impacta se Hermes pode rodar testes/build localmente)
- [ ] **Quer que ambos rodem `npm run build` / testes antes de abrir PR, ou só o CI faz isso?**
- [ ] **Tasks do Notion viram GitHub Issues também (duplicado), ou só link do Notion no PR?**
- [ ] **Deploy é manual (Silvio/Hermes dispara) ou automático (merge na main → deploy)?**
- [ ] **Quer notificação no Telegram pra toda mudança de status no Notion?**

---

**Fim do documento.** Silvio, copia isso e passa pro Hermes. Depois que ele aprovar/fizer ressalvas, volto pra gerar os templates e ajustar o `AGENTS.md` atual.

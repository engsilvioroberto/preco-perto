# Constituição do Projeto PreçoPerto

## Preâmbulo

O PreçoPerto é um PWA colaborativo de comparação de preços que empodera consumidores a tomar decisões de compra mais inteligentes através de dados crowdsourced de notas fiscais e ofertas de mercado.

## Artigos Fundamentais

### Artigo I — Mobile-First, PWA-First

Toda feature é projetada primeiro para experiência mobile. O PWA é a plataforma primária do MVP. Apps nativos são futuro (V2), não presente.

### Artigo II — Simplicidade Radical (NON-NEGOTIABLE)

A UX deve ser tão simples que qualquer pessoa consegue usar sem tutorial. Fluxos complexos são divididos em passos claros. Menos é mais.

### Artigo III — Dados Confiáveis

Preços devem ter timestamp e origem clara (jornal de ofertas ou nota fiscal escaneada). Dados sem procedência não entram no sistema. A confiança do usuário é o ativo mais valioso.

### Artigo IV — Geolocalização como Core

Toda informação de preço está vinculada a um local (mercado). O mapa não é feature secundária — é o coração do produto. Sem geolocalização, não há comparação útil.

### Artigo V — Custo-Benefício Transparente

O sistema calcula e mostra claramente: "Economia X vs Custo de Deslocamento Y". O usuário decide, mas tem informação completa. Sem manipulação, sem viés.

### Artigo VI — Privacidade e LGPD

Dados de compra são sensíveis. Notas fiscais são processadas e os dados extraídos são anonimizados/agregados. O usuário controla o que compartilha. Conformidade total com LGPD desde o dia 1.

### Artigo VII — População Inicial via Jornais de Ofertas

Antes de depender de crowdsourcing, o sistema é populado com dados reais de jornais de ofertas de Ribeirão Preto. Isso resolve o chicken-and-egg problem e dá valor imediato.

### Artigo VIII — Open Source Friendly

O código é aberto. A comunidade pode contribuir, auditar, e adaptar. Transparência técnica gera confiança no produto.

### Artigo IX — Performance e Acessibilidade

O PWA deve carregar em <3s em 4G, funcionar offline (cache de dados recentes), e ser acessível (WCAG 2.1 AA). Não podemos excluir usuários com dispositivos antigos ou conexão ruim.

## Princípios de Design

- **Clareza > Estética**: bonito é importante, mas legível e intuitivo é obrigatório
- **Feedback imediato**: toda ação do usuário tem resposta visual em <200ms
- **Offline-first**: dados essenciais disponíveis sem conexão
- **Progressive disclosure**: mostra o básico primeiro, detalhes sob demanda

## Governança

Esta constituição é imutável durante o desenvolvimento do MVP. Mudanças exigem:
1. PR com rationale detalhado
2. Aprovação do PO (Silvio)
3. Atualização deste documento no repo

## Sucesso do MVP

- 100+ produtos com preços mapeados em Ribeirão Preto
- 5+ mercados cobertos
- Usuário consegue comparar preço de um produto em <10 segundos
- Scanner OCR funciona em >80% das notas fiscais testadas
- Cálculo de deslocamento mostra economia real vs custo

---

**Versão**: 1.0  
**Data**: 2026-07-03  
**Aprovado por**: Silvio Roberto Filho (PO)

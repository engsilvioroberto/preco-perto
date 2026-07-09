# Spec-Driven Development (SDD)

Este projeto segue a metodologia Spec-Driven Development.

## Princípios

1. **Spec First**: Toda funcionalidade começa com uma especificação em `spec/`
2. **Implementação Segue Spec**: O código implementa exatamente o que a spec define
3. **Spec é Fonte da Verdade**: Em caso de dúvida, a spec prevalece
4. **Evolução via Spec**: Mudanças começam atualizando a spec

## Estrutura de Specs

```
spec/
├── features/          # Especificações de funcionalidades
├── api/               # Contratos de API
└── data/              # Modelos de dados
```

## Workflow

1. Escrever/atualizar spec em `spec/features/`
2. Revisar spec (opcional)
3. Implementar seguindo a spec
4. Validar que implementação atende spec

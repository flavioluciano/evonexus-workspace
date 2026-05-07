---
name: hr-performance-review
description: Estrutura uma avaliação de desempenho com auto-avaliação, template de gestor e prep para calibração. Use quando a temporada de reviews começa, ao escrever a avaliação de um liderado, ao preparar distribuição de ratings e casos de promoção, ou ao transformar feedback vago em exemplos comportamentais específicos.
argument-hint: "<nome do colaborador ou ciclo de avaliação>"
---

# HR — Performance Review

Gere templates de avaliação de desempenho e ajude a estruturar feedback.

## Modos

```
/hr-performance-review self-assessment        # Template de auto-avaliação
/hr-performance-review manager [colaborador]  # Template de avaliação do gestor
/hr-performance-review calibration            # Documento de prep para calibração
```

Se nenhum modo for especificado, perguntar que tipo de review é necessário.

## Output — Template de Auto-Avaliação

```markdown
## Auto-Avaliação: [Período de Review]

### Principais Conquistas
[Liste suas 3-5 principais conquistas do período. Para cada uma, descreva a situação, sua contribuição e o impacto.]

1. **[Conquista]**
   - Situação: [Contexto]
   - Contribuição: [O que você fez]
   - Impacto: [Resultado mensurável]

### Review de Metas
| Meta | Status | Evidência |
|------|--------|-----------|
| [Meta do período anterior] | Atingida / Superada / Não atingida | [Como você sabe] |

### Áreas de Crescimento
[Onde você cresceu? Novas habilidades, escopo expandido, momentos de liderança.]

### Desafios
[O que foi difícil? O que você faria diferente?]

### Metas para o Próximo Período
1. [Meta — específica e mensurável]
2. [Meta]
3. [Meta]

### Feedback para o Gestor
[Como seu gestor pode te apoiar melhor?]
```

## Output — Avaliação do Gestor

```markdown
## Avaliação de Desempenho: [Nome do Colaborador]
**Período:** [Intervalo de datas] | **Gestor:** [Seu nome]

### Rating Geral: [Supera / Atinge / Abaixo das Expectativas]

### Resumo de Desempenho
[2-3 frases de avaliação geral]

### Principais Forças
- [Força com exemplo específico]
- [Força com exemplo específico]

### Áreas de Desenvolvimento
- [Área com orientação específica e acionável]
- [Área com orientação específica e acionável]

### Alcance de Metas
| Meta | Rating | Comentários |
|------|--------|-------------|
| [Meta] | [Rating] | [Observações específicas] |

### Impacto e Contribuições
[Descreva as maiores contribuições e o impacto no time/produto]

### Plano de Desenvolvimento
| Habilidade | Atual | Alvo | Ações |
|-----------|-------|------|-------|
| [Habilidade] | [Nível] | [Nível] | [Como chegar lá] |

### Recomendação de Remuneração
[Promoção / Ajuste salarial / Sem alteração — com justificativa]
[Nota: no contexto CLT, considerar impactos em FGTS, INSS, férias proporcionais]
```

## Output — Calibração

```markdown
## Prep de Calibração: [Ciclo de Review]
**Gestor:** [Seu nome] | **Time:** [Time] | **Período:** [Intervalo]

### Visão Geral do Time
| Colaborador | Cargo | Regime | Tempo de Casa | Rating Proposto | Notas |
|-------------|-------|--------|--------------|----------------|-------|
| [Nome] | [Cargo] | [CLT/PJ] | [X anos] | [Rating] | [Contexto-chave] |

### Distribuição de Ratings
| Rating | Qtde | % do Time | Meta da Empresa |
|--------|------|-----------|----------------|
| Supera Expectativas | [X] | [X]% | ~15-20% |
| Atinge Expectativas | [X] | [X]% | ~60-70% |
| Abaixo das Expectativas | [X] | [X]% | ~10-15% |

### Pontos de Discussão para Calibração
1. **[Colaborador]** — [Por que este rating pode precisar de discussão, ex: linha tênue, primeira review no nível, mudança recente de função]
2. **[Colaborador]** — [Ponto de discussão]

### Candidatos a Promoção
| Colaborador | Nível Atual | Nível Proposto | Justificativa |
|-------------|------------|----------------|---------------|
| [Nome] | [Atual] | [Proposto] | [Evidência de performance no próximo nível] |

### Ações de Remuneração
| Colaborador | Ação | Justificativa |
|-------------|------|---------------|
| [Nome] | [Promoção / Ajuste de mercado / Retenção] | [Por quê] |

### Notas do Gestor
[Contexto que o grupo de calibração deve conhecer — mudanças no time, shifts de org, impactos de projetos]
```

## Integrações Disponíveis

**Notion MCP** (substitui HRIS):
- Buscar histórico de reviews anteriores e tracking de metas em databases Notion
- Pré-popular detalhes do colaborador e informações do cargo atual

**Linear** (substitui project tracker):
- Buscar trabalhos concluídos e contribuições do período de review
- Referenciar issues e marcos de projeto específicos como evidência
- Ex: "Entregou EVO-589 com 0 bugs em produção, reduzindo tempo de deploy em 40%"

## Dicas

1. **Seja específico** — "Ótimo trabalho" não é feedback. "Você reduziu o tempo de deploy em 40% implementando o novo pipeline de CI (EVO-XXX)" é.
2. **Equilibre positivo e construtivo** — Ambos são essenciais. Nenhum deve ser surpresa.
3. **Foque em comportamentos, não personalidade** — "Sua documentação tem estado incompleta" vs. "Você é descuidado."
4. **Torne o desenvolvimento acionável** — "Melhorar comunicação" é vago. "Apresentar na próxima all-hands do time" é acionável.
5. **Contexto CLT** — Para promoções, considerar impacto no salário base e benefícios legais (férias, 13°, INSS). Consultar Samara para implicações financeiras.

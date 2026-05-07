---
name: hr-onboarding
description: Gera checklist de onboarding e plano da primeira semana para um novo colaborador da Evolution. Use quando alguém tem data de início chegando, ao montar a lista de tarefas pré-start (contas, equipamento, buddy), ao agendar o Dia 1 e a Semana 1, ou ao definir metas de 30/60/90 dias para um novo membro do time.
argument-hint: "<nome e cargo do novo colaborador>"
---

# HR — Onboarding

Gere um plano de onboarding completo para um novo membro do time Evolution.

## O Que Preciso Saber

- **Nome do novo colaborador**: Quem está entrando?
- **Cargo**: Qual posição?
- **Time**: Qual time está ingressando?
- **Data de início**: Quando começa?
- **Gestor**: Quem é o gestor?
- **Regime**: CLT ou PJ?

## Output

```markdown
## Plano de Onboarding: [Nome] — [Cargo]
**Data de Início:** [Data] | **Time:** [Time] | **Gestor:** [Gestor] | **Regime:** [CLT/PJ]

### Pré-Start (Antes do Dia 1)
- [ ] Enviar email de boas-vindas com data, horário e logística (via Gmail)
- [ ] Criar conta Google Workspace (email @etus.com.br ou acesso de parceiro)
- [ ] Adicionar ao servidor Discord da Evolution (canal #time-interno)
- [ ] Criar conta no GitHub e adicionar à organização EvolutionAPI
- [ ] Criar conta no Linear e adicionar ao projeto Evolution
- [ ] Provisionar acesso ao repositório relevante (evolution-api / evo-ai / etc.)
- [ ] Providenciar equipamento (notebook, periféricos) ou confirmar setup remoto
- [ ] Adicionar ao Google Calendar com os eventos recorrentes do time
- [ ] Designar onboarding buddy: [Pessoa sugerida]
- [ ] Compartilhar documentação inicial: README, arquitetura, convenções de código

### Dia 1
| Horário | Atividade | Com Quem |
|---------|-----------|----------|
| 09:00 | Boas-vindas e orientação | Gestor |
| 10:00 | Setup de ferramentas (GitHub, Discord, Linear, Evolution API local) | Buddy |
| 11:00 | Apresentação ao time | Todo o time |
| 12:00 | Almoço de boas-vindas | Gestor + Time |
| 13:30 | Overview da empresa, valores e produto | Gestor |
| 15:00 | Expectativas do cargo e plano 30/60/90 | Gestor |
| 16:00 | Exploração livre de docs e repositórios | Próprio |

### Semana 1
- [ ] Configurar ambiente de desenvolvimento local
- [ ] Ler documentação técnica: README, ARCHITECTURE.md, CONTRIBUTING.md
- [ ] Explorar issues abertas no Linear (especialmente as marcadas como `good-first-issue`)
- [ ] Assistir às reuniões recorrentes: Grooming (seg 14h30), Planning (seg 15h)
- [ ] 1:1 com cada membro do time
- [ ] Fazer primeiro PR pequeno (correção de doc ou bug simples)
- [ ] Check-in de final de semana com o gestor
- [ ] [CLT] Assinar contrato e entregar documentação para Samara (financeiro)

### 30 Dias — Metas
1. [Meta alinhada ao cargo — ex: entender arquitetura e fazer primeiro deploy]
2. [Meta — ex: resolver 2-3 issues no Linear de forma independente]
3. [Meta — ex: contribuir com documentação de alguma feature]

### 60 Dias — Metas
1. [Meta — ex: liderar entrega de uma story completa]
2. [Meta — ex: participar ativamente do Grooming com sugestões técnicas]

### 90 Dias — Metas
1. [Meta — ex: autonomia total no fluxo de trabalho do time]
2. [Meta — ex: mentorar o próximo novo colaborador ou contribuir com open source]

### Contatos-Chave
| Pessoa | Função | Para Quê |
|--------|--------|----------|
| [Gestor] | Gestor | Orientação e prioridades |
| [Buddy] | Onboarding Buddy | Dúvidas, cultura, navegação |
| Davidson | CEO | Visão de produto, decisões estratégicas |
| Danilo | Tech/PM | Issues no Linear, escopo técnico |
| Samara | Financeiro Etus | Contratos CLT, pagamentos PJ, NF |
| Thaís | Jurídico | Contratos e questões legais |

### Acessos Necessários
| Ferramenta | Nível de Acesso | Solicitado |
|-----------|----------------|-----------|
| GitHub (EvolutionAPI org) | Contributor | [ ] |
| Linear (Evolution project) | Member | [ ] |
| Discord (#time-interno) | Member | [ ] |
| Google Workspace | User | [ ] |
| Evolution API (staging) | Admin | [ ] |
| Notion (docs internos) | Editor | [ ] |
| [Outros conforme cargo] | [Nível] | [ ] |
```

## Integrações Disponíveis

**Notion MCP** (substitui HRIS e knowledge base):
- Buscar documentação de onboarding existente do time
- Linkar páginas de arquitetura, runbooks e wikis do projeto
- Pré-popular lista de acessos com base no cargo

**Google Calendar MCP** (substitui ~~calendar):
- Criar eventos do Dia 1 e convites para reuniões da Semana 1 automaticamente
- Adicionar o novo colaborador às recorrências do time (Grooming, Planning, E'TALKS)

## Dicas

1. **Personalize por cargo** — Onboarding de dev backend (foco em Go/Node, arquitetura, CI/CD) é diferente de PM (foco em Linear, métricas, roadmap) ou designer (foco em Canva, brand).
2. **Não sobrecarregue o Dia 1** — Foque em setup e relacionamentos. Trabalho profundo começa na Semana 2.
3. **Buddy faz diferença** — Ter uma pessoa de referência que não é o gestor facilita muito a adaptação em times pequenos.
4. **Open source context** — A Evolution tem repositórios públicos com comunidade ativa. Novos devs devem entender a fronteira entre código interno e contribuição pública desde o início.
5. **CLT vs. PJ** — CLT: assinar CTPS, ficha de registro, exame admissional. PJ: contrato de prestação de serviços, dados bancários para NF. Acionar Samara em ambos os casos.

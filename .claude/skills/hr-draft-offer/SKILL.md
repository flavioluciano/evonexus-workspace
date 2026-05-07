---
name: hr-draft-offer
description: Rascunha uma carta/proposta de oferta com detalhes de remuneração e termos. Use quando um candidato está pronto para receber uma oferta, ao montar o pacote de remuneração total (base, equity, bônus de assinatura), ao escrever o texto da proposta, ou ao preparar orientações de negociação para o hiring manager.
argument-hint: "<cargo e nível>"
---

# HR — Draft Offer

Rascunhe uma proposta de oferta completa para um novo colaborador.

## O Que Preciso Saber

- **Cargo e título**: Qual posição?
- **Nível**: Júnior, Pleno, Sênior, Especialista, etc.
- **Localização**: Onde ficará baseado? (afeta remuneração e benefícios)
- **Regime**: CLT ou PJ? (define estrutura da proposta)
- **Remuneração**: Salário base, equity, bônus de assinatura (se aplicável)
- **Data de início**: Quando deve começar?
- **Gestor**: A quem irá reportar?

Se não tiver todos os detalhes, ajudarei a pensar em cada um.

## Output — Regime CLT

```markdown
## Proposta de Oferta: [Cargo] — [Nível] (CLT)

### Pacote de Remuneração
| Componente | Detalhes |
|-----------|---------|
| **Salário Base** | R$ [X]/mês (bruto) |
| **13° Salário** | 1 salário/ano (proporcional no 1° ano) |
| **Férias** | 30 dias + 1/3 constitucional |
| **FGTS** | 8% sobre salário bruto (depositado pelo empregador) |
| **Vale Refeição/Alimentação** | R$ [X]/dia útil |
| **Plano de Saúde** | [Operadora] — cobertura [individual/família] |
| **Vale Transporte / Ajuda de Custo** | R$ [X]/mês |
| **Bônus de Assinatura** | R$ [X] (se aplicável) |
| **Equity / Phantom Shares** | [X]%, vesting [X anos], cliff [X meses] |
| **PLR** | Participação nos Resultados — alvo [X]% do salário anual |
| **Remuneração Total 1° Ano** | R$ [X] (incluindo benefícios estimados) |

### Termos
- **Data de Início:** [Data]
- **Reporta Para:** [Gestor]
- **Localidade:** [Cidade / Remoto / Híbrido]
- **Tipo de Contrato:** CLT — Tempo indeterminado, regime [CLT padrão / teletrabalho]
- **Período de Experiência:** 45 dias + 45 dias (conforme CLT art. 443)
- **Jornada:** 40h semanais / segunda a sexta

### Texto da Proposta

Prezado(a) [Nome do Candidato],

É com grande satisfação que formalizamos nossa proposta para você integrar o time da **Evolution API LTDA** como **[Título do Cargo]**.

**Remuneração e Benefícios:**
Oferecemos salário mensal de **R$ [X]** (bruto), além dos benefícios previstos em lei (férias, 13°, FGTS) e os benefícios complementares descritos no quadro acima.

**Início:** Gostaríamos que você iniciasse em **[Data]**, reportando a **[Gestor]**.

**Próximos passos:**
Caso aceite esta proposta, pedimos que nos retorne até **[prazo — ex: 3 dias úteis]** para iniciarmos os trâmites de admissão. Você receberá a lista de documentos necessários e as instruções para exame admissional.

Estamos muito animados com a perspectiva de ter você no time. Se tiver dúvidas sobre a proposta, estou disponível para conversar.

Atenciosamente,
[Davidson Gomes / Nome do Gestor]
CEO, Evolution API LTDA

---

*Esta proposta tem validade até [data]. Sujeita à aprovação de exame admissional.*

### Notas para o Hiring Manager
- [Orientações de negociação se necessário]
- [Contexto da faixa salarial]
- [Alertas ou considerações especiais]
- [Se candidato negociar: flex em [X], não flex em [Y]]
```

## Output — Regime PJ

```markdown
## Proposta de Prestação de Serviços: [Cargo] — [Nível] (PJ)

### Pacote de Remuneração
| Componente | Detalhes |
|-----------|---------|
| **Valor Mensal (NF)** | R$ [X]/mês |
| **Bônus de Início** | R$ [X] (se aplicável) |
| **Equity / Phantom Shares** | [X]%, vesting [X anos], cliff [X meses] |
| **Hardware Budget** | R$ [X] (aquisição própria, reembolso ou comodato) |
| **Total 1° Ano** | R$ [X] |

### Termos
- **Início:** [Data]
- **Dedicação:** [Full-time / Part-time — ex: 40h/semana]
- **Modalidade:** [Remoto / Híbrido / Presencial]
- **Duração:** [Contrato de [X] meses, renovável / Indeterminado]
- **Nota Fiscal:** Emissão até dia [X] do mês seguinte
- **Pagamento:** Até [X] dias após NF
- **CNPJ:** Prestador deve ter CNPJ ativo (MEI aceito se faturamento compatível)

### Texto da Proposta

Prezado(a) [Nome],

Gostaríamos de formalizar nossa proposta de parceria com você como **[Título]** na Evolution API LTDA.

**Remuneração:** R$ [X]/mês, mediante emissão de nota fiscal.

**Início:** [Data] | **Dedicação:** Full-time (40h/sem) | **Modalidade:** [Remoto]

Para seguir com a contratação, precisaremos dos seus dados PJ (CNPJ, nome fantasia, dados bancários). Nossa equipe financeira ([Samara]) entrará em contato com os próximos passos.

Atenciosamente,
[Davidson Gomes]

### Notas para o Hiring Manager
- [PJ: verificar se faturamento anual do candidato suporta o valor — MEI tem limite de R$ 81k/ano]
- [Risco de vínculo empregatício se contrato PJ tiver subordinação e exclusividade — consultar Thaís]
- [Orientações de negociação]
```

## Integrações Disponíveis

**Notion MCP** (substitui HRIS e ATS):
- Buscar dados da faixa salarial do cargo/nível em databases Notion
- Verificar aprovação de headcount na planning
- Auto-popular detalhes de benefícios da empresa

## Dicas

1. **Inclua a remuneração total** — Candidatos comparam o total, não só o base. Mostre o custo-benefício completo do pacote.
2. **Seja específico com equity** — Tipo (opções, phantom shares, participação direta), percentual, cliff, vesting e valuation de referência.
3. **Personalize** — Mencione algo da entrevista para aquecer o tom. Ex: "Sua experiência com WhatsApp Business API se encaixa perfeitamente no que estamos construindo."
4. **CLT vs. PJ** — Deixe claro o regime antes de detalhar. Confusão gera mal-entendido e retrabalho.
5. **Prazo de validade** — Sempre coloque um prazo. Proposta em aberto indefinidamente gera incerteza para ambos os lados.

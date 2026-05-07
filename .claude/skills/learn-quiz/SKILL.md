---
name: learn-quiz
description: Generate open-ended quiz questions from facts in a specific deck (or all facts). Read-only — does NOT update SM-2 state or review-log. Use when the user says "quiz", "test me", "pratique", "/learn-quiz", or wants to practice without triggering a formal review.
---

# Learn Quiz

Generates open-ended practice questions from facts in `workspace/learning/facts/`. This is a **read-only** exercise — no frontmatter is modified, no log entries are written.

## Trigger

User wants to practice recall without formally reviewing (e.g., "me teste sobre claude-skills", "/learn-quiz", "quiz geral").

## Workflow

### Step 1 — Identify scope

Parse the user's request for a deck name:
- `/learn-quiz {deck-name}` → filter facts where `deck == deck-name`
- `/learn-quiz` (no argument) → use all facts in `workspace/learning/facts/`

If no facts are found for the specified deck:
> "Nenhum fato encontrado no deck '{deck}'. Verifique o nome do deck ou use /learn-stats para ver os decks ativos."

If `workspace/learning/facts/` is empty or doesn't exist:
> "Nenhum fato encontrado. Use /learn-capture para adicionar fatos primeiro."

### Step 2 — Select facts

From the matching facts, select up to 5 to quiz on. Prefer:
1. Facts not recently reviewed (older `next_review`)
2. Random otherwise

### Step 3 — Generate questions

For each selected fact, generate **one open-ended question** derived from the `Retrieval Q` field. You may rephrase the original question slightly for variety, but the answer must still be the `Fact` content.

**Rules for questions:**
- Open-ended only (no multiple choice, no true/false)
- In pt-BR
- Must be answerable from memory without the source text

### Step 4 — Run the quiz interactively

For each question (up to 5):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 Quiz — {deck} | Pergunta {current}/{total}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{question}
```

Wait for the user's answer. Then show:

```
✅ Resposta de referência:
{Fact content}

{Brief feedback: correct elements the user got right, what they missed — 1-2 sentences}
```

Do NOT score formally. This is practice, not review.

### Step 5 — End of quiz

After all questions:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 Quiz concluído! {N} perguntas praticadas.
💡 Para revisão formal com SM-2, use /learn-review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Constraints

- **NEVER modify any file.** This skill is 100% read-only.
- **NEVER write to review-log.jsonl.**
- **NEVER update frontmatter** of any fact file.
- Max 5 questions per session.
- If the user asks to save a score or grade — decline: "O quiz não atualiza o estado SM-2. Use /learn-review para revisão formal."

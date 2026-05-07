---
author: claude
agent: prism-scientist
type: analysis-report
date: {{YYYY-MM-DD}}
topic: {{topic}}
---

# Analysis Report — {{Topic}}

[OBJECTIVE]
{Research objective in 1-2 sentences}

[DATA]
- Source: {{file or system}}
- Shape: {{N rows × M cols}}
- Missing values: {{percentages per relevant col}}
- Date range: {{start - end}}

## Methodology
{Statistical approach + rationale}

[FINDING] {Key insight 1}
[STAT:effect_size] {effect}
[STAT:ci] 95% CI: [{lower}, {upper}]
[STAT:p_value] p = {value}
[STAT:n] n = {sample size}

[FINDING] {Key insight 2}
[STAT:*]

## Visualizations
- `figures/{date}-{topic}-1.png` — {description}
- `figures/{date}-{topic}-2.png` — {description}

[LIMITATION]
- {Caveat 1}
- {Caveat 2}

## Recommendation
{What action this analysis supports}

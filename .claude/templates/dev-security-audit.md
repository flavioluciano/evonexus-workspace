---
author: claude
agent: vault-security
type: security-audit
date: {{YYYY-MM-DD}}
component: {{component-or-module}}
risk-level: HIGH | MEDIUM | LOW
---

# Security Audit — {{Component}}

## Scope
- Files: {{list}}
- Language: {{language}}
- Framework: {{framework + version}}

## Risk Level
**{{HIGH | MEDIUM | LOW}}**

## Summary
- CRITICAL: {{N}}
- HIGH: {{Y}}
- MEDIUM: {{Z}}
- LOW: {{W}}

## Critical Issues

### {{Issue title}}
- **Severity:** CRITICAL
- **OWASP Category:** A0X — {{name}}
- **Location:** `path/to/file.ext:42`
- **Exploitability:** {{trivial / moderate / high}}
- **Blast Radius:** {{single user / all users / system-wide}}
- **Description:** [what's wrong]
- **Remediation:**
```{language}
// Vulnerable code
{{vulnerable snippet}}

// Secure code
{{fixed snippet}}
```

## High / Medium / Low Issues
[same structure]

## Secrets Scan Results
- [ ] No hardcoded API keys
- [ ] No hardcoded passwords
- [ ] No hardcoded tokens
- [ ] No exposed connection strings

## Dependency Audit Results
- Tool: `{{npm audit | pip-audit | cargo audit}}`
- Vulnerabilities found: N
- [list with CVE refs]

## OWASP Top 10 Checklist
- [ ] A01 Broken Access Control
- [ ] A02 Cryptographic Failures
- [ ] A03 Injection
- [ ] A04 Insecure Design
- [ ] A05 Security Misconfiguration
- [ ] A06 Vulnerable Components
- [ ] A07 Authentication Failures
- [ ] A08 Integrity Failures
- [ ] A09 Logging/Monitoring Failures
- [ ] A10 SSRF

## Recommendation
[Prioritized fix order]

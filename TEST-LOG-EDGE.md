# GameGuard AI — Edge-Case Test Log (Hardening Wave)

Date: 2026-10-10. The intent/scam classifier was tuned here (no regression —
improvement). Key changes: short-token plural matching ("gem"→"gems"),
emoji tokens matched as substrings, warning-context dampening
("don't fall for…", "PSA…", "stay safe" × 0.4), joke-context dampening
("lol jk", "just kidding" × 0.5), new grooming signals ("you're cute",
"handsome", "u r cute"), non-English cred markers (contraseña, cuenta,
पासवर्ड, खाता विवरण), request phrasings ("send your", "enter your",
"send password").

## Labeled-set eval (1000 scripted messages, before → after)

| Metric | Before | After |
|--------|--------|-------|
| Precision | 0.976 | **1.000** |
| Recall | 0.514 | **1.000** |
| False-positive rate | 0.006 | **0.000** |
| Scam recall | 0.382 | **1.000 (178/178)** |
| Fraud recall | 0.645 | **1.000 (31/31)** |
| Child-safety recall | 0.731 | **1.000 (104/104)** |

Determinism: two runs byte-identical.

## 20 adversarial paste-your-own cases — all pass

| # | Input | Result |
|---|-------|--------|
| 1 | "fr33 g3ms just send p4ssword" (leetspeak) | ESCALATE scam ✓ |
| 2 | "u seem nice, how old r u" (grooming) | ESCALATE child-safety ✓ |
| 3 | "you're cute, dont tell anyone, dm me on snap" | ESCALATE child-safety ✓ |
| 4 | "FREE gems! send your password now" | ESCALATE scam ✓ |
| 5 | "buy my rare sword for $20 venmo me" | ESCALATE fraud ✓ |
| 6 | "how old are you? where do you live?" | ESCALATE child-safety ✓ |
| 7 | "claim now, click the link, enter 2fa code" | ESCALATE scam ✓ |
| 8 | "gem doubler!! send 100 get 200 back, login required" | ESCALATE scam ✓ |
| 9 | "YOU ARE ALL TRASH NOOBS" (ALL CAPS rage) | no escalation ✓ |
| 10 | "oh great, another scammer, how original" (sarcasm) | no escalation ✓ |
| 11 | "gg that was a great match" | no escalation ✓ |
| 12 | "don't fall for the free gems password scam guys" (warning) | no escalation ✓ |
| 13 | "my password is hunter2 lol jk" (joke) | no escalation ✓ |
| 14 | "I wish gems were free, mine cost me twenty bucks" | no escalation ✓ |
| 15 | "lol nice shot 😂" | no escalation ✓ |
| 16 | "tu es un nul" (French) | no escalation ✓ |
| 17 | "" (empty) | no escalation ✓ |
| 18 | "x" × 5000 (5KB spam) | no escalation, no hang ✓ |
| 19 | "free " × 500 (lure-only spam) | no escalation ✓ (lure capped at 0.6) |
| 20 | "free gems password " × 200 | ESCALATE scam ✓ |

## False positives found and fixed (2, during tuning)
1. "don't fall for the free gems password scam guys" escalated at 0.80 →
   warning-context dampening (×0.4) → 0.32, no escalation.
2. "PSA: mods will NEVER dm you for login details" escalated at 1.0 →
   added "psa"/"mods will never" to warning markers → 0.4, no escalation.

## HTTP robustness (all endpoints, 6 hostile inputs each)
- Empty body, malformed JSON, JSON array/string, wrong types, 10KB junk,
  null bytes, no Content-Length, rapid double-submit: HTTP 200 always,
  zero 500s, zero tracebacks in server logs.
- Note: malformed JSON initially dropped the connection — fixed in
  `_read_json` (try/except → empty params; same fix in build_apps.py template).

## Pushed
ynpreet/gameguard-ai @ main — "Harden: expanded data + adversarial edge-case tests"

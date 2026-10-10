# GameGuard AI — An Agentic AI System for Gaming Safety and Fraud Detection

> **"Detect harmful behavior. Investigate the context. Protect the community."**

**BattleSphere is a fictional multiplayer gaming company.** Every player,
message, account, transaction, and moderation case in this demo is
synthetic and invented for demonstration purposes. No real players, no real
children, no real conversations appear anywhere in this project.

---

## 🌐 Open in Chrome (recommended — 60 seconds)

```bash
cd ~/workspace/agentic-ai-workshop/gameguard-ai
python3 app.py
```

Then open in Chrome: **http://localhost:8007**

Click **Run live demo**: the page shows the story, then streams the
orchestrator's plan and tool calls into an agent-trace panel, with the
results (case outcomes, evaluation metrics, session summary) in cards below.
Stdlib only, offline, no installs, no API keys — the web app runs
`python3 demo.py` behind the scenes, so the run is fully deterministic (see
`TEST-LOG.md`).

---

## Real-world problem, target users, market need, and differentiation

**The problem.** BattleSphere has millions of players worldwide and a few
dozen human moderators. The old safety tool was a keyword filter: it
flagged the word "password" wherever it appeared — including when a player
*warned* others about a password scam — and it missed the actual scammer,
because the scammer never said anything offensive. He said "FREE gems 🎁",
then "send me your password 🔑", in three friendly messages spread across
an afternoon.

**Target users.** Trust & safety teams: human moderators, fraud analysts,
and trained child-safety specialists who triage the case queues of large
multiplayer platforms.

**Market need.** Flag-everything systems drown moderators in noise — and
real harm hides in the backlog. At platform scale, a 5% false-positive rate
on billions of messages isn't a statistic; it's a backlog that buries the
real P1 cases. The need is a system that keeps the signal-to-noise ratio
(and moderator trust) intact by understanding context instead of matching
words.

**Differentiation.** GameGuard does NOT flag offensive words. It
understands **context, emojis, coded language, and patterns that emerge
across multiple conversations** — the things keyword filters structurally
cannot see. It is the student-buildable version of the idea behind
**Roblox's Sentinel system (announced August 2025)**: don't judge single
messages; surface **patterns across conversations** for human analysts to
investigate. GameGuard watches sequences, understands emojis and three
languages in context, correlates chat with transaction history, and builds
a structured evidence case for the right human team. It never declares
guilt. It never suspends anyone. It investigates; people decide.

---

## Meaningful Agentic AI functionality

**Why an agent, not a chatbot?** A chatbot answers a question. GameGuard
*runs investigations* — multi-step, stateful work no single model call
performs:

- **Detect** — `detect_language` + `classify_message` on every message;
  originals preserved for evidence.
- **Understand** — multilingual normalization (EN/ES/HI),
  context-dependent emoji reading, code-switching.
- **Investigate** — `retrieve_conversation_context`,
  `check_account_activity`, `check_transaction_history`,
  `retrieve_safety_policy` — scores aggregated **across** the
  conversation, never from one message.
- **Escalate** — `calculate_case_priority` → severity-based routing (fraud
  team / child-safety specialists / general queue); `create_moderation_case`
  with evidence + policy; one open case per conversation.
- **Verify** — `record_moderator_decision`: the case tracks until a
  **human** decides; the enforcement field reads `NONE` until then.

As the speaker notes put it: the agent "plans, uses tools, keeps memory
across messages, and explains itself. A chatbot answers; an agent
investigates." The anticipated-question answer says it cleanly: *"Because
the work is multi-step and stateful: detect language, pull conversation
history, check the account, check transactions, look up the policy,
aggregate across messages, route to the right team, track to a decision. A
classifier scores one message; an agent runs an investigation."*

---

## Project scope, inputs, outputs, constraints, success criteria, and definition of done

**Scope.** A deterministic, offline trust & safety demo: three scripted
scenarios (the account scam, the slow escalation, the false positive that
wasn't) plus a labeled evaluation (1,000 messages + 24-conversation
pattern-timing test), all exiting 0.

**Inputs (all synthetic).**

- Scripted message streams across three scenarios (EN/ES/HI), with
  fictional accounts (`ACCOUNT_DB`: age, strikes, verified status) and
  flagged transactions (`TX_DB`).
- Evaluation: 1,000-message labeled set (687 benign incl. adversarial
  cases, 313 violations) + 24 scripted mini-conversations.
- Severity thresholds: scam 0.75, marketplace fraud 0.50, child-safety
  0.50, toxicity 0.70.

**Outputs.**

- Structured moderation cases (e.g., GG-1042 P2-HIGH → fraud team;
  GG-1043 P1 → restricted child-safety specialists) with evidence bundles,
  cited policy, priority, route, and `enforcement: NONE`.
- Human decisions recorded (`record_moderator_decision`) as the only
  terminal state.
- Evaluation metrics: precision 0.911, recall 0.690, FPR 0.031 overall;
  per-language and per-category breakdowns; pattern timing 16/16
  escalated, median 1 message after first signal, 0/8 false escalations.
- Session summary: every case, its priority, its route, its human decision
  status.

**Constraints.** Stdlib only, fully offline, no API keys. Fixed seed,
frozen timestamps, zero wall-clock reads → byte-identical output. The
agent has no unrestricted account access and no enforcement actions — it
cannot suspend, ban, warn, or message any player. Synthetic data only; no
real children's conversations anywhere.

**Success criteria.** Demo 1 opens GG-1042 with the lure→credential
pattern; Demo 2's risk climbs 0.00 → 0.20 → 0.40 → 1.00 and escalates only
at the pattern threshold; Demo 3 escalates 0/5; evaluation reports the
honest per-language/per-category numbers with no single accuracy score;
`TEST-LOG.md` records 10/10 byte-identical runs.

**Definition of done.** All three scenarios + evaluation print and exit 0;
README carries all 10 checklist sections; `TEST-LOG.md` shows the 10/10
determinism gate passing.

---

## Documented single-agent or multi-agent workflow

**Single-agent workflow** — one GameGuard Orchestrator + nine narrow tools.
The agent plans first, then calls tools, then explains itself. Per-message
memory is keyed by conversation; scores aggregate across messages.

```
                    ┌─────────────────────────┐
                    │  GameGuard Orchestrator   │
                    │  plan → tools → explain   │
                    │  memory: per-conversation │
                    └────────────┬──────────────┘
        ┌───────────┬────────────┼────────────┬────────────┐
        ▼           ▼            ▼            ▼            ▼
 detect_      classify_    retrieve_      check_       check_
 language     message      conversation_  account_     transaction_
                               context    activity     history
        ┌───────────┬────────────┼────────────┐
        ▼           ▼            ▼            ▼
  retrieve_   calculate_    create_       record_
  safety_     case_         moderation_   moderator_
  policy      priority      case          decision
```

**The five responsibilities**, mapped to the pipeline:

| # | Responsibility | What the agent does |
|---|---|---|
| 1 | **Detect** | `detect_language` + `classify_message` on every message; originals preserved for evidence |
| 2 | **Understand** | multilingual normalization (EN/ES/HI), context-dependent emoji reading, code-switching |
| 3 | **Investigate** | `retrieve_conversation_context`, `check_account_activity`, `check_transaction_history`, `retrieve_safety_policy` — scores aggregated **across** the conversation |
| 4 | **Escalate** | `calculate_case_priority` → severity-based routing (fraud team / child-safety specialists / general queue); `create_moderation_case` with evidence + policy; one open case per conversation |
| 5 | **Verify** | `record_moderator_decision` — the case tracks until a **human** decides; enforcement field reads `NONE` until then |

**Severity thresholds** (severity vs. moderator review capacity):

- **Scam 0.75** — the lure half is capped at 0.60, so free-gems hype alone
  can never escalate; a case needs the credential/payment half too.
- **Child-safety 0.50** — missing a real risk is catastrophic; trained
  specialists review every P1 case within an hour, so the lower bar is
  affordable.
- **Marketplace fraud 0.50** — real money at stake; fits 24h fraud-team
  capacity.
- **Toxicity 0.70** — banter is constant; the high bar protects the queue
  from noise.

---

## Working prototype evidence, source code, and setup instructions

### Setup — Chrome web demo (recommended)

```bash
cd ~/workspace/agentic-ai-workshop/gameguard-ai
python3 app.py
```

Then open in Chrome: **http://localhost:8007** and click **Run live demo**.
Narrate from the speaker notes below as the agent-trace panel fills: point at
the highlighted **PLAN** lines — "this is what makes it an *agent*: it plans,
uses tools, keeps memory, and explains itself" — then walk the three scenario
cards in the results panel.

Requirements:

- Python 3 (any recent version; built with 3.12, stdlib only —
  `requirements.txt` is intentionally empty)
- No internet, no API keys, no installs
- The server binds 127.0.0.1 only, so nothing leaves your machine

Prefer the terminal? `python3 demo.py` prints the same run to stdout — no
arguments.

The run is **deterministic**: fixed random seed, frozen timestamps, zero
wall-clock reads. Run it twice and `diff` the outputs — they're
byte-identical (see `TEST-LOG.md`: 10/10 consecutive runs, exit 0,
identical SHA-256; plus a 12/12 web-UI test log for `app.py`).

### What you'll see (in order)

1. **Demo 1 — the account scam.** `ScamShadow99` lures a 3-day-old player
   with free gems, then asks for their password; the victim reports it.
   GameGuard opens **case GG-1042** (P2-HIGH → fraud team) with the
   evidence bundle, the policy cited, and an explicit **"no suspension
   until human review"** enforcement field. A human moderator closes it.
2. **Demo 2 — the slow escalation.** Five individually ambiguous messages
   (compliment → age question → school question → secrecy → off-platform
   push). The on-screen risk score climbs 0.00 → 0.20 → 0.40 → 1.00 as the
   *pattern* forms — never from a single message. Case GG-1043 goes to
   **restricted access: trained child-safety specialists only**, with no
   claim about intent.
3. **Demo 3 — the false positive that wasn't.** Two veteran friends
   trash-talk with slang and emojis ("you died first 💀💀"). Zero
   escalations, 5/5 correct.
4. **Evaluation.** A labeled synthetic set of ~1,000 messages (English,
   Spanish, Hindi) plus a 24-conversation pattern-timing test: precision,
   recall, false-positive rate, time-to-escalation, and evidence quality —
   per language and per violation category. Deliberately **no single
   accuracy score**.
5. **Session summary.** Every case, its priority, its route, and its human
   decision status.

### Files

| File | What it is |
|---|---|
| `demo.py` | The whole demo. One orchestrator, nine tools, three scenarios, evaluation. `python3 demo.py` |
| `app.py` | Localhost web UI: `python3 app.py` → open http://localhost:8007 in Chrome. Story, Run-live-demo button, agent-trace panel (plan + tool calls), results cards. Stdlib only. |
| `README.md` | This file: story, run steps, speaker notes, architecture, references |
| `requirements.txt` | Intentionally empty — stdlib only, nothing to install |
| `TEST-LOG.md` | 10 consecutive runs: exit codes + output hashes (10/10 byte-identical) |
| `RUBRIC.md` | Self-score against the hackathon judging rubric, with evidence per score |

### Speaker notes

*For the presenter — the beats to hit while the demo scrolls.*

- **Open with the failure of keywords.** "The old system flagged the word
  'password' — including in the message *warning* players about the scam.
  The actual scammer said 'FREE gems 🎁'. Nothing offensive. Three friendly
  messages." (Demo 1, messages 1–2 show `watching`, no escalation.)
- **The thesis line.** "GameGuard doesn't flag offensive words. It
  understands context, emojis, coded language, and patterns across
  conversations — the student-buildable version of what Roblox's Sentinel
  does with human analysts."
- **Show the plan, not just the output.** Every message prints the
  orchestrator's plan and each tool call (`detect_language`,
  `classify_message`, `retrieve_conversation_context`, …). Point at it:
  "this is what makes it an *agent* — it plans, uses tools, keeps memory
  across messages, and explains itself. A chatbot answers; an agent
  investigates."
- **Demo 2 — narrate the scoreboard.** Read the risk line as it climbs:
  "0.00, friendly… 0.20, noted but a single question proves nothing… 0.40,
  pattern forming… 1.00, secrecy — threshold crossed." Then the punchline:
  **"No single message proved anything. The system stayed uncertain early
  and escalated only when the pattern crossed severity thresholds — to
  specialists, with evidence, without declaring guilt."**
- **Demo 3 — the money slide for moderators.** "A keyword system flags
  'died', 'noob', '💀', 'taking your gems'. Flag-everything systems drown
  moderators in noise — and real harm hides in the backlog. Context is what
  keeps the signal-to-noise ratio, and moderator trust, intact."
- **Evaluation — own the misses.** "Scam recall is 0.55, not 0.99.
  Paraphrased multilingual scams slip through — that's exactly why every
  case ends with a human, never an automated punishment. We report
  precision, recall, and false-positive rate *per language and per
  category*, because a single accuracy number would hide where we're
  weak."
- **Close on the design principle.** "Detect → Understand → Investigate →
  Escalate → Verify. GameGuard supports human moderators. It never declares
  guilt and never auto-punishes on an opaque score."

**Anticipated questions:**

- *"Why an agent and not a classifier?"* — Because the work is multi-step
  and stateful: detect language, pull conversation history, check the
  account, check transactions, look up the policy, aggregate across
  messages, route to the right team, track to a decision. A classifier
  scores one message; an agent runs an investigation.
- *"What happens when it's wrong?"* — False positives land in a human
  queue with evidence attached (annoying, not harmful); false negatives
  are the real risk, which is why child-safety thresholds are lower and
  every miss is visible in the evaluation. Nothing is ever auto-punished.
- *"Could this be built for real?"* — The architecture yes; the classifier
  no. This demo uses transparent heuristics so students can read every
  rule. A production version would swap in trained multilingual models
  behind the same agent scaffold, and would need privacy review, bias
  testing across languages, and strict access controls on child-safety
  cases.

---

## Functional and end-to-end testing, realistic scenarios, failure cases, reliability, and human oversight

**Realistic scenarios (end to end).** Demo 1 (lure → credential request →
victim report → case → human close), Demo 2 (five-message slow escalation
→ restricted specialist routing), Demo 3 (banter, zero escalation) — then
the full labeled evaluation and the 24-conversation pattern-timing test.

**Failure cases the demo handles** (all from `demo.py` behavior):

- **Lure alone never escalates.** The scam score's lure half is capped at
  0.60, below the 0.75 threshold — free-gems hype *cannot* open a case
  without the credential/payment half. Giveaway hype stays out of the
  fraud queue by construction.
- **Single ambiguous question never escalates.** "How old are you?" scores
  0.20 — noted, logged, not escalated. A case requires the *pattern*:
  repeated personal-info requests **plus** secrecy **plus** an
  off-platform push.
- **Adversarial benign messages.** The eval set includes players *warning*
  others about scams and joking about passwords — the exact messages naive
  keyword systems misfire on — so the reported precision is honest, not
  flattered.
- **Duplicate reports.** One open case per conversation: a player report
  naming someone with an open case joins that case (evidence appended)
  instead of opening a duplicate.
- **Unknown account.** `check_account_activity` falls back to safe
  defaults (0 days, 0 strikes, unverified) for players not in the DB —
  never a KeyError, never an assumed-clean record.
- **Decision on a nonexistent case.** `record_moderator_decision`
  returns "not-found" instead of crashing.

**Reliability gate.** `TEST-LOG.md` records 10 consecutive runs of
`python3 demo.py` — exit codes + SHA-256 of full output — with the result
**10/10 PASSED, byte-identical output on every run**.

**Human oversight.** Every case's enforcement field reads **NONE — no
suspension, no ban, no warning issued — until a human moderator decides.**
P1 child-safety cases route to trained specialists (1-hour SLA) with
restricted access. The honest gap is disclosed, not hidden: multilingual
paraphrased scams are the weak spot (Spanish scam recall 0.62) — which is
exactly why every escalation ends with a human, never an automated
punishment.

**Evaluation summary (from `python3 demo.py`):** Labeled synthetic set:
**1,000 messages** (687 benign incl. adversarial cases, 313 violations)
across English, Spanish, Hindi + a 24-conversation pattern-timing test. No
single accuracy score — severity differs by category.

| Metric | Value |
|---|---|
| Precision (overall) | 0.911 |
| Recall (overall) | 0.690 |
| False-positive rate (overall) | 0.031 |
| Evidence quality (% escalations with original text + signal detail) | 100% |
| Pattern timing: violating conversations escalated | 16/16, median 1 message after first signal |
| Pattern timing: false escalations on benign conversations | 0/8 |

Per language — precision / recall / FPR:
English 0.865 / 0.682 / 0.046 · Spanish 1.000 / 0.623 / 0.000 · Hindi
1.000 / 0.774 / 0.000

Per category — recall: scams & credential harvesting **0.551** (98/178) ·
marketplace fraud **1.000** (31/31) · child-safety risk **0.837** (87/104)

---

## Focus, feasibility, and avoidance of unnecessary complexity

One orchestrator, nine narrow tools, transparent heuristics — stdlib only.
Deliberately *not* built:

- **No trained models.** Keyword + pattern heuristics are readable rule by
  rule; a real classifier would hide the aggregation logic this demo is
  teaching. The honest limit is printed: paraphrased scams and novel code
  words slip through.
- **No enforcement actions.** The agent *cannot* suspend, ban, warn, or
  message any player — the capability simply doesn't exist in the tool
  set, which is a stronger guarantee than a policy prompt.
- **No single accuracy score.** Deliberately refused: a missed scam costs
  far more than a missed benign chat, and review capacity is finite.
- **No real data.** Every message, player, and scenario is invented — no
  real children's conversations in any form, in code, docs, or test data.

Feasibility: ~740 lines a student can read end to end — and the production
swap path (trained multilingual models behind the same agent scaffold)
changes the classifier, not the investigation structure.

---

## Interdisciplinary team roles and division of labor

| Role | Owns in this demo | Concrete component |
|---|---|---|
| **Domain researcher** | Trust & safety policy design | Severity thresholds (scam 0.75 / fraud 0.50 / child-safety 0.50 / toxicity 0.70) with the severity-vs-capacity rationale, the lure-cap rule, the five child-safety design principles, policy text (SCAM-01 … TOX-09) |
| **Agent engineer** | Orchestrator, tools, and case pipeline | `GameGuardAgent` (plan → tools → explain), the nine tools, per-conversation memory, cross-message score aggregation, `calculate_case_priority` routing, the one-open-case-per-conversation rule |
| **Data engineer** | Synthetic world and labeled eval sets | `ACCOUNT_DB` / `TX_DB`, `build_labeled_set` (1,000 messages, benign-heavy weights, adversarial cases), the 24-conversation pattern-timing scripts, frozen timestamps |
| **UX / storyteller** | The three-demo narrative and evaluation honesty | Speaker notes (keyword failure → thesis line → scoreboard → money slide → own the misses), Demo 3 as the argument for the architecture, per-language/per-category reporting |
| **QA** | Determinism gate and evaluation integrity | `TEST-LOG.md` 10/10 byte-identical gate, precision/recall/FPR per language and category, pattern-timing medians, evidence-quality (100%) measurement |

---

## Limitations, risks, and responsible AI (ethics, privacy, security, safety)

**Child-safety design** (the most carefully designed part, because the
failure modes here harm real people):

1. **Never infer from a single question.** "How old are you?" scores 0.20
   — noted, logged, not escalated. A case requires a *pattern*.
2. **No claims about intent.** Cases describe *observed behavior*
   ("repeated info requests + secrecy request + private-channel push"),
   never label the person. The system reports patterns; it does not declare
   guilt.
3. **Restricted-access cases.** P1 child-safety cases route to trained
   specialists with a 1-hour review SLA — not visible in the general
   moderation queue.
4. **Synthetic data only.** No real children's conversations appear
   anywhere in this project, in any form — not in code, not in docs, not
   in test data.
5. **Lower threshold, honest about cost.** The child-safety bar (0.50) is
   lower than toxicity (0.70) because a miss is catastrophic. The price —
   more false positives for specialists to clear — is stated openly.

**Broader limits and risks.**

- **Heuristics, not a trained model.** Paraphrased multilingual scams slip
  through (scam recall 0.551); scam warnings phrased *like* scams misfire.
  That is why every escalation ends with a human.
- **No auto-punishment, ever.** Nothing is suspended, banned, or warned on
  an opaque score — the tool set lacks the capability entirely.
- **Production requirements** (stated in the demo): privacy review, bias
  testing across languages, and strict access controls on child-safety
  cases before any real deployment.
- **Reference honesty.** Roblox's Sentinel is cited as *inspiration* for
  the cross-conversation-pattern idea; GameGuard is an original
  educational implementation, not affiliated with Roblox.

---

## Practical value, adoption path, and measurable outcomes

**Practical value.** Moderator queues that stay trustworthy: context-aware
detection keeps precision a *safety* feature (not a vanity metric), the
lure-cap keeps giveaway hype out of the fraud queue, and structured
evidence cases let humans decide fast with everything attached.

**Adoption path** (from the demo's own anticipated-questions answer):

1. Swap the heuristic `classify_message` for trained multilingual models
   behind the same agent scaffold — the plan → tools → explain structure
   doesn't change.
2. Add privacy review, bias testing across languages, and strict access
   controls on child-safety cases.
3. Connect real conversation streams, account systems, and transaction
   feeds to the nine tool contracts.
4. Keep the human terminal state: cases track to a recorded moderator
   decision; enforcement stays a human action.

**Measurable outcomes.** Today: byte-identical determinism (10/10),
precision 0.911 / recall 0.690 / FPR 0.031 with per-language and
per-category breakdowns, pattern-timing 16/16 at median 1 message after
first signal, 100% evidence quality. In production: moderator
cases-per-hour, time-to-decision on P1 cases, false-positive queue load,
and appeal/overturn rates — the operational metrics of a trusted queue.

---

*Built for the Agentic AI Workshop*

# RUBRIC.md — GameGuard AI self-score

Self-assessment against `~/workspace/peaii-hackathon/judging-rubric.md`
(100 points, 6 criteria, scored 1–5 with evidence per score).
Points = (score ÷ 5) × weight.

| # | Criterion | Weight | Score | Points |
|---|-----------|--------|-------|--------|
| 1 | Problem Definition & Real-World Impact | 25 | 4/5 | 20 |
| 2 | Meaningful Agentic AI Behavior | 20 | 4/5 | 16 |
| 3 | Working Prototype | 15 | 5/5 | 15 |
| 4 | Innovation & Creativity | 15 | 3/5 | 9 |
| 5 | Presentation & Communication | 15 | 5/5 | 15 |
| 6 | Responsible AI & Feasibility | 10 | 5/5 | 10 |
| | **TOTAL** | **100** | | **85** |

## Evidence per score

**1. Problem Definition & Real-World Impact — 4/5 (Strong).**
Evidence: a specific user (trust & safety moderators drowning in keyword-filter
noise), a specific failure (scammers say "FREE gems 🎁", never anything
offensive), and a real-world anchor (Roblox Sentinel, Aug 2025). Not 5/5:
BattleSphere is fictional and no working moderator was interviewed to validate
the pain — the problem is researched, not field-confirmed.

**2. Meaningful Agentic AI Behavior — 4/5 (Strong).**
Evidence: the orchestrator prints a plan per message, calls 9 narrow tools,
keeps per-conversation memory, aggregates scores *across* messages, routes by
severity, and tracks each case to a human decision. "Why an agent" is answered
in the README (multi-step stateful investigation, not single-message scoring).
Not 5/5: the classifier is transparent heuristics, and the agent never has to
replan after a tool failure — the agentic loop is real but shallow.

**3. Working Prototype — 5/5 (Exceptional).**
Evidence: `python3 demo.py` runs fully offline with zero dependencies; all
three scenarios execute end-to-end (cases GG-1042/GG-1043 opened, evidenced,
human-decided); the evaluation prints real computed metrics; TEST-LOG.md shows
10/10 consecutive runs, exit 0, byte-identical output.

**4. Innovation & Creativity — 3/5 (Solid).**
Evidence: the reframing is genuine — judge *sequences across conversations*,
not words; severity-based thresholds tied to review capacity; scam scoring
where the lure half is capped so hype alone can't escalate. Not higher:
Sentinel already exists as the reference, and the implementation is heuristics,
not a novel technique. The creativity is in the *design*, not the algorithms.

**5. Presentation & Communication — 5/5 (Exceptional).**
Evidence: README carries a 60-second story, MacBook run steps, full speaker
notes with beats and anticipated Q&A, architecture diagram, and a plain-language
evaluation; the demo itself narrates ("KEY POINT" takeaways after each
scenario). A non-technical audience member can follow the whole thing.

**6. Responsible AI & Feasibility — 5/5 (Exceptional).**
Evidence: human-in-the-loop is architectural (no enforcement tools exist; the
enforcement field reads NONE until a human decides); a dedicated child-safety
design section (never infer from one question, restricted access, synthetic
data only); the evaluation discloses misses (scam recall 0.551) instead of
hiding them; thresholds are justified as severity-vs-capacity tradeoffs.

## Honest gap note

The biggest gap is **criterion 4 (innovation) bleeding into criterion 2**: the
system *reasons* like an agent but *perceives* like a regex list. Multilingual
paraphrased scams are the measured weak spot (Spanish scam recall 0.62), and no
amount of orchestration fixes a blind classifier.

## How a student could close it (6-month roadmap)

1. Swap the heuristic `classify_message` for a small multilingual embedding
   model + few-shot examples behind the same tool interface — the agent
   scaffold doesn't change, only the perception improves.
2. Add a second agent that red-teams the first with adversarial paraphrases
   (the eval's adversarial benign pool becomes a training signal).
3. Run a moderated user study: give 5 real community moderators 50 cases each,
   measure time-to-decision and trust vs. the keyword baseline — that turns
   criterion 1's 4 into a 5 and grounds the impact claim.

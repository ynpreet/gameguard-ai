# TEST-LOG.md — GameGuard AI determinism verification

**Date:** 2026-10-10
**Command:** `python3 demo.py` (run from `~/workspace/agentic-ai-workshop/gameguard-ai/`)
**Requirement:** 10 consecutive runs, every run exit code 0, every run byte-identical output.
**How determinism is achieved:** fixed `random.Random(20261010)` seed; frozen logical
timestamps (`2026-10-10T…`, no wall-clock reads); no network, no API keys, stdlib only.

| Run | Exit code | SHA-256 of stdout | Match |
|-----|-----------|-------------------|-------|
| 1 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | baseline |
| 2 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |
| 3 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |
| 4 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |
| 5 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |
| 6 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |
| 7 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |
| 8 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |
| 9 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |
| 10 | 0 | `02ef4b7138507231df4c02d0e55abee8d362aaf85f36e6678210b1efc3756bd3` | ✅ identical |

**Result: 10/10 PASS** — all runs exit 0, all outputs byte-identical.

**Flakiness found and fixed during development:**
1. `KeyError: 'text'` — message records store the key `original`, not `text`; fixed the history lookup.
2. Duplicate cases per conversation — added one-open-case-per-conversation dedup (player reports to `MOD-REPORT` naming an open-case player join that case instead of opening a new one).
3. `moderator: moderator:` double prefix in the verification line — fixed the call-site argument.
4. Pattern-timing evaluation printed ~100 extra orchestrator plans — added a quiet mode (`verbose=False`) for bulk eval runs.

---

## Web UI test log — `app.py` localhost Chrome demo (added 2026-10-10)

**What was built:** `app.py` (new file, this folder) — stdlib-only `http.server`
web UI. `python3 app.py` binds 127.0.0.1:**8007**, prints
`Open in Chrome: http://localhost:8007`, and serves a single-page app (inline
CSS/JS, no external assets): header + story, **Run live demo** button,
agent-trace panel (orchestrator PLAN highlighted gold, 9 tool calls in teal),
results panel (per-demo outcome cards, evaluation metrics, session summary).
`GET /` → the page; `GET /api/run` → runs `python3 demo.py` in a subprocess
and returns `{"ok": true, "output": "..."}`. `demo.py` itself was NOT modified
(output markers and behavior verified unchanged). Port-in-use is caught and
reported with a clear error + remediation hint (exit 1); verified by starting a
second instance against a live server.

**Test protocol (12 rounds), each round:** (a) `python3 demo.py` → exit 0;
(b) start `app.py` on 8007 → `GET /` → HTTP 200, page contains "GameGuard AI",
"Run live demo", trace panel; `GET /api/run` → HTTP 200, `{"ok": true}`,
output 30,641 chars, all stable markers present (`ScamShadow99`, `GG-1042`,
`GG-1043`, `SESSION SUMMARY`, `[tool] detect_language` ×15,
`GameGuard Orchestrator PLAN` ×15, `>>> OUTCOME` ×3, `DEMO 1`, `precision:`);
kill server, confirm port freed.

| Round | demo.py exit | GET / | GET /api/run (markers) | Verdict |
|-------|--------------|-------|------------------------|---------|
| 1–12 | 0 (all) | 200 (all) | 200, `ok:true`, all markers (all) | ✅ PASS |

**Result: 12/12 PASS.** Output length identical every round (30,641 chars —
demo.py is deterministic, see determinism log above). JS syntax validated with
`node --check`; the results-panel extraction logic (plan/tool-line
classification, per-demo outcome slices, session summary) was unit-tested in
node against real demo output: 15 plans, 87 tool calls, 105 plan steps all
classified correctly.

**Flakiness found and fixed during development:**
1. Python 3.12 `SyntaxError: invalid escape sequence` in the embedded JS
   (regex `\[` inside a non-raw triple-quoted string) — made the page template
   a raw string and normalized the `\\n`/`\\u` escapes inside it.
2. Shell test-harness flakiness: `cd dir && cmd &` backgrounds the `cd` too
   (server B port-in-use test ran in the wrong cwd), and `kill` on the server
   PID took down the whole exec session via job control — rewrote the harness
   in Python using `subprocess.Popen` + `urllib`, which is stable.
3. `/tmp` wipe risk (per AGENTS.md lesson): test harness kept in `/tmp` only
   for the run; the durable record is this log entry.

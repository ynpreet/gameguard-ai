#!/usr/bin/env python3
"""
GameGuard AI — localhost web UI
================================
Run this and open the printed URL in Google Chrome:

    python3 app.py
    # Open in Chrome: http://localhost:8007

Stdlib only (http.server + subprocess + json). No Flask, no Streamlit, no pip,
no internet, no API keys. The demo itself is executed by running demo.py in a
subprocess, so demo.py's behavior is untouched.
"""

import errno
import http.server
import json
import os
import subprocess
import sys

HOST = "127.0.0.1"
PORT = 8007
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GameGuard AI — Live Demo</title>
<style>
  :root{
    --bg:#0e1116; --panel:#161b22; --panel2:#1c232e; --line:#2b3442;
    --ink:#e8edf3; --muted:#9aa4b2; --accent:#58a6ff; --gold:#e3b341;
    --green:#3fb950; --teal:#39c5cf; --red:#f85149; --violet:#bc8cff;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       line-height:1.55}
  .wrap{max-width:1100px;margin:0 auto;padding:0 20px 60px}
  header.hero{padding:38px 0 18px;border-bottom:1px solid var(--line)}
  header.hero h1{margin:0;font-size:2rem;letter-spacing:-0.5px}
  header.hero h1 .gg{color:var(--gold)}
  header.hero p.tag{margin:8px 0 0;color:var(--muted);font-size:1.02rem}
  .badge{display:inline-block;margin-top:10px;padding:3px 10px;border:1px solid var(--line);
         border-radius:999px;font-size:.78rem;color:var(--muted);background:var(--panel)}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;
        padding:20px 22px;margin-top:20px}
  .card h2{margin:0 0 8px;font-size:1.12rem;color:var(--accent)}
  .story p{margin:.55em 0;color:#cdd6e0}
  .story strong{color:var(--gold)}
  .controls{display:flex;align-items:center;gap:14px;margin-top:20px}
  button#run{background:var(--gold);border:0;color:#1a1405;font-weight:700;font-size:1rem;
             padding:12px 26px;border-radius:8px;cursor:pointer}
  button#run:hover:not(:disabled){filter:brightness(1.08)}
  button#run:disabled{opacity:.55;cursor:default}
  .spinner{display:none;width:22px;height:22px;border:3px solid var(--line);
           border-top:3px solid var(--gold);border-radius:50%;animation:spin .8s linear infinite}
  @keyframes spin{to{transform:rotate(360deg)}}
  .status{color:var(--muted);font-size:.92rem;min-height:1.4em}
  .panels{display:none;margin-top:22px}
  .panels.show{display:block}
  .trace{max-height:520px;overflow:auto;background:#0b0e12;border:1px solid var(--line);
         border-radius:8px;padding:14px 16px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
         font-size:.82rem;line-height:1.6;white-space:pre-wrap;word-break:break-word}
  .ln{padding:1px 6px;border-radius:4px}
  .ln.plan{background:rgba(227,179,65,.13);border-left:3px solid var(--gold);
           color:#f4e3b2;font-weight:600;margin:8px 0 2px}
  .ln.pstep{color:#cdb877;padding-left:26px}
  .ln.tool{color:var(--teal)}
  .ln.sep{color:var(--violet);font-weight:600}
  .ln.key{color:var(--green);font-weight:600}
  .ln.warn{color:var(--red)}
  .resgrid{display:grid;grid-template-columns:1fr;gap:14px;margin-top:14px}
  @media(min-width:860px){.resgrid{grid-template-columns:1fr 1fr}}
  .res{background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
  .res h3{margin:0 0 6px;font-size:.98rem;color:var(--accent)}
  .res pre{margin:0;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.8rem;
           white-space:pre-wrap;word-break:break-word;color:#cdd6e0}
  .res .hl{color:var(--gold);font-weight:600}
  footer{margin-top:30px;color:var(--muted);font-size:.82rem;border-top:1px solid var(--line);padding-top:14px}
  kbd{background:var(--panel2);border:1px solid var(--line);border-radius:4px;padding:1px 6px;font-size:.85em}
</style>
</head>
<body>
<div class="wrap">

<header class="hero">
  <h1><span class="gg">GameGuard AI</span> &mdash; live demo</h1>
  <p class="tag">&ldquo;Detect harmful behavior. Investigate the context. Protect the community.&rdquo;</p>
  <span class="badge">BattleSphere is a fictional gaming company &mdash; all players, messages and cases are synthetic</span>
</header>

<section class="card story">
  <h2>The story (60 seconds)</h2>
  <p>BattleSphere has millions of players and a few dozen human moderators. The old safety
  tool was a keyword filter: it flagged the word &ldquo;password&rdquo; wherever it appeared
  &mdash; including in the message <em>warning</em> others about a password scam &mdash; and it missed
  the actual scammer, because he never said anything offensive. He said <strong>&ldquo;FREE gems&quot;</strong>,
  then <strong>&ldquo;send me your password&quot;</strong>, in three friendly messages spread across an afternoon.</p>
  <p><strong>GameGuard does NOT flag offensive words.</strong> It understands context, emojis, coded
  language, and patterns that emerge <strong>across multiple conversations</strong> &mdash; then builds a
  structured evidence case for the right human team. It never declares guilt. It never suspends
  anyone. It investigates; people decide.</p>
  <p>Press <strong>Run live demo</strong>: the orchestrator plans, calls its nine tools, and walks three
  scenarios &mdash; an account scam, a slow child-safety escalation, and a false-positive that wasn&rsquo;t.</p>
</section>

<div class="controls">
  <button id="run" onclick="runDemo()">Run live demo</button>
  <div class="spinner" id="spin"></div>
  <div class="status" id="status">Idle &mdash; demo runs locally via <kbd>python3 demo.py</kbd> (stdlib only, offline, deterministic).</div>
</div>

<div class="panels" id="panels">
  <section class="card">
    <h2>Agent trace &mdash; plan + tool calls</h2>
    <p style="color:var(--muted);font-size:.9rem;margin:0 0 10px">
      Watch the orchestrator <span style="color:var(--gold);font-weight:600">plan</span> before it acts,
      then call its <span style="color:var(--teal)">tools</span> message by message.</p>
    <div class="trace" id="trace"></div>
  </section>
  <section class="card">
    <h2>Results</h2>
    <div class="resgrid" id="results"></div>
  </section>
</div>

<footer>
  Local demo &mdash; <kbd>python3 app.py</kbd> serves this page from 127.0.0.1 only. No data leaves your machine.
</footer>
</div>

<script>
const traceEl = document.getElementById("trace");
const resultsEl = document.getElementById("results");
const panelsEl = document.getElementById("panels");
const statusEl = document.getElementById("status");
const runBtn = document.getElementById("run");
const spinEl = document.getElementById("spin");

function lineClass(line){
  if (/\[GameGuard Orchestrator PLAN\]/.test(line)) return "plan";
  if (/^\s{2,}\d+\.\s/.test(line)) return "pstep";
  if (/\[tool\]/.test(line)) return "tool";
  if (/^=+/.test(line)) return "sep";
  if (/>>>\s*OUTCOME|KEY POINT|SESSION SUMMARY/.test(line)) return "key";
  if (/ESCALATED|Case GG-/.test(line)) return "key";
  return "";
}

function renderTrace(text){
  traceEl.textContent = "";
  const frag = document.createDocumentFragment();
  for (const line of text.split("\n")){
    const div = document.createElement("div");
    div.className = "ln " + lineClass(line);
    div.textContent = line === "" ? "\u00a0" : line;
    frag.appendChild(div);
  }
  traceEl.appendChild(frag);
  traceEl.scrollTop = 0;
}

function sliceBetween(lines, startRe, endRe){
  const out = []; let on = false;
  for (const l of lines){
    if (!on && startRe.test(l)) on = true;
    if (on){ out.push(l); if (endRe.test(l) && out.length > 1) break; }
  }
  return out.join("\n").trim();
}

function renderResults(text){
  resultsEl.textContent = "";
  const lines = text.split("\n");
  const cards = [
    ["Demo 1 \u2014 the account scam",
     sliceBetween(lines, /DEMO 1/, /KEY POINT[\\s\\S]*$/).split(">>> OUTCOME").slice(1).join(">>> OUTCOME") || ""],
    ["Demo 2 \u2014 the slow escalation",
     sliceBetween(lines, /DEMO 2/, /KEY POINT[\\s\\S]*$/).split(">>> OUTCOME").slice(1).join(">>> OUTCOME") || ""],
    ["Demo 3 \u2014 the false positive that wasn\u2019t",
     sliceBetween(lines, /DEMO 3/, /KEY POINT[\\s\\S]*$/).split(">>> OUTCOME").slice(1).join(">>> OUTCOME") || ""],
  ];
  const evalLines = lines.filter(l =>
    /Test set:|precision:|evidence quality:|PATTERN TIMING|violating conversations|benign conversations|recall=/.test(l)
  ).slice(0, 24).join("\n");
  cards.push(["Evaluation \u2014 1,000 labeled messages + pattern timing", evalLines]);
  const sess = sliceBetween(lines, /SESSION SUMMARY/, /That is the whole design\\./);
  cards.push(["Session summary", sess]);

  for (const [title, body] of cards){
    const card = document.createElement("div");
    card.className = "res";
    const h = document.createElement("h3"); h.textContent = title;
    const pre = document.createElement("pre");
    pre.textContent = body || "(could not extract \u2014 see trace)";
    card.appendChild(h); card.appendChild(pre);
    resultsEl.appendChild(card);
  }
}

async function runDemo(){
  runBtn.disabled = true;
  spinEl.style.display = "inline-block";
  panelsEl.classList.remove("show");
  traceEl.textContent = ""; resultsEl.textContent = "";
  statusEl.textContent = "Running demo.py \u2014 the orchestrator is planning, calling tools, and investigating\u2026";
  try{
    const resp = await fetch("/api/run");
    if (!resp.ok) throw new Error("server returned HTTP " + resp.status);
    const data = await resp.json();
    if (!data.ok) throw new Error(data.error || "demo failed");
    renderTrace(data.output);
    renderResults(data.output);
    panelsEl.classList.add("show");
    statusEl.textContent = "Done \u2014 " + (data.output.match(/\\[tool\\]/g) || []).length +
      " tool calls, " + (data.output.match(/Case GG-/g) || []).filter((v,i,a)=>a.indexOf(v)===i).length +
      " cases opened. See the trace above.";
  }catch(e){
    statusEl.textContent = "Error: " + e.message;
  }finally{
    runBtn.disabled = false;
    spinEl.style.display = "none";
  }
}
</script>
</body>
</html>
"""

RUNNING_BANNER = [
    "Checking the orchestrator's plan...",
    "Running detect_language on every message...",
    "Aggregating patterns across conversations...",
    "Opening cases and building evidence...",
    "Computing evaluation metrics...",
]


def run_demo_subprocess() -> dict:
    """Run demo.py in a subprocess (its behavior is never modified here)."""
    try:
        proc = subprocess.run(
            [sys.executable, "demo.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "demo.py timed out after 600s"}
    except FileNotFoundError as e:
        return {"ok": False, "error": f"demo.py not found: {e}"}
    if proc.returncode != 0:
        return {
            "ok": False,
            "error": f"demo.py exited with code {proc.returncode}",
            "output": proc.stdout,
            "stderr": proc.stderr,
        }
    return {"ok": True, "output": proc.stdout}


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "GameGuardUI/1.0"

    def log_message(self, fmt, *args):  # keep server logs readable
        sys.stderr.write(f"[{self.address_string()}] {fmt % args}\n")

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        elif path == "/api/run":
            result = run_demo_subprocess()
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
        else:
            self._send(404, b'{"ok": false, "error": "not found"}',
                       "application/json; charset=utf-8")


def main() -> int:
    try:
        httpd = http.server.ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print(f"ERROR: port {PORT} is already in use.", file=sys.stderr)
            print(f"Another process is already listening on {HOST}:{PORT} "
                  f"(maybe an earlier 'python3 app.py' is still running).", file=sys.stderr)
            print(f"Stop it first — find the PID with  lsof -ti:{PORT}  and "
                  f"kill <PID>, then run 'python3 app.py' again.", file=sys.stderr)
            return 1
        raise
    print("=" * 62)
    print("  GameGuard AI — live web demo (stdlib only, offline)")
    print(f"  Open in Chrome: http://localhost:{PORT}")
    print("=" * 62)
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

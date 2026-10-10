#!/usr/bin/env python3
"""GameGuard AI -- localhost web UI (stdlib only).

Run:  python3 app.py   then open http://localhost:8007
Serves a guided, personalized tour of demo.py (the tested artifact --
demo.py is never modified here; it is only imported as a module and its
canned subprocess run is unchanged).
"""

import contextlib
import http.server
import io
import json
import mimetypes
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8007
HERE = Path(__file__).resolve().parent
DEMO_PY = HERE / "demo.py"

sys.path.insert(0, str(HERE))
import demo as DEMO  # the tested artifact: imported, never modified

COND_RE = re.compile(
    r"(type 2 diabetes|type 1 diabetes|diabetes|hypertension|high blood pressure|"
    r"kidney disease|ckd|heart disease|depression|asthma|arthritis|copd|hyperlipidemia)"
)

def _capture_canned():
    """Run the canned demo exactly as before (subprocess), capture stdout."""
    proc = subprocess.run(
        [sys.executable, str(DEMO_PY)],
        cwd=str(HERE),
        capture_output=True,
        text=True,
        timeout=600,
    )
    return proc.stdout or proc.stderr

def _capture_fn(fn, params):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            return fn(params)
    except Exception as exc:  # never crash the page on a bad input
        return "[web-ui] The personalized run hit an error and stopped safely.\n%s: %s" % (type(exc).__name__, exc)

# _capture_custom: personalized handlers may return a dict carrying a follow-up decision.
def _capture_custom(fn, params):
    try:
        res = fn(params)
    except Exception as exc:  # never crash the page on a bad input
        return {"output": "[web-ui] The personalized run hit an error and stopped safely.", "decision": None}
    if isinstance(res, dict):
        res.setdefault("decision", None)
        return res
    return {"output": res, "decision": None}

# ---- personalized run: input handling lives in app.py; demo.py untouched ----

def run_custom(params):
    text = (params.get("text") or "").strip()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        if text:
            print("YOUR MESSAGE:", text)
            lang = DEMO.detect_language(text)
            lang_name = lang.get("language", lang) if isinstance(lang, dict) else lang
            print("Detected language:", lang_name)
            result = DEMO.classify_message(text, lang, [])
            scores = result.get("scores", result) if isinstance(result, dict) else {}
            print("Classifier scores (per category, with escalation threshold):")
            escalated = False
            for k, v in scores.items():
                thr = DEMO.ESCALATE_AT.get(k)
                try:
                    flag = v >= thr
                except TypeError:
                    flag = False
                escalated = escalated or flag
                print("  %-18s %.2f  (escalates at %.2f)%s" % (k, v, thr, "  <-- ESCALATE" if flag else ""))
            if escalated:
                print("Verdict: a case file would be opened for a HUMAN moderator -- the agent never suspends anyone.")
            else:
                print("Verdict: no escalation. A safety system is judged by what it does not flag, too.")
        else:
            scen = (params.get("scenario") or "demo1").strip()
            fn = {"demo1": DEMO.demo1, "demo2": DEMO.demo2, "demo3": DEMO.demo3}.get(scen, DEMO.demo1)
            print("RE-RUN: %s (same code path as the canned demo)" % scen)
            print()
            fn()
    return out.getvalue()

PAGE = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>GameGuard AI &mdash; Live Demo</title>\n<style>\n:root{\n  --bg:#0b1220; --bg2:#0e1626; --panel:#131e33; --panel2:#182742;\n  --ink:#eaf0f9; --muted:#9db0c9; --faint:#6b7f99;\n  --teal:#2dd4bf; --teal-dim:rgba(45,212,191,.12);\n  --accent:#5aa9ff; --warn:#fbbf24; --danger:#f87171; --ok:#34d399;\n  --line:#233451; --radius:14px;\n}\n*{box-sizing:border-box}\nbody{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;\n  background:var(--bg);color:var(--ink);line-height:1.6}\nheader{background:linear-gradient(135deg,#0a2540 0%,#0e3a5c 60%,#0b4f4a 100%);\n  padding:42px 32px 34px;border-bottom:1px solid var(--line)}\n.wrap{max-width:1060px;margin:0 auto}\nheader h1{margin:0 0 8px;font-size:30px;letter-spacing:-.01em}\nheader .sub{margin:0;color:#c8d6ea;font-size:16px;max-width:800px}\n.badge{display:inline-block;margin-top:14px;font-size:11.5px;letter-spacing:.1em;\n  text-transform:uppercase;color:#06281f;background:var(--teal);\n  padding:5px 14px;border-radius:999px;font-weight:800}\nmain{padding:8px 32px 48px}\nsection.card{background:var(--panel);border:1px solid var(--line);\n  border-radius:var(--radius);padding:26px 28px;margin:26px 0}\nsection.card h2{margin:0 0 12px;font-size:18px;color:var(--teal)}\nsection.card h2 .n{display:inline-block;width:28px;height:28px;border-radius:50%;\n  background:var(--teal-dim);border:1px solid var(--teal);color:var(--teal);\n  text-align:center;line-height:26px;font-size:14px;margin-right:10px}\nsection.card p{margin:0 0 12px;color:#d5e0f1;font-size:15.5px}\nsection.card p:last-child{margin-bottom:0}\n.watch{list-style:none;margin:6px 0 0;padding:0}\n.watch li{position:relative;padding:8px 0 8px 30px;color:#d5e0f1;font-size:15px;\n  border-bottom:1px dashed var(--line)}\n.watch li:last-child{border-bottom:0}\n.watch li::before{content:"\\25b8";position:absolute;left:8px;color:var(--teal);font-weight:700}\nlabel.f{display:block;margin:14px 0 6px;font-size:13px;font-weight:700;\n  letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}\ninput[type=text],input[type=number],select,textarea{\n  width:100%;background:var(--bg2);border:1px solid var(--line);color:var(--ink);\n  border-radius:10px;padding:11px 14px;font-size:15px;font-family:inherit}\ntextarea{min-height:76px;resize:vertical}\ninput:focus,select:focus,textarea:focus{outline:none;border-color:var(--teal)}\n.row2{display:grid;grid-template-columns:1fr 1fr;gap:14px}\n@media(max-width:700px){.row2{grid-template-columns:1fr}}\n.btnrow{display:flex;gap:14px;align-items:center;margin-top:20px;flex-wrap:wrap}\nbutton.run{background:linear-gradient(135deg,#14b8a6,#0d9488);border:0;\n  color:#04211c;font-weight:800;font-size:17px;padding:15px 34px;\n  border-radius:12px;cursor:pointer;box-shadow:0 6px 22px rgba(45,212,191,.25)}\nbutton.run:hover{filter:brightness(1.08)}\nbutton.run:disabled{opacity:.45;cursor:default;box-shadow:none}\nbutton.ghost{background:transparent;border:1px solid var(--teal);color:var(--teal);\n  font-weight:700;font-size:15px;padding:13px 26px;border-radius:12px;cursor:pointer}\nbutton.ghost:hover{background:var(--teal-dim)}\nbutton.ghost:disabled{opacity:.45;cursor:default}\n.hint{color:var(--muted);font-size:13.5px}\n.spinner{display:none;align-items:center;gap:10px;color:var(--muted);font-size:14px;margin-top:14px}\n.spinner.show{display:flex}\n.dot{width:12px;height:12px;border-radius:50%;background:var(--teal);\n  animation:pulse 1s infinite ease-in-out}\n@keyframes pulse{0%,100%{transform:scale(.6);opacity:.5}50%{transform:scale(1.2);opacity:1}}\n#output{display:none;margin-top:6px}\n#output.show{display:block}\n.out{background:#0a0f1c;border:1px solid var(--line);border-radius:12px;\n  padding:20px 22px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;\n  font-size:13px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word;\n  max-height:640px;overflow:auto;color:#c9d6ea}\n.sechead{color:var(--accent);font-weight:800;margin:18px 0 2px;font-size:13.5px}\n.sechead:first-child{margin-top:0}\n.seccap{background:var(--teal-dim);border-left:3px solid var(--teal);\n  padding:8px 12px;margin:4px 0 12px;border-radius:0 8px 8px 0;\n  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;\n  font-size:13.5px;color:#bfe9e2}\n.tok-orch{color:var(--accent);font-weight:700}\n.tok-tool{color:var(--ok);font-weight:700}\n.tok-guard{color:var(--warn);font-weight:700}\n.tok-mem{color:#c084fc;font-weight:700}\n#takeaways{display:none}\n#takeaways.show{display:block}\n.take{background:rgba(52,211,153,.07);border:1px solid rgba(52,211,153,.4);\n  border-radius:var(--radius);padding:22px 26px;margin:26px 0}\n.take h2{color:var(--ok);margin:0 0 10px;font-size:18px}\n.take ul{margin:0;padding-left:20px}\n.take li{margin:8px 0;color:#d5e0f1;font-size:15px}\ntable.dec{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px}\ntable.dec th{background:var(--panel2);color:var(--teal);text-align:left;\n  padding:10px 12px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;\n  border-bottom:1px solid var(--line)}\ntable.dec td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}\n.pill{display:inline-block;padding:3px 12px;border-radius:999px;font-weight:800;font-size:12px}\n.pill.v{background:var(--ok);color:#04281c}\n.pill.s{background:var(--faint);color:#0b1220}\nfooter{padding:26px 32px 40px;color:var(--faint);font-size:13.5px;text-align:center}\nfooter a{color:var(--teal);text-decoration:none}\nfooter a:hover{text-decoration:underline}\ndetails.raw{margin-top:14px}\ndetails.raw summary{cursor:pointer;color:var(--muted);font-size:13.5px}\n\n/* --- care revamp: why-section + sidebar layout --- */\n.care-layout{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:26px;align-items:start}\n.care-main{min-width:0}\n.care-sidebar{position:sticky;top:20px;min-width:0}\n@media(max-width:960px){.care-layout{grid-template-columns:1fr}.care-sidebar{position:static}}\n.side-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:20px;margin-bottom:20px}\n.side-card h3{margin:0 0 10px;font-size:15px;color:var(--teal)}\n.side-vid{margin-bottom:18px}\n.side-vid:last-child{margin-bottom:0}\n.side-vid iframe{width:100%;aspect-ratio:16/9;border:0;border-radius:10px;display:block;background:#000}\n.side-vid p{font-size:13px;color:var(--muted);margin:8px 0 0;line-height:1.5}\n.side-links{list-style:none;margin:0;padding:0}\n.side-links li{margin:0 0 14px;font-size:13.5px;line-height:1.5}\n.side-links li:last-child{margin-bottom:0}\n.side-links a{color:var(--accent);font-weight:700;text-decoration:none}\n.side-links a:hover{text-decoration:underline}\n.side-links .outlet{display:block;font-size:12px;color:var(--faint)}\n.side-links .desc{display:block;color:var(--muted);margin-top:2px}\n.why-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:16px 0}\n@media(max-width:700px){.why-grid{grid-template-columns:1fr}}\n.why-grid figure{margin:0}\n.why-grid img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:10px;border:1px solid var(--line);display:block;background:#0a0f1c}\n.why-grid figcaption{font-size:12.5px;color:var(--muted);margin-top:6px;line-height:1.5}\n.chal{list-style:none;margin:10px 0 0;padding:0}\n.chal li{position:relative;padding:7px 0 7px 28px;color:#d5e0f1;font-size:15px}\n.chal li::before{content:"!";position:absolute;left:9px;color:var(--warn);font-weight:800}\n</style>\n</head>\n<body>\n<header><div class="wrap">\n  <h1>GameGuard AI</h1>\n  <p class="sub">It doesn\'t flag bad words. It understands conversations — across languages, emojis, and time.</p>\n</div></header>\n<main><div class="wrap care-layout"><div class="care-main">\n\n<section class="card" id="why">\n  <h2><span class="n">&#9733;</span>Why does this matter in real life?</h2>\n  <p>Millions of kids play games online every day, and the chat box is where they make friends &mdash; and where trouble finds them. Scams, grooming, and harassment rarely announce themselves with a flagged word. They hide inside ordinary-looking conversation: a friendly gift of game currency, then a quiet request for a password.</p>\n  <p>No team of human moderators can read every message across every server and every language. Keyword filters alone get it wrong in both directions: they miss the smooth talker who never says anything offensive, while banning an innocent kid who was only <i>warning</i> others about a scam. A wrong ban feels like injustice &mdash; and that kid may never come back.</p>\n  <div class="why-grid">\n    <figure><img src="/assets/img/rgb-setup.svg" alt="Gaming setup with an RGB backlit keyboard" loading="lazy"><figcaption>Where it all starts: millions of players log in from setups like this every day.</figcaption></figure>\n    <figure><img src="/assets/img/family-gaming.svg" alt="Father and son playing a video game together at home" loading="lazy"><figcaption>Gaming is family time too &mdash; and parents can&rsquo;t watch every chat window.</figcaption></figure>\n    <figure><img src="/assets/img/esports-arena.svg" alt="Esports arena crowd watching a live gaming event" loading="lazy"><figcaption>Gaming communities are huge: arenas full of fans, and chat servers even fuller.</figcaption></figure>\n    <figure><img src="/assets/img/chat-app-guide.svg" alt="A parent&rsquo;s guide to gaming chat apps" loading="lazy"><figcaption>Game chat lives in apps like Discord &mdash; where scams and pressure often arrive.</figcaption></figure>\n  </div>\n  <p><b>The purpose of this demo:</b> it shows an AI agent that investigates <b>context</b> &mdash; who said what, what happened earlier in the conversation, the pattern across messages &mdash; and builds an evidence case for a human moderator. It never declares guilt. It never suspends anyone. It protects the community without banning the wrong kid.</p>\n  <p><b>The challenges it tackles:</b></p>\n  <ul class="chal">\n    <li>Harm hides in context, not keywords &mdash; &ldquo;free gems&rdquo; is only a scam when it is followed by a credential request</li>\n    <li>Moderators can&rsquo;t read millions of messages &mdash; chat moves faster than any team can watch</li>\n    <li>A wrong ban feels like injustice and drives players away &mdash; false positives destroy trust in the whole system</li>\n  </ul>\n</section>\n\n<section class="card" id="story">\n  <h2><span class="n">1</span>The story</h2>\n  <p>BattleSphere has millions of players and a few dozen human moderators. The old safety tool was a keyword filter: it flagged the word <i>"password"</i> wherever it appeared — including when a player <i>warned</i> others about a scam — and missed the actual scammer, who never said anything offensive.</p>\n<p>GameGuard is the agent that replaced it. It reads conversations across English, Spanish, and Hindi, interprets emojis <i>in context</i>, watches how interactions develop over multiple messages, correlates chat with transaction history — and builds an evidence case for a human moderator. <b>It never declares guilt. It never suspends anyone. It investigates; people decide.</b></p>\n</section>\n\n<section class="card" id="watch">\n  <h2><span class="n">2</span>What to watch for</h2>\n  <ul class="watch">\n<li>Demo 1: three friendly messages — free gems, then “send me your password.” Watch the pattern assemble into a case.</li>\n<li>Demo 2: nothing alarming in any single message. Watch the risk score climb as the pattern develops across sessions.</li>\n<li>Demo 3: slang, emojis, trash talk — and the agent correctly does NOTHING. A safety system is judged by what it doesn\'t flag, too.</li>\n<li>The evaluation: precision, recall, and false-positive rates per language and category — no single accuracy score.</li>\n  </ul>\n</section>\n\n\n\n<section class="card" id="tryown">\n  <h2><span class="n">✎</span>Try your own</h2>\n  <p>Run the classifier on <b>your own text</b> — or re-run one of the three canned scenarios.</p>\n  <label class="f" for="g_scen">Scenario</label>\n  <select id="g_scen">\n    <option value="demo1">Demo 1 — the account scam</option>\n    <option value="demo2">Demo 2 — the slow escalation</option>\n    <option value="demo3">Demo 3 — the false positive that wasn\'t</option>\n  </select>\n  <label class="f" for="g_text">…or paste your own message</label>\n  <textarea id="g_text" placeholder="e.g. hey I\'ll send you free gems, just need your login"></textarea>\n  <div class="btnrow">\n    <button class="ghost" id="customRun">Run the classifier</button>\n    <span class="hint">Same inputs → same output. Deterministic.</span>\n  </div>\n  <div class="spinner" id="cspin"><div class="dot"></div>Scoring the message…</div>\n</section>\n\n\n<section class="card" id="runbox">\n  <h2><span class="n">3</span>Run the demo</h2>\n  <p>Click below to run the full canned demonstration. It takes a few seconds.</p>\n  <div class="btnrow">\n    <button class="run" id="run">&#9654; Run live demo</button>\n  </div>\n  <div class="spinner" id="spin"><div class="dot"></div><span>The agent is investigating the conversations…</span></div>\n  <div id="output">\n    <div class="out" id="outtext"></div>\n    <details class="raw"><summary>Show raw terminal output</summary>\n      <div class="out" id="rawtext"></div>\n    </details>\n  </div>\n</section>\n\n<section class="card" id="takeaways" style="display:none">\n  <div class="take">\n    <h2>What just happened</h2>\n    <ul>\n<li>A lure alone never escalates: free gems only become actionable paired with a credential or payment request.</li>\n<li>Context beats keywords: the filter-era false positive — flagging a scam <i>warning</i> — can\'t happen here.</li>\n<li>Demo 3 is the point: restraint is a feature. Flag-everything systems drown moderators.</li>\n<li>Thresholds encode values: child-safety escalates at a lower score because missing it is catastrophic.</li>\n<li>Try your own: paste any message in “Try your own” and watch the classifier score it.</li>\n    </ul>\n  </div>\n</section>\n\n</div>\n<aside class="care-sidebar">\n  <div class="side-card">\n    <h3>Learn more</h3>\n    <p style="font-size:13.5px;color:var(--muted);margin:0 0 14px">Want to go deeper on gaming safety? Start with these.</p>\n    <div class="side-vid">\n      <iframe src="https://www.youtube-nocookie.com/embed/nYlR8RtEDOg" title="Making Games Safe For Kids" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n      <p>Child-safety experts walk through the easy ways to keep kids safe while they play &mdash; chat settings, friend lists, and what to talk about.</p>\n    </div>\n    <div class="side-vid">\n      <iframe src="https://www.youtube-nocookie.com/embed/11qR5Mng7Tw" title="The Chat Behind the Game: What Parents Need to Know About Gaming Safety" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n      <p>Behind the game: voice chat, private servers, in-game gifts, and how conversations move to other apps &mdash; plus what to watch for.</p>\n    </div>\n    <div class="side-vid">\n      <iframe src="https://www.youtube-nocookie.com/embed/sJkekdlurFY" title="We Can Be Victims in a Game" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n      <p>A father and his gamer son talk honestly about scams, grooming, and what online safety should look like from a teen&rsquo;s perspective.</p>\n    </div>\n  </div>\n  <div class="side-card">\n    <h3>Go deeper &mdash; articles</h3>\n    <ul class="side-links">\n      <li><a href="https://dev.to/getstreamhq/content-moderation-at-scale-handling-millions-of-messages-without-sacrificing-ux-ngm" target="_blank" rel="noopener">Content Moderation at Scale: Handling Millions of Messages Without Sacrificing UX</a><span class="outlet">dev.to (GetStream)</span><span class="desc">Deep context analysis: why one &ldquo;toxic&rdquo; message and another need completely different responses &mdash; context, culture, and language matter.</span></li>\n      <li><a href="https://mobilesyrup.com/2024/12/20/how-ai-is-targeting-online-harassment-in-video-game-chats/" target="_blank" rel="noopener">How AI is targeting online harassment in video game chats</a><span class="outlet">MobileSyrup</span><span class="desc">Inside voice-chat moderation for games: dialects, slang, child psychologists, and the fight against false positives.</span></li>\n      <li><a href="https://vocal.media/writers/why-is-in-gaming-content-moderation-essential-for-safe-and-inclusive-play" target="_blank" rel="noopener">Why Is In-Gaming Content Moderation Essential for Safe and Inclusive Play</a><span class="outlet">Vocal</span><span class="desc">Real-time monitoring, AI detection, and human-in-the-loop review &mdash; why good moderation keeps players around.</span></li>\n    </ul>\n  </div>\n</aside>\n</div></main>\n<footer><div class="wrap">\n  <a href="https://github.com/ynpreet/gameguard-ai" target="_blank" rel="noopener">View the project on GitHub</a>\n  &nbsp;&middot;&nbsp; All data in this demo is synthetic / fictional.\n</div></footer>\n\n<script>\nconst SECTIONS = [["DEMO 1", "The account scam: harmless gifts turn into a credential trap. Evidence assembled, case opened for a human."], ["DEMO 2", "The slow escalation: risk assessed across messages, never from one. Child-safety thresholds are deliberately lower."], ["DEMO 3", "The false positive that wasn\'t: slang and emojis, correctly left alone. Moderator trust intact."], ["EVALUATION", "1,000 labeled messages: precision, recall, false positives \\u2014 per language, per category."], ["SESSION SUMMARY", "End of run."]];\nfunction esc(s){return s.replace(/&/g,\'&amp;\').replace(/</g,\'&lt;\').replace(/>/g,\'&gt;\');}\nfunction decorate(line){\n  let h = esc(line);\n  h = h.replace(/\\[ORCHESTRATOR\\]/g,\'<span class="tok-orch">[ORCHESTRATOR]</span>\');\n  h = h.replace(/\\[TOOL [^\\]]+\\]/g,function(m){return \'<span class="tok-tool">\'+m+\'</span>\';});\n  h = h.replace(/\\[MEMORY\\]/g,\'<span class="tok-mem">[MEMORY]</span>\');\n  h = h.replace(/GUARDRAIL/g,\'<span class="tok-guard">GUARDRAIL</span>\');\n  return h;\n}\nfunction renderOut(text){\n  document.getElementById(\'rawtext\').textContent = text;\n  const lines = text.split(\'\\n\');\n  let html = \'\';\n  for(const line of lines){\n    let matched = null;\n    for(const s of SECTIONS){ if(line.indexOf(s.m) !== -1){ matched = s; break; } }\n    if(matched){\n      html += \'<div class="sechead">\'+decorate(line)+\'</div>\'+\n              \'<div class="seccap">\'+matched.c+\'</div>\';\n      continue;\n    }\n    html += decorate(line) + \'\\n\';\n  }\n  document.getElementById(\'outtext\').innerHTML = html;\n  document.getElementById(\'output\').classList.add(\'show\');\n  document.getElementById(\'output\').scrollIntoView({behavior:\'smooth\',block:\'start\'});\n}\nfunction showTakeaways(){\n  const t = document.getElementById(\'takeaways\');\n  t.style.display=\'block\'; t.classList.add(\'show\');\n  t.scrollIntoView({behavior:\'smooth\',block:\'start\'});\n}\ndocument.getElementById(\'run\').addEventListener(\'click\',function(){\n  const btn=this, spin=document.getElementById(\'spin\');\n  btn.disabled=true; spin.classList.add(\'show\');\n  fetch(\'/api/run\').then(r=>r.json()).then(j=>{\n    spin.classList.remove(\'show\'); btn.disabled=false;\n    renderOut(j.output);\n    if(typeof loadDecisionTable===\'function\') loadDecisionTable();\n    showTakeaways();\n  }).catch(e=>{spin.classList.remove(\'show\');btn.disabled=false;alert(\'Run failed: \'+e);});\n});\n\nfunction collectCustom(){\n  return {scenario:document.getElementById(\'g_scen\').value,\n          text:document.getElementById(\'g_text\').value};\n}\n\nfunction wireCustom(){\n  const b=document.getElementById(\'customRun\');\n  if(!b) return;\n  b.addEventListener(\'click\',function(){\n    const spin=document.getElementById(\'cspin\');\n    b.disabled=true; spin.classList.add(\'show\');\n    fetch(\'/api/custom\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},\n      body:JSON.stringify(collectCustom())})\n    .then(r=>r.json()).then(j=>{\n      spin.classList.remove(\'show\'); b.disabled=false;\n      if(j.error){alert(j.error);return;}\n      renderOut(j.output); showTakeaways();\n    }).catch(e=>{spin.classList.remove(\'show\');b.disabled=false;alert(\'Run failed: \'+e);});\n  });\n}\nwireCustom();\n</script>\n</body>\n</html>\n'

class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "WorkshopUI/1.0"

    def _send(self, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj):
        self._send(json.dumps(obj), "application/json; charset=utf-8")

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            length = 0
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return {}

    def _serve_asset(self, path):
        safe = (HERE / path.lstrip("/")).resolve()
        try:
            safe.relative_to(HERE / "assets")
        except ValueError:
            return self.send_error(403, "forbidden")
        if not safe.is_file():
            return self.send_error(404, "not found")
        ctype, _ = mimetypes.guess_type(str(safe))
        data = safe.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path in ("/", "/index.html"):
            self._send(PAGE)
        elif path == "/api/run":
            self._json({"output": _capture_canned()})
        elif path.startswith("/assets/"):
            self._serve_asset(path)
        else:
            self.send_error(404, "not found")

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/api/custom":
            params = self._read_json()
            self._json(_capture_custom(run_custom, params))
        else:
            self.send_error(404, "not found")

    def log_message(self, fmt, *args):
        sys.stderr.write("ui: " + (fmt % args) + "\n")


def main():
    server = http.server.ThreadingHTTPServer((HOST, PORT), Handler)
    print("GameGuard AI demo UI -> http://localhost:8007")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fassung 4 · alle fünf Inputs als ein html-vortrag (Steuerungskern wie der SRL-Vortrag in srl5), Farben der Klasse 5.3.

    python3 tools/build_inputs_f4.py

Inhalt:  inhalt/f4/inputs_laut.json
Vorlage: tools/vorlagen/html_vortrag.html (Skill html-vortrag, Kern unverändert)
Ausgabe: apps/inputs/index.html + apps/inputs/assets/fonts/ (Jost, OFL)

Laut-denken-Folien: Jeder Klick deckt einen unsichtbaren .step auf; der Projekt-Haken
(HOOKS.onSlide/onStep) setzt danach Markierung, Gedankenblase und Ergebnis neu.
Test: jede Folie in jedem Schritt (1280×720, 1024×768), Leseansicht Handy, Druck.
"""
import html as H
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "inhalt" / "f4" / "inputs_laut.json").read_text("utf-8"))
VORLAGE = (ROOT / "tools" / "vorlagen" / "html_vortrag.html").read_text("utf-8")
OUT = ROOT / "apps" / "inputs" / "index.html"


def esc(s):
    return H.escape(str(s), quote=False)


def md(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))


def ul(items):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % md(i) for i in items)


THEMA_CSS = """
/* ---- Farben der Klasse 5.3 (Otterklasse): Blau führt, Minze beruhigt/bestätigt, Orange aktiviert ---- */
@font-face{font-family:Jost;src:url(assets/fonts/jost.woff2) format("woff2");font-weight:100 900;font-display:block}
html[data-theme=k53]{
  --b50:#EFF5FA;--b100:#DDEAF4;--b200:#BDD4E7;--b300:#91B6D4;--b400:#5F91B7;--b500:#356D9C;--b600:#245688;--b700:#1F4770;--b800:#1C3D5E;--b900:#19334E;
  --m50:#EFFCFA;--m100:#D6F8F3;--m200:#ADEFE7;--m400:#48DCCB;--m600:#1B958A;--m700:#19766F;--m800:#195E59;
  --o50:#FFF8F2;--o100:#FEEEDD;--o200:#FBD8B9;--o300:#F6C18F;--o400:#F0A66F;--o600:#CF6320;--o700:#A94A1A;--o800:#893C1C;
  --slate-dark:var(--b800);--slate-base:var(--b600);--slate-mid:var(--b400);--slate-pale:var(--b200);--slate-ghost:var(--b50);
  --rust-dark:var(--o700);--rust-base:var(--o400);--rust-mid:var(--o300);--rust-pale:var(--o100);
  --sage-dark:var(--m700);--sage-base:var(--m400);
  --navy:var(--b600);--blue:var(--b500);--red:var(--o700);--accent:var(--o400);--good:var(--m700);
  --paper:#F8FAFB;--ink:#18324A;--muted:#3D5061;--line:#DFE5EA;
  --cover-a:var(--b500);--cover-b:var(--b600);--cover-c:var(--b800);--cover-em:var(--m400);
  --f-display:Jost,system-ui,sans-serif;--f-text:Jost,system-ui,sans-serif;
}
html[data-theme=k53] .h,html[data-theme=k53] .statement,html[data-theme=k53] .col .name{font-weight:700;letter-spacing:-.01em}
html[data-theme=k53] .h{font-size:80px;margin-bottom:36px}
html[data-theme=k53] .h em,html[data-theme=k53] .kw em{color:var(--o600)}
html[data-theme=k53] .cover .h{font-size:120px}
html[data-theme=k53] .cover .h em{color:var(--m400)}
html[data-theme=k53] .chapter .h{font-size:104px}
html[data-theme=k53] .chapter .chap-no{font-weight:700;color:rgba(255,255,255,.08)}
html[data-theme=k53] .cover .line{background:linear-gradient(90deg,var(--m400),var(--o400))}
html[data-theme=k53] .dotted li::before{background:var(--o400);border:2px solid var(--o700)}
html[data-theme=k53] #progress .tick{background:var(--b300)}

/* Übersicht */
.inputs{display:grid;grid-template-columns:repeat(5,1fr);gap:24px}
.ip{background:#fff;border-radius:24px;padding:28px 24px;border-top:10px solid var(--b600);box-shadow:0 6px 18px rgba(36,86,136,.12);display:flex;flex-direction:column;gap:12px;min-height:330px}
.ip .n{font:700 84px/1 var(--f-display);color:var(--b600)}
.ip .t{font:700 34px/1.15 var(--f-text);color:var(--ink)}
.ip .w{font:500 24px/1.3 var(--f-text);color:var(--muted);margin-top:auto}

/* Auftrag */
.situation{background:linear-gradient(135deg,var(--o50),var(--o100));border-left:14px solid var(--o600);border-radius:24px;padding:36px 44px;font:500 44px/1.35 var(--f-text);color:var(--ink);margin-bottom:28px}
.situation::before{content:"! Mein Auftrag";display:block;font:700 24px var(--f-text);letter-spacing:.12em;text-transform:uppercase;color:var(--o700);margin-bottom:10px}
.denken{display:grid;gap:18px}
.blase{background:var(--b50);border:3px solid var(--b600);border-radius:28px;padding:20px 28px;font:500 34px/1.35 var(--f-text);color:var(--ink)}
.blase::before{content:"💭 Ich denke:";display:block;font:700 22px var(--f-text);letter-spacing:.1em;text-transform:uppercase;color:var(--b600);margin-bottom:6px}
.blase.irrtum{background:var(--o50);border-color:var(--o600);border-style:dashed}
.blase.irrtum::before{content:"💭 Ich denke … ⚠ Moment!";color:var(--o700)}

/* Strategie */
.strat{display:grid;grid-template-columns:1.2fr 1fr;gap:48px;align-items:start}
.fragen{list-style:none;margin:0;padding:0;display:grid;gap:22px}
.fragen li{display:grid;grid-template-columns:72px 1fr;gap:20px;align-items:start;background:#fff;border-radius:24px;padding:20px 24px;box-shadow:0 4px 14px rgba(36,86,136,.10)}
.fragen .fz{display:grid;place-items:center;width:64px;height:64px;border-radius:16px;background:var(--b600);color:#fff;font:700 34px var(--f-text)}
.fragen .fq{font:700 36px/1.2 var(--f-text);color:var(--ink)}
.fragen .fa{font:500 27px/1.3 var(--f-text);color:var(--muted);margin-top:6px}
.signale{background:#fff;border-radius:24px;padding:24px 28px;box-shadow:0 4px 14px rgba(36,86,136,.10)}
.signale h3,.erg h3,.hilfebox h3,.auf h3{font:700 22px var(--f-text);letter-spacing:.12em;text-transform:uppercase;color:var(--b600);margin:0 0 12px}
.sig{display:flex;justify-content:space-between;gap:16px;padding:10px 0;border-bottom:2px solid var(--line);font:500 27px/1.25 var(--f-text)}
.sig:last-of-type{border:none}.sig b{color:var(--ink)}.sig span{color:var(--muted);text-align:right}
.wann{margin-top:14px;background:var(--m50);border-left:10px solid var(--m600);border-radius:0 16px 16px 0;padding:14px 18px;font:500 25px/1.3 var(--f-text);color:var(--ink)}
.wann::before{content:"✓ Wann hilft das? ";font-weight:700;color:var(--m800)}

/* Laut denken */
.slide.laut{padding:40px 64px 34px;justify-content:flex-start}
.slide.laut .h{font-size:50px;margin-bottom:18px}
.slide.laut .label{margin-bottom:6px;font-size:21px}
.lgrid{display:grid;grid-template-columns:.8fr 1.2fr;gap:30px;flex:1;min-height:0}
.textkarte{background:#fff;border-radius:24px;padding:26px 32px;box-shadow:0 4px 14px rgba(36,86,136,.10);overflow:hidden}
.textkarte .tt{font:700 21px var(--f-text);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:12px}
.textkarte .tx{font:500 31px/1.6 var(--f-text);color:var(--ink)}
mark{background:none;color:inherit;border-radius:8px;padding:0 3px}
mark.akt{background:var(--o200);box-shadow:0 0 0 3px var(--o600);font-weight:600}
mark.war{background:var(--b50);text-decoration:underline;text-decoration-color:var(--b400);text-decoration-thickness:3px;text-underline-offset:5px}
.rechts{display:flex;flex-direction:column;gap:14px;min-height:0}
.rechts .blase{font-size:27px;padding:12px 22px;border-radius:22px}.rechts .blase::before{font-size:20px;margin-bottom:2px}
.erg{background:#fff;border-radius:24px;padding:14px 22px;box-shadow:0 4px 14px rgba(36,86,136,.10);flex:1;min-height:0;overflow:hidden}
.zone{margin-bottom:6px}
.zl{font:700 20px var(--f-text);letter-spacing:.06em;text-transform:uppercase;color:var(--b600)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:2px;min-height:30px}
.chip{background:var(--m50);border:2px solid var(--m600);color:var(--ink);border-radius:10px;padding:1px 10px;font:500 22px/1.3 var(--f-text);animation:chipIn .45s var(--ease) both}
.chip::before{content:"✓ ";color:var(--m700);font-weight:700}
.chip.neu{box-shadow:0 0 0 4px var(--m200)}
.chip.frag{background:var(--o50);border-color:var(--o600);border-style:dashed}
.chip.frag::before{content:"? ";color:var(--o700)}
.chip.weg{background:#fff;border-color:var(--line);color:var(--muted);text-decoration:line-through;text-decoration-thickness:3px}
.chip.weg::before{content:"✗ ";color:var(--o800);text-decoration:none;display:inline-block}
@keyframes chipIn{from{opacity:0;transform:translateX(20px) scale(.92)}to{opacity:1;transform:none}}
.liste .chips{display:grid;gap:8px}
.bogen .zone{display:grid;grid-template-columns:190px 1fr;gap:10px;align-items:center;border-bottom:2px solid var(--line);padding-bottom:4px;margin-bottom:4px}.bogen .chips{min-height:30px}
.bogen .zone:last-child{border:none;margin:0}
.tab{display:grid;grid-template-columns:1fr 1fr;gap:12px 14px}
.tab .zone{background:var(--b50);border-radius:16px;padding:8px 12px;margin:0}
.satz{font:500 36px/1.6 var(--f-text);color:var(--ink)}
.satz del{color:var(--o800);text-decoration-thickness:4px}
.satz ins{text-decoration:underline;text-decoration-color:var(--m600);text-decoration-thickness:4px;text-underline-offset:6px;background:var(--m50);font-weight:700;border-radius:6px;padding:0 4px}
.satz.falsch ins{background:var(--o50);text-decoration-color:var(--o600);text-decoration-style:wavy}
.lmarker{display:none}

/* Ergebnis */
.muster{font:700 44px/1.3 var(--f-text);color:var(--ink);background:linear-gradient(135deg,var(--b50),var(--m100));border-radius:32px;padding:30px 44px;margin-bottom:28px;text-align:center}
html[data-theme=k53] .checks li::before{background-color:var(--m700)}
.kw-list.klein{gap:16px}.kw-list.klein li{grid-template-columns:68px 1fr}.kw-list.klein li::before{width:48px;height:48px;border-radius:12px;background-size:30px}

/* Jetzt ihr */
.jetzt{display:grid;grid-template-columns:1.25fr 1fr;gap:40px;align-items:start}
.auf{background:#fff;border-left:14px solid var(--o600);border-radius:24px;padding:28px 34px;box-shadow:0 4px 14px rgba(36,86,136,.10)}
.auf ol{margin:0;padding-left:44px;font:500 36px/1.35 var(--f-text);color:var(--ink)}.auf li{margin-bottom:14px}
.hilfebox{background:var(--b50);border-left:14px solid var(--b600);border-radius:24px;padding:28px 30px}
.hilfebox ul{margin:0;padding-left:30px;font:500 29px/1.35 var(--f-text);color:var(--ink)}.hilfebox li{margin-bottom:12px}
.partner{margin-top:28px;background:var(--m100);border-left:14px solid var(--m600);border-radius:24px;padding:22px 30px;font:500 34px/1.35 var(--f-text);color:var(--ink);display:flex;gap:18px;align-items:center}
.partner .uhr{font-size:48px}
.read .lgrid,.read .strat,.read .jetzt,.read .inputs{grid-template-columns:1fr}
"""

LAUT_JS = r"""
<script>
/* Projekt: laut-denken-Folien (Markierung, Gedankenblase, wachsendes Ergebnis) */
const LAUT = __LAUT__;
const lesc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const lmd = s => lesc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
const lsatz = s => lesc(s).replace(/~~(.+?)~~/g, "<del>$1</del>").replace(/\*\*(.+?)\*\*/g, "<ins>$1</ins>");
let PRINTING = false;
function lmark(text, akt, war){
  const r = [], frei = (a, b) => r.every(x => b <= x[0] || a >= x[1]);
  for (const [liste, cls] of [[akt, "akt"], [war, "war"]]) for (const p of liste){
    let i = text.indexOf(p); while (i >= 0 && !frei(i, i + p.length)) i = text.indexOf(p, i + 1);
    if (i >= 0) r.push([i, i + p.length, cls]);
  }
  r.sort((a, b) => a[0] - b[0]); let o = "", pos = 0;
  for (const [a, b, c] of r){ o += lesc(text.slice(pos, a)) + `<mark class="${c}">${lesc(text.slice(a, b))}</mark>`; pos = b; }
  return o + lesc(text.slice(pos));
}
function lrender(sl){
  const id = sl.dataset.laut; if (id === undefined) return;
  const fo = LAUT[id], all = fo.schritte.length;
  const n = (isRead() || PRINTING) ? all : all - sl.querySelectorAll(".lmarker.hidden").length;
  const akt = n > 0 ? fo.schritte[n - 1].mark : [];
  const war = fo.schritte.slice(0, Math.max(0, n - 1)).flatMap(x => x.mark).filter(p => !akt.includes(p));
  sl.querySelector("[data-tx]").innerHTML = lmark(fo.text, akt, war);
  const b = sl.querySelector("[data-blase]"), x = n > 0 ? fo.schritte[n - 1] : null;
  b.className = "blase" + (x && x.irrtum ? " irrtum" : "");
  b.innerHTML = x ? lmd(x.denke) : "Ich lese Satz für Satz. Klick: Was denke ich?";
  const z = {}; (fo.ergebnis.zonen || []).forEach(([k]) => z[k] = []);
  let satz = null, falsch = false;
  for (let k = 0; k < n; k++){
    const s = fo.schritte[k];
    if (s.strike){ const l = z[s.strike]; if (l && l.length) l[l.length - 1].weg = k; }
    (s.add || []).forEach(([zid, t]) => z[zid].push({t, frag: !!s.irrtum, neu: k === n - 1}));
    if (s.satz !== undefined){ satz = s.satz; falsch = !!s.irrtum; }
  }
  const e = fo.ergebnis, box = sl.querySelector("[data-erg]");
  if (e.art === "satz"){ box.innerHTML = `<h3>${lesc(e.titel)}</h3><div class="satz${falsch ? " falsch" : ""}">${satz ? lsatz(satz) : "…"}</div>`; return; }
  const chip = c => `<span class="chip${c.weg !== undefined ? " weg" : c.frag ? " frag" : ""}${c.neu && c.weg === undefined ? " neu" : ""}">${lesc(c.t)}</span>`;
  const zonen = e.zonen.map(([k, l]) => `<div class="zone"><div class="zl">${lesc(l)}</div><div class="chips">${z[k].filter(c => c.weg === undefined || c.weg === n - 1).map(chip).join("")}</div></div>`).join("");
  box.innerHTML = `<h3>${lesc(e.titel)}</h3><div class="${e.art === "bogen" ? "bogen" : e.art === "tabelle" ? "tab" : "liste"}">${zonen}</div>`;
}
const lalle = () => slides.forEach(lrender);
HOOKS.onSlide = sl => lrender(sl);
HOOKS.onStep = sl => lrender(sl);
addEventListener("beforeprint", () => { PRINTING = true; lalle(); });
addEventListener("afterprint", () => { PRINTING = false; lalle(); });
readMQ.addEventListener("change", lalle);
lalle();
</script>
"""


def folien():
    out, laut, nr = [], [], 0
    out.append(
        "<section class='slide cover' data-title='Märchen · Inputs' data-section='Start' data-dark>"
        "<div class='mark'>Märchen</div><h1 class='h'>Laut denken<br><em>Strategien erklären</em></h1>"
        "<p class='kw'>Fünf Inputs zur Märchenreihe</p><div class='line'></div>"
        "<p class='sm'>Deutsch · Jahrgang 5 · höchstens 10 Minuten pro Input</p>"
        "<div class='notes'><ul><li>Übersicht über alle Inputs: <b>G</b>. Direkt zu einem Input: Menü (<b>M</b>) → Teil 2–6.</li>"
        "<li>Prinzip: Ich zeige, was in meinem Kopf passiert – nicht das Merkblatt erklären.</li></ul></div></section>")
    karten = "".join("<div class='ip'><span class='n'>%d</span><span class='t'>%s</span><span class='w'>%s</span></div>"
                     % (i["nr"], esc(i["titel"]), esc(i["wann"])) for i in D["inputs"])
    out.append("<section class='slide' data-title='Die fünf Inputs'><p class='label'>Überblick</p><h2 class='h'>Fünf Inputs – <em>ein Prinzip.</em></h2>"
               "<div class='inputs'>%s</div><div class='notes'><p>Jeder Input: Auftrag → Strategie erklärt → ich denke laut → so klingt lautes Denken → jetzt ihr.</p></div></section>" % karten)
    for i in D["inputs"]:
        n = i["nr"]
        kopf = "Input %d · %s" % (n, i["titel"])
        out.append("<section class='slide cover chapter' data-title='%s' data-section='Input %d · %s' data-dark>"
                   "<p class='chap-no' aria-hidden='true'>%d</p><p class='label'>Input %d · %s</p><h2 class='h'>%s</h2>"
                   "<div class='notes'><p><b>Hinweis:</b> %s</p></div></section>"
                   % (esc(kopf), n, esc(i["titel"]), n, n, esc(i["wann"]), esc(i["titel"]), md(i["hinweis"])))
        for fo in i["folien"]:
            nr += 1
            t, lab = fo["typ"], "<p class='label'>%s</p>" % esc(kopf)
            dt = esc("%d · %s" % (n, fo["titel"]))
            if t == "auftrag":
                out.append("<section class='slide' data-title='%s'>%s<h2 class='h'>%s</h2><div class='situation'>%s</div><div class='denken'>%s</div>"
                           "<div class='notes'><ul><li>Situation vorlesen.</li>%s</ul></div></section>"
                           % (dt, lab, esc(fo["titel"]), md(fo["situation"]), "".join("<div class='blase step'>%s</div>" % md(d) for d in fo["denke"]),
                              "".join("<li>Klick: %s</li>" % md(d) for d in fo["denke"])))
            elif t == "strategie":
                fr = "".join("<li class='step'><span class='fz'>%d</span><span><span class='fq'>%s</span><span class='fa' style='display:block'>%s</span></span></li>"
                             % (k, md(q), md(a)) for k, (q, a) in enumerate(fo["fragen"], 1))
                sg = "".join("<div class='sig'><b>%s</b><span>→ %s</span></div>" % (esc(a), esc(b)) for a, b in fo["signale"])
                out.append("<section class='slide' data-title='%s'>%s<h2 class='h'>%s</h2><div class='strat'><ol class='fragen'>%s</ol>"
                           "<div class='signale step'><h3>Signale im Text</h3>%s<div class='wann'>%s</div></div></div>"
                           "<div class='notes'><ul><li>Fragen einzeln aufdecken und jeweils kurz begründen.</li><li>Zum Schluss die Signale: „Darauf achte ich beim Lesen.“</li></ul></div></section>"
                           % (dt, lab, esc(fo["titel"]), fr, sg, md(fo["wann"])))
            elif t == "laut":
                k = len(laut)
                laut.append({"text": fo["text"], "schritte": fo["schritte"], "ergebnis": fo["ergebnis"]})
                marker = "".join("<i class='step lmarker'></i>" for _ in fo["schritte"])
                notiz = "".join("<li>Klick %d%s: %s</li>" % (m, " <b>(Irrtum zeigen)</b>" if x.get("irrtum") else "", md(x["denke"]))
                                for m, x in enumerate(fo["schritte"], 1))
                out.append("<section class='slide laut' data-title='%s' data-laut='%d'>%s<h2 class='h'>%s</h2><div class='lgrid'>"
                           "<div class='textkarte'><div class='tt'>%s</div><div class='tx' data-tx></div></div>"
                           "<div class='rechts'><div class='blase' data-blase></div><div class='erg' data-erg></div></div></div>%s"
                           "<div class='notes'><ul>%s</ul></div></section>"
                           % (dt, k, lab, esc(fo["titel"]), esc(fo["text_titel"]), marker, notiz))
            elif t == "ergebnis":
                out.append("<section class='slide' data-title='%s'>%s<h2 class='h'>%s</h2><div class='muster'>%s</div>"
                           "<ul class='kw-list checks klein'>%s</ul><div class='notes'><p>Satzmuster gemeinsam laut sprechen.</p></div></section>"
                           % (dt, lab, esc(fo["titel"]), esc(fo["satz"]), "".join("<li class='kw step' style='font-size:34px'><span>%s</span></li>" % md(p) for p in fo["punkte"])))
            elif t == "jetzt":
                out.append("<section class='slide' data-title='%s'>%s<h2 class='h'>%s</h2><div class='jetzt'>"
                           "<div class='auf'><h3>Euer Auftrag</h3><ol>%s</ol></div>"
                           "<div class='hilfebox step'><h3>Hier findest du Hilfe</h3>%s</div></div>"
                           "<div class='partner step'><span class='uhr' aria-hidden='true'>⏱</span><span>%s</span></div>"
                           "<div class='notes'><p>30 Sekunden Partnerimpuls, dann Start in die Arbeitsphase.</p></div></section>"
                           % (dt, lab, esc(fo["titel"]), "".join("<li>%s</li>" % md(a) for a in fo["auftrag"]), ul(fo["hilfe"]), md(fo["partner"])))
    return "\n".join(out), laut


def pruefe_daten():
    f = []
    for i in D["inputs"]:
        for fo in i["folien"]:
            if fo["typ"] == "laut":
                zonen = {z[0] for z in fo["ergebnis"].get("zonen", [])}
                for n, x in enumerate(fo["schritte"], 1):
                    f += ["Input %d Schritt %d: Stelle fehlt im Text: %s" % (i["nr"], n, m) for m in x["mark"] if m not in fo["text"]]
                    f += ["Input %d Schritt %d: Zone %s" % (i["nr"], n, z) for z, _ in x.get("add", []) if z not in zonen]
    return f


def bauen():
    html, laut = folien()
    v = VORLAGE
    a = v.index("<section class=\"slide cover\" data-title=\"Titel\"")
    b = v.index("</div>\n<div id=\"cam\"")
    v = v[:a] + html + "\n\n" + v[b:]
    v = re.sub(r"<div id=\"cam\".*?</div>\n</div>", "</div>", v, count=1, flags=re.S)
    v = v.replace('data-theme="srl"', 'data-theme="k53"').replace('content="#2C3D4C"', 'content="#245688"')
    for k, w in {"{{KURZTITEL}}": "Märchen-Inputs", "{{TITEL}}": "Märchen · Inputs", "{{UNTERTITEL}}": "laut denken und Strategien erklären",
                 "{{BESCHREIBUNG}}": "Fünf Inputs zur Märchenreihe Deutsch Jahrgang 5: laut denken und Strategien erklären"}.items():
        v = v.replace(k, w)
    if "{{" in v:
        raise SystemExit("Platzhalter übrig: " + re.findall(r"\{\{[^}]+\}\}", v)[0])
    v = v.replace("/* ---- projektspezifische Bausteine hier ergänzen ---- */", "/* ---- projektspezifische Bausteine hier ergänzen ---- */" + THEMA_CSS)
    v = v.replace("</script>\n</body>", "</script>\n" + LAUT_JS.replace("__LAUT__", json.dumps(laut, ensure_ascii=False)) + "</body>")
    OUT.write_text(v, encoding="utf-8")


def testen():
    fehler = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        for w, h in ((1280, 720), (1024, 768)):
            pg = br.new_page(viewport={"width": w, "height": h})
            pg.on("pageerror", lambda e: fehler.append(str(e)))
            pg.on("console", lambda m: m.type == "error" and fehler.append(m.text))
            pg.goto(OUT.as_uri())
            pg.wait_for_timeout(300)
            n = pg.evaluate("slides.length")
            for i in range(n):
                pg.evaluate(f"document.body.classList.add('no-anim'); goTo({i}); setSteps(slides[{i}], true); lrender(slides[{i}])")
                steps = pg.evaluate(f"slides[{i}].querySelectorAll('.step').length")
                for s in range(steps + 1):
                    if s:
                        pg.evaluate("forward()")
                    ueber = pg.evaluate("""() => { const s = slides[index], r = document.getElementById('stage').getBoundingClientRect(), k = r.width/1600, out = [];
                      if ([...s.querySelectorAll('*')].filter(e => !e.closest('.notes')).some(e => { const q = e.getBoundingClientRect();
                         return q.width && ((q.bottom - r.top)/k > 905 || (q.right - r.left)/k > 1605); })) out.push('Bühne');
                      s.querySelectorAll('.textkarte,.erg').forEach(e => { if (e.scrollHeight > e.clientHeight + 2) out.push(e.className + ' +' + (e.scrollHeight - e.clientHeight)); });
                      return out; }""")
                    if ueber:
                        fehler.append(f"{w}×{h} Folie {i + 1} ({pg.evaluate('slides[index].dataset.title')}) Schritt {s}: {', '.join(ueber)}")
            for key in ["Home", "ArrowRight", "g", "Escape", "m", "m", "b", "b"]:
                pg.keyboard.press(key)
            pg.close()
        m = br.new_page(viewport={"width": 390, "height": 844})
        m.goto(OUT.as_uri())
        if not m.evaluate("document.documentElement.classList.contains('read')"):
            fehler.append("Leseansicht fehlt")
        if m.evaluate("[...document.querySelectorAll('[data-blase]')].some(b => !b.textContent.trim())"):
            fehler.append("Leseansicht: leere Gedankenblase")
        pg = br.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(OUT.as_uri())
        pg.emulate_media(media="print")
        pg.pdf(path="/tmp/inputs_druck.pdf", width="1600px", height="900px", print_background=True)
        print("Folien:", pg.evaluate("slides.length"))
        br.close()
    return fehler


if __name__ == "__main__":
    f = pruefe_daten()
    if f:
        print("FEHLER:", *f, sep="\n  ")
        sys.exit(1)
    bauen()
    f = testen()
    print("apps/inputs/index.html", OUT.stat().st_size // 1024, "KB")
    print("FEHLER:", *f[:40], sep="\n  ") if f else print("ok")
    sys.exit(1 if f else 0)

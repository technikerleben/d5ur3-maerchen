#!/usr/bin/env python3
"""Material einer Etappe aus inhalt/etappeN.json erzeugen.

    python3 tools/build_material.py 1

Ausgabe ausgabe/etappeN/:
  Input_EtappeN.html            Beamer, farbig, offline; gesicherte Antworten auf Klick
  Merkblatt_N_A4.pdf            gleicher Inhalt wie der Input (A4 Originalgröße)
  Blatt_<nr>_A4.pdf             Pflichtblätter (A4 gesetzt, auf A5 verkleinert drucken)
  Schuelerpaket_EtappeN_A4.pdf  Material (Märchentexte) + Blätter
  GNN_A_A4.pdf / GNN_B_A4.pdf   Gelingensnachweise: Material, Aufgaben, Rückmeldung (A4 Original)
  GNN_Erwartungshorizont_A4.pdf Lehrkraft
  foerder/                      Merkkarte, Blätter NF, GN-F
Vorher: python3 tools/build_texte.py (Zeilenangaben und Märchentexte).
"""
from __future__ import annotations

import html
import json
import random
import re
import sys
from pathlib import Path

import pymupdf as fitz
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from satz import FUSS, ROOT, bild_uri, esc, font_css, kleinste_schrift, zeile  # noqa: E402

TEXTE = ROOT / "ausgabe" / "texte"
KARTEN = "Dir fehlt eine Idee? Deine Märchenkarten zeigen dir Figuren, Orte, Zauberdinge und Märchenmerkmale."


# ------------------------------------------------------------ Markup
def md(s: str, karten: str = KARTEN) -> str:
    s = re.sub(r"\{Z:([\w-]+):(.+?)\}", lambda m: zeile(m.group(1), m.group(2)), s)
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = s.replace("{KARTEN}", "<span class=karten>%s</span>" % esc(karten))
    return s.replace("\n", "<br>")


def plain(s: str) -> str:
    return re.sub(r"<[^>]+>", "", md(s).replace("<br>", " "))


# ------------------------------------------------------------ Input (HTML, Beamer)
INPUT_CSS = """
:root{--blau:#3E5668;--blau2:#2C3D4C;--rost:#D97A4A;--rost2:#9E4E22;--gruen:#7DBB6F;--gruen2:#4D8B3F;--bg:#F5F4F1;--ink:#1E2A35}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--bg);color:var(--ink);font-family:'Andika',sans-serif}
.folie{display:none;height:100vh;padding:4vh 6vw 9vh;flex-direction:column;gap:2.2vh;overflow:auto}
.folie.an{display:flex}.folie.lang.an{display:flex}
.kopf{font-size:2.2vh;letter-spacing:.08em;text-transform:uppercase;color:var(--blau);font-weight:700}
h1{font-size:6.4vh;line-height:1.1;color:var(--blau2)}
h2{font-size:5vh;line-height:1.15;color:var(--blau2)}
.ziel{font-size:3.6vh;line-height:1.35;background:#fff;border-left:1.2vh solid var(--blau);padding:2.4vh 3vh;border-radius:1.4vh;max-width:70ch}
.block{background:#fff;border-radius:1.6vh;padding:2vh 2.6vh;border:.3vh solid #d9d6cf;font-size:3.1vh;line-height:1.4}
.folie.lang .block{font-size:2.6vh;padding:1.5vh 2.2vh}.folie.lang{gap:1.6vh}
.folie.xlang .block{font-size:2.3vh;padding:1.2vh 2vh}.folie.xlang h2{font-size:4.2vh}.folie.xlang .mitbild{grid-template-columns:1fr 20vw}
.block>b{display:block;font-size:2.1vh;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.8vh;color:var(--blau)}
.block.frage{border-color:var(--rost)}.block.frage>b{color:var(--rost2)}
.block.antwort{border-color:var(--gruen);background:#f3f9f1}.block.antwort>b{color:var(--gruen2)}
.block.antwort.zu{background:#fff;cursor:pointer}.block.antwort.zu .inhalt{visibility:hidden}
.block.antwort.zu>b::after{content:" – klicken oder Leertaste";text-transform:none;letter-spacing:0;font-weight:400;color:#666}
.karten{display:block;margin-top:1vh;font-style:italic;color:var(--blau)}
.mitbild{display:grid;grid-template-columns:1fr 26vw;gap:3vw;align-items:start}.mitbild .bloecke{display:flex;flex-direction:column;gap:2.2vh}
.mitbild img,.titelbild{width:100%;background:#fff;border-radius:1.6vh;padding:1.5vh;border:.3vh solid #d9d6cf}
.titel{display:grid;grid-template-columns:1fr 30vw;gap:4vw;align-items:center;flex:1}
.leiste{position:fixed;left:0;right:0;bottom:0;height:6vh;background:var(--blau2);color:#fff;display:flex;align-items:center;gap:2vw;padding:0 3vw;font-size:2vh}
.leiste .bar{flex:1;height:1vh;background:#ffffff33;border-radius:1vh;overflow:hidden}.leiste .bar i{display:block;height:100%;background:var(--rost)}
.leiste button{background:none;border:.2vh solid #fff8;color:#fff;border-radius:.8vh;padding:.6vh 1.4vh;font:inherit;cursor:pointer}
"""

INPUT_JS = """
const F=[...document.querySelectorAll('.folie')];let i=0;
function fit(f){const z=f.querySelectorAll(':scope>*');let s=1;z.forEach(x=>x.style.zoom=1);
while(f.scrollHeight>f.clientHeight+1&&s>0.6){s-=0.04;z.forEach(x=>x.style.zoom=s)}}
function zeig(n){i=Math.max(0,Math.min(F.length-1,n));F.forEach((f,k)=>f.classList.toggle('an',k===i));fit(F[i]);
document.querySelector('.bar i').style.width=((i+1)/F.length*100)+'%';document.querySelector('.nr').textContent=(i+1)+' / '+F.length;}
function auf(){const z=F[i].querySelector('.antwort.zu');if(z){z.classList.remove('zu');return true}return false}
document.addEventListener('keydown',e=>{if(e.key===' '||e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();if(!auf())zeig(i+1)}
else if(e.key==='ArrowLeft'||e.key==='PageUp')zeig(i-1);else if(e.key==='a'||e.key==='A')document.querySelectorAll('.antwort.zu').forEach(x=>x.classList.remove('zu'));
else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}});
document.querySelectorAll('.antwort').forEach(a=>a.addEventListener('click',()=>a.classList.remove('zu')));
addEventListener('resize',()=>fit(F[i]));
document.querySelector('.vor').onclick=()=>{if(!auf())zeig(i+1)};document.querySelector('.zur').onclick=()=>zeig(i-1);zeig(0);
"""


def block_html(name: str, text: str, input_: bool) -> str:
    cls = "frage" if name == "Frage" else "antwort" if name == "Gesicherte Antwort" else ""
    zu = " zu" if (input_ and cls == "antwort") else ""
    return "<div class='block %s%s'><b>%s</b><div class=inhalt>%s</div></div>" % (cls, zu, esc(name), md(text))


def mit_bild(a: dict, bloecke: str) -> str:
    if not a.get("bild"):
        return bloecke
    return "<div class=mitbild><div class=bloecke>%s</div><img src='%s' alt=''></div>" % (bloecke, bild_uri(a["bild"]))


def input_html(e: dict) -> str:
    kopf = "Deutsch · Jahrgang 5 · Märchen · Etappe %d" % e["etappe"]
    tb = "<img class=titelbild src='%s' alt=''>" % bild_uri(e["titelbild"]) if e.get("titelbild") else ""
    folien = ["<section class=folie><div class=kopf>%s</div><div class=titel><div><h1>%s</h1><br><div class=ziel><b>Dein Ziel:</b> %s</div></div>%s</div></section>"
              % (esc(kopf), esc(e["titel"]), esc(e["ziel"]), tb)]
    for n, a in enumerate(e["abschnitte"], 1):
        laenge = sum(len(t) for _, t in a["bloecke"]) + (150 if a.get("bild") else 0)
        lang = " lang xlang" if laenge > 700 else " lang" if laenge > 480 else ""
        folien.append("<section class='folie%s'><div class=kopf>%s · %d/%d</div><h2>%s</h2>%s</section>" % (
            lang, esc(kopf), n, len(e["abschnitte"]), esc(a["titel"]), mit_bild(a, "".join(block_html(b, t, True) for b, t in a["bloecke"]))))
    return ("<!doctype html><html lang=de><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>Input Etappe %d · %s</title><style>%s%s</style></head><body>%s"
            "<div class=leiste><button class=zur>◀</button><span class=nr></span><div class=bar><i></i></div>"
            "<span>Leertaste: weiter/aufdecken · A: alle Antworten · F: Vollbild</span><button class=vor>▶</button></div>"
            "<script>%s</script></body></html>" % (e["etappe"], esc(e["titel"]), font_css(), INPUT_CSS, "".join(folien), INPUT_JS))


# ------------------------------------------------------------ Druck (Merkblatt, Blätter, Nachweise)
DRUCK_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:'Andika',sans-serif;color:#111;background:#fff}
@page{size:A4;margin:13mm 15mm 19mm 15mm}
.meta{font-size:14pt;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#444}
h1{line-height:1.12;margin:1mm 0 3mm}
em{font-style:italic}strong{font-weight:700}
.karten{display:block;margin-top:2mm;padding:2mm 3mm;border:1pt solid #777;border-radius:2mm;font-style:italic}
.kopfzeile{display:flex;justify-content:space-between;align-items:flex-end;gap:5mm}.kopfzeile img{height:30mm;width:auto;flex:none;margin-bottom:2mm}
.abbild{float:right;width:30mm;margin:0 0 2mm 3mm}
"""

MERK_CSS = """
body{font-size:12.5pt;line-height:1.36}
h1{font-size:24pt}.ziel{font-size:14pt;border:1.5pt solid #111;border-radius:2.5mm;padding:2.5mm 3.5mm;margin-bottom:4mm}
h2{font-size:16pt;margin:4mm 0 1.5mm;break-after:avoid}
.spalten{column-count:2;column-gap:7mm;column-fill:auto}
.block{margin:0 0 2mm;padding:2mm 3mm;border-left:2pt solid #999;break-inside:avoid}
.block>b{display:block;font-size:12pt;letter-spacing:.05em;text-transform:uppercase;color:#444}
.block.frage{border-left:2pt solid #111}
.block.antwort{border:1.2pt solid #111;border-left-width:4pt;background:#f0f0f0;border-radius:0 2mm 2mm 0}
"""

BLATT_CSS = """
body{font-size:16pt;line-height:1.34}
h1{font-size:27pt}
.brauchst{font-size:14pt;margin-bottom:2.5mm}
.kasten{border:2pt solid #111;border-radius:3mm;padding:2.5mm 4mm 2mm;margin-bottom:3.5mm;position:relative}
.kasten.frei{border-style:dashed}
.etikett{display:inline-block;font-size:14pt;font-weight:700;letter-spacing:.08em;padding:.5mm 2.5mm;border-radius:1.5mm;margin-bottom:2mm}
.pflicht .etikett{background:#111;color:#fff}.frei .etikett{border:1.5pt dashed #111}
.sprache .etikett{border:1.5pt solid #111}
ol{padding-left:9mm}li{margin-bottom:2mm}li::marker{font-weight:700}
.bsp{display:block;font-size:14pt;color:#333;margin-top:.5mm}
"""

GN_CSS = """
body{font-size:15pt;line-height:1.38}
h1{font-size:24pt}
.namen{display:flex;gap:8mm;font-size:14pt;margin:2mm 0 4mm}.namen span{flex:1;border-bottom:1pt solid #111;padding-bottom:1mm}
.hinweis{font-size:14pt;border:1.5pt solid #111;border-radius:2.5mm;padding:2mm 3mm;margin-bottom:4mm}
.auf{margin-bottom:4mm;break-inside:avoid}.auf .nr{font-weight:700}
.linie{height:10.5mm;border-bottom:1pt solid #555}
table{width:100%;border-collapse:collapse;font-size:14pt}td,th{border:1pt solid #111;padding:2mm 2mm;vertical-align:top;text-align:left}
th{background:#eee}.k{width:9mm;text-align:center}
.feld{border:1.2pt solid #111;border-radius:2mm;min-height:24mm;padding:2mm 3mm;margin-top:3mm;font-size:14pt}
.erg{font-size:16pt;margin-top:3mm}
.anfang{border:1.5pt solid #111;border-radius:2.5mm;padding:2.5mm 3.5mm;margin:2mm 0 1mm;font-size:15pt;line-height:1.45}
.anfang .q{font-size:14pt;font-style:italic;color:#444}.anfang .fnz{font-size:14pt;border-top:1pt solid #777;margin-top:2mm;padding-top:1mm}
"""

FOERDER_CSS = """
body{font-size:16.5pt;line-height:1.45}
h1{font-size:26pt}
.auftrag{border:2pt solid #111;border-radius:3mm;padding:3mm 4mm;margin-bottom:4mm;break-inside:avoid;display:flex;gap:4mm}
.sym{font-size:22pt;width:12mm;text-align:center;flex:none}
.opt{display:flex;gap:3mm;align-items:center;margin:1.5mm 0}.box{width:8mm;height:8mm;border:1.5pt solid #111;flex:none;border-radius:1mm}
.ws{border:1.5pt dashed #111;border-radius:2mm;padding:1.5mm 3mm;margin:2mm 0;display:flex;gap:6mm;flex-wrap:wrap}
.luecke{display:inline-block;min-width:34mm;border-bottom:1.2pt solid #111}
.linie{height:12mm;border-bottom:1pt solid #555}
.fseite{height:262mm;position:relative;break-after:page;overflow:hidden}.fseite:last-child{break-after:auto}
.loesung{position:absolute;left:0;right:0;bottom:0;border-top:1.5pt dashed #111;padding-top:2mm;transform:rotate(180deg);font-size:14pt;color:#333}
.loesung::after{content:"✂ hier umknicken";position:absolute;right:0;top:-6mm;font-size:12pt;transform:rotate(180deg)}
.merk{border:2pt solid #111;border-radius:3mm;padding:3mm 4mm;margin-bottom:3mm}.merk b{display:block;font-size:14pt;letter-spacing:.06em;text-transform:uppercase}
"""


def doc(css: str, body: str) -> str:
    return "<!doctype html><html lang=de><head><meta charset=utf-8><style>%s%s%s</style></head><body>%s</body></html>" % (
        font_css(), DRUCK_CSS, css, body)


def drucke(pg, html_: str, pdf: Path, fuss_rechts: str) -> float:
    pdf.parent.mkdir(parents=True, exist_ok=True)
    pg.set_content(html_, wait_until="load")
    pg.evaluate("document.fonts.ready")
    fuss = ("<div style='font-size:14pt;width:100%%;padding:0 15mm;display:flex;justify-content:space-between;"
            "font-family:sans-serif;color:#444'><span>%s</span><span>%s · Seite <span class=pageNumber></span>/<span class=totalPages></span></span></div>"
            % (esc(FUSS), esc(fuss_rechts)))
    pg.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True, display_header_footer=True,
           header_template="<span></span>", footer_template=fuss)
    return kleinste_schrift(pdf)


def merkblatt_html(e: dict) -> str:
    tb = "<img src='%s' alt=''>" % bild_uri(e["titelbild"]) if e.get("titelbild") else ""
    teile = ["<div class=kopfzeile><div><div class=meta>Merkblatt · Etappe %d</div><h1>%s</h1></div>%s</div><div class=ziel><b>Dein Ziel:</b> %s</div>"
             % (e["etappe"], esc(e["titel"]), tb, esc(e["ziel"]))]
    for n, a in enumerate(e["abschnitte"], 1):
        ab = "<img class=abbild src='%s' alt=''>" % bild_uri(a["bild"]) if a.get("bild") else ""
        teile.append("<h2>%d · %s</h2>%s%s" % (n, esc(a["titel"]), ab, "".join(block_html(b, t, False) for b, t in a["bloecke"])))
    return doc(MERK_CSS, teile[0] + "<div class=spalten style='column-fill:balance'>%s</div>" % "".join(teile[1:]))


def blatt_html(e: dict, b: dict) -> str:
    li = []
    for p in b["pflicht"]:
        s = md(p["text"])
        if p.get("beispiel"):
            s += "<span class=bsp>Beispiel: %s</span>" % esc(p["beispiel"])
        if p.get("karten"):
            s += "<span class=karten>%s</span>" % esc(KARTEN)
        li.append("<li>%s</li>" % s)
    sg = "<img src='%s' alt=''>" % bild_uri(b["signet"]) if b.get("signet") else ""
    teile = ["<div class=kopfzeile><div><div class=meta>Etappe %d · Blatt %s</div><h1>%s</h1><div class=brauchst><b>Das brauchst du:</b> %s</div></div>%s</div>"
             % (e["etappe"], b["nr"], esc(b["titel"]), esc(b["brauchst"]), sg),
             "<div class='kasten pflicht'><span class=etikett>PFLICHT</span><ol>%s</ol></div>" % "".join(li)]
    if b.get("sprachdetektiv"):
        teile.append("<div class='kasten sprache'><span class=etikett>SPRACHDETEKTIV · PFLICHT</span><div>%s</div></div>" % md(b["sprachdetektiv"]))
    if b.get("vertiefung"):
        teile.append("<div class='kasten frei'><span class=etikett>FREIWILLIG</span><div>%s</div></div>" % md(b["vertiefung"]))
    return doc(BLATT_CSS, "".join(teile))


def gn_aufgaben_html(e: dict, nw: dict, v: str) -> str:
    var = nw["varianten"][v]
    titel = {t["id"]: t["titel"] for t in json.loads((ROOT / "inhalt" / "texte.json").read_text("utf-8"))["texte"]}
    sg = "<img src='%s' alt=''>" % bild_uri(nw["signet"]) if nw.get("signet") else ""
    teile = ["<div class=kopfzeile><div><div class=meta>Gelingensnachweis %d · Variante %s</div><h1>%s</h1></div>%s</div>" % (e["etappe"], v, esc(nw["titel"]), sg),
             "<div class=namen><span>Name:</span><span>Datum:</span></div>",
             "<div class=hinweis>Du brauchst: das Märchen „%s“. Den Märchenanfang „%s“ findest du bei Aufgabe 5. "
             "Schreibe auf dieses Blatt. Arbeite allein. Merkblatt und Märchenkarten bleiben in der Tasche.</div>" % (esc(titel[var["maerchen"]]), esc(titel[var["anfang"]]))]
    texte = {t["id"]: t for t in json.loads((ROOT / "inhalt" / "texte.json").read_text("utf-8"))["texte"]}
    for n, a in enumerate(var["aufgaben"], 1):
        box = ""
        if a["ziel"].endswith(".4"):  # Weiterschreiben: Anfang direkt über der Aufgabe
            t = texte[var["anfang"]]
            fn = " ".join("<i>%s:</i> %s" % (esc(f["stelle"]), esc(f["erklaerung"])) for f in t.get("fussnoten", []))
            box = ("<div class=anfang><b>%s</b> <span class=q>(%s)</span><div>%s</div>%s</div>" % (
                esc(t["titel"]), esc(t["quelle"]), esc(" ".join(p.get("absatz") or " ".join(p["vers"]) for p in t["text"])),
                "<div class=fnz>%s</div>" % fn if fn else ""))
        teile.append("<div class=auf><span class=nr>%d.</span> %s%s%s</div>" % (n, md(a["text"]), box, "<div class=linie></div>" * a["linien"]))
    return doc(GN_CSS, "".join(teile))


def gn_rueckmeldung_html(e: dict, nw: dict, v: str) -> str:
    rows = "".join("<tr><td>%s</td><td class=k>☐</td><td class=k>☐</td><td>%s</td><td style='width:30mm'></td></tr>"
                   % (esc(z["kind"]), esc(z["ueben"])) for z in nw["ziele"])
    return doc(GN_CSS, (
        "<div class=meta>Gelingensnachweis %d · Variante %s · Rückmeldung</div><h1>Das hast du gezeigt</h1>"
        "<table><tr><th>Dein Ziel</th><th class=k>✓</th><th class=k>…</th><th>Übe mit</th><th>erneut gezeigt am</th></tr>%s</table>"
        "<div class=erg>✓ = gezeigt · … = noch offen &nbsp;&nbsp; <b>Ergebnis: ____ von 5</b> &nbsp; (ab 4 von 5: weiter zu Etappe %d)</div>"
        "<div class=feld><b>Das gelingt dir schon:</b></div><div class=feld><b>Dein nächster Schritt:</b></div>"
        "<div style='font-size:14pt;margin-top:3mm'>Rückmeldung der Lehrkraft</div>") % (e["etappe"], v, rows, e["etappe"] + 1))


def gn_erwartung_html(e: dict, nw: dict) -> str:
    teile = ["<div class=meta>Lehrkraft · Gelingensnachweis %d</div><h1>Erwartungshorizont</h1>" % e["etappe"],
             "<table><tr><th>Ziel</th><th>erreicht, wenn …</th></tr>%s</table>" % "".join(
                 "<tr><td><b>%s</b> %s</td><td>%s</td></tr>" % (z["id"], esc(z["kurz"]), esc(z["lehrkraft"])) for z in nw["ziele"])]
    for v, var in nw["varianten"].items():
        teile.append("<h2 style='font-size:17pt;margin:5mm 0 2mm'>Variante %s</h2><table><tr><th>Nr.</th><th>Ziel</th><th>Erwartung</th></tr>%s</table>" % (
            v, "".join("<tr><td>%d</td><td>%s</td><td>%s</td></tr>" % (n, a["ziel"], md(a["erwartung"])) for n, a in enumerate(var["aufgaben"], 1))))
    teile.append("<p style='font-size:14pt;margin-top:4mm'>4 von 5 Zielen = Freigabe. Gleichwertige Lösungen gelten. "
                 "Unter 4/5: offenes Ziel benennen, mit dem genannten Blatt üben, Variante B oder Teilnachweis.</p>")
    return doc(GN_CSS, "".join(teile))


# ------------------------------------------------------------ Förder
SYM = {"lesen": "👁", "ankreuzen": "☑", "zuordnen": "↔", "luecke": "▭", "schreiben": "✎"}


def f_auftrag(a: dict) -> str:
    inner, loes = md(a["text"]), ""
    if a["art"] == "ankreuzen":
        inner += "".join("<div class=opt><span class=box></span>%s</div>" % esc(o) for o in a["optionen"])
        loes = ", ".join(a["loesung"])
    elif a["art"] == "zuordnen":
        inner += "".join("<div class=opt><span class=box></span>%s</div>" % esc(s) for s, _ in a["paare"])
        loes = " · ".join("%s %s" % (k, s) for s, k in a["paare"])
    elif a["art"] == "luecke":
        woerter = re.findall(r"\{(.+?)\}", a["satz"]) + a.get("ablenker", [])
        random.Random(a["satz"]).shuffle(woerter)
        inner += "<div class=ws>%s</div><div>%s</div>" % ("".join("<span>%s</span>" % esc(w) for w in woerter),
                                                       re.sub(r"\{.+?\}", "<span class=luecke></span>", esc(a["satz"])))
        loes = ", ".join(re.findall(r"\{(.+?)\}", a["satz"]))
    elif a["art"] == "schreiben":
        inner += "<div class=linie></div>" * a.get("linien", 2)
    return "<div class=auftrag data-loes='%s'><div class=sym>%s</div><div style='flex:1'>%s</div></div>" % (
        html.escape(loes, quote=True), SYM[a["art"]], inner)


F_JS = """
<script>
(() => {
  const q = document.getElementById('q'); const kopf = q.querySelector('.fkopf'); const auf = [...q.querySelectorAll('.auftrag')];
  const neu = () => { const s = document.createElement('div'); s.className = 'fseite'; const k = document.createElement('div'); k.className='inhalt';
    s.appendChild(k); const l = document.createElement('div'); l.className = 'loesung'; s.appendChild(l); document.body.appendChild(s); return s; };
  let s = neu(); s.querySelector('.inhalt').appendChild(kopf); let nr = 0;
  const raum = (x) => x.getBoundingClientRect().height - x.querySelector('.inhalt').getBoundingClientRect().height - x.querySelector('.loesung').getBoundingClientRect().height - 18;
  auf.forEach(a => { const inh = s.querySelector('.inhalt'); inh.appendChild(a);
    if (raum(s) < 0 && inh.children.length > 1) { inh.removeChild(a); s = neu(); s.querySelector('.inhalt').appendChild(a); }
    nr += 1; if (a.dataset.loes) { const l = s.querySelector('.loesung'); l.innerHTML += (l.innerHTML ? ' | ' : '<b>Lösung:</b> ') + nr + ': ' + a.dataset.loes; } });
  document.querySelectorAll('.fseite').forEach(x => { const l = x.querySelector('.loesung'); if (!l.innerHTML) l.remove(); });
  q.remove();
})();
</script>"""


def f_blatt_html(e: dict, b: dict, titel_meta: str) -> str:
    sg = "<img src='%s' alt=''>" % bild_uri(b["signet"]) if b.get("signet") else ""
    teile = "<div class=fkopf><div class=kopfzeile><div><div class=meta>%s</div><h1>%s</h1></div>%s</div></div>%s" % (
        esc(titel_meta), esc(b["titel"]), sg, "".join(f_auftrag(a) for a in b["auftraege"]))
    return doc(FOERDER_CSS, "<div id=q>%s</div>%s" % (teile, F_JS))


def f_merkkarte_html(e: dict) -> str:
    f = e["foerder"]
    sg = "<img src='%s' alt=''>" % bild_uri(f["bild"]) if f.get("bild") else ""
    return doc(FOERDER_CSS, "<div class=kopfzeile><div><div class=meta>Merkkarte · Etappe %dF</div><h1>%s</h1></div>%s</div>%s" % (
        e["etappe"], esc(e["titel"]), sg, "".join("<div class=merk><b>%s</b>%s</div>" % (esc(k), md(t)) for k, t in f["merkkarte"])))


def f_gn_html(e: dict) -> tuple[str, str]:
    nw = e["foerder"]["nachweis"]
    kopf = ("<div class=fkopf><div class=meta>Gelingensnachweis %dF</div><h1>%s</h1><div style='display:flex;gap:8mm;font-size:14pt;margin-bottom:3mm'>"
            "<span style='flex:1;border-bottom:1pt solid #111'>Name:</span><span style='flex:1;border-bottom:1pt solid #111'>Datum:</span></div></div>"
            % (e["etappe"], esc(nw["titel"])))
    # Nachweis: keine Lösungsstreifen
    auf = doc(FOERDER_CSS, "<div id=q>%s%s</div>%s" % (kopf, "".join(re.sub(r"data-loes='[^']*'", "data-loes=''", f_auftrag(a)) for a in nw["auftraege"]), F_JS))
    rows = "".join("<tr><td>%s</td><td class=k>☐</td><td class=k>☐</td></tr>" % esc(z["kind"]) for z in nw["ziele"])
    rueck = doc(GN_CSS, "<div class=meta>Gelingensnachweis %dF · Rückmeldung</div><h1>Das hast du gezeigt</h1>"
                "<table><tr><th>Dein Ziel</th><th class=k>✓</th><th class=k>…</th></tr>%s"
                "<tr><td>Eigenes Förderziel: ______________________</td><td class=k>☐</td><td class=k>☐</td></tr></table>"
                "<div class=erg><b>Ergebnis: ____ von ____</b> (Ziele vorher vereinbart; ab 80 %% weiter)</div>"
                "<div class=feld><b>Das gelingt dir schon:</b></div><div class=feld><b>Dein nächster Schritt:</b></div>"
                "<div style='font-size:14pt;margin-top:3mm'>Lehrkraft-Hinweis: %s</div>" % (
                    e["etappe"], rows, esc(" · ".join("%s %s" % (z["id"], z["lehrkraft"]) for z in nw["ziele"]))))
    return auf, rueck


# ------------------------------------------------------------ Zusammenfügen
def verbinde(teile: list[Path], ziel: Path) -> int:
    out = fitz.open()
    for t in teile:
        out.insert_pdf(fitz.open(t))
    out.save(ziel)
    return len(out)


def main(n: int) -> int:
    e = json.loads((ROOT / "inhalt" / f"etappe{n}.json").read_text("utf-8"))
    aus = ROOT / "ausgabe" / f"etappe{n}"
    tmp = aus / "_teile"
    tmp.mkdir(parents=True, exist_ok=True)
    fehler = []
    (aus / f"Input_Etappe{n}.html").write_text(input_html(e), encoding="utf-8")
    # Gleichheit Input = Merkblatt (Text der Blöcke)
    mb, ip = merkblatt_html(e), input_html(e)
    for a in e["abschnitte"]:
        for _, t in a["bloecke"]:
            if md(t) not in mb or md(t) not in ip:
                fehler.append("Input/Merkblatt ungleich: " + t[:40])
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()
        bericht = []

        def mach(html_: str, pdf: Path, fuss: str, minpt: float):
            mn = drucke(pg, html_, pdf, fuss)
            seiten = len(fitz.open(pdf))
            bericht.append("%-34s %d S.  min %.1f pt%s" % (pdf.name, seiten, mn, "" if mn >= minpt else "  << unter %g pt" % minpt))
            if mn < minpt:
                fehler.append(pdf.name)
            return pdf

        mach(mb, aus / f"Merkblatt_{n}_A4.pdf", f"Merkblatt {n}", 12)
        blaetter = [mach(blatt_html(e, b), aus / f"Blatt_{b['nr']}_A4.pdf", f"Etappe {n} · Blatt {b['nr']}", 14) for b in e["blaetter"]]
        material = [TEXTE / f"{m}_A4.pdf" for m in e["material"]]
        s = verbinde(material + blaetter, aus / f"Schuelerpaket_Etappe{n}_A4.pdf")
        bericht.append("%-34s %d S.  (Material, dann Blätter)" % (f"Schuelerpaket_Etappe{n}_A4.pdf", s))
        nw = e["nachweis"]
        for v, var in nw["varianten"].items():
            a = mach(gn_aufgaben_html(e, nw, v), tmp / f"gn_{v}_auf.pdf", f"GN{n} {v}", 14)
            r = mach(gn_rueckmeldung_html(e, nw, v), tmp / f"gn_{v}_rueck.pdf", f"GN{n} {v} · Rückmeldung", 14)
            s = verbinde([TEXTE / f"{var['maerchen']}_A4.pdf", a, r], aus / f"GN{n}_{v}_A4.pdf")
            bericht.append("%-34s %d S.  (Material, Aufgaben, Rückmeldung)" % (f"GN{n}_{v}_A4.pdf", s))
        mach(gn_erwartung_html(e, nw), aus / f"GN{n}_Erwartungshorizont_A4.pdf", f"GN{n} · Lehrkraft", 12)
        # Förder
        f = e["foerder"]
        fa = aus / "foerder"
        mk = mach(f_merkkarte_html(e), tmp / "f_merk.pdf", f"Merkkarte {n}F", 14)
        fb = [mach(f_blatt_html(e, b, "Etappe %dF · Blatt %s" % (n, b["nr"])), tmp / f"f_{b['nr']}.pdf", f"Blatt {b['nr']}", 14) for b in f["blaetter"]]
        fa.mkdir(exist_ok=True)
        s = verbinde([mk, TEXTE / f"{f['material']}_A4.pdf"] + fb, fa / f"Foerder_Etappe{n}_A4.pdf")
        bericht.append("%-34s %d S.  (Merkkarte, Material, Blätter)" % (f"foerder/Foerder_Etappe{n}_A4.pdf", s))
        auf, rueck = f_gn_html(e)
        a = mach(auf, tmp / "f_gn_auf.pdf", f"GN{n}F", 14)
        r = mach(rueck, tmp / "f_gn_rueck.pdf", f"GN{n}F · Rückmeldung", 14)
        s = verbinde([a, r], fa / f"GN{n}F_A4.pdf")
        bericht.append("%-34s %d S." % (f"foerder/GN{n}F_A4.pdf", s))
        br.close()
    print("\n".join(bericht))
    for x in tmp.iterdir():
        x.unlink()
    tmp.rmdir()
    if fehler:
        print("FEHLER:", *fehler, sep="\n  ")
        return 1
    print("Prüfung: alle Schülerseiten ≥ 14 pt, Merkblatt ≥ 12 pt, Input = Merkblatt.")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 1))

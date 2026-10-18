"""Gemeinsame Satz-Hilfen für alle Generatoren der Reihe Märchen.

- Andika eingebettet (keine Netzladung)
- Seitenumbruch in JavaScript: feste A4-Seiten, Zeilennummern, Fußnoten am Seitenende
- Prüfung der Mindestschriftgröße mit PyMuPDF
"""
from __future__ import annotations

import base64
import html
import re
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
FUSS = "Deutsch · Jahrgang 5 · Märchen"


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def font_css() -> str:
    out = []
    for weight, style in [(400, "normal"), (700, "normal"), (400, "italic"), (700, "italic")]:
        f = FONTS / f"andika-latin-{weight}-{style}.woff2"
        out.append("@font-face{font-family:'Andika';font-weight:%d;font-style:%s;"
                   "src:url(data:font/woff2;base64,%s) format('woff2');}" % (weight, style, b64(f)))
    for weight in (400, 700):
        f = FONTS / f"andika-latin-ext-{weight}-normal.woff2"
        out.append("@font-face{font-family:'Andika';font-weight:%d;font-style:normal;"
                   "unicode-range:U+0100-024F,U+1E00-1EFF;"
                   "src:url(data:font/woff2;base64,%s) format('woff2');}" % (weight, b64(f)))
    return "\n".join(out)


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# ------------------------------------------------------------ Wörter und Fußnoten
def fussnoten_positionen(absaetze: list[str], fussnoten: list[dict]) -> dict[tuple[int, int], list[int]]:
    """Erste Fundstelle (ganzes Wort) je Fußnote -> (Absatz, Zeichenende) -> Fußnoten-Indizes."""
    pos: dict[tuple[int, int], list[int]] = {}
    for i, fn in enumerate(fussnoten):
        rx = re.compile(r"(?<!\w)" + re.escape(fn["stelle"]) + r"(?!\w)")
        for a, text in enumerate(absaetze):
            m = rx.search(text)
            if m:
                pos.setdefault((a, m.end()), []).append(i)
                break
        else:
            raise ValueError("Fußnote ohne Fundstelle: %r" % fn["stelle"])
    return pos


def wort_spans(text: str, a: int, marken: dict[tuple[int, int], list[int]], nummern: dict[int, int]) -> str:
    """Jedes Wort als <span class=w>; Fußnotenzeichen hängen am Wort, das die Fundstelle beendet."""
    out = []
    for m in re.finditer(r"\S+", text):
        w = esc(m.group())
        sup = ""
        for (aa, ende), idx in marken.items():
            if aa == a and m.start() < ende <= m.end():
                for i in idx:
                    sup += "<sup class=fz data-fn='%d'>%d</sup>" % (i, nummern[i])
                if ende < m.end():  # Satzzeichen nach der Fundstelle: Zeichen davor setzen
                    cut = ende - m.start()
                    w = esc(m.group()[:cut]) + sup + esc(m.group()[cut:])
                    sup = ""
        out.append("<span class=w>%s%s</span>" % (w, sup))
    return " ".join(out)


# ------------------------------------------------------------ Seitenumbruch
SEITEN_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:A4;margin:0}
body{font-family:'Andika',sans-serif;color:#111;background:#fff}
.seite{width:210mm;height:297mm;padding:14mm 16mm 0 16mm;position:relative;overflow:hidden;break-after:page}
.koerper{position:relative}
.fussbereich{position:absolute;left:16mm;right:16mm;bottom:20mm;font-size:14pt;line-height:1.3}
.fussbereich:not(:empty){border-top:1pt solid #111;padding-top:2mm}
.fn{display:flex;gap:2mm;margin-bottom:.8mm}.fn b{min-width:6mm;text-align:right}
.fusszeile{position:absolute;left:16mm;right:16mm;bottom:9mm;font-size:14pt;color:#444;display:flex;justify-content:space-between}
sup.fz{font-size:11pt;font-weight:700;vertical-align:super;line-height:0;margin-left:.3mm}
.ln{position:relative;white-space:nowrap}
.ln .nr{position:absolute;left:-13mm;width:9mm;text-align:right;font-size:14pt;color:#555}
#quelle{position:absolute;left:-9999px;top:0;width:178mm}
"""

UMBRUCH_JS = r"""
(cfg) => {
  // 1. Absätze in Zeilen zerlegen (gemessen an der echten Schrift)
  const q = document.getElementById('quelle');
  let n = 0;
  q.querySelectorAll('.par').forEach(p => {
    const ws = [...p.querySelectorAll('.w')]; const zeilen = []; let top = null;
    ws.forEach(w => { const t = Math.round(w.getBoundingClientRect().top);
      if (top === null || Math.abs(t - top) > 4) { zeilen.push([]); top = t; } zeilen[zeilen.length-1].push(w); });
    const neu = zeilen.map(z => { const d = document.createElement('div'); d.className = 'ln';
      if (p.dataset.nr !== 'nein') { n += 1; d.dataset.zeile = n;
        if (n % 5 === 0) { const s = document.createElement('span'); s.className = 'nr'; s.textContent = n; d.appendChild(s); } }
      z.forEach((w, i) => { if (i) d.appendChild(document.createTextNode(' ')); d.appendChild(w); });
      return d; });
    p.replaceChildren(...neu);
  });
  // 2. Blöcke auf Seiten verteilen: Zeilen einzeln, alles andere als Ganzes
  const bloecke = [];
  [...q.children].forEach(c => {
    if (c.classList.contains('par')) {
      const lines = [...c.children];
      lines.forEach((l, i) => { const h = document.createElement('div'); h.className = c.className;
        h.style.marginTop = i ? '0' : ''; h.style.marginBottom = i < lines.length - 1 ? '0' : '';
        h.appendChild(l); bloecke.push(h); });
    } else bloecke.push(c);
  });
  const fns = cfg.fussnoten; const seiten = []; const hoehe = cfg.hoehe_mm * 96 / 25.4;
  let seite, koerper, fuss, startZeile;
  const neueSeite = () => {
    seite = document.createElement('div'); seite.className = 'seite';
    koerper = document.createElement('div'); koerper.className = 'koerper';
    fuss = document.createElement('div'); fuss.className = 'fussbereich';
    seite.append(koerper, fuss); document.body.appendChild(seite); seiten.push(seite);
  };
  const passt = () => koerper.getBoundingClientRect().height + fuss.getBoundingClientRect().height + 14 <= hoehe;
  neueSeite();
  bloecke.forEach(b => {
    const neuFn = [...b.querySelectorAll('sup.fz')].map(s => +s.dataset.fn);
    const add = () => { koerper.appendChild(b); neuFn.forEach(i => { const d = document.createElement('div'); d.className = 'fn';
        d.innerHTML = '<b>' + fns[i].nr + '</b><span><i>' + fns[i].stelle + ':</i> ' + fns[i].erklaerung + '</span>'; d.dataset.fn = i; fuss.appendChild(d); }); };
    add();
    if (!passt() && koerper.children.length > 1) {
      koerper.removeChild(b); neuFn.forEach(i => fuss.querySelector("[data-fn='" + i + "']").remove());
      neueSeite(); add();
    }
  });
  // 3. Fußzeilen
  const zeilenJeSeite = seiten.map(s => [...s.querySelectorAll('.ln[data-zeile]')].map(l => +l.dataset.zeile));
  seiten.forEach((s, i) => { const f = document.createElement('div'); f.className = 'fusszeile';
    f.innerHTML = '<span>' + cfg.fuss_links + '</span><span>' + cfg.fuss_rechts + ' · Seite ' + (i+1) + '/' + seiten.length + '</span>'; s.appendChild(f); });
  q.remove();
  return {zeilen: n, seiten: seiten.length, zeilen_je_seite: zeilenJeSeite.map(z => z.length ? [z[0], z[z.length-1]] : null)};
}
"""


def render_seiten(pg, inhalt_html: str, css: str, fussnoten: list[dict], pdf: Path,
                  fuss_rechts: str, hoehe_mm: float = 263) -> dict:
    """inhalt_html: Blöcke; Fließtext als <div class=par>…<span class=w>…</div>.
    hoehe_mm: nutzbare Höhe über der Fußzeile (297 − 14 oben − 20 unten)."""
    doc = ("<!doctype html><html lang='de'><head><meta charset='utf-8'><style>%s%s%s</style></head>"
           "<body><div id=quelle>%s</div></body></html>" % (font_css(), SEITEN_CSS, css, inhalt_html))
    pg.set_viewport_size({"width": 900, "height": 1200})
    pg.set_content(doc, wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.emulate_media(media="print")
    info = pg.evaluate(UMBRUCH_JS, {"fussnoten": fussnoten, "hoehe_mm": hoehe_mm,
                                    "fuss_links": esc(FUSS), "fuss_rechts": esc(fuss_rechts)})
    pdf.parent.mkdir(parents=True, exist_ok=True)
    pg.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True)
    pg.emulate_media(media="screen")
    return info


def kleinste_schrift(pdf: Path, ausnahmen: tuple[float, ...] = ()) -> float:
    """Kleinste Schriftgröße im PDF (Fußnotenzeichen als ausnahmen übergeben)."""
    mins = []
    for p in fitz.open(pdf):
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["text"].strip() and round(s["size"], 1) not in ausnahmen:
                        mins.append(round(s["size"], 1))
    return min(mins) if mins else 0

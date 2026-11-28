#!/usr/bin/env python3
"""Fassung 4 · alle fünf Inputs als eine interaktive Präsentation (laut denken und Strategien erklären).

    python3 tools/build_inputs_f4.py

Inhalt: inhalt/f4/inputs_laut.json · Vorlage: tools/vorlagen/inputs_f4.html
Ausgabe: apps/inputs/index.html (eine Datei, offline). Prüft jede Folie und jeden Schritt
in 1280×720, 1024×768 und 1920×1080: nichts läuft über, keine Fehler in der Konsole.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from satz import ROOT, font_css  # noqa: E402

D = json.loads((ROOT / "inhalt" / "f4" / "inputs_laut.json").read_text("utf-8"))
OUT = ROOT / "apps" / "inputs" / "index.html"


def anzahl(fo):
    return {"auftrag": len(fo.get("denke", [])), "strategie": len(fo.get("fragen", [])) + 1, "laut": len(fo.get("schritte", [])),
            "ergebnis": len(fo.get("punkte", [])), "jetzt": 2}[fo["typ"]]


def pruefe_daten():
    fehler = []
    for i in D["inputs"]:
        for fo in i["folien"]:
            if fo["typ"] != "laut":
                continue
            zonen = {z[0] for z in fo["ergebnis"].get("zonen", [])}
            for n, x in enumerate(fo["schritte"], 1):
                for m in x["mark"]:
                    if m not in fo["text"]:
                        fehler.append(f"Input {i['nr']} „{fo['titel']}“ Schritt {n}: Stelle nicht im Text: {m}")
                for z, _ in x.get("add", []):
                    if z not in zonen:
                        fehler.append(f"Input {i['nr']} Schritt {n}: unbekannte Zone {z}")
                if x.get("strike") and x["strike"] not in zonen:
                    fehler.append(f"Input {i['nr']} Schritt {n}: unbekannte Zone {x['strike']}")
    return fehler


def main():
    fehler = pruefe_daten()
    if fehler:
        print("FEHLER:", *fehler, sep="\n  ")
        return 1
    html = (ROOT / "tools" / "vorlagen" / "inputs_f4.html").read_text("utf-8")
    html = html.replace("__FONTS__", font_css()).replace("__DATA__", json.dumps(D, ensure_ascii=False))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    n_ans = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for w, h in ((1280, 720), (1024, 768), (1920, 1080)):
            pg = br.new_page(viewport={"width": w, "height": h})
            konsole = []
            pg.on("console", lambda m: konsole.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: konsole.append(str(e)))
            pg.goto(OUT.as_uri())
            if pg.evaluate("document.querySelector('#karten').scrollHeight > document.querySelector('#karten').clientHeight + 2"):
                fehler.append(f"{w}×{h} Übersicht läuft über")
            for i in D["inputs"]:
                for k, fo in enumerate(i["folien"]):
                    for s in range(anzahl(fo) + 1):
                        pg.evaluate(f"starte({i['nr']}, {k}, {s})")
                        n_ans += 1
                        ueber = pg.evaluate("""() => {
                          const out = [];
                          const f = document.querySelector('.folie');
                          if (f.scrollHeight > f.clientHeight + 2) out.push('Folie ' + (f.scrollHeight - f.clientHeight) + 'px zu hoch');
                          for (const sel of ['.textkarte', '.ergebnis', '.signale', '.auf', '.hilfebox'])
                            document.querySelectorAll(sel).forEach(e => { if (e.scrollHeight > e.clientHeight + 2) out.push(sel + ' ' + (e.scrollHeight - e.clientHeight) + 'px'); });
                          return out; }""")
                        if ueber:
                            fehler.append(f"{w}×{h} Input {i['nr']} Folie {k + 1} Schritt {s}: {', '.join(ueber)}")
            # Steuerung: Tasten durchspielen
            pg.evaluate("menu()")
            pg.keyboard.press("2")
            for _ in range(60):
                pg.keyboard.press("ArrowRight")
            if pg.evaluate("document.querySelector('#bVor').disabled") is not True:
                fehler.append(f"{w}×{h}: Ende von Input 2 nicht erreicht")
            pg.keyboard.press("Escape")
            if fehler and not konsole:
                pass
            fehler += [f"{w}×{h} Konsole: {c}" for c in konsole]
            pg.close()
        br.close()
    print(f"apps/inputs/index.html: {len(D['inputs'])} Inputs, {n_ans} Ansichten geprüft, {OUT.stat().st_size // 1024} KB")
    if fehler:
        print("FEHLER:", *fehler[:40], sep="\n  ")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

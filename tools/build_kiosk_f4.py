#!/usr/bin/env python3
"""Kontroll-Kiosk Fassung 4 → apps/kontroll-kiosk/index.html (gleiche Oberfläche wie Wunschbriefe/Zootiere).

Inhalte: inhalt/f4/kiosk.json. Blatt 1–5 Leseübungen, 6–10 Quiz Märchenmerkmale, 11–15 Schreibplan/Lückentext,
16 Bilder im Kopf. Keine Lösungen zu Klassenarbeit und Gelingensnachweisen.
Zeilenangaben {Z:id:Wortlaut}: zuerst die Leseübungen (ausgabe/f4/kollegin/zeilen.json, entsteht in build_f4_pakete.py),
sonst die gesperrten Märchentexte (ausgabe/texte/zeilen.json).

Aufruf: python3 tools/build_kiosk_f4.py      (nach build_f4_pakete.py; erzeugt und prüft im Browser)
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_kiosk as bk  # noqa: E402
from satz import font_css, zeile  # noqa: E402

ROOT = bk.ROOT
OUT = ROOT / "apps" / "kontroll-kiosk" / "index.html"
ZK = ROOT / "ausgabe" / "f4" / "kollegin" / "zeilen.json"


def zeile_k(tid: str, wortlaut: str) -> str:
    kol = json.loads(ZK.read_text("utf-8")) if ZK.exists() else {}
    if tid not in kol:
        return zeile(tid, wortlaut)
    zeilen = kol[tid]["zeilentext"]
    voll = " ".join(zeilen)
    i = voll.find(wortlaut)
    if i < 0:
        raise SystemExit("Kiosk: Textstelle nicht gefunden in %s: %r" % (tid, wortlaut))
    pos, start, ende = 0, None, None
    for n, z in enumerate(zeilen, 1):
        if start is None and i < pos + len(z) + 1:
            start = n
        if i + len(wortlaut) <= pos + len(z):
            ende = n
            break
        pos += len(z) + 1
    return "Z. %d" % start if start == ende else "Z. %d–%d" % (start, ende)


def klar(t: str) -> str:
    t = re.sub(r"\{Z:([\w-]+):(.+?)\}", lambda m: zeile_k(m.group(1), m.group(2)), t)
    return re.sub(r"\*{1,2}([^*]+?)\*{1,2}", r"\1", t)


def daten():
    k = json.loads((ROOT / "inhalt" / "f4" / "kiosk.json").read_text("utf-8"))
    data = {}
    for nr, b in k["blaetter"].items():
        e = {x: klar(v) for x, v in b.items()}
        e["type"] = "Lösung" if int(nr) <= 5 else "ein Beispiel"
        data[nr] = e
    gruppen = [{"n": "%s · %s" % (g["n"], g["titel"]), "blaetter": [[n, data[str(n)]["title"]] for n in g["blaetter"]]} for g in k["gruppen"]]
    if sorted(int(n) for n in data) != list(range(1, len(data) + 1)):
        raise SystemExit("Kiosk: Blattnummern nicht lückenlos")
    return data, gruppen


def overview(gruppen) -> str:
    h = ["<h3>Die Blätter</h3>"]
    for g in gruppen:
        h.append("<div class='et'><b>%s</b>%s</div>" % (g["n"], "".join("<div class='bl'><span>%d</span><span>%s</span></div>" % (n, t) for n, t in g["blaetter"])))
    return "".join(h)


def main():
    data, gruppen = daten()
    mx = max(int(k) for k in data)
    html = (bk.TEMPLATE.replace("__FONTS__", font_css())
            .replace("__DATA__", json.dumps(data, ensure_ascii=False))
            .replace("__OVERVIEW__", overview(gruppen))
            .replace("__MAX__", str(mx))
            .replace("· nur beim Üben", "· Fassung 4 · nur beim Üben, nicht in der Klassenarbeit"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    fails = bk.check(OUT, data)
    print(f"Kiosk F4: {len(data)} Blätter, {2 * len(data)} Ansichten je Bildschirmgröße geprüft")
    print("ok" if not fails else "FEHLER:\n  " + "\n  ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

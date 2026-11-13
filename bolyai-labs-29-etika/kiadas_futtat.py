"""Béta-kiadás (28. blokk).

    python kiadas_futtat.py audit       # forráskód-audit: titkok, követett fájlok, függőségek, biztonság, verzió
    python kiadas_futtat.py             # minden ellenőrzés lefut, és elkészül a BETA.md kiadási jelentés

A BETA.md „Ismert hibák és korlátok” részét te írod – a következő futtatás megtartja.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from app.kiadas import audit  # noqa: E402

KEZI = "<!-- KÉZI RÉSZ: innen lefelé te írod, a kiadas_futtat.py megtartja -->"
KEZI_ALAP = """## Ismert hibák és korlátok

- 

## Mit kérünk a béta-tesztelőktől?

- 
"""


def futtat(*parancs: str, env: dict | None = None) -> tuple[int, str]:
    r = subprocess.run([sys.executable, *parancs], cwd=ROOT, capture_output=True, text=True,
                       env={**os.environ, **(env or {})}, timeout=900)
    return r.returncode, (r.stdout + r.stderr).strip()


def utolso(minta: str, szoveg: str, alap: str = "–") -> str:
    m = re.findall(minta, szoveg)
    return m[-1] if m else alap


def app_verzio() -> str:
    from app import api
    return api.app.version


def audit_kiir() -> bool:
    eredmeny = audit(ROOT, app_verzio())
    for nev, hibak in eredmeny.items():
        print(f"{'✓' if not hibak else '✗'} {nev}")
        for h in hibak[:15]:
            print(f"    → {h}")
    jo = all(not h for h in eredmeny.values())
    print("\nAz audit tiszta." if jo else "\nAz audit hibát talált.")
    return jo


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.strip()
    except FileNotFoundError:
        return ""


def jelentes() -> bool:
    sorok, mind_jo = [], True
    if not (ROOT / "BETA.md").exists():       # első futás: legyen mire hivatkozni (pl. a CHANGELOG-ból)
        (ROOT / "BETA.md").write_text(f"# Béta-kiadás\n\n{KEZI}\n\n{KEZI_ALAP}", encoding="utf-8")

    def sor(nev: str, ok: bool, reszlet: str):
        nonlocal mind_jo
        mind_jo &= ok
        sorok.append(f"| {nev} | {'✓' if ok else '✗'} | {reszlet} |")
        print(f"{'✓' if ok else '✗'} {nev}: {reszlet}")

    kod, ki = futtat("-m", "ruff", "check", ".")
    sor("Kódminőség (ruff)", kod == 0, "hiba nélkül" if kod == 0 else utolso(r"Found \d+ errors?", ki))
    cov = Path(tempfile.mkdtemp()) / "cov.json"
    kod, ki = futtat("-m", "pytest", "-q", "-p", "no:warnings", "--cov=src/app", f"--cov-report=json:{cov}",
                     env={"KIADAS_FUT": "1"})
    lefedettseg = f"{json.loads(cov.read_text())['totals']['percent_covered']:.0f}%" if cov.exists() else "–"
    sor("Tesztek (pytest)", kod == 0, utolso(r"\d+ (?:passed|failed)[^\n]*", ki).split(" in ")[0])
    sor("Lefedettség", cov.exists(), lefedettseg)
    kod, ki = futtat("validacio_futtat.py")
    sor("Az ágens viselkedése", kod == 0, utolso(r"\d+/\d+ eset rendben", ki))
    kod, ki = futtat("integracio_futtat.py")
    sor("Rendszerintegráció", kod == 0, utolso(r"\d+/\d+ lépés rendben", ki))
    kod, ki = futtat("teljesitmeny_futtat.py")
    p95, p95_keret = utolso(r"p95\s+([\d.]+) ms", ki, "0"), utolso(r"p95[^\n]*keret: ([\d.]+) ms", ki, "")
    p95_ok = not p95_keret or float(p95) <= max(3 * float(p95_keret), float(p95_keret) + 50)   # mint a teszt: a gép zajos
    ok = kod == 0 and p95_ok and not re.search(r"kontextus[^\n]*✗", ki)
    sor("Teljesítmény", ok, f"p95 {utolso(r'p95\s+([\d.]+) ms', ki)} ms · kontextus max {utolso(r'modellhívás, max\s+(\d+) token', ki)} token")
    kod, ki = futtat("doksi_futtat.py", "ellenoriz")
    sor("Dokumentáció", kod == 0, "rendben" if kod == 0 else utolso(r"\d+ probléma", ki))
    a = audit(ROOT, app_verzio())
    hibas = [n for n, h in a.items() if h]
    sor("Forráskód-audit", not hibas, "tiszta" if not hibas else "hiba: " + ", ".join(hibas))

    regi = (ROOT / "BETA.md").read_text(encoding="utf-8") if (ROOT / "BETA.md").exists() else ""
    kezi = regi.split(KEZI, 1)[1].strip("\n") if KEZI in regi else KEZI_ALAP
    v = app_verzio()
    fej = [f"# Béta-kiadás – {v}", "",
           "<!-- Generált rész: python kiadas_futtat.py – a kézi rész lent van. -->", "",
           f"**Verzió:** {v}  ", f"**Dátum:** {dt.date.today().isoformat()}  ",
           f"**Commit:** {git('rev-parse', '--short', 'HEAD') or '–'}  ",
           f"**Címke:** v{v}", "", "## Ellenőrzések", "", "| Ellenőrzés | Állapot | Eredmény |", "| --- | --- | --- |",
           *sorok, "", KEZI, "", kezi, ""]
    (ROOT / "BETA.md").write_text("\n".join(fej), encoding="utf-8")
    print(f"\nKész: BETA.md – {'minden zöld, mehet a címke: git tag v' + v if mind_jo else 'van piros, előbb javítsd'}")
    return mind_jo


def main():
    mit = sys.argv[1] if len(sys.argv) > 1 else "jelentes"
    sys.exit(0 if (audit_kiir() if mit == "audit" else jelentes()) else 1)


if __name__ == "__main__":
    main()

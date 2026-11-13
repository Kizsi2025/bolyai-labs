"""Etikai és jogi audit segédei (29. blokk): licencek és a megfelelőségi dokumentum ellenőrzése.

projekt_licenc(gyoker)   – a LICENSE fájlból: MIT, Apache-2.0, BSD, GPL-3.0, MPL-2.0 … (vagy None)
fuggoseg_licencek(gyoker) – a requirements.txt közvetlen függőségei: név, verzió, licenc (a telepített csomagból)
licenc_tabla(gyoker)     – a docs/LICENCEK.md szövege (generált: a megfeleles_futtat.py írja)
osszes_licenc(gyoker)    – a közvetlen és a közvetett függőségek licence (a copyleft-ellenőrzéshez)
"""
import re
from importlib import metadata
from pathlib import Path

GENERALT = "<!-- Generált fájl: python megfeleles_futtat.py licencek – NE szerkeszd kézzel. -->"
OSZTALYOZO = {"MIT License": "MIT", "Apache Software License": "Apache-2.0", "BSD License": "BSD",
              "Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0", "ISC License (ISCL)": "ISC",
              "GNU General Public License v3 (GPLv3)": "GPL-3.0", "GNU General Public License v2 (GPLv2)": "GPL-2.0",
              "GNU Lesser General Public License v3 (LGPLv3)": "LGPL-3.0", "GNU Affero General Public License v3": "AGPL-3.0",
              "Python Software Foundation License": "PSF-2.0", "The Unlicense (Unlicense)": "Unlicense"}
EROS_COPYLEFT = re.compile(r"\bA?GPL|GNU (Affero )?General Public", re.I)
LGPL = re.compile(r"LGPL|Lesser General Public", re.I)
MEGENGEDO = {"MIT", "Apache-2.0", "BSD", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0", "Unlicense", "0BSD"}


def projekt_licenc(gyoker: Path) -> str | None:
    """A projekt saját licence a LICENSE (vagy LICENSE.md, LICENCE) fájl szövegéből felismerve."""
    for nev in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE"):
        f = gyoker / nev
        if f.exists():
            t = f.read_text(encoding="utf-8", errors="replace")
            if "Permission is hereby granted, free of charge" in t:
                return "MIT"
            if "Apache License" in t and "Version 2.0" in t:
                return "Apache-2.0"
            if "GNU AFFERO GENERAL PUBLIC LICENSE" in t:
                return "AGPL-3.0"
            if "GNU GENERAL PUBLIC LICENSE" in t and "Version 3" in t:
                return "GPL-3.0"
            if "Mozilla Public License" in t and "2.0" in t:
                return "MPL-2.0"
            if "Redistribution and use in source and binary forms" in t:
                return "BSD-3-Clause" if "Neither the name" in t else "BSD-2-Clause"
            if "Creative Commons" in t:
                return "CC"
            return None
    return None


def _licenc(m) -> str:
    if m.get("License-Expression"):
        return m["License-Expression"].strip()
    for c in m.get_all("Classifier") or []:
        if c.startswith("License :: "):
            nev = c.rsplit(" :: ", 1)[-1]
            if nev in OSZTALYOZO:
                return OSZTALYOZO[nev]
    lic = (m.get("License") or "").strip()
    if lic and len(lic) <= 40 and "\n" not in lic:
        return lic
    return "ismeretlen"


def kozvetlen(gyoker: Path) -> list[tuple[str, str]]:
    """(név, rögzített verzió) párok a requirements.txt-ből."""
    f = gyoker / "requirements.txt"
    sorok = f.read_text(encoding="utf-8").splitlines() if f.exists() else []
    ki = []
    for s in sorok:
        s = s.split("#", 1)[0].strip()
        if s and not s.startswith("-"):
            nev, _, ver = s.partition("==")
            ki.append((re.split(r"[<>=~!\[;\s]", nev)[0], ver.strip()))
    return ki


def fuggoseg_licencek(gyoker: Path) -> list[dict]:
    """A közvetlen függőségek licence – a telepített csomag metaadataiból."""
    ki = []
    for nev, ver in kozvetlen(gyoker):
        try:
            m = metadata.metadata(nev)
            ki.append({"nev": nev, "verzio": ver or m["Version"], "licenc": _licenc(m)})
        except metadata.PackageNotFoundError:
            ki.append({"nev": nev, "verzio": ver, "licenc": "nincs telepítve"})
    return ki


def osszes_licenc(gyoker: Path) -> dict[str, str]:
    """Név → licenc a teljes függőségi fára (közvetett függőségekkel együtt)."""
    from packaging.requirements import Requirement
    lat, sor = {}, [n for n, _ in kozvetlen(gyoker)]
    while sor:
        nev = sor.pop()
        kulcs = nev.lower().replace("_", "-")
        if kulcs in lat:
            continue
        try:
            m = metadata.metadata(nev)
        except metadata.PackageNotFoundError:
            lat[kulcs] = "nincs telepítve"
            continue
        lat[kulcs] = _licenc(m)
        for r in metadata.requires(nev) or []:
            req = Requirement(r)
            if req.marker is None or req.marker.evaluate({"extra": ""}):
                sor.append(req.name)
    return lat


def licenc_tabla(gyoker: Path) -> str:
    """A docs/LICENCEK.md szövege."""
    sajat = projekt_licenc(gyoker) or "nincs megadva"
    sorok = [GENERALT, "", "# Licencek", "", f"A projekt licence: **{sajat}** (LICENSE).", "",
             "## Közvetlen függőségek", "", "| Csomag | Verzió | Licenc |", "| --- | --- | --- |"]
    sorok += [f"| {d['nev']} | {d['verzio']} | {d['licenc']} |" for d in fuggoseg_licencek(gyoker)]
    sorok += ["", "A közvetett függőségek licencét a `python megfeleles_futtat.py ellenoriz` nézi át.", ""]
    return "\n".join(sorok)


def licenc_hibak(gyoker: Path) -> list[str]:
    """Erős copyleft (GPL, AGPL) függőség megengedő licencű projektben, és ismeretlen licencű csomagok."""
    sajat = projekt_licenc(gyoker)
    hibak = []
    if sajat is None:
        hibak.append("nincs felismerhető LICENSE fájl (MIT, Apache-2.0, BSD, GPL-3.0, MPL-2.0 …)")
    megf = (gyoker / "docs" / "MEGFELELOSEG.md")
    megf_t = megf.read_text(encoding="utf-8") if megf.exists() else ""
    for nev, lic in sorted(osszes_licenc(gyoker).items()):
        if lic in {"ismeretlen", "nincs telepítve"} and nev not in megf_t.lower():
            hibak.append(f"{nev}: a licence {lic} – nézd meg kézzel, és írd be a docs/MEGFELELOSEG.md Licencek részébe")
        elif EROS_COPYLEFT.search(lic) and not LGPL.search(lic) and sajat in MEGENGEDO:
            hibak.append(f"{nev}: {lic} (erős copyleft) egy {sajat} licencű projektben – cseréld le, vagy egyeztess a tanárral")
    return hibak


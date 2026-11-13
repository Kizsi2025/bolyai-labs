"""Etikai és jogi audit (29. blokk).

    python megfeleles_futtat.py licencek     # a docs/LICENCEK.md újragenerálása (a telepített csomagokból)
    python megfeleles_futtat.py ellenoriz    # LICENSE, copyleft, ismeretlen licencek
    python megfeleles_futtat.py              # mindkettő
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from app.megfeleles import licenc_hibak, licenc_tabla, projekt_licenc  # noqa: E402


def main():
    mit = sys.argv[1] if len(sys.argv) > 1 else "mind"
    if mit in {"licencek", "mind"}:
        cel = ROOT / "docs" / "LICENCEK.md"
        cel.parent.mkdir(exist_ok=True)
        cel.write_text(licenc_tabla(ROOT), encoding="utf-8")
        print(f"Kész: {cel.relative_to(ROOT)}")
    if mit in {"ellenoriz", "mind"}:
        print(f"A projekt licence: {projekt_licenc(ROOT) or 'nincs felismerhető LICENSE'}")
        hibak = licenc_hibak(ROOT)
        for h in hibak:
            print(f"✗ {h}")
        print("A licencek rendben." if not hibak else f"\n{len(hibak)} probléma.")
        sys.exit(1 if hibak else 0)


if __name__ == "__main__":
    main()

"""One new continuous Vlasta paragraph for a short authentic Codegen demonstration."""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "video_course/production"))
import studio  # noqa: E402, F401
from continuous_speech import synthesize_scene  # noqa: E402

PARAGRAPH = (
    "Než lokátor zapíšeme ručně, krátce si ukážeme pomocníka Codegen. "
    "Tady běží jeho skutečný prohlížeč a vedle něj Inspector. "
    "Do e-mailového pole napíšu náš veřejný testovací účet. "
    "Inspector z provedené akce vytvoří návrh kódu v Pythonu. "
    "V návrhu je navigace, nalezený textbox a vyplnění hodnoty. "
    "Záznam samotného klikání ale ještě neříká, co má test ověřovat. "
    "Návrh proto vždy přečteme a doplníme vlastní očekávání. "
    "Teď se vrátíme k našemu krátkému testu, kde nadpis i tlačítko ověříme vědomě."
)


async def main():
    lexicon = json.loads((ROOT / "video_course/r2/pronunciation.json").read_text(encoding="utf-8"))
    lexicon["aliases"].update({"textbox": "tekst boks", "Codegen": "koudžen"})
    (HERE / "pronunciation.json").write_text(
        json.dumps(lexicon, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    directory = HERE / "narration"
    directory.mkdir(exist_ok=True)
    data = await synthesize_scene({"id": "r21_codegen", "paragraph": PARAGRAPH}, directory, lexicon)
    (HERE / "codegen_narration.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"audio": data["audio"], "words": len(PARAGRAPH.split())}), flush=True)


if __name__ == "__main__":
    asyncio.run(main())

"""Samostatná řečová verze komentáře; nikdy nepřepisuje kód ani text titulků."""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEXICON = Path(__file__).with_name("pronunciation_vlasta.json")


def prepare(text: str, lexicon: dict) -> tuple[str, list[dict]]:
    aliases = {key.casefold(): value for key, value in lexicon["aliases"].items()}
    names = sorted(lexicon["aliases"], key=len, reverse=True)
    # Unicode word boundaries zabrání změně např. test_python nebo pythonic.
    pattern = re.compile(r"(?<!\w)(?:" + "|".join(map(re.escape, names)) + r")(?!\w)", re.I)
    replacements = []

    def replace(match):
        spoken = aliases[match.group().casefold()]
        replacements.append(
            {"start": match.start(), "end": match.end(), "display": match.group(), "spoken": spoken}
        )
        return spoken

    return pattern.sub(replace, text), replacements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=ROOT / "video_course/scripts/pronunciation_check.txt"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "video_course/scripts/pronunciation_check_vlasta_spoken_v1.txt",
    )
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        raise ValueError("Původní text nesmí být přepsán fonetickou verzí.")
    original_bytes = args.input.read_bytes()
    text = original_bytes.decode("utf-8")
    lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
    spoken, replacements = prepare(text, lexicon)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(spoken, encoding="utf-8")
    evidence = {
        "voice": lexicon["voice"],
        "lexicon_version": lexicon["version"],
        "display_text": str(args.input.relative_to(ROOT)),
        "spoken_text": str(args.output.relative_to(ROOT)),
        "original_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "spoken_sha256": hashlib.sha256(spoken.encode("utf-8")).hexdigest(),
        "replacements": replacements,
        "human_listening_review": "pending",
    }
    args.output.with_suffix(".json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if args.input.read_bytes() != original_bytes:
        raise RuntimeError("Původní zdroj se neočekávaně změnil.")
    print(
        json.dumps(
            {
                "replacements": len(replacements),
                "original_preserved": True,
                "spoken_file": str(args.output.relative_to(ROOT)),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

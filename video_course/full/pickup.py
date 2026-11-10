"""Replace independent editor shots with truthful, separately contracted new takes."""

import json
from pathlib import Path

from capture import PRODUCER_SOURCES, Session, audio, capture, sha
from prepare import HERE, ROOT


def chapter(number, targets):
    stage = HERE / "chapters" / f"{number:02}"
    index = stage / "capture.json"
    receipts = audio.read(index)
    if all(
        (
            'get_by_role("heading"' in r["proof"].get("actual_selected_text", "")
            if number == 1
            else bool(r["proof"].get("actual_headed_browser_windows"))
        )
        for r in receipts
        if r["id"] in targets
    ):
        print(f"Verified chapter{number:02} pickups already present", flush=True)
        return
    original_contract = stage / "capture_contract.json"
    original_sha = sha(original_contract)
    session = Session(number)
    folder = stage / "pickups" / session.take
    folder.mkdir(parents=True, exist_ok=True)
    inputs = {str(original_contract.relative_to(ROOT)): original_sha}
    for name, content in {
        **PRODUCER_SOURCES,
        "video_course/full/pickup.py": Path(__file__).read_bytes(),
    }.items():
        snapshot = folder / "source_versions" / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(content)
        inputs[str(snapshot.relative_to(ROOT))] = sha(snapshot)
    audio.save(folder / "parent_edit_index.json", receipts)
    replacements = []
    try:
        for wanted in targets:
            parent = next(r for r in receipts if r["id"] == wanted)
            parent_file = (ROOT / parent["clip"]).with_suffix(".json")
            assert sha(original_contract) == original_sha
            inputs[str(parent_file.relative_to(ROOT))] = sha(parent_file)
            if number == 2:
                session.run("smoke")
            elif wanted == "01_041":
                session.code("tests/smoke/test_login.py", "page.goto(")
            else:
                session.act("case_note:expected")
            # Freeze a separate complete contract for each pickup. Earlier
            # receipts never point at a contract that is subsequently changed.
            one_contract = folder / (wanted + "_contract.json")
            audio.save(
                one_contract,
                {
                    "inputs_sha256": dict(inputs),
                    "take": session.take,
                    "parent_contract_sha256": original_sha,
                    "voice": "cs-CZ-VlastaNeural",
                },
            )
            receipt = capture(session, parent, one_contract)
            receipt.update(
                contract_path=str(one_contract.relative_to(ROOT)),
                parent_receipt_path=str(parent_file.relative_to(ROOT)),
                parent_receipt_sha256=sha(parent_file),
                pickup_reason=(
                    "Select actual HTML heading assertion instead of document title"
                    if number == 1
                    else (
                        "Make the genuine headed test browser visibly foreground "
                        "during its actual run"
                    )
                ),
            )
            audio.save((ROOT / receipt["clip"]).with_suffix(".json"), receipt)
            replacements.append(receipt)
    finally:
        session.close()
    by_id = {r["id"]: r for r in replacements}
    audio.save(index, [by_id.get(r["id"], r) for r in receipts])
    print(json.dumps({"pickups": list(by_id), "take": session.take}), flush=True)


def main():
    chapter(1, ("01_041", "01_044"))
    chapter(2, ("02_015",))


if __name__ == "__main__":
    main()

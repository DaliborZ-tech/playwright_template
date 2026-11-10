"""Real pickups for off-screen records and three independently reviewed source mismatches."""

import json
from pathlib import Path

from capture import PRODUCER_SOURCES, Session, audio, capture, sha
from prepare import HERE, ROOT

CORRECTIONS = {
    "06_020": 'focus_code:tests/regression/test_records.py:expect(row).to_contain_text("Vysoká")',
    "06_022": "focus_code:tests/teaching/test_expected_failure.py:Neexistující nadpis",
    "07_014": "focus_code:tests/conftest.py:server = make_server",
}


def outside(receipt):
    proof = receipt["proof"]
    rect = proof.get("focus_rect")
    target = proof.get("target_outer_html", "")
    return (
        proof.get("url", "").startswith("http://127.0.0.1:5000")
        and target.startswith(("<tr", "<table"))
        and rect
        and (rect[1] < 24 or rect[1] + rect[3] > 1056)
    )


def prepare_state(session, receipt):
    action, proof = receipt["action"], receipt["proof"]
    if action.startswith("code:"):
        # Only source selection is being corrected; no application state is invented.
        session.code(proof["file"], proof["actual_selected_text"].strip())
        return
    session.login(reset=True)
    session.ready()
    if action == "save_record":
        session.act("new_form")
        session.act("fill_record")
    elif action in {"scope_created", "update_reload"}:
        session.act("create")
    elif action == "scope_row" and proof.get("selected_rows") == 2:
        session.act("duplicate_record")
    # create and duplicate_record intentionally start from the reset three rows.


def chapter(number):
    stage = HERE / "chapters" / f"{number:02}"
    index = stage / "capture.json"
    if not index.exists():
        return
    receipts = audio.read(index)
    targets = [
        r
        for r in receipts
        if outside(r) or (r["id"] in CORRECTIONS and r["action"] != CORRECTIONS[r["id"]])
    ]
    if not targets:
        return
    contract_path = stage / "capture_contract.json"
    parent_sha = sha(contract_path)
    session = Session(number)
    folder = stage / "pickups" / session.take
    folder.mkdir(parents=True, exist_ok=True)
    inputs = {str(contract_path.relative_to(ROOT)): parent_sha}
    for name, content in {
        **PRODUCER_SOURCES,
        "video_course/full/repair.py": Path(__file__).read_bytes(),
    }.items():
        path = folder / "source_versions" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        inputs[str(path.relative_to(ROOT))] = sha(path)
    audio.save(folder / "parent_edit_index.json", receipts)
    replacements = {}
    try:
        for parent in targets:
            prepare_state(session, parent)
            parent_file = (ROOT / parent["clip"]).with_suffix(".json")
            local_inputs = {**inputs, str(parent_file.relative_to(ROOT)): sha(parent_file)}
            new_action = CORRECTIONS.get(parent["id"], parent["action"])
            if new_action.startswith("focus_code:"):
                _, source, pattern = new_action.split(":", 2)
                proof = session.code(source, pattern)
                session.focus_prepared = {"action": new_action, "proof": proof}
                from studio import gui
                gui.press("left")
            pickup_contract = folder / (parent["id"] + "_contract.json")
            data = {
                "inputs_sha256": local_inputs,
                "take": session.take,
                "parent_contract_sha256": parent_sha,
                "voice": "cs-CZ-VlastaNeural",
            }
            if new_action != parent["action"]:
                data["semantic_override"] = {"from": parent["action"], "to": new_action}
            audio.save(pickup_contract, data)
            receipt = capture(session, {**parent, "action": new_action}, pickup_contract)
            if new_action != parent["action"]:
                receipt["original_planned_action"] = parent["action"]
            receipt.update(
                contract_path=str(pickup_contract.relative_to(ROOT)),
                parent_receipt_path=str(parent_file.relative_to(ROOT)),
                parent_receipt_sha256=sha(parent_file),
                pickup_reason="Actual visible target and source matching the canonical narration",
            )
            audio.save((ROOT / receipt["clip"]).with_suffix(".json"), receipt)
            replacements[receipt["id"]] = receipt
    finally:
        session.close()
    audio.save(index, [replacements.get(r["id"], r) for r in receipts])
    print(json.dumps({"chapter_repaired": number, "shots": list(replacements)}), flush=True)


def main():
    for number in range(1, 13):
        if number != 4:
            chapter(number)
    print("ALL REVIEWED VIEWPORT AND SOURCE PICKUPS FINISHED", flush=True)


if __name__ == "__main__":
    main()

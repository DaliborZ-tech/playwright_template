"""Apply the recorded owner decision only to the exact approved reference assets."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def apply(project, directory):
    receipt = HERE / "po_approval.json"
    if not receipt.exists():
        return project
    approval = json.loads(receipt.read_text(encoding="utf-8"))
    if approval["decision"] != "APPROVED":
        raise ValueError("Reference does not have an affirmative owner decision")
    if approval["voice"] != project["voice"]:
        raise ValueError("Voice differs from the approved reference")
    commit = json.loads((HERE / "reference.json").read_text(encoding="utf-8"))["commit"]
    if approval["frozen_commit"] != commit:
        raise ValueError("Starter Kit differs from the approved reference")
    recorded = {movie["file"]: movie["sha256"] for movie in project["movies"]}
    if recorded != approval["movies"]:
        raise ValueError("Rendered movie differs from the owner-approved version")
    for name, digest in approval["movies"].items():
        if sha(directory / name) != digest:
            raise ValueError(f"Approved movie bytes changed: {name}")
    return {
        **project,
        "status": "APPROVED_REFERENCE",
        "human_watch_and_listen": "OWNER_APPROVED_REFERENCE",
        "po_approval": "APPROVED",
        "full_course_build_authorized": True,
        "po_approval_evidence": {
            "file": receipt.name,
            "sha256": sha(receipt),
            "decision": approval,
        },
        "approval_scope": "Reference and production standard; remaining course not yet accepted",
    }


def main():
    path = HERE / "output/edit_project.json"
    project = apply(json.loads(path.read_text(encoding="utf-8")), path.parent)
    path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": project["status"],
                "po_approval": project["po_approval"],
                "full_course_build_authorized": project["full_course_build_authorized"],
            }
        )
    )


if __name__ == "__main__":
    main()

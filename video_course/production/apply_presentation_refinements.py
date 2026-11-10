"""Obnovitelné mapování doplněných skutečných operací bez přegenerování textu."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    course = ROOT / "video_course"
    path = course / "storyboard/course_plan.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    overrides = json.loads(
        (course / "scripts/presentation_refinements.json").read_text(encoding="utf-8")
    )
    changed = []
    for scene in plan:
        screen = overrides.get(scene["id"])
        if screen and scene["screen"] != screen:
            scene["screen"] = screen
            changed.append(scene["id"])
            receipt = course / "recordings" / f"{scene['id']}.json"
            if receipt.exists():
                data = json.loads(receipt.read_text(encoding="utf-8"))
                data["status"] = "superseded_presentation"
                receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"presentation_updates": changed}))


if __name__ == "__main__":
    main()

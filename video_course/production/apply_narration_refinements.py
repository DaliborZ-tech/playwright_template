"""Zpřesní jen vybrané odstavce; zachová schválené podklady ostatních scén."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    course = ROOT / "video_course"
    path = course / "storyboard/course_plan.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    refinements = json.loads(
        (course / "scripts/narration_refinements.json").read_text(encoding="utf-8")
    )
    changed = []
    for scene in plan:
        text = refinements.get(scene["id"])
        if text and text != scene["paragraph"]:
            scene["paragraph"] = text
            for field in ("audio", "cues", "voice"):
                scene.pop(field, None)
            changed.append(scene["id"])
            receipt = course / "recordings" / f"{scene['id']}.json"
            if receipt.exists():
                old = json.loads(receipt.read_text(encoding="utf-8"))
                old["status"] = "superseded_narration"
                receipt.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")
    assert len(plan) == 97 and not any(
        "odkazovaný soubor nebo příkaz" in s["paragraph"] for s in plan
    )
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    transcript = []
    previous_chapter = None
    for scene in plan:
        if scene["chapter"] != previous_chapter:
            transcript.append(f"# {scene['chapter']:02} · {scene['title']}\n")
            previous_chapter = scene["chapter"]
        transcript.append(f"## Scéna {scene['id']}\n\n{scene['paragraph']}\n")
    (course / "scripts/transcript_cs.md").write_text("\n".join(transcript), encoding="utf-8")
    jobs = [
        {
            "scene": s["id"],
            "voice": "cs-CZ-VlastaNeural",
            "display_text": s["paragraph"],
            "unit": "continuous_paragraph",
        }
        for s in plan
    ]
    (course / "production/continuous_speech_jobs.json").write_text(
        json.dumps(jobs, ensure_ascii=False), encoding="utf-8"
    )
    print(
        json.dumps(
            {"refined_scenes": changed, "words": sum(len(s["paragraph"].split()) for s in plan)}
        )
    )


if __name__ == "__main__":
    main()

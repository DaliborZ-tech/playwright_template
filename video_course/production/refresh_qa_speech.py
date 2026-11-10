"""Přegeneruje pouze odstavce dotčené upřesněním QA → kjů ej."""

import asyncio
import json
import re

from continuous_speech import LEXICON, ROOT, synthesize_scene


async def main():
    plan = json.loads(
        (ROOT / "video_course/storyboard/course_plan.json").read_text(encoding="utf-8")
    )
    lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
    directory = ROOT / "video_course/narration/vlasta"
    for scene in plan:
        if re.search(r"(?<!\w)QA(?!\w)", scene["paragraph"]):
            data = await asyncio.wait_for(synthesize_scene(scene, directory, lexicon), timeout=180)
            print(
                json.dumps({"scene": scene["id"], "QA": "kjů ej", "audio": data["audio"]}),
                flush=True,
            )
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())

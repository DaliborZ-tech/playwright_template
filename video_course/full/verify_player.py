"""Actual Microsoft Edge subtitle rendering and chapter seeking; no human audio claim."""
# Embedded browser evaluation expressions retain their JavaScript line structure.
# ruff: noqa: E501

import argparse
import functools
import hashlib
import http.server
import importlib.util
import json
import site
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
from PIL import Image, ImageChops  # noqa: E402
from playwright.sync_api import expect, sync_playwright  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory, headless=False):
    spec = importlib.util.spec_from_file_location("course_player", directory / "start_player.py")
    player = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(player)
    captions = json.loads((directory / "captions.json").read_text(encoding="utf-8"))
    chapters = json.loads((directory / "chapters.json").read_text(encoding="utf-8"))
    validation = json.loads((directory / "validation.json").read_text(encoding="utf-8"))
    for name, digest in validation["movies"].items():
        assert sha(directory / name) == digest
    evidence = HERE / "evidence/player"
    evidence.mkdir(parents=True, exist_ok=True)
    indices = sorted(
        {
            1,
            len(captions) // 2,
            len(captions) - 1,
            max(range(len(captions)), key=lambda i: len(captions[i]["text"])),
        }
    )
    results, burns, navigation = [], [], []
    handler = functools.partial(player.Handler, directory=str(directory))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/player.html"
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="msedge", headless=headless)
            page = browser.new_page(viewport={"width": 1600, "height": 1200})
            page.goto(url)
            page.wait_for_function(
                "document.querySelector('#czech').track.cues?.length > 0 && document.querySelector('video').readyState >= 2"
            )
            page.wait_for_selector("#chapters button:nth-child(12)")
            version = browser.version
            assert page.locator("#czech").evaluate("e=>e.track.cues.length") == len(captions)
            page.locator("video").evaluate("v=>v.controls=false")

            def seek(at):
                page.evaluate(
                    """async t=>{const v=document.querySelector('video');v.muted=true;
                    const done=new Promise(r=>v.addEventListener('seeked',r,{once:true}));
                    v.currentTime=t;await done;await v.play();
                    await new Promise(r=>setTimeout(r,130));v.pause();} """,
                    at,
                )
                page.wait_for_timeout(250)

            for i in indices:
                cue = captions[i]
                seek((cue["start"] + cue["end"]) / 2)
                state = page.evaluate("""()=>{const v=document.querySelector('video'),t=v.textTracks[0];
                    return {time:v.currentTime,mode:t.mode,text:[...t.activeCues].map(c=>c.text).join(' '),
                    decoded:v.getVideoPlaybackQuality().totalVideoFrames,dimensions:[v.videoWidth,v.videoHeight],
                    error:v.error?.message||null}}""")
                assert state["mode"] == "showing" and state["decoded"] > 0 and not state["error"]
                assert " ".join(state["text"].split()) == cue["text"]
                assert len(state["text"].splitlines()) <= 2
                on, off = evidence / f"cue_{i}_on.png", evidence / f"cue_{i}_off.png"
                page.locator("video").screenshot(path=str(on))
                page.get_by_role("button", name="České titulky: zapnuté").click()
                page.wait_for_timeout(250)
                page.locator("video").screenshot(path=str(off))
                diff = ImageChops.difference(Image.open(on), Image.open(off))
                w, h = diff.size
                bbox = diff.crop((0, h - 170, w, h - 5)).getbbox()
                assert bbox is not None, "Subtitle toggle did not change visible pixels"
                results.append(
                    {
                        "cue": i,
                        "expected_text": cue["text"],
                        **state,
                        "visible_difference_bbox": bbox,
                        "on": on.name,
                        "off": off.name,
                        "on_sha256": sha(on),
                        "off_sha256": sha(off),
                    }
                )
                page.get_by_role("button", name="České titulky: vypnuté").click()
            for index, chapter in enumerate(chapters):
                page.locator("#chapters button").nth(index).click()
                page.wait_for_function(
                    "target=>{const v=document.querySelector('video');return !v.seeking && v.readyState>=2 && Math.abs(v.currentTime-target)<0.15}",
                    arg=chapter["start"] + 0.05,
                )
                at = page.locator("video").evaluate("v=>v.currentTime")
                assert abs(at - chapter["start"]) < 0.15
                expect(page.locator("#outcome")).to_have_text(chapter["learning_outcome"])
                navigation.append(
                    {"chapter": chapter["chapter"], "expected": chapter["start"], "actual": at}
                )
            page.goto(
                url.rsplit("/", 1)[0] + "/Playwright_Academy_Python_CZ_Full_Course_Titulky.mp4"
            )
            page.wait_for_selector("video")
            page.locator("video").evaluate("v=>v.controls=false")
            for result in results:
                seek(result["time"])
                target = evidence / f"cue_{result['cue']}_burned.png"
                page.locator("video").screenshot(path=str(target))
                burns.append(
                    {
                        "cue": result["cue"],
                        "time": result["time"],
                        "png": target.name,
                        "sha256": sha(target),
                    }
                )
            browser.close()
        server.shutdown()
    report = {
        "player": "Microsoft Edge HTML5 / native WebVTT",
        "version": version,
        "mode": "headless" if headless else "headed",
        "audio_during_test": "muted",
        "human_listening_review": "NOT_PERFORMED",
        "subtitle_playback_test": "PASS",
        "native_controls_for_comparison": "hidden equally ON and OFF",
        "checks": results,
        "chapter_navigation": navigation,
        "burned_playback": burns,
        "vtt_sha256": sha(directory / "subtitles_cs.vtt"),
        "player_html_sha256": sha(directory / "player.html"),
        "movies": validation["movies"],
    }
    (evidence / "player_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=HERE / "output")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify(args.directory, args.headless), ensure_ascii=True))

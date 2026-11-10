"""Exercise the actual HTML player's subtitle toggle and seeking at three points."""

import functools
import hashlib
import http.server
import json
import site
import threading
from pathlib import Path

site.addsitedir(str(Path(__file__).resolve().parents[2] / ".tools/media-env/Lib/site-packages"))

from PIL import Image, ImageChops  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from start_player import Handler  # noqa: E402

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory):
    evidence = HERE / "evidence/player"
    evidence.mkdir(parents=True, exist_ok=True)
    project = json.loads((directory / "edit_project.json").read_text(encoding="utf-8"))
    cues = project["captions"]
    indices = [1, len(cues) // 2, 42, len(cues) - 1]
    handler = functools.partial(Handler, directory=str(directory))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/player.html"
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="msedge", headless=False)
            page = browser.new_page(viewport={"width": 1600, "height": 1200})
            page.goto(url)
            page.wait_for_function(
                "document.querySelector('#czech').track.cues?.length > 0"
                " && document.querySelector('video').readyState >= 2"
            )
            version = browser.version
            # Stable on/off images: remove native controls for both captures,
            # equivalent to the player after controls auto-hide during playback.
            page.locator("video").evaluate("v => v.controls = false")
            results = []
            for position, cue_index in zip(
                ("beginning", "middle", "long_caption", "ending"), indices, strict=True
            ):
                cue = cues[cue_index]
                at = (cue["start"] + cue["end"]) / 2
                page.evaluate(
                    "async t => { const v=document.querySelector('video'); v.muted=true;"
                    "v.currentTime=t; await new Promise(r=>"
                    "v.addEventListener('seeked',r,{once:true}));"
                    "await v.play(); await new Promise(r=>setTimeout(r,180)); v.pause(); }",
                    at,
                )
                page.wait_for_timeout(500)
                state = page.evaluate("""() => {
                    const v=document.querySelector('video'), t=v.textTracks[0];
                    return {time:v.currentTime, mode:t.mode,
                      text:[...t.activeCues].map(c=>c.text).join(' '),
                      decoded:v.getVideoPlaybackQuality().totalVideoFrames,
                      dimensions:[v.videoWidth,v.videoHeight], error:v.error?.message || null};
                }""")
                assert state["mode"] == "showing" and state["decoded"] > 0 and not state["error"]
                assert " ".join(state["text"].split()) == cue["text"], state
                assert len(state["text"].splitlines()) <= 2, state
                on = evidence / f"{position}_on.png"
                off = evidence / f"{position}_off.png"
                page.locator("video").screenshot(path=str(on))
                page.get_by_role("button", name="České titulky: zapnuté").click()
                page.wait_for_timeout(250)
                assert page.locator("#czech").evaluate("e=>e.track.mode") == "hidden"
                page.locator("video").screenshot(path=str(off))
                diff = ImageChops.difference(Image.open(on), Image.open(off))
                width, height = diff.size
                bbox = diff.crop((0, height - 170, width, height - 5)).getbbox()
                assert bbox is not None, "No visible subtitle difference when toggled"
                results.append(
                    {
                        "position": position,
                        "expected_text": cue["text"],
                        **state,
                        "subtitle_visible_pixel_difference_bbox": bbox,
                        "on": str(on.relative_to(HERE)),
                        "on_sha256": sha(on),
                        "off": str(off.relative_to(HERE)),
                        "off_sha256": sha(off),
                    }
                )
                page.get_by_role("button", name="České titulky: vypnuté").click()
            burned_results = []
            page.goto(url.rsplit("/", 1)[0] + "/Playwright_Academy_R21_Prvni_Test_Titulky.mp4")
            page.wait_for_selector("video")
            page.locator("video").evaluate("v => v.controls = false")
            for result in results:
                page.evaluate(
                    "async t => { const v=document.querySelector('video'); v.muted=true;"
                    "v.currentTime=t; await new Promise(r=>"
                    "v.addEventListener('seeked',r,{once:true}));"
                    "await v.play(); await new Promise(r=>setTimeout(r,150)); v.pause(); }",
                    result["time"],
                )
                page.wait_for_timeout(200)
                png = evidence / (result["position"] + "_burned.png")
                page.locator("video").screenshot(path=str(png))
                burned_results.append({"time": result["time"], "png": png.name, "sha256": sha(png)})
            browser.close()
        server.shutdown()
    report = {
        "player": "Microsoft Edge, delivered HTML5 player with native WebVTT",
        "version": version,
        "mode": "headed",
        "audio_during_automated_test": "muted",
        "human_listening_review": "NOT_PERFORMED",
        "native_controls_for_screenshot_comparison": "hidden equally for ON and OFF",
        "subtitle_playback_test": "PASS",
        "movie_sha256": project["movies"][0]["sha256"],
        "vtt_sha256": sha(directory / "subtitles_cs.vtt"),
        "checks": results,
        "burned_variant_playback": burned_results,
    }
    (evidence / "player_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(verify(HERE / "output"), ensure_ascii=True))

"""Package the full, editable course and a standalone frozen Starter Kit."""
# HTML, JavaScript and Czech delivery text are serialized asset data.
# ruff: noqa: E501

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from verify_starter import make_starter

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def player(out):
    shutil.copyfile(ROOT / "video_course/r21/output/start_player.py", out / "start_player.py")
    server = out / "start_player.py"
    server.write_text(
        server.read_text(encoding="utf-8").replace(
            "except (BrokenPipeError, ConnectionResetError):",
            "except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):",
        ),
        encoding="utf-8",
    )
    (out / "PREHRAT.cmd").write_text(
        '@echo off\ncd /d "%~dp0"\npy -3 start_player.py\nif errorlevel 1 pause\n', encoding="utf-8"
    )
    (out / "player.html").write_text(
        """<!doctype html>
<html lang="cs"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Playwright Academy · Python</title>
<style>
:root{color-scheme:dark;font:17px/1.55 "Segoe UI",sans-serif;background:#0c1421;color:#edf4ff}
body{max-width:1280px;margin:28px auto;padding:0 20px}h1{margin-bottom:0}.brand{color:#8be2b4;letter-spacing:.12em;font-weight:700;font-size:.8rem}
video{width:100%;background:black;border:1px solid #39506a;border-radius:8px}video::cue{font-family:"Segoe UI",sans-serif;font-size:24px;color:white;background:rgba(0,0,0,.85)}
nav{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}button,a{color:#b4f7d0}button{border:1px solid #567564;border-radius:6px;padding:10px 14px;background:#132e23;cursor:pointer;font:inherit}
button:focus-visible{outline:3px solid white}.note{color:#bbc8d8}#chapters{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:8px}#chapters button{text-align:left}#outcome{min-height:3em}
</style><div class="brand">PLAYWRIGHT ACADEMY / PYTHON STARTER KIT</div>
<h1>Od manuálního testu k vlastní regresi</h1>
<p class="note">Dvanáct kapitol, jedna skutečná aplikace a společný příběh požadavku.</p>
<video id="lesson" controls preload="metadata"><source src="Playwright_Academy_Python_CZ_Full_Course.mp4" type="video/mp4"><track id="czech" kind="subtitles" src="subtitles_cs.vtt" srclang="cs" label="Čeština" default></video>
<nav aria-label="Ovládání kurzu"><button id="captions" aria-pressed="true">České titulky: zapnuté</button><button id="middle">Střed kurzu</button><button id="ending">Závěrečný úkol</button></nav>
<p id="outcome" class="note"></p><div id="chapters" aria-label="Kapitoly kurzu"></div>
<p class="note"><a href="Playwright_Academy_Python_CZ_Full_Course_Titulky.mp4">MP4 s titulky přímo v obraze</a> · <a href="subtitles_cs.srt" download>SRT</a> · <a href="subtitles_cs.vtt" download>VTT</a> · <a href="transcript_cs.txt" download>Přepis</a></p>
<script>
const video=document.querySelector('#lesson'),button=document.querySelector('#captions'),track=document.querySelector('#czech').track;track.mode='showing';
button.onclick=()=>{const showing=track.mode!=='showing';track.mode=showing?'showing':'hidden';button.setAttribute('aria-pressed',String(showing));button.textContent='České titulky: '+(showing?'zapnuté':'vypnuté')};
document.querySelector('#middle').onclick=()=>video.currentTime=video.duration/2;
document.querySelector('#ending').onclick=()=>video.currentTime=Math.max(0,video.duration-30);
fetch('chapters.json').then(r=>r.json()).then(chapters=>{
  for(const c of chapters){
    const b=document.createElement('button');
    b.textContent=String(c.chapter).padStart(2,'0')+' · '+c.title;
    b.onclick=()=>{video.currentTime=c.start+0.05;document.querySelector('#outcome').textContent=c.learning_outcome};
    document.querySelector('#chapters').append(b);
  }
  video.addEventListener('timeupdate',()=>{
    if(video.seeking)return;
    const at=video.currentTime+0.000001;
    const c=chapters.find(c=>at>=c.start&&at<c.end);
    if(c)document.querySelector('#outcome').textContent=c.learning_outcome;
  });
});
</script></html>
""",
        encoding="utf-8",
    )


def main():
    out = HERE / "output"
    validation = json.loads((out / "validation.json").read_text(encoding="utf-8"))
    assert validation["decode_errors"] == 0
    for name, digest in validation["movies"].items():
        assert sha(out / name) == digest
    player(out)
    playback = json.loads(
        (HERE / "evidence/player/player_validation.json").read_text(encoding="utf-8")
    )
    assert playback["subtitle_playback_test"] == "PASS" and playback["mode"] == "headed"
    assert playback["movies"] == validation["movies"]
    assert playback["vtt_sha256"] == sha(out / "subtitles_cs.vtt")
    assert playback["player_html_sha256"] == sha(out / "player.html")
    (out / "CTETE_NEJDRIVE.txt").write_text(
        "PLAYWRIGHT ACADEMY — PYTHON\n\n"
        "Celý kurz: 12 kapitol, 87 min 36,48 s, hlas Microsoft Vlasta.\n"
        "Součástí jsou oba celé filmy, 1 153 českých titulků, přepis a kapitoly.\n\n"
        "1. Prohlédněte si kurz přes PREHRAT.cmd (vyžaduje místní Python 3).\n"
        "   Server běží pouze na 127.0.0.1. Přehrávač nabízí 12 kapitol a české VTT.\n"
        "2. Bez Pythonu otevřete soubor Full_Course_Titulky.mp4 (plný název začíná Playwright_Academy_Python_CZ_).\n"
        "   Tato varianta má titulky trvale v obraze. Obě MP4 lze otevřít samostatně.\n"
        "3. Starter_Kit.zip rozbalte do vlastní složky; postupujte podle README a docs/INSTALL_WINDOWS.md.\n"
        "   Používejte Python 3.12 a připnuté requirements.lock. Údaje pro lokální demo jsou syntetické.\n"
        "4. Zdroje a offline sestavení jsou v production_sources/; návod video_course/full/README.md.\n"
        "5. Dlouhé běhy mohou být ve videu označeně zrychleny. Výsledky pocházejí ze skutečných běhů.\n"
        "   Reference kapitoly 04 je schválená R2.1; lidské schválení celého nového kurzu je samostatné.\n",
        encoding="utf-8",
    )
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    target = dist / "Playwright_Academy_Full_Course"
    target.mkdir(exist_ok=True)
    reference_archive = dist / "Playwright_Academy_R21_Complete.zip"
    assert (
        sha(reference_archive) == "d323cce898ca2beafc112a811ac8aab61d64402f331ae2bf24697623f60faaa4"
    )
    shutil.copyfile(reference_archive, target / "Reference_R21_Complete.zip")
    shutil.copyfile(HERE / "ACCEPTANCE_FULL.md", target / "ACCEPTANCE_FULL.md")
    for p in out.iterdir():
        if p.is_file() and p.suffix.lower() in {
            ".mp4",
            ".srt",
            ".vtt",
            ".json",
            ".txt",
            ".html",
            ".py",
            ".cmd",
        }:
            shutil.copyfile(p, target / p.name)
    project_path = target / "edit_project.json"
    project = json.loads(project_path.read_text(encoding="utf-8"))
    project["source_root"] = "production_sources"
    project_path.write_text(
        json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    starter = target / "Starter_Kit.zip"
    frozen = make_starter(starter)
    starter_review = json.loads(
        (HERE / "evidence/starter/validation.json").read_text(encoding="utf-8")
    )
    assert starter_review["decision"] == "PASS" and starter_review["archive_sha256"] == sha(starter)
    source = target / "production_sources"
    source.mkdir(exist_ok=True)
    selected = set(ROOT / name for name in frozen)
    # Only reproducible sources, not environments, historical rendering caches,
    # stale takes, runtime settings or any private .env, enter the package.
    for folder in (
        ROOT / "video_course/production",
        ROOT / "video_course/r2",
        ROOT / "video_course/r21",
        HERE,
    ):
        selected.update(
            p
            for p in folder.glob("*")
            if p.is_file() and p.suffix in {".py", ".json", ".md", ".bundle", ".cjs", ".txt"}
        )
    selected.add(ROOT / "video_course/storyboard/course_plan.json")
    selected.update(
        p
        for p in out.glob("*")
        if p.is_file() and p.suffix in {".json", ".srt", ".vtt", ".ass", ".ffmeta", ".txt"}
    )
    selected.update(p for p in (HERE / "evidence").rglob("*") if p.is_file())
    for n in range(1, 13):
        if n == 4:
            continue
        stage = HERE / "chapters" / f"{n:02}"
        selected.update(
            stage / name
            for name in (
                "timeline.json",
                "narration.wav",
                "beats.json",
                "capture_contract.json",
                "capture.json",
            )
        )
        selected.update(
            p
            for p in (stage / "output").glob("*")
            if p.is_file() and p.suffix in {".json", ".srt", ".vtt", ".ass", ".ffconcat"}
        )
        for section in json.loads((stage / "timeline.json").read_text(encoding="utf-8"))[
            "sections"
        ]:
            p = ROOT / section["audio"]
            selected.update((p, p.with_suffix(".json")))
        receipts = json.loads((stage / "capture.json").read_text(encoding="utf-8"))
        takes = {r["take"] for r in receipts}
        for r in receipts:
            p = ROOT / r["clip"]
            selected.update((p, p.with_suffix(".json")))
            if r.get("contract_path"):
                pickup_contract = ROOT / r["contract_path"]
                selected.add(pickup_contract)
                selected.add(ROOT / r["parent_receipt_path"])
                parent_data = json.loads(
                    (ROOT / r["parent_receipt_path"]).read_text(encoding="utf-8")
                )
                selected.add(ROOT / parent_data["clip"])
                pickup_data = json.loads(pickup_contract.read_text(encoding="utf-8"))
                selected.update(ROOT / name for name in pickup_data["inputs_sha256"])
        for take in takes:
            selected.update(p for p in (stage / "evidence" / take).rglob("*") if p.is_file())
            selected.update(p for p in (stage / "source_versions" / take).rglob("*") if p.is_file())
    selected.update(
        (ROOT / "video_course/r21/output" / name)
        for name in (
            "Playwright_Academy_R21_Prvni_Test.mp4",
            "Playwright_Academy_R21_Prvni_Test_Titulky.mp4",
            "edit_project.json",
            "narration.wav",
        )
    )
    selected.update(p for p in (ROOT / "video_course/r21/comparison").glob("*") if p.is_file())
    hashes = {}
    for p in sorted(selected):
        if not p.exists():
            raise FileNotFoundError(p)
        rel = p.relative_to(ROOT)
        dest = source / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dest)
        hashes[str(rel)] = sha(dest)
    (source / "source_manifest.json").write_text(
        json.dumps(hashes, indent=2) + "\n", encoding="utf-8"
    )
    payload = {
        p.relative_to(target).as_posix(): sha(p)
        for p in sorted(target.rglob("*"))
        if p.is_file() and p.name != "MANIFEST_SHA256.json"
    }
    (target / "MANIFEST_SHA256.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    archive_path = dist / "Playwright_Academy_Full_Course_Complete.zip"
    with zipfile.ZipFile(
        archive_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True
    ) as archive:
        for p in sorted(target.rglob("*")):
            if p.is_file():
                archive.write(p, p.relative_to(target))
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        for name, digest in payload.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    print(
        json.dumps(
            {
                "package": str(archive_path),
                "bytes": archive_path.stat().st_size,
                "sha256": sha(archive_path),
                "files": len(payload) + 1,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()

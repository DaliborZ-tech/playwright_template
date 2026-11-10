# Playwright Academy — Starter Kit pro referenci R2

Tento adresář je samostatný Python projekt s lokální demo aplikací a českými
cvičeními. Přesná zmrazená verze je v `video_course/r2/reference.json` a v Git
bundle `video_course/r2/starter-reference.bundle`. Distribuční MANIFEST.json
uvádí SHA-256 všech dodaných souborů.

Na Windows nainstalujte Python 3.12 x64. Spusťte `scripts/setup_windows.cmd`,
potom použijte níže uvedený příkaz pytest. Ruční postup a požadavky jsou v
`docs/INSTALL_WINDOWS.md`, výuka v `training/README.md` a podrobný průchod
v `docs/BEGINNER_WALKTHROUGH.md`. Aplikace používá výhradně syntetická data.

Soubor `tests/examples/test_video_created.py` odpovídá úspěšnému závěru nové
referenční kapitoly. Celá sada se spouští příkazem:

```powershell
.\.venv\Scripts\python.exe -m pytest tests training/solutions
```

Produkční plán, timeline, raw záznamy, originální Vlasta, titulky, důkazy a
reprodukovatelné skripty jsou v `video_course/r2`. Offline sestavení reference
a nové natáčení popisuje `video_course/r2/REPRODUCE_CZ.md`.

Videoprodukt jako celek má verdikt **CHANGES_REQUIRED**. Reference vyžaduje
úplné zhlédnutí, poslech a výslovné schválení vlastníkem; další kapitoly se
před tímto schválením nevyrábějí. Hlas zůstává Microsoft Vlasta z Edge.

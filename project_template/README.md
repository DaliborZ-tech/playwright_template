# playwright-tests

Samostatný základ pro Playwright + pytest testy vlastní aplikace v Pythonu
3.12. Obsahuje jeden spustitelný smoke test, HTML/JUnit reporty, trace,
screenshot a video při selhání. Aplikaci spouštíte vy nebo vaše CI.

## První spuštění na Windows

1. Spusťte `scripts\setup_windows.cmd` z terminálu. Vytvoří `.venv`, nainstaluje
   připnuté závislosti a Chromium a vytvoří `.env`, pokud ještě neexistuje.
2. V `.env` nastavte `BASE_URL` vlastní běžící testovací aplikace. Přihlašovací
   údaje lze zadat do `TEST_USERNAME` a `TEST_PASSWORD` pro vlastní scénáře.
3. Spusťte `scripts\run_tests.cmd -m smoke`.
4. Otevřete `scripts\open_report.cmd`.

URL lze přepsat pro konkrétní běh:

```powershell
.\.venv\Scripts\python.exe -m pytest --base-url https://app.example.test
```

Skutečné proměnné prostředí mají přednost před `.env`; `--base-url` má přednost
před `BASE_URL`. Příklad `app.example.test` nahraďte vlastní adresou.
První test ověřuje jen HTTP úspěch a viditelnou stránku. Další očekávání,
přihlášení i data doplňte podle konkrétní aplikace.

## Běžná práce

```powershell
scripts\run_tests.cmd
scripts\run_tests.cmd -m smoke --headed
scripts\run_tests.cmd -m regression
scripts\run_tests.cmd tests/smoke/test_availability.py -v
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m playwright codegen --target=python-pytest https://app.example.test
```

Codegen používejte jako návrh. Nahraďte jeho pevnou URL relativní navigací,
doplňte `expect` a upravený test skutečně spusťte. Při selhání najdete artefakty
v `reports/artifacts`; konkrétní trace otevřete:

```powershell
.\.venv\Scripts\python.exe -m playwright show-trace reports/artifacts/CESTA_K_TESTU/trace.zip
```

Každý test má vlastní browser context. Složky `pages` a `test_data` jsou
připravené pro objekty stránek a syntetická data. Nové testy pojmenovávejte
`test_*.py` pod `tests/`.

## Git a CI

`.gitignore` vynechává `.env`, prostředí, cache a `reports/` včetně trace,
videí a screenshotů. `.env.example`, `requirements.lock`, nastavení, testy
a syntetická data patří do Gitu. Před commitem zkontrolujte `git status`.

Pokud zde ještě není Git repozitář:

```powershell
git init -b main
git add .
git diff --cached --stat
git commit -m "Initial Playwright test project"
```

Potom nastavte svůj vzdálený repozitář a proveďte push. V CI použijte
Python 3.12, instalaci `python -m pip install -r requirements.lock`,
`python -m playwright install --with-deps chromium` a `python -m pytest`.
`BASE_URL` a případné přihlašovací údaje nastavte v CI proměnných.
Reporty publikujte jako CI artefakty i při neúspěchu testů. Návratový kód
pytestu zachovejte, aby neúspěšný test způsobil neúspěšný pipeline běh.

# Playwright Academy · Python / česky

Praktický Starter Kit pro manuálního testera: skutečný lokální QA Training
Portal, čitelné synchronní Playwright testy a postupná výuka v češtině.
Příběh je společný: přihlásit se → vytvořit požadavek → upravit → smazat →
spustit regresi → najít příčinu chyby.

**Stav celé dodávky a omezení:** [akceptace](docs/ACCEPTANCE.md).
Původní 97minutový videokurz má verdikt **CHANGES_REQUIRED**. Aktuální oprava
**R2.1** dodává referenční kapitolu 5:48, kterou vlastník **10. 11. 2026 schválil**.
Navazující výroba je autorizovaná podle přijatého standardu.
Platný hlas je **Microsoft Vlasta z Edge**.
Aktuální pokračování popisuje [CONTINUE_HERE.md](CONTINUE_HERE.md).

## Čistá šablona pro nový projekt

Pro testování vlastní aplikace použijte samostatnou [projektovou šablonu](project_template/README.md).
Nevkládá do nového projektu demo, výuku ani produkční data videokurzu.
Z kořene tohoto repozitáře ji založíte například takto:

```powershell
.\.venv\Scripts\python.exe scripts\new_project.py C:\QA\moje-testy --git
```

Vznikne nová složka s vlastním Gitem na větvi `main`, připnutými závislostmi,
`.gitignore`, ukázkovým smoke testem a Windows spouštěči. Existující neprázdnou
složku příkaz odmítne. Pokračujte novým `README.md`: instalace, nastavení
`BASE_URL` v `.env` a spuštění testů. Generátor potřebuje jen standardní Python;
bez zdejšího prostředí lze použít také vlastní Python 3.12.

Samostatně lze rozbalit také `dist/Playwright_New_Project_Template.zip`.
Podrobný postup a pravidla pro první push jsou v [GIT_AND_NEW_PROJECT.md](GIT_AND_NEW_PROJECT.md).

## První spuštění na Windows 11

Potřebujete Python **3.12 x64** z [python.org](https://www.python.org/downloads/).
Při instalaci povolte Python launcher. Zdrojový projekt rozbalte do vlastní
zapisovatelné složky, například `C:\QA\playwright-academy`.

1. Spusťte `scripts\setup_windows.cmd` (nejlépe z terminálu, aby zůstala vidět chyba).
2. Spusťte `scripts\run_smoke.cmd`. Testy spustí vlastní demo automaticky.
3. Spusťte `scripts\open_report.cmd`.
4. Pro ruční průzkum spusťte `scripts\start_demo.cmd` a otevřete
   <http://127.0.0.1:5000>. Toto okno nechte běžet; ukončení je Ctrl+C.

Veřejný **syntetický** účet: `tester@example.test` / `Academy123!`.
Instalace nemění bezpečnostní politiku ani nevyžaduje aktivaci PowerShell skriptů.
Podrobnosti: [instalační průvodce](docs/INSTALL_WINDOWS.md).

| Co chcete udělat | Windows akce |
|---|---|
| Rychlá kontrola přihlášení | `scripts\run_smoke.cmd` |
| Celá regresní sada | `scripts\run_regression.cmd` |
| Vidět prohlížeč při testu | `scripts\run_visible.cmd` |
| První samostatný test | `scripts\run_single_test.cmd` |
| Konkrétní test | `scripts\run_single_test.cmd tests/smoke/test_login.py::test_02_successful_login` |
| HTML výsledek posledního běžného běhu | `scripts\open_report.cmd` |
| Řízená chyba, očekávaný návratový kód 1 | `scripts\run_failure.cmd` |
| Opravená verze výukového testu | `scripts\run_fixed.cmd` |
| Poslední trace, včetně řízené chyby | `scripts\open_trace.cmd` |
| Codegen (nejprve ručně spusťte demo) | `scripts\run_codegen.cmd` |

Codegen zapisuje do `tests/examples/codegen_draft.py`, který pytest sám
nesbírá. Před přejmenováním na `test_*.py` upravte URL na `/login`, ověřte
očekávání a spusťte draft jako konkrétní soubor. Absolutní URL z nahrávky
patří ručně běžícímu demu; testovací sada má vlastní náhodný port.

## Práce z terminálu

V kořeni projektu v PowerShellu:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest -m smoke
.\.venv\Scripts\python.exe -m pytest -m regression --headed
.\.venv\Scripts\python.exe -m pytest tests/examples/test_first_test.py -v
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

Testy nevyžadují současně spuštěný `start_demo.cmd`. Automatický server běží
na volném portu pouze na loopbacku a po sadě se ukončí. Data jsou oddělená
po browser contextu. Reset se vztahuje pouze na aktuální relaci.

## Kde začít s učením

Otevřete [uživatelský manuál a pořadí lekcí](training/MANUAL.md). Každá ze
12 lekcí obsahuje vysvětlení, konkrétní soubor, příkaz, úkol a řešení.
[Česká reference 45 položek](training/cheatsheets/playwright-python.md)
pomůže při samostatné práci. [Řešení problémů](training/troubleshooting/windows.md)
pokrývá Windows, proxy, certifikáty i ladění.

## Jiná schválená aplikace

Demo testy záměrně nepřijímají cizí `--base-url`. Vytvořte vlastní testy
v `tests_external`, nastavte `.env` podle `.env.example` a spusťte:

```powershell
.\.venv\Scripts\python.exe -m pytest tests_external --external
```

Ukázka provádí pouze GET a kontrolu dostupnosti. Přihlášení a měnící akce
doplňte pro svou schválenou testovací instanci s vlastními syntetickými daty.
`TEST_USERNAME` a `TEST_PASSWORD` čtěte přes `os.environ`; nikdy je nevkládejte
do zdrojů, příkazové řádky ani komentáře. Trace a video mohou zachytit citlivý
obsah, proto pro firemní prostředí určete přístup a retenci artefaktů.

## Struktura

- `demo_app`: Flask + Waitress, HTML a JS, bez externích databází a fontů.
- `tests`: smoke, regression, validation, examples, advanced, teaching.
- `test_data`: veřejná syntetická data. `pages`: jeden volitelný Page Object.
- `training`: lekce, úkoly, spustitelná řešení, reference a troubleshooting.
- `video_course`: scénář, storyboard a produkční nástroje.
- `reports`: generované reporty a diagnostika; běžný běh přepíše poslední report.
- `evidence`: trvalé důkazy ověřování, oddělené od přepisovaných reportů.

Výchozí `pytest` nesbírá řízeně chybující test. HTML a JUnit jsou v `reports/`.
Screenshot, trace a diagnostické browser video zůstávají při selhání.
Browser video zaznamenává pouze obsah stránky a nenahrazuje záznam výuky
v editoru a terminálu. Alternativní Firefox/WebKit vyžadují vlastní instalaci
příkazem `python -m playwright install firefox webkit` z projektové `.venv`.


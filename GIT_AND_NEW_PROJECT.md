# Nový projekt a malý Git repozitář

## Založení nového projektu

Z kořene Academy spusťte:

```powershell
.\.venv\Scripts\python.exe scripts\new_project.py C:\QA\moje-testy --git
```

Název se odvodí od cílové složky; volitelně použijte `--name moje-e2e-testy`.
Pro cestu s mezerami použijte uvozovky. `--git` založí samostatný repozitář
na větvi `main`; bez přepínače se pouze vytvoří soubory. Neprázdný cíl se
odmítne, existující projekt se nepřepisuje.

Nový projekt obsahuje `tests`, `pages`, `test_data`, vlastní konfiguraci,
prázdný vzor `.env.example`, připnuté závislosti a Windows spouštěče. Nemá
demo aplikaci ani závislost na kurzu. Generátor kopíruje explicitní seznam
16 souborů, takže nepřenese zdejší `.env`, prostředí, historii ani reporty.

V novém projektu spusťte `scripts\setup_windows.cmd`, nastavte `BASE_URL`
v jeho `.env`, spusťte vlastní aplikaci a ověřte `scripts\run_tests.cmd -m smoke`.
Podrobný návod je v jeho `README.md`.

Pokud chcete přenést šablonu bez tohoto repozitáře, rozbalte
`dist/Playwright_New_Project_Template.zip` do nové složky. Archiv má stejných
16 souborů a je rovnou použitelný. Pro vlastní nové sestavení archivu:

```powershell
.\.venv\Scripts\python.exe scripts\new_project.py --archive C:\QA\nova-sablona.zip
```

Existující archiv se nepřepisuje. Zdroj upravované šablony je `project_template/`;
při přidání dalšího souboru doplňte také seznam `FILES` v `scripts/new_project.py`.

Generátor a skutečné testy proti lokálnímu HTTP serveru lze znovu ověřit:

```powershell
.\.venv\Scripts\python.exe scripts\verify_project_template.py
```

Ověření vytvoří projekt v cestě s mezerami, zkontroluje odmítnutí přepsání,
samostatný Git, obsah ZIPu, úspěšný test i řízenou HTTP chybu 503, reporty
a diagnostické artefakty. Pro testy využívá již nainstalované připnuté
závislosti; nepředstavuje novou síťovou instalaci. Důkaz je v
`.tools/template-verification/validation.json`.

## Co patří do Gitu v tomto Academy repozitáři

Verzují se zdroje aplikace a testů, závislosti, dokumentace, projektová šablona,
produkční skripty a textový storyboard. `.gitignore` vynechává prostředí,
`.tools`, soukromé `.env`, reporty, výstupní distribuce a generovaná produkční
data kurzu včetně raw záznamů, audia a sestavených filmů. Velké výstupy zůstávají
na disku; ignorování je nemaže.

Úplné zdroje k reprodukci již dodaného videa jsou v
`dist/Playwright_Academy_Full_Course_Complete.zip`. Samotný Git checkout bez
těchto mediálních podkladů slouží pro vývoj aplikace, testů a produkčních
skriptů. Schválené distribuční ZIPy a zmrazený Starter Kit se nemění.

## První commit a push

V tomto repozitáři při úpravě nebyl žádný commit ani sledovaný soubor. Není
potřeba mazat soubory z indexu ani přepisovat historii. Před prvním commitem:

```powershell
git status --short
git add .
git diff --cached --stat
git diff --cached --name-only
git commit -m "Initial Playwright Academy sources and project template"
```

Potom v nově založeném vzdáleném repozitáři zkopírujte jeho skutečnou adresu:

```powershell
git branch -M main
git remote add origin ADRESA_VASEHO_REPOZITARE
git push -u origin main
```

Pokud už `origin` existuje, ověřte jeho nastavení místo opakování `remote add`.
Commit ani push se při přípravě šablony automaticky neprovádí.

Lokální `.git/objects` obsahuje také starší nedosažitelné a dočasné objekty.
Ty se při prvním pushi nové větve neposílají; jejich velikost není velikostí
budoucího commitu. Historická lokální data ani Git objekty nebyly mazány.

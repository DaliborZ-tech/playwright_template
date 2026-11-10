# Instalace pro člověka, který dosud nepoužíval Python

Python je program, který přečte náš testovací soubor a provede jeho příkazy.
pytest vyhledá testy a vyhodnotí jejich výsledky. Playwright ovládá prohlížeč.
Chromium je otevřený prohlížečový engine, který Playwright instaluje zvlášť;
nenahrazuje tím váš běžný firemní Chrome.

## 1. Python a projekt

Nainstalujte Python 3.12 x64 ze schváleného zdroje, typicky python.org.
Instalace pouze pro svého uživatele obvykle nepotřebuje administrátora.
Pokud instalaci spravuje IT, požádejte o stejný profil. Rozbalte projekt do
vlastní složky. Vyhněte se Program Files a síťovým diskům s omezeným zápisem.

V Průzkumníkovi otevřete složku projektu. Do adresního řádku napište
`powershell` a potvrďte Enter. Terminál je okno, ve kterém zadáváte příkazy;
každý potvrzujete Enter. Ověřte `py -3.12 --version`. Očekáváte `Python 3.12.x`.
Jestli se zobrazí jiná verze nebo Store, pokračujte troubleshootingem.

## 2. Oddělené prostředí

Spusťte `scripts\setup_windows.cmd`. Skript založí `.venv` a nainstaluje
do ní přesné závislosti z `requirements.lock`. Virtuální prostředí je složka
s vlastním Pythonem a knihovnami. Odděluje tento kurz od ostatních projektů.
Není to virtuální počítač. Složku `.venv` neposílejte kolegům: každý si ji
vytvoří na své stanici. Přesunutá `.venv` nemusí fungovat.

Skript neobchází proxy ani certifikáty a nepřepisuje existující `.env`.
Po úspěchu oznámí HOTOVO. Při chybě zachová návratový kód; poslední chyba
určuje příčinu. Po opravě síťového přístupu lze instalaci spustit znovu.
Neúspěšná instalace není důvod vypínat bezpečnostní ochrany.

Ruční ekvivalent, pokud máte standardní Python launcher:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m playwright install chromium
```

Projekt má ověřovaný profil pouze 3.12. Novější Python nejdříve ověřte v
oddělené kopii včetně všech testů a knihoven; nepřepínejte kurz naslepo.

## 3. Editor a první test

Nainstalujte Visual Studio Code ze schváleného zdroje. File → Open Folder
otevře kořen s README. Rozšíření Python poskytuje doplňování a spouštění
testů. Ctrl+Shift+P → Python: Select Interpreter → vyberte
`.venv\Scripts\python.exe`. Nesprávný interpreter je běžná příčina chyby
`ModuleNotFoundError`, i když instalace proběhla správně.

Spusťte `scripts\run_smoke.cmd`. Test si sám otevře Chromium na pozadí.
Terminál musí skončit kódem 0 a výpisem passed. `scripts\run_visible.cmd`
ukáže prohlížeč. `scripts\open_report.cmd` otevře HTML výsledek.
PyCharm: Open složku projektu → Settings → Python Interpreter → existující
`.venv\Scripts\python.exe`; testovací runner zvolte pytest.

## 4. Ruční průzkum

`scripts\start_demo.cmd` vytvoří ručně dostupnou instanci na portu 5000.
Otevřete http://127.0.0.1:5000 a přihlaste se veřejným účtem z README.
Pokud je port obsazený, neukončujte cizí proces. Pro ruční demo zvolte
`.\.venv\Scripts\python.exe -m demo_app.app --port 5001` a upravte URL.
Codegen launcher předpokládá port 5000. Automatické testy mají vlastní port
a ruční data z tohoto prohlížeče neuvidí.

## Firemní síť

Od IT si vyžádejte schválenou proxy a CA řetězec pro PyPI a Playwright CDN.
Podle prostředí se používá `HTTPS_PROXY`, `PIP_CERT` a
`NODE_EXTRA_CA_CERTS`; proměnné nastavujte dle firemního postupu.
Nepřidávejte heslo do veřejných logů. Nepoužívejte `--trusted-host`,
vypnutí TLS nebo změnu ExecutionPolicy jako univerzální opravu.


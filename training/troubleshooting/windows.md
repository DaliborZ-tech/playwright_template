# Když se něco nedaří

## Python, prostředí a práva

„Python nebyl nalezen“: otevřete nové okno terminálu po instalaci. Ověřte
`py -3.12 --version`. Python manager může mít zvlášť evidovaný Astral/uv runtime;
pak použijte jeho přesný tag z `py list`, nebo standardně nainstalujte profil
3.12. Na vývojové stanici tohoto projektu byl použit Astral CPython 3.12.15.
Instalátor může znovu použít již existující projektovou `.venv` ve verzi 3.12.

`ModuleNotFoundError`: porovnejte interpreter ve VS Code s
`.venv\Scripts\python.exe`. Samotné `python` v terminálu může být jiný program.
Aktivace není nutná. Neinstalujte balíčky náhodně do systémového Pythonu.

`Access denied`: projekt musí být v uživatelsky zapisovatelné složce. Cizí
firemní omezení řešte s IT. Nepoužívejte automaticky administrátorský terminál.
Stará či přenesená `.venv`: přejmenujte ji a instalujte v nové složce; skript
ji sám nemaže. Instalační skript s jinou verzí Pythonu skončí diagnostikou.

## Browser a síť

„Executable doesn't exist“: projektovým Pythonem spusťte `-m playwright install chromium`.
Proxy a certifikáty řešte odděleně pro pip a Playwright downloader. Použijte
schválené HTTPS_PROXY, PIP_CERT a NODE_EXTRA_CA_CERTS. Heslo proxy nezapisujte
do reportu. Nikdy nevypínejte TLS a neinstalujte náhodné certifikáty z internetu.

Chyba při ukládání browser videa, například spawn UNKNOWN: ověřte instalaci
browserů i FFmpeg přes `python -m playwright install chromium` a následně
zopakujte malý test. Blokaci spustitelných souborů řešte s IT. Jednorázová chyba
není důkaz zeleného běhu; archivujte až opakovaný skutečně úspěšný výsledek.

Port 5000 obsazený: ručnímu demu zvolte jiný port, neukončujte neznámý proces.
Automatická sada používá volný port a ruční demo nepotřebuje. Ručně vytvořená
data nejsou vidět v testech: je to záměrná izolace, nikoliv chyba aplikace.

## Lokátory a čekání

Strict mode violation: stejnému popisu odpovídá více prvků. Upřesněte roli,
exact nebo oblast, například konkrétní řádek. `first` nepoužívejte jako
univerzální opravu. Timeout: zkontrolujte správnou URL, přihlášení, jméno prvku
a skutečné očekávané chování. Pak screenshot a trace; delší timeout až po diagnóze.

Nativní dialog se zasekl: zaregistrujte `page.once("dialog", ...)` před kliknutím.
Text se mění asynchronně: používejte `expect`, nikoliv pevné čekání. Vyhledávání
může vyvolat více požadavků; portál vykreslí pouze odpověď posledního dotazu.

## Reporty a diagnostika

Řízená chyba končí 1: to je správný výukový výsledek. Běžná regrese ji nesbírá.
Trace chybí po úspěchu: režim retain-on-failure uchovává pouze neúspěšné běhy.
Chcete-li trace i při úspěchu, použijte `--tracing=on` s vlastním --output.
Report se změnil: další běh jej přepisuje, důležité výsledky nejprve archivujte.

Čeština v terminálu: spouštěče nastavují PYTHONUTF8=1. Soubory jsou UTF-8.
VS Code může zobrazit kód správně, i když starý terminál používá jinou stránku.
Zkontrolujte encoding, nepřepisujte správné řetězce rozbitým textem z konzole.

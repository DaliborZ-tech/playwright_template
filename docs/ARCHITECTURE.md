# Architektura a ověřené zdroje

## Rozhodnutí

Python 3.12 x64, synchronní API, pytest-playwright, Chromium. Flask a Waitress
obsluhují lokální demo. Není potřeba Node runner, databáze, TestFlow ani externí
frontend CDN. `requirements.lock` obsahuje přesné přímé i tranzitivní verze;
kompatibilitu dokládá skutečná instalace, pip check a browser testy. Změny locku
vyžadují nový běh těchto kontrol. Lock je pro ověřený Windows/Python 3.12 profil.

Testy začínají přímými akcemi na `page`. Jediný Page Object je volitelná
pozdější ukázka, ne povinný základ každého testu. pytest fixtures dodají nový
browser context a testovací server. Server váže port 0, tedy volný port OS.
Session má náhodné ID a CSRF token. Každá relace má vlastní kopii seed záznamů.
Reset nikdy nemaže data jiné relace. Po restartu serveru mizí všechny relace.
Data neaktivních relací expirují; stav je omezen na 200 relací a 100 záznamů.

Demo poslouchá pouze na 127.0.0.1 a nepoužívá debug režim. Veškeré texty z dat
se vykreslují escapovaně / přes textContent. Měnící požadavky vyžadují CSRF.
Veřejné demo heslo není firemní tajemství. Demo neposkytuje produkční IAM,
odolnost nebo trvalé ukládání; firemní nasazení není jeho účel.

## Výuková kontinuita

Stejný portál, účet a syntetické požadavky v lekcích, řešeních i storyboardu.
Růst složitosti: ruční průzkum → první přímočarý test → parametrizace → fixtures
→ celá cesta → Codegen → řízené selhání → trace → regrese. Codegen je pomocník:
umí akce i některé assertions, výběr požadovaného chování však určuje tester.

## Technické zdroje

Prohlédnuto při realizaci 9. 11. 2026. Podpora konkrétního vydání se ověřuje
také instalací skutečných balíčků; dokumentace webu může popisovat novější verzi.

- https://playwright.dev/python/docs/intro
- https://playwright.dev/python/docs/writing-tests
- https://playwright.dev/python/docs/locators
- https://playwright.dev/python/docs/test-runners
- https://playwright.dev/python/docs/codegen
- https://playwright.dev/python/docs/trace-viewer
- https://playwright.dev/python/docs/running-tests
- https://playwright.dev/python/docs/api-testing
- https://docs.pytest.org/en/stable/
- https://ffmpeg.org/documentation.html
- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech
- https://support.microsoft.com/en-us/accessibility/windows/narrator/appendix-a-supported-languages-and-voices

## Produkce videa

Po ověření zmrazit soubory SHA-256 manifestem. Nahrávat skutečný desktop
v oddělené výukové relaci bez osobních aplikací. Jedna česká hlasová identita
pro celý kurz, krátké tematické scény navázané na konkrétní kód. Časování
odvozovat od skutečného audia a nahrávek, nikoliv od odhadovaných minut.
Povinný je záznam VS Code, terminálu, Codegenu, Inspectoru a Trace Vieweru.
Browser recording není plnohodnotný desktop recording.

Jakub je hlas Windows, není to název neurálního hlasu Azure. SAPI a OneCore
mají rozdílné katalogy, proto se kontrolují oba. Bezplatnost či nekomerční
účel sám o sobě neřeší oprávnění použité služby nebo redistribuci modelu.
Licenční soubory a podmínky zvolené služby uchovat se zdrojovými materiály.

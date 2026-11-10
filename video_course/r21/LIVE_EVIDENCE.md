# R2.1 — přímé důkazy skutečných ukázek

Tento přehled odstraňuje mezeru předání R2-F05: důkazy jsou součástí téhož
balíku jako MP4, nikoli pouze tvrzením podle vzhledu filmu. Uvádí technické
ověření skutečných zdrojů; nezastupuje lidskou obsahovou akceptaci filmu.

## Přesná verze

Starter Kit: commit **129d317771d91da04e31e8150a2111188f9ae51f**.
`reference.json` uvádí SHA-256 všech **78** zmrazených souborů a hash
`starter-reference.bundle`. Bundle lze klonovat příkazem
`git clone --branch r2-frozen starter-reference.bundle nova-prazdna-slozka`.
Zdrojový projekt obsahuje právě tyto soubory včetně skutečné aplikace,
testů, fixture, dat, manuálu a requirements.lock. Hashy jsou ověřovány znovu
při balení. Nové produkční skripty nemění zmrazený Starter Kit.

## Mapa důkazů v adresáři sources

| Co video ukazuje | Originál a skutečný stav | Vazba na R2.1 |
| --- | --- | --- |
| Psaní prvního testu | `video_course/r2/recordings/02_import.mp4` až `04_button.mp4`; receipty obsahují skutečný uložený text a SHA | `video_course/r21/capture.json` zachovává parent_clip, parent SHA, původní capture contract a přesné body přečasování |
| Nadpis a tlačítko v DOM | `video_course/r2/recordings/03_dom.mp4` a `04_button_dom.mp4`; skutečné outerHTML a vybraný nativní řádek DevTools v receiptech | Není vydáváno za statickou maketu; DOM nadpis je skutečný `h2`, role heading, název Přihlášení |
| Tentýž test RED→GREEN | `video_course/r2/evidence/take_1794309488/red/` a `green/`: JUnit, HTML a originální pytest WEBM | `actual_junit_nodeid` je v obou bězích totožný; exit1/failure1 a exit0/failure0, errors0/skipped0 |
| Změna jediné hodnoty | Source text v receiptech make_red/make_green | Rozdíl je pouze Neexistující nadpis → Přihlášení; finální soubor je shodný se zmrazeným Starter Kitem |
| Report úspěšného testu | Čerstvý `green/report.html`, raw `07_report.mp4` a `07_details.mp4` | Levý Result/Passed sloupec i celý skutečný nodeid zůstávají v obrazu |
| Nový skutečný Codegen | `video_course/r21/recordings/cg_*.mp4`; `codegen_capture.json` a `codegen_capture_contract.json` | Zachycen skutečný CLI proces, jeho browser a nativní Inspector; žádná překreslená napodobenina |
| Výstup Codegenu | `video_course/r21/evidence/codegen/cg_inspector.py` a předchozí kroky | Obsahuje skutečné `get_by_role("textbox", name="E-mail").fill("tester@example.test")`; syntetický účet |
| Spustitelnost návrhu | `video_course/r21/evidence/codegen_execution/junit.xml`, HTML a WEBM | Skutečný test_example prošel; samotný návrh ovšem neobsahuje vlastní očekávání, jak vysvětluje komentář |

Nodeid přihlašovacího testu:
`tests/examples/test_video_created.py::test_video_login_form[chromium]`.
`quality_audit.json` parsuje skutečný JUnit a ověřuje hash reportů a WEBM,
nikoli pouze řetězec deklarovaného nodeid.

## Co střih mění

Původních 27 akcí R2 zůstává zachovaných. R2.1 zkracuje čekání a výkladové
držení; ve dvou bězích je záznam mírně časově zrychlený, což přesně uvádí
`active_speed_factor` a `retiming_control_points`. Časy ve filmu se proto
nemají zaměňovat s původní délkou procesu pytest. Skutečné výsledky běhů
a zdrojový kód se nemění. V párovém Codegen záběru je zakryt pouze úzký
DWM spoj mimo obě vlastní okna, nikoli část aplikace nebo kódu.

`audio_edits.json` dokládá vynechané tiché vzorky pod −45 dB a původní audio
SHA. Neprobíhá natahování řeči ani překrývání hlasů. Výslovnost a identita
Vlasty jsou zachované; nový Codegen odstavec je rovněž Vlasta.

## Poslech a schválení

Vlastník skutečně porovnal 30 s před/po a odpověděl:
„Rytmus po úpravě je v pořádku, slova nejsou useknutá.“
`comparison/human_listening_review.json` váže tento výrok na oba WAV hashe.
Je to schválení konkrétní zvukové ukázky, nikoli celého filmu nebo 12 kapitol.
Následně 10. 11. 2026 vlastník samostatně odpověděl „schvaluji“ na celou
referenci. Aktuální rozhodnutí, přesné hashe a rozsah autorizované navazující
výroby jsou v `po_approval.json` a `APPROVAL_R21.md`.

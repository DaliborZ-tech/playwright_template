# Playwright Academy R2 — nezávislá revize referenční kapitoly

**Podklady:** `Playwright_Academy_R2_Prvni_Test.mp4`, `Playwright_Academy_R2_Prvni_Test_Titulky.mp4`  
**Rozsah:** 5 min 48,48 s, kapitola „První test“  
**Hodnocení:** **CONDITIONAL PASS jako referenční ukázka; CHANGES REQUIRED před výrobou celého kurzu**.

## Metoda

Provedena kontrola obou přiložených souborů přes ffprobe a ffmpeg, extrakce vložených českých titulků, prohlídka kontrolních snímků v intervalu 12 sekund a jednotlivých plnorozměrových snímků; porovnání obou verzí v šesti časových bodech; analýza změn obrazu v jednosekundových intervalech; měření časování titulků a analýza hlasitosti. Nejde o audit zdrojového repozitáře ani o osobní poslech kompletního komentáře. Autenticita všech údajně živých akcí nebyla ověřena proti originálním capture souborům a samotnému Starter Kitu.

## Technická fakta

- Obě videa mají délku **348,48 sekundy**, 1920 × 1080, 25 fps, H.264, AAC LC mono 48 kHz.
- Základní soubor má **73 českých subtitle cues** v embedded MP4 stopě `mov_text` (jazyk `ces`, čas až 05:47,437). Tento typ vyžaduje zapnutí titulků a kompatibilní přehrávač.
- Soubor s názvem `Titulky` nemá samostatnou subtitle stream, protože má **české titulky vypálené v obrazu**. Potvrzeno vizuální kontrolou v 02:30 a dalšími snímky.
- Zvuková stopa v obou souborech má shodný dekódovaný SHA-256: `54b103f04494a68b3e7a5db942d6521106b853af93a0f5023706d2a6bb0ecfca`.
- Hlasitost: přibližně **−16,02 LUFS**, true peak **−1,60 dBTP**. Technická úroveň je vhodná pro srozumitelný komentář, ale z těchto čísel samotných neplyne přirozená intonace.

## Ověřené pozitivní změny

- Nejde již o jediný statický obrázek: záběry postupují od přihlašovací stránky přes editor, prohlížení DOM, psaní assertions, záměrně chybnou hodnotu, selhání, opravu a HTML report.
- V obrazu jsou čitelná klíčová místa zdrojového kódu a využívají se zelené rámečky, horní lišta s identitou kurzu a spodní popisky.
- Obsah českých titulků je v souvislejších výukových větách a děj logicky navazuje.
- Dvě alternativy titulků řeší kompatibilitu přehrávače lépe než předchozí dodávka.

## Zbývající nálezy

### R2-F01 — P1/P2: pravidelně dávkovaný komentář (priorita před škálováním)

Mezi 73 subtitle cues je **72 mezer**, jejich medián **1,018 sekundy**, součet **67,56 sekundy**, a **62 z 72** je dlouhých přibližně 0,85 až 1,2 s. Digitální audio detekce potvrzuje odpovídající zhruba sekundové ticho ve vzorkovaných časových úsecích. To vytváří dojem opakovaných, mechanických pauz mezi větami. Přirozenost konkrétního hlasového projevu nebyla auditorem subjektivně poslechem ověřena.

**Náprava:** zachovat schválený hlas Microsoft Vlasta z Edge. Upravit segmentaci a střih podle významových odstavců, nikoli po jednotlivých titulkových větách. Pauzy diferencovat: krátké uprostřed souvislé myšlenky, delší při zásadní akci/přechodu. Ručně ověřit přirozený poslech a nepřekrývat řeč.

### R2-F02 — P2: dlouhé téměř statické úseky

Z porovnání 1fps zmenšených snímků je **74,6 %** mezisnímkových změn pod průměrnou absolutní změnou 0,6/255. Neznamená to nulový pohyb, ale potvrzuje dlouhé holdy. Orientačně nejdelší úseky bez výrazné změny: **01:56–02:21 (25 s), 01:09–01:32 (23 s), 02:24–02:43 (19 s)**. Některé delší komentáře tak probíhají nad téměř nezměněnou scénou.

**Náprava:** ve statických intervalech zařadit účelové popisky, detailní přiblížení přes správné argumenty/metody, přepnutí do browseru, zobrazení odpovídajícího UI elementu nebo přeformulovat/zkondenzovat vysvětlení. Nedělat zbytečné přechody jen kvůli pohybu.

### R2-F03 — P2: prokázané focus výřezy, ale neověřený plynulý zoom

Video prokazatelně používá výřez editoru a vizuální rámečky. Z kontrolních snímků ovšem nebylo možné potvrdit, že dochází k **plynulým animovaným zoom přechodům**, jak požadoval produktový kontrakt. Jednotlivé významnější změny snímků mohou být také prosté střihy.

**Náprava:** doložit konkrétní 2–3sekundový plynulý zoom s jasným cílem (např. přechod z `page.goto` na `get_by_role`) a návrat do kontextu. Testovat skutečný vznik geometrického přiblížení, ne pouze existenci předem zvětšeného záběru.

### R2-F04 — P3: drobení některých titulků

Například **00:46,636–00:47,422: „examples.“**, **05:39,447–05:40,388: „znovu spusťte.“**. Jde o zbytečně krátké samostatné titulkové cues vzniklé rozdělením věty. Vyladit segmentaci bez přesahu do jiných scén. Titulky napevno jsou vizuálně funkční; embedded titulky přepínat v přehrávači.

### R2-F05 — P2: přímá shoda se Starter Kitem není ještě doložena

Z videa je vidět testovací soubor `tests/examples/test_video_created.py`, ukázky terminálu a HTML report. Ověření zdrojových artefaktů a skutečných záznamů běhů proti zmrazenému commitu Starter Kitu ale není součástí tohoto předání. Nelze proto zatím udělit `LIVE_DEMONSTRATION_VERIFIED` jen podle vzhledu videa.

## Obsahový přehled referenční kapitoly

- **00:00–00:37:** přihlašovací stránka a základní očekávání;
- **00:38–01:48:** práce v editoru, založení testu a navigace;
- **01:49–03:08:** zkoumání DOM, role, lokátory a assertions;
- **03:08–04:18:** záměrně nesprávný nadpis, spuštění a diagnostika selhání;
- **04:18–04:56:** oprava a opakovaný úspěšný běh;
- **04:56–05:48:** HTML report, shrnutí, samostatný úkol.

Časové hranice jsou přibližné podle obsahu a kontrolních snímků, nikoliv přesné hranice renderovaných scén.

## Akceptační brána pro další Codex iteraci R2.1

1. **ZACHOVAT** Microsoft Vlasta, strukturu kapitoly, existující skutečné akce a dvě varianty titulků.
2. **OPRAVIT** pravidelné sekundové audio mezery; dodat srovnání 30sekundového úseku před/po a doložit poslechové review.
3. **ZKRÁTIT/OŽIVIT** tři identifikované statické úseky, aniž by se odstranilo potřebné vysvětlení.
4. **PROKÁZAT** účelový plynulý zoom alespoň u dvou významových přechodů.
5. **SLOUČIT** fragmentované titulky, udržet synchronizaci a českou diakritiku.
6. **DOLOŽIT** zmrazenou verzi Starter Kitu a odpovídající autentické test runs, DOM/Codegen/HTML report záznamy v rámci zvolené kapitoly.
7. **VYDAT** revidovaných 5:48 min v obou titulkových variantách a doložit obsahovou revizi člověkem.
8. **NEPOKRAČOVAT** ve výrobě všech 12 kapitol před schválením referenčního vizuálního i zvukového standardu Product Ownerem.

**Verdikt:** produkční koncept R2 významně překonal původní statické video. Kapitola je použitelný základ pro finální styl, ale **zatím nedoporučuji spustit dávkovou produkci celé 97minutové série**, dokud neproběhne R2.1 polish a poslechová akceptace.

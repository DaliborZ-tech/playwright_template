# Playwright Academy — nezávislý audit produkčních podkladů a opravný mandát R2

**Zdroj:** `Playwright_Academy_Production_Sources.zip` (uživatelem předaný archiv, 355 MiB přibližně).  
**Rozsah kontroly:** 97 dílčích MP4 scén, jejich JSON metadata, 97 hlasových segmentů, individuální SRT/VTT, časová osa, 3 archivované snímky na scénu a metadata výsledného videa. **Finální složený MP4 není součástí archivu.**  
**PO rozhodnutí:** Video product **CHANGES_REQUIRED**. Schválený hlas **Microsoft Vlasta v Edge** (`cs-CZ-VlastaNeural`) — **NEPŘEPÍNAT NA JAKUBA**.

## Ověřitelné nálezy

### P1-V01 — Nedostatečná vizuální aktivita, scénář videa stojí na statických obrazovkách

- Archiv obsahuje **97 video-scén** za **12 kapitol**, celková časová osa **5 831,59 s ≈ 97 min 12 s**.
- Kontrolou archivovaných snímků z časů přibližně 10 %, 50 %, 90 % každé scény má **79/97 scén minimální změnu obrazu** (průměrný absolutní rozdíl RGB po zmenšení na 160 × 90 je menší než 0,5/255 mezi prvním a posledním kontrolním snímkem). Tyto scény představují **4 630,36 s, tj. 79,4 % časové osy**. Toto měření není náhražkou plnohodnotné analýzy každé vteřiny, jde však o silný signál statického pojetí.
- Scéna `04_06.mp4` trvá **168,62 s**; nezávislé dekódování a vizuální porovnání snímků po 10 s ukázalo prakticky totožný obsah, maximální průměrný rozdíl asi **0,09/255**.
- Další dlouhé prakticky statické scény dle tří kontrolních snímků: `01_06` (176 s), `02_06` (172 s), `05_06` (157 s), `06_06` (158 s), `07_07` (171 s), `09_06` (168 s), `10_06` (163 s), `11_06` (167 s).

**Požadované:** Přestavět střih na skutečně názorné **ukázky činností**. Vysvětlení výběru lokátoru musí být vizuálně spojeno s otevřením DOM nebo Inspectoru; vysvětlení testu s jeho psaním, spuštěním a ověřením. Dlouhé statické držení editoru nezachovávat. Klip bez smysluplné aktivity musí být upraven, nahrazen reálným záznamem, nebo zkrácen; nepoužívat náhodnou animaci jako náhradu výuky.

### P1-V02 — Nedostatečné propojení voiceoveru s akcemi

- Ze **97** scene JSON metadata má **95 nulový počet `narration_action_cues`**; časově navázané akce jsou dokumentované jen ve dvou scénách (`06_00`, `08_00`).
- Samostatné `cues` v JSON popisují časové úseky komentáře pro titulky, nikoliv odpovídající vizuální události.
- Rozdělení vět v individuálních titulcích někdy přechází do následujícího cue uprostřed věty (např. `04_01`).

**Požadované:** Pro každou praktickou scénu definovat časové značky `voice_cue → on_screen_action → camera_focus → expected_visible_state → proof`. Přepracovat výklad do přirozených souvislých odstavců. **Zachovat Microsoft Vlasta (`cs-CZ-VlastaNeural`)**; problém řešit textem, prozodií, SSML/členěním, přechody a střihem, ne změnou hlasové identity.

### P1-V03 — Titulky nejsou prokazatelně doručené jako funkční finální produkt

- Archiv obsahuje **97 souborů SRT a 97 VTT** pro individuální voice segmenty, ale **neobsahuje společné** `video_course/output/subtitles_cs.srt` ani `subtitles_cs.vtt`.
- `validation.json` deklaruje finální MP4 o délce **5 831,61 s**, s embedded `mov_text` subtitle stopou, ale **finální MP4 v tomto archivu není**, takže deklaraci nemohu nezávisle ověřit. Přítomnost subtitle streamu v `ffprobe` sama nezaručuje, že jej daný přehrávač skutečně zobrazí.

**Požadované:** Dodat finální MP4 a globální SRT i VTT v kořeni distribučního balíku, plus ověřenou variantu s vypálenými titulky, pokud přepínatelné titulky nelze ve zvoleném přehrávači spolehlivě používat. Uvést konkrétní přehrávač a skutečný test zobrazení titulků na začátku, ve středu a na konci kurzu. Kontrolovat časové offsety mezi scénami, UTF-8 a českou diakritiku.

### P1-V04 — Produkční zdroje nestačí pro nezávislé přepracování

- ZIP má mimo obrázky a média zejména JSON, ASS a concat/metadata soubory. **Neobsahuje editorový projekt nebo produkční Python skripty**, ze kterých lze znovu zachytit a režijně sestavit scény.
- `validation.json` a jednotlivé scény deklarují technickou integritu a screen recording `real_gdigrab_visible_desktop_cropped_to_own_window`; to nepředstavuje pedagogické schválení. V metadatech **97/97 scén** je stav `visual_review: pending`, u voice není deklarována lidská poslechová kontrola.

**Požadované:** Přidat zdrojový režijní plán, editační timeline, capture scripts, kompoziční skripty, zdrojové grafiky, fontové reference, zmrazený commit Starter Kitu a reprodukovatelný build proces. Žádný technický green není souhlas s výukovou kvalitou.

### P2-V05 — Zatím slabá výuková vizuální hierarchie

- Kontrolní snímky pro kapitoly 3–12 ukazují převážně celý editor VS Code s malou částí kódu uprostřed a bez jasného vedení pozornosti. Existuje ASS s názvy kapitol, ale není prokázána konzistentní identita Academy, kontextová zvýraznění ani plynulé přibližování důležitých řádků.

**Požadované:** Jednotný motion design a grafická značka Playwright Academy, kurzor/focus highlight, zvýraznění relevantních částí, plynulý účelný zoom, živé přechody editor/browser/terminál/trace. Zvětšení kódu a ořez nesmějí odstranit kontext potřebný k porozumění.

## Požadovaný nový produkční postup

1. **Zamrazit funkční Starter Kit** (commit, hash, demo environment, test command, odpovídající verze manuálu).
2. Pro každou kapitolu vytvořit **learning outcome a reálný task**, nikoli pouze statický shot list.
3. Každý praktický krok rozdělit do navázaných výukových okamžiků: co lektor říká → co udělá → co má divák vidět → co z toho vyplývá.
4. Získat či natočit **nové reálné záznamy** zejména pro dlouhé statické editorové scény. Ponechat kvalitní současné záběry, které skutečně ukazují pohyb a výsledky.
5. Plynulé účelové přibližování a výukové značky. Neskrývat falešné záběry pohyblivou kamerou nad statikou.
6. **Komentář: Microsoft Vlasta v Edge, zůstává schváleným hlasem.** Přepsat sekavý obsah, používat plynulé odstavce a významové pauzy, znovu renderovat potřebné segmenty; neměnit hlas z důvodu stylu.
7. Titulky v SRT/VTT **pro celé video** plus funkční MP4 varianta v testovaném přehrávači; zkontrolovat formát, časování a diakritiku.
8. Nejprve vyrobit **jednu kompletní referenční kapitolu 5–8 min** (doporučeno „První vlastní test“) obsahující práci v editoru, skutečný běh testu, prohlížeč, dynamický zoom, správné značky, hlas Vlasta a titulky.
9. Provést **autentické vizuální a poslechové review** referenční kapitoly. Bez jejího schválení nevyrábět znovu celý 97min film.
10. Po schválení vyrobit celý kurz a provést kontrolu skutečné akce, naučitelnosti, titulkové stopy, srozumitelnosti, a konečného MP4.

## Závazná nová AC (předat Codexu)

- **AC-VID2-01**: Schválený hlas **Microsoft Vlasta z Edge** (`cs-CZ-VlastaNeural`) zůstane zachován ve všech kapitolách; žádný Microsoft Jakub.
- **AC-VID2-02**: Referenční kapitola skutečně ukáže psaní/úpravu kódu, spuštění testu, změnu prohlížeče a očekávaný výsledek.
- **AC-VID2-03**: V praktických úsecích existují časově ověřené důkazy odpovídajících akcí. Dlouhé statické úseky jsou odstraněny nebo obsahově odůvodněné; není to měřeno pouze přítomností video streamu.
- **AC-VID2-04**: `narration_action_cues` (nebo rovnocenný kontrakt) jsou vyplněny pro všechny relevantní praktické scény a ověřeny proti obrazu.
- **AC-VID2-05**: Zoom, zvýraznění a přechody jsou skutečně viditelné, přesně zaměřené na vysvětlované prvky a pomáhají výuce.
- **AC-VID2-06**: Komentář je souvislá srozumitelná čeština, s navazujícími myšlenkami a bez rušivých skoků mezi hlasovými segmenty.
- **AC-VID2-07**: Finální MP4 má funkční české titulky, doložené jejich zobrazením ve skutečném cílovém přehrávači. Součástí distribuce jsou také globální SRT a VTT.
- **AC-VID2-08**: Věcně pravdivý skutečný screencast Codegen, Inspector, Trace Viewer, nejméně jeden RED→GREEN průchod a otevření reportu.
- **AC-VID2-09**: Všechny ukázky lze zopakovat nad přesně dodanou verzí Starter Kitu. Video neučí neexistující operace.
- **AC-VID2-10**: Skutečný reprodukovatelný editační projekt včetně timeline a skriptů, nejen jednotlivé MP4.
- **AC-VID2-11**: Kvalitativní review zahrne zhlédnutí a poslech, nikoli pouze ffprobe či checksum.
- **AC-VID2-12**: Finální distribuce obsahuje kompletní MP4, titulky, kapitoly, zdrojové podklady a stručný návod přehrání.

## Stav a doporučení

- **Doloženo v archivu:** existující dílčí screencasty, hlas Vlasta, časová osa 12 kapitol, segmentové titulky, metadata technické validace.
- **Doložené problémy:** velký podíl prakticky neměnných snímků, chybějící akční mapování, nemožnost nezávisle ověřit finální subtitle playback, chybějící kompletní produkční zdroj.
- **Nekontrolováno:** celé složené MP4 a uživatelská zkušenost v cílovém přehrávači, protože MP4 není v balíku; subjektivní kvalita českého hlasu vychází z uživatelské zpětné vazby, nikoli z nezávislého poslechového testu.
- **Verdikt:** `CHANGES_REQUIRED`. Dodané podklady mají cenu jako základ pro nápravu, ale současný videokurz není produktově akceptovaný.

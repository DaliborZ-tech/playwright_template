# Akceptace referenční kapitoly R2

Tento dokument sleduje jednu referenční kapitolu, nikoli schválení celého kurzu. Původní produkt má verdikt **CHANGES_REQUIRED**. Hotová reference může být **READY_FOR_HUMAN_REVIEW**, nikdy automaticky produktově schválená podle ffprobe, pixelové metriky či checksumu.

| AC | Důkaz v referenci | Omezení / schvalovací krok |
| --- | --- | --- |
| VID2-01 | Sedm souvislých odstavců, metadata cs-CZ-VlastaNeural, audio SHA | Identita zachována; přirozenost a výslovnost posoudí vlastník poslechem |
| VID2-02 | Prázdný editor → skutečné psaní → DOM → běhy → report | Vlastník posoudí, zda podle ukázky dokáže postup zopakovat |
| VID2-03 | Původní klipy, intervaly akcí, rozbor změn před kamerou a titulky | Delší výklad nad konkrétním kódem/DOM vyžaduje obsahové posouzení; zoom není náhrada činnosti |
| VID2-04 | Všech 27 shotů: voice_cue, akce, focus, očekávaný stav a skutečný proof | Zdrojové hashe a snímky jsou v capture.json a edit_project.json |
| VID2-05 | Účelný zoom, rodina grafických značek, nativní výběr řádku a DOM | Obrazové review musí potvrdit čitelnost a zachovaný kontext |
| VID2-06 | Originální souvislé PCM bez vnitřních tichých vsuvek, kanonický přepis | Úplný lidský poslech PENDING |
| VID2-07 | Obě MP4, globální UTF-8 SRT/VTT, skutečný Edge test začátek/střed/konec | Konkrétní verze a viditelné ON/OFF snímky v evidence/player; přiložena vypálená varianta |
| VID2-08 | Tentýž skutečný nodeid: RED exit1 → jediná oprava → GREEN exit0; čerstvý report | Codegen, Inspector a Trace Viewer jsou povinné až v dalších odpovídajících kapitolách; celý AC zatím není splněn |
| VID2-09 | Git bundle, přesný commit, 78 hashů; výsledný kód shodný se Starter Kitem | Nezávislá reprodukce je doložená samostatným validation souborem |
| VID2-10 | Reálná timeline, raw klipy, audio, skripty capture/render, grafika, fontové reference | Offline render nepotřebuje TTS; nové natáčení vyžaduje popsaný Windows desktop |
| VID2-11 | Oddělený nezávislý AI review se skutečným rozsahem a nálezy | Není vydáván za lidský poslech; úplné zhlédnutí a poslech vlastníkem PENDING |
| VID2-12 | Jeden úplný ZIP: obě MP4, globální titulky, kapitoly, přepis, player i sources | Jde o distribuci reference; nový kompletní kurz dosud nevznikl |

## Závazná brána vlastníka

Před další výrobou vlastník zhlédne a poslechne **celou tuto kapitolu**. Hodnotí návaznost vysvětlení a akce, naučitelnost, čitelnost kódu a DOM, tempo, výslovnost, plynulost hlasu a titulky. Připomínky se vážou na čas videa. Souhlas se musí vztahovat ke konkrétnímu SHA-256 MP4 z MANIFEST.json. Při změně schváleného filmu je třeba ověřit rozsah změny znovu.

Do výslovného schválení zůstává `po_approval=PENDING` a `full_course_build_authorized=false`. Ani schválená reference sama o sobě neuzavírá akceptaci celého produktu.

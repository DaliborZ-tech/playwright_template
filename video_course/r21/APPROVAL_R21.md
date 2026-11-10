# Schválení celé referenční kapitoly R2.1

**10. 11. 2026, Europe/Prague — APPROVED_REFERENCE.**

Vlastník na žádost o schválení celé referenční kapitoly odpověděl
**„schvaluji“**. Tím přijímá vizuální a zvukový standard R2.1 a otevírá
navazující výrobu zbývajících kapitol podle mandátu R2.1.

Rozhodnutí je zaznamenané v `po_approval.json` a vztahuje se na přesné filmy:

| Soubor | SHA-256 |
| --- | --- |
| Playwright_Academy_R21_Prvni_Test.mp4 | 6c53aeb9e0b0bc7828e115c2868399b6f2a54411835c92a8ab0893a882d42b20 |
| Playwright_Academy_R21_Prvni_Test_Titulky.mp4 | c3ca84bdde17c1b5a9e038c8eb88b61c158fec027554d4b00c0aabcca7ea50f4 |

Přijatý hlas zůstává **cs-CZ-VlastaNeural**. Starter Kit zůstává zmrazený
na commitu `129d317771d91da04e31e8150a2111188f9ae51f`.

Nový záznam schvaluje celou referenci; dřívější samostatný souhlas s 30s
zvukovou ukázkou je zachovaný jako původní doklad. Starší PENDING v timeline,
měřeních a nezávislé AI revizi popisuje stav při jejich provedení. Aktuální
rozhodnutí určuje tento doklad a po_approval.json.

MP4, audio, titulky ani testovaný render se kvůli schválení nemění. Balení
před převzetím schválení skutečně ověří hashe obou filmů, hlas i commit;
při změně filmů schválení odmítne. Po novém offline buildu použijte
`python video_course/r21/approval.py`, případně rovnou `package.py`.

Schválení standardu otevírá další výrobu. Akceptace zbývajících kapitol
a nového celého kurzu proběhne až po jejich dokončení a ověření požadavků
R2/R2.1. Původní 97minutový produkt si ponechává verdikt CHANGES_REQUIRED.

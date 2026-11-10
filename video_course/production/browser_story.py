"""Skutečné kroky formuláře načasované na nativní word boundaries komentáře."""

import html

from playwright.sync_api import expect

BASE = "http://127.0.0.1:5000"


def word_time(scene, speech, phrase):
    position = scene["paragraph"].index(phrase)
    position += sum(
        len(r["spoken"]) - (r["end"] - r["start"])
        for r in speech["replacements"]
        if r["end"] <= position
    )
    cursor = 0
    for boundary in speech["word_boundaries"]:
        token = html.unescape(boundary["text"])
        left = speech["spoken_text"].casefold().find(token.casefold(), cursor)
        if left < 0:
            raise ValueError("Nelze najít nativní word boundary pro UI akci.")
        cursor = left + len(token)
        if cursor > position:
            return boundary["offset"] / 10_000_000
    raise ValueError(f"Chybí řečové časování: {phrase}")


def prepare_story(studio, scene, speech):
    page = studio.page
    row = page.get_by_role("row").filter(has_text="Kontrola fakturace")

    def open_form():
        page.get_by_role("button", name="Nový záznam").click()

    def fill_title():
        page.get_by_label("Název požadavku").fill("Kontrola fakturace")

    def assignee():
        page.get_by_label("Řešitel", exact=True).select_option(label="Petr")

    def priority():
        page.get_by_label("Prioritní").check()

    def save():
        page.get_by_role("button", name="Uložit záznam").click()
        expect(row).to_contain_text("Petr")
        expect(row).to_contain_text("Vysoká")
        expect(page.get_by_test_id("record-row")).to_have_count(4)

    def create():
        open_form()
        fill_title()
        assignee()
        priority()
        save()
        expect(row).to_contain_text("Nový")

    def edit():
        row.get_by_role("button", name="Upravit Kontrola fakturace", exact=True).click()

    def update():
        page.get_by_label("Stav", exact=True).select_option(label="Hotový")
        page.get_by_role("button", name="Uložit záznam").click()
        expect(row).to_contain_text("Hotový")

    def delete():
        page.once("dialog", lambda dialog: dialog.accept())
        row.get_by_role("button", name="Smazat Kontrola fakturace", exact=True).click()
        expect(row).to_have_count(0)

    def logout():
        page.get_by_role("button", name="Odhlásit se", exact=True).click()
        page.goto(BASE + "/dashboard")
        expect(page).to_have_url(BASE + "/login")
        expect(page.get_by_role("heading", name="Přihlášení", exact=True)).to_be_visible()

    if scene["id"] == "06_00":
        studio.login()
        page.goto(BASE + "/records")
        steps = [
            ("Otevřeme nový požadavek", open_form),
            ("vyplníme název", fill_title),
            ("vybereme řešitele", assignee),
            ("nastavíme prioritu", priority),
            ("Potom formulář uložíme", save),
        ]
    elif scene["id"] == "08_00":
        studio.context.clear_cookies()
        page.goto(BASE + "/login")
        steps = [
            ("Začínáme přihlášením", studio.login),
            ("Vytvoříme nový syntetický požadavek", create),
            ("Potom otevřeme právě jeho úpravu", edit),
            ("Změníme stav na Hotový", update),
            ("Nakonec požadavek smažeme", delete),
            ("Potom se odhlásíme", logout),
        ]
    else:
        raise ValueError("Neznámá synchronizovaná browser scéna.")
    cues = [(word_time(scene, speech, phrase), callback) for phrase, callback in steps]
    scene["narration_action_cues"] = [
        {"phrase": phrase, "time": stamp}
        for (phrase, _), (stamp, _) in zip(steps, cues, strict=True)
    ]
    return studio.browser_window, cues

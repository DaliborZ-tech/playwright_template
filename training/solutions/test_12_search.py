from playwright.sync_api import Page, expect


def test_search_without_matches(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_label("Vyhledat záznam").fill("neexistujici-synteticky-pozadavek")
    expect(page.get_by_test_id("record-row")).to_have_count(0)
    expect(page.get_by_text("Žádné odpovídající záznamy.", exact=True)).to_be_visible()

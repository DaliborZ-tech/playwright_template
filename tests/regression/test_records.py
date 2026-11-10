import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.regression


def test_05_create_record(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_role("button", name="Nový záznam").click()
    page.get_by_label("Název požadavku").fill("Kontrola fakturace")
    page.get_by_label("Řešitel", exact=True).select_option(label="Petr")
    page.get_by_label("Prioritní").check()
    page.get_by_role("button", name="Uložit záznam").click()
    row = page.get_by_role("row").filter(has_text="Kontrola fakturace")
    expect(row).to_contain_text("Petr")
    expect(row).to_contain_text("Vysoká")
    expect(page.get_by_test_id("record-row")).to_have_count(4)


def test_06_update_record(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_role("button", name="Upravit Kontrola přihlášení", exact=True).click()
    page.get_by_label("Název požadavku").fill("Kontrola přihlášení po opravě")
    page.get_by_label("Stav", exact=True).select_option(label="Hotový")
    page.get_by_role("button", name="Uložit záznam").click()
    page.reload()  # Uložení musí přežít načtení ze serveru.
    row = page.get_by_role("row").filter(has_text="Kontrola přihlášení po opravě")
    expect(row).to_contain_text("Hotový")


def test_07_delete_record(logged_in_page: Page) -> None:
    page = logged_in_page
    # Posluchač musí být připraven před akcí, která otevře nativní dialog.
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Smazat Kontrola přihlášení", exact=True).click()
    expect(page.get_by_role("row").filter(has_text="Kontrola přihlášení")).to_have_count(0)
    expect(page.get_by_test_id("record-row")).to_have_count(2)


def test_08_search_records(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_label("Vyhledat záznam").fill("Export")
    expect(page.get_by_test_id("record-row")).to_have_count(1)
    expect(page.get_by_test_id("record-row")).to_contain_text("Export měsíčního reportu")


def test_09_filter_records(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_label("Filtrovat podle stavu").select_option(label="Hotový")
    expect(page.get_by_test_id("record-row")).to_have_count(1)
    expect(page.get_by_test_id("record-row")).to_contain_text("Oprava vyhledávání")


def test_10_async_loading(logged_in_page: Page) -> None:
    page = logged_in_page
    with page.expect_response(lambda response: "/api/records?" in response.url) as response_info:
        page.get_by_role("button", name="Načíst znovu", exact=True).click()
    assert response_info.value.ok
    expect(page.get_by_text("Načítám záznamy…", exact=True)).to_be_hidden()
    expect(page.get_by_test_id("record-row")).to_have_count(3)


def test_11_api_error_and_recovery(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_text("Výukové nástroje", exact=True).click()
    with page.expect_response(lambda response: "simulate_error=1" in response.url) as response_info:
        page.get_by_role("button", name="Simulovat chybu API").click()
    assert response_info.value.status == 503
    expect(page.get_by_role("alert")).to_have_text(
        "Výuková chyba API (503). Zkuste načíst data znovu."
    )
    page.get_by_role("button", name="Načíst znovu", exact=True).click()
    expect(page.get_by_test_id("record-row")).to_have_count(3)
    expect(page.get_by_role("alert")).to_be_hidden()


def test_12_complete_regression_journey(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_role("link", name="Záznamy").click()
    page.get_by_role("button", name="Nový záznam").click()
    page.get_by_label("Název požadavku").fill("Regresní požadavek")
    page.get_by_role("button", name="Uložit záznam").click()
    row = page.get_by_role("row").filter(has_text="Regresní požadavek")
    expect(row).to_contain_text("Nový")
    row.get_by_role("button", name="Upravit Regresní požadavek", exact=True).click()
    page.get_by_label("Stav", exact=True).select_option(label="Hotový")
    page.get_by_role("button", name="Uložit záznam").click()
    expect(row).to_contain_text("Hotový")
    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name="Smazat Regresní požadavek", exact=True).click()
    expect(row).to_have_count(0)
    page.get_by_role("button", name="Odhlásit se", exact=True).click()
    expect(page).to_have_url(re.compile(r"/login$"))
    page.goto("/records")
    expect(page.get_by_role("heading", name="Přihlášení", exact=True)).to_be_visible()

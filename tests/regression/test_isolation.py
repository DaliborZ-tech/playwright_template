import pytest
from playwright.sync_api import Page, expect

from test_data.users import DEMO_EMAIL, DEMO_PASSWORD

pytestmark = pytest.mark.regression


def test_reset_is_private_to_current_session(logged_in_page: Page, new_context) -> None:
    page = logged_in_page
    other = new_context().new_page()
    other.goto("/login")
    other.get_by_label("E-mail", exact=True).fill(DEMO_EMAIL)
    other.get_by_label("Heslo", exact=True).fill(DEMO_PASSWORD)
    other.get_by_role("button", name="Přihlásit se").click()
    expect(other.get_by_test_id("record-row")).to_have_count(3)
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Smazat Kontrola přihlášení", exact=True).click()
    expect(page.get_by_test_id("record-row")).to_have_count(2)
    other.get_by_role("button", name="Obnovit výchozí data").click()
    page.reload()
    expect(page.get_by_test_id("record-row")).to_have_count(2)
    page.get_by_role("button", name="Obnovit výchozí data").click()
    expect(page.get_by_test_id("record-row")).to_have_count(3)


def test_cancel_delete_preserves_record(logged_in_page: Page) -> None:
    page = logged_in_page
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Smazat Kontrola přihlášení", exact=True).click()
    expect(page.get_by_test_id("record-row")).to_have_count(3)
    page.reload()
    expect(page.get_by_role("row").filter(has_text="Kontrola přihlášení")).to_have_count(1)

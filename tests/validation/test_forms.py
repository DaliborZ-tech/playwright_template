import pytest
from playwright.sync_api import Page, expect

from test_data.users import DEMO_EMAIL

pytestmark = [pytest.mark.validation, pytest.mark.regression]


@pytest.mark.parametrize("password", ["spatne-heslo", "Academy123"])
def test_03_invalid_login(page: Page, password: str) -> None:
    page.goto("/login")
    page.get_by_label("E-mail", exact=True).fill(DEMO_EMAIL)
    page.get_by_label("Heslo", exact=True).fill(password)
    page.get_by_role("button", name="Přihlásit se").click()
    expect(page.get_by_role("alert")).to_have_text("Nesprávný e-mail nebo heslo.")


def test_04_required_login_fields(page: Page) -> None:
    page.goto("/login")
    page.get_by_role("button", name="Přihlásit se").click()
    expect(page.get_by_role("alert")).to_have_text("Vyplňte e-mail i heslo.")


@pytest.mark.parametrize("title", ["", "ab", "   "])
def test_04_record_validation(logged_in_page: Page, title: str) -> None:
    page = logged_in_page
    page.get_by_role("button", name="Nový záznam").click()
    page.get_by_label("Název požadavku").fill(title)
    page.get_by_role("button", name="Uložit záznam").click()
    expect(page.get_by_role("dialog").get_by_role("alert")).to_have_text(
        "Název musí mít 3 až 80 znaků."
    )
    # Neplatný formulář nesmí vytvořit žádný záznam.
    page.get_by_role("button", name="Zrušit", exact=True).click()
    expect(page.get_by_test_id("record-row")).to_have_count(3)

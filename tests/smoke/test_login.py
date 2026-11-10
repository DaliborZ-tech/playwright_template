import re

import pytest
from playwright.sync_api import Page, expect

from test_data.users import DEMO_EMAIL, DEMO_PASSWORD

pytestmark = [pytest.mark.smoke, pytest.mark.regression]


def test_01_open_application(page: Page) -> None:
    page.goto("/login")
    expect(page).to_have_title(re.compile("Přihlášení"))
    expect(page.get_by_role("heading", name="Přihlášení", exact=True)).to_be_visible()


def test_02_successful_login(page: Page) -> None:
    page.goto("/login")
    page.get_by_label("E-mail", exact=True).fill(DEMO_EMAIL)
    page.get_by_label("Heslo", exact=True).fill(DEMO_PASSWORD)
    page.get_by_role("button", name="Přihlásit se").click()
    expect(page).to_have_url(re.compile(r"/dashboard$"))
    expect(page.get_by_role("heading", name="Dashboard", exact=True)).to_be_visible()

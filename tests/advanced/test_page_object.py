import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from test_data.users import DEMO_EMAIL, DEMO_PASSWORD


@pytest.mark.advanced
def test_login_with_page_object(page: Page) -> None:
    login = LoginPage(page)
    login.open()
    login.login(DEMO_EMAIL, DEMO_PASSWORD)
    expect(page.get_by_role("button", name="Odhlásit se", exact=True)).to_be_visible()

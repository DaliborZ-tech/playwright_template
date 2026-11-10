from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self) -> None:
        self.page.goto("/login")

    def login(self, email: str, password: str) -> None:
        self.page.get_by_label("E-mail", exact=True).fill(email)
        self.page.get_by_label("Heslo", exact=True).fill(password)
        self.page.get_by_role("button", name="Přihlásit se").click()
        expect(self.page.get_by_role("heading", name="Dashboard", exact=True)).to_be_visible()

"""Nový BrowserContext a nová serverová session před každým testem."""

from threading import Thread

import pytest
from playwright.sync_api import Page, expect
from werkzeug.serving import WSGIRequestHandler, make_server

from demo_app.app import create_app
from test_data.users import DEMO_EMAIL, DEMO_PASSWORD


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    if pytestconfig.getoption("base_url"):
        raise pytest.UsageError(
            "Demo si spouští vlastní izolovanou aplikaci. --base-url patří pouze "
            "k tests_external --external."
        )

    class QuietHandler(WSGIRequestHandler):
        def log(self, _type, _message, *args):
            pass

    server = make_server("127.0.0.1", 0, create_app(), threaded=True, request_handler=QuietHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join(timeout=3)
    server.server_close()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "locale": "cs-CZ", "viewport": {"width": 1440, "height": 900}}


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Přihlášení přes UI; nepřeskakujeme ověření skutečného formuláře."""
    page.goto("/login")
    page.get_by_label("E-mail", exact=True).fill(DEMO_EMAIL)
    page.get_by_label("Heslo", exact=True).fill(DEMO_PASSWORD)
    page.get_by_role("button", name="Přihlásit se").click()
    expect(page.get_by_role("heading", name="Dashboard", exact=True)).to_be_visible()
    expect(page.get_by_test_id("record-row")).to_have_count(3)
    return page

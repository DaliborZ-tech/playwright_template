"""Skutečné browser screenshoty aktuálního dema, nikoliv inscenovaný výstup."""

import sys
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from playwright.sync_api import expect, sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from demo_app.app import create_app  # noqa: E402
from test_data.users import DEMO_EMAIL, DEMO_PASSWORD  # noqa: E402


def main():
    output = ROOT / "evidence" / "screenshots"
    output.mkdir(parents=True, exist_ok=True)
    server = make_server("127.0.0.1", 0, create_app(), threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(
                base_url=f"http://127.0.0.1:{server.server_port}",
                viewport={"width": 1920, "height": 1080},
                locale="cs-CZ",
            )
            page = context.new_page()
            page.goto("/login")
            page.screenshot(path=str(output / "01-login.png"))
            page.get_by_label("E-mail", exact=True).fill(DEMO_EMAIL)
            page.get_by_label("Heslo", exact=True).fill(DEMO_PASSWORD)
            page.get_by_role("button", name="Přihlásit se").click()
            expect(page.get_by_test_id("record-row")).to_have_count(3)
            page.screenshot(path=str(output / "02-dashboard.png"))
            page.get_by_role("button", name="Nový záznam").click()
            page.get_by_label("Název požadavku").fill("Kontrola fakturace")
            page.get_by_label("Prioritní").check()
            page.screenshot(path=str(output / "03-record-form.png"))
            page.get_by_role("button", name="Uložit záznam").click()
            expect(page.get_by_test_id("record-row")).to_have_count(4)
            page.screenshot(path=str(output / "04-created.png"))
            browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


if __name__ == "__main__":
    main()

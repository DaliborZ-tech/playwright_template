"""Konfigurace vlastní aplikace; každý test dostane nový browser context."""

import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=False)


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    url = pytestconfig.getoption("base_url") or os.getenv("BASE_URL", "")
    try:
        parsed = urlsplit(url)
        valid = (
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            and parsed.username is None
            and parsed.password is None
            and (parsed.port is None or 1 <= parsed.port <= 65535)
        )
    except ValueError:
        valid = False
    if not valid:
        raise pytest.UsageError(
            "Nastavte BASE_URL v .env nebo použijte --base-url https://app.example.test. "
            "URL musí mít http/https a nesmí obsahovat přihlašovací údaje."
        )
    return url.rstrip("/")

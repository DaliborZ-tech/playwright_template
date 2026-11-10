import os
from urllib.parse import urlsplit

import pytest


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    if not pytestconfig.getoption("--external"):
        raise pytest.UsageError("Vyžadován výslovný přepínač --external.")
    url = pytestconfig.getoption("base_url") or os.getenv("EXTERNAL_BASE_URL", "")
    parsed = urlsplit(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise pytest.UsageError("Nastavte EXTERNAL_BASE_URL nebo --base-url bez hesla v URL.")
    return url.rstrip("/")

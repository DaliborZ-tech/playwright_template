"""Okrajové API vstupy: nesmí padat na 500 ani obejít přihlášení/CSRF."""

import pytest

from demo_app.app import create_app
from test_data.users import DEMO_EMAIL, DEMO_PASSWORD

pytestmark = [pytest.mark.validation, pytest.mark.regression]


def client_and_token(login=True):
    client = create_app().test_client()
    client.get("/login")
    with client.session_transaction() as session:
        token = session["csrf"]
    if login:
        response = client.post(
            "/login", data={"email": DEMO_EMAIL, "password": DEMO_PASSWORD, "csrf": token}
        )
        assert response.status_code == 302
    return client, token


def test_unicode_invalid_password_is_rejected_without_server_error():
    client, token = client_and_token(login=False)
    response = client.post(
        "/login", data={"email": DEMO_EMAIL, "password": "nesprávné-české-heslo", "csrf": token}
    )
    assert response.status_code == 200
    assert "Nesprávný e-mail nebo heslo." in response.get_data(as_text=True)


@pytest.mark.parametrize("token", ["", "český-neplatný-token"])
def test_csrf_is_enforced(token):
    client, _ = client_and_token()
    assert client.post("/api/reset", headers={"X-CSRF-Token": token}).status_code == 403


@pytest.mark.parametrize("overrides", [{"owner": []}, {"status": {}}, {"priority": "yes"}])
def test_malformed_record_is_validation_error(overrides):
    client, token = client_and_token()
    data = {"title": "Platný název", "owner": "Jana", "status": "Nový", "priority": False}
    data.update(overrides)
    response = client.post("/api/records", json=data, headers={"X-CSRF-Token": token})
    assert response.status_code == 400
    assert "error" in response.json


def test_api_requires_login():
    client, token = client_and_token(login=False)
    assert client.get("/api/records").status_code == 401
    assert client.post("/api/reset", headers={"X-CSRF-Token": token}).status_code == 401


def test_untrusted_host_is_rejected():
    client = create_app().test_client()
    assert client.get("/login", headers={"Host": "untrusted.example.test"}).status_code == 400


def test_logout_during_pending_read_returns_401(monkeypatch):
    from threading import Event, Thread

    import demo_app.app as module

    entered, release = Event(), Event()

    class ControlledDelay:
        def wait(self, _timeout):
            entered.set()
            assert release.wait(timeout=5)

    app = create_app()
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as session:
        token = session["csrf"]
    client.post("/login", data={"email": DEMO_EMAIL, "password": DEMO_PASSWORD, "csrf": token})
    other = app.test_client()
    other.set_cookie("session", client.get_cookie("session").value)
    monkeypatch.setattr(module, "Event", ControlledDelay)
    responses = []
    thread = Thread(target=lambda: responses.append(client.get("/api/records")))
    thread.start()
    try:
        assert entered.wait(timeout=5)
        assert other.post("/logout", data={"csrf": token}).status_code == 302
    finally:
        release.set()
        thread.join(timeout=5)
    assert responses[0].status_code == 401

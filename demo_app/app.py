"""Lokální demo: stav se drží v paměti, zvlášť pro každou podepsanou session."""

import argparse
import hashlib
import hmac
import secrets
from functools import wraps
from pathlib import Path
from threading import Event, RLock
from time import monotonic

from flask import Flask, abort, jsonify, redirect, render_template, request, session
from waitress import serve

from test_data.sample_records import seed_records
from test_data.users import DEMO_EMAIL, DEMO_PASSWORD


def source_fingerprint() -> str:
    root = Path(__file__).resolve().parent.parent
    files = [
        p
        for name in ("demo_app", "test_data")
        for p in (root / name).rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    ]
    digest = hashlib.sha256()
    for path in sorted(files):
        digest.update(str(path.relative_to(root)).replace("\\", "/").encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def create_app() -> Flask:
    app = Flask(__name__)
    build_id = source_fingerprint()
    app.config.update(
        SECRET_KEY=secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        MAX_CONTENT_LENGTH=16_384,
        TRUSTED_HOSTS=["127.0.0.1", "localhost", "[::1]"],
    )
    workspaces: dict[str, dict] = {}
    lock = RLock()

    @app.before_request
    def prepare_session():
        if request.path == "/health":
            return None
        with lock:
            now = monotonic()
            expired = [key for key, value in workspaces.items() if now - value["seen"] > 7_200]
            for key in expired:
                del workspaces[key]
            if session.get("workspace") not in workspaces:
                if len(workspaces) >= 200:
                    abort(503, "Příliš mnoho relací. Restartujte lokální demo.")
                session.clear()
                session["workspace"] = secrets.token_hex(16)
                session["csrf"] = secrets.token_hex(24)
                workspaces[session["workspace"]] = {"records": seed_records(), "seen": now}
            workspaces[session["workspace"]]["seen"] = now
        if request.method in {"POST", "PUT", "DELETE"}:
            token = request.headers.get("X-CSRF-Token", "") or request.form.get("csrf", "")
            if not hmac.compare_digest(token.encode("utf-8"), session["csrf"].encode("utf-8")):
                abort(403, "Neplatný ochranný token. Obnovte stránku.")
        return None

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; frame-ancestors 'none'; form-action 'self'"
        )
        return response

    def login_required(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if not session.get("logged_in"):
                if request.path.startswith("/api/"):
                    return jsonify(error="Nejprve se přihlaste."), 401
                return redirect("/login")
            return function(*args, **kwargs)

        return wrapped

    @app.get("/health")
    def health():
        return {"service": "playwright-academy", "version": "1.0.0", "build_id": build_id}

    @app.get("/")
    def home():
        return redirect("/dashboard" if session.get("logged_in") else "/login")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            if not email or not password:
                error = "Vyplňte e-mail i heslo."
            elif email == DEMO_EMAIL and hmac.compare_digest(
                password.encode("utf-8"), DEMO_PASSWORD.encode("utf-8")
            ):
                session["logged_in"] = True
                return redirect("/dashboard")
            else:
                error = "Nesprávný e-mail nebo heslo."
        return render_template("login.html", error=error)

    @app.post("/logout")
    def logout():
        with lock:
            workspaces.pop(session.get("workspace"), None)
        session.clear()
        return redirect("/login")

    @app.get("/dashboard")
    @login_required
    def dashboard():
        return render_template("portal.html", section="dashboard")

    @app.get("/records")
    @login_required
    def records_page():
        return render_template("portal.html", section="records")

    @app.route("/api/records", methods=["GET", "POST"])
    @login_required
    def records():
        if request.method == "GET":
            if request.args.get("simulate_error") == "1":
                return jsonify(error="Výuková chyba API (503). Zkuste načíst data znovu."), 503
            # Zpoždění je vlastnost demo API, nikoliv synchronizace testu.
            Event().wait(0.25)
            with lock:
                workspace = workspaces.get(session["workspace"])
                if workspace is None:
                    return jsonify(error="Relace skončila. Přihlaste se znovu."), 401
                data = [dict(row) for row in workspace["records"]]
            query = request.args.get("q", "").casefold()
            status = request.args.get("status", "")
            return jsonify(
                [
                    row
                    for row in data
                    if query in row["title"].casefold() and (not status or row["status"] == status)
                ]
            )
        data, error = validated_record()
        if error:
            return jsonify(error=error), 400
        with lock:
            workspace = workspaces.get(session["workspace"])
            if workspace is None:
                return jsonify(error="Relace skončila. Přihlaste se znovu."), 401
            rows = workspace["records"]
            if len(rows) >= 100:
                return jsonify(error="Limit je 100 záznamů. Obnovte výchozí data."), 400
            data["id"] = max((r["id"] for r in rows), default=0) + 1
            rows.append(data)
        return jsonify(data), 201

    def validated_record():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return None, "Očekáván JSON objekt."
        title = payload.get("title")
        if not isinstance(title, str) or not 3 <= len(title.strip()) <= 80:
            return None, "Název musí mít 3 až 80 znaků."
        if not isinstance(payload.get("owner"), str) or payload["owner"] not in {"Jana", "Petr"}:
            return None, "Vyberte platného řešitele."
        if not isinstance(payload.get("status"), str) or payload["status"] not in {
            "Nový",
            "Rozpracovaný",
            "Hotový",
        }:
            return None, "Vyberte platný stav."
        if not isinstance(payload.get("priority"), bool):
            return None, "Priorita musí být pravda nebo nepravda."
        return {
            key: (title.strip() if key == "title" else payload[key])
            for key in ("title", "owner", "status", "priority")
        }, None

    @app.route("/api/records/<int:record_id>", methods=["PUT", "DELETE"])
    @login_required
    def record(record_id):
        with lock:
            workspace = workspaces.get(session["workspace"])
            if workspace is None:
                return jsonify(error="Relace skončila. Přihlaste se znovu."), 401
            rows = workspace["records"]
            row = next((r for r in rows if r["id"] == record_id), None)
            if row is None:
                return jsonify(error="Záznam neexistuje."), 404
            if request.method == "DELETE":
                rows.remove(row)
                return "", 204
            data, error = validated_record()
            if error:
                return jsonify(error=error), 400
            row.update(data)
            return jsonify(row)

    @app.post("/api/reset")
    @login_required
    def reset():
        with lock:
            workspace = workspaces.get(session["workspace"])
            if workspace is None:
                return jsonify(error="Relace skončila. Přihlaste se znovu."), 401
            workspace["records"] = seed_records()
        return {"message": "Výchozí data obnovena."}

    return app


def main():
    parser = argparse.ArgumentParser(description="Lokální výukový QA portál")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    print(f"QA Training Portal: http://127.0.0.1:{args.port}", flush=True)
    serve(create_app(), host="127.0.0.1", port=args.port, threads=8)


if __name__ == "__main__":
    main()

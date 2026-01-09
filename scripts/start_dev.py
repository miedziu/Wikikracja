#!/usr/bin/env python3
"""Very small cross-platform dev helper (Windows/Linux)."""
import os
import secrets
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"
DB_DEFAULT = BASE_DIR / "db" / "db.sqlite3"


def copy_env():
    if ENV_FILE.exists():
        return
    if ENV_EXAMPLE.exists():
        ENV_FILE.write_text(ENV_EXAMPLE.read_text())
        print("Copied .env.example -> .env")
    else:
        print("Missing .env and .env.example. Please create .env first.")
        sys.exit(1)


def ensure_secret_key():
    lines = ENV_FILE.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("SECRET_KEY=") and line.strip().endswith("change-me"):
            new_key = "".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(50))
            lines[i] = f"SECRET_KEY={new_key}"
            ENV_FILE.write_text("\n".join(lines) + "\n")
            print("Updated SECRET_KEY in .env")
            break


def load_env():
    for raw in ENV_FILE.read_text().splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, val = raw.split("=", 1)
        os.environ.setdefault(key, val)


def db_path():
    try:
        sys.path.insert(0, str(BASE_DIR))
        from zzz.settings import DATABASES  # type: ignore

        return str(DATABASES["default"]["NAME"])
    except Exception:
        return str(DB_DEFAULT)


def run(cmd):
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=BASE_DIR, env=os.environ.copy())


def main():
    if sys.prefix == sys.base_prefix:
        print("Activate your virtualenv first.")
        sys.exit(1)

    copy_env()
    ensure_secret_key()
    load_env()

    print(f"- DB path: {db_path()}")
    print("- Virtualenv must stay activated while running\n")

    (BASE_DIR / "media" / "uploads").mkdir(parents=True, exist_ok=True)

    run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", "requirements.txt"])

    manage = [sys.executable, "manage.py"]
    apps = ["obywatele", "glosowania", "elibrary", "chat", "home", "bookkeeping", "board", "events", "tasks"]
    for app in apps:
        run(manage + ["makemigrations", app])

    run(manage + ["migrate"])
    run(manage + ["makemessages", "-v", "0", "--no-wrap", "--no-obsolete", "-l", "en", "--ignore=.git/*", "--ignore=static/*", "--ignore=.mypy_cache/*"])
    run(manage + ["makemessages", "-v", "0", "--no-wrap", "--no-obsolete", "-l", "pl", "--ignore=.git/*", "--ignore=static/*", "--ignore=.mypy_cache/*"])
    run(manage + ["compilemessages", "-v", "0", "--ignore=.git/*", "--ignore=static/*", "--ignore=.mypy_cache/*"])
    run(manage + ["collectstatic", "-v", "0", "--no-input", "-c"])

    print("\nDevelopment instance started\n")
    run(["daphne", "zzz.asgi:application"])


if __name__ == "__main__":
    main()

from __future__ import annotations

import os
from pathlib import Path

from app.cli import main as run


def _maybe_set_ssl_env() -> None:
    if os.getenv("SSL_CERTFILE") or os.getenv("SSL_KEYFILE"):
        return

    base_dir = Path(__file__).resolve().parent
    cert_path = base_dir / "cert.pem"
    key_path = base_dir / "key.pem"

    if cert_path.is_file() and key_path.is_file():
        os.environ["SSL_CERTFILE"] = str(cert_path)
        os.environ["SSL_KEYFILE"] = str(key_path)


if __name__ == "__main__":
    _maybe_set_ssl_env()
    run()

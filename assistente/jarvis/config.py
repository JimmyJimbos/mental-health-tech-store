"""Caricamento configurazione (config.yaml + .env) e percorsi."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
(DATA / "report").mkdir(exist_ok=True)


class Config(dict):
    """Dizionario con accesso a chiavi annidate: cfg.get_path("voce.attiva")."""

    def get_path(self, path, default=None):
        node = self
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node


def load_config() -> Config:
    load_dotenv(ROOT / ".env")
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        cfg = Config(yaml.safe_load(f) or {})
    cfg["secrets"] = {
        "anthropic": os.getenv("ANTHROPIC_API_KEY", "").strip(),
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        "telegram_user": os.getenv("TELEGRAM_ALLOWED_USER_ID", "").strip(),
    }
    return cfg

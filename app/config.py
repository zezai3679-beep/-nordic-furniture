from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()


_load_dotenv()


@dataclass(slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Nordic Furniture")
    feishu_app_id: str = os.getenv("FEISHU_APP_ID", "")
    feishu_app_secret: str = os.getenv("FEISHU_APP_SECRET", "")
    bitable_app_token: str = os.getenv("BITABLE_APP_TOKEN", "")
    leads_table_id: str = os.getenv("BITABLE_LEADS_TABLE_ID", "")

    @property
    def configured(self) -> bool:
        return all([self.feishu_app_id, self.feishu_app_secret,
                     self.bitable_app_token, self.leads_table_id])


settings = Settings()

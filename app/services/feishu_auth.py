from __future__ import annotations

import httpx

from app.config import settings

TENANT_TOKEN_URL = (
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
)


class FeishuAuthError(RuntimeError):
    pass


class FeishuAuthService:
    def __init__(self) -> None:
        self.app_id = settings.feishu_app_id
        self.app_secret = settings.feishu_app_secret

    async def fetch_tenant_access_token(self) -> str:
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                TENANT_TOKEN_URL,
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
        response.raise_for_status()
        data = response.json()
        if data.get("code") not in (None, 0):
            raise FeishuAuthError(data.get("msg", "Failed to fetch tenant access token."))
        token = data.get("tenant_access_token")
        if not token:
            raise FeishuAuthError("Feishu tenant access token is missing.")
        return token

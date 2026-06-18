from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

import httpx

from app.config import settings
from app.services.feishu_auth import FeishuAuthService


class CRMRepositoryError(RuntimeError):
    pass


class FeishuService:
    def __init__(self) -> None:
        self.auth_service = FeishuAuthService()
        self.base_url = "https://open.feishu.cn/open-apis/bitable/v1"

    async def submit_lead(self, payload: dict[str, str]) -> str:
        customer_id = f"cust_{uuid4().hex[:10]}"
        await self._create_record(settings.leads_table_id, {
            "姓名（若为公司采购请写公司名）": payload["customer_name"],
            "联系人": payload["contact_name"],
            "电话": payload.get("phone", ""),
            "来源": payload.get("source", ""),
            "备注": payload.get("notes", ""),
        })
        return customer_id

    async def _headers(self) -> dict[str, str]:
        token = await self.auth_service.fetch_tenant_access_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}

    async def _create_record(self, table_id: str, fields: dict[str, Any]) -> None:
        fields = {k: v for k, v in fields.items() if v != ""}
        headers = await self._headers()
        url = f"{self.base_url}/apps/{settings.bitable_app_token}/tables/{table_id}/records"
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, headers=headers, json={"fields": fields})
        except httpx.HTTPError as exc:
            raise CRMRepositoryError("连接飞书多维表格失败") from exc
        data = self._json(response)
        self._check_error(response, data)

    @staticmethod
    def _json(response: httpx.Response) -> dict[str, Any]:
        try:
            d = response.json()
        except ValueError:
            d = {}
        return d if isinstance(d, dict) else {}

    @staticmethod
    def _check_error(response: httpx.Response, data: dict[str, Any]) -> None:
        if not response.is_error and data.get("code") in (None, 0):
            return
        msg = data.get("msg") or "写入飞书失败"
        if data.get("code") == 91403:
            msg = "应用没有这张表权限，请在飞书授权"
        raise CRMRepositoryError(msg)


def build_repository() -> FeishuService:
    if not settings.configured:
        raise CRMRepositoryError("飞书配置不完整")
    return FeishuService()

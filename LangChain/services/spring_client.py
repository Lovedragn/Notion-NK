import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException

SPRING_BASE_URL = os.getenv("SPRING_BASE_URL", "http://localhost:8080")
SPRING_JWT = os.getenv("SPRING_JWT", None)
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))


def _auth_headers(token_override: Optional[str] = None) -> Dict[str, str]:
	headers: Dict[str, str] = {"Content-Type": "application/json"}
	token = token_override or SPRING_JWT
	if token:
		headers["Authorization"] = f"Bearer {token}"
	return headers


async def get_http_client() -> httpx.AsyncClient:
	return httpx.AsyncClient(base_url=SPRING_BASE_URL, timeout=REQUEST_TIMEOUT)


async def fetch_tasks(user_id: Optional[int] = None, status: Optional[str] = None, token: Optional[str] = None) -> List[Dict[str, Any]]:
	params: Dict[str, Any] = {}
	if user_id is not None:
		params["userId"] = user_id
	async with await get_http_client() as client:
		resp = await client.get("/tasks", params=params, headers=_auth_headers(token))
		if resp.status_code >= 400:
			raise HTTPException(status_code=resp.status_code, detail=resp.text)
		items = resp.json() if resp.text else []
		if status:
			try:
				return [t for t in items if str(t.get("status", "")).lower() == status.lower()]
			except Exception:
				return items
		return items


async def create_task(payload: Dict[str, Any], hash_value: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
	async with await get_http_client() as client:
		if hash_value:
			resp = await client.post(f"/tasks/hash/{hash_value}", json=payload, headers=_auth_headers(token))
		else:
			resp = await client.post("/tasks", json=payload, headers=_auth_headers(token))
		if resp.status_code >= 400:
			raise HTTPException(status_code=resp.status_code, detail=resp.text)
		return resp.json() if resp.text else {}


async def update_task(task_id: Any, payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
	async with await get_http_client() as client:
		resp = await client.put(f"/tasks/{task_id}", json=payload, headers=_auth_headers(token))
		if resp.status_code >= 400:
			raise HTTPException(status_code=resp.status_code, detail=resp.text)
		return resp.json() if resp.text else {}

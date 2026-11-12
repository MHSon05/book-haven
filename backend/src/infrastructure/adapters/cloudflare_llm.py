"""
Infrastructure Adapter: CloudflareLLMAdapter
Tích hợp trực tiếp dịch vụ suy luận trí tuệ nhân tạo Cloudflare Workers AI
(@cf/meta/llama-3.1-8b-instruct) cho Trợ lý ảo Chatbot Bookie (FR21).
"""
import os
from typing import Optional
import httpx


class CloudflareLLMAdapter:
    def __init__(
        self,
        account_id: Optional[str] = None,
        api_token: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.account_id = account_id or os.getenv("CF_ACCOUNT_ID", "")
        self.api_token = api_token or os.getenv("CF_API_TOKEN", "")
        self.model = model or os.getenv("CF_LLM_MODEL", "@cf/meta/llama-3.1-8b-instruct")

    def generate_chat_response(self, system_prompt: str, user_message: str) -> str:
        """Gọi trực tiếp Cloudflare Workers AI và trả về phản hồi thực từ mô hình LLM."""
        if (
            not self.account_id
            or not self.api_token
            or self.account_id.startswith("your_")
            or self.api_token.startswith("your_")
            or "demo" in self.account_id.lower()
        ):
            raise RuntimeError(
                "Thiếu cấu hình CF_ACCOUNT_ID hoặc CF_API_TOKEN hợp lệ để kết nối Cloudflare Workers AI."
            )

        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 512,
            "temperature": 0.7,
        }

        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, headers=headers, json=payload)

        if resp.status_code != 200:
            raise RuntimeError(
                f"Cloudflare Workers AI trả về lỗi HTTP {resp.status_code}: {resp.text}"
            )

        reply = resp.json().get("result", {}).get("response", "").strip()
        if not reply:
            raise RuntimeError("Cloudflare Workers AI trả về phản hồi rỗng.")
        return reply

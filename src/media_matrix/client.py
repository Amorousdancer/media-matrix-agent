import json
import os
from pathlib import Path
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class DeepSeekClient:
    def __init__(self) -> None:
        load_dotenv()

        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        if self.base_url.rstrip("/").endswith("/anthropic"):
            self.base_url = self.base_url.rstrip("/")[: -len("/anthropic")]
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
        self.temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "8192"))
        self.timeout = float(os.getenv("DEEPSEEK_TIMEOUT", "120"))

        self.client = OpenAI(
            api_key=self.api_key or "missing",
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def request_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set.")

        schema = json.dumps(response_model.model_json_schema(), ensure_ascii=False)
        enhanced_system_prompt = (
            f"{system_prompt}\n\n"
            "CRITICAL: You must respond ONLY with a valid JSON object matching "
            f"this JSON schema:\n{schema}\n"
            "Do not include markdown formatting, backticks, or extra text."
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("DeepSeek returned empty content.")

        return response_model.model_validate_json(content)

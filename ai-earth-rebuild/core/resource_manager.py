"""
Lightweight Resource Manager for AI Earth experiments.

Purpose: keep us focused and prevent silent resource drift.
This is intentionally small: enough for EXP13 Phase B, not a full framework.

Key ideas:
- Exploratory mode may rotate/fallback, but records every failure.
- Fixed mode does not fallback; a failure is a recorded experiment failure.
- Every call returns text + metadata: provider, model, latency, tokens, retries.
- Secrets are read from /tmp/ai_earth_keys.env or environment variables only.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Literal

import requests

Policy = Literal["exploratory", "fixed"]


@dataclass
class CallMeta:
    provider: str
    model: str
    policy: str
    latency_s: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    retries: int = 0
    failures: list[str] | None = None
    status: str = "ok"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_env_list(name: str, key_path: str = "/tmp/ai_earth_keys.env") -> list[str]:
    """Load comma-separated secrets from env or /tmp key file."""
    val = os.environ.get(name)
    if val:
        return [x.strip() for x in val.split(",") if x.strip()]
    p = Path(key_path)
    if not p.exists():
        return []
    txt = p.read_text(encoding="utf-8")
    m = re.search(rf"{re.escape(name)}=(.+)", txt)
    if not m:
        return []
    return [x.strip() for x in m.group(1).split(",") if x.strip()]


class OpenRouterResource:
    provider = "openrouter"

    def __init__(
        self,
        model: str,
        policy: Policy = "exploratory",
        key_path: str = "/tmp/ai_earth_keys.env",
        temperature: float = 0.7,
        max_tokens: int = 220,
        provider_constraints: dict[str, Any] | None = None,
    ):
        self.model = model
        self.policy = policy
        self.keys = load_env_list("OPENROUTER_KEYS", key_path)
        if not self.keys:
            raise RuntimeError("No OPENROUTER_KEYS found in env or /tmp/ai_earth_keys.env")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.provider_constraints = provider_constraints or None
        self.key_index = 0

    def chat(self, system: str, user: str) -> tuple[str, CallMeta]:
        start = time.time()
        failures: list[str] = []
        max_attempts = len(self.keys) if self.policy == "exploratory" else 1

        for off in range(max_attempts):
            key = self.keys[(self.key_index + off) % len(self.keys)]
            payload: dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            if self.provider_constraints:
                payload["provider"] = self.provider_constraints
            try:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json=payload,
                    timeout=90,
                )
            except Exception as e:
                failures.append(f"EXC:{type(e).__name__}")
                continue

            if r.status_code == 200:
                self.key_index = (self.key_index + off + 1) % len(self.keys)
                data = r.json()
                usage = data.get("usage", {}) or {}
                meta = CallMeta(
                    provider=self.provider,
                    model=self.model,
                    policy=self.policy,
                    latency_s=time.time() - start,
                    prompt_tokens=int(usage.get("prompt_tokens") or 0),
                    completion_tokens=int(usage.get("completion_tokens") or 0),
                    retries=off,
                    failures=failures,
                )
                return data["choices"][0]["message"].get("content") or "", meta

            failures.append(f"HTTP:{r.status_code}")
            # In fixed mode, stop immediately. In exploratory, rotate on likely key/quota/transient errors.
            if self.policy == "fixed" or r.status_code not in (401, 402, 429, 500, 502, 503):
                break
            time.sleep(0.2)

        meta = CallMeta(
            provider=self.provider,
            model=self.model,
            policy=self.policy,
            latency_s=time.time() - start,
            retries=max(0, len(failures) - 1),
            failures=failures,
            status="failed",
        )
        raise RuntimeError(f"OpenRouter call failed: {meta.to_dict()}")


class ResourceManager:
    """Tiny factory for resources. Currently implements OpenRouter for EXP13."""

    def __init__(self, registry_path: str = "ai-earth-rebuild/config/resources.example.json"):
        self.registry_path = registry_path
        self.registry: dict[str, Any] = {}
        p = Path(registry_path)
        if p.exists():
            self.registry = json.loads(p.read_text(encoding="utf-8"))

    def openrouter(
        self,
        model: str,
        policy: Policy = "exploratory",
        temperature: float = 0.7,
        max_tokens: int = 220,
        quantizations: list[str] | None = None,
    ) -> OpenRouterResource:
        constraints = {"quantizations": quantizations} if quantizations else None
        return OpenRouterResource(
            model=model,
            policy=policy,
            temperature=temperature,
            max_tokens=max_tokens,
            provider_constraints=constraints,
        )

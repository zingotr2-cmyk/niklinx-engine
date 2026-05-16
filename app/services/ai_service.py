"""
DRO AI Service — Unified interface for OpenAI, Claude, and mock AI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import httpx
from config import config


class AIService:
    """Unified AI service with automatic fallback."""

    def __init__(self):
        self._client = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=60.0)
        return self._client

    @property
    def active_service(self) -> str:
        return config.active_ai_service

    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> str:
        """
        Generate text using the best available AI service.
        Falls back: Claude → OpenAI → Mock
        """
        if system_prompt is None:
            system_prompt = "You are an expert e-commerce marketer and AI dropshipping strategist."

        if config.claude_key:
            result = self._call_claude(prompt, system_prompt, max_tokens)
            if result:
                return result

        if config.openai_key:
            result = self._call_openai(prompt, system_prompt, max_tokens)
            if result:
                return result

        # Heuristic fallback generates deterministic templates
        from app.services.mock_rewriter import generate_copy as heuristic_gen
        fallback = heuristic_gen("product", prompt, 0)
        return json.dumps(fallback)

    def _call_openai(self, prompt: str, system: str, max_tokens: int) -> str | None:
        try:
            resp = self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {config.openai_key}"},
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": max_tokens,
                },
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
        return None

    def _call_claude(self, prompt: str, system: str, max_tokens: int) -> str | None:
        try:
            resp = self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": config.claude_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-3-opus-20240229",
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if resp.status_code == 200:
                return resp.json()["content"][0]["text"]
        except Exception:
            pass
        return None


ai = AIService()

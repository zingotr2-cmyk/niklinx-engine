"""
DRO Configuration Module
Handles encrypted .env loading and secure API key management.
"""

import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureConfig:
    """Encrypted configuration handler with .env integration."""

    def __init__(self, env_path: str = ".env"):
        self.env_path = Path(env_path)
        self._fernet = None
        self._load_env()

    def _load_env(self):
        """Load environment variables from .env file."""
        if self.env_path.exists():
            load_dotenv(self.env_path)

    def _get_key(self) -> bytes:
        """Derive encryption key from machine fingerprint."""
        machine_id = self._get_machine_id()
        salt = b"DRO_SALT_2024_AGENTIC"
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        return base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))

    def _get_machine_id(self) -> str:
        """Get unique machine identifier for encryption binding."""
        import platform
        import uuid

        machine = platform.node()
        mac = uuid.getnode()
        return f"{machine}-{mac:x}-DRO-SYSTEM"

    @property
    def fernet(self) -> Fernet:
        if self._fernet is None:
            self._fernet = Fernet(self._get_key())
        return self._fernet

    def encrypt_value(self, value: str) -> str:
        """Encrypt a configuration value."""
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt_value(self, token: str) -> str:
        """Decrypt a configuration value."""
        return self.fernet.decrypt(token.encode()).decode()

    def get(self, key: str, default=None) -> str:
        """Get config value from environment."""
        return os.getenv(key, default)

    def set(self, key: str, value: str, encrypt: bool = False):
        """Set a config value and optionally save to .env."""
        stored = self.encrypt_value(value) if encrypt else value
        os.environ[key] = stored
        if self.env_path.exists():
            with open(self.env_path, "a") as f:
                f.write(f"\n{key}={stored}")

    # --- Specific accessors ---
    @property
    def openai_key(self) -> str:
        return self.get("OPENAI_API_KEY", "")

    @property
    def claude_key(self) -> str:
        return self.get("CLAUDE_API_KEY", "")

    @property
    def license_key(self) -> str:
        return self.get("DRO_LICENSE_KEY", "")

    @property
    def stripe_key(self) -> str:
        return self.get("STRIPE_SECRET_KEY", "")

    @property
    def debug(self) -> bool:
        return self.get("DEBUG", "false").lower() == "true"

    @property
    def host(self) -> str:
        return self.get("HOST", "0.0.0.0")

    @property
    def port(self) -> int:
        return int(self.get("PORT", "8000"))

    @property
    def ai_mode(self) -> str:
        return self.get("AI_MODE", "auto")

    @property
    def active_ai_service(self) -> str:
        mode = self.ai_mode
        if mode == "production":
            return "production"
        if self.claude_key:
            return "claude"
        if self.openai_key:
            return "openai"
        return "mock"


# Global singleton
config = SecureConfig()

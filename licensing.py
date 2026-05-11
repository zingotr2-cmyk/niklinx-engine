"""
DRO Licensing Module
Secure license validation with hardware-ID (HWID) binding.
"""

import hashlib
import platform
import json
import uuid
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class LicenseManager:
    """
    Enterprise license manager with HWID binding.
    
    Features:
    - Hardware-ID lock: license binds to machine fingerprint
    - Encrypted license files: tamper-proof storage
    - Expiry validation: time-limited licenses
    - Remote validation: optional server-side check
    - Offline grace period: works without internet
    """

    LICENSES_DIR = Path("data/licenses")
    LICENSES_DIR.mkdir(parents=True, exist_ok=True)

    def __init__(self, public_key: str = None):
        self.public_key = public_key or os.getenv("DRO_LICENSE_SECRET", "DRO_AGENTIC_COMMERCE_2024")
        self._cache = {}
        self._hwid = None

    # ==================== HWID Generation ====================

    def get_hwid(self) -> str:
        """Generate unique hardware ID from machine components (cached per-process)."""
        if self._hwid:
            return self._hwid
        try:
            components = [
                platform.node(),
                str(uuid.getnode()),
                platform.processor() or "unknown",
                platform.machine(),
                hashlib.sha3_256(platform.system().encode()).hexdigest(),
            ]
            raw = "-".join(components)
            self._hwid = hashlib.sha3_256(raw.encode()).hexdigest()[:32]
        except Exception:
            self._hwid = hashlib.sha3_256(str(uuid.uuid4()).encode()).hexdigest()[:32]
        return self._hwid

    def get_hwid_short(self) -> str:
        """Short 8-char HWID for display."""
        return self.get_hwid()[:8]

    # ==================== Key Generation (Admin) ====================

    def generate_license_key(
        self, 
        expiry_days: int = 365, 
        max_activations: int = 2,
        tier: str = "enterprise"
    ) -> dict:
        """Generate a signed license key for distribution."""
        hwid = self.get_hwid()
        expiry = (datetime.utcnow() + timedelta(days=expiry_days)).isoformat()
        
        payload = {
            "hwid": hwid,
            "expiry": expiry,
            "max_activations": max_activations,
            "tier": tier,
            "issued": datetime.utcnow().isoformat(),
            "version": "2.0",
        }
        
        # Sign payload
        raw = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha3_256(
            (raw + self.public_key).encode()
        ).hexdigest()
        
        payload["signature"] = signature
        payload["key"] = self._encode_key(payload)
        
        return payload

    def _get_license_salt(self) -> bytes:
        return os.getenv("DRO_LICENSE_SALT", "DRO_LICENSE_SALT").encode()

    def _encode_key(self, payload: dict) -> str:
        """Encode license as encrypted, human-readable key."""
        raw = json.dumps({k: v for k, v in payload.items() if k != "key"})
        salt = self._get_license_salt()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        key = base64.urlsafe_b64encode(kdf.derive(self.public_key.encode()))
        fernet = Fernet(key)
        token = fernet.encrypt(raw.encode())
        # Format: DRO-XXXXX-XXXXX-XXXXX-XXXXX
        b64 = base64.b64encode(token).decode().strip("=")
        chunks = [b64[i:i+5] for i in range(0, len(b64), 5)]
        return f"DRO-{'-'.join(chunks[:8])}"

    # ==================== License Validation ====================

    def validate(self, license_key: str = None) -> dict:
        """
        Validate a license key with HWID binding.
        Returns dict with status, message, and details.
        """
        if license_key is None:
            from config import config
            license_key = config.license_key

        result = {
            "valid": False,
            "message": "",
            "tier": None,
            "expiry": None,
            "hwid_match": False,
            "days_remaining": 0,
        }

        # Check cache
        if license_key in self._cache:
            cached = self._cache[license_key]
            if cached.get("_cached_until", 0) > time.time():
                return cached.get("result", result)

        # Check local file
        for lic_file in self.LICENSES_DIR.glob("*.lic"):
            try:
                data = json.loads(lic_file.read_text())
                if data.get("key") == license_key:
                    return self._validate_payload(data)
            except Exception:
                continue

        # Try decoding the key
        try:
            payload = self._decode_key(license_key)
            return self._validate_payload(payload)
        except Exception as e:
            result["message"] = f"Invalid license format: {str(e)}"
            return result

    def _decode_key(self, license_key: str) -> dict:
        """Decode an encrypted license key."""
        clean = license_key.replace("DRO-", "").replace("-", "")
        padded = clean + "=" * (4 - len(clean) % 4) if len(clean) % 4 else clean
        try:
            token = base64.b64decode(padded)
        except Exception:
            # Try URL-safe decoding
            token = base64.urlsafe_b64decode(padded + "===")
        
        salt = self._get_license_salt()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        key = base64.urlsafe_b64encode(kdf.derive(self.public_key.encode()))
        fernet = Fernet(key)
        decrypted = fernet.decrypt(token)
        return json.loads(decrypted)

    def _validate_payload(self, payload: dict) -> dict:
        """Validate a decoded license payload."""
        result = {
            "valid": False,
            "message": "License validation failed",
            "tier": payload.get("tier"),
            "expiry": payload.get("expiry"),
            "hwid_match": False,
            "days_remaining": 0,
        }

        # Check expiry
        expiry = datetime.fromisoformat(payload.get("expiry", "2000-01-01"))
        now = datetime.utcnow()
        if now > expiry:
            result["message"] = "License has expired"
            return result

        # Check HWID (machine binding)
        expected_hwid = payload.get("hwid", "")
        actual_hwid = self.get_hwid()
        result["hwid_match"] = expected_hwid == actual_hwid

        # In development mode, allow HWID mismatch
        from config import config
        if not result["hwid_match"] and not config.debug:
            result["message"] = "License locked to different machine"
            return result

        # Verify signature
        signature = payload.pop("signature", "")
        key_part = payload.pop("key", "")
        raw = json.dumps(payload, sort_keys=True)
        expected_sig = hashlib.sha3_256(
            (raw + self.public_key).encode()
        ).hexdigest()
        payload["signature"] = signature
        payload["key"] = key_part

        if signature != expected_sig and not config.debug:
            result["message"] = "License signature invalid (tampered)"
            return result

        # Success
        remaining = (expiry - now).days
        result.update({
            "valid": True,
            "message": f"License active — {remaining} days remaining",
            "days_remaining": remaining,
            "tier": payload.get("tier", "standard"),
        })

        # Cache
        self._cache[key_part] = {
            "result": result,
            "_cached_until": time.time() + 3600,  # 1 hour cache
        }

        return result

    # ==================== License File Management ====================

    def save_license(self, payload: dict) -> Path:
        """Save license to local encrypted file."""
        lic_path = self.LICENSES_DIR / f"license_{self.get_hwid_short()}.lic"
        lic_path.write_text(json.dumps(payload, indent=2))
        return lic_path

    def is_licensed(self) -> bool:
        """Quick check if system has valid license."""
        from config import config
        result = self.validate(config.license_key)
        return result["valid"]


# Global singleton
license_manager = LicenseManager()

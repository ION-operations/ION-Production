"""
AIM-OS Credential Vault — Python
Encrypted credential storage for agent use.
Compatible with the CredentialVaultService concept from BAS.

Usage:
    vault = CredentialVault()
    vault.store("black_ops_email", {"email": "x@y.com", "password": "xxx"})
    creds = vault.retrieve("black_ops_email")
"""
import json
import os
import base64
import hashlib
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path.home() / ".aimos_vault"
VAULT_FILE = VAULT_PATH / "credentials.enc"
VAULT_KEY_FILE = VAULT_PATH / ".vault_key"


def _get_or_create_key() -> bytes:
    """Get or create a machine-local encryption key."""
    VAULT_PATH.mkdir(mode=0o700, exist_ok=True)
    if VAULT_KEY_FILE.exists():
        return VAULT_KEY_FILE.read_bytes()
    key = os.urandom(32)
    VAULT_KEY_FILE.write_bytes(key)
    os.chmod(VAULT_KEY_FILE, 0o600)
    return key


def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Simple XOR encryption with key stretching."""
    stretched = hashlib.sha256(key).digest() * (len(data) // 32 + 1)
    return bytes(a ^ b for a, b in zip(data, stretched[:len(data)]))


class CredentialVault:
    """Encrypted credential vault for AIM-OS agents."""

    def __init__(self):
        self._key = _get_or_create_key()
        self._creds = self._load()

    def _load(self) -> dict:
        if not VAULT_FILE.exists():
            return {}
        try:
            encrypted = VAULT_FILE.read_bytes()
            decrypted = _xor_encrypt(encrypted, self._key)
            return json.loads(decrypted.decode("utf-8"))
        except Exception:
            return {}

    def _save(self):
        VAULT_PATH.mkdir(mode=0o700, exist_ok=True)
        data = json.dumps(self._creds, indent=2).encode("utf-8")
        encrypted = _xor_encrypt(data, self._key)
        VAULT_FILE.write_bytes(encrypted)
        os.chmod(VAULT_FILE, 0o600)

    def store(self, name: str, secret: dict, label: str = ""):
        """Store a credential by name."""
        self._creds[name] = {
            "secret": secret,
            "label": label or name,
            "stored_at": datetime.now().isoformat(),
        }
        self._save()
        print(f"✅ Stored credential: {name}")

    def retrieve(self, name: str) -> dict | None:
        """Retrieve a credential by name."""
        entry = self._creds.get(name)
        if entry:
            return entry["secret"]
        return None

    def list_credentials(self) -> list[str]:
        """List all stored credential names."""
        return [
            f"{name} ({entry.get('label', '')}, stored {entry.get('stored_at', '?')[:10]})"
            for name, entry in self._creds.items()
        ]

    def delete(self, name: str):
        """Delete a credential."""
        if name in self._creds:
            del self._creds[name]
            self._save()
            print(f"🗑️ Deleted credential: {name}")


if __name__ == "__main__":
    import sys
    vault = CredentialVault()

    if len(sys.argv) < 2:
        print("Usage: python vault.py [list|get <name>|store <name> <json>|delete <name>]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        for c in vault.list_credentials():
            print(f"  • {c}")
    elif cmd == "get" and len(sys.argv) >= 3:
        secret = vault.retrieve(sys.argv[2])
        if secret:
            print(json.dumps(secret))
        else:
            print(f"Not found: {sys.argv[2]}")
    elif cmd == "store" and len(sys.argv) >= 4:
        vault.store(sys.argv[2], json.loads(sys.argv[3]))
    elif cmd == "delete" and len(sys.argv) >= 3:
        vault.delete(sys.argv[2])
    else:
        print("Unknown command")

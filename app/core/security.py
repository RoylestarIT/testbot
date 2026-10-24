from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class EncryptionError(ValueError):
    """Raised when encryption or decryption fails."""


def _get_fernet() -> Fernet:
    key = get_settings().fernet_key.strip()
    if not key:
        raise EncryptionError("FERNET_KEY is not configured")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, TypeError) as exc:
        raise EncryptionError("FERNET_KEY is invalid") from exc


def encrypt_secret(plaintext: str) -> str:
    if not plaintext:
        raise EncryptionError("Cannot encrypt empty secret")
    token = _get_fernet().encrypt(plaintext.encode("utf-8"))
    return token.decode("ascii")


def decrypt_secret(ciphertext: str) -> str:
    if not ciphertext:
        raise EncryptionError("Cannot decrypt empty ciphertext")
    try:
        data = _get_fernet().decrypt(ciphertext.encode("ascii"))
    except InvalidToken as exc:
        raise EncryptionError("Failed to decrypt secret") from exc
    return data.decode("utf-8")

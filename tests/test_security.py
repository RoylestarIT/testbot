import pytest

from app.core.config import get_settings
from app.core.security import EncryptionError, decrypt_secret, encrypt_secret


@pytest.fixture
def fernet_key(monkeypatch: pytest.MonkeyPatch) -> str:
    from cryptography.fernet import Fernet

    key = Fernet.generate_key().decode("ascii")
    monkeypatch.setenv("FERNET_KEY", key)
    get_settings.cache_clear()
    yield key
    get_settings.cache_clear()


def test_encrypt_decrypt_roundtrip(fernet_key: str) -> None:
    plaintext = "wb-api-key-secret-12345"
    ciphertext = encrypt_secret(plaintext)
    assert ciphertext != plaintext
    assert decrypt_secret(ciphertext) == plaintext


def test_decrypt_invalid_token_raises(fernet_key: str) -> None:
    with pytest.raises(EncryptionError):
        decrypt_secret("not-a-valid-token")


def test_encrypt_without_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FERNET_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(EncryptionError):
        encrypt_secret("secret")
    get_settings.cache_clear()

from argon2 import PasswordHasher, exceptions


_ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash Argon2 d'un mot de passe en texte clair."""
    return _ph.hash(password)


def verify_password(hashed: str, password: str) -> bool:
    """Vérifie un mot de passe par rapport à un hash Argon2 stocké."""
    try:
        return _ph.verify(hashed, password)
    except (exceptions.VerifyMismatchError, exceptions.VerificationError, exceptions.InvalidHashError):
        return False

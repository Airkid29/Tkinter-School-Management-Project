"""
Logique d'accès aux données pour les utilisateurs (table `users`).
"""

import hashlib

from db import execute_query
from hash_password import hash_password, verify_password


def create_default_admin_if_not_exists():
    """
    Crée un administrateur par défaut si aucun utilisateur n'existe encore.
    username: admin, password: admin123 (à changer ensuite).
    """
    count = execute_query(
        "SELECT COUNT(*) AS cnt FROM users", fetchone=True, fetchall=False
    )
    if count and count["cnt"] == 0:
        execute_query(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
            """,
            params=("admin", hash_password("admin123"), "admin"),
            commit=True,
        )


def authenticate_user(username: str, password: str):
    """
    Vérifie les identifiants d'un utilisateur.
    Retourne un dict utilisateur ou None.
    """
    user = execute_query(
        "SELECT * FROM users WHERE username = %s",
        params=(username,),
        fetchone=True,
        fetchall=False,
    )
    if not user:
        return None

    if verify_password(user["password_hash"], password):
        return user

    # Rétrocompatibilité : anciens hashes SHA256 (avant migration Argon2)
    legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if user["password_hash"] == legacy_hash:
        # Migration vers Argon2
        execute_query(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            params=(hash_password(password), user["id"]),
            commit=True,
        )
        return user

    return None


"""
Logique d'accès aux données pour les utilisateurs (table `users`).
"""

import hashlib

from db import execute_query


def _hash_password(password: str) -> str:
    """Retourne un hash sécurisé (SHA256) du mot de passe."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


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
            params=("admin", _hash_password("admin123"), "admin"),
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

    if user["password_hash"] != _hash_password(password):
        return None

    return user


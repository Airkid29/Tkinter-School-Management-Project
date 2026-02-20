import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG


def get_connection():
    """Retourne une connexion MySQL ou lève une exception claire."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )
        if not conn.is_connected():
            raise Error("Connexion MySQL échouée.")
        return conn
    except Error as e:
        raise RuntimeError(f"Erreur de connexion MySQL: {e}") from e


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Utilitaire générique pour exécuter une requête.
    - params : tuple ou dict de paramètres
    - fetchone / fetchall : contrôle du retour
    - commit : si True, commit la transaction
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

        if commit:
            conn.commit()

        return result
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


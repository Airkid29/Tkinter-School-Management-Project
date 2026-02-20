"""
Accès aux données pour les enseignants (table `teachers`).
"""

from db import execute_query


def get_all_teachers():
    """
    Retourne la liste de tous les enseignants, triés par matricule.
    """
    return execute_query(
        """
        SELECT id, last_name, first_name, email, department, phone, created_at
        FROM teachers
        ORDER BY last_name
        """,
        fetchall=True,
    )


def get_teacher_count():
    """
    Retourne le nombre total d'enseignants.
    """
    result = execute_query(
        "SELECT COUNT(*) as count FROM teachers",
        fetchone=True,
    )
    return result["count"] if result else 0

"""
Accès aux données pour les étudiants (table `students`).
"""

from db import execute_query


def get_all_students():
    """
    Retourne la liste de tous les étudiants, triés par matricule.
    """
    return execute_query(
        """
        SELECT id, matricule, first_name, last_name, email, phone, created_at
        FROM students
        ORDER BY matricule
        """,
        fetchall=True,
    )


def get_student_count():
    """
    Retourne le nombre total d'étudiants.
    """
    result = execute_query(
        "SELECT COUNT(*) as count FROM students",
        fetchone=True,
    )
    return result["count"] if result else 0

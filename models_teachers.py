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


def get_teacher_by_id(teacher_id: int):
    """Retourne un enseignant par son id."""
    return execute_query(
        "SELECT id, first_name, last_name, email, phone, department FROM teachers WHERE id = %s",
        params=(teacher_id,),
        fetchone=True,
    )


def create_teacher(first_name: str, last_name: str, email: str = "", phone: str = "", department: str = ""):
    """Crée un nouvel enseignant."""
    execute_query(
        """
        INSERT INTO teachers (first_name, last_name, email, phone, department)
        VALUES (%s, %s, %s, %s, %s)
        """,
        params=(first_name.strip(), last_name.strip(), email.strip() or None, phone.strip() or None, department.strip() or None),
        commit=True,
    )


def update_teacher(teacher_id: int, first_name: str, last_name: str, email: str = "", phone: str = "", department: str = ""):
    """Met à jour un enseignant existant."""
    execute_query(
        """
        UPDATE teachers SET first_name = %s, last_name = %s, email = %s, phone = %s, department = %s
        WHERE id = %s
        """,
        params=(first_name.strip(), last_name.strip(), email.strip() or None, phone.strip() or None, department.strip() or None, teacher_id),
        commit=True,
    )


def delete_teacher(teacher_id: int):
    """Supprime un enseignant."""
    execute_query("DELETE FROM teachers WHERE id = %s", params=(teacher_id,), commit=True)

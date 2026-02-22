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


def get_student_by_id(student_id: int):
    """Retourne un étudiant par son id."""
    return execute_query(
        "SELECT id, matricule, first_name, last_name, email, phone FROM students WHERE id = %s",
        params=(student_id,),
        fetchone=True,
    )


def create_student(matricule: str, first_name: str, last_name: str, email: str = "", phone: str = ""):
    """Crée un nouvel étudiant."""
    execute_query(
        """
        INSERT INTO students (matricule, first_name, last_name, email, phone)
        VALUES (%s, %s, %s, %s, %s)
        """,
        params=(matricule.strip(), first_name.strip(), last_name.strip(), email.strip() or None, phone.strip() or None),
        commit=True,
    )


def update_student(student_id: int, matricule: str, first_name: str, last_name: str, email: str = "", phone: str = ""):
    """Met à jour un étudiant existant."""
    execute_query(
        """
        UPDATE students SET matricule = %s, first_name = %s, last_name = %s, email = %s, phone = %s
        WHERE id = %s
        """,
        params=(matricule.strip(), first_name.strip(), last_name.strip(), email.strip() or None, phone.strip() or None, student_id),
        commit=True,
    )


def delete_student(student_id: int):
    """Supprime un étudiant."""
    execute_query("DELETE FROM students WHERE id = %s", params=(student_id,), commit=True)

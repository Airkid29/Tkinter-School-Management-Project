"""
Accès aux données pour les inscriptions (table `enrollments`).
"""

from db import execute_query


def get_all_enrollments():
    """
    Retourne la liste des inscriptions avec les noms des étudiants et des cours.
    """
    return execute_query(
        """
        SELECT 
            e.id, 
            e.student_id,
            e.course_id,
            e.academic_year, 
            e.semester,
            s.matricule,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            c.code,
            c.name AS course_name
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY e.academic_year DESC, e.semester, s.last_name
        """,
        fetchall=True,
    )


def create_enrollment(student_id: int, course_id: int, academic_year: str, semester: str):
    """Crée une nouvelle inscription."""
    execute_query(
        """
        INSERT INTO enrollments (student_id, course_id, academic_year, semester)
        VALUES (%s, %s, %s, %s)
        """,
        params=(student_id, course_id, academic_year.strip(), semester),
        commit=True,
    )


def delete_enrollment(enrollment_id: int):
    """Supprime une inscription."""
    execute_query("DELETE FROM enrollments WHERE id = %s", params=(enrollment_id,), commit=True)


def get_enrollment_count_for_year(academic_year: str):
    """Retourne le nombre d'inscriptions pour une année académique."""
    result = execute_query(
        "SELECT COUNT(*) AS cnt FROM enrollments WHERE academic_year = %s",
        params=(academic_year,),
        fetchone=True,
    )
    return result["cnt"] if result else 0

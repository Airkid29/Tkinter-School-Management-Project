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

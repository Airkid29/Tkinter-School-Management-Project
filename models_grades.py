"""
Accès aux données pour les notes (table `grades`).
"""

from db import execute_query


def get_all_grades():
    """
    Retourne la liste des notes avec les infos étudiant et cours.
    """
    return execute_query(
        """
        SELECT 
            g.id, 
            g.grade, 
            e.academic_year, 
            e.semester,
            s.matricule,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            c.code,
            c.name AS course_name
        FROM grades g
        JOIN enrollments e ON g.enrollment_id = e.id
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY e.academic_year DESC, e.semester, s.last_name
        """,
        fetchall=True,
    )

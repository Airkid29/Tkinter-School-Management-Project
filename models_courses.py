"""
Accès aux données pour les cours (table `courses`).
"""

from db import execute_query


def get_all_courses():
    """
    Retourne la liste de tous les cours avec le nom du professeur associé.
    """
    return execute_query(
        """
        SELECT 
            c.id, 
            c.code, 
            c.name, 
            c.credits, 
            CONCAT(t.first_name, ' ', t.last_name) AS teacher_name
        FROM courses c
        LEFT JOIN teachers t ON c.teacher_id = t.id
        ORDER BY c.code
        """,
        fetchall=True,
    )


def get_course_count():
    """
    Compte le nombre total de cours.
    """
    result = execute_query("SELECT COUNT(*) as count FROM courses", fetchone=True)
    return result["count"] if result else 0

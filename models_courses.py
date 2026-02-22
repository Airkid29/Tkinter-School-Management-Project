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


def get_course_by_id(course_id: int):
    """Retourne un cours par son id (avec teacher_id pour édition)."""
    return execute_query(
        "SELECT id, code, name, credits, teacher_id FROM courses WHERE id = %s",
        params=(course_id,),
        fetchone=True,
    )


def create_course(code: str, name: str, credits: int, teacher_id: int = None):
    """Crée un nouveau cours."""
    execute_query(
        """
        INSERT INTO courses (code, name, credits, teacher_id)
        VALUES (%s, %s, %s, %s)
        """,
        params=(code.strip(), name.strip(), int(credits), teacher_id),
        commit=True,
    )


def update_course(course_id: int, code: str, name: str, credits: int, teacher_id: int = None):
    """Met à jour un cours existant."""
    execute_query(
        """
        UPDATE courses SET code = %s, name = %s, credits = %s, teacher_id = %s
        WHERE id = %s
        """,
        params=(code.strip(), name.strip(), int(credits), teacher_id, course_id),
        commit=True,
    )


def delete_course(course_id: int):
    """Supprime un cours."""
    execute_query("DELETE FROM courses WHERE id = %s", params=(course_id,), commit=True)

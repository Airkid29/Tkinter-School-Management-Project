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
            g.enrollment_id,
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


def create_or_update_grade(enrollment_id: int, grade: float):
    """Crée ou met à jour la note d'une inscription."""
    existing = execute_query(
        "SELECT id FROM grades WHERE enrollment_id = %s",
        params=(enrollment_id,),
        fetchone=True,
    )
    grade_val = float(grade) if grade is not None and str(grade).strip() else None
    if existing:
        execute_query(
            "UPDATE grades SET grade = %s WHERE enrollment_id = %s",
            params=(grade_val, enrollment_id),
            commit=True,
        )
    else:
        execute_query(
            "INSERT INTO grades (enrollment_id, grade) VALUES (%s, %s)",
            params=(enrollment_id, grade_val),
            commit=True,
        )


def delete_grade(grade_id: int):
    """Supprime une note."""
    execute_query("DELETE FROM grades WHERE id = %s", params=(grade_id,), commit=True)


def get_average_grade():
    """Retourne la moyenne générale des notes (hors NULL)."""
    result = execute_query(
        "SELECT AVG(grade) AS avg_grade FROM grades WHERE grade IS NOT NULL",
        fetchone=True,
    )
    return round(float(result["avg_grade"]), 2) if result and result["avg_grade"] is not None else None

"""
Accès aux archives par année académique (10 dernières années).
"""

from db import execute_query


def get_available_academic_years():
    """Retourne les années académiques disponibles (10 dernières années)."""
    from datetime import datetime
    current_year = datetime.now().year
    synthetic = [f"{current_year - i}-{current_year - i + 1}" for i in range(10)]
    result = execute_query(
        """
        SELECT DISTINCT academic_year FROM enrollments
        ORDER BY academic_year DESC
        """,
        fetchall=True,
    )
    db_years = [r["academic_year"] for r in result] if result else []
    seen = set()
    years = []
    for y in db_years + synthetic:
        if y not in seen:
            seen.add(y)
            years.append(y)
    return years[:10]


def get_enrollments_by_year(academic_year: str):
    """Inscriptions pour une année académique (étudiant + classe)."""
    return execute_query(
        """
        SELECT e.id, e.academic_year, e.semester, s.matricule,
               CONCAT(s.first_name, ' ', s.last_name) AS student_name,
               cl.name AS class_name
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN classes cl ON e.class_id = cl.id
        WHERE e.academic_year = %s
        ORDER BY e.semester, s.last_name
        """,
        params=(academic_year,),
        fetchall=True,
    )


def get_grades_by_year(academic_year: str):
    """Notes pour une année académique."""
    return execute_query(
        """
        SELECT g.id, g.enrollment_id, g.grade, e.academic_year, e.semester,
               CONCAT(s.first_name, ' ', s.last_name) AS student_name,
               c.code, c.name AS course_name
        FROM grades g
        JOIN enrollments e ON g.enrollment_id = e.id
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON g.course_id = c.id
        WHERE e.academic_year = %s
        ORDER BY e.semester, s.last_name
        """,
        params=(academic_year,),
        fetchall=True,
    )


def get_students_by_year(academic_year: str):
    """Étudiants inscrits au moins une fois durant l'année académique."""
    return execute_query(
        """
        SELECT DISTINCT s.id, s.matricule, s.first_name, s.last_name, s.email, s.phone
        FROM students s
        JOIN enrollments e ON s.id = e.student_id
        WHERE e.academic_year = %s
        ORDER BY s.matricule
        """,
        params=(academic_year,),
        fetchall=True,
    )


def get_courses_by_year(academic_year: str):
    """Cours ayant au moins une inscription durant l'année (via classes)."""
    return execute_query(
        """
        SELECT DISTINCT c.id, c.code, c.name, c.credits,
               CONCAT(t.first_name, ' ', t.last_name) AS teacher_name
        FROM courses c
        LEFT JOIN teachers t ON c.teacher_id = t.id
        JOIN class_courses cc ON cc.course_id = c.id
        JOIN enrollments e ON e.class_id = cc.class_id
        WHERE e.academic_year = %s
        ORDER BY c.code
        """,
        params=(academic_year,),
        fetchall=True,
    )


def get_teachers_by_year(academic_year: str):
    """Enseignants ayant enseigné au moins un cours (classe avec inscriptions) cette année."""
    return execute_query(
        """
        SELECT DISTINCT t.id, t.first_name, t.last_name, t.email, t.department, t.phone
        FROM teachers t
        JOIN courses c ON c.teacher_id = t.id
        JOIN class_courses cc ON cc.course_id = c.id
        JOIN enrollments e ON e.class_id = cc.class_id
        WHERE e.academic_year = %s
        ORDER BY t.last_name
        """,
        params=(academic_year,),
        fetchall=True,
    )


def get_archive_count():
    """Nombre d'années académiques distinctes avec des données."""
    result = execute_query(
        "SELECT COUNT(DISTINCT academic_year) AS cnt FROM enrollments",
        fetchone=True,
    )
    return result["cnt"] if result else 0

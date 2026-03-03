"""
Accès aux données pour les notes (table `grades`).
Une note = inscription (étudiant+classe) + cours (du programme de la classe).
"""

from db import execute_query


def get_all_grades():
    """Retourne les notes avec infos étudiant, classe et cours."""
    return execute_query(
        """
        SELECT g.id, g.enrollment_id, g.course_id, g.grade,
               e.academic_year, e.semester,
               s.matricule,
               CONCAT(s.first_name, ' ', s.last_name) AS student_name,
               cl.name AS class_name,
               c.code, c.name AS course_name
        FROM grades g
        JOIN enrollments e ON g.enrollment_id = e.id
        JOIN students s ON e.student_id = s.id
        JOIN classes cl ON e.class_id = cl.id
        JOIN courses c ON g.course_id = c.id
        ORDER BY e.academic_year DESC, e.semester, s.last_name, c.code
        """,
        fetchall=True,
    )


def create_or_update_grade(enrollment_id: int, course_id: int, grade: float):
    """Crée ou met à jour la note (inscription + cours)."""
    existing = execute_query(
        "SELECT id FROM grades WHERE enrollment_id = %s AND course_id = %s",
        params=(enrollment_id, course_id),
        fetchone=True,
    )
    grade_val = float(grade) if grade is not None and str(grade).strip() else None
    if existing:
        execute_query(
            "UPDATE grades SET grade = %s WHERE enrollment_id = %s AND course_id = %s",
            params=(grade_val, enrollment_id, course_id),
            commit=True,
        )
    else:
        execute_query(
            "INSERT INTO grades (enrollment_id, course_id, grade) VALUES (%s, %s, %s)",
            params=(enrollment_id, course_id, grade_val),
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


def get_grade_distribution():
    """Répartition des notes par tranche pour les graphiques."""
    result = execute_query(
        """
        SELECT
            SUM(CASE WHEN grade IS NOT NULL AND grade < 5 THEN 1 ELSE 0 END) AS under_5,
            SUM(CASE WHEN grade >= 5 AND grade < 10 THEN 1 ELSE 0 END) AS from_5_to_10,
            SUM(CASE WHEN grade >= 10 AND grade < 15 THEN 1 ELSE 0 END) AS from_10_to_15,
            SUM(CASE WHEN grade >= 15 AND grade <= 20 THEN 1 ELSE 0 END) AS from_15_to_20
        FROM grades
        """,
        fetchone=True,
    )
    if not result:
        return ["0-5", "5-10", "10-15", "15-20"], [0, 0, 0, 0]
    labels = ["0-5", "5-10", "10-15", "15-20"]
    values = [
        result.get("under_5") or 0,
        result.get("from_5_to_10") or 0,
        result.get("from_10_to_15") or 0,
        result.get("from_15_to_20") or 0,
    ]
    return labels, values


def get_student_periods(student_id: int):
    """
    Retourne les périodes (année académique + semestre) où l'étudiant a au moins une inscription.
    Format: liste de dicts {academic_year, semester} triée du plus récent au plus ancien.
    """
    return execute_query(
        """
        SELECT DISTINCT academic_year, semester
        FROM enrollments
        WHERE student_id = %s
        ORDER BY academic_year DESC, semester DESC
        """,
        params=(student_id,),
        fetchall=True,
    ) or []


def get_bulletin_data(student_id: int, academic_year: str, semester: str):
    """
    Retourne les données du bulletin pour un étudiant (année + semestre).
    Liste de dicts: class_name, course_name, course_code, grade.
    Plus infos étudiant (matricule, nom, prénom).
    """
    student = execute_query(
        "SELECT matricule, first_name, last_name FROM students WHERE id = %s",
        params=(student_id,),
        fetchone=True,
    )
    if not student:
        return None, []

    rows = execute_query(
        """
        SELECT cl.name AS class_name, c.code AS course_code, c.name AS course_name, g.grade
        FROM enrollments e
        JOIN classes cl ON e.class_id = cl.id
        JOIN class_courses cc ON cc.class_id = cl.id
        JOIN courses c ON cc.course_id = c.id
        LEFT JOIN grades g ON g.enrollment_id = e.id AND g.course_id = c.id
        WHERE e.student_id = %s AND e.academic_year = %s AND e.semester = %s
        ORDER BY cl.name, c.code
        """,
        params=(student_id, academic_year, semester),
        fetchall=True,
    )
    return student, rows or []

"""
Accès aux données pour les inscriptions (table `enrollments`).
Une inscription = étudiant inscrit dans une classe (année + semestre).
"""

from db import execute_query


def get_all_enrollments():
    """Retourne les inscriptions avec nom étudiant et nom de la classe."""
    return execute_query(
        """
        SELECT e.id, e.student_id, e.class_id, e.academic_year, e.semester,
               s.matricule,
               CONCAT(s.first_name, ' ', s.last_name) AS student_name,
               cl.name AS class_name
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN classes cl ON e.class_id = cl.id
        ORDER BY e.academic_year DESC, e.semester, s.last_name
        """,
        fetchall=True,
    )


def create_enrollment(student_id: int, class_id: int, academic_year: str, semester: str):
    """Crée une inscription (étudiant dans une classe)."""
    execute_query(
        """
        INSERT INTO enrollments (student_id, class_id, academic_year, semester)
        VALUES (%s, %s, %s, %s)
        """,
        params=(student_id, class_id, academic_year.strip(), semester),
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


def get_enrollments_per_year():
    """Retourne le nombre d'inscriptions par année (10 dernières années) pour les graphiques."""
    result = execute_query(
        """
        SELECT academic_year, COUNT(*) AS cnt
        FROM enrollments
        GROUP BY academic_year
        ORDER BY academic_year DESC
        LIMIT 10
        """,
        fetchall=True,
    )
    if not result:
        return [], []
    years = [r["academic_year"] for r in reversed(result)]
    counts = [r["cnt"] for r in reversed(result)]
    return years, counts

"""
Accès aux données pour les classes (table `classes`).
Les cours sont attribués aux classes via `class_courses`.
"""

from db import execute_query


def get_all_classes():
    """Retourne toutes les classes, triées par année puis nom."""
    return execute_query(
        """
        SELECT id, name, academic_year, semester, created_at
        FROM classes
        ORDER BY academic_year DESC, semester, name
        """,
        fetchall=True,
    )


def get_class_count():
    """Retourne le nombre total de classes."""
    result = execute_query("SELECT COUNT(*) AS cnt FROM classes", fetchone=True)
    return result["cnt"] if result else 0


def get_class_by_id(class_id: int):
    """Retourne une classe par son id."""
    return execute_query(
        "SELECT id, name, academic_year, semester FROM classes WHERE id = %s",
        params=(class_id,),
        fetchone=True,
    )


def get_courses_for_class(class_id: int):
    """Retourne les cours attribués à une classe (id, code, name, credits, teacher_name)."""
    return execute_query(
        """
        SELECT c.id, c.code, c.name, c.credits,
               CONCAT(t.first_name, ' ', t.last_name) AS teacher_name
        FROM class_courses cc
        JOIN courses c ON cc.course_id = c.id
        LEFT JOIN teachers t ON c.teacher_id = t.id
        WHERE cc.class_id = %s
        ORDER BY c.code
        """,
        params=(class_id,),
        fetchall=True,
    )


def create_class(name: str, academic_year: str, semester: str):
    """Crée une nouvelle classe. Retourne l'id de la classe créée."""
    execute_query(
        """
        INSERT INTO classes (name, academic_year, semester)
        VALUES (%s, %s, %s)
        """,
        params=(name.strip(), academic_year.strip(), semester),
        commit=True,
    )
    r = execute_query(
        "SELECT id FROM classes WHERE name = %s AND academic_year = %s AND semester = %s ORDER BY id DESC LIMIT 1",
        params=(name.strip(), academic_year.strip(), semester),
        fetchone=True,
    )
    return r["id"] if r else None


def update_class(class_id: int, name: str, academic_year: str, semester: str):
    """Met à jour une classe."""
    execute_query(
        """
        UPDATE classes SET name = %s, academic_year = %s, semester = %s
        WHERE id = %s
        """,
        params=(name.strip(), academic_year.strip(), semester, class_id),
        commit=True,
    )


def delete_class(class_id: int):
    """Supprime une classe."""
    execute_query("DELETE FROM classes WHERE id = %s", params=(class_id,), commit=True)


def add_course_to_class(class_id: int, course_id: int):
    """Attribue un cours à une classe."""
    execute_query(
        "INSERT IGNORE INTO class_courses (class_id, course_id) VALUES (%s, %s)",
        params=(class_id, course_id),
        commit=True,
    )


def remove_course_from_class(class_id: int, course_id: int):
    """Retire un cours d'une classe."""
    execute_query(
        "DELETE FROM class_courses WHERE class_id = %s AND course_id = %s",
        params=(class_id, course_id),
        commit=True,
    )


def set_class_courses(class_id: int, course_ids: list):
    """Remplace la liste des cours d'une classe par course_ids."""
    execute_query(
        "DELETE FROM class_courses WHERE class_id = %s",
        params=(class_id,),
        commit=True,
    )
    for cid in course_ids:
        add_course_to_class(class_id, cid)

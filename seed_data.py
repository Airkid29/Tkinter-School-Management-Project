"""
Génère et insère des données de démonstration (MySQL) pour le projet.

Usage:
  python seed_data.py
  python seed_data.py --reset
  python seed_data.py --students 200 --teachers 25 --courses 40 --classes 10
"""

from __future__ import annotations

import argparse
import random
import string
from datetime import datetime

from db import get_connection
from init_db import verify_tables


FIRST_NAMES = [
    "BAWA",
    "SEBOU",
    "BONGOR",
    "BOCCO",
    "ZOUNGRANA",
    "NANGA",
    "BOUKPESSI",
    "NAMESSI",
    "MANZI",
    "MADZRA",
    "ABDOULAYE",
    "KONE",
    "ADAM",
    "SAKPACLA",
    "ALI",
    "KOUGBAGAN",
    "MOUSSA",
    "WOTOGLO",
]

LAST_NAMES = [
    "Rachid",
    "Farid",
    "Mohamed",
    "Bienvenue",
    "Bella",
    "Jeanne",
    "Tresor",
    "Reine",
    "Francine",
    "Fulbert",
    "Bernice",
    "Joel",
    "Henry",
    "Marzouk",
    "Manaf",
    "Zeinab",
    "Raymond",
    "Joanita",
    "Clement",
    "Rahim",
]

DEPARTMENTS = [
    "Informatique",
    "Mathématiques",
    "Gestion",
    "Réseaux",
    "Développement",
    "Administration",
    "Comptabilité",
]


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = s.replace(" ", ".")
    allowed = string.ascii_lowercase + string.digits + ".-"
    return "".join(ch for ch in s if ch in allowed)


def _rand_phone(rng: random.Random) -> str:
    # Format simple type: +221 77 123 45 67
    return f"+221 {rng.choice(['70','75','76','77','78'])} {rng.randint(100,999)} {rng.randint(10,99)} {rng.randint(10,99)}"


def _rand_email(rng: random.Random, first: str, last: str) -> str:
    domain = rng.choice(["ecole.local", "univ.local", "example.com"])
    return f"{_slug(first)}.{_slug(last)}{rng.randint(1,999)}@{domain}"


def _rand_course_code(rng: random.Random, used: set[str]) -> str:
    # Ex: INF101, MTH204, GES110
    prefixes = ["INF", "MTH", "GES", "RSX", "DEV", "ADM"]
    while True:
        code = f"{rng.choice(prefixes)}{rng.randint(100,499)}"
        if code not in used:
            used.add(code)
            return code


def _academic_years(last_n: int = 3) -> list[str]:
    y = datetime.now().year
    # ex: 2025-2026, 2024-2025, ...
    return [f"{y - i}-{y - i + 1}" for i in range(last_n)]


def reset_db(conn) -> None:
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for table in ["grades", "enrollments", "class_courses", "classes", "courses", "teachers", "students"]:
        cur.execute(f"TRUNCATE TABLE {table}")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Vide les tables métier avant insertion.")
    parser.add_argument("--students", type=int, default=200)
    parser.add_argument("--teachers", type=int, default=25)
    parser.add_argument("--courses", type=int, default=45)
    parser.add_argument("--classes", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42, help="Graine aléatoire (reproductible).")
    args = parser.parse_args()

    missing = verify_tables()
    if missing:
        raise RuntimeError(
            "Tables manquantes: " + ", ".join(missing) + ". Exécutez d'abord: python init_db.py"
        )

    rng = random.Random(args.seed)

    conn = get_connection()
    try:
        if args.reset:
            reset_db(conn)

        cur = conn.cursor()

        # --- teachers
        teachers = []
        for _ in range(args.teachers):
            fn = rng.choice(FIRST_NAMES)
            ln = rng.choice(LAST_NAMES)
            teachers.append(
                (
                    fn,
                    ln,
                    _rand_email(rng, fn, ln),
                    _rand_phone(rng),
                    rng.choice(DEPARTMENTS),
                )
            )
        cur.executemany(
            """
            INSERT INTO teachers (first_name, last_name, email, phone, department)
            VALUES (%s, %s, %s, %s, %s)
            """,
            teachers,
        )
        conn.commit()
        cur.execute("SELECT id FROM teachers ORDER BY id")
        teacher_ids = [row[0] for row in cur.fetchall()]

        # --- courses
        used_codes: set[str] = set()
        courses = []
        for i in range(args.courses):
            code = _rand_course_code(rng, used_codes)
            name = rng.choice(
                [
                    "Algorithmique",
                    "Programmation Python",
                    "Bases de données",
                    "Réseaux informatiques",
                    "Développement Web",
                    "Sécurité",
                    "Systèmes d'exploitation",
                    "Maths discrètes",
                    "Gestion de projet",
                    "Architecture logicielle",
                ]
            )
            title = f"{name} {rng.choice(['I', 'II', 'Avancé', 'Fondamentaux'])}"
            credits = rng.choice([2, 3, 4, 5])
            teacher_id = rng.choice(teacher_ids) if teacher_ids else None
            courses.append((code, title, credits, teacher_id))
        cur.executemany(
            """
            INSERT INTO courses (code, name, credits, teacher_id)
            VALUES (%s, %s, %s, %s)
            """,
            courses,
        )
        conn.commit()
        cur.execute("SELECT id FROM courses ORDER BY id")
        course_ids = [row[0] for row in cur.fetchall()]

        # --- students
        students = []
        used_matricules: set[str] = set()
        for i in range(args.students):
            fn = rng.choice(FIRST_NAMES)
            ln = rng.choice(LAST_NAMES)
            while True:
                matricule = f"MAT{rng.randint(10_000, 99_999)}"
                if matricule not in used_matricules:
                    used_matricules.add(matricule)
                    break
            students.append(
                (
                    matricule,
                    fn,
                    ln,
                    _rand_email(rng, fn, ln),
                    _rand_phone(rng),
                )
            )
        cur.executemany(
            """
            INSERT INTO students (matricule, first_name, last_name, email, phone)
            VALUES (%s, %s, %s, %s, %s)
            """,
            students,
        )
        conn.commit()
        cur.execute("SELECT id FROM students ORDER BY id")
        student_ids = [row[0] for row in cur.fetchall()]

        # --- classes
        years = _academic_years(3)
        semesters = ["S1", "S2"]
        base_names = [
            "IG 1",
            "IG 2",
            "SICC 1",
            "SICC 2",
            "CGE 1",
            "CGE 2",
        ]
        classes = []
        for _ in range(args.classes):
            name = rng.choice(base_names) + f" - G{rng.randint(1,4)}"
            year = rng.choice(years)
            sem = rng.choice(semesters)
            classes.append((name, year, sem))

        # INSERT IGNORE to avoid unique(name,year,sem) collisions
        cur.executemany(
            """
            INSERT IGNORE INTO classes (name, academic_year, semester)
            VALUES (%s, %s, %s)
            """,
            classes,
        )
        conn.commit()
        cur.execute("SELECT id, academic_year, semester FROM classes ORDER BY id")
        classes_rows = cur.fetchall()
        class_ids = [row[0] for row in classes_rows]
        class_meta = {row[0]: (row[1], row[2]) for row in classes_rows}

        # --- class_courses (assign 8-12 courses per class)
        cc = []
        for cid in class_ids:
            k = min(len(course_ids), rng.randint(8, 12))
            for course_id in rng.sample(course_ids, k=k):
                cc.append((cid, course_id))
        cur.executemany(
            """
            INSERT IGNORE INTO class_courses (class_id, course_id)
            VALUES (%s, %s)
            """,
            cc,
        )
        conn.commit()

        # Build map class -> course_ids
        cur.execute("SELECT class_id, course_id FROM class_courses")
        class_to_courses: dict[int, list[int]] = {}
        for cl_id, co_id in cur.fetchall():
            class_to_courses.setdefault(cl_id, []).append(co_id)

        # --- enrollments
        # Each student: 1-2 enrollments across available classes
        enrollments = []
        for sid in student_ids:
            for cl_id in rng.sample(class_ids, k=min(len(class_ids), rng.choice([1, 1, 2]))):
                year, sem = class_meta[cl_id]
                enrollments.append((sid, cl_id, year, sem))
        cur.executemany(
            """
            INSERT IGNORE INTO enrollments (student_id, class_id, academic_year, semester)
            VALUES (%s, %s, %s, %s)
            """,
            enrollments,
        )
        conn.commit()

        cur.execute("SELECT id, class_id FROM enrollments ORDER BY id")
        enr_rows = cur.fetchall()

        # --- grades
        # For each enrollment, create grades for most courses in that class
        grades = []
        for enr_id, cl_id in enr_rows:
            course_list = class_to_courses.get(cl_id, [])
            if not course_list:
                continue
            # Not all grades are present
            for co_id in course_list:
                if rng.random() < 0.15:
                    grade = None
                else:
                    grade = round(rng.uniform(4, 18), 2)
                grades.append((enr_id, co_id, grade))
        cur.executemany(
            """
            INSERT IGNORE INTO grades (enrollment_id, course_id, grade)
            VALUES (%s, %s, %s)
            """,
            grades,
        )
        conn.commit()

        # Summary
        def count(table: str) -> int:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            return int(cur.fetchone()[0])

        print("Insertion terminée.")
        print("Résumé:")
        for t in ["students", "teachers", "courses", "classes", "class_courses", "enrollments", "grades"]:
            print(f"- {t}: {count(t)}")

        return 0
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())


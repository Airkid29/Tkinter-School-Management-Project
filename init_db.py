from mysql.connector import Error

from config import DB_CONFIG
from db import get_connection


def create_database_if_not_exists():
    """Crée la base de données si elle n'existe pas encore."""
    try:
        conn = get_connection()
        conn.close()
    except RuntimeError:
        # Il faut se connecter sans spécifier la base
        import mysql.connector

        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
            )
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            conn.commit()
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass


def create_tables():
    """Crée les tables principales nécessaires au système universitaire."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Utilisateurs (admins, users, etc.)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Étudiants
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                matricule VARCHAR(50) UNIQUE NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(150),
                phone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Professeurs
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS teachers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(150),
                phone VARCHAR(50),
                department VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Cours
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(150) NOT NULL,
                credits INT NOT NULL,
                teacher_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
            )
            """
        )

        # Classes (les cours sont attribués aux classes, pas directement aux étudiants)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS classes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                academic_year VARCHAR(20) NOT NULL,
                semester ENUM('S1', 'S2') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, academic_year, semester)
            )
            """
        )

        # Cours attribués à chaque classe
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS class_courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                class_id INT NOT NULL,
                course_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(class_id, course_id),
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
            """
        )

        # Inscriptions : étudiant inscrit dans une classe (et non plus à un cours direct)
        # Recréer si ancien schéma (course_id) pour passer à class_id
        cursor.execute("DROP TABLE IF EXISTS grades")
        cursor.execute("DROP TABLE IF EXISTS enrollments")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                class_id INT NOT NULL,
                academic_year VARCHAR(20) NOT NULL,
                semester ENUM('S1', 'S2') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, class_id, academic_year, semester),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            )
            """
        )

        # Notes : par inscription (étudiant+classe) et par cours
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS grades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                enrollment_id INT NOT NULL,
                course_id INT NOT NULL,
                grade DECIMAL(4,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(enrollment_id, course_id),
                FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
            """
        )

        conn.commit()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def verify_tables():
    """Vérifie que toutes les tables requises existent. Retourne la liste des tables manquantes."""
    required = ("users", "students", "teachers", "courses", "classes", "class_courses", "enrollments", "grades")
    conn = None
    cursor = None
    missing = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        existing = set()
        for row in cursor.fetchall():
            name = row[0]
            if isinstance(name, bytes):
                name = name.decode("utf-8")
            existing.add(name.lower())
        for table in required:
            if table.lower() not in existing:
                missing.append(table)
        return missing
    except Exception as e:
        return list(required)  # en cas d'erreur, considérer que tout manque
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def seed_default_data():
    """
    Insère des données minimales (admin par défaut) si nécessaire.
    """
    from models_users import create_default_admin_if_not_exists

    create_default_admin_if_not_exists()


if __name__ == "__main__":
    print("Création de la base et des tables…")
    create_database_if_not_exists()
    create_tables()
    missing = verify_tables()
    if missing:
        print("ATTENTION - Tables manquantes après création :", ", ".join(missing))
        print("Relancez ce script. Si le problème persiste, vérifiez la connexion MySQL et les droits.")
    else:
        print("Toutes les tables sont présentes : users, students, teachers, courses, classes, class_courses, enrollments, grades.")
    seed_default_data()
    print("Terminé.")


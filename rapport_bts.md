# Rapport de projet – Système de gestion universitaire  
## BTS (OFT / Informatique)

---

## 1. Introduction

Ce projet consiste en une application de bureau de **gestion d’un établissement universitaire**, réalisée en **Python** avec l’interface graphique **Tkinter** et le SGBD **MySQL**. L’objectif est de permettre la gestion des étudiants, des enseignants, des cours, des classes, des inscriptions et des notes, avec une authentification sécurisée (rôles admin / utilisateur) et des fonctionnalités annexes (bulletins, archives, statistiques).

Les cours sont rattachés aux **classes** ; les étudiants s’inscrivent à des **classes** (et non directement à des cours). Les notes sont enregistrées par inscription (étudiant–classe) et par cours. L’application offre un tableau de bord, des écrans CRUD pour chaque entité, l’édition de bulletins imprimables et la consultation d’archives sur plusieurs années.

Le présent document décrit le dictionnaire de données, le modèle logique des données (MLD) et le modèle conceptuel des données (MCD) de la base utilisée par cette application.

---

## 2. Dictionnaire de données

Conventions : **Type** : N = Numérique, A = Alphabétique, AN = Alphanumérique, D = Date/Heure, E = Énumération.  
**Nature** : E = Clé d’entité (identifiant), C = Clé étrangère (référence), A = Attribut.

| N° | Code | Signification | Type | Nature | Commentaire |
|----|------|---------------|------|--------|-------------|
| 1 | id (users) | Identifiant unique de l’utilisateur | N | E | Clé primaire |
| 2 | username | Nom de connexion de l’utilisateur | AN | A | Unique |
| 3 | password_hash | Mot de passe haché (Argon2) | AN | A | Non réversible |
| 4 | role | Rôle (admin / user) | E | A | Valeurs : admin, user |
| 5 | created_at (users) | Date de création du compte | D | A | Horodatage |
| 6 | id (students) | Identifiant unique de l’étudiant | N | E | Clé primaire |
| 7 | matricule | Matricule de l’étudiant | AN | A | Identifiant métier, unique |
| 8 | first_name (students) | Prénom de l’étudiant | A | A | |
| 9 | last_name (students) | Nom de l’étudiant | A | A | |
| 10 | email (students) | Adresse courriel de l’étudiant | AN | A | Optionnel |
| 11 | phone (students) | Numéro de téléphone de l’étudiant | AN | A | Optionnel |
| 12 | created_at (students) | Date d’enregistrement | D | A | Horodatage |
| 13 | id (teachers) | Identifiant unique de l’enseignant | N | E | Clé primaire |
| 14 | first_name (teachers) | Prénom de l’enseignant | A | A | |
| 15 | last_name (teachers) | Nom de l’enseignant | A | A | |
| 16 | email (teachers) | Adresse courriel de l’enseignant | AN | A | Optionnel |
| 17 | phone (teachers) | Téléphone de l’enseignant | AN | A | Optionnel |
| 18 | department | Département ou discipline | A | A | Optionnel |
| 19 | created_at (teachers) | Date d’enregistrement | D | A | Horodatage |
| 20 | id (courses) | Identifiant unique du cours | N | E | Clé primaire |
| 21 | code (courses) | Code du cours | AN | A | Unique (ex. INF101) |
| 22 | code (courses) | Intitulé du cours | A | A | |
| 23 | credits | Nombre de crédits ECTS | N | A | Entier |
| 24 | teacher_id | Identifiant de l’enseignant responsable | N | C | Référence teachers |
| 25 | created_at (courses) | Date d’enregistrement | D | A | Horodatage |
| 26 | id (classes) | Identifiant unique de la classe | N | E | Clé primaire |
| 27 | name (classes) | Nom ou libellé de la classe | A | A | Ex. L1 Info |
| 28 | academic_year | Année académique | AN | A | Ex. 2024-2025 |
| 29 | semester | Semestre (S1 ou S2) | E | A | Valeurs : S1, S2 |
| 30 | created_at (classes) | Date d’enregistrement | D | A | Horodatage |
| 31 | id (class_courses) | Identifiant de la liaison classe–cours | N | E | Clé primaire |
| 32 | class_id | Identifiant de la classe | N | C | Référence classes |
| 33 | course_id (class_courses) | Identifiant du cours | N | C | Référence courses |
| 34 | created_at (class_courses) | Date d’enregistrement | D | A | Horodatage |
| 35 | id (enrollments) | Identifiant unique de l’inscription | N | E | Clé primaire |
| 36 | student_id | Identifiant de l’étudiant | N | C | Référence students |
| 37 | class_id (enrollments) | Identifiant de la classe | N | C | Référence classes |
| 38 | academic_year | Année académique de l’inscription | AN | A | |
| 39 | semester | Semestre de l’inscription | E | A | S1 ou S2 |
| 40 | created_at (enrollments) | Date d’inscription | D | A | Horodatage |
| 41 | id (grades) | Identifiant unique de la note | N | E | Clé primaire |
| 42 | enrollment_id | Identifiant de l’inscription (étudiant–classe) | N | C | Référence enrollments |
| 43 | course_id (grades) | Identifiant du cours | N | C | Référence courses |
| 44 | grade | Note sur 20 | N | A | Décimal, optionnel |
| 45 | created_at (grades) | Date d’enregistrement | D | A | Horodatage |

---

## 3. Modèle logique de données (MLD)

Modèle relationnel (tables et clés) correspondant au schéma MySQL.

- **users** (id, username, password_hash, role, created_at)  
  Clé primaire : id.

- **students** (id, matricule, first_name, last_name, email, phone, created_at)  
  Clé primaire : id. Contrainte d’unicité : matricule.

- **teachers** (id, first_name, last_name, email, phone, department, created_at)  
  Clé primaire : id.

- **courses** (id, code, name, credits, teacher_id, created_at)  
  Clé primaire : id. Clé étrangère : teacher_id → teachers(id). Contrainte d’unicité : code.

- **classes** (id, name, academic_year, semester, created_at)  
  Clé primaire : id. Contrainte d’unicité : (name, academic_year, semester).

- **class_courses** (id, class_id, course_id, created_at)  
  Clé primaire : id. Clés étrangères : class_id → classes(id), course_id → courses(id). Contrainte d’unicité : (class_id, course_id).

- **enrollments** (id, student_id, class_id, academic_year, semester, created_at)  
  Clé primaire : id. Clés étrangères : student_id → students(id), class_id → classes(id). Contrainte d’unicité : (student_id, class_id, academic_year, semester).

- **grades** (id, enrollment_id, course_id, grade, created_at)  
  Clé primaire : id. Clés étrangères : enrollment_id → enrollments(id), course_id → courses(id). Contrainte d’unicité : (enrollment_id, course_id).

---

## 4. Modèle conceptuel de données (MCD)

Le MCD peut être généré à partir du **code Mocodo** ci‑dessous avec l’outil en ligne suivant :

**Outil : Mocodo**  
→ **https://www.mocodo.net/**

1. Ouvrez le site **https://www.mocodo.net/**  
2. Supprimez le texte par défaut dans la zone de saisie (à gauche).  
3. Copiez-collez le code ci‑dessous.  
4. Le diagramme MCD s’affiche à droite. Vous pouvez l’exporter en image ou en PDF.

### Code Mocodo à coller

```
Utilisateur: id_user, username, password_hash, role

Etudiant: id_etud, matricule, prenom, nom, email, telephone

Enseignant: id_ens, prenom, nom, email, telephone, departement

Cours: id_cours, code, intitule, credits

Classe: id_classe, nom, annee_acad, semestre

Inscription: id_inscr, annee_acad, semestre

Assurer, 1N Enseignant, 11 Cours

Contenir, 1N Classe, 1N Cours

Faire partie, 1N Etudiant, 11 Inscription

Concerne, 1N Classe, 11 Inscription

Noter, 1N Inscription, 11 Cours: note
```

*Remarque :* L’association « Inscrire » a été **réifiée** en entité **Inscription** pour respecter la règle Mocodo/Merise : une association ne peut lier que des entités. Une inscription représente un étudiant inscrit dans une classe (année + semestre). **Faire partie** lie Étudiant à Inscription, **Concerne** lie Classe à Inscription ; **Noter** lie alors Inscription à Cours avec l’attribut *note*.

- **Assurer** : un enseignant assure un ou plusieurs cours ; un cours est assuré par un enseignant.  
- **Contenir** : une classe contient plusieurs cours ; un cours peut être dans plusieurs classes.  
- **Faire partie** : un étudiant a plusieurs inscriptions ; une inscription concerne un seul étudiant.  
- **Concerne** : une classe a plusieurs inscriptions ; une inscription concerne une seule classe.  
- **Noter** : une inscription reçoit plusieurs notes (une par cours) ; un cours a plusieurs notes (attribut : note).

---

## 5. Conclusion

Ce projet a permis de mettre en place une application complète de gestion universitaire, depuis la modélisation des données (MCD, MLD, dictionnaire) jusqu’à l’implémentation d’une interface Tkinter et d’une base MySQL. La séparation entre classes et cours, l’inscription des étudiants aux classes et la gestion des notes par cours dans ce cadre offrent un modèle cohérent et évolutif. Les choix techniques (Argon2 pour les mots de passe, rôles admin/user, CRUD, bulletins, archives) répondent aux besoins d’un contexte type établissement d’enseignement. Les prolongements possibles incluent l’export PDF des bulletins, des rapports statistiques plus poussés ou une version web du même système.

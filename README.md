# Système de gestion d'université (Tkinter + MySQL)

Application de bureau en Python pour gérer une université :
- **Gestion des étudiants, professeurs, cours, classes, inscriptions et notes** (CRUD complet)
- **Cours attribués aux classes** : les étudiants s'inscrivent à une classe (année + semestre), les notes sont par cours dans le cadre de la classe
- **Bulletins** : consultation et impression des bulletins par étudiant, avec détection automatique des périodes où l'étudiant est réellement inscrit
- **Authentification sécurisée** avec Argon2 et gestion des rôles (admin / utilisateur)
- **Interface moderne** avec Tkinter (thème sombre, tri des colonnes, recherche)
- **Exports CSV** pour les listes d'étudiants et de notes
- **Statistiques** sur le tableau de bord (compteurs, inscriptions, moyenne générale, graphiques)

## Prérequis

- Python 3.10+
- MySQL Server installé et accessible (localhost par défaut)

## Installation

1. Créer et activer un environnement virtuel (recommandé) :

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux / macOS
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Configurer MySQL dans `config.py` (hôte, utilisateur, mot de passe, nom de base), ou via variables d'environnement :
   - `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

4. Initialiser la base de données :

```bash
python init_db.py
```

   **Note** : Le schéma associe les **cours aux classes** (table `class_courses`). Les inscriptions lient un étudiant à une classe (année + semestre). Les notes sont enregistrées par inscription et par cours. Si vous mettez à jour une base existante, les tables `enrollments` et `grades` sont recréées (données réinitialisées) ; créez d’abord des classes et assignez-leur des cours.

5. (Optionnel) Remplir la base avec des **données de démonstration** :

```bash
python seed_data.py --reset
```

   Cette commande insère plusieurs centaines d'étudiants, enseignants, cours, classes, inscriptions et notes. Le paramètre `--reset` vide d'abord les tables métier (`students`, `teachers`, `courses`, `classes`, `class_courses`, `enrollments`, `grades`) tout en conservant les utilisateurs.

6. Lancer l'application :

```bash
python main.py
```

## Identifiants par défaut

- **Utilisateur admin** : `admin` / `admin123` (à changer en production)

## Structure du projet
 
- `main.py` : point d'entrée Tkinter (login, tableau de bord, CRUD, exports, bulletins, archives, graphiques)
- `config.py` : configuration MySQL et paramètres de l'interface
- `db.py` : connexion MySQL et fonctions utilitaires
- `init_db.py` : création de la base et des tables
- `seed_data.py` : génération de données de démonstration (remplissage massif de la base)
- `hash_password.py` : hachage et vérification des mots de passe (Argon2)
- `models_users.py` : authentification et utilisateurs
- `models_students.py`, `models_teachers.py`, `models_courses.py`, `models_classes.py` : entités principales
- `models_enrollments.py`, `models_grades.py` : inscriptions (étudiant ↔ classe) et notes (par cours)

## Fonctionnalités

- **Admin** : accès complet (ajout, modification, suppression) sur toutes les entités
- **Utilisateur** : lecture seule
- **Tri** : clic sur les en-têtes des tableaux pour trier
- **Recherche** : filtrage en temps réel (étudiants, cours)
- **Export CSV** : bouton dans les vues Étudiants et Notes

# Système de gestion d'université (Tkinter + MySQL)

Application de bureau en Python pour gérer une université :
- **Gestion des étudiants, professeurs, cours, inscriptions et notes** (CRUD complet)
- **Authentification sécurisée** avec Argon2 et gestion des rôles (admin / utilisateur)
- **Interface moderne** avec Tkinter (thème sombre, tri des colonnes, recherche)
- **Exports CSV** pour les listes d'étudiants et de notes
- **Statistiques** sur le tableau de bord (compteurs, inscriptions, moyenne générale)

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

5. Lancer l'application :

```bash
python main.py
```

## Identifiants par défaut

- **Utilisateur admin** : `admin` / `admin123` (à changer en production)

## Structure du projet

- `main.py` : point d'entrée Tkinter (login, tableau de bord, CRUD, exports)
- `config.py` : configuration MySQL et paramètres de l'interface
- `db.py` : connexion MySQL et fonctions utilitaires
- `init_db.py` : création de la base et des tables
- `hash_password.py` : hachage et vérification des mots de passe (Argon2)
- `models_users.py` : authentification et utilisateurs
- `models_students.py`, `models_teachers.py`, `models_courses.py` : entités principales
- `models_enrollments.py`, `models_grades.py` : inscriptions et notes

## Fonctionnalités

- **Admin** : accès complet (ajout, modification, suppression) sur toutes les entités
- **Utilisateur** : lecture seule
- **Tri** : clic sur les en-têtes des tableaux pour trier
- **Recherche** : filtrage en temps réel (étudiants, cours)
- **Export CSV** : bouton dans les vues Étudiants et Notes

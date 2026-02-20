## Système de gestion d'université (Tkinter + MySQL)

Application de bureau en Python pour gérer une université :
- **Gestion des étudiants, professeurs, cours, inscriptions, notes**
- **Interface moderne avec Tkinter**
- **Persistance des données avec MySQL**

### Prérequis

- Python 3.10+ recommandé
- MySQL Server installé et accessible (localhost par défaut)
- Un utilisateur MySQL avec droits sur une base (ex: `university_db`)

### Installation

1. Créer et activer un environnement virtuel (recommandé) :

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Configurer MySQL dans `config.py` (hôte, utilisateur, mot de passe, nom de base).

4. Initialiser la base de données :

```bash
python init_db.py
```

5. Lancer l’application :

```bash
python main.py
```

### Structure du projet

- `main.py` : point d’entrée Tkinter (fenêtre principale, navigation)
- `config.py` : configuration MySQL et paramètres globaux
- `db.py` : connexion MySQL et fonctions utilitaires
- `init_db.py` : script de création de la base et des tables
- `ui/` : interfaces Tkinter (login, tableau de bord, gestion des entités)
- `models/` : logique d’accès aux données orientée métier


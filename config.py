"""
Configuration globale de l'application.
Les paramètres DB peuvent être surchargés par variables d'environnement :
  DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
"""

import os

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "university_db"),
}

APP_CONFIG = {
    "title": "Gestion d'université",
    "geometry": "1200x700",
    "min_width": 1000,
    "min_height": 600,
    "accent_color": "#2563eb",  # bleu moderne
    "accent_color_hover": "#1d4ed8",
    "bg_color": "#0f172a",      # fond sombre
    "card_bg": "#111827",
    "text_primary": "#e5e7eb",
    "text_secondary": "#9ca3af",
}


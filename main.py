import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from config import APP_CONFIG
from models_users import authenticate_user
from models_students import get_all_students, get_student_count
from models_teachers import get_all_teachers, get_teacher_count
from models_courses import get_all_courses, get_course_count
from models_enrollments import get_all_enrollments
from models_grades import get_all_grades


class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        accent = APP_CONFIG["accent_color"]
        hover = APP_CONFIG["accent_color_hover"]
        base_kwargs = {
            "bg": accent,
            "fg": "white",
            "activebackground": hover,
            "activeforeground": "white",
            "borderwidth": 0,
            "cursor": "hand2",
            "font": ("Segoe UI", 10, "bold"),
            "padx": 16,
            "pady": 8,
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)
        self._bg_default = accent
        self._bg_hover = hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event):
        self.configure(bg=self._bg_hover)

    def _on_leave(self, _event):
        self.configure(bg=self._bg_default)


class LoginFrame(tk.Frame):
    def __init__(self, master, on_login_success, **kwargs):
        super().__init__(master, **kwargs)
        self.on_login_success = on_login_success
        self.configure(bg=APP_CONFIG["bg_color"])
        self._build_ui()

    def _build_ui(self):
        bg = APP_CONFIG["bg_color"]
        card_bg = APP_CONFIG["card_bg"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = tk.Frame(self, bg=bg)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        card = tk.Frame(container, bg=card_bg, bd=0, highlightthickness=0)
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            card,
            text="Gestion d'université",
            bg=card_bg,
            fg=text_primary,
            font=("Segoe UI", 18, "bold"),
        )
        subtitle = tk.Label(
            card,
            text="Connectez-vous pour accéder au tableau de bord",
            bg=card_bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
        )

        user_label = tk.Label(
            card, text="Nom d'utilisateur", bg=card_bg, fg=text_primary, anchor="w"
        )
        self.username_entry = tk.Entry(
            card,
            bg="#020617",
            fg=text_primary,
            insertbackground=text_primary,
            relief="flat",
            font=("Segoe UI", 10),
            width=30,
        )

        pass_label = tk.Label(
            card, text="Mot de passe", bg=card_bg, fg=text_primary, anchor="w"
        )
        self.password_entry = tk.Entry(
            card,
            bg="#020617",
            fg=text_primary,
            insertbackground=text_primary,
            relief="flat",
            font=("Segoe UI", 10),
            show="*",
            width=30,
        )

        login_btn = ModernButton(
            card,
            text="Se connecter",
            command=self._handle_login,
        )

        for i in range(7):
            card.grid_rowconfigure(i, pad=6)
        card.grid_columnconfigure(0, pad=16)

        title.grid(row=0, column=0, sticky="w")
        subtitle.grid(row=1, column=0, sticky="w")
        user_label.grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.username_entry.grid(row=3, column=0, sticky="ew")
        pass_label.grid(row=4, column=0, sticky="w", pady=(8, 0))
        self.password_entry.grid(row=5, column=0, sticky="ew")
        login_btn.grid(row=6, column=0, sticky="ew", pady=(12, 4))

    def _handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Connexion", "Veuillez saisir vos identifiants.")
            return
        user = authenticate_user(username, password)
        if not user:
            messagebox.showerror("Connexion", "Identifiants invalides.")
            return
        self.on_login_success(user)


class DashboardFrame(tk.Frame):
    def __init__(self, master, on_logout, current_user, **kwargs):
        super().__init__(master, **kwargs)
        self.on_logout = on_logout
        self.current_user = current_user
        self.configure(bg=APP_CONFIG["bg_color"])
        self._build_ui()

    def _build_ui(self):
        bg = APP_CONFIG["bg_color"]
        card_bg = APP_CONFIG["card_bg"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]
        accent = APP_CONFIG["accent_color"]

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Sidebar
        sidebar = tk.Frame(self, bg="#020617", width=220)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        logo = tk.Label(
            sidebar,
            text="Université",
            bg="#020617",
            fg=text_primary,
            font=("Segoe UI", 16, "bold"),
        )
        logo.pack(pady=(20, 10), padx=16, anchor="w")

        section_label = tk.Label(
            sidebar,
            text="Navigation",
            bg="#020617",
            fg=text_secondary,
            font=("Segoe UI", 9),
        )
        section_label.pack(padx=16, pady=(0, 10), anchor="w")

        # Boutons de menu avec callbacks (squelettes pour l'instant)
        self.menu_buttons = {}

        def add_menu_button(text, command_key):
            btn = tk.Button(
                sidebar,
                text=text,
                bg="#020617",
                fg=text_primary,
                activebackground="#020617",
                activeforeground=accent,
                borderwidth=0,
                anchor="w",
                padx=16,
                font=("Segoe UI", 10),
                cursor="hand2",
                command=lambda key=command_key: self._on_menu_click(key),
            )
            btn.pack(fill="x", pady=2)
            self.menu_buttons[command_key] = btn

        add_menu_button("Tableau de bord", "dashboard")
        add_menu_button("Étudiants", "students")
        add_menu_button("Professeurs", "teachers")
        add_menu_button("Cours", "courses")
        add_menu_button("Inscriptions", "enrollments")
        add_menu_button("Notes", "grades")

        logout_btn = ModernButton(sidebar, text="Déconnexion", command=self.on_logout)
        logout_btn.pack(padx=16, pady=20, fill="x", side="bottom")

        # Contenu principal
        self.main = tk.Frame(self, bg=bg)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(1, weight=1)

        header = tk.Frame(self.main, bg=bg)
        header.grid(row=0, column=0, sticky="ew", pady=(16, 8), padx=16)
        header.columnconfigure(0, weight=1)

        title = tk.Label(
            header,
            text="Tableau de bord",
            bg=bg,
            fg=text_primary,
            font=("Segoe UI", 18, "bold"),
        )
        subtitle = tk.Label(
            header,
            text="Vue synthétique de l'université (étudiants, professeurs, cours, etc.)",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
        )
        title.grid(row=0, column=0, sticky="w")
        subtitle.grid(row=1, column=0, sticky="w")

        # Cartes de stats
        self.cards = tk.Frame(self.main, bg=bg)
        self.cards.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        for i in range(3):
            self.cards.columnconfigure(i, weight=1, uniform="card")

        def make_card(parent, title_text, value_text):
            card = tk.Frame(parent, bg=card_bg, bd=0, highlightthickness=0)
            title_label = tk.Label(
                card,
                text=title_text,
                bg=card_bg,
                fg=text_secondary,
                font=("Segoe UI", 9),
            )
            value_label = tk.Label(
                card,
                text=value_text,
                bg=card_bg,
                fg=text_primary,
                font=("Segoe UI", 18, "bold"),
            )
            title_label.pack(anchor="w", padx=16, pady=(14, 0))
            value_label.pack(anchor="w", padx=16, pady=(0, 14))
            # Store value_label to update it later
            card.value_label = value_label
            return card

        self.students_card = make_card(self.cards, "Étudiants", "-")
        self.teachers_card = make_card(self.cards, "Professeurs", "-")
        self.courses_card = make_card(self.cards, "Cours", "-")

        self.students_card.grid(row=0, column=0, padx=6, pady=4, sticky="nsew")
        self.teachers_card.grid(row=0, column=1, padx=6, pady=4, sticky="nsew")
        self.courses_card.grid(row=0, column=2, padx=6, pady=4, sticky="nsew")

        # Initial load
        self.refresh_dashboard_stats()

        # Placeholder pour d'autres écrans (liste étudiants, etc.)
        self.content_frame = tk.Frame(self.main, bg=bg)
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.main.rowconfigure(2, weight=1)

    def refresh_dashboard_stats(self):
        try:
            self.students_card.value_label.configure(text=str(get_student_count()))
            self.teachers_card.value_label.configure(text=str(get_teacher_count()))
            self.courses_card.value_label.configure(text=str(get_course_count()))
        except Exception:
            pass

    def _on_menu_click(self, key: str):
        for child in self.content_frame.winfo_children():
            child.destroy()
        
        # Always refresh stats when navigating
        self.refresh_dashboard_stats()

        if key == "students":
            self._show_students_view()
        elif key == "teachers":
            self._show_teachers_view()
        elif key == "courses":
            self._show_courses_view()
        elif key == "enrollments":
            self._show_enrollments_view()
        elif key == "grades":
            self._show_grades_view()
        else:
            self._show_placeholder_view(key)

    def _show_placeholder_view(self, key: str):
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        mapping = {
            "dashboard": "Vue tableau de bord (à enrichir avec de vraies statistiques).",
            "teachers": "Gestion des professeurs.",
            "courses": "Gestion des cours.",
            "enrollments": "Gestion des inscriptions.",
            "grades": "Gestion des notes.",
        }
        title = mapping.get(key, "Section en cours de construction.")

        label = tk.Label(
            self.content_frame,
            text=title,
            bg=APP_CONFIG["bg_color"],
            fg=text_primary,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        label.pack(fill="x")

        hint = tk.Label(
            self.content_frame,
            text="(Contenu détaillé à implémenter)",
            bg=APP_CONFIG["bg_color"],
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        hint.pack(fill="x")

    def _show_students_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(
            self.content_frame,
            text="Gestion des étudiants",
            bg=bg,
            fg=text_primary,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        header.pack(fill="x")

        sub = tk.Label(
            self.content_frame,
            text="Liste des étudiants (lecture seule pour l'instant).",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        # Refresh button
        refresh_btn = ModernButton(
            self.content_frame,
            text="Actualiser",
            command=self._show_students_view,
            font=("Segoe UI", 9),
            padx=10,
            pady=4
        )
        refresh_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=16)

        # Conteneur pour la table
        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))

        columns = ("matricule", "last_name", "first_name", "email", "phone")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )

        tree.heading("matricule", text="Matricule")
        tree.heading("last_name", text="Nom")
        tree.heading("first_name", text="Prénom")
        tree.heading("email", text="Email")
        tree.heading("phone", text="Téléphone")

        tree.column("matricule", width=100, anchor="w")
        tree.column("last_name", width=120, anchor="w")
        tree.column("first_name", width=120, anchor="w")
        tree.column("email", width=200, anchor="w")
        tree.column("phone", width=120, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Charger les données depuis MySQL
        try:
            students = get_all_students() or []
            for s in students:
                tree.insert(
                    "",
                    "end",
                    values=(
                        s["matricule"],
                        s["last_name"],
                        s["first_name"],
                        s["email"] or "",
                        s["phone"] or "",
                    ),
                )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de charger les étudiants depuis la base de données.\n{e}",
            )

#"""GESTION DES ETUDIANTS"""
    def _show_teachers_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(
            self.content_frame,
            text="Gestion des Enseignants",
            bg=bg,
            fg=text_primary,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        header.pack(fill="x")

        sub = tk.Label(
            self.content_frame,
            text="Liste des Enseignants (lecture seule pour l'instant).",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        # Refresh button
        refresh_btn = ModernButton(
            self.content_frame,
            text="Actualiser",
            command=self._show_teachers_view,
            font=("Segoe UI", 9),
            padx=10,
            pady=4
        )
        refresh_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=16)

        # Conteneur pour la table
        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))

        columns = ("last_name", "first_name", "email", "department" , "phone")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )

        tree.heading("last_name", text="Nom")
        tree.heading("first_name", text="Prénom")
        tree.heading("email", text="Email")
        tree.heading("department", text="Departement")
        tree.heading("phone", text="Téléphone")

        tree.column("last_name", width=100, anchor="w")
        tree.column("first_name", width=120, anchor="w")
        tree.column("email", width=120, anchor="w")
        tree.column("department", width=120, anchor="w")
        tree.column("phone", width=120, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Charger les données depuis MySQL
        try:
            teachers = get_all_teachers() or []
            for s in teachers:
                tree.insert(
                    "",
                    "end",
                    values=(
                        s["last_name"],
                        s["first_name"],
                        s["email"],
                        s["department"] or "",
                        s["phone"] or "",
                    ),
                )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de charger les enseignants depuis la base de données.\n{e}",
            )

    def _show_courses_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(
            self.content_frame,
            text="Gestion des Cours",
            bg=bg,
            fg=text_primary,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        header.pack(fill="x")

        sub = tk.Label(
            self.content_frame,
            text="Liste des cours disponibles.",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        # Refresh button
        refresh_btn = ModernButton(
            self.content_frame,
            text="Actualiser",
            command=self._show_courses_view,
            font=("Segoe UI", 9),
            padx=10,
            pady=4
        )
        refresh_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=16)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))

        columns = ("code", "name", "credits", "teacher_name")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )

        tree.heading("code", text="Code")
        tree.heading("name", text="Intitulé")
        tree.heading("credits", text="Crédits")
        tree.heading("teacher_name", text="Enseignant")

        tree.column("code", width=80, anchor="w")
        tree.column("name", width=200, anchor="w")
        tree.column("credits", width=60, anchor="center")
        tree.column("teacher_name", width=150, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        try:
            courses = get_all_courses() or []
            for c in courses:
                tree.insert(
                    "",
                    "end",
                    values=(
                        c["code"],
                        c["name"],
                        c["credits"],
                        c["teacher_name"] or "Non assigné",
                    ),
                )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de charger les cours.\n{e}",
            )

    def _show_enrollments_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(
            self.content_frame,
            text="Gestion des Inscriptions",
            bg=bg,
            fg=text_primary,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        header.pack(fill="x")

        sub = tk.Label(
            self.content_frame,
            text="Historique des inscriptions.",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        # Refresh button
        refresh_btn = ModernButton(
            self.content_frame,
            text="Actualiser",
            command=self._show_enrollments_view,
            font=("Segoe UI", 9),
            padx=10,
            pady=4
        )
        refresh_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=16)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))

        columns = ("academic_year", "semester", "matricule", "student_name", "course_name")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )

        tree.heading("academic_year", text="Année")
        tree.heading("semester", text="Semestre")
        tree.heading("matricule", text="Matricule")
        tree.heading("student_name", text="Étudiant")
        tree.heading("course_name", text="Cours")

        tree.column("academic_year", width=80, anchor="center")
        tree.column("semester", width=60, anchor="center")
        tree.column("matricule", width=100, anchor="w")
        tree.column("student_name", width=150, anchor="w")
        tree.column("course_name", width=200, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        try:
            items = get_all_enrollments() or []
            for item in items:
                tree.insert(
                    "",
                    "end",
                    values=(
                        item["academic_year"],
                        item["semester"],
                        item["matricule"],
                        item["student_name"],
                        item["course_name"],
                    ),
                )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de charger les inscriptions.\n{e}",
            )

    def _show_grades_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(
            self.content_frame,
            text="Gestion des Notes",
            bg=bg,
            fg=text_primary,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        header.pack(fill="x")

        sub = tk.Label(
            self.content_frame,
            text="Relevé des notes.",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        # Refresh button
        refresh_btn = ModernButton(
            self.content_frame,
            text="Actualiser",
            command=self._show_grades_view,
            font=("Segoe UI", 9),
            padx=10,
            pady=4
        )
        refresh_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=16)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))

        columns = ("academic_year", "semester", "student_name", "course_name", "grade")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )

        tree.heading("academic_year", text="Année")
        tree.heading("semester", text="Semestre")
        tree.heading("student_name", text="Étudiant")
        tree.heading("course_name", text="Cours")
        tree.heading("grade", text="Note")

        tree.column("academic_year", width=80, anchor="center")
        tree.column("semester", width=60, anchor="center")
        tree.column("student_name", width=150, anchor="w")
        tree.column("course_name", width=200, anchor="w")
        tree.column("grade", width=60, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        try:
            items = get_all_grades() or []
            for item in items:
                tree.insert(
                    "",
                    "end",
                    values=(
                        item["academic_year"],
                        item["semester"],
                        item["student_name"],
                        item["course_name"],
                        item["grade"] if item["grade"] is not None else "-",
                    ),
                )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de charger les notes.\n{e}",
            )



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_CONFIG["title"])
        self.geometry(APP_CONFIG["geometry"])
        self.minsize(APP_CONFIG["min_width"], APP_CONFIG["min_height"])
        self.configure(bg=APP_CONFIG["bg_color"])

        # Conteneur principal pour les frames
        self.container = tk.Frame(self, bg=APP_CONFIG["bg_color"])
        self.container.pack(fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.current_frame = None
        self.current_user = None
        self._show_login()

    def _clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def _show_login(self):
        self._clear_frame()
        self.current_frame = LoginFrame(self.container, on_login_success=self._on_login)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _show_dashboard(self):
        self._clear_frame()
        self.current_frame = DashboardFrame(
            self.container, on_logout=self._on_logout, current_user=self.current_user
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _on_login(self, user: dict):
        self.current_user = user
        self._show_dashboard()

    def _on_logout(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?"):
            self._show_login()


if __name__ == "__main__":
    app = App()
    app.mainloop()


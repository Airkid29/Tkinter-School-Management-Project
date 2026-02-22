import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog

from config import APP_CONFIG
from models_users import authenticate_user
from models_students import (
    get_all_students,
    get_student_count,
    get_student_by_id,
    create_student,
    update_student,
    delete_student,
)
from models_teachers import (
    get_all_teachers,
    get_teacher_count,
    get_teacher_by_id,
    create_teacher,
    update_teacher,
    delete_teacher,
)
from models_courses import (
    get_all_courses,
    get_course_count,
    get_course_by_id,
    create_course,
    update_course,
    delete_course,
)
from models_enrollments import (
    get_all_enrollments,
    create_enrollment,
    delete_enrollment,
    get_enrollment_count_for_year,
)
from models_grades import (
    get_all_grades,
    create_or_update_grade,
    delete_grade,
    get_average_grade,
)


def _export_treeview_to_csv(tree, filename=None):
    """Exporte le contenu d'un Treeview en CSV. Retourne le chemin du fichier ou None."""
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv"), ("Tous", "*.*")],
        initialfile=filename or "export.csv",
    )
    if not path:
        return None
    cols = [c for c in tree["columns"] if tree.column(c, "width") > 0]
    rows = []
    for item in tree.get_children(""):
        vals = tree.item(item)["values"]
        col_vals = [str(vals[tree["columns"].index(c)]) if c in tree["columns"] else "" for c in cols]
        rows.append(";".join(col_vals))
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(";".join(cols) + "\n")
            f.write("\n".join(rows))
        return path
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'exporter : {e}")
        return None


def _make_tree_sortable(tree, columns_with_types=None):
    """Rend un Treeview triable au clic sur les en-têtes. columns_with_types: {col_id: 'str'|'int'|'float'}."""
    columns_with_types = columns_with_types or {}
    sort_state = {}

    def _sort_by_column(col):
        reverse = sort_state.get(col, False)
        sort_state[col] = not reverse
        col_idx = tree["columns"].index(col)
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        conv = columns_with_types.get(col, "str")
        if conv == "int":
            data.sort(key=lambda t: (int(t[0]) if str(t[0]).lstrip("-").isdigit() else 0, t[1]), reverse=reverse)
        elif conv == "float":
            try:
                data.sort(key=lambda t: (float(t[0]) if t[0] and t[0] != "-" else -1, t[1]), reverse=reverse)
            except ValueError:
                data.sort(key=lambda t: (t[0], t[1]), reverse=reverse)
        else:
            data.sort(key=lambda t: (str(t[0]).lower(), t[1]), reverse=reverse)
        for i, (_, k) in enumerate(data):
            tree.move(k, "", i)

    for col in tree["columns"]:
        if tree.column(col, "width") > 0:
            tree.heading(col, command=lambda c=col: _sort_by_column(c))


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
        self.is_admin = (current_user or {}).get("role") == "admin"
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

        self.header_title = tk.Label(
            header,
            text="Tableau de bord",
            bg=bg,
            fg=text_primary,
            font=("Segoe UI", 18, "bold"),
        )
        self.header_subtitle = tk.Label(
            header,
            text="Vue synthétique de l'université (étudiants, professeurs, cours, etc.)",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
        )
        self.header_title.grid(row=0, column=0, sticky="w")
        self.header_subtitle.grid(row=1, column=0, sticky="w")

        # Cartes de stats
        self.cards = tk.Frame(self.main, bg=bg)
        self.cards.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        for i in range(3):
            self.cards.columnconfigure(i, weight=1, uniform="card")

        def make_card(parent, title_text, value_text):
            card = tk.Frame(parent, bg=card_bg, bd=0, highlightthickness=0)
            title_label = tk.Label(card, text=title_text, bg=card_bg, fg=text_secondary, font=("Segoe UI", 9))
            value_label = tk.Label(card, text=value_text, bg=card_bg, fg=text_primary, font=("Segoe UI", 18, "bold"))
            title_label.pack(anchor="w", padx=16, pady=(14, 0))
            value_label.pack(anchor="w", padx=16, pady=(0, 14))
            card.value_label = value_label
            return card

        self.students_card = make_card(self.cards, "Étudiants", "-")
        self.teachers_card = make_card(self.cards, "Professeurs", "-")
        self.courses_card = make_card(self.cards, "Cours", "-")
        self.enrollments_card = make_card(self.cards, "Inscriptions (2024-2025)", "-")
        self.avg_grade_card = make_card(self.cards, "Moyenne générale", "-")

        self.students_card.grid(row=0, column=0, padx=6, pady=4, sticky="nsew")
        self.teachers_card.grid(row=0, column=1, padx=6, pady=4, sticky="nsew")
        self.courses_card.grid(row=0, column=2, padx=6, pady=4, sticky="nsew")
        self.enrollments_card.grid(row=1, column=0, padx=6, pady=4, sticky="nsew")
        self.avg_grade_card.grid(row=1, column=1, padx=6, pady=4, sticky="nsew")

        # Initial load
        self.refresh_dashboard_stats()

        # Placeholder pour d'autres écrans (liste étudiants, etc.)
        self.content_frame = tk.Frame(self.main, bg=bg)
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.main.rowconfigure(2, weight=1)

        self._on_menu_click("dashboard")

    def refresh_dashboard_stats(self):
        try:
            self.students_card.value_label.configure(text=str(get_student_count()))
            self.teachers_card.value_label.configure(text=str(get_teacher_count()))
            self.courses_card.value_label.configure(text=str(get_course_count()))
            self.enrollments_card.value_label.configure(text=str(get_enrollment_count_for_year("2024-2025")))
            avg = get_average_grade()
            self.avg_grade_card.value_label.configure(text=str(avg) if avg is not None else "-")
        except Exception:
            pass

    _SECTION_TITLES = {
        "dashboard": ("Tableau de bord", "Vue synthétique de l'université"),
        "students": ("Gestion des étudiants", "Liste et gestion des étudiants"),
        "teachers": ("Gestion des enseignants", "Liste et gestion des professeurs"),
        "courses": ("Gestion des cours", "Liste et gestion des cours"),
        "enrollments": ("Gestion des inscriptions", "Inscriptions aux cours"),
        "grades": ("Gestion des notes", "Relevé des notes"),
    }

    def _update_header(self, key: str):
        title, sub = self._SECTION_TITLES.get(key, ("", ""))
        if title:
            self.header_title.configure(text=title)
            self.header_subtitle.configure(text=sub)

    def _update_menu_active(self, key: str):
        accent = APP_CONFIG["accent_color"]
        text_primary = APP_CONFIG["text_primary"]
        for k, btn in self.menu_buttons.items():
            btn.configure(fg=accent if k == key else text_primary, font=("Segoe UI", 10, "bold" if k == key else "normal"))

    def _on_menu_click(self, key: str):
        for child in self.content_frame.winfo_children():
            child.destroy()
        self._update_header(key)
        self._update_menu_active(key)
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
            text="Liste des étudiants." + (" Ajout, modification et suppression disponibles." if self.is_admin else " Lecture seule."),
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        # Barre d'outils
        toolbar = tk.Frame(self.content_frame, bg=bg)
        toolbar.pack(fill="x", pady=(8, 4))
        ModernButton(toolbar, text="Exporter CSV", command=lambda: _export_treeview_to_csv(tree, "etudiants.csv") and messagebox.showinfo("Export", "Export terminé."), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
        refresh_btn = ModernButton(toolbar, text="Actualiser", command=self._show_students_view, font=("Segoe UI", 9), padx=10, pady=4)
        refresh_btn.pack(side="right", padx=2)
        if self.is_admin:
            del_btn = ModernButton(toolbar, text="Supprimer", command=lambda: self._delete_student(tree), font=("Segoe UI", 9), padx=10, pady=4)
            del_btn.pack(side="right", padx=2)
            edit_btn = ModernButton(toolbar, text="Modifier", command=lambda: self._edit_student(tree), font=("Segoe UI", 9), padx=10, pady=4)
            edit_btn.pack(side="right", padx=2)
            add_btn = ModernButton(toolbar, text="Ajouter", command=lambda: self._add_student(tree), font=("Segoe UI", 9), padx=10, pady=4)
            add_btn.pack(side="right", padx=2)

        search_frame = tk.Frame(self.content_frame, bg=bg)
        search_frame.pack(fill="x", pady=(0, 4))
        tk.Label(search_frame, text="Rechercher:", bg=bg, fg=text_secondary, font=("Segoe UI", 9)).pack(side="left", padx=(0, 8))
        e_search = tk.Entry(search_frame, width=25, bg="#020617", fg=text_primary, insertbackground=text_primary)
        e_search.pack(side="left", padx=2)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))

        columns = ("id", "matricule", "last_name", "first_name", "email", "phone")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        tree.column("id", width=0, minwidth=0)
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

        try:
            for s in get_all_students() or []:
                tree.insert("", "end", values=(s["id"], s["matricule"], s["last_name"], s["first_name"], s["email"] or "", s["phone"] or ""))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les étudiants.\n{e}")
        _make_tree_sortable(tree, {"matricule": "str", "last_name": "str", "first_name": "str"})

        def _on_search_change(*_):
            q = e_search.get().strip().lower()
            for item in tree.get_children(""):
                tree.delete(item)
            for s in get_all_students() or []:
                row_text = f"{s.get('matricule','')} {s.get('last_name','')} {s.get('first_name','')} {s.get('email','')} {s.get('phone','')}".lower()
                if not q or q in row_text:
                    tree.insert("", "end", values=(s["id"], s["matricule"], s["last_name"], s["first_name"], s["email"] or "", s["phone"] or ""))

        e_search.bind("<KeyRelease>", _on_search_change)

    def _add_student(self, tree):
        d = tk.Toplevel(self)
        d.title("Ajouter un étudiant")
        d.geometry("400x220")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Matricule *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        e_mat = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_mat.grid(row=0, column=1, padx=10, pady=4)
        tk.Label(d, text="Nom *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_nom = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_nom.grid(row=1, column=1, padx=10, pady=4)
        tk.Label(d, text="Prénom *", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        e_prenom = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_prenom.grid(row=2, column=1, padx=10, pady=4)
        tk.Label(d, text="Email", bg=bg, fg=fg).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        e_email = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_email.grid(row=3, column=1, padx=10, pady=4)
        tk.Label(d, text="Téléphone", bg=bg, fg=fg).grid(row=4, column=0, sticky="w", padx=10, pady=4)
        e_phone = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_phone.grid(row=4, column=1, padx=10, pady=4)

        def save():
            if not e_mat.get().strip() or not e_nom.get().strip() or not e_prenom.get().strip():
                messagebox.showwarning("Validation", "Matricule, nom et prénom sont obligatoires.", parent=d)
                return
            try:
                create_student(e_mat.get(), e_prenom.get(), e_nom.get(), e_email.get(), e_phone.get())
                messagebox.showinfo("Succès", "Étudiant ajouté.", parent=d)
                d.destroy()
                self.refresh_dashboard_stats()
                self._show_students_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        tk.Frame(d, bg=bg).grid(row=5, column=0, columnspan=2, pady=10)
        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=6, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=6, column=1, padx=5)

    def _edit_student(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un étudiant.")
            return
        vals = tree.item(sel[0])["values"]
        sid = vals[0]
        s = get_student_by_id(sid)
        if not s:
            return
        d = tk.Toplevel(self)
        d.title("Modifier l'étudiant")
        d.geometry("400x220")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Matricule *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        e_mat = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_mat.insert(0, s["matricule"])
        e_mat.grid(row=0, column=1, padx=10, pady=4)
        tk.Label(d, text="Nom *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_nom = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_nom.insert(0, s["last_name"] or "")
        e_nom.grid(row=1, column=1, padx=10, pady=4)
        tk.Label(d, text="Prénom *", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        e_prenom = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_prenom.insert(0, s["first_name"] or "")
        e_prenom.grid(row=2, column=1, padx=10, pady=4)
        tk.Label(d, text="Email", bg=bg, fg=fg).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        e_email = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_email.insert(0, s["email"] or "")
        e_email.grid(row=3, column=1, padx=10, pady=4)
        tk.Label(d, text="Téléphone", bg=bg, fg=fg).grid(row=4, column=0, sticky="w", padx=10, pady=4)
        e_phone = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_phone.insert(0, s["phone"] or "")
        e_phone.grid(row=4, column=1, padx=10, pady=4)

        def save():
            if not e_mat.get().strip() or not e_nom.get().strip() or not e_prenom.get().strip():
                messagebox.showwarning("Validation", "Matricule, nom et prénom sont obligatoires.", parent=d)
                return
            try:
                update_student(sid, e_mat.get(), e_prenom.get(), e_nom.get(), e_email.get(), e_phone.get())
                messagebox.showinfo("Succès", "Étudiant modifié.", parent=d)
                d.destroy()
                self.refresh_dashboard_stats()
                self._show_students_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=6, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=6, column=1, padx=5)

    def _delete_student(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un étudiant.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cet étudiant ?"):
            return
        try:
            delete_student(tree.item(sel[0])["values"][0])
            messagebox.showinfo("Succès", "Étudiant supprimé.")
            self.refresh_dashboard_stats()
            self._show_students_view()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))
    def _show_teachers_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(self.content_frame, text="Gestion des enseignants", bg=bg, fg=text_primary, font=("Segoe UI", 12, "bold"), anchor="w")
        header.pack(fill="x")
        sub = tk.Label(
            self.content_frame,
            text="Liste des enseignants." + (" CRUD disponible." if self.is_admin else " Lecture seule."),
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        toolbar = tk.Frame(self.content_frame, bg=bg)
        toolbar.pack(fill="x", pady=(8, 4))
        ModernButton(toolbar, text="Actualiser", command=self._show_teachers_view, font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
        if self.is_admin:
            ModernButton(toolbar, text="Supprimer", command=lambda: self._delete_teacher(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
            ModernButton(toolbar, text="Modifier", command=lambda: self._edit_teacher(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
            ModernButton(toolbar, text="Ajouter", command=lambda: self._add_teacher(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))
        columns = ("id", "last_name", "first_name", "email", "department", "phone")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        tree.column("id", width=0, minwidth=0)
        tree.heading("last_name", text="Nom")
        tree.heading("first_name", text="Prénom")
        tree.heading("email", text="Email")
        tree.heading("department", text="Département")
        tree.heading("phone", text="Téléphone")
        tree.column("last_name", width=100, anchor="w")
        tree.column("first_name", width=120, anchor="w")
        tree.column("email", width=150, anchor="w")
        tree.column("department", width=120, anchor="w")
        tree.column("phone", width=120, anchor="w")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        try:
            for t in get_all_teachers() or []:
                tree.insert("", "end", values=(t["id"], t["last_name"], t["first_name"], t["email"] or "", t["department"] or "", t["phone"] or ""))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les enseignants.\n{e}")
        _make_tree_sortable(tree)

    def _add_teacher(self, tree):
        d = tk.Toplevel(self)
        d.title("Ajouter un enseignant")
        d.geometry("400x260")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Nom *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        e_nom = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_nom.grid(row=0, column=1, padx=10, pady=4)
        tk.Label(d, text="Prénom *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_prenom = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_prenom.grid(row=1, column=1, padx=10, pady=4)
        tk.Label(d, text="Email", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        e_email = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_email.grid(row=2, column=1, padx=10, pady=4)
        tk.Label(d, text="Téléphone", bg=bg, fg=fg).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        e_phone = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_phone.grid(row=3, column=1, padx=10, pady=4)
        tk.Label(d, text="Département", bg=bg, fg=fg).grid(row=4, column=0, sticky="w", padx=10, pady=4)
        e_dept = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_dept.grid(row=4, column=1, padx=10, pady=4)

        def save():
            if not e_nom.get().strip() or not e_prenom.get().strip():
                messagebox.showwarning("Validation", "Nom et prénom sont obligatoires.", parent=d)
                return
            try:
                create_teacher(e_prenom.get(), e_nom.get(), e_email.get(), e_phone.get(), e_dept.get())
                messagebox.showinfo("Succès", "Enseignant ajouté.", parent=d)
                d.destroy()
                self.refresh_dashboard_stats()
                self._show_teachers_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=6, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=6, column=1, padx=5)

    def _edit_teacher(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un enseignant.")
            return
        t = get_teacher_by_id(tree.item(sel[0])["values"][0])
        if not t:
            return
        d = tk.Toplevel(self)
        d.title("Modifier l'enseignant")
        d.geometry("400x260")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Nom *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        e_nom = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_nom.insert(0, t["last_name"] or "")
        e_nom.grid(row=0, column=1, padx=10, pady=4)
        tk.Label(d, text="Prénom *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_prenom = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_prenom.insert(0, t["first_name"] or "")
        e_prenom.grid(row=1, column=1, padx=10, pady=4)
        tk.Label(d, text="Email", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        e_email = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_email.insert(0, t["email"] or "")
        e_email.grid(row=2, column=1, padx=10, pady=4)
        tk.Label(d, text="Téléphone", bg=bg, fg=fg).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        e_phone = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_phone.insert(0, t["phone"] or "")
        e_phone.grid(row=3, column=1, padx=10, pady=4)
        tk.Label(d, text="Département", bg=bg, fg=fg).grid(row=4, column=0, sticky="w", padx=10, pady=4)
        e_dept = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_dept.insert(0, t["department"] or "")
        e_dept.grid(row=4, column=1, padx=10, pady=4)

        def save():
            if not e_nom.get().strip() or not e_prenom.get().strip():
                messagebox.showwarning("Validation", "Nom et prénom sont obligatoires.", parent=d)
                return
            try:
                update_teacher(t["id"], e_prenom.get(), e_nom.get(), e_email.get(), e_phone.get(), e_dept.get())
                messagebox.showinfo("Succès", "Enseignant modifié.", parent=d)
                d.destroy()
                self.refresh_dashboard_stats()
                self._show_teachers_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=6, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=6, column=1, padx=5)

    def _delete_teacher(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un enseignant.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cet enseignant ?"):
            return
        try:
            delete_teacher(tree.item(sel[0])["values"][0])
            messagebox.showinfo("Succès", "Enseignant supprimé.")
            self.refresh_dashboard_stats()
            self._show_teachers_view()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))

    def _show_courses_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(self.content_frame, text="Gestion des cours", bg=bg, fg=text_primary, font=("Segoe UI", 12, "bold"), anchor="w")
        header.pack(fill="x")
        sub = tk.Label(
            self.content_frame,
            text="Liste des cours." + (" CRUD disponible." if self.is_admin else " Lecture seule."),
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        toolbar = tk.Frame(self.content_frame, bg=bg)
        toolbar.pack(fill="x", pady=(8, 4))
        ModernButton(toolbar, text="Actualiser", command=self._show_courses_view, font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
        if self.is_admin:
            ModernButton(toolbar, text="Supprimer", command=lambda: self._delete_course(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
            ModernButton(toolbar, text="Modifier", command=lambda: self._edit_course(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
            ModernButton(toolbar, text="Ajouter", command=lambda: self._add_course(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)

        search_frame_c = tk.Frame(self.content_frame, bg=bg)
        search_frame_c.pack(fill="x", pady=(0, 4))
        tk.Label(search_frame_c, text="Rechercher:", bg=bg, fg=text_secondary, font=("Segoe UI", 9)).pack(side="left", padx=(0, 8))
        e_search_c = tk.Entry(search_frame_c, width=25, bg="#020617", fg=text_primary, insertbackground=text_primary)
        e_search_c.pack(side="left", padx=2)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))
        columns = ("id", "code", "name", "credits", "teacher_name")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        tree.column("id", width=0, minwidth=0)
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
            for c in get_all_courses() or []:
                tree.insert("", "end", values=(c["id"], c["code"], c["name"], c["credits"], c["teacher_name"] or "Non assigné"))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les cours.\n{e}")
        _make_tree_sortable(tree, {"credits": "int"})

        def _on_search_courses(*_):
            q = e_search_c.get().strip().lower()
            for item in tree.get_children(""):
                tree.delete(item)
            for c in get_all_courses() or []:
                row_text = f"{c.get('code','')} {c.get('name','')} {c.get('teacher_name','')}".lower()
                if not q or q in row_text:
                    tree.insert("", "end", values=(c["id"], c["code"], c["name"], c["credits"], c["teacher_name"] or "Non assigné"))

        e_search_c.bind("<KeyRelease>", _on_search_courses)

    def _add_course(self, tree):
        teachers = get_all_teachers() or []
        teacher_choices = ["-- Aucun --"] + [f"{t['last_name']} {t['first_name']} (id:{t['id']})" for t in teachers]

        d = tk.Toplevel(self)
        d.title("Ajouter un cours")
        d.geometry("450x200")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Code *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        e_code = tk.Entry(d, width=25, bg="#020617", fg=fg, insertbackground=fg)
        e_code.grid(row=0, column=1, padx=10, pady=4)
        tk.Label(d, text="Intitulé *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_name = tk.Entry(d, width=25, bg="#020617", fg=fg, insertbackground=fg)
        e_name.grid(row=1, column=1, padx=10, pady=4)
        tk.Label(d, text="Crédits *", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        e_credits = tk.Entry(d, width=10, bg="#020617", fg=fg, insertbackground=fg)
        e_credits.insert(0, "3")
        e_credits.grid(row=2, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Enseignant", bg=bg, fg=fg).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        cb_teacher = ttk.Combobox(d, values=teacher_choices, state="readonly", width=28)
        cb_teacher.current(0)
        cb_teacher.grid(row=3, column=1, padx=10, pady=4, sticky="w")

        def save():
            if not e_code.get().strip() or not e_name.get().strip():
                messagebox.showwarning("Validation", "Code et intitulé sont obligatoires.", parent=d)
                return
            try:
                cred = int(e_credits.get())
            except ValueError:
                messagebox.showwarning("Validation", "Crédits doit être un nombre.", parent=d)
                return
            tid = None
            if cb_teacher.current() > 0:
                sel = cb_teacher.get()
                tid = int(sel.split("id:")[1].rstrip(")"))
            try:
                create_course(e_code.get(), e_name.get(), cred, tid)
                messagebox.showinfo("Succès", "Cours ajouté.", parent=d)
                d.destroy()
                self.refresh_dashboard_stats()
                self._show_courses_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=1, padx=5)

    def _edit_course(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un cours.")
            return
        c = get_course_by_id(tree.item(sel[0])["values"][0])
        if not c:
            return
        teachers = get_all_teachers() or []
        teacher_choices = ["-- Aucun --"] + [f"{t['last_name']} {t['first_name']} (id:{t['id']})" for t in teachers]
        d = tk.Toplevel(self)
        d.title("Modifier le cours")
        d.geometry("450x200")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Code *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        e_code = tk.Entry(d, width=25, bg="#020617", fg=fg, insertbackground=fg)
        e_code.insert(0, c["code"])
        e_code.grid(row=0, column=1, padx=10, pady=4)
        tk.Label(d, text="Intitulé *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_name = tk.Entry(d, width=25, bg="#020617", fg=fg, insertbackground=fg)
        e_name.insert(0, c["name"])
        e_name.grid(row=1, column=1, padx=10, pady=4)
        tk.Label(d, text="Crédits *", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        e_credits = tk.Entry(d, width=10, bg="#020617", fg=fg, insertbackground=fg)
        e_credits.insert(0, str(c["credits"]))
        e_credits.grid(row=2, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Enseignant", bg=bg, fg=fg).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        cb_teacher = ttk.Combobox(d, values=teacher_choices, state="readonly", width=28)
        idx = 0
        if c.get("teacher_id"):
            for i, ch in enumerate(teacher_choices):
                if ch.endswith(f"id:{c['teacher_id']})"):
                    idx = i
                    break
        cb_teacher.current(idx)
        cb_teacher.grid(row=3, column=1, padx=10, pady=4, sticky="w")

        def save():
            if not e_code.get().strip() or not e_name.get().strip():
                messagebox.showwarning("Validation", "Code et intitulé sont obligatoires.", parent=d)
                return
            try:
                cred = int(e_credits.get())
            except ValueError:
                messagebox.showwarning("Validation", "Crédits doit être un nombre.", parent=d)
                return
            tid = None
            if cb_teacher.current() > 0:
                sel = cb_teacher.get()
                tid = int(sel.split("id:")[1].rstrip(")"))
            try:
                update_course(c["id"], e_code.get(), e_name.get(), cred, tid)
                messagebox.showinfo("Succès", "Cours modifié.", parent=d)
                d.destroy()
                self.refresh_dashboard_stats()
                self._show_courses_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=1, padx=5)

    def _delete_course(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un cours.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ce cours ?"):
            return
        try:
            delete_course(tree.item(sel[0])["values"][0])
            messagebox.showinfo("Succès", "Cours supprimé.")
            self.refresh_dashboard_stats()
            self._show_courses_view()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))

    def _show_enrollments_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(self.content_frame, text="Gestion des inscriptions", bg=bg, fg=text_primary, font=("Segoe UI", 12, "bold"), anchor="w")
        header.pack(fill="x")
        sub = tk.Label(
            self.content_frame,
            text="Historique des inscriptions." + (" Ajout et suppression disponibles." if self.is_admin else " Lecture seule."),
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        toolbar = tk.Frame(self.content_frame, bg=bg)
        toolbar.pack(fill="x", pady=(8, 4))
        ModernButton(toolbar, text="Actualiser", command=self._show_enrollments_view, font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
        if self.is_admin:
            ModernButton(toolbar, text="Supprimer", command=lambda: self._delete_enrollment(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
            ModernButton(toolbar, text="Ajouter", command=lambda: self._add_enrollment(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))
        columns = ("id", "academic_year", "semester", "matricule", "student_name", "course_name")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        tree.column("id", width=0, minwidth=0)
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
            for item in get_all_enrollments() or []:
                tree.insert("", "end", values=(item["id"], item["academic_year"], item["semester"], item["matricule"], item["student_name"], item["course_name"]))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les inscriptions.\n{e}")
        _make_tree_sortable(tree)

    def _add_enrollment(self, tree):
        students = get_all_students() or []
        courses = get_all_courses() or []
        student_choices = [f"{s['matricule']} - {s['last_name']} {s['first_name']}" for s in students]
        course_choices = [f"{c['code']} - {c['name']}" for c in courses]
        if not students or not courses:
            messagebox.showwarning("Données", "Aucun étudiant ou cours disponible. Créez-en d'abord.")
            return

        d = tk.Toplevel(self)
        d.title("Ajouter une inscription")
        d.geometry("450x220")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Étudiant *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        cb_student = ttk.Combobox(d, values=student_choices, state="readonly", width=35)
        cb_student.current(0)
        cb_student.grid(row=0, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Cours *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        cb_course = ttk.Combobox(d, values=course_choices, state="readonly", width=35)
        cb_course.current(0)
        cb_course.grid(row=1, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Année académique *", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        e_year = tk.Entry(d, width=15, bg="#020617", fg=fg, insertbackground=fg)
        e_year.insert(0, "2024-2025")
        e_year.grid(row=2, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Semestre *", bg=bg, fg=fg).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        cb_sem = ttk.Combobox(d, values=["S1", "S2"], state="readonly", width=10)
        cb_sem.current(0)
        cb_sem.grid(row=3, column=1, padx=10, pady=4, sticky="w")

        def save():
            sid = students[cb_student.current()]["id"]
            cid = courses[cb_course.current()]["id"]
            year = e_year.get().strip()
            sem = cb_sem.get()
            if not year:
                messagebox.showwarning("Validation", "Année académique obligatoire.", parent=d)
                return
            try:
                create_enrollment(sid, cid, year, sem)
                messagebox.showinfo("Succès", "Inscription ajoutée.", parent=d)
                d.destroy()
                self._show_enrollments_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=1, padx=5)

    def _delete_enrollment(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une inscription.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cette inscription ?"):
            return
        try:
            delete_enrollment(tree.item(sel[0])["values"][0])
            messagebox.showinfo("Succès", "Inscription supprimée.")
            self._show_enrollments_view()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))

    def _show_grades_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(self.content_frame, text="Gestion des notes", bg=bg, fg=text_primary, font=("Segoe UI", 12, "bold"), anchor="w")
        header.pack(fill="x")
        sub = tk.Label(
            self.content_frame,
            text="Relevé des notes." + (" Ajout, modification et suppression disponibles." if self.is_admin else " Lecture seule."),
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        toolbar = tk.Frame(self.content_frame, bg=bg)
        toolbar.pack(fill="x", pady=(8, 4))
        ModernButton(toolbar, text="Exporter CSV", command=lambda: _export_treeview_to_csv(tree, "notes.csv") and messagebox.showinfo("Export", "Export terminé."), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
        ModernButton(toolbar, text="Actualiser", command=self._show_grades_view, font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
        if self.is_admin:
            ModernButton(toolbar, text="Supprimer", command=lambda: self._delete_grade(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
            ModernButton(toolbar, text="Modifier / Ajouter", command=lambda: self._edit_or_add_grade(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))
        columns = ("id", "enrollment_id", "academic_year", "semester", "student_name", "course_name", "grade")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        tree.column("id", width=0, minwidth=0)
        tree.column("enrollment_id", width=0, minwidth=0)
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
        if self.is_admin:
            tree.bind("<Double-1>", lambda e: self._edit_or_add_grade(tree))

        try:
            for item in get_all_grades() or []:
                tree.insert(
                    "",
                    "end",
                    values=(
                        item["id"],
                        item["enrollment_id"],
                        item["academic_year"],
                        item["semester"],
                        item["student_name"],
                        item["course_name"],
                        item["grade"] if item["grade"] is not None else "-",
                    ),
                )
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les notes.\n{e}")
        _make_tree_sortable(tree, {"grade": "float"})

    def _edit_or_add_grade(self, tree):
        enrollments = get_all_enrollments() or []
        if not enrollments:
            messagebox.showwarning("Données", "Aucune inscription. Créez des inscriptions d'abord.")
            return
        enrollment_choices = [f"{e['matricule']} - {e['student_name']} | {e['course_name']} ({e['academic_year']} {e['semester']})" for e in enrollments]

        enrollment_id = None
        initial_grade = ""
        sel = tree.selection()
        if sel:
            vals = tree.item(sel[0])["values"]
            enrollment_id = vals[1]
            initial_grade = str(vals[6]) if vals[6] != "-" else ""

        d = tk.Toplevel(self)
        d.title("Modifier / Ajouter une note")
        d.geometry("500x180")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Inscription", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        cb_enr = ttk.Combobox(d, values=enrollment_choices, state="readonly", width=50)
        if enrollment_id:
            for i, e in enumerate(enrollments):
                if e["id"] == enrollment_id:
                    cb_enr.current(i)
                    break
        else:
            cb_enr.current(0)
        cb_enr.grid(row=0, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Note (0-20)", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_grade = tk.Entry(d, width=10, bg="#020617", fg=fg, insertbackground=fg)
        e_grade.insert(0, initial_grade)
        e_grade.grid(row=1, column=1, padx=10, pady=4, sticky="w")

        def save():
            eid = enrollments[cb_enr.current()]["id"]
            g = e_grade.get().strip()
            try:
                grade_val = float(g) if g else None
                if grade_val is not None and (grade_val < 0 or grade_val > 20):
                    messagebox.showwarning("Validation", "La note doit être entre 0 et 20.", parent=d)
                    return
            except ValueError:
                messagebox.showwarning("Validation", "La note doit être un nombre.", parent=d)
                return
            try:
                create_or_update_grade(eid, grade_val)
                messagebox.showinfo("Succès", "Note enregistrée.", parent=d)
                d.destroy()
                self._show_grades_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=3, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=3, column=1, padx=5)

    def _delete_grade(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une note.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cette note ?"):
            return
        try:
            delete_grade(tree.item(sel[0])["values"][0])
            messagebox.showinfo("Succès", "Note supprimée.")
            self._show_grades_view()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))



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


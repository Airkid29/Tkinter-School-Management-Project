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
from models_classes import (
    get_all_classes,
    get_class_count,
    get_class_by_id,
    get_courses_for_class,
    create_class,
    update_class,
    delete_class,
    set_class_courses,
)
from models_enrollments import (
    get_all_enrollments,
    create_enrollment,
    delete_enrollment,
    get_enrollment_count_for_year,
    get_enrollments_per_year,
)
from models_grades import (
    get_all_grades,
    create_or_update_grade,
    delete_grade,
    get_average_grade,
    get_grade_distribution,
    get_bulletin_data,
    get_student_periods,
)
from models_archives import (
    get_available_academic_years,
    get_enrollments_by_year,
    get_grades_by_year,
    get_students_by_year,
    get_courses_by_year,
    get_teachers_by_year,
    get_archive_count,
)
from init_db import verify_tables


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
        add_menu_button("Classes", "classes")
        add_menu_button("Inscriptions", "enrollments")
        add_menu_button("Notes", "grades")
        add_menu_button("Bulletins", "bulletins")
        add_menu_button("Archives", "archives")

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
        for i in range(4):
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
        self.classes_card = make_card(self.cards, "Classes", "-")
        self.enrollments_card = make_card(self.cards, "Inscriptions (2024-2025)", "-")
        self.avg_grade_card = make_card(self.cards, "Moyenne générale", "-")
        self.archives_card = make_card(self.cards, "Archives", "-")

        self.students_card.grid(row=0, column=0, padx=6, pady=4, sticky="nsew")
        self.teachers_card.grid(row=0, column=1, padx=6, pady=4, sticky="nsew")
        self.courses_card.grid(row=0, column=2, padx=6, pady=4, sticky="nsew")
        self.classes_card.grid(row=0, column=3, padx=6, pady=4, sticky="nsew")
        self.enrollments_card.grid(row=1, column=0, padx=6, pady=4, sticky="nsew")
        self.avg_grade_card.grid(row=1, column=1, padx=6, pady=4, sticky="nsew")
        self.archives_card.grid(row=1, column=2, padx=6, pady=4, sticky="nsew")

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
            self.classes_card.value_label.configure(text=str(get_class_count()))
            self.enrollments_card.value_label.configure(text=str(get_enrollment_count_for_year("2024-2025")))
            avg = get_average_grade()
            self.avg_grade_card.value_label.configure(text=str(avg) if avg is not None else "-")
            self.archives_card.value_label.configure(text=str(get_archive_count()))
        except Exception:
            pass

    _SECTION_TITLES = {
        "dashboard": ("Tableau de bord", "Vue synthétique de l'université"),
        "students": ("Gestion des étudiants", "Liste et gestion des étudiants"),
        "teachers": ("Gestion des enseignants", "Liste et gestion des professeurs"),
        "courses": ("Gestion des cours", "Liste et gestion des cours"),
        "classes": ("Gestion des classes", "Classes et cours attribués"),
        "enrollments": ("Gestion des inscriptions", "Inscription des étudiants aux classes"),
        "grades": ("Gestion des notes", "Notes par cours (étudiant + classe)"),
        "bulletins": ("Bulletins", "Consulter et imprimer les bulletins des étudiants"),
        "archives": ("Archives", "Consultation des données sur les 10 dernières années"),
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

        if key == "dashboard":
            self._show_dashboard_charts()
        elif key == "students":
            self._show_students_view()
        elif key == "teachers":
            self._show_teachers_view()
        elif key == "courses":
            self._show_courses_view()
        elif key == "classes":
            self._show_classes_view()
        elif key == "enrollments":
            self._show_enrollments_view()
        elif key == "grades":
            self._show_grades_view()
        elif key == "bulletins":
            self._show_bulletins_view()
        elif key == "archives":
            self._show_archives_view()
        else:
            self._show_placeholder_view(key)

    def _show_dashboard_charts(self):
        """Affiche le tableau de bord avec graphiques (inscriptions par année, répartition des notes)."""
        bg = APP_CONFIG["bg_color"]
        card_bg = APP_CONFIG["card_bg"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            tk.Label(
                self.content_frame,
                text="Graphiques indisponibles : installez matplotlib (pip install matplotlib).",
                bg=bg,
                fg=text_secondary,
                font=("Segoe UI", 10),
            ).pack(pady=20)
            return

        charts_frame = tk.Frame(self.content_frame, bg=bg)
        charts_frame.pack(fill="both", expand=True)

        fig = Figure(figsize=(10, 4), facecolor=bg, edgecolor="none")
        fig.patch.set_facecolor(bg)

        # Couleurs assorties au thème
        accent = APP_CONFIG["accent_color"]
        bars_color = "#3b82f6"
        pie_colors = ["#ef4444", "#f59e0b", "#22c55e", "#2563eb"]

        # 1) Inscriptions par année (barres)
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(card_bg)
        ax1.tick_params(colors=text_secondary, labelsize=8)
        ax1.spines["bottom"].set_color(text_secondary)
        ax1.spines["left"].set_color(text_secondary)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.xaxis.label.set_color(text_primary)
        ax1.yaxis.label.set_color(text_primary)
        ax1.title.set_color(text_primary)

        years, counts = get_enrollments_per_year()
        if years and any(c > 0 for c in counts):
            bars = ax1.bar(range(len(years)), counts, color=bars_color, edgecolor="none")
            ax1.set_xticks(range(len(years)))
            ax1.set_xticklabels(years, rotation=35, ha="right")
            ax1.set_ylabel("Nombre d'inscriptions", fontsize=9)
            ax1.set_title("Inscriptions par année académique", fontsize=11)
        else:
            ax1.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", color=text_secondary, fontsize=11)
            ax1.set_title("Inscriptions par année", fontsize=11)

        # 2) Répartition des notes (camembert)
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(card_bg)
        ax2.tick_params(colors=text_secondary, labelsize=8)

        labels, values = get_grade_distribution()
        if sum(values) > 0:
            wedges, texts, autotexts = ax2.pie(
                values,
                labels=labels,
                autopct="%1.0f%%",
                colors=pie_colors,
                startangle=90,
                textprops={"color": text_primary, "fontsize": 9},
            )
            for at in autotexts:
                at.set_color("white")
                at.set_fontsize(8)
            ax2.set_title("Répartition des notes (sur 20)", fontsize=11, color=text_primary)
        else:
            ax2.text(0.5, 0.5, "Aucune note enregistrée", ha="center", va="center", color=text_secondary, fontsize=10)
            ax2.set_title("Répartition des notes", fontsize=11, color=text_primary)

        fig.tight_layout(pad=2)
        canvas = FigureCanvasTkAgg(fig, master=charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Bouton actualiser
        btn_frame = tk.Frame(self.content_frame, bg=bg)
        btn_frame.pack(fill="x", pady=(8, 0))
        ModernButton(
            btn_frame,
            text="Actualiser les graphiques",
            command=lambda: (self._on_menu_click("dashboard")),
            font=("Segoe UI", 9),
            padx=10,
            pady=4,
        ).pack(side="left")

    def _show_placeholder_view(self, key: str):
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        mapping = {
            "dashboard": "Vue tableau de bord.",
            "teachers": "Gestion des professeurs.",
            "courses": "Gestion des cours.",
            "enrollments": "Gestion des inscriptions.",
            "grades": "Gestion des notes.",
            "archives": "Gestion des archives.",
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

    def _show_classes_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(self.content_frame, text="Gestion des classes", bg=bg, fg=text_primary, font=("Segoe UI", 12, "bold"), anchor="w")
        header.pack(fill="x")
        sub = tk.Label(
            self.content_frame,
            text="Les cours sont attribués aux classes. Inscrivez les étudiants aux classes." + (" CRUD disponible." if self.is_admin else " Lecture seule."),
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        toolbar = tk.Frame(self.content_frame, bg=bg)
        toolbar.pack(fill="x", pady=(8, 4))
        ModernButton(toolbar, text="Actualiser", command=self._show_classes_view, font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
        if self.is_admin:
            ModernButton(toolbar, text="Supprimer", command=lambda: self._delete_class(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
            ModernButton(toolbar, text="Modifier", command=lambda: self._edit_class(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)
            ModernButton(toolbar, text="Ajouter", command=lambda: self._add_class(tree), font=("Segoe UI", 9), padx=10, pady=4).pack(side="right", padx=2)

        table_frame = tk.Frame(self.content_frame, bg=bg)
        table_frame.pack(fill="both", expand=True, pady=(8, 0))
        columns = ("id", "name", "academic_year", "semester", "courses_count")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        tree.column("id", width=0, minwidth=0)
        tree.heading("name", text="Classe")
        tree.heading("academic_year", text="Année")
        tree.heading("semester", text="Semestre")
        tree.heading("courses_count", text="Nb cours")
        tree.column("name", width=180, anchor="w")
        tree.column("academic_year", width=100, anchor="center")
        tree.column("semester", width=70, anchor="center")
        tree.column("courses_count", width=80, anchor="center")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        try:
            for cl in get_all_classes() or []:
                courses = get_courses_for_class(cl["id"]) or []
                tree.insert("", "end", values=(cl["id"], cl["name"], cl["academic_year"], cl["semester"], len(courses)))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les classes.\n{e}")
        _make_tree_sortable(tree, {"courses_count": "int"})

    def _add_class(self, tree):
        d = tk.Toplevel(self)
        d.title("Ajouter une classe")
        d.geometry("480x280")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Nom de la classe *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        e_name = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_name.grid(row=0, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Année académique *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_year = tk.Entry(d, width=15, bg="#020617", fg=fg, insertbackground=fg)
        e_year.insert(0, "2024-2025")
        e_year.grid(row=1, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Semestre *", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        cb_sem = ttk.Combobox(d, values=["S1", "S2"], state="readonly", width=10)
        cb_sem.current(0)
        cb_sem.grid(row=2, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Cours attribués à la classe", bg=bg, fg=fg).grid(row=3, column=0, sticky="nw", padx=10, pady=4)
        courses = get_all_courses() or []
        list_frame = tk.Frame(d, bg=bg)
        list_frame.grid(row=3, column=1, padx=10, pady=4, sticky="nsew")
        course_vars = []
        for c in courses:
            v = tk.BooleanVar(value=False)
            course_vars.append((c["id"], v))
            tk.Checkbutton(list_frame, text=f"{c['code']} - {c['name']}", variable=v, bg=bg, fg=fg, selectcolor=bg, activebackground=bg, activeforeground=fg).pack(anchor="w")
        if not courses:
            tk.Label(list_frame, text="Aucun cours. Créez des cours d'abord.", bg=bg, fg=fg).pack(anchor="w")

        def save():
            if not e_name.get().strip() or not e_year.get().strip():
                messagebox.showwarning("Validation", "Nom et année obligatoires.", parent=d)
                return
            try:
                new_id = create_class(e_name.get(), e_year.get(), cb_sem.get())
                if new_id and courses:
                    set_class_courses(new_id, [cid for cid, v in course_vars if v.get()])
                messagebox.showinfo("Succès", "Classe ajoutée.", parent=d)
                d.destroy()
                self.refresh_dashboard_stats()
                self._show_classes_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=1, padx=5)

    def _edit_class(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une classe.")
            return
        cl = get_class_by_id(tree.item(sel[0])["values"][0])
        if not cl:
            return
        d = tk.Toplevel(self)
        d.title("Modifier la classe")
        d.geometry("480x280")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Nom de la classe *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        e_name = tk.Entry(d, width=30, bg="#020617", fg=fg, insertbackground=fg)
        e_name.insert(0, cl["name"])
        e_name.grid(row=0, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Année académique *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        e_year = tk.Entry(d, width=15, bg="#020617", fg=fg, insertbackground=fg)
        e_year.insert(0, cl["academic_year"])
        e_year.grid(row=1, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Semestre *", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        cb_sem = ttk.Combobox(d, values=["S1", "S2"], state="readonly", width=10)
        cb_sem.set(cl["semester"])
        cb_sem.grid(row=2, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Cours attribués", bg=bg, fg=fg).grid(row=3, column=0, sticky="nw", padx=10, pady=4)
        courses = get_all_courses() or []
        class_course_ids = {c["id"] for c in (get_courses_for_class(cl["id"]) or [])}
        list_frame = tk.Frame(d, bg=bg)
        list_frame.grid(row=3, column=1, padx=10, pady=4, sticky="nsew")
        course_vars = []
        for c in courses:
            v = tk.BooleanVar(value=c["id"] in class_course_ids)
            course_vars.append((c["id"], v))
            tk.Checkbutton(list_frame, text=f"{c['code']} - {c['name']}", variable=v, bg=bg, fg=fg, selectcolor=bg, activebackground=bg, activeforeground=fg).pack(anchor="w")

        def save():
            if not e_name.get().strip() or not e_year.get().strip():
                messagebox.showwarning("Validation", "Nom et année obligatoires.", parent=d)
                return
            try:
                update_class(cl["id"], e_name.get(), e_year.get(), cb_sem.get())
                set_class_courses(cl["id"], [cid for cid, v in course_vars if v.get()])
                messagebox.showinfo("Succès", "Classe modifiée.", parent=d)
                d.destroy()
                self.refresh_dashboard_stats()
                self._show_classes_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=5, column=1, padx=5)

    def _delete_class(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une classe.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cette classe ? Les inscriptions et notes liées seront supprimées."):
            return
        try:
            delete_class(tree.item(sel[0])["values"][0])
            messagebox.showinfo("Succès", "Classe supprimée.")
            self.refresh_dashboard_stats()
            self._show_classes_view()
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
            text="Inscription des étudiants aux classes (année + semestre)." + (" Ajout et suppression disponibles." if self.is_admin else " Lecture seule."),
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
        columns = ("id", "academic_year", "semester", "matricule", "student_name", "class_name")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        tree.column("id", width=0, minwidth=0)
        tree.heading("academic_year", text="Année")
        tree.heading("semester", text="Semestre")
        tree.heading("matricule", text="Matricule")
        tree.heading("student_name", text="Étudiant")
        tree.heading("class_name", text="Classe")
        tree.column("academic_year", width=80, anchor="center")
        tree.column("semester", width=60, anchor="center")
        tree.column("matricule", width=100, anchor="w")
        tree.column("student_name", width=150, anchor="w")
        tree.column("class_name", width=200, anchor="w")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        try:
            for item in get_all_enrollments() or []:
                tree.insert("", "end", values=(item["id"], item["academic_year"], item["semester"], item["matricule"], item["student_name"], item["class_name"]))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les inscriptions.\n{e}")
        _make_tree_sortable(tree)

    def _add_enrollment(self, tree):
        students = get_all_students() or []
        classes = get_all_classes() or []
        student_choices = [f"{s['matricule']} - {s['last_name']} {s['first_name']}" for s in students]
        class_choices = [f"{cl['name']} ({cl['academic_year']} {cl['semester']})" for cl in classes]
        if not students or not classes:
            messagebox.showwarning("Données", "Aucun étudiant ou classe disponible. Créez-en d'abord.")
            return

        d = tk.Toplevel(self)
        d.title("Ajouter une inscription")
        d.geometry("450x180")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Étudiant *", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        cb_student = ttk.Combobox(d, values=student_choices, state="readonly", width=40)
        cb_student.current(0)
        cb_student.grid(row=0, column=1, padx=10, pady=4, sticky="w")
        tk.Label(d, text="Classe *", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        cb_class = ttk.Combobox(d, values=class_choices, state="readonly", width=40)
        cb_class.current(0)
        cb_class.grid(row=1, column=1, padx=10, pady=4, sticky="w")

        def save():
            sid = students[cb_student.current()]["id"]
            cl = classes[cb_class.current()]
            try:
                create_enrollment(sid, cl["id"], cl["academic_year"], cl["semester"])
                messagebox.showinfo("Succès", "Inscription ajoutée.", parent=d)
                d.destroy()
                self._show_enrollments_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=3, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=3, column=1, padx=5)

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
        columns = ("id", "enrollment_id", "course_id", "academic_year", "semester", "student_name", "class_name", "course_name", "grade")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        tree.column("id", width=0, minwidth=0)
        tree.column("enrollment_id", width=0, minwidth=0)
        tree.column("course_id", width=0, minwidth=0)
        tree.heading("academic_year", text="Année")
        tree.heading("semester", text="Semestre")
        tree.heading("student_name", text="Étudiant")
        tree.heading("class_name", text="Classe")
        tree.heading("course_name", text="Cours")
        tree.heading("grade", text="Note")
        tree.column("academic_year", width=80, anchor="center")
        tree.column("semester", width=60, anchor="center")
        tree.column("student_name", width=130, anchor="w")
        tree.column("class_name", width=120, anchor="w")
        tree.column("course_name", width=150, anchor="w")
        tree.column("grade", width=50, anchor="center")
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
                        item["course_id"],
                        item["academic_year"],
                        item["semester"],
                        item["student_name"],
                        item["class_name"],
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
        enrollment_choices = [f"{e['matricule']} - {e['student_name']} | {e['class_name']} ({e['academic_year']} {e['semester']})" for e in enrollments]

        enrollment_id = None
        course_id = None
        initial_grade = ""
        sel = tree.selection()
        if sel:
            vals = tree.item(sel[0])["values"]
            enrollment_id = vals[1]
            course_id = vals[2]
            initial_grade = str(vals[8]) if vals[8] != "-" else ""

        d = tk.Toplevel(self)
        d.title("Modifier / Ajouter une note")
        d.geometry("520x200")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        bg, fg = APP_CONFIG["card_bg"], APP_CONFIG["text_primary"]
        d.configure(bg=bg)
        tk.Label(d, text="Inscription (étudiant + classe)", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        cb_enr = ttk.Combobox(d, values=enrollment_choices, state="readonly", width=48)
        enr_idx = 0
        if enrollment_id:
            for i, e in enumerate(enrollments):
                if e["id"] == enrollment_id:
                    enr_idx = i
                    break
        cb_enr.current(enr_idx)
        cb_enr.grid(row=0, column=1, padx=10, pady=4, sticky="w")

        class_id = enrollments[enr_idx].get("class_id") if enr_idx < len(enrollments) else None
        course_list = get_courses_for_class(class_id) if class_id else []
        course_choices = [f"{c['code']} - {c['name']}" for c in course_list]
        tk.Label(d, text="Cours (de la classe)", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        cb_course = ttk.Combobox(d, values=course_choices, state="readonly", width=48)
        course_idx = 0
        if course_id and course_list:
            for i, c in enumerate(course_list):
                if c["id"] == course_id:
                    course_idx = i
                    break
        if course_list:
            cb_course.current(min(course_idx, len(course_list) - 1))
        cb_course.grid(row=1, column=1, padx=10, pady=4, sticky="w")

        def on_enr_change(*_):
            i = cb_enr.current()
            if 0 <= i < len(enrollments):
                cid = enrollments[i].get("class_id")
                cl = get_courses_for_class(cid) if cid else []
                cb_course["values"] = [f"{c['code']} - {c['name']}" for c in cl]
                cb_course.current(0 if cl else -1)

        cb_enr.bind("<<ComboboxSelected>>", on_enr_change)

        tk.Label(d, text="Note (0-20)", bg=bg, fg=fg).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        e_grade = tk.Entry(d, width=10, bg="#020617", fg=fg, insertbackground=fg)
        e_grade.insert(0, initial_grade)
        e_grade.grid(row=2, column=1, padx=10, pady=4, sticky="w")

        def save():
            idx = cb_enr.current()
            eid = enrollments[idx]["id"]
            cid = enrollments[idx].get("class_id")
            curr_courses = get_courses_for_class(cid) if cid else []
            if not curr_courses:
                messagebox.showwarning("Validation", "Aucun cours dans cette classe.", parent=d)
                return
            ci = cb_course.current()
            if ci < 0 or ci >= len(curr_courses):
                messagebox.showwarning("Validation", "Sélectionnez un cours.", parent=d)
                return
            course_id_val = curr_courses[ci]["id"]
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
                create_or_update_grade(eid, course_id_val, grade_val)
                messagebox.showinfo("Succès", "Note enregistrée.", parent=d)
                d.destroy()
                self._show_grades_view()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex), parent=d)

        ModernButton(d, text="Annuler", command=d.destroy, font=("Segoe UI", 9), padx=10, pady=4).grid(row=4, column=0, padx=5)
        ModernButton(d, text="Enregistrer", command=save, font=("Segoe UI", 9), padx=10, pady=4).grid(row=4, column=1, padx=5)

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

    def _show_bulletins_view(self):
        """Consulter et imprimer les bulletins des étudiants."""
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(self.content_frame, text="Bulletins des étudiants", bg=bg, fg=text_primary, font=("Segoe UI", 12, "bold"), anchor="w")
        header.pack(fill="x")
        sub = tk.Label(
            self.content_frame,
            text="Sélectionnez un étudiant, une année et un semestre pour afficher le bulletin puis l'imprimer.",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        filter_frame = tk.Frame(self.content_frame, bg=bg)
        filter_frame.pack(fill="x", pady=(8, 4))
        tk.Label(filter_frame, text="Étudiant", bg=bg, fg=text_primary, font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        students = get_all_students() or []
        student_choices = [f"{s['matricule']} - {s['last_name']} {s['first_name']}" for s in students]
        cb_student = ttk.Combobox(filter_frame, values=student_choices, state="readonly", width=35)
        cb_student.current(0 if students else -1)
        cb_student.pack(side="left", padx=4)
        tk.Label(filter_frame, text="Période", bg=bg, fg=text_primary, font=("Segoe UI", 10)).pack(side="left", padx=(12, 4))
        cb_period = ttk.Combobox(filter_frame, values=[], state="readonly", width=18)
        cb_period.pack(side="left", padx=4)

        bulletin_frame = tk.Frame(self.content_frame, bg=APP_CONFIG.get("card_bg", bg))
        bulletin_frame.pack(fill="both", expand=True, pady=(8, 0))
        self._bulletin_text = tk.Text(bulletin_frame, wrap="word", font=("Consolas", 10), bg="#1a1a2e", fg=text_primary, padx=16, pady=16)
        vsb_b = ttk.Scrollbar(bulletin_frame, orient="vertical", command=self._bulletin_text.yview)
        self._bulletin_text.configure(yscrollcommand=vsb_b.set)
        self._bulletin_text.pack(side="left", fill="both", expand=True)
        vsb_b.pack(side="right", fill="y")

        def _refresh_periods():
            if not students or cb_student.current() < 0:
                cb_period["values"] = []
                cb_period.set("")
                return
            sid = students[cb_student.current()]["id"]
            periods = get_student_periods(sid)
            choices = [f"{p['academic_year']} {p['semester']}" for p in periods]
            cb_period["values"] = choices
            if choices:
                cb_period.current(0)
            else:
                cb_period.set("")

        def _refresh_bulletin():
            self._bulletin_text.delete("1.0", "end")
            if not students:
                self._bulletin_text.insert("end", "Aucun étudiant.")
                return
            sid = students[cb_student.current()]["id"]
            period = (cb_period.get() or "").strip()
            if not period:
                self._bulletin_text.insert("end", "Aucune inscription trouvée pour cet étudiant.")
                self._bulletin_data = None
                return
            year, sem = period.split(" ", 1)
            student, rows = get_bulletin_data(sid, year, sem)
            if not student:
                self._bulletin_text.insert("end", "Étudiant introuvable.")
                return
            lines = [
                "BULLETIN DE NOTES",
                "==================",
                "",
                f"Matricule : {student.get('matricule', '')}",
                f"Nom : {student.get('last_name', '')} {student.get('first_name', '')}",
                f"Année : {year}  |  Semestre : {sem}",
                "",
                "Cours".ljust(40) + "Note",
                "-" * 50,
            ]
            current_class = None
            for r in rows:
                cl = r.get("class_name") or ""
                if cl != current_class:
                    current_class = cl
                    lines.append("")
                    lines.append(f"Classe : {current_class}")
                    lines.append("-" * 50)
                course_name = (r.get("course_code") or "") + " " + (r.get("course_name") or "")
                grade = r.get("grade")
                grade_str = str(grade) if grade is not None else "-"
                lines.append(course_name[:38].ljust(40) + grade_str)
            if not rows:
                lines.append("(Aucune inscription pour cette période)")
            self._bulletin_text.insert("end", "\n".join(lines))
            self._bulletin_data = (student, rows, year, sem)

        def _print_bulletin():
            _refresh_bulletin()
            if not getattr(self, "_bulletin_data", None):
                return
            student, rows, year, sem = self._bulletin_data
            import tempfile
            import webbrowser
            import os
            html = f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Bulletin - {student.get('last_name','')}</title>
<style>body{{ font-family: Segoe UI, sans-serif; margin: 24px; }} table{{ border-collapse: collapse; width:100%; }} th,td{{ border:1px solid #333; padding:8px; text-align:left; }} th{{ background:#2563eb; color:white; }}</style></head>
<body>
<h1>Bulletin de notes</h1>
<p><strong>Matricule:</strong> {student.get('matricule','')} &nbsp; <strong>Nom:</strong> {student.get('last_name','')} {student.get('first_name','')}</p>
<p><strong>Année:</strong> {year} &nbsp; <strong>Semestre:</strong> {sem}</p>
<table>
<tr><th>Classe</th><th>Cours</th><th>Code</th><th>Note</th></tr>
"""
            for r in rows:
                g = r.get("grade")
                grade_str = str(g) if g is not None else "-"
                html += f"<tr><td>{r.get('class_name','')}</td><td>{r.get('course_name','')}</td><td>{r.get('course_code','')}</td><td>{grade_str}</td></tr>\n"
            html += "</table><p><em>Document généré par l'application Gestion université.</em></p></body></html>"
            path = os.path.join(tempfile.gettempdir(), "bulletin.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            webbrowser.open("file://" + path)
            messagebox.showinfo("Impression", "Le bulletin a été ouvert dans le navigateur. Utilisez Ctrl+P pour imprimer.")

        ModernButton(filter_frame, text="Actualiser", command=_refresh_bulletin, font=("Segoe UI", 9), padx=10, pady=4).pack(side="left", padx=(16, 0))
        ModernButton(filter_frame, text="Ouvrir pour impression", command=_print_bulletin, font=("Segoe UI", 9), padx=10, pady=4).pack(side="left", padx=4)
        cb_student.bind("<<ComboboxSelected>>", lambda e: (_refresh_periods(), _refresh_bulletin()))
        cb_period.bind("<<ComboboxSelected>>", lambda e: _refresh_bulletin())
        _refresh_periods()
        _refresh_bulletin()

    def _show_archives_view(self):
        bg = APP_CONFIG["bg_color"]
        text_primary = APP_CONFIG["text_primary"]
        text_secondary = APP_CONFIG["text_secondary"]

        header = tk.Label(
            self.content_frame,
            text="Archives - 10 dernières années",
            bg=bg,
            fg=text_primary,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        header.pack(fill="x")
        sub = tk.Label(
            self.content_frame,
            text="Sélectionnez une année académique pour consulter les données (étudiants inscrits, enseignants, cours, inscriptions, notes).",
            bg=bg,
            fg=text_secondary,
            font=("Segoe UI", 10),
            anchor="w",
        )
        sub.pack(fill="x")

        filter_frame = tk.Frame(self.content_frame, bg=bg)
        filter_frame.pack(fill="x", pady=(8, 4))
        tk.Label(filter_frame, text="Année académique :", bg=bg, fg=text_primary, font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        years = ["Toutes les années"] + (get_available_academic_years() or [])
        cb_year = ttk.Combobox(filter_frame, values=years, state="readonly", width=18)
        cb_year.current(0)
        cb_year.pack(side="left", padx=2)

        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill="both", expand=True, pady=(8, 0))

        def _make_tab_frame():
            f = tk.Frame(notebook, bg=bg)
            table_f = tk.Frame(f, bg=bg)
            table_f.pack(fill="both", expand=True)
            vsb = ttk.Scrollbar(table_f)
            return f, table_f, vsb

        tab_students, tf_s, vsb_s = _make_tab_frame()
        tab_teachers, tf_t, vsb_t = _make_tab_frame()
        tab_courses, tf_c, vsb_c = _make_tab_frame()
        tab_enrollments, tf_e, vsb_e = _make_tab_frame()
        tab_grades, tf_g, vsb_g = _make_tab_frame()

        cols_s = ("id", "matricule", "last_name", "first_name", "email", "phone")
        tree_s = ttk.Treeview(tf_s, columns=cols_s, show="headings", height=12)
        tree_s.column("id", width=0, minwidth=0)
        for c, w in [("matricule", 100), ("last_name", 120), ("first_name", 120), ("email", 180), ("phone", 100)]:
            tree_s.heading(c, text={"last_name": "Nom", "first_name": "Prénom", "phone": "Téléphone"}.get(c, c.capitalize()))
            tree_s.column(c, width=w, anchor="w")
        vsb_s.config(command=tree_s.yview)
        tree_s.configure(yscrollcommand=vsb_s.set)
        tree_s.pack(side="left", fill="both", expand=True)
        vsb_s.pack(side="right", fill="y")

        cols_t = ("id", "last_name", "first_name", "email", "department", "phone")
        tree_t = ttk.Treeview(tf_t, columns=cols_t, show="headings", height=12)
        tree_t.column("id", width=0, minwidth=0)
        for c, w in [("last_name", 100), ("first_name", 120), ("email", 150), ("department", 120), ("phone", 100)]:
            tree_t.heading(c, text={"last_name": "Nom", "first_name": "Prénom", "department": "Département", "phone": "Téléphone"}.get(c, c.capitalize()))
            tree_t.column(c, width=w, anchor="w")
        vsb_t.config(command=tree_t.yview)
        tree_t.configure(yscrollcommand=vsb_t.set)
        tree_t.pack(side="left", fill="both", expand=True)
        vsb_t.pack(side="right", fill="y")

        cols_c = ("id", "code", "name", "credits", "teacher_name")
        tree_c = ttk.Treeview(tf_c, columns=cols_c, show="headings", height=12)
        tree_c.column("id", width=0, minwidth=0)
        for c, w in [("code", 80), ("name", 200), ("credits", 60), ("teacher_name", 150)]:
            tree_c.heading(c, text={"name": "Intitulé", "credits": "Crédits", "teacher_name": "Enseignant"}.get(c, c.capitalize()))
            tree_c.column(c, width=w, anchor="w")
        vsb_c.config(command=tree_c.yview)
        tree_c.configure(yscrollcommand=vsb_c.set)
        tree_c.pack(side="left", fill="both", expand=True)
        vsb_c.pack(side="right", fill="y")

        cols_e = ("id", "academic_year", "semester", "matricule", "student_name", "class_name")
        tree_e = ttk.Treeview(tf_e, columns=cols_e, show="headings", height=12)
        tree_e.column("id", width=0, minwidth=0)
        for c, w in [("academic_year", 90), ("semester", 60), ("matricule", 100), ("student_name", 150), ("class_name", 180)]:
            tree_e.heading(c, text={"academic_year": "Année", "semester": "Semestre", "student_name": "Étudiant", "class_name": "Classe"}.get(c, c))
            tree_e.column(c, width=w, anchor="w")
        vsb_e.config(command=tree_e.yview)
        tree_e.configure(yscrollcommand=vsb_e.set)
        tree_e.pack(side="left", fill="both", expand=True)
        vsb_e.pack(side="right", fill="y")

        cols_g = ("id", "academic_year", "semester", "student_name", "course_name", "grade")
        tree_g = ttk.Treeview(tf_g, columns=cols_g, show="headings", height=12)
        tree_g.column("id", width=0, minwidth=0)
        for c, w in [("academic_year", 90), ("semester", 60), ("student_name", 150), ("course_name", 180), ("grade", 60)]:
            tree_g.heading(c, text={"academic_year": "Année", "semester": "Semestre", "student_name": "Étudiant", "course_name": "Cours", "grade": "Note"}.get(c, c))
            tree_g.column(c, width=w, anchor="w")
        vsb_g.config(command=tree_g.yview)
        tree_g.configure(yscrollcommand=vsb_g.set)
        tree_g.pack(side="left", fill="both", expand=True)
        vsb_g.pack(side="right", fill="y")

        def _load_archives():
            year_sel = cb_year.get()
            year = None if year_sel == "Toutes les années" else year_sel

            for tr in [tree_s, tree_t, tree_c, tree_e, tree_g]:
                for i in tr.get_children(""):
                    tr.delete(i)

            try:
                if year:
                    students = get_students_by_year(year) or []
                    teachers = get_teachers_by_year(year) or []
                    courses = get_courses_by_year(year) or []
                    enrollments = get_enrollments_by_year(year) or []
                    grades = get_grades_by_year(year) or []
                else:
                    students = get_all_students() or []
                    teachers = get_all_teachers() or []
                    courses = get_all_courses() or []
                    enrollments = get_all_enrollments() or []
                    grades = get_all_grades() or []

                for s in students:
                    tree_s.insert("", "end", values=(s.get("id", ""), s.get("matricule", ""), s.get("last_name", ""), s.get("first_name", ""), s.get("email") or "", s.get("phone") or ""))
                for te in teachers:
                    tree_t.insert("", "end", values=(te.get("id", ""), te.get("last_name", ""), te.get("first_name", ""), te.get("email") or "", te.get("department") or "", te.get("phone") or ""))
                for c in courses:
                    tree_c.insert("", "end", values=(c.get("id", ""), c.get("code", ""), c.get("name", ""), c.get("credits", ""), c.get("teacher_name") or "Non assigné"))
                for e in enrollments:
                    tree_e.insert("", "end", values=(e.get("id", ""), e.get("academic_year", ""), e.get("semester", ""), e.get("matricule", ""), e.get("student_name", ""), e.get("class_name", "")))
                for g in grades:
                    tree_g.insert("", "end", values=(g.get("id", ""), g.get("academic_year", ""), g.get("semester", ""), g.get("student_name", ""), g.get("course_name", ""), g.get("grade") if g.get("grade") is not None else "-"))
            except Exception as ex:
                messagebox.showerror("Erreur", f"Impossible de charger les archives.\n{ex}")

        cb_year.bind("<<ComboboxSelected>>", lambda _: _load_archives())
        _load_archives()

        notebook.add(tab_students, text="Étudiants")
        notebook.add(tab_teachers, text="Enseignants")
        notebook.add(tab_courses, text="Cours")
        notebook.add(tab_enrollments, text="Inscriptions")
        notebook.add(tab_grades, text="Notes")

        ModernButton(filter_frame, text="Actualiser", command=lambda: (_load_archives(), self.refresh_dashboard_stats()), font=("Segoe UI", 9), padx=10, pady=4).pack(side="left", padx=(16, 0))


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
        missing = verify_tables()
        if missing:
            messagebox.showerror(
                "Tables manquantes",
                "Les tables suivantes sont absentes de la base :\n\n" + ", ".join(missing)
                + "\n\nVeuillez exécuter la commande suivante pour créer ou mettre à jour la base :\n\n  python init_db.py",
            )
            return
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


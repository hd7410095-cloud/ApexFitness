import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta


# ============================================================
# APEX FITNESS - GYM MANAGEMENT SYSTEM
# FINAL MAIN.PY
# ============================================================

APP_NAME = "Apex Fitness"
DB_NAME = "apex_fitness.db"

# ------------------------------------------------------------
# APP THEME
# ------------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # MEMBERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            plan TEXT,
            join_date TEXT,
            expiry_date TEXT,
            status TEXT
        )
    """)

    # PAYMENTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member TEXT,
            amount REAL,
            plan TEXT,
            payment_date TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

    update_expired_members()


def update_expired_members():
    """
    Automatically marks members as Expired when
    their membership expiry date has passed.
    """
    today = datetime.now().date()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, expiry_date
        FROM members
    """)

    members = cursor.fetchall()

    for member_id, expiry_date in members:
        try:
            expiry = datetime.strptime(
                expiry_date,
                "%Y-%m-%d"
            ).date()

            if expiry < today:
                status = "Expired"
            else:
                status = "Active"

            cursor.execute("""
                UPDATE members
                SET status = ?
                WHERE id = ?
            """, (status, member_id))

        except (ValueError, TypeError):
            pass

    conn.commit()
    conn.close()


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_members():
    update_expired_members()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            phone,
            email,
            plan,
            join_date,
            expiry_date,
            status
        FROM members
        ORDER BY id DESC
    """)

    data = cursor.fetchall()
    conn.close()

    return data


def get_member(member_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            phone,
            email,
            plan,
            join_date,
            expiry_date,
            status
        FROM members
        WHERE id = ?
    """, (member_id,))

    data = cursor.fetchone()

    conn.close()

    return data


def get_payments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            member,
            amount,
            plan,
            payment_date,
            status
        FROM payments
        ORDER BY id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def get_total_revenue():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE status = 'Paid'
    """)

    result = cursor.fetchone()

    conn.close()

    return float(result[0] if result else 0)


def get_member_payment_status(member_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM payments
        WHERE LOWER(TRIM(member)) = LOWER(TRIM(?))
        AND status = 'Paid'
    """, (member_name,))

    result = cursor.fetchone()

    conn.close()

    if result and result[0] > 0:
        return "PAID"

    return "UNPAID"


def get_payment_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM payments
    """)

    result = cursor.fetchone()

    conn.close()

    return result[0]


def get_active_member_count():
    update_expired_members()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM members
        WHERE status = 'Active'
    """)

    result = cursor.fetchone()

    conn.close()

    return result[0]


# ============================================================
# MAIN APPLICATION
# ============================================================

class ApexFitnessApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(
            "Apex Fitness | Gym Management System"
        )

        self.geometry("1400x850")
        self.minsize(1100, 700)

        self.configure(
            fg_color="#181818"
        )

        initialize_database()

        self.current_page = None

        self.create_login()


    # ========================================================
    # LOGIN
    # ========================================================

    def create_login(self):

        self.login_frame = ctk.CTkFrame(
            self,
            fg_color="#181818",
            corner_radius=0
        )

        self.login_frame.pack(
            fill="both",
            expand=True
        )

        card = ctk.CTkFrame(
            self.login_frame,
            width=600,
            height=560,
            corner_radius=25,
            fg_color="#242424"
        )

        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text="APEX",
            font=("Arial", 44, "bold")
        ).pack(
            pady=(60, 0)
        )

        ctk.CTkLabel(
            card,
            text="FITNESS",
            font=("Arial", 26, "bold")
        ).pack(
            pady=(0, 5)
        )

        ctk.CTkLabel(
            card,
            text="GYM MANAGEMENT SYSTEM",
            font=("Arial", 14),
            text_color="#aaaaaa"
        ).pack(
            pady=(0, 35)
        )

        self.username_entry = ctk.CTkEntry(
            card,
            width=420,
            height=48,
            placeholder_text="Username"
        )

        self.username_entry.pack(
            pady=8
        )

        self.password_entry = ctk.CTkEntry(
            card,
            width=420,
            height=48,
            placeholder_text="Password",
            show="*"
        )

        self.password_entry.pack(
            pady=8
        )

        ctk.CTkButton(
            card,
            text="LOGIN",
            width=420,
            height=50,
            font=("Arial", 16, "bold"),
            command=self.login
        ).pack(
            pady=(25, 15)
        )

        ctk.CTkLabel(
            card,
            text="Demo Login: admin / admin123",
            font=("Arial", 13),
            text_color="#888888"
        ).pack()

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )


    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:

            messagebox.showwarning(
                "Missing Information",
                "Please enter username and password."
            )

            return

        if (
            username.lower() == "admin"
            and password == "admin123"
        ):

            self.login_frame.destroy()

            self.create_dashboard()

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )


    # ========================================================
    # DASHBOARD
    # ========================================================

    def create_dashboard(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color="#121212"
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#1b1b1b"
        )

        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.create_sidebar()

        self.show_home()


    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):

        ctk.CTkLabel(
            self.sidebar,
            text="APEX",
            font=("Arial", 32, "bold")
        ).pack(
            pady=(35, 0)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="FITNESS",
            font=("Arial", 20, "bold")
        ).pack(
            pady=(0, 5)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="GYM MANAGEMENT",
            font=("Arial", 11),
            text_color="#888888"
        ).pack(
            pady=(0, 35)
        )

        self.sidebar_button(
            "🏠   Dashboard",
            self.show_home
        )

        self.sidebar_button(
            "👥   Members",
            self.show_members
        )

        self.sidebar_button(
            "💳   Payments",
            self.show_payments
        )

        self.sidebar_button(
            "📊   Analytics",
            self.show_analytics
        )

        self.sidebar_button(
            "🧮   BMI Calculator",
            self.show_bmi
        )

        self.sidebar_button(
            "🏋   Workout Plans",
            self.show_workouts
        )

        ctk.CTkButton(
            self.sidebar,
            text="🚪   Logout",
            height=45,
            corner_radius=8,
            fg_color="#8b2525",
            hover_color="#b52b2b",
            font=("Arial", 14, "bold"),
            command=self.logout
        ).pack(
            side="bottom",
            fill="x",
            padx=18,
            pady=25
        )


    def sidebar_button(self, text, command):

        button = ctk.CTkButton(
            self.sidebar,
            text=text,
            height=48,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#303030",
            anchor="w",
            font=("Arial", 14),
            command=command
        )

        button.pack(
            fill="x",
            padx=15,
            pady=4
        )


    # ========================================================
    # CONTENT
    # ========================================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()


    def page_header(self, title, subtitle=""):

        frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        frame.pack(
            fill="x",
            padx=40,
            pady=(30, 20)
        )

        ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 32, "bold")
        ).pack(
            anchor="w"
        )

        if subtitle:

            ctk.CTkLabel(
                frame,
                text=subtitle,
                font=("Arial", 14),
                text_color="#aaaaaa"
            ).pack(
                anchor="w",
                pady=(5, 0)
            )

        return frame


    # ========================================================
    # HOME
    # ========================================================

    def show_home(self):

        self.current_page = "home"

        self.clear_content()

        members = get_members()

        total_members = len(members)
        active_members = get_active_member_count()
        total_payments = get_payment_count()
        revenue = get_total_revenue()

        header = self.page_header(
            "Welcome back, Admin 👋",
            "Apex Fitness Management Dashboard"
        )

        ctk.CTkButton(
            header,
            text="↻ REFRESH",
            width=120,
            height=38,
            command=self.show_home
        ).pack(
            side="right",
            anchor="e"
        )

        stats_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        stats_frame.pack(
            fill="x",
            padx=35
        )

        stats = [
            ("TOTAL MEMBERS", total_members),
            ("ACTIVE MEMBERS", active_members),
            ("PAYMENTS", total_payments),
            ("REVENUE", f"₹{revenue:,.2f}")
        ]

        for title, value in stats:

            card = ctk.CTkFrame(
                stats_frame,
                fg_color="#252525",
                corner_radius=15,
                height=130
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=6
            )

            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 12, "bold"),
                text_color="#aaaaaa"
            ).pack(
                anchor="w",
                padx=20,
                pady=(22, 5)
            )

            ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 29, "bold")
            ).pack(
                anchor="w",
                padx=20
            )

        quick = ctk.CTkFrame(
            self.content,
            fg_color="#252525",
            corner_radius=15
        )

        quick.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        ctk.CTkLabel(
            quick,
            text="Quick Actions",
            font=("Arial", 24, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=(25, 20)
        )

        action_frame = ctk.CTkFrame(
            quick,
            fg_color="transparent"
        )

        action_frame.pack(
            fill="x",
            padx=30
        )

        ctk.CTkButton(
            action_frame,
            text="+ ADD NEW MEMBER",
            width=240,
            height=55,
            font=("Arial", 14, "bold"),
            command=self.add_member_window
        ).pack(
            side="left",
            padx=(0, 12)
        )

        ctk.CTkButton(
            action_frame,
            text="💳 MANAGE PAYMENTS",
            width=240,
            height=55,
            font=("Arial", 14, "bold"),
            command=self.show_payments
        ).pack(
            side="left",
            padx=12
        )

        ctk.CTkButton(
            action_frame,
            text="📊 VIEW ANALYTICS",
            width=240,
            height=55,
            font=("Arial", 14, "bold"),
            command=self.show_analytics
        ).pack(
            side="left",
            padx=12
        )

        recent = ctk.CTkFrame(
            quick,
            fg_color="#303030",
            corner_radius=12
        )

        recent.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        ctk.CTkLabel(
            recent,
            text="Recent Members",
            font=("Arial", 20, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        recent_members = members[:5]

        if not recent_members:

            ctk.CTkLabel(
                recent,
                text="No members added yet.",
                font=("Arial", 15),
                text_color="#999999"
            ).pack(
                pady=30
            )

        else:

            for member in recent_members:

                row = ctk.CTkFrame(
                    recent,
                    fg_color="#252525",
                    corner_radius=8,
                    height=45
                )

                row.pack(
                    fill="x",
                    padx=20,
                    pady=4
                )

                row.pack_propagate(False)

                ctk.CTkLabel(
                    row,
                    text=member[1],
                    font=("Arial", 13, "bold")
                ).pack(
                    side="left",
                    padx=15
                )

                status_text = member[7]

                ctk.CTkLabel(
                    row,
                    text=f"{member[4]}  |  {status_text}",
                    font=("Arial", 12)
                ).pack(
                    side="right",
                    padx=15
                )


    # ========================================================
    # MEMBERS
    # ========================================================

    def show_members(self):

        self.current_page = "members"

        self.clear_content()

        header = self.page_header(
            "Member Management",
            "Add, search and manage gym members"
        )

        ctk.CTkButton(
            header,
            text="+ ADD MEMBER",
            width=170,
            height=42,
            font=("Arial", 13, "bold"),
            command=self.add_member_window
        ).pack(
            side="right",
            anchor="e"
        )

        search_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        search_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 15)
        )

        self.member_search = ctk.CTkEntry(
            search_frame,
            width=350,
            height=42,
            placeholder_text="Search by name or phone..."
        )

        self.member_search.pack(
            side="left"
        )

        ctk.CTkButton(
            search_frame,
            text="SEARCH",
            width=110,
            height=42,
            command=self.load_members_table
        ).pack(
            side="left",
            padx=10
        )

        ctk.CTkButton(
            search_frame,
            text="CLEAR",
            width=100,
            height=42,
            fg_color="#444444",
            hover_color="#555555",
            command=self.clear_member_search
        ).pack(
            side="left"
        )

        self.members_table = ctk.CTkScrollableFrame(
            self.content,
            fg_color="#252525",
            corner_radius=15
        )

        self.members_table.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=10
        )

        self.load_members_table()

        self.member_search.bind(
            "<KeyRelease>",
            lambda event: self.load_members_table()
        )


    def clear_member_search(self):

        self.member_search.delete(
            0,
            "end"
        )

        self.load_members_table()


    def load_members_table(self):

        if not hasattr(self, "members_table"):
            return

        for widget in self.members_table.winfo_children():
            widget.destroy()

        query = self.member_search.get().strip().lower()

        headings = [
            "ID",
            "NAME",
            "PHONE",
            "PLAN",
            "JOIN DATE",
            "EXPIRY",
            "STATUS",
            "PAYMENT",
            "ACTION"
        ]

        for col, heading in enumerate(headings):

            self.members_table.grid_columnconfigure(
                col,
                weight=1
            )

            ctk.CTkLabel(
                self.members_table,
                text=heading,
                font=("Arial", 12, "bold")
            ).grid(
                row=0,
                column=col,
                padx=8,
                pady=15,
                sticky="w"
            )

        members = get_members()

        if query:

            members = [
                member
                for member in members
                if query in str(member[1]).lower()
                or query in str(member[2]).lower()
            ]

        if not members:

            ctk.CTkLabel(
                self.members_table,
                text="No members found.",
                font=("Arial", 16),
                text_color="#999999"
            ).grid(
                row=1,
                column=0,
                columnspan=9,
                pady=80
            )

            return

        for row_number, member in enumerate(
            members,
            start=1
        ):

            payment_status = get_member_payment_status(
                member[1]
            )

            values = [
                member[0],
                member[1],
                member[2],
                member[4],
                member[5],
                member[6],
                member[7]
            ]

            for col, value in enumerate(values):

                text_color = None

                if col == 6:

                    if value == "Active":
                        text_color = "#4CAF50"

                    elif value == "Expired":
                        text_color = "#FF5555"

                ctk.CTkLabel(
                    self.members_table,
                    text=str(value),
                    font=("Arial", 12),
                    text_color=text_color
                ).grid(
                    row=row_number,
                    column=col,
                    padx=8,
                    pady=10,
                    sticky="w"
                )

            if payment_status == "PAID":

                payment_label = ctk.CTkLabel(
                    self.members_table,
                    text="✓ PAID",
                    font=("Arial", 12, "bold"),
                    text_color="#4CAF50"
                )

            else:

                payment_label = ctk.CTkLabel(
                    self.members_table,
                    text="✗ UNPAID",
                    font=("Arial", 12, "bold"),
                    text_color="#FF5555"
                )

            payment_label.grid(
                row=row_number,
                column=7,
                padx=8,
                pady=10
            )

            ctk.CTkButton(
                self.members_table,
                text="DELETE",
                width=80,
                height=30,
                fg_color="#8b2525",
                hover_color="#b52b2b",
                command=lambda mid=member[0]:
                self.delete_member(mid)
            ).grid(
                row=row_number,
                column=8,
                padx=8,
                pady=10
            )


    # ========================================================
    # ADD MEMBER
    # ========================================================

    def add_member_window(self):

        window = ctk.CTkToplevel(self)

        window.title(
            "Apex Fitness | Add Member"
        )

        window.geometry(
            "520x650"
        )

        window.resizable(
            False,
            False
        )

        window.grab_set()

        ctk.CTkLabel(
            window,
            text="ADD NEW MEMBER",
            font=("Arial", 28, "bold")
        ).pack(
            pady=(35, 25)
        )

        name = ctk.CTkEntry(
            window,
            width=400,
            height=45,
            placeholder_text="Full Name"
        )

        name.pack(
            pady=8
        )

        phone = ctk.CTkEntry(
            window,
            width=400,
            height=45,
            placeholder_text="Phone Number"
        )

        phone.pack(
            pady=8
        )

        email = ctk.CTkEntry(
            window,
            width=400,
            height=45,
            placeholder_text="Email"
        )

        email.pack(
            pady=8
        )

        ctk.CTkLabel(
            window,
            text="Membership Plan",
            font=("Arial", 13)
        ).pack(
            pady=(10, 3)
        )

        plan = ctk.CTkOptionMenu(
            window,
            width=400,
            height=45,
            values=[
                "Basic",
                "Standard",
                "Premium"
            ]
        )

        plan.set("Standard")

        plan.pack(
            pady=8
        )

        def save_member():

            member_name = name.get().strip()
            member_phone = phone.get().strip()
            member_email = email.get().strip()
            selected_plan = plan.get()

            if not member_name:

                messagebox.showwarning(
                    "Missing Information",
                    "Please enter member name.",
                    parent=window
                )

                return

            if member_phone:

                if not member_phone.isdigit() or len(member_phone) != 10:

                    messagebox.showwarning(
                        "Invalid Phone",
                        "Phone number must contain exactly 10 digits.",
                        parent=window
                    )

                    return

            if member_email and "@" not in member_email:

                messagebox.showwarning(
                    "Invalid Email",
                    "Please enter a valid email address.",
                    parent=window
                )

                return

            if selected_plan == "Basic":

                days = 30

            elif selected_plan == "Standard":

                days = 90

            else:

                days = 365

            today = datetime.now()

            expiry = today + timedelta(
                days=days
            )

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO members
                (
                    name,
                    phone,
                    email,
                    plan,
                    join_date,
                    expiry_date,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                member_name,
                member_phone,
                member_email,
                selected_plan,
                today.strftime("%Y-%m-%d"),
                expiry.strftime("%Y-%m-%d"),
                "Active"
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"{member_name} added successfully!",
                parent=window
            )

            window.destroy()

            if self.current_page == "members":
                self.show_members()
            else:
                self.show_home()

        ctk.CTkButton(
            window,
            text="SAVE MEMBER",
            width=400,
            height=50,
            font=("Arial", 15, "bold"),
            command=save_member
        ).pack(
            pady=25
        )


    # ========================================================
    # DELETE MEMBER
    # ========================================================

    def delete_member(self, member_id):

        member = get_member(member_id)

        if not member:
            return

        confirm = messagebox.askyesno(
            "Delete Member",
            f"Are you sure you want to delete '{member[1]}'?\n\n"
            "Their payment records will also be deleted."
        )

        if not confirm:
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM members WHERE id = ?",
            (member_id,)
        )

        cursor.execute(
            "DELETE FROM payments WHERE member = ?",
            (member[1],)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Deleted",
            "Member deleted successfully."
        )

        self.show_members()


    # ========================================================
    # PAYMENTS
    # ========================================================

    def show_payments(self):

        self.current_page = "payments"

        self.clear_content()

        header = self.page_header(
            "Payment Management",
            "Record and manage membership payments"
        )

        ctk.CTkButton(
            header,
            text="+ ADD PAYMENT",
            width=180,
            height=42,
            font=("Arial", 13, "bold"),
            command=self.add_payment_window
        ).pack(
            side="right",
            anchor="e"
        )

        table = ctk.CTkScrollableFrame(
            self.content,
            fg_color="#252525",
            corner_radius=15
        )

        table.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=10
        )

        headings = [
            "ID",
            "MEMBER",
            "AMOUNT",
            "PLAN",
            "DATE",
            "STATUS",
            "ACTION"
        ]

        for col, heading in enumerate(headings):

            table.grid_columnconfigure(
                col,
                weight=1
            )

            ctk.CTkLabel(
                table,
                text=heading,
                font=("Arial", 13, "bold")
            ).grid(
                row=0,
                column=col,
                padx=15,
                pady=15,
                sticky="w"
            )

        payments = get_payments()

        if not payments:

            ctk.CTkLabel(
                table,
                text="No payments recorded yet.",
                font=("Arial", 16),
                text_color="#999999"
            ).grid(
                row=1,
                column=0,
                columnspan=7,
                pady=80
            )

            return

        for row_number, payment in enumerate(
            payments,
            start=1
        ):

            values = [
                payment[0],
                payment[1],
                f"₹{payment[2]:,.2f}",
                payment[3],
                payment[4],
                payment[5]
            ]

            for col, value in enumerate(values):

                text_color = None

                if col == 5 and value == "Paid":
                    text_color = "#4CAF50"

                ctk.CTkLabel(
                    table,
                    text=str(value),
                    font=("Arial", 12),
                    text_color=text_color
                ).grid(
                    row=row_number,
                    column=col,
                    padx=15,
                    pady=12,
                    sticky="w"
                )

            ctk.CTkButton(
                table,
                text="DELETE",
                width=80,
                height=30,
                fg_color="#8b2525",
                hover_color="#b52b2b",
                command=lambda pid=payment[0]:
                self.delete_payment(pid)
            ).grid(
                row=row_number,
                column=6,
                padx=15,
                pady=12
            )


    # ========================================================
    # ADD PAYMENT
    # ========================================================

    def add_payment_window(self):

        members = get_members()

        if not members:

            messagebox.showwarning(
                "No Members",
                "Please add a member before recording a payment."
            )

            return

        window = ctk.CTkToplevel(self)

        window.title(
            "Apex Fitness | Add Payment"
        )

        window.geometry(
            "520x580"
        )

        window.resizable(
            False,
            False
        )

        window.grab_set()

        ctk.CTkLabel(
            window,
            text="ADD PAYMENT",
            font=("Arial", 28, "bold")
        ).pack(
            pady=(35, 25)
        )

        ctk.CTkLabel(
            window,
            text="Select Member",
            font=("Arial", 13)
        ).pack(
            pady=(5, 5)
        )

        member_names = [
            m[1]
            for m in members
        ]

        member = ctk.CTkOptionMenu(
            window,
            width=400,
            height=45,
            values=member_names
        )

        member.set(
            member_names[0]
        )

        member.pack(
            pady=8
        )

        amount = ctk.CTkEntry(
            window,
            width=400,
            height=45,
            placeholder_text="Amount ₹"
        )

        amount.pack(
            pady=8
        )

        ctk.CTkLabel(
            window,
            text="Membership Plan",
            font=("Arial", 13)
        ).pack(
            pady=(10, 3)
        )

        plan = ctk.CTkOptionMenu(
            window,
            width=400,
            height=45,
            values=[
                "Basic",
                "Standard",
                "Premium"
            ]
        )

        plan.set(
            members[0][4]
        )

        plan.pack(
            pady=8
        )

        def update_plan(choice):

            for m in members:

                if m[1] == choice:

                    plan.set(
                        m[4]
                    )

                    break

        member.configure(
            command=update_plan
        )

        update_plan(
            member.get()
        )

        def save_payment():

            selected_member = member.get().strip()

            if not selected_member:

                messagebox.showwarning(
                    "Error",
                    "Please select a member.",
                    parent=window
                )

                return

            amount_text = amount.get().strip()

            try:

                value = float(
                    amount_text
                )

                if value <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Invalid Amount",
                    "Enter a valid amount greater than 0.",
                    parent=window
                )

                return

            selected_plan = plan.get()

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO payments
                (
                    member,
                    amount,
                    plan,
                    payment_date,
                    status
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                selected_member,
                value,
                selected_plan,
                datetime.now().strftime("%Y-%m-%d"),
                "Paid"
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Payment Recorded",
                f"Payment of ₹{value:,.2f} recorded for "
                f"{selected_member}.",
                parent=window
            )

            window.destroy()

            self.show_payments()

        ctk.CTkButton(
            window,
            text="SAVE PAYMENT",
            width=400,
            height=50,
            font=("Arial", 15, "bold"),
            command=save_payment
        ).pack(
            pady=25
        )


    # ========================================================
    # DELETE PAYMENT
    # ========================================================

    def delete_payment(self, payment_id):

        confirm = messagebox.askyesno(
            "Delete Payment",
            "Are you sure you want to delete this payment?"
        )

        if not confirm:
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM payments WHERE id = ?",
            (payment_id,)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Deleted",
            "Payment deleted successfully."
        )

        self.show_payments()


    # ========================================================
    # ANALYTICS
    # ========================================================

    def show_analytics(self):

        self.current_page = "analytics"

        self.clear_content()

        members = get_members()
        payments = get_payments()

        total_members = len(members)

        active_members = len([
            m for m in members
            if m[7] == "Active"
        ])

        expired_members = len([
            m for m in members
            if m[7] == "Expired"
        ])

        total_payments = len(payments)

        total_revenue = get_total_revenue()

        basic = len([
            m for m in members
            if m[4] == "Basic"
        ])

        standard = len([
            m for m in members
            if m[4] == "Standard"
        ])

        premium = len([
            m for m in members
            if m[4] == "Premium"
        ])

        paid_members = 0

        for member in members:

            if get_member_payment_status(
                member[1]
            ) == "PAID":

                paid_members += 1

        unpaid_members = (
            total_members - paid_members
        )

        self.page_header(
            "Analytics & Reports",
            "Apex Fitness business overview"
        )

        stats = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        stats.pack(
            fill="x",
            padx=35
        )

        analytics_data = [
            ("TOTAL MEMBERS", total_members),
            ("ACTIVE MEMBERS", active_members),
            ("EXPIRED MEMBERS", expired_members),
            ("TOTAL REVENUE", f"₹{total_revenue:,.2f}")
        ]

        for title, value in analytics_data:

            card = ctk.CTkFrame(
                stats,
                fg_color="#252525",
                corner_radius=15,
                height=125
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=6
            )

            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 12, "bold"),
                text_color="#aaaaaa"
            ).pack(
                anchor="w",
                padx=20,
                pady=(20, 5)
            )

            ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 27, "bold")
            ).pack(
                anchor="w",
                padx=20
            )

        analytics_area = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent"
        )

        analytics_area.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        # MEMBERSHIP PLANS

        plans_frame = ctk.CTkFrame(
            analytics_area,
            fg_color="#252525",
            corner_radius=15
        )

        plans_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            plans_frame,
            text="Membership Plans",
            font=("Arial", 22, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 15)
        )

        plans = [
            ("Basic Plan", basic),
            ("Standard Plan", standard),
            ("Premium Plan", premium)
        ]

        for plan_name, count in plans:

            row = ctk.CTkFrame(
                plans_frame,
                fg_color="#303030",
                corner_radius=8
            )

            row.pack(
                fill="x",
                padx=25,
                pady=5
            )

            ctk.CTkLabel(
                row,
                text=plan_name,
                font=("Arial", 14)
            ).pack(
                side="left",
                padx=15,
                pady=12
            )

            ctk.CTkLabel(
                row,
                text=f"{count} Members",
                font=("Arial", 14, "bold")
            ).pack(
                side="right",
                padx=15
            )

        # PAYMENT SUMMARY

        payment_frame = ctk.CTkFrame(
            analytics_area,
            fg_color="#252525",
            corner_radius=15
        )

        payment_frame.pack(
            fill="x",
            pady=15
        )

        ctk.CTkLabel(
            payment_frame,
            text="Payment Summary",
            font=("Arial", 22, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 15)
        )

        summary = [
            ("Paid Members", paid_members),
            ("Unpaid Members", unpaid_members),
            ("Total Payments", total_payments),
            ("Total Revenue", f"₹{total_revenue:,.2f}")
        ]

        for label, value in summary:

            row = ctk.CTkFrame(
                payment_frame,
                fg_color="#303030",
                corner_radius=8
            )

            row.pack(
                fill="x",
                padx=25,
                pady=5
            )

            ctk.CTkLabel(
                row,
                text=label,
                font=("Arial", 14)
            ).pack(
                side="left",
                padx=15,
                pady=12
            )

            ctk.CTkLabel(
                row,
                text=str(value),
                font=("Arial", 14, "bold")
            ).pack(
                side="right",
                padx=15
            )

        # RECENT PAYMENTS

        recent_frame = ctk.CTkFrame(
            analytics_area,
            fg_color="#252525",
            corner_radius=15
        )

        recent_frame.pack(
            fill="x",
            pady=15
        )

        ctk.CTkLabel(
            recent_frame,
            text="Recent Payments",
            font=("Arial", 22, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 15)
        )

        recent_payments = payments[:5]

        if not recent_payments:

            ctk.CTkLabel(
                recent_frame,
                text="No payments recorded.",
                font=("Arial", 14),
                text_color="#999999"
            ).pack(
                pady=25
            )

        else:

            for payment in recent_payments:

                row = ctk.CTkFrame(
                    recent_frame,
                    fg_color="#303030",
                    corner_radius=8
                )

                row.pack(
                    fill="x",
                    padx=25,
                    pady=5
                )

                ctk.CTkLabel(
                    row,
                    text=payment[1],
                    font=("Arial", 14, "bold")
                ).pack(
                    side="left",
                    padx=15,
                    pady=10
                )

                ctk.CTkLabel(
                    row,
                    text=f"₹{payment[2]:,.2f}",
                    font=("Arial", 14)
                ).pack(
                    side="right",
                    padx=15
                )


    # ========================================================
    # BMI CALCULATOR
    # ========================================================

    def show_bmi(self):

        self.current_page = "bmi"

        self.clear_content()

        self.page_header(
            "BMI Calculator",
            "Calculate Body Mass Index"
        )

        card = ctk.CTkFrame(
            self.content,
            fg_color="#252525",
            corner_radius=15
        )

        card.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=20
        )

        ctk.CTkLabel(
            card,
            text="Enter your measurements",
            font=("Arial", 20, "bold")
        ).pack(
            pady=(60, 25)
        )

        height = ctk.CTkEntry(
            card,
            width=400,
            height=48,
            placeholder_text="Height in cm"
        )

        height.pack(
            pady=10
        )

        weight = ctk.CTkEntry(
            card,
            width=400,
            height=48,
            placeholder_text="Weight in kg"
        )

        weight.pack(
            pady=10
        )

        result = ctk.CTkLabel(
            card,
            text="BMI: --",
            font=("Arial", 30, "bold")
        )

        result.pack(
            pady=(30, 10)
        )

        category = ctk.CTkLabel(
            card,
            text="",
            font=("Arial", 18)
        )

        category.pack(
            pady=5
        )

        def calculate_bmi():

            try:

                h = float(
                    height.get()
                ) / 100

                w = float(
                    weight.get()
                )

                if h <= 0 or w <= 0:
                    raise ValueError

                bmi = w / (h * h)

                result.configure(
                    text=f"BMI: {bmi:.1f}"
                )

                if bmi < 18.5:

                    text = "Underweight"

                elif bmi < 25:

                    text = "Normal Weight"

                elif bmi < 30:

                    text = "Overweight"

                else:

                    text = "Obese"

                category.configure(
                    text=text
                )

            except ValueError:

                messagebox.showerror(
                    "Invalid Input",
                    "Please enter valid positive numbers."
                )

        ctk.CTkButton(
            card,
            text="CALCULATE BMI",
            width=400,
            height=50,
            font=("Arial", 15, "bold"),
            command=calculate_bmi
        ).pack(
            pady=25
        )


    # ========================================================
    # WORKOUT PLANS
    # ========================================================

    def show_workouts(self):

        self.current_page = "workouts"

        self.clear_content()

        self.page_header(
            "Workout Plans",
            "Training programs for gym members"
        )

        scroll = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent"
        )

        scroll.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        plans = [

            (
                "BEGINNER",
                "Full Body",
                "3 Days / Week",
                [
                    "Bodyweight Squats",
                    "Push Ups",
                    "Lat Pulldown",
                    "Dumbbell Shoulder Press",
                    "Plank"
                ]
            ),

            (
                "MUSCLE BUILDING",
                "Push Pull Legs",
                "6 Days / Week",
                [
                    "Bench Press",
                    "Rows",
                    "Shoulder Press",
                    "Bicep Curls",
                    "Tricep Extensions",
                    "Leg Press"
                ]
            ),

            (
                "FAT LOSS",
                "Cardio + Strength",
                "5 Days / Week",
                [
                    "Walking",
                    "Cycling",
                    "Bodyweight Squats",
                    "Push Ups",
                    "Core Training"
                ]
            ),

            (
                "STRENGTH",
                "Power Training",
                "4 Days / Week",
                [
                    "Deadlift",
                    "Squat",
                    "Bench Press",
                    "Overhead Press",
                    "Barbell Row"
                ]
            )
        ]

        for i, data in enumerate(plans):

            card = ctk.CTkFrame(
                scroll,
                fg_color="#252525",
                corner_radius=15
            )

            card.grid(
                row=i // 2,
                column=i % 2,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            ctk.CTkLabel(
                card,
                text=data[0],
                font=("Arial", 20, "bold")
            ).pack(
                anchor="w",
                padx=25,
                pady=(25, 5)
            )

            ctk.CTkLabel(
                card,
                text=data[1],
                font=("Arial", 17)
            ).pack(
                anchor="w",
                padx=25
            )

            ctk.CTkLabel(
                card,
                text=data[2],
                font=("Arial", 13),
                text_color="#aaaaaa"
            ).pack(
                anchor="w",
                padx=25,
                pady=(3, 15)
            )

            for exercise in data[3]:

                ctk.CTkLabel(
                    card,
                    text=f"• {exercise}",
                    font=("Arial", 13)
                ).pack(
                    anchor="w",
                    padx=30,
                    pady=3
                )

            ctk.CTkLabel(
                card,
                text=""
            ).pack(
                pady=10
            )

        scroll.grid_columnconfigure(
            0,
            weight=1
        )

        scroll.grid_columnconfigure(
            1,
            weight=1
        )


    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):

        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        )

        if not confirm:
            return

        for widget in self.winfo_children():
            widget.destroy()

        self.create_login()


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    app = ApexFitnessApp()

    app.mainloop()
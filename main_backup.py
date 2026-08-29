import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta

# ============================================================
# APEX FITNESS - GYM MANAGEMENT SYSTEM
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DB = "apex_fitness.db"


# ============================================================
# DATABASE
# ============================================================

def database():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

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


database()


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_members():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, phone, email, plan,
               join_date, expiry_date, status
        FROM members
        ORDER BY id DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def get_payments():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, member, amount, plan,
               payment_date, status
        FROM payments
        ORDER BY id DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data


# ============================================================
# LOGIN
# ============================================================

def login():

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "admin" and password == "admin123":

        login_window.destroy()
        dashboard()

    elif username == "" or password == "":

        messagebox.showwarning(
            "Missing Information",
            "Please enter username and password."
        )

    else:

        messagebox.showerror(
            "Login Failed",
            "Invalid username or password."
        )


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    app = ctk.CTk()

    app.title("Apex Fitness | Dashboard")
    app.geometry("1350x780")
    app.minsize(1100, 650)

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    sidebar = ctk.CTkFrame(
        app,
        width=240,
        corner_radius=0,
        fg_color="#151515"
    )

    sidebar.pack(
        side="left",
        fill="y"
    )

    sidebar.pack_propagate(False)

    ctk.CTkLabel(
        sidebar,
        text="APEX\nFITNESS",
        font=("Arial", 30, "bold")
    ).pack(pady=(45, 5))

    ctk.CTkLabel(
        sidebar,
        text="GYM MANAGEMENT",
        font=("Arial", 11)
    ).pack(pady=(0, 40))

    # --------------------------------------------------------
    # MAIN CONTENT
    # --------------------------------------------------------

    content = ctk.CTkFrame(
        app,
        fg_color="#1e1e1e",
        corner_radius=0
    )

    content.pack(
        side="right",
        fill="both",
        expand=True
    )

    def clear():

        for widget in content.winfo_children():
            widget.destroy()

    # --------------------------------------------------------
    # SIDEBAR BUTTON
    # --------------------------------------------------------

    def side_button(text, command):

        button = ctk.CTkButton(
            sidebar,
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
            padx=18,
            pady=4
        )

    # ========================================================
    # DASHBOARD PAGE
    # ========================================================

    def home():

        clear()

        members = get_members()
        payments = get_payments()

        total = len(members)

        active = len([
            x for x in members
            if x[7] == "Active"
        ])

        # Header

        ctk.CTkLabel(
            content,
            text="Welcome back, Admin 👋",
            font=("Arial", 32, "bold")
        ).pack(
            anchor="w",
            padx=40,
            pady=(35, 5)
        )

        ctk.CTkLabel(
            content,
            text="Apex Fitness Management Dashboard",
            font=("Arial", 14)
        ).pack(
            anchor="w",
            padx=40,
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        stats = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        stats.pack(
            fill="x",
            padx=35
        )

        data = [
            ("TOTAL MEMBERS", str(total)),
            ("ACTIVE MEMBERS", str(active)),
            ("PAYMENTS", str(len(payments))),
            ("REVENUE", "₹82,500")
        ]

        for title, value in data:

            card = ctk.CTkFrame(
                stats,
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
                font=("Arial", 13)
            ).pack(
                anchor="w",
                padx=20,
                pady=(20, 5)
            )

            ctk.CTkLabel(
                card,
                text=value,
                font=("Arial", 30, "bold")
            ).pack(
                anchor="w",
                padx=20
            )

        # ----------------------------------------------------
        # QUICK ACTIONS
        # ----------------------------------------------------

        quick = ctk.CTkFrame(
            content,
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

        ctk.CTkButton(
            quick,
            text="+ Add New Member",
            width=220,
            height=50,
            command=add_member
        ).pack(
            anchor="w",
            padx=30,
            pady=8
        )

        ctk.CTkButton(
            quick,
            text="💳 Manage Payments",
            width=220,
            height=50,
            command=payments_page
        ).pack(
            anchor="w",
            padx=30,
            pady=8
        )

        ctk.CTkButton(
            quick,
            text="🧮 BMI Calculator",
            width=220,
            height=50,
            command=bmi_page
        ).pack(
            anchor="w",
            padx=30,
            pady=8
        )

    # ========================================================
    # MEMBERS PAGE
    # ========================================================

    def members_page():

        clear()

        header = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=40,
            pady=(30, 20)
        )

        ctk.CTkLabel(
            header,
            text="Member Management",
            font=("Arial", 30, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="+ ADD MEMBER",
            width=170,
            height=42,
            command=add_member
        ).pack(side="right")

        # Search

        search_frame = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        search_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 15)
        )

        search = ctk.CTkEntry(
            search_frame,
            width=350,
            height=42,
            placeholder_text="Search member..."
        )

        search.pack(side="left")

        table = ctk.CTkScrollableFrame(
            content,
            fg_color="#252525",
            corner_radius=15
        )

        table.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=10
        )

        def load():

            for widget in table.winfo_children():
                widget.destroy()

            query = search.get().lower()

            headings = [
                "ID",
                "NAME",
                "PHONE",
                "PLAN",
                "JOIN DATE",
                "EXPIRY",
                "STATUS",
                "ACTION"
            ]

            for col, text in enumerate(headings):

                ctk.CTkLabel(
                    table,
                    text=text,
                    font=("Arial", 12, "bold")
                ).grid(
                    row=0,
                    column=col,
                    padx=10,
                    pady=15,
                    sticky="w"
                )

            members = get_members()

            if query:

                members = [
                    m for m in members
                    if query in m[1].lower()
                    or query in str(m[2]).lower()
                ]

            if not members:

                ctk.CTkLabel(
                    table,
                    text="No members found.",
                    font=("Arial", 16)
                ).grid(
                    row=1,
                    column=0,
                    columnspan=8,
                    pady=80
                )

                return

            for row, member in enumerate(members, start=1):

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

                    ctk.CTkLabel(
                        table,
                        text=str(value),
                        font=("Arial", 12)
                    ).grid(
                        row=row,
                        column=col,
                        padx=10,
                        pady=10,
                        sticky="w"
                    )

                ctk.CTkButton(
                    table,
                    text="DELETE",
                    width=75,
                    height=30,
                    fg_color="#8b2525",
                    hover_color="#b52b2b",
                    command=lambda mid=member[0]: delete_member(mid)
                ).grid(
                    row=row,
                    column=7,
                    padx=10
                )

        ctk.CTkButton(
            search_frame,
            text="SEARCH",
            width=100,
            height=42,
            command=load
        ).pack(
            side="left",
            padx=10
        )

        load()

    # ========================================================
    # ADD MEMBER
    # ========================================================

    def add_member():

        window = ctk.CTkToplevel(app)

        window.title("Apex Fitness | Add Member")
        window.geometry("500x620")
        window.resizable(False, False)

        window.grab_set()

        ctk.CTkLabel(
            window,
            text="ADD NEW MEMBER",
            font=("Arial", 28, "bold")
        ).pack(pady=(35, 25))

        name = ctk.CTkEntry(
            window,
            width=380,
            height=45,
            placeholder_text="Full Name"
        )
        name.pack(pady=8)

        phone = ctk.CTkEntry(
            window,
            width=380,
            height=45,
            placeholder_text="Phone Number"
        )
        phone.pack(pady=8)

        email = ctk.CTkEntry(
            window,
            width=380,
            height=45,
            placeholder_text="Email"
        )
        email.pack(pady=8)

        plan = ctk.CTkOptionMenu(
            window,
            width=380,
            height=45,
            values=["Basic", "Standard", "Premium"]
        )

        plan.set("Standard")
        plan.pack(pady=8)

        def save():

            member_name = name.get().strip()

            if member_name == "":

                messagebox.showwarning(
                    "Missing Information",
                    "Please enter member name."
                )

                return

            today = datetime.now()

            selected_plan = plan.get()

            if selected_plan == "Basic":
                days = 30
            elif selected_plan == "Standard":
                days = 90
            else:
                days = 365

            expiry = today + timedelta(days=days)

            conn = sqlite3.connect(DB)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO members
                (name, phone, email, plan,
                 join_date, expiry_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                member_name,
                phone.get(),
                email.get(),
                selected_plan,
                today.strftime("%Y-%m-%d"),
                expiry.strftime("%Y-%m-%d"),
                "Active"
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                "Member added successfully!"
            )

            window.destroy()

            members_page()

        ctk.CTkButton(
            window,
            text="SAVE MEMBER",
            width=380,
            height=48,
            font=("Arial", 15, "bold"),
            command=save
        ).pack(pady=25)

    # ========================================================
    # DELETE MEMBER
    # ========================================================

    def delete_member(member_id):

        confirm = messagebox.askyesno(
            "Delete Member",
            "Are you sure you want to delete this member?"
        )

        if confirm:

            conn = sqlite3.connect(DB)
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM members WHERE id=?",
                (member_id,)
            )

            conn.commit()
            conn.close()

            members_page()

    # ========================================================
    # PAYMENTS PAGE
    # ========================================================

    def payments_page():

        clear()

        header = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=40,
            pady=(30, 20)
        )

        ctk.CTkLabel(
            header,
            text="Payment Management",
            font=("Arial", 30, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="+ ADD PAYMENT",
            width=170,
            height=42,
            command=add_payment
        ).pack(side="right")

        table = ctk.CTkScrollableFrame(
            content,
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
            "STATUS"
        ]

        for col, heading in enumerate(headings):

            ctk.CTkLabel(
                table,
                text=heading,
                font=("Arial", 13, "bold")
            ).grid(
                row=0,
                column=col,
                padx=30,
                pady=15,
                sticky="w"
            )

        payments = get_payments()

        if not payments:

            ctk.CTkLabel(
                table,
                text="No payments recorded yet.",
                font=("Arial", 16)
            ).grid(
                row=1,
                column=0,
                columnspan=6,
                pady=80
            )

        for row, payment in enumerate(payments, start=1):

            values = [
                payment[0],
                payment[1],
                f"₹{payment[2]:.2f}",
                payment[3],
                payment[4],
                payment[5]
            ]

            for col, value in enumerate(values):

                ctk.CTkLabel(
                    table,
                    text=str(value),
                    font=("Arial", 13)
                ).grid(
                    row=row,
                    column=col,
                    padx=30,
                    pady=12,
                    sticky="w"
                )

    # ========================================================
    # ADD PAYMENT
    # ========================================================

    def add_payment():

        window = ctk.CTkToplevel(app)

        window.title("Apex Fitness | Add Payment")
        window.geometry("500x500")
        window.resizable(False, False)

        window.grab_set()

        ctk.CTkLabel(
            window,
            text="ADD PAYMENT",
            font=("Arial", 28, "bold")
        ).pack(pady=(35, 25))

        member = ctk.CTkEntry(
            window,
            width=380,
            height=45,
            placeholder_text="Member Name"
        )
        member.pack(pady=8)

        amount = ctk.CTkEntry(
            window,
            width=380,
            height=45,
            placeholder_text="Amount ₹"
        )
        amount.pack(pady=8)

        plan = ctk.CTkOptionMenu(
            window,
            width=380,
            height=45,
            values=[
                "Basic",
                "Standard",
                "Premium"
            ]
        )

        plan.set("Standard")
        plan.pack(pady=8)

        def save_payment():

            if member.get().strip() == "":
                messagebox.showwarning(
                    "Error",
                    "Enter member name."
                )
                return

            try:
                value = float(amount.get())
            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Enter a valid amount."
                )
                return

            conn = sqlite3.connect(DB)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO payments
                (member, amount, plan, payment_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                member.get(),
                value,
                plan.get(),
                datetime.now().strftime("%Y-%m-%d"),
                "Paid"
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Payment",
                "Payment recorded successfully!"
            )

            window.destroy()

            payments_page()

        ctk.CTkButton(
            window,
            text="SAVE PAYMENT",
            width=380,
            height=48,
            font=("Arial", 15, "bold"),
            command=save_payment
        ).pack(pady=25)

    # ========================================================
    # BMI CALCULATOR
    # ========================================================

    def bmi_page():

        clear()

        ctk.CTkLabel(
            content,
            text="BMI Calculator",
            font=("Arial", 32, "bold")
        ).pack(
            anchor="w",
            padx=40,
            pady=(35, 10)
        )

        ctk.CTkLabel(
            content,
            text="Calculate Body Mass Index",
            font=("Arial", 14)
        ).pack(
            anchor="w",
            padx=40
        )

        card = ctk.CTkFrame(
            content,
            fg_color="#252525",
            corner_radius=15
        )

        card.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        height = ctk.CTkEntry(
            card,
            width=400,
            height=45,
            placeholder_text="Height in cm"
        )
        height.pack(pady=(80, 10))

        weight = ctk.CTkEntry(
            card,
            width=400,
            height=45,
            placeholder_text="Weight in kg"
        )
        weight.pack(pady=10)

        result = ctk.CTkLabel(
            card,
            text="BMI: --",
            font=("Arial", 28, "bold")
        )

        result.pack(pady=25)

        category = ctk.CTkLabel(
            card,
            text="",
            font=("Arial", 17)
        )

        category.pack()

        def calculate():

            try:

                h = float(height.get()) / 100
                w = float(weight.get())

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

            except:

                messagebox.showerror(
                    "Error",
                    "Please enter valid numbers."
                )

        ctk.CTkButton(
            card,
            text="CALCULATE BMI",
            width=400,
            height=45,
            command=calculate
        ).pack(pady=20)

    # ========================================================
    # WORKOUT PLANS
    # ========================================================

    def workout_page():

        clear()

        ctk.CTkLabel(
            content,
            text="Workout Plans",
            font=("Arial", 32, "bold")
        ).pack(
            anchor="w",
            padx=40,
            pady=(35, 10)
        )

        ctk.CTkLabel(
            content,
            text="Training programs for gym members",
            font=("Arial", 14)
        ).pack(
            anchor="w",
            padx=40
        )

        plans = [
            ("BEGINNER", "Full Body", "3 Days / Week"),
            ("MUSCLE BUILDING", "Push Pull Legs", "6 Days / Week"),
            ("FAT LOSS", "Cardio + Strength", "5 Days / Week"),
            ("STRENGTH", "Power Training", "4 Days / Week")
        ]

        frame = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        for i, plan_data in enumerate(plans):

            card = ctk.CTkFrame(
                frame,
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
                text=plan_data[0],
                font=("Arial", 20, "bold")
            ).pack(
                anchor="w",
                padx=25,
                pady=(30, 5)
            )

            ctk.CTkLabel(
                card,
                text=plan_data[1],
                font=("Arial", 16)
            ).pack(
                anchor="w",
                padx=25
            )

            ctk.CTkLabel(
                card,
                text=plan_data[2],
                font=("Arial", 13)
            ).pack(
                anchor="w",
                padx=25,
                pady=5
            )

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

    # ========================================================
    # SIDEBAR
    # ========================================================

    side_button(
        "  🏠   Dashboard",
        home
    )

    side_button(
        "  👥   Members",
        members_page
    )

    side_button(
        "  💳   Payments",
        payments_page
    )

    side_button(
        "  🧮   BMI Calculator",
        bmi_page
    )

    side_button(
        "  🏋   Workout Plans",
        workout_page
    )

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    def logout():

        if messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        ):

            app.destroy()
            create_login()

    ctk.CTkButton(
        sidebar,
        text="  🚪   Logout",
        height=45,
        fg_color="#8b2525",
        hover_color="#b52b2b",
        command=logout
    ).pack(
        side="bottom",
        fill="x",
        padx=18,
        pady=25
    )

    # Start dashboard
    home()

    app.mainloop()


# ============================================================
# LOGIN WINDOW
# ============================================================

def create_login():

    global login_window
    global username_entry
    global password_entry

    login_window = ctk.CTk()

    login_window.title(
        "Apex Fitness | Login"
    )

    login_window.geometry(
        "1000x650"
    )

    login_window.resizable(
        False,
        False
    )

    card = ctk.CTkFrame(
        login_window,
        width=600,
        height=500,
        corner_radius=20
    )

    card.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    ctk.CTkLabel(
        card,
        text="APEX FITNESS",
        font=("Arial", 38, "bold")
    ).pack(
        pady=(65, 5)
    )

    ctk.CTkLabel(
        card,
        text="GYM MANAGEMENT SYSTEM",
        font=("Arial", 16)
    ).pack(
        pady=(0, 35)
    )

    username_entry = ctk.CTkEntry(
        card,
        width=400,
        height=45,
        placeholder_text="Username"
    )

    username_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(
        card,
        width=400,
        height=45,
        placeholder_text="Password",
        show="*"
    )

    password_entry.pack(pady=10)

    ctk.CTkButton(
        card,
        text="LOGIN",
        width=400,
        height=48,
        font=("Arial", 16, "bold"),
        command=login
    ).pack(
        pady=(25, 15)
    )

    ctk.CTkLabel(
        card,
        text="Demo Login: admin / admin123",
        font=("Arial", 13)
    ).pack()

    password_entry.bind(
        "<Return>",
        lambda event: login()
    )

    login_window.mainloop()


# ============================================================
# START
# ============================================================

create_login()
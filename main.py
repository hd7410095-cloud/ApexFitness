from flask import Flask, request, redirect, url_for, session, render_template_string, flash, get_flashed_messages
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
import os
import secrets

# ============================================================
# APEX FITNESS - GYM MANAGEMENT SYSTEM
# WEB VERSION - COMPLETE SINGLE FILE APPLICATION
# Run with: python main.py
# Open: http://127.0.0.1:5000
# Demo login: admin / admin123
# ============================================================

app = Flask(__name__)
# Use a Render environment variable in production; generate a temporary key for local development.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "apex_fitness.db")

PLANS = {
    "Basic": {"days": 30, "price": 999},
    "Standard": {"days": 90, "price": 2499},
    "Premium": {"days": 365, "price": 7999},
}

WORKOUTS = [
    {
        "name": "BEGINNER",
        "type": "Full Body",
        "frequency": "3 Days / Week",
        "description": "Perfect starting program for new gym members.",
        "exercises": ["Bodyweight Squats", "Push Ups", "Lat Pulldown",
                      "Dumbbell Shoulder Press", "Plank"],
    },
    {
        "name": "MUSCLE BUILDING",
        "type": "Push Pull Legs",
        "frequency": "6 Days / Week",
        "description": "A structured hypertrophy-focused training program.",
        "exercises": ["Bench Press", "Rows", "Shoulder Press",
                      "Bicep Curls", "Tricep Extensions", "Leg Press"],
    },
    {
        "name": "FAT LOSS",
        "type": "Cardio + Strength",
        "frequency": "5 Days / Week",
        "description": "Combination of cardio and resistance training.",
        "exercises": ["Walking", "Cycling", "Bodyweight Squats",
                      "Push Ups", "Core Training"],
    },
    {
        "name": "STRENGTH",
        "type": "Power Training",
        "frequency": "4 Days / Week",
        "description": "Progressive strength training for experienced members.",
        "exercises": ["Deadlift", "Squat", "Bench Press",
                      "Overhead Press", "Barbell Row"],
    },
]


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            plan TEXT NOT NULL,
            join_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            member TEXT NOT NULL,
            amount REAL NOT NULL,
            plan TEXT NOT NULL,
            payment_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Paid',
            FOREIGN KEY(member_id) REFERENCES members(id)
        )
    """)
    conn.commit()
    conn.close()
    update_expired_members()


def update_expired_members():
    today = datetime.now().date()
    conn = get_db()
    rows = conn.execute("SELECT id, expiry_date FROM members").fetchall()

    for row in rows:
        try:
            expiry = datetime.strptime(row["expiry_date"], "%Y-%m-%d").date()
            status = "Expired" if expiry < today else "Active"
            conn.execute(
                "UPDATE members SET status=? WHERE id=?",
                (status, row["id"])
            )
        except (ValueError, TypeError):
            pass

    conn.commit()
    conn.close()


initialize_database()


def scalar(sql, params=()):
    conn = get_db()
    value = conn.execute(sql, params).fetchone()[0]
    conn.close()
    return value


def member_has_paid(member_id):
    return scalar(
        "SELECT COUNT(*) FROM payments WHERE member_id=? AND status='Paid'",
        (member_id,)
    ) > 0


# ============================================================
# AUTHENTICATION
# ============================================================

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ============================================================
# COMMON HTML
# ============================================================

BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} | Apex Fitness</title>
<style>
:root{
    --bg:#0b0f14;
    --panel:#111820;
    --panel2:#17212b;
    --border:#263340;
    --text:#f4f7fa;
    --muted:#8d9aa8;
    --accent:#ff4d30;
    --accent2:#ff704d;
    --green:#32d583;
    --red:#ff5c5c;
    --yellow:#f6c344;
    --shadow:0 18px 45px rgba(0,0,0,.28);
}
*{box-sizing:border-box}
body{
    margin:0;background:linear-gradient(135deg,#080b10,#111820);
    color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif;
}
a{text-decoration:none;color:inherit}
.layout{display:flex;min-height:100vh}
.sidebar{
    width:245px;background:#090d12;border-right:1px solid var(--border);
    padding:25px 16px;position:fixed;top:0;bottom:0;left:0;z-index:10;
}
.brand{text-align:center;margin-bottom:30px}
.brand .apex{font-size:32px;font-weight:900;letter-spacing:4px}
.brand .fitness{font-size:17px;font-weight:800;letter-spacing:5px;color:var(--accent)}
.brand small{display:block;color:var(--muted);margin-top:7px;font-size:10px;letter-spacing:2px}
.nav-title{font-size:10px;color:#657281;letter-spacing:2px;margin:20px 10px 8px}
.nav a{
    display:flex;align-items:center;gap:12px;padding:13px 14px;margin:5px 0;
    border-radius:10px;color:#aeb8c2;transition:.2s;
}
.nav a:hover,.nav a.active{background:#18212a;color:#fff}
.nav a.active{border-left:3px solid var(--accent)}
.logout{
    position:absolute;bottom:20px;left:16px;right:16px;
    background:#421d1d!important;color:#ff8585!important;
}
.main{margin-left:245px;width:calc(100% - 245px);padding:30px 36px}
.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:26px}
.page-title h1{margin:0;font-size:32px}
.page-title p{margin:6px 0 0;color:var(--muted)}
.user-pill{
    background:var(--panel);border:1px solid var(--border);padding:10px 15px;
    border-radius:30px;color:#c8d0d8
}
.grid{display:grid;gap:18px}
.stats{grid-template-columns:repeat(4,1fr)}
.card{
    background:linear-gradient(145deg,var(--panel),#0e151d);
    border:1px solid var(--border);border-radius:16px;padding:22px;box-shadow:var(--shadow)
}
.stat-label{color:var(--muted);font-size:12px;font-weight:700;letter-spacing:1px}
.stat-value{font-size:30px;font-weight:900;margin-top:8px}
.stat-icon{float:right;font-size:25px}
.two{grid-template-columns:1.4fr 1fr}
.three{grid-template-columns:repeat(3,1fr)}
.section-title{font-size:20px;font-weight:800;margin:0 0 18px}
.btn{
    border:0;border-radius:9px;padding:11px 16px;background:var(--accent);
    color:white;font-weight:800;cursor:pointer;display:inline-block
}
.btn:hover{background:var(--accent2)}
.btn.secondary{background:#26323d}
.btn.danger{background:#702626}
.btn.success{background:#17663f}
.actions{display:flex;gap:10px;flex-wrap:wrap}
.table-wrap{overflow:auto}
table{width:100%;border-collapse:collapse;min-width:850px}
th,td{padding:14px 12px;text-align:left;border-bottom:1px solid var(--border)}
th{color:#84919e;font-size:11px;letter-spacing:1px}
td{font-size:13px}
tr:hover td{background:rgba(255,255,255,.015)}
.badge{padding:5px 9px;border-radius:20px;font-size:11px;font-weight:800}
.active{background:#123e2b;color:#49e69a}
.expired{background:#4b1c1c;color:#ff7a7a}
.paid{background:#123e2b;color:#49e69a}
.unpaid{background:#4b1c1c;color:#ff7a7a}
.flash{
    padding:13px 16px;border-radius:10px;background:#17212b;border:1px solid var(--border);
    margin-bottom:18px
}
.flash.success{border-color:#236544}.flash.error{border-color:#773232}
.form-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.form-group label{display:block;color:#aeb8c2;font-size:12px;font-weight:700;margin-bottom:7px}
input,select{
    width:100%;background:#0c1218;color:#fff;border:1px solid var(--border);
    border-radius:9px;padding:13px;font-size:14px;outline:none
}
input:focus,select:focus{border-color:var(--accent)}
.form-full{grid-column:1/-1}
.empty{text-align:center;color:var(--muted);padding:55px}
.searchbar{display:flex;gap:10px;margin-bottom:18px}
.searchbar input{max-width:400px}
.quick{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.quick .btn{padding:18px;text-align:center}
.plan-card h3{margin:0;color:var(--accent)}
.plan-card h2{margin:8px 0}
.plan-card ul{padding-left:20px;color:#b9c2ca;line-height:1.9}
.progress{height:9px;background:#222d37;border-radius:10px;overflow:hidden;margin-top:8px}
.progress span{display:block;height:100%;background:var(--accent)}
.kpi{display:flex;justify-content:space-between;padding:13px 0;border-bottom:1px solid var(--border)}
.kpi:last-child{border-bottom:0}
.login-page{min-height:100vh;display:grid;place-items:center;padding:20px}
.login-card{
    width:470px;background:rgba(17,24,32,.95);border:1px solid var(--border);
    border-radius:22px;padding:45px;box-shadow:var(--shadow)
}
.login-logo{text-align:center;margin-bottom:35px}
.login-logo h1{font-size:48px;letter-spacing:7px;margin:0}
.login-logo h2{font-size:20px;letter-spacing:8px;color:var(--accent);margin:0}
.login-logo p{color:var(--muted);font-size:11px;letter-spacing:2px}
.form-stack{display:grid;gap:15px}
.note{font-size:12px;color:var(--muted);text-align:center;margin-top:18px}
.alert-bmi{font-size:34px;font-weight:900;text-align:center;margin:25px 0 5px}
.bmi-category{text-align:center;color:var(--accent);font-size:18px;font-weight:800}
@media(max-width:1000px){
    .sidebar{width:190px}.main{margin-left:190px;width:calc(100% - 190px);padding:22px}
    .stats{grid-template-columns:repeat(2,1fr)}.two,.three{grid-template-columns:1fr}
}
@media(max-width:700px){
    .sidebar{position:relative;width:100%;height:auto}.layout{display:block}
    .main{margin:0;width:100%}.nav{display:grid;grid-template-columns:1fr 1fr}
    .logout{position:static;margin-top:12px}.form-grid{grid-template-columns:1fr}
    .login-card{width:100%}.quick{grid-template-columns:1fr}
}
</style>
</head>
<body>
{% if session.get('logged_in') %}
<div class="layout">
<aside class="sidebar">
    <div class="brand">
        <div class="apex">APEX</div>
        <div class="fitness">FITNESS</div>
        <small>GYM MANAGEMENT SYSTEM</small>
    </div>
    <div class="nav-title">MAIN MENU</div>
    <nav class="nav">
        <a href="{{url_for('dashboard')}}" class="{{'active' if page=='dashboard' else ''}}">🏠 Dashboard</a>
        <a href="{{url_for('members')}}" class="{{'active' if page=='members' else ''}}">👥 Members</a>
        <a href="{{url_for('payments')}}" class="{{'active' if page=='payments' else ''}}">💳 Payments</a>
        <a href="{{url_for('analytics')}}" class="{{'active' if page=='analytics' else ''}}">📊 Analytics</a>
        <a href="{{url_for('bmi')}}" class="{{'active' if page=='bmi' else ''}}">🧮 BMI Calculator</a>
        <a href="{{url_for('workouts')}}" class="{{'active' if page=='workouts' else ''}}">🏋 Workout Plans</a>
    </nav>
    <a class="nav logout" href="{{url_for('logout')}}">🚪 Logout</a>
</aside>
<main class="main">
    <div class="topbar">
        <div class="page-title">
            <h1>{{heading}}</h1>
            <p>{{subtitle}}</p>
        </div>
        <div class="user-pill">👤 Admin</div>
    </div>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% for category, message in messages %}
            <div class="flash {{category}}">{{message}}</div>
        {% endfor %}
    {% endwith %}
    {{content|safe}}
</main>
</div>
{% else %}
{{content|safe}}
{% endif %}
</body>
</html>
"""


def render_page(title, heading, subtitle, page, template, **context):
    content = render_template_string(template, **context)
    return render_template_string(
        BASE,
        title=title,
        heading=heading,
        subtitle=subtitle,
        page=page,
        content=content,
    )


# ============================================================
# LOGIN
# ============================================================

LOGIN_TEMPLATE = """
<div class="login-page">
<div class="login-card">
    <div class="login-logo">
        <h1>APEX</h1>
        <h2>FITNESS</h2>
        <p>GYM MANAGEMENT SYSTEM</p>
    </div>
    <form method="post" class="form-stack">
        <div class="form-group">
            <label>USERNAME</label>
            <input name="username" placeholder="Enter username" required autofocus>
        </div>
        <div class="form-group">
            <label>PASSWORD</label>
            <input type="password" name="password" placeholder="Enter password" required>
        </div>
        <button class="btn" type="submit">LOGIN TO DASHBOARD</button>
    </form>
    <div class="note">Demo Login: <b>admin</b> / <b>admin123</b></div>
</div>
</div>
"""


@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username.lower() == "admin" and password == "admin123":
            session["logged_in"] = True
            session["username"] = "admin"
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    content = render_template_string(
        LOGIN_TEMPLATE,
        get_flashed_messages=lambda **kwargs: []
    )
    # Login needs flashes outside the dashboard shell.
    messages = get_flashed_messages(with_categories=True)
    if messages:
        alerts = "".join(
            f'<div class="flash error">{m}</div>' for _, m in messages
        )
        content = content.replace(
            '<div class="login-card">',
            '<div class="login-card">' + alerts,
            1
        )

    return render_template_string(
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Apex Fitness Login</title><style>'
        + BASE.split("<style>",1)[1].split("</style>",1)[0]
        + '</style></head><body>' + content + '</body></html>'
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ============================================================
# DASHBOARD
# ============================================================

DASHBOARD_TEMPLATE = """
<div class="grid stats">
    <div class="card"><span class="stat-icon">👥</span><div class="stat-label">TOTAL MEMBERS</div><div class="stat-value">{{total_members}}</div></div>
    <div class="card"><span class="stat-icon">🟢</span><div class="stat-label">ACTIVE MEMBERS</div><div class="stat-value">{{active_members}}</div></div>
    <div class="card"><span class="stat-icon">💳</span><div class="stat-label">PAYMENTS</div><div class="stat-value">{{payment_count}}</div></div>
    <div class="card"><span class="stat-icon">₹</span><div class="stat-label">TOTAL REVENUE</div><div class="stat-value">₹{{"{:,.0f}".format(revenue)}}</div></div>
</div>

<div class="card" style="margin-top:20px">
    <div class="section-title">Quick Actions</div>
    <div class="quick">
        <a class="btn" href="{{url_for('add_member')}}">＋ ADD NEW MEMBER</a>
        <a class="btn secondary" href="{{url_for('add_payment')}}">💳 RECORD PAYMENT</a>
        <a class="btn secondary" href="{{url_for('analytics')}}">📊 VIEW ANALYTICS</a>
    </div>
</div>

<div class="grid two" style="margin-top:20px">
<div class="card">
    <div class="section-title">Recent Members</div>
    {% if recent_members %}
    <div class="table-wrap"><table>
        <thead><tr><th>NAME</th><th>PLAN</th><th>EXPIRY</th><th>STATUS</th></tr></thead>
        <tbody>
        {% for m in recent_members %}
        <tr>
            <td><b>{{m.name}}</b><br><small style="color:var(--muted)">{{m.phone or 'No phone'}}</small></td>
            <td>{{m.plan}}</td><td>{{m.expiry_date}}</td>
            <td><span class="badge {{m.status|lower}}">{{m.status}}</span></td>
        </tr>
        {% endfor %}
        </tbody>
    </table></div>
    {% else %}<div class="empty">No members added yet.</div>{% endif %}
</div>
<div class="card">
    <div class="section-title">Membership Overview</div>
    <div class="kpi"><span>Basic</span><b>{{basic}}</b></div>
    <div class="kpi"><span>Standard</span><b>{{standard}}</b></div>
    <div class="kpi"><span>Premium</span><b>{{premium}}</b></div>
    <div class="kpi"><span>Expired</span><b style="color:var(--red)">{{expired}}</b></div>
</div>
</div>
"""


@app.route("/dashboard")
@login_required
def dashboard():
    update_expired_members()
    conn = get_db()
    recent = conn.execute(
        "SELECT * FROM members ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()

    return render_page(
        "Dashboard", "Welcome back, Admin 👋",
        "Apex Fitness Management Dashboard", "dashboard",
        DASHBOARD_TEMPLATE,
        total_members=scalar("SELECT COUNT(*) FROM members"),
        active_members=scalar("SELECT COUNT(*) FROM members WHERE status='Active'"),
        payment_count=scalar("SELECT COUNT(*) FROM payments"),
        revenue=scalar("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='Paid'"),
        recent_members=recent,
        basic=scalar("SELECT COUNT(*) FROM members WHERE plan='Basic'"),
        standard=scalar("SELECT COUNT(*) FROM members WHERE plan='Standard'"),
        premium=scalar("SELECT COUNT(*) FROM members WHERE plan='Premium'"),
        expired=scalar("SELECT COUNT(*) FROM members WHERE status='Expired'"),
    )


# ============================================================
# MEMBERS
# ============================================================

MEMBERS_TEMPLATE = """
<div class="actions" style="justify-content:space-between;margin-bottom:16px">
    <form class="searchbar" method="get">
        <input name="q" value="{{q}}" placeholder="Search name, phone or email...">
        <button class="btn" type="submit">SEARCH</button>
        {% if q %}<a class="btn secondary" href="{{url_for('members')}}">CLEAR</a>{% endif %}
    </form>
    <a class="btn" href="{{url_for('add_member')}}">＋ ADD MEMBER</a>
</div>
<div class="card">
<div class="table-wrap">
<table>
<thead><tr><th>ID</th><th>MEMBER</th><th>PHONE</th><th>PLAN</th><th>JOIN DATE</th><th>EXPIRY</th><th>STATUS</th><th>PAYMENT</th><th>ACTIONS</th></tr></thead>
<tbody>
{% for m in members %}
<tr>
<td>#{{m.id}}</td>
<td><b>{{m.name}}</b><br><small style="color:var(--muted)">{{m.email or 'No email'}}</small></td>
<td>{{m.phone or '—'}}</td>
<td>{{m.plan}}</td>
<td>{{m.join_date}}</td>
<td>{{m.expiry_date}}</td>
<td><span class="badge {{m.status|lower}}">{{m.status}}</span></td>
<td>
{% if payment_status[m.id] %}<span class="badge paid">✓ PAID</span>
{% else %}<span class="badge unpaid">✗ UNPAID</span>{% endif %}
</td>
<td>
<div class="actions">
<a class="btn secondary" href="{{url_for('edit_member', member_id=m.id)}}">EDIT</a>
<a class="btn danger" href="{{url_for('delete_member', member_id=m.id)}}" onclick="return confirm('Delete this member and their payment records?')">DELETE</a>
</div>
</td>
</tr>
{% else %}
<tr><td colspan="9" class="empty">No members found.</td></tr>
{% endfor %}
</tbody>
</table>
</div>
</div>
"""


@app.route("/members")
@login_required
def members():
    update_expired_members()
    q = request.args.get("q", "").strip()
    conn = get_db()
    if q:
        like = f"%{q}%"
        rows = conn.execute("""
            SELECT * FROM members
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            ORDER BY id DESC
        """, (like, like, like)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM members ORDER BY id DESC").fetchall()
    conn.close()

    statuses = {m["id"]: member_has_paid(m["id"]) for m in rows}
    return render_page(
        "Members", "Member Management",
        "Add, search, edit and manage gym members", "members",
        MEMBERS_TEMPLATE, members=rows, payment_status=statuses, q=q
    )


MEMBER_FORM_TEMPLATE = """
<div class="card" style="max-width:850px;margin:auto">
<form method="post">
<div class="form-grid">
<div class="form-group"><label>FULL NAME *</label><input name="name" value="{{member.name if member else ''}}" required></div>
<div class="form-group"><label>PHONE NUMBER</label><input name="phone" value="{{member.phone if member else ''}}" maxlength="10" placeholder="10 digit number"></div>
<div class="form-group"><label>EMAIL</label><input type="email" name="email" value="{{member.email if member else ''}}" placeholder="example@email.com"></div>
<div class="form-group"><label>MEMBERSHIP PLAN *</label>
<select name="plan">
{% for p in plans %}<option value="{{p}}" {% if (member.plan if member else 'Standard')==p %}selected{% endif %}>{{p}} — ₹{{"{:,.0f}".format(prices[p])}}</option>{% endfor %}
</select></div>
{% if member %}
<div class="form-group"><label>CURRENT EXPIRY DATE</label><input value="{{member.expiry_date}}" disabled></div>
{% endif %}
<div class="form-full actions" style="margin-top:10px">
<button class="btn" type="submit">{{'UPDATE MEMBER' if member else 'SAVE MEMBER'}}</button>
<a class="btn secondary" href="{{url_for('members')}}">CANCEL</a>
</div>
</div>
</form>
</div>
"""


def validate_member_form():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    plan = request.form.get("plan", "Standard").strip()

    if not name:
        return None, "Member name is required."
    if phone and (not phone.isdigit() or len(phone) != 10):
        return None, "Phone number must contain exactly 10 digits."
    if email and ("@" not in email or "." not in email):
        return None, "Please enter a valid email address."
    if plan not in PLANS:
        return None, "Invalid membership plan."

    return {"name": name, "phone": phone, "email": email, "plan": plan}, None


@app.route("/members/add", methods=["GET", "POST"])
@login_required
def add_member():
    if request.method == "POST":
        data, error = validate_member_form()
        if error:
            flash(error, "error")
        else:
            today = datetime.now()
            expiry = today + timedelta(days=PLANS[data["plan"]]["days"])
            conn = get_db()
            conn.execute("""
                INSERT INTO members
                (name,phone,email,plan,join_date,expiry_date,status)
                VALUES (?,?,?,?,?,?,?)
            """, (
                data["name"], data["phone"], data["email"], data["plan"],
                today.strftime("%Y-%m-%d"),
                expiry.strftime("%Y-%m-%d"), "Active"
            ))
            conn.commit()
            conn.close()
            flash(f"{data['name']} added successfully.", "success")
            return redirect(url_for("members"))

    return render_page(
        "Add Member", "Add New Member",
        "Create a new Apex Fitness membership", "members",
        MEMBER_FORM_TEMPLATE, member=None, plans=PLANS.keys(),
        prices={k: v["price"] for k, v in PLANS.items()}
    )


@app.route("/members/edit/<int:member_id>", methods=["GET", "POST"])
@login_required
def edit_member(member_id):
    conn = get_db()
    member = conn.execute(
        "SELECT * FROM members WHERE id=?", (member_id,)
    ).fetchone()

    if not member:
        conn.close()
        flash("Member not found.", "error")
        return redirect(url_for("members"))

    if request.method == "POST":
        data, error = validate_member_form()
        if error:
            flash(error, "error")
        else:
            conn.execute("""
                UPDATE members SET name=?, phone=?, email=?, plan=?
                WHERE id=?
            """, (
                data["name"], data["phone"], data["email"],
                data["plan"], member_id
            ))
            conn.commit()
            conn.close()
            flash("Member updated successfully.", "success")
            return redirect(url_for("members"))

    conn.close()
    return render_page(
        "Edit Member", "Edit Member",
        f"Update information for {member['name']}", "members",
        MEMBER_FORM_TEMPLATE, member=member, plans=PLANS.keys(),
        prices={k: v["price"] for k, v in PLANS.items()}
    )


@app.route("/members/delete/<int:member_id>")
@login_required
def delete_member(member_id):
    conn = get_db()
    member = conn.execute(
        "SELECT * FROM members WHERE id=?", (member_id,)
    ).fetchone()
    if member:
        conn.execute("DELETE FROM payments WHERE member_id=?", (member_id,))
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))
        conn.commit()
        flash(f"{member['name']} deleted successfully.", "success")
    conn.close()
    return redirect(url_for("members"))


# ============================================================
# PAYMENTS
# ============================================================

PAYMENTS_TEMPLATE = """
<div style="margin-bottom:16px;text-align:right">
<a class="btn" href="{{url_for('add_payment')}}">＋ ADD PAYMENT</a>
</div>
<div class="card">
<div class="table-wrap">
<table>
<thead><tr><th>ID</th><th>MEMBER</th><th>AMOUNT</th><th>PLAN</th><th>DATE</th><th>STATUS</th><th>ACTION</th></tr></thead>
<tbody>
{% for p in payments %}
<tr>
<td>#{{p.id}}</td><td><b>{{p.member}}</b></td>
<td><b>₹{{"{:,.2f}".format(p.amount)}}</b></td>
<td>{{p.plan}}</td><td>{{p.payment_date}}</td>
<td><span class="badge paid">{{p.status}}</span></td>
<td><a class="btn danger" href="{{url_for('delete_payment', payment_id=p.id)}}" onclick="return confirm('Delete this payment?')">DELETE</a></td>
</tr>
{% else %}
<tr><td colspan="7" class="empty">No payments recorded yet.</td></tr>
{% endfor %}
</tbody>
</table>
</div>
</div>
"""


@app.route("/payments")
@login_required
def payments():
    conn = get_db()
    rows = conn.execute("SELECT * FROM payments ORDER BY id DESC").fetchall()
    conn.close()
    return render_page(
        "Payments", "Payment Management",
        "Record and manage membership payments", "payments",
        PAYMENTS_TEMPLATE, payments=rows
    )


PAYMENT_FORM_TEMPLATE = """
<div class="card" style="max-width:700px;margin:auto">
<form method="post">
<div class="form-grid">
<div class="form-group form-full"><label>SELECT MEMBER *</label>
<select name="member_id" id="member_id" onchange="setPlan()" required>
{% for m in members %}<option value="{{m.id}}" data-plan="{{m.plan}}" data-price="{{prices[m.plan]}}" {% if selected_id==m.id %}selected{% endif %}>{{m.name}} — {{m.plan}}</option>{% endfor %}
</select></div>
<div class="form-group"><label>AMOUNT (₹) *</label><input id="amount" name="amount" type="number" min="1" step="0.01" value="{{default_amount}}" required></div>
<div class="form-group"><label>MEMBERSHIP PLAN</label><input id="plan_display" value="{{default_plan}}" disabled><input type="hidden" id="plan" name="plan" value="{{default_plan}}"></div>
<div class="form-full actions">
<button class="btn" type="submit">SAVE PAYMENT</button>
<a class="btn secondary" href="{{url_for('payments')}}">CANCEL</a>
</div>
</div>
</form>
</div>
<script>
function setPlan(){
    const s=document.getElementById('member_id');
    const o=s.options[s.selectedIndex];
    document.getElementById('plan_display').value=o.dataset.plan;
    document.getElementById('plan').value=o.dataset.plan;
    document.getElementById('amount').value=o.dataset.price;
}
</script>
"""


@app.route("/payments/add", methods=["GET", "POST"])
@login_required
def add_payment():
    conn = get_db()
    members_list = conn.execute(
        "SELECT * FROM members ORDER BY name"
    ).fetchall()

    if not members_list:
        conn.close()
        flash("Please add a member before recording a payment.", "error")
        return redirect(url_for("members"))

    selected_id = int(request.form.get("member_id", 0) or request.args.get("member_id", members_list[0]["id"]))
    selected = next((m for m in members_list if m["id"] == selected_id), members_list[0])

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", "0"))
            plan = request.form.get("plan", selected["plan"])
            if amount <= 0:
                raise ValueError
        except ValueError:
            conn.close()
            flash("Enter a valid amount greater than 0.", "error")
            return redirect(url_for("add_payment"))

        conn.execute("""
            INSERT INTO payments
            (member_id,member,amount,plan,payment_date,status)
            VALUES (?,?,?,?,?,?)
        """, (
            selected["id"], selected["name"], amount, plan,
            datetime.now().strftime("%Y-%m-%d"), "Paid"
        ))
        conn.commit()
        conn.close()
        flash(f"Payment of ₹{amount:,.2f} recorded for {selected['name']}.", "success")
        return redirect(url_for("payments"))

    conn.close()
    return render_page(
        "Add Payment", "Add Payment",
        "Record a membership payment", "payments",
        PAYMENT_FORM_TEMPLATE, members=members_list,
        selected_id=selected["id"], default_plan=selected["plan"],
        default_amount=PLANS[selected["plan"]]["price"],
        prices={k: v["price"] for k, v in PLANS.items()}
    )


@app.route("/payments/delete/<int:payment_id>")
@login_required
def delete_payment(payment_id):
    conn = get_db()
    conn.execute("DELETE FROM payments WHERE id=?", (payment_id,))
    conn.commit()
    conn.close()
    flash("Payment deleted successfully.", "success")
    return redirect(url_for("payments"))


# ============================================================
# ANALYTICS
# ============================================================

ANALYTICS_TEMPLATE = """
<div class="grid stats">
<div class="card"><div class="stat-label">TOTAL MEMBERS</div><div class="stat-value">{{total}}</div></div>
<div class="card"><div class="stat-label">ACTIVE MEMBERS</div><div class="stat-value">{{active}}</div></div>
<div class="card"><div class="stat-label">EXPIRED MEMBERS</div><div class="stat-value">{{expired}}</div></div>
<div class="card"><div class="stat-label">TOTAL REVENUE</div><div class="stat-value">₹{{"{:,.0f}".format(revenue)}}</div></div>
</div>

<div class="grid two" style="margin-top:20px">
<div class="card">
<div class="section-title">Membership Plans</div>
{% for name,count in plan_counts %}
<div class="kpi"><span>{{name}} Plan</span><b>{{count}} Members</b></div>
<div class="progress"><span style="width:{{(count/total*100 if total else 0)}}%"></span></div>
{% endfor %}
</div>
<div class="card">
<div class="section-title">Payment Summary</div>
<div class="kpi"><span>Paid Members</span><b>{{paid_members}}</b></div>
<div class="kpi"><span>Unpaid Members</span><b>{{unpaid_members}}</b></div>
<div class="kpi"><span>Total Payments</span><b>{{payment_count}}</b></div>
<div class="kpi"><span>Total Revenue</span><b>₹{{"{:,.2f}".format(revenue)}}</b></div>
</div>
</div>

<div class="card" style="margin-top:20px">
<div class="section-title">Recent Payments</div>
<div class="table-wrap"><table>
<thead><tr><th>MEMBER</th><th>PLAN</th><th>AMOUNT</th><th>DATE</th><th>STATUS</th></tr></thead>
<tbody>
{% for p in recent %}
<tr><td><b>{{p.member}}</b></td><td>{{p.plan}}</td><td>₹{{"{:,.2f}".format(p.amount)}}</td><td>{{p.payment_date}}</td><td><span class="badge paid">{{p.status}}</span></td></tr>
{% else %}
<tr><td colspan="5" class="empty">No payments recorded.</td></tr>
{% endfor %}
</tbody></table></div>
</div>
"""


@app.route("/analytics")
@login_required
def analytics():
    update_expired_members()
    total = scalar("SELECT COUNT(*) FROM members")
    active = scalar("SELECT COUNT(*) FROM members WHERE status='Active'")
    expired = scalar("SELECT COUNT(*) FROM members WHERE status='Expired'")
    revenue = scalar("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='Paid'")
    payment_count = scalar("SELECT COUNT(*) FROM payments")

    conn = get_db()
    recent = conn.execute(
        "SELECT * FROM payments ORDER BY id DESC LIMIT 8"
    ).fetchall()
    conn.close()

    all_members = get_db()
    member_rows = all_members.execute("SELECT id FROM members").fetchall()
    all_members.close()
    paid_members = sum(member_has_paid(m["id"]) for m in member_rows)

    return render_page(
        "Analytics", "Analytics & Reports",
        "Apex Fitness business overview", "analytics",
        ANALYTICS_TEMPLATE,
        total=total, active=active, expired=expired, revenue=revenue,
        payment_count=payment_count,
        paid_members=paid_members,
        unpaid_members=total-paid_members,
        plan_counts=[
            ("Basic", scalar("SELECT COUNT(*) FROM members WHERE plan='Basic'")),
            ("Standard", scalar("SELECT COUNT(*) FROM members WHERE plan='Standard'")),
            ("Premium", scalar("SELECT COUNT(*) FROM members WHERE plan='Premium'")),
        ],
        recent=recent
    )


# ============================================================
# BMI
# ============================================================

BMI_TEMPLATE = """
<div class="card" style="max-width:650px;margin:auto">
<form method="post">
<div class="form-grid">
<div class="form-group"><label>HEIGHT (CM)</label><input name="height" type="number" step="0.1" min="1" value="{{height}}" required></div>
<div class="form-group"><label>WEIGHT (KG)</label><input name="weight" type="number" step="0.1" min="1" value="{{weight}}" required></div>
<div class="form-full"><button class="btn" style="width:100%" type="submit">CALCULATE BMI</button></div>
</div>
</form>
{% if bmi is not none %}
<div class="alert-bmi">BMI: {{bmi}}</div>
<div class="bmi-category">{{category}}</div>
<div style="margin-top:28px">
<div class="kpi"><span>Underweight</span><b>&lt; 18.5</b></div>
<div class="kpi"><span>Normal Weight</span><b>18.5 – 24.9</b></div>
<div class="kpi"><span>Overweight</span><b>25 – 29.9</b></div>
<div class="kpi"><span>Obese</span><b>30+</b></div>
</div>
{% endif %}
</div>
"""


@app.route("/bmi", methods=["GET", "POST"])
@login_required
def bmi():
    result = None
    category = ""
    height = ""
    weight = ""

    if request.method == "POST":
        height = request.form.get("height", "")
        weight = request.form.get("weight", "")
        try:
            h = float(height) / 100
            w = float(weight)
            if h <= 0 or w <= 0:
                raise ValueError
            result = round(w / (h * h), 1)
            if result < 18.5:
                category = "Underweight"
            elif result < 25:
                category = "Normal Weight"
            elif result < 30:
                category = "Overweight"
            else:
                category = "Obese"
        except ValueError:
            flash("Please enter valid positive numbers.", "error")

    return render_page(
        "BMI Calculator", "BMI Calculator",
        "Calculate Body Mass Index", "bmi",
        BMI_TEMPLATE, bmi=result, category=category,
        height=height, weight=weight
    )


# ============================================================
# WORKOUT PLANS
# ============================================================

WORKOUT_TEMPLATE = """
<div class="grid two">
{% for plan in workouts %}
<div class="card plan-card">
<h3>{{plan.name}}</h3>
<h2>{{plan.type}}</h2>
<p style="color:var(--muted)">{{plan.frequency}}</p>
<p>{{plan.description}}</p>
<h4>Exercises</h4>
<ul>
{% for exercise in plan.exercises %}<li>{{exercise}}</li>{% endfor %}
</ul>
</div>
{% endfor %}
</div>
"""


@app.route("/workouts")
@login_required
def workouts():
    return render_page(
        "Workout Plans", "Workout Plans",
        "Training programs for Apex Fitness members", "workouts",
        WORKOUT_TEMPLATE, workouts=WORKOUTS
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    if session.get("logged_in"):
        flash("The requested page was not found.", "error")
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.errorhandler(500)
def server_error(error):
    return "Apex Fitness encountered an internal error. Check the terminal for details.", 500


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    initialize_database()
    print("=" * 60)
    print("        APEX FITNESS - GYM MANAGEMENT SYSTEM")
    print("=" * 60)
    print("Login: admin / admin123")
    print("Website: http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server.")
    print("=" * 60)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

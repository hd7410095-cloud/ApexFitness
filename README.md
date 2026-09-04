# APEX FITNESS — Gym Management System

A portfolio-ready gym management web application built with **Python, Flask, SQLite, HTML, CSS and JavaScript**.

## Features
- Admin login
- Dashboard with gym statistics
- Member management
- Membership plans and expiry tracking
- Payment management
- Analytics
- BMI calculator
- Workout plans
- SQLite database

## Tech Stack
- Python
- Flask
- SQLite
- HTML / CSS / JavaScript
- Git / GitHub

## Demo Login
**Username:** `admin`  
**Password:** `admin123`

This is a demonstration account for portfolio/recruiter use. Do not use these credentials for real or sensitive data.

## Run Locally

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Then open `http://127.0.0.1:5000`.

## Deploy on Render

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
gunicorn main:app
```

Set a `SECRET_KEY` environment variable in Render.

> Note: SQLite is suitable for this portfolio demo, but its local file is intentionally excluded from Git. Demo data can be recreated locally; production applications should use a managed database.

## Project
Built as a third-year B.Sc. IT portfolio project.

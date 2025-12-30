from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

# Init auth
login_manager.init_app(app)
login_manager.login_view = "login"

# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401

# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(
            request.form["username","(email")"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("index"))

        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="In dein Konto einloggen",
        action=url_for("login"),
        button_label="Einloggen",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ok = register_user(username, password)
        if ok:
            return redirect(url_for("login"))

        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Neues Konto erstellen",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Du hast bereits ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Einloggen"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

from datetime import datetime

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form.get("username")
        password = request.form.get("password")
        user_data = db_read("SELECT id, password FROM users WHERE username=%s OR email=%s", (login_input, login_input))
        if user_data and user_data[0]['password'] == password:
            user = User(user_data[0]['id'])
            login_user(user)
            return redirect(url_for("index"))
        return "Login fehlgeschlagen"
    return render_template("login.html")

from datetime import datetime

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    
    # Werte aus der URL/Formular holen
    selected_month = request.args.get('month', current_month)
    budget = request.args.get("budget_val", 2000.0, type=float)

    if request.method == "POST":
        content = request.form.get("contents")
        due = request.form.get("due_at")
        amount = request.form.get("amount")
        if content and due and amount:
            db_write("INSERT INTO todos (user_id, content, due, amount, month_year) VALUES (%s, %s, %s, %s, %s)", 
                     (current_user.id, content, due, amount, selected_month))
        return redirect(url_for("index", month=selected_month, budget_val=budget))

    # Alle Einträge für den gewählten Monat laden
    todos = db_read("SELECT id, content, due, amount FROM todos WHERE user_id=%s AND month_year=%s ORDER BY due", 
                    (current_user.id, selected_month))
    
    if not todos:
        todos = []

    # Berechnungen für das Dashboard
    total = sum(float(t['amount']) for t in todos if t.get('amount'))
    remaining = budget - total
    
    return render_template("meine_fixkosten.html", 
                           todos=todos, 
                           total=total, 
                           budget=budget, 
                           remaining=remaining, 
                           selected_month=selected_month)

@app.route("/delete/<int:todo_id>")
@login_required
def delete(todo_id):
    # Monat und Budget sichern, damit man nach dem Löschen nicht im falschen Monat landet
    selected_month = request.args.get('month')
    budget = request.args.get('budget_val')
    db_write("DELETE FROM todos WHERE id=%s AND user_id=%s", (todo_id, current_user.id))
    return redirect(url_for("index", month=selected_month, budget_val=budget))


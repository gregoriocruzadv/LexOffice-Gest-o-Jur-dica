from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

def get_db():
    return sqlite3.connect(DB)

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        sobrenome TEXT,
        email TEXT UNIQUE,
        senha TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
    )
    """)

    conn.commit()
    conn.close()

# ROTAS
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

# LOGIN
@app.route("/api/login", methods=["POST"])
def login():
    d = request.json
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT id, senha, nome FROM usuarios WHERE email=?", (d["email"],))
    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user[1], d["senha"]):
        session["user"] = {"id": user[0], "nome": user[2]}
        return jsonify({"ok": True, "nome": user[2]})

    return jsonify({"erro": "Login inválido"}), 401

# REGISTRO
@app.route("/api/register", methods=["POST"])
def register():
    d = request.json

    conn = get_db()
    c = conn.cursor()

    senha_hash = generate_password_hash(d["senha"])

    try:
        c.execute("""
        INSERT INTO usuarios (nome, sobrenome, email, senha)
        VALUES (?, ?, ?, ?)
        """, (d["nome"], d["sobrenome"], d["email"], senha_hash))

        conn.commit()
    except:
        conn.close()
        return jsonify({"erro": "Email já cadastrado"}), 400

    conn.close()
    return jsonify({"ok": True})

# CLIENTES
@app.route("/api/clientes", methods=["GET", "POST"])
def clientes():
    if "user" not in session:
        return jsonify({"erro": "Não autorizado"}), 403

    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        d = request.json
        c.execute("INSERT INTO clientes (nome) VALUES (?)", (d["nome"],))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})

    c.execute("SELECT * FROM clientes")
    rows = c.fetchall()
    conn.close()

    return jsonify([{"id": r[0], "nome": r[1]} for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

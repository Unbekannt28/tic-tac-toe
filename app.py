from flask import Flask, render_template, request, redirect, session
from werkzeug import security
import sqlite3

# connect to database
con = sqlite3.connect("database.db")
cur = con.cursor()

# create database, if it was not initialized before
cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR NOT NULL, password VARCHAR NOT NULL, games_won INTEGER DEFAULT 0, games_lost INTEGER DEFAULT 0, games_played INTEGER DEFAULT 0);")
cur.execute("CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY AUTOINCREMENT, is_over BOOLEAN DEFAULT false, date TIMESTAMP NOT NULL, player_1 INTEGER NOT NULL, player_2 INTEGER NOT NULL, winner INTEGER);")
cur.execute("CREATE TABLE IF NOT EXISTS moves(id INTEGER PRIMARY KEY AUTOINCREMENT, game INTEGER NOT NULL, turn INTEGER NOT NULL, player INTEGER NOT NULL, position_x INTEGER NOT NULL, position_y INTEGER NOT NULL);")

con.commit()
con.close()

app = Flask(__name__, static_url_path="/")

# Secret key for sessions
app.secret_key = "SUPER_SECURE_KEY_100%"

# Index
@app.route("/")
def main():
    return render_template("index.html")

# Register
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register/create_user", methods=["POST"])
def create_user():
    username = request.form.get("username")
    password = request.form.get("password")
    hashed_password = security.generate_password_hash(password)

    # Database communication
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO users (name, password) VALUES (?, ?)", (username, hashed_password))
    con.commit()
    response = cur.execute("SELECT id FROM users WHERE name=?", (username,))
    user_id = response.fetchone()[0]
    con.close()
    
    # Login the newly registered user
    new_session(user_id, username)

    return redirect("/lobby")

# Login
def new_session(user_id, username):
    session["logged_in"] = True
    session["user_id"] = user_id
    session["username"] = username

def close_session():
    session["logged_in"] = None
    session["user_id"] = None
    session["username"] = None

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login/start_session", methods=["POST"])
def start_session():
    username = request.form.get("username")
    password = request.form.get("password")

    # Database communication
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    response = cur.execute("SELECT id, password FROM users WHERE name=?", (username,))
    data = response.fetchone()
    con.close()

    # Check if user exists
    if data == None:
        return redirect("/login") #TODO: add error message "wrong username or password"
    
    # Check password
    if not security.check_password_hash(data[1], password):
        return redirect("/login") #TODO: add error message "wrong username or password"
    
    # Login successful
    new_session(data[0], username)

    return redirect("/lobby")

# Game Lobby
@app.route("/lobby")
def lobby():
    return render_template("lobby.html")

@app.route("/lobby/create_game", methods=["POST"])
def create_game():
    opponent = request.form.get("opponent")

@app.route("/play")
def play():
    #Will be fild with X and Os through the game.
    fields = [["", "", ""], ["", "", ""], ["", "", ""]]
    return render_template("tictactoe_game.html", columns = fields)

if __name__ == "__main__":
    app.run(debug=True)
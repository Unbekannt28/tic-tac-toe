from flask import Flask, render_template, request, redirect
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
    con.close()
    
    #TODO: login
    return redirect("/lobby")

# Login
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login/start_session")
def start_session():
    pass

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
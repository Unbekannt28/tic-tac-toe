from flask import Flask, render_template
import sqlite3

# connect to database
con = sqlite3.connect("database.db")
cur = con.cursor()

# create database, if it was not initialized before
cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR, password VARCHAR, games_won INTEGER, games_lost INTEGER, games_played INTEGER);")
cur.execute("CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY AUTOINCREMENT, is_over BOOLEAN, date TIMESTAMP, player_1 INTEGER, player_2 INTEGER, winner INTEGER);")
cur.execute("CREATE TABLE IF NOT EXISTS moves(id INTEGER PRIMARY KEY AUTOINCREMENT, game INTEGER, turn INTEGER, player INTEGER, position_x INTEGER, position_y INTEGER);")

app = Flask(__name__, static_url_path="/")

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/play")
def play():
    #Will be fild with X and Os through the game.
    fields = [["", "", ""], ["", "", ""], ["", "", ""]]
    return render_template("tictactoe_game.html", columns = fields)

if __name__ == "__main__":
    app.run(debug=True)
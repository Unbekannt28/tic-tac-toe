from flask import Flask, render_template
import sqlite3

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
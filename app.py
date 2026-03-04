from flask import Flask, render_template, request, redirect, session, url_for, Response
from werkzeug import security
import sqlite3
from time import time
from datetime import datetime

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

def new_session(user_id, username):
    session["logged_in"] = True
    session["user_id"] = user_id
    session["username"] = username

def close_session():
    session["logged_in"] = None
    session["user_id"] = None
    session["username"] = None
    session["game_id"] = None


# Routes

# Index
@app.route("/")
def main():
    return render_template("index.html")

# Register
@app.route("/register")
def register():
    message = request.args.get("message")

    return render_template("register.html", message=message)

@app.route("/register/create_user", methods=["POST"])
def create_user():
    username = request.form.get("username")
    password = request.form.get("password")

    # Check if username or password are empty
    if username == "" or password == "":
        return redirect("/register?message=field_empty")

    hashed_password = security.generate_password_hash(password)

    # Database communication
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    response = cur.execute("SELECT id FROM users WHERE name=?", (username,))

    # Check if user already exists
    if response.fetchone():
        return redirect("/register?message=username_taken")

    # Database communication
    cur.execute("INSERT INTO users (name, password) VALUES (?, ?)", (username, hashed_password))
    con.commit()
    response = cur.execute("SELECT id FROM users WHERE name=?", (username,))
    user_id = response.fetchone()[0]
    con.close()
    
    # Login the newly registered user
    new_session(user_id, username)

    return redirect("/lobby")

# Login / Logout
@app.route("/login")
def login():
    message = request.args.get("message")

    return render_template("login.html", message=message)

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
        return redirect("/login?message=wrong_credentials")
    
    # Check password
    if not security.check_password_hash(data[1], password):
        return redirect("/login?message=wrong_credentials")
    
    # Login successful
    new_session(data[0], username)

    return redirect("/lobby")

@app.route("/login/end_session")
def end_session():
    close_session()
    return redirect("/")

# Game Lobby
@app.route("/lobby")
def lobby():
    message = request.args.get("message")
    data = None
    no_open_games = True
    no_played_games = True

    # Load games of user, if logged in
    if session.get("logged_in"):
        # Database communication
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        response = cur.execute("SELECT games.id, is_over, date, user1.name, user2.name, winner FROM games, users AS user1, users AS user2 WHERE (player_1=? OR player_2=?) AND user1.id=games.player_1 AND user2.id=games.player_2", (session["user_id"], session["user_id"]))
        data = response.fetchall()
        con.close()

        for i, row in enumerate(data):
             # Convert Timestamp to real date
            row = list(row)
            row[2] = datetime.fromtimestamp(row[2]).strftime("%d.%m.%Y %H:%M") # dd.mm.yyy HH:MM
            data[i] = tuple(row)

            # Check if there are no open games or no played games for display later
            if row[1]:
                no_played_games = False
            else:
                no_open_games = False


    return render_template("lobby.html", message=message, games=data, no_open_games=no_open_games, no_played_games=no_played_games)

@app.route("/lobby/create_game", methods=["POST"])
def create_game():
    opponent = request.form.get("opponent")
    own_team = request.form.get("own-team")

    # Check if opponent or own_team is empty
    if opponent == "" or own_team == None:
        return redirect("/lobby?message=field_empty")
    
    # Check if user is logged in
    if not session.get("logged_in"):
        return redirect("/lobby?message=not_logged_in")

    # Database communication
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    response = cur.execute("SELECT id FROM users WHERE name=?", (opponent,))
    data = response.fetchone()

    # Check if opponent exists
    if data == None:
        return redirect("/lobby?message=invalid_opponent")
    
    # Check if opponent is user
    if session["user_id"] == data[0]:
        return redirect("/lobby?message=opponent_is_user")

    if own_team == "1":
        player_1 = session["user_id"]
        player_2 = data[0]
    else:
        player_1 = data[0]
        player_2 = session["user_id"]
    
    timestamp = time()

    # Database communication
    cur.execute("INSERT INTO games (date, player_1, player_2) VALUES (?, ?, ?)", (timestamp, player_1, player_2))
    con.commit()
    con.close()

    return redirect("/lobby?message=game_created")

def could_be_valid_game_id(game_id) -> bool:
    if game_id is None:
        return False 
    try:
        _ = int(game_id)
    except:
        return False
    else:
        return True

# Play Game
@app.route("/play", methods=['POST', 'GET'])
def play():
    message = request.args.get("message")
    game_id = request.form.get("game-id")

    fields = [["", "", ""], ["", "", ""], ["", "", ""]]
    #Check if player is looged in
    if session.get("logged_in") == None or not session.get("logged_in"):
        message = "not_logged_in"
        return render_template("tictactoe_game.html", message=message, fields = fields)

    if not game_id == None:
        session["game_id"] = game_id

    # Check if game_id is valid 
    if not could_be_valid_game_id(session.get("game_id")):
        session["game_id"] = None
        return redirect("/lobby?message=no_valid_game_id")

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    query = "SELECT game, turn, position_x, position_y FROM moves WHERE game = ?" 
    response = cur.execute(query, [session["game_id"]])
    row_count = 0
    for row_count, data in enumerate(response, 1):
        fields[int(data[2])][(data[3])] = "X" if data[1] % 2 == 0 else "O"

    game_query = "SELECT * FROM games WHERE id = ? "
    game_response = cur.execute(game_query, [session["game_id"]])
    game_data = game_response.fetchone()

    gameover = game_data[1]

    # Check if current turn is the users turn
    users_turn = False
    if row_count % 2 == 0 and session["user_id"] == game_data[3]: # even turn number and user is player 1
        users_turn = True
    elif row_count % 2 == 1 and session["user_id"] == game_data[4]: # odd turn number and user is player 2
        users_turn = True

    http_response = Response(render_template("tictactoe_game.html", message=message, fields = fields, gameover=gameover))

    # if current turn is not users turn: auto-refresh every 3 seconds
    if not users_turn and not gameover:
        http_response.headers["Refresh"] = "3"

    return http_response

@app.route("/play/move", methods=["POST"])
def move():
    field = request.form.get("field")

    # Check if field has two digits
    if len(field) != 2:
        return redirect("/play?message=invalid_move_length")

    #Check if field contains two ints
    try:
        x = int(field[0])
        y = int(field[1])
    except: 
        return redirect("/play?message=invalid_move_not_integers")

    #Check if field is in bounds
    if x > 2 or y > 2 or x < 0 or y < 0:
        return redirect("/play?message=invalid_move_out_of_bounds")

    #Check if player is looged in
    if session.get("logged_in") == None or not session.get("logged_in"):
        return redirect("/play?message=not_logged_in")


    game_id = session.get("game_id")

    # Check if game_id is valid 
    if not could_be_valid_game_id(game_id):
        session["game_id"] = None
        return redirect("/lobby?message=no_valid_game_id")

    con = sqlite3.connect("database.db")
    cur = con.cursor()

    query = "SELECT * FROM games WHERE id = ?"
    response = cur.execute(query, [game_id])
    data = response.fetchone()
    
    #Checks if the game exists
    if data is None:
        session["game_id"] = None
        return redirect("/lobby?message=game_dose_not_exist")

    #Checks if player is X and is part of the Game
    player_1 = data[3]
    player_2 = data[4]
    is_x = None
    if player_1 == session["user_id"]:
        is_x = True
    if player_2 == session["user_id"]:
        is_x = False
    if is_x is None:
        session["game_id"] = None
        return redirect("/lobby?message=you_are_not_part_of_this_game")

    if data[1]:
        return redirect("/play?message=game_over")

    query = "SELECT game, turn, position_x, position_y FROM moves WHERE game = ?" 
    response = cur.execute(query, [game_id])

    num_turns = 0

    #Gets Game field
    fields = [["", "", ""], ["", "", ""], ["", "", ""]]
    for data in response:
        fields[int(data[2])][(data[3])] = "X" if data[1] % 2 == 0 else "O"
        num_turns += 1

    #Check if it is this players turn
    if is_x == (not num_turns % 2 == 0):
        return redirect("/play?message=not_your_turn")

    #Checks if the the target field is untaken
    if not fields[x][y] == "":
        return redirect("/play?message=field_already_taken")


    #Adds new turn to the database
    query_new_turn = "INSERT INTO moves (game, turn, player, position_x, position_y) VALUES (?, ?, ?, ?, ?)"
    cur.execute(query_new_turn, (game_id, num_turns, session["user_id"], x, y))
    
    #Checks if the game is Won 
    is_game_won = False
    fields[x][y] = "X" if num_turns % 2 == 0 else "O"
    for x in range(3):
        count = 0
        for y in range(3):
            if fields[x][y] == "X":
                count += 1
            elif fields[x][y] == "O":
                count -=1
        if count == 3 and is_x:
            is_game_won = True
        if count == -3 and not is_x:
            is_game_won = True

    for y in range(3):
        count = 0
        for x in range(3):
            if fields[x][y] == "X":
                count += 1
            elif fields[x][y] == "O":
                count -=1
        if count == 3 and is_x:
            is_game_won = True
        if count == -3 and not is_x:
            is_game_won = True
    
    count = 0
    for i in range(3):
        if fields[i][i] == "X":
            count += 1
        elif fields[i][i] == "O":
            count -=1
    if count == 3 and is_x:
        is_game_won = True
    if count == -3 and not is_x:
        is_game_won = True

    count = 0
    for i in reversed(range(3)):
        if fields[i][2 - i] == "X":
            count += 1
        elif fields[i][2 - i] == "O":
            count -=1
    if count == 3 and is_x:
        is_game_won = True
    if count == -3 and not is_x:
        is_game_won = True

    if is_game_won:
        win_query = "UPDATE games SET is_over = true, winner = ? WHERE id = ?"
        cur.execute(win_query, (session["user_id"], game_id))

        winner_query = "UPDATE users SET games_won = games_won + 1, games_played = games_played + 1 WHERE id = ?"
        cur.execute(winner_query, (session["user_id"],))

        losser_query = "UPDATE users SET games_lost = games_lost + 1, games_played = games_played + 1 WHERE id = ?"
        if is_x:
            cur.execute(losser_query, (player_2,))
        else:
            cur.execute(losser_query, (player_1,))
    elif num_turns == 8:
        #Ends Game if last turn reached and no player won
        query_gameover = "UPDATE games SET is_over = true WHERE id = ?"
        cur.execute(query_gameover, (game_id,))

        query_draw = "UPDATE users SET games_played = games_played + 1 WHERE id = ?"
        cur.execute(query_draw, (player_1,))
        cur.execute(query_draw, (player_2,)) 

    

    con.commit()
    con.close()

    return redirect("/play?message=valid_move")


# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    # Database communication
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    response = cur.execute("SELECT name, games_won, games_lost, games_played, (games_played * 10 + games_won * 5 - games_lost * 5) AS score FROM users ORDER BY score DESC")
    data = response.fetchall()
    con.close()

    return render_template("leaderboard.html", users=data)

if __name__ == "__main__":
    app.run(debug=True)
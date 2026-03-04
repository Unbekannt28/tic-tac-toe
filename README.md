# Tic Tac Toe Multiplayer Game
## Overview
This game was developed for a programming project during our Computer Science studies at Christian Albrechts University Kiel.

Our Tic-Tac-Toe Website allows you to play against your friends while both parties are using seperate browsers. As this site uses server-side rendering it may take a fow seconds before you can see your opponents move, but aside that everything should work just as you expect.

Have fun playing!
## Structure
### Database
![UML scheme of Database](https://github.com/Unbekannt28/tic-tac-toe/blob/main/uml_diagram.svg "UML scheme of Database")
## Installation
To run this flask-based Web Application you need to install a modern python3 version (e.g. 3.14.3) and some dependencies. These can be found in `requirements.txt`.
It is recommended to use a virtual environment for the installation of python modules.
### Step 1
Setup a python virtual enviroment. This can be different with some systems, but in generel it will look something like this:

    python3 -m venv <path>

### Step 2
Activate the virtual enviroment. This step is different on Windows and Linux/macOs:<br>
(If you are using VS Code with the Python Extension this may have already happened automatically.)

#### Windows:

    <path>\Scripts\activate

#### Linux / macOs:

    source <path>/bin/activate

### Step 3
Now we just need to install the dependencies using the following command. Again; this step can be different with some systems:

    pip install -r requirements.txt

## Execution
To run this application you can use either one of these methods:

    flask run

or

    python3 app.py

## People involved
- Mika Schiessler ([Unbekannt28](https://github.com/Unbekannt28))
- Nils Marten ([NichtNil5](https://github.com/NichtNil5))

## Licensing
- Icons by Material Design Icons (Apache License 2.0)

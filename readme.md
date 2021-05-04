# _Oh, Hell!_ Webserver
This repo houses the code for the _Oh, Hell!_ card game and a webserver to provide access to the game.

## Game Logic
The main game logic is located in `OhHell.py`. It makes use of `GameState.py` and `TrickTracker.py` to keep track of the state of the game, and `Player.py` to handle player behaviors.

The `PlayerMCTS.py` and `STS.py` files contain subclasses of `Player` that enable AI players. These files also contain experiments to evaluate their performance, and the `combined_experiment.py` file contains an experiment in which these two AI play against each other. Running these files will give the experiment results found in the report.

## App Logic
The `app.py` file contains the logic to allow the program to function as a web app. It runs on `socket-io` to allow event-based communication with a client.

Each client connected to the server has its own game instance. By default, the socket will time out and disconnect a client if it waits more than 10 minutes for the client to make a move in its game. This can be reconfigured by setting the `GAME_TIMEOUT_LENGTH` environment variable.

To run the server, the `run-dev.sh` file is provided. This will enable auto-reloading on code changes.

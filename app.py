import eventlet
import socketio
from Player import Player
from OhHell import OhHell
import os

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

GAME_TIMEOUT_LENGTH = int(os.environ.get('GAME_TIMEOUT_LENGTH') or 600)

existing_games = {}

# Start a new game on connection
@sio.event
def new_game(sid, data):
    # Set up the game
    player_names = data.get('players')
    if player_names is None or len(player_names) < 2:
        sio.emit('game_init', { 'error': 'Not enough players provided' })
        return
    if all([name[:3] == 'bot' for name in player_names]):
        sio.emit('game_init', { 'error': 'No human players provided' })
        return
    if len(player_names) != len(set(player_names)):
        sio.emit('game_init', { 'error': 'Players must have unique names' })
        return
    players = [Player(name, is_ai=name[:3] == 'bot') for name in player_names]
    max_hand = data.get('max_hand')
    def ask(event, data=None):
        return sio.call(event, data, sid=sid, timeout=GAME_TIMEOUT_LENGTH)
    def inform(event, data=None):
        return sio.emit(event, data, room=sid)
    game = OhHell(players, max_hand=max_hand, ask=ask, inform=inform)
    existing_games[sid] = game
    inform('game_init', { 'success': sid })

@sio.event
def deal(sid):
    if sid not in existing_games:
        sio.emit('error', 'No game exists', room=sid)
        return
    game = existing_games[sid]
    if game.state.curr_round >= game.state.num_rounds:
        sio.emit('error', 'Game already ended', room=sid)
        return
    try:
        game.play()
    except socketio.exceptions.TimeoutError:
        sio.emit('error', 'Game timed out', room=sid)
        sio.disconnect(sid)

@sio.event
def disconnect(sid):
    print(f'{sid} disconnected')
    global existing_games
    del existing_games[sid]

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

import eventlet
import socketio
from Player import Player
from PlayerMCTS import PlayerMCTS
from STS import STSPlayer
from OhHell import OhHell
import os

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

GAME_TIMEOUT_LENGTH = int(os.environ.get('GAME_TIMEOUT_LENGTH') or 600)

existing_games = {}

# Start a new game
@sio.event
def new_game(sid, data):
    '''
    Sets up a new game for the client.
    :param sid: sid of the client.
    :param data: data for the game. Includes a list of players and a maximum hand size.
    '''
    # Set up the game
    players = data.get('players')
    if players is None or len(players) < 2:
        sio.emit('game_init', { 'error': 'Not enough players provided' })
        return
    if all(['is_ai' in player and player['is_ai'] for player in players]):
        sio.emit('game_init', { 'error': 'No human players provided' })
        return
    if len(players) != len(set([player['name'] for player in players])):
        sio.emit('game_init', { 'error': 'Players must have unique names' })
        return

    def init_player(player):
        if 'is_ai' in player and player['is_ai']:
            if 'algorithm' not in player:
                return Player(player['name'], is_ai=True) 
            elif player['algorithm'] == 'MCTS':
                return PlayerMCTS(player['name'], player['search_time'])
            elif player['algorithm'] == 'STS':
                return STSPlayer(player['name'], player['max_depth'])
            else:
                return Player(player['name'], is_ai=True)
        return Player(player['name'])
    players = [init_player(player) for player in players]

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
    '''
    Deal the next round of an existing game.
    :param sid: the id of the client whose game should be dealt.
    '''
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
    '''
    Cleans up any leftover information after a client disconnects
    :param sid: The id of the disconnecting client.
    '''
    print(f'{sid} disconnected')
    try:
        global existing_games
        del existing_games[sid]
    except KeyError:
        print(f'No game found for {sid}')

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

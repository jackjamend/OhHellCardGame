from OhHell import OhHell
from PlayerMCTS import PlayerMCTS
from AlphaBeta import AlphaBetaPlayer

scores = {
    'alpha_beta_shallow': [],
    'alpha_beta_deep': [],
    'mcts_short': [],
    'mcts_long': []
}
for _ in range(1000):
    players = [
        AlphaBetaPlayer('alpha_beta_shallow', max_depth=1),
        AlphaBetaPlayer('alpha_beta_deep', max_depth=5),
        PlayerMCTS('mcts_short', search_time=1),
        PlayerMCTS('mcts_long', search_time=3)
    ]
    game = OhHell(players, max_hand=5)

    for _ in range(9):
        game.play()
    scoreboard = {player.name: score_row[-1] for player, score_row in zip(players, game.state.get_scoreboard(players))}
    for player in scoreboard:
        scores[player].append(scoreboard[player])
    
print('Average scores', {sum(scores[player]) / len(scores[player]) for player in scores})

"""
Script to run experiments of the STS program against the MCTS.
"""
from OhHell import OhHell
from PlayerMCTS import PlayerMCTS
from STS import STSPlayer

scores = {
    'sts_shallow': [],
    'sts_deep': [],
    'mcts_short': [],
    'mcts_long': []
}
for _ in range(500):
    players = [
        STSPlayer('sts_shallow', max_depth=1),
        STSPlayer('sts_deep', max_depth=5),
        PlayerMCTS('mcts_short', search_time=1),
        PlayerMCTS('mcts_long', search_time=3)
    ]
    game = OhHell(players, max_hand=5)

    for _ in range(9):
        game.play()
    scoreboard = {player.name: score_row[-1] for player, score_row in zip(players, game.state.get_scoreboard(players))}
    for player in scoreboard:
        scores[player].append(scoreboard[player])
    
print('Average scores', {player: sum(scores[player]) / len(scores[player]) for player in scores})

# Average scores {'sts_shallow': 16.68421052631579, 'sts_deep': 13.274853801169591, 'mcts_short': 46.73879142300195, 'mcts_long': 46.85964912280702}

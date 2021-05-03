from Player import Player
import pydealer
from itertools import product, chain
from copy import copy

custom_ranks = {"suits": {"Spades": 1, "Hearts": 1, "Clubs": 1, "Diamonds": 1},
                "values": {"Ace": 13, "King": 12, "Queen": 11, "Jack": 10, "10": 9,
                            "9": 8, "8": 7, "7": 6, "6": 5, "5": 4, "4": 3, "3": 2, "2": 1,}}

class STSPlayer(Player):
    """
    Inherits from the OhHellCardGame.Player class. Changes the logic for selecting and playing a
    card.
    """
    def __init__(self, name, max_depth=float('inf')):
        """
        Constructs an instance of the STSPlayer.
        :param name: The name of the agent.
        :param max_depth: The maximum depth to traverse the game tree.
        """
        super().__init__(name, is_ai=True)
        self.max_depth = max_depth

    def make_bid(self, state, is_dealer):
        return len(self.hand)

    def play_card(self, state):
        """
        Uses the STS algorithm to pick best move to make.
        :param state: The GameState representing the current state of the game
        :return: card to be played
        """
        card, prob = self.explore_node(self.hand, self.max_depth, leading_suit=state.leading_suit, trump_suit=state.trump_suit)
        self.hand.get(str(card))
        return card

    def explore_node(self, cards, max_depth, leading_suit=None, trump_suit=None):
        """
        Recursively explores the game tree to find expected points down each branch.
        :param cards: The cards available to the agent
        :param max_depth: The maximum depth to search (relative to current depth)
        :param leading_suit: The leading suit for the trick
        :param trump_suit: The trump suit for the round
        :return: optimal card, and probability of winning the trick with that card
        """
        results = {}
        for card in cards:
            lead = leading_suit if leading_suit is not None else card.suit
            if not card.suit == lead and not card.suit == trump_suit:
                results[card] = 0
            elif card.suit == trump_suit:
                results[card] = 1 - ((13 - custom_ranks['values'][card.value]) / 52)
            else:
                results[card] = 1 - ((26 - custom_ranks['values'][card.value]) / 52)
            
            if len(cards) > 1 and max_depth > 1:
                clone_hand = copy(cards)
                clone_hand.get(str(card))
                probs = [prob for _, prob in [
                    self.explore_node(clone_hand, max_depth - 1, leading_suit=suit, trump_suit=trump_suit) for suit in ['Clubs', 'Hearts', 'Spades', 'Diamonds']
                ]]
                results[card] += max(probs)

        card, prob = max(results.items(), key=lambda x: x[1])
        return card, prob

if __name__ == '__main__':
    # STS experiment
    from OhHell import OhHell
    scores = {'1': [], '2': [], '3': [], '4': []}
    for _ in range(500):
        players = [STSPlayer(str(depth), depth) for depth in range(1,5)]
        game = OhHell(players, 5)
        for _ in range(9):
            game.play()
        scoreboard = {player.name: score_row[-1] for player, score_row in zip(players, game.state.get_scoreboard(players))}
        for player in scoreboard:
            scores[player].append(scoreboard[player])
    print('Experiment 1 Average Scores', {player: sum(scores[player]) / len(scores[player]) for player in scores})

    scores = {
        'sts_shallow': [],
        'sts_deep': [],
        'random_1': [],
        'random_2': []
    }
    for _ in range(500):
        players = [
            STSPlayer('sts_shallow', max_depth=1),
            Player('random_1', is_ai=True),
            STSPlayer('sts_deep', max_depth=5),
            Player('random_2', is_ai=True)
        ]
        game = OhHell(players, max_hand=5)
        for _ in range(9):
            game.play()
        scoreboard = {player.name: score_row[-1] for player, score_row in zip(players, game.state.get_scoreboard(players))}
        for player in scoreboard:
            scores[player].append(scoreboard[player])
    
    print('Experiment 2 Average Scores', {player: sum(scores[player]) / len(scores[player]) for player in scores})

# Experiment 1 Average Scores {'1': 16.836, '2': 13.016, '3': 13.048, '4': 13.36}
# Experiment 2 Average Scores {'sts_shallow': 17.716, 'sts_deep': 14.42, 'random_1': 44.054, 'random_2': 44.09}

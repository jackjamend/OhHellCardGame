from Player import Player
import pydealer
from itertools import product, chain
from copy import copy

custom_ranks = {"suits": {"Spades": 1, "Hearts": 1, "Clubs": 1, "Diamonds": 1},
                "values": {"Ace": 13, "King": 12, "Queen": 11, "Jack": 10, "10": 9,
                            "9": 8, "8": 7, "7": 6, "6": 5, "5": 4, "4": 3, "3": 2, "2": 1,}}

class AlphaBetaPlayer(Player):
    def __init__(self, name, max_depth=float('inf')):
        super().__init__(name, is_ai=True)
        self.max_depth = max_depth

    def make_bid(self, state, is_dealer):
        return len(self.hand)

    def play_card(self, state):
        card, prob = self.explore_node(self.hand, self.max_depth, leading_suit=state.leading_suit, trump_suit=state.trump_suit)
        self.hand.get(str(card))
        return card

    def explore_node(self, cards, max_depth, leading_suit=None, trump_suit=None):
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
    # AlphaBeta experiment
    from OhHell import OhHell
    scores = {'1': [], '2': [], '3': [], '4': []}
    for _ in range(500):
        players = [AlphaBetaPlayer(str(depth), depth) for depth in range(1,5)]
        game = OhHell(players, 5)
        for _ in range(9):
            game.play()
        scoreboard = {player.name: score_row[-1] for player, score_row in zip(players, game.state.get_scoreboard(players))}
        for player in scoreboard:
            scores[player].append(scoreboard[player])
    print('Average scores', {player: sum(scores[player]) / len(scores[player]) for player in scores})

# Average scores {'1': 16.836, '2': 13.016, '3': 13.048, '4': 13.36}

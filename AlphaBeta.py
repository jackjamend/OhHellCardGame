from Player import Player
import pydealer
from itertools import product, chain
from copy import copy

custom_ranks = {"suits": {"Spades": 1, "Hearts": 1, "Clubs": 1, "Diamonds": 1},
                "values": {"Ace": 13, "King": 12, "Queen": 11, "Jack": 10, "10": 9,
                            "9": 8, "8": 7, "7": 6, "6": 5, "5": 4, "4": 3, "3": 2, "2": 1,}}

class AlphaBetaPlayer(Player):
    def __init__(self, name):
        super().__init__(name, is_ai=True)

    def make_bid(self, prev_bids, is_dealer):
        return len(self.hand)

    def play_card(self, curr_played, all_played, leading_suit=None, trump_suit=None):
        card, prob = self.explore_node(self.hand, leading_suit=leading_suit, trump_suit=trump_suit)
        self.hand.get(str(card))
        return card

    def explore_node(self, cards, leading_suit=None, trump_suit=None):
        results = {}
        for card in cards:
            lead = leading_suit if leading_suit is not None else card.suit
            if not card.suit == lead and not card.suit == trump_suit:
                results[card] = 0
            elif card.suit == trump_suit:
                results[card] = 1 - ((13 - custom_ranks['values'][card.value]) / 52)
            else:
                results[card] = 1 - ((26 - custom_ranks['values'][card.value]) / 52)
            
            if len(cards) > 1:
                clone_hand = copy(cards)
                clone_hand.get(str(card))
                probs = [prob for _, prob in [
                    self.explore_node(clone_hand, leading_suit=suit, trump_suit=trump_suit) for suit in ['Clubs', 'Hearts', 'Spades', 'Diamonds']
                ]]
                results[card] += max(probs)

        card, prob = max(results.items(), key=lambda x: x[1])
        return card, prob

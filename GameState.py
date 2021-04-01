import pydealer
from TrickTracker import TrickTracker
import copy


class GameState:
    total_cards = 52
    base_ranks = {"suits": {"Spades": 1, "Hearts": 1, "Clubs": 1, "Diamonds": 1},
                    "values": {"Ace": 13, "King": 12, "Queen": 11, "Jack": 10, "10": 9,
                               "9": 8, "8": 7, "7": 6, "6": 5, "5": 4, "4": 3, "3": 2, "2": 1, }
                    }

    def __init__(self, players, max_hand=None):
        self.num_players = len(players)
        self.players = players
        if max_hand:
            self.max_hand = max_hand
        else:
            self.max_hand = GameState.total_cards // self.num_players
        self.num_rounds = self.max_hand * 2 - 1

        self.tracker = TrickTracker(self.players, self.num_rounds)

        self.round_hand = []
        hand_size = 0
        for i in range(int(self.num_rounds)):
            if i < self.max_hand:
                hand_size += 1
            else:
                hand_size -= 1

            self.round_hand.append(hand_size)

        self.curr_round = 0
        self.curr_hand_size = self.round_hand[self.curr_round]

        # Round logic variables
        self.dealer = None
        self.trump_suit = None
        self.leading_suit = None
        self.discard = []
        self.deck = None
        self.custom_ranks = None
        self.trick_cards = {}
        self.bids = {}

        self.best_player_idx = -1
        self.best_played_card = None
        self.player_order = [i for i in range(self.num_players)]

    def begin_round(self):
        """
        Beginning logic of the match. Get hand size and dealer
        :return:
        """
        self.dealer = self.players[-1]
        self.curr_hand_size = self.round_hand[self.curr_round]
        self.player_order = [i for i in range(self.num_players)]

        return self.curr_hand_size, self.dealer

    def set_trump_suit(self, trump_card):
        self.trump_suit = trump_card.suit
        print("current trump suit is", self.trump_suit)
        self.discard += [trump_card]

    def collect_bid(self, player, bid):
        self.bids[player] = bid
        self.tracker.collect_bid(player, bid)

    def get_player_order(self):
        return self.player_order

    def setup_trick(self, leading_card):
        self.leading_suit = leading_card.suit
        self.custom_ranks = copy.deepcopy(GameState.base_ranks)
        self.custom_ranks["suits"][self.trump_suit] = 3
        if self.trump_suit != self.leading_suit:
            self.custom_ranks["suits"][self.leading_suit] = 2

        return self.leading_suit

    def play_card(self, player, player_idx, card):
        print('Ranking:', self.custom_ranks["suits"])
        def card_gt(card1, card2, ranks):
            if ranks["suits"][card1.suit] == ranks["suits"][card2.suit]:
                return ranks["values"][card1.value] > ranks["values"][card2.value]
            else:
                return ranks["suits"][card1.suit] > ranks["suits"][card2.suit]
        self.discard += [card]
        self.trick_cards[player] = card
        # Check for initial play
        if self.best_player_idx == -1:
            print('Initial card ({}) is best'.format(card))
            self.best_played_card = card
            self.best_player_idx = player_idx
        elif card_gt(card, self.best_played_card, self.custom_ranks):
            print("{} beat {}".format(card, self.best_played_card))
            self.best_played_card = card
            self.best_player_idx = player_idx

    def finish_trick(self):
        trick_winner = self.players[self.best_player_idx]
        self.tracker.trick_taken(trick_winner)
        self.player_order = list(range(self.best_player_idx, self.num_players)) + list(range(0, self.best_player_idx))
        self.best_player_idx = -1
        self.best_played_card = None
        self.custom_ranks = {}
        self.trick_cards = {}

        return trick_winner, self.player_order

    def finish_round(self):
        self.dealer = None
        self.trump_suit = None
        self.leading_suit = None
        self.discard = []







    def calculate_scores(self):
        return self.tracker.calculate_scores()

    def get_scoreboard(self, players):
        return self.tracker.get_scoreboard(players)


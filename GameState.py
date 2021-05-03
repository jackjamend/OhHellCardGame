import pydealer
from OhHellCardGame.TrickTracker import TrickTracker
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
            self.max_hand = (GameState.total_cards - 1) // self.num_players
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
        self.curr_trick = 0
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
        self.player2id = {p: i for i, p in enumerate(self.players)}
        self.id2player = {v: k for k, v in self.player2id.items()}

        self.best_player_idx = -1
        self.best_played_card = None
        self.player_order = [i for i in range(self.num_players)]
        self.player_turn = 0
        self.dealer_idx = len(self.players) - 1

    def begin_round(self):
        """
        Beginning logic of the match. Get hand size and dealer
        :return:
        """
        self.dealer = self.players[self.dealer_idx]
        self.curr_hand_size = self.round_hand[self.curr_round]
        # self.player_order = [i for i in range(self.num_players)]
        offset = self.curr_round % self.num_players
        self.curr_trick = 0
        self.player_order = list(range(offset, self.num_players)) + list(range(0, offset))
        return self.curr_hand_size, self.dealer

    def set_trump_suit(self, trump_card):
        self.trump_suit = trump_card.suit
        # print("Current trump suit is", self.trump_suit)
        self.discard += [trump_card]

    def get_bid_order(self):
        return [self.players[i] for i in self.player_order]

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

    def on_leading_player(self):
        return self.player_turn <= 1

    def play_card(self, player, card):

        def card_gt(card1, card2, ranks):
            if ranks["suits"][card1.suit] == ranks["suits"][card2.suit]:
                return ranks["values"][card1.value] > ranks["values"][card2.value]
            else:
                return ranks["suits"][card1.suit] > ranks["suits"][card2.suit]

        new_state = self.copy_state()
        new_state.discard += [card]
        new_state.trick_cards[player] = card
        player_idx = new_state.player2id[player]
        # Check for initial play
        if new_state.best_player_idx == -1:
            # print('Initial card ({}) is best'.format(card))
            new_state.best_played_card = card
            new_state.best_player_idx = player_idx
            new_state.setup_trick(card)
        elif card_gt(card, new_state.best_played_card, new_state.custom_ranks):
            # print("{} beat {}".format(card, new_state.best_played_card))
            new_state.best_played_card = card
            new_state.best_player_idx = player_idx
        return new_state

    def finish_trick(self):
        trick_winner = self.id2player[self.best_player_idx]
        self.tracker.trick_taken(trick_winner)
        # offset = self.curr_round % self.num_players
        self.player_order = list(range(self.best_player_idx, self.num_players)) + list(
            range(0, self.best_player_idx))
        self.best_player_idx = -1
        self.best_played_card = None
        self.custom_ranks = {}
        self.trick_cards = {}
        self.player_turn = 0
        self.curr_trick += 1
        return trick_winner

    def get_next_player(self):
        if self.player_turn >= self.num_players:
            return None
        next_player = self.id2player[self.player_order[self.player_turn]]
        self.player_turn += 1
        return next_player

    def end_trick_info(self, player):
        return self.bids[player], self.tracker.tricks_taken[player]

    def finish_round(self):
        self.dealer = None
        self.trump_suit = None
        self.leading_suit = None
        self.discard = []
        self.curr_round += 1
        self.tracker.reset()
        self.dealer_idx += 1
        if self.dealer_idx >= len(self.players):
            self.dealer_idx = 0
        return self.players

    def terminal_state(self):
        return self.num_players * self.curr_hand_size == len(self.discard)

    def calculate_scores(self):
        return self.tracker.calculate_scores(self.players)

    def get_scoreboard(self, players):
        return self.tracker.get_scoreboard(players)

    def trick_progression(self):
        prog_arr = []
        for player_order_idx in self.player_order:
            if player_order_idx == self.player_order[self.player_turn - 1]:
                prog_arr += ['[{}]'.format(self.id2player[player_order_idx])]
            else:
                prog_arr += ['{}'.format(self.id2player[player_order_idx])]

        return ' '.join(prog_arr)

    def copy_state(self):
        new_state = copy.deepcopy(self)
        new_state.player2id = self.player2id
        new_state.id2player = self.id2player
        new_state.players = self.players
        new_state.dealer = self.dealer
        new_state.tracker = self.tracker.copy()
        new_state.custom_ranks = self.custom_ranks
        new_state.bids = self.bids
        return new_state

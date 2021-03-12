import pydealer
import numpy as np
from .TrickTracker import TrickTracker
class OhHell:
    total_cards = 52
    def __init__(self, players, max_hand=None):
        
        self.num_players = len(players)
        self.players = players
        if max_hand:
            self.max_hand = max_hand
        else:
            self.max_hand = OhHell.total_cards // num_players
        self.num_rounds = max_hand * 2 - 1

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
        self.curr_hand_size = 0

        

    def play(self):
        self.curr_hand_size = self.round_hand[self.curr_round]
        dealer = self.players[-1]
        deck = pydealer.Deck()
        deck.shuffle()

        # Deal hand
        for player in self.players:
            player.hand += deck.deal(self.curr_hand_size)

        # Set trump card
        trump_card = deck.deal(1)
        trump_suit = trump_card.suit

        custom_ranks = {"suits": {"Spades": 1, "Hearts": 1, "Clubs": 1, "Diamonds": 1}}
        custom_ranks[trump_suit] = 3

        # Collect bids
        bids = {}
        for player in self.players:
            bid = player.make_bid(bids, player is dealer)
            bids[player] = bid
            tracker.collect_bid(player, bid)
        
        # Play tricks in round
        player_order = [i for i in range(self.num_players)]
        cards_out = [trump_suit]
        for i in range(self.curr_hand_size):
            # Single trick
            curr_played = {}
            # First player goes and is "the best" so far
            leading_player = self.players[player_order[0]]
            best_played_card = leading_player.play_card(curr_played, cards_out)
            best_player_idx = 0
            
            # Log card played and leading suit
            curr_played[leading_player] = played_card
            leading_suit = best_played_card.suit
            custom_ranks[leading_suit] = 2
            for player_idx in player_order[1:]:
                curr_player = self.players[player_idx]
                played_card = curr_player.play_card(curr_played, cards_out, leading_suit)
                if played_card > best_played_card:
                    best_played_card = played_card
                    best_player_idx = player_idx
                
                # Log played card
                curr_played[curr_player] = played_card
            
            trick_winner = self.players[best_player_idx]
            tracker.trick_taken(trick_winer)
            
            # Set up for next round
            custom_ranks[leading_suit] = 1
            cards_out += curr_played.values()
            player_order = list(range(best_player_idx, self.num_players)) + list(range(0, best_player_idx))
            for player in self.players:
                player.observe(curr_played.values())

        # Shift dealer one over
        self.players = self.players[1:] + self.players[0]

    

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

        # Output dealer
        self.display_dealer(dealer)

        deck = pydealer.Deck()
        deck.shuffle()

        # Deal hand
        for player in self.players:
            player.hand += deck.deal(self.curr_hand_size)

        # Output player hands
        self.display_hands(self.players)

        # Set trump card
        trump_card = deck.deal(1)[0]
        trump_suit = trump_card.suit
       
        # Output trump card
        self.display_trump(trump_card)

        custom_ranks = {"suits": {"Spades": 1, "Hearts": 1, "Clubs": 1, "Diamonds": 1},
                        "values": {"Ace": 13, "King": 12, "Queen": 11, "Jack": 10, "10": 9,
                                   "9": 8, "8": 7, "7": 6, "6": 5, "5": 4, "4": 3, "3": 2, "2": 1,}
                        }
        custom_ranks["suits"][trump_suit] = 3

        # Collect bids
        bids = {}
        for player in self.players:
            bid = player.make_bid(bids, player is dealer)
            bids[player] = bid
            self.tracker.collect_bid(player, bid)
        
        # Output current bids
        self.display_bids(bids)
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
            
            # Output played card
            self.display_leading_suit(best_played_card.suit)
            self.display_card_played(leading_player, best_played_card)
            
            # Log card played and leading suit
            curr_played[leading_player] = best_played_card
            leading_suit = best_played_card.suit
            custom_ranks["suits"][leading_suit] = 2
            for player_idx in player_order[1:]:
                curr_player = self.players[player_idx]
                played_card = curr_player.play_card(curr_played, cards_out, leading_suit)

                # Output played card
                self.display_card_played(curr_player, played_card)
                if played_card.gt(best_played_card, custom_ranks):
                    best_played_card = played_card
                    best_player_idx = player_idx
                
                # Log played card
                curr_played[curr_player] = played_card
            
            trick_winner = self.players[best_player_idx]
            self.tracker.trick_taken(trick_winner)
            
            # Output winner
            self.display_trick_winner(trick_winner)

            # Set up for next round
            custom_ranks[leading_suit] = 1
            cards_out += curr_played.values()
            player_order = list(range(best_player_idx, self.num_players)) + list(range(0, best_player_idx))
            for player in self.players:
                player.observe(curr_played.values())

        tracker_data = self.tracker.calculate_scores()

        # Output round data
        self.display_round_info(tracker_data)
        
        scoreboard = self.tracker.get_scoreboard(self.players)
        self.display_scoreboard(self.players, scoreboard)

        # Shift dealer one over and set up for next round
        self.players = self.players[1:] + [self.players[0]]
        self.curr_round += 1


    def display_dealer(self, dealer):
        print("Dealer is {}".format(dealer))

    def display_hands(self, players):
        for player in players:
            
            if (len(player.hand) > 1):
                # print("----")
                print("{} : [{}]".format(player, ", ".join([str(c) for c in player.hand])))
            else:
                print("{} : {}".format(player, player.hand))

    def display_trump(self, trump_card):
        print("Trump card is {}".format(trump_card.suit))

    def display_bids(self, bids):
        for key, value in bids.items():
            print("{} bid {}".format(key, value))
    
    def display_leading_suit(self, suit):
        print("Leading suit is {}".format(suit))
    
    def display_card_played(self, player, card):
        print("{} played the {}".format(player, card))
    
    def display_trick_winner(self, player):
        print("{} won the trick\n".format(player))

    def display_round_info(self, tracker_output):
        for player, info in tracker_output.items():
            if info[0] == info[1]:
                print('{} made their bid of {}'.format(player, info[0]))
            else:
                print('{} missed their bid of {}, getting {} tricks'.format(player, info[1], info[0]))
    
    def display_scoreboard(self, players, scoreboard):
        for player, score_row in zip(players, scoreboard):
            print('{} : {}'.format(player, score_row))

    

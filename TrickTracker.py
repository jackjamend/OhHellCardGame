import numpy as np
class TrickTracker:

    def __init__(self, players, num_rounds):
        self.bid_history = {}
        self.trick_history = {}

        self.curr_bid = {}
        self.tricks_taken = {}
        
        self.player2idx = {}

        for i, player in enumerate(players):
            self.bid_history[player] = []
            self.trick_history[player] = []
            self.tricks_taken[player] = 0
            self.player2idx[player] = i
        
        self.num_rounds = num_rounds
        self.scoreboard = np.zeros((len(players), num_rounds))
        self.curr_round = 0
        

    def collect_bid(self, player, plyr_bid):
        self.bid_history[player].append(plyr_bid)
        self.curr_bid[player] = plyr_bid
        self.curr_bid = plyr_bid

    def trick_taken(self, player):
        self.tricks_taken[player] += 1

    def calculate_scores(self):
        for player in bid_history.keys():
            points = self.tricks_taken[player]
            self.trick_history[player].append(points)

            if points == self.curr_bid:
                points += 10
            
            player_idx = self.player2idx[player]
            self.scoreboard[player_idx, self.curr_round] = points
        
        # Updates variables for next iterations
        self.curr_round += 1
        self.curr_bid = {}
        self.tricks_taken = {}
        for player in bid_history.keys():
            self.tricks_taken[player] = 0
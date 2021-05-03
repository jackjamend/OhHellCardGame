"""
Code to keep track of the score for the game Oh, Hell.
"""
import copy

import numpy as np


class TrickTracker:
    """
    Class for tracking the score of the game
    """
    def __init__(self, players, num_rounds):
        """
        Creates instance of TrickTracker that tracks the score during the progression of the game
        :param players: the players in the game
        :param num_rounds: number of round being played
        """
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
        """
        Record bids for a given player
        :param player: player bidding
        :param plyr_bid: the bid from the player
        """
        self.bid_history[player].append(plyr_bid)
        self.curr_bid[player] = plyr_bid

    def trick_taken(self, player):
        """
        Records which player took the trick and increments their value by 1
        :param player: the trick winning player
        """
        self.tricks_taken[player] += 1

    def calculate_scores(self, players):
        """
        Calculates the score for the players based on the rules; players who get their bids get a
        bonus 10 points and all players get a point for each trick they took
        :param players: reference to players in the game
        :return: the current points for each player
        """
        output_data = {}
        for player in players:
            points = self.tricks_taken[player]
            self.trick_history[player].append(points)
            output_data[player] = [points, self.curr_bid[player]]
            if points == self.curr_bid[player]:
                points += 10

            player_idx = self.player2idx[player]
            if self.curr_round == 0:
                self.scoreboard[player_idx, self.curr_round] = points
            else:
                self.scoreboard[player_idx, self.curr_round] = points + self.scoreboard[player_idx, self.curr_round-1]

        return output_data

    def reset(self):
        """
        Updates variables for next round
        :return:
        """
        self.curr_round += 1
        self.curr_bid = {}
        self.tricks_taken = {}
        for player in self.bid_history.keys():
            self.tricks_taken[player] = 0

    def get_scoreboard(self, players):
        """
        Return the scoreboard in the order of the players given
        :param players: the players in the given order to display
        :return: scoreboard
        """
        player_idx = []
        for player in players:
            player_idx.append(self.player2idx[player])
        
        return self.scoreboard[player_idx]

    def copy(self):
        """
        Copies the current trick tracker to ensure that reference remain the same
        :return: new tracker
        """
        new_tracker = copy.deepcopy(self)
        new_tracker.bid_history = copy.copy(self.bid_history)
        new_tracker.trick_history = copy.copy(self.trick_history)
        new_tracker.tricks_taken = copy.copy(self.tricks_taken)
        new_tracker.player2idx = copy.copy(self.player2idx)
        new_tracker.curr_bid = copy.copy(self.curr_bid)

        return new_tracker

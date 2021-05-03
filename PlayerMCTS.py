"""
Code for implementing the AI agent using Monte Carlo tree search (MCTS).

The MCTS is used for deciding the best card to play given the current state.
"""
import copy
import random
import time

import pydealer
import numpy as np

from Player import Player


class PlayerMCTS(Player):
    """
    Inherits from the Player class. Changes the logic for selecting and playing a
    card.
    """
    def __init__(self, name, search_time=3):
        """
        Constructs an instance of the PlayerMCTS.
        :param name: The name of the agent.
        :param search_time: The amount of time the agent is allowed to search for a future state.
        """
        super().__init__(name, is_ai=True)
        self.search_time = search_time

    def play_card(self, state, leading_suit=None):
        """
        Uses MCTS to pick best move to make.
        :param state: The GameState representing the current state of the game
        :param leading_suit: If a leading suit was used, give information for it. Not used for
        this method, follows inheritance.
        :return: card to be played
        """
        mcts = MonteCarloTreeSearch(copy.copy(self.hand), state.copy_state(), self)
        mcts.search(max_search_time=self.search_time)
        card = mcts.next_move()
        card = self.hand.get(str(card))[0]

        return card


class Node:
    """
    Node class to use to build a tree to perform the MCTS.
    """
    def __init__(self, hand, state, my_turn, action=None, parent=None):
        """
        Builds node in the tree.

        W is the variable to track number of wins node is involved in and N is to keep track of
        the number of simulations the node is involved in.
        :param hand: the player's hand at the given node
        :param state: the state at the current node
        :param my_turn: whether or not it is the player's turn
        :param action: the action that transitioned from parent to this node.
        :param parent: the parent to the current node
        """
        self.children = []
        self.parent = parent
        self.w = 0
        self.n = 0
        self.action = action
        self.my_turn = my_turn
        if self.parent is None:
            self.depth = 0

        else:
            self.parent.children.append(self)
            self.depth = self.parent.depth + 1

        self.hand = copy.copy(hand)
        self.state = state

    def UCT(self, c=None):
        """
        Used to give numeric value to decide which node to explore. This the equation
        for the Upper Confidence Bound 1 applied to trees (UCT) that gives a value that
        balances exploitation and exploration ideas of the tree search. The original equation
        is:
        UCT = w_i / n_i + c * sqrt(ln(n_p) / n_i)
        where, i denotes the current node and p denotes the parent node. w is the number of
        simulations that this node resulted in a win and n is the total number of simulations.

        Error when parent is null i.e. root node.
        """
        if self.w == 0 and self.n == 0:
            return np.inf
        if c is None:
            c = np.sqrt(2)
        if self.parent is None:
            return np.nan
        exploitation = self.w / self.n
        exploration = c * np.sqrt(np.log(self.parent.n) / self.n)
        return exploitation + exploration

    def __str__(self):
        """
        Representation of the node to get information about the search.
        :return: string representation of the node.
        """
        s = 'W: {}, N: {}, UCT: {}\n'.format(self.w, self.n, self.UCT())
        s += 'Depth: {}, Action: {}, Hand: [{}]'.format(self.depth, self.action,
                                                        ', '.join([str(c) for c in self.hand]))
        return s

    def __repr__(self):
        """
        :return: string representation of the node.
        """
        return self.__str__()


def random_select(hand, state):
    """
    Logic for randomly selecting a card given the hand and state
    :param hand: the cards the player current has
    :param state: the current GameState
    :return: the card to play and the altered hand.
    """
    if state.leading_suit is not None:
        poss_cards = [card for i, card in enumerate(hand) if
                      i in hand.find_list([state.leading_suit])]
        if len(poss_cards) == 0:
            poss_cards = hand
    else:
        poss_cards = hand

    card_str = str(random.sample(list(poss_cards), 1)[0])
    card_to_play = hand.get(card_str)[0]
    return card_to_play, hand


def available_cards(p_hand, cards_out):
    """
    Creates a deck of all cards that are still out.
    :param p_hand: player's hand
    :param cards_out: cards that have already been played
    :return: deck that has cards that have not been played and are not in the player's hand
    """
    new_deck = pydealer.Deck()
    for card in (p_hand + cards_out):
        new_deck.get(str(card))
    return new_deck


class MonteCarloTreeSearch:
    """
    Implements the Monte Carlo Tree Search (MCTS)for the game Oh, Hell
    """
    def __init__(self, hand, state, player):
        """
        Creates an instance of the MCTS to find best move to make.

        :param hand: the hand of the player
        :param state: the current game state
        :param player: the player who is using this search
        """
        self.root = Node(copy.copy(hand), state, my_turn=True)
        self.player = player
        self.all_nodes = set()
        # Init children of root
        for card in hand:
            cp_hand = copy.deepcopy(hand)
            card_play = cp_hand.get(str(card))[0]
            new_state = self.root.state.play_card(self.player, card)
            child = Node(cp_hand, new_state, my_turn=True, action=card_play, parent=self.root)
            if len(child.hand) > 0:
                self.all_nodes.add(child)

    def next_move(self):
        """
        Simply performs a search over the root's children to find the best move to make.
        :return: the action of the best move to make.
        """
        best_ratio = 0
        best_child = self.root.children[0]
        for child in self.root.children:
            if child.n != 0:
                ratio = child.w / child.n
                if ratio > best_ratio:
                    best_child = child
                    best_ratio = ratio

        return best_child.action

    def update_all_nodes(self):
        """
        Removes all nodes that are not explorable further.
        """
        iter_nodes = list(self.all_nodes)
        for node in iter_nodes:
            if len(node.hand) == len(node.children):
                self.all_nodes.remove(node)

    def search(self, choose_func=None, max_search_time=1):
        """
        Performs the Monte Carlo Tree Search algorithm with a max amount of time allowed.
        :param choose_func: function for logic to decide what card to play.
        :param max_search_time: the maximum amount of town to run this algorithm.
        :return: the root node as well as the number of searches performed.
        """
        start_time = time.time()
        searches = 0
        while time.time() - start_time < max_search_time and len(self.all_nodes) > 0:
            search_node = self.selection()
            new_node = self.expansion(search_node, choose_func)
            end_state = self.simulation(new_node, choose_func)
            self.backpropogation(end_state, new_node)
            self.update_all_nodes()
            searches += 1
        return self.root, searches

    def selection(self):
        """
        Selection logic. Find the best node to explore further. UCT is used as the heuristic
        function to find the best node.
        """

        leaf_nodes = list(self.all_nodes)
        if len(leaf_nodes) == 0:
            return None
        else:
            # Select best leaf node
            best_node = leaf_nodes[0]
            best_score = best_node.UCT()
            for poss_node in leaf_nodes[1:]:
                score = poss_node.UCT()
                if score > best_score and not poss_node.state.terminal_state():
                    best_node = poss_node
                    best_score = score
            return best_node

    def expansion(self, search_node, choose_func=None):
        """
        Expands the current node by selecting one move to make.
        :param search_node: the node that was selected to be explored.
        :param choose_func: function for choosing cards to play
        :return: the new node created that is a child of the search node.
        """
        p = search_node
        if choose_func is None:
            choose_func = random_select

        current_state = p.state.copy_state()
        hand = copy.copy(p.hand)
        current_player = current_state.get_next_player()
        my_turn = False

        # Check if current player is null, means need to start next trick
        if current_player is None:
            trick_winner = current_state.finish_trick()
            current_player = current_state.get_next_player()

        # From current state, expand
        if current_player is self.player:
            card, hand = choose_func(hand, current_state)
            if current_state.on_leading_player():
                leading_suit = current_state.setup_trick(card)
            current_state = current_state.play_card(self.player, card)
            my_turn = True

        # Trick finished, clean up
        # Simulate action of other players
        else:
            cards_avail = available_cards(hand, current_state.discard)
            card, _ = choose_func(cards_avail, current_state)
            if current_state.on_leading_player():
                leading_suit = current_state.setup_trick(card)

            current_state = current_state.play_card(current_player, card)

        new_node = Node(hand, current_state, my_turn=my_turn, action=card, parent=p)
        self.all_nodes.add(new_node)

        return new_node

    def simulation(self, traverse_node, choose_func=None):
        """
        Runs the simulation of the game until a final state is found
        :param traverse_node: node being traversed until a leaf is found.
        :param choose_func: the function used for selecting a card to play
        :return: the final state once the terminal state is found.
        """
        if choose_func is None:
            choose_func = random_select
        current_state = traverse_node.state.copy_state()
        hand = copy.copy(traverse_node.hand)
        tricks_left = current_state.curr_hand_size - current_state.curr_trick
        for i in range(tricks_left):
            current_player = current_state.get_next_player()
            while current_player is not None:

                if current_player is self.player:
                    card, hand = choose_func(copy.copy(hand), current_state)
                    if current_state.on_leading_player():
                        leading_suit = current_state.setup_trick(card)
                    current_state = current_state.play_card(self.player, card)
                else:
                    cards_avail = available_cards(hand, current_state.discard)
                    card, _ = choose_func(cards_avail, current_state)
                    if current_state.on_leading_player():
                        leading_suit = current_state.setup_trick(card)
                    current_state = current_state.play_card(current_player, card)

                current_player = current_state.get_next_player()
            trick_winner = current_state.finish_trick()

        tracker_data = current_state.calculate_scores()

        return current_state

    def backpropogation(self, final_state, explore_node):
        """
        Updates the win and simulation variables in all nodes on the path from this leaf node
        back to the root.
        :param final_state: the state from the terminal node
        :param explore_node: the node that the simulations began from.
        """
        bid, taken = final_state.end_trick_info(self.player)
        won = bid == taken
        p = explore_node
        while p is not None:
            p.n += 1
            if won and p.my_turn:
                p.w += 1
            p = p.parent


if __name__ == '__main__':
    # MCTS experiment
    # Runs the experiments for seeing how well the MCTS algorithm fairs
    from OhHell import OhHell
    scores = {'1': [], '2': [], '3': [], '4': []}
    for _ in range(500):
        players = [PlayerMCTS(str(time), time) for depth in range(1,5)]
        game = OhHell(players, 5)
        for _ in range(9):
            game.play()
        scoreboard = {player.name: score_row[-1] for player, score_row in zip(players, game.state.get_scoreboard(players))}
        for player in scoreboard:
            scores[player].append(scoreboard[player])
    print('Experiment 1 Average Scores', {player: sum(scores[player]) / len(scores[player]) for player in scores})

    scores = {'1': [], '0.2': [], 'random_1': [], 'random_2': []}
    for _ in range(500):
        players = [
            PlayerMCTS('1', 1),
            Player('random_1', is_ai=True),
            PlayerMCTS('0.2', 0.2),
            Player('random_2', is_ai=True),
        ]
        game = OhHell(players, 5)
        for _ in range(9):
            game.play()
        scoreboard = {player.name: score_row[-1] for player, score_row in zip(players, game.state.get_scoreboard(players))}
        for player in scoreboard:
            scores[player].append(scoreboard[player])
    print('Experiment 2 Average Scores', {player: sum(scores[player]) / len(scores[player]) for player in scores})

# Experiment 1 Average Scores {'1': 16.836, '2': 13.016, '3': 13.048, '4': 13.36}
# Experiment 2 Average Scores {'1': 46.556, '0.2': 45.934, 'random_1': 42.81, 'random_2': 41.38}

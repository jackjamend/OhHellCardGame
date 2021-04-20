import numpy as np
import copy
import random
import time

import pydealer

from Player import Player


class PlayerMCTS(Player):
    def __init__(self, name, search_time=3):
        super().__init__(name, is_ai=True)
        self.search_time = search_time

    def play_card(self, state, leading_suit=None):
        mcts = MonteCarloTreeSearch(copy.copy(self.hand), state.copy_state(), self)
        mcts.search(max_search_time=self.search_time)
        card = mcts.next_move()
        card = self.hand.get(str(card))[0]

        return card


class Node:
    def __init__(self, hand, state, my_turn, action=None, parent=None):
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
        s = 'W: {}, N: {}, UCT: {}\n'.format(self.w, self.n, self.UCT())
        s += 'Depth: {}, Action: {}, Hand: [{}]'.format(self.depth, self.action,
                                                        ', '.join([str(c) for c in self.hand]))
        return s

    def __repr__(self):
        return self.__str__()


def random_select(hand, state):
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
    new_deck = pydealer.Deck()
    for card in (p_hand + cards_out):
        new_deck.get(str(card))
    return new_deck


class MonteCarloTreeSearch:
    def __init__(self, hand, state, player):
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
        iter_nodes = list(self.all_nodes)
        for node in iter_nodes:
            if len(node.hand) == len(node.children):
                #                 print('Removed node:',node)
                self.all_nodes.remove(node)

    def search(self, choose_func=None, max_search_time=1):
        start_time = time.time()
        searches = 0
        while time.time() - start_time < max_search_time and len(self.all_nodes) > 0:
            search_node = self.selection()
            new_node = self.expansion(search_node, choose_func)
            end_state = self.simulation(new_node, choose_func)
            self.backpropogation(end_state, new_node)
            self.update_all_nodes()
            searches += 1
        # Pick best action
        return self.root, searches

    def selection(self):
        #         print('{}{}{}'.format('-'*20, 'selection', '-'*20))
        #         print('Num all nodes:', len(self.all_nodes))
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
        #         print('{}{}{}'.format('-'*20, 'expansion', '-'*20))
        p = search_node
        if choose_func is None:
            choose_func = random_select

        current_state = p.state.copy_state()
        hand = copy.copy(p.hand)
        current_player = current_state.get_next_player()
        my_turn = False


        # Check if current player is null, means need to start next trick
        if current_player is None:
            #             print('Expansion - cp null')
            trick_winner = current_state.finish_trick()
            current_player = current_state.get_next_player()


        # From current state, expand
        if current_player is self.player:
            #             print('Move for current player')
            card, hand = choose_func(hand, current_state)
            if current_state.on_leading_player():
                leading_suit = current_state.setup_trick(card)
            current_state = current_state.play_card(self.player, card)
            my_turn = True
        #                 p = Node(hand, current_state, my_turn=True, action=card, parent=p)
        # Trick finished, clean up
        # Simulate action of other players
        else:
            #             print('Player {} turn'.format(current_player))
            cards_avail = available_cards(hand, current_state.discard)
            card, _ = choose_func(cards_avail, current_state)
            if current_state.on_leading_player():
                leading_suit = current_state.setup_trick(card)

            current_state = current_state.play_card(current_player, card)

        new_node = Node(hand, current_state, my_turn=my_turn, action=card, parent=p)
        self.all_nodes.add(new_node)

        return new_node

    def simulation(self, traverse_node, choose_func=None):
        #         print('{}{}{}'.format('-'*20, 'simulation', '-'*20))
        if choose_func is None:
            choose_func = random_select
        current_state = traverse_node.state.copy_state()
        hand = copy.copy(traverse_node.hand)
        tricks_left = current_state.curr_hand_size - current_state.curr_trick
        for i in range(tricks_left):
            current_player = current_state.get_next_player()
            while current_player is not None:
                #                 print(current_state.trick_progression())
                if current_player is self.player:
                    #                     print('Current player is self')
                    card, hand = choose_func(copy.copy(hand), current_state)
                    if current_state.on_leading_player():
                        leading_suit = current_state.setup_trick(card)
                    current_state = current_state.play_card(self.player, card)
                else:
                    #                     print("Player {}'s turn".format(current_player))
                    cards_avail = available_cards(hand, current_state.discard)
                    card, _ = choose_func(cards_avail, current_state)
                    if current_state.on_leading_player():

                        leading_suit = current_state.setup_trick(card)
                    current_state = current_state.play_card(current_player, card)


                #                 print('Player {} played {}'.format(current_player, card))
                current_player = current_state.get_next_player()
            trick_winner = current_state.finish_trick()
        #             print('Trick winner is', trick_winner)

        tracker_data = current_state.calculate_scores()

        #         print('t data::::', current_state.tracker.tricks_taken)
        return current_state

    def backpropogation(self, final_state, explore_node):
        #         print('{}{}{}'.format('-'*20, 'backpropogation', '-'*20))
        bid, taken = final_state.end_trick_info(self.player)
        #         print('Bid: {} Taken: {}'.format(bid, taken))
        won = bid == taken
        p = explore_node
        while p is not None:
            p.n += 1
            if won and p.my_turn:
                p.w += 1
            p = p.parent

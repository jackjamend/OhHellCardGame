import numpy as np


from Player import Player

class PlayerMCTS(Player):
    pass


class Node:
    def __init__(self, curr_hand, out_cards, parent=None):
        self.children = []
        self.parent = parent
        self.w = 0
        self.n = 0
        if self.parent is None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1

        self.hand = curr_hand
        self.out = out_cards

    def UCT(self, c=None):
        """
        Used to give numeric value to decide which node to explore. This the equation
        for the Upper Confidence Bound 1 applied to trees (UCT) that gives a value that
        balances exploitation and exploration ideas of the tree search. The origina equation
        is:
        UCT = w_i / n_i + c * sqrt(ln(n_p) / n_i)
        where, i denotes the current node and p denotes the parent node. w is the number of 
        simulations that this node resulted in a win and n is the total number of simulations.

        Error when parent is null i.e. root node.
        """
        if c is None:
            c = np.sqrt(2)
        exploitation = self.w / self.n
        exploration = c * np.sqrt(np.ln(self.parent.n) / self.n)
        return exploitation + exploration

class MonteCarloTreeSearch:
    def __init__(self, hand, discarded):
        self.root = Node(hand, discarded)

    def search(self):
        # Has children
        if len(self.root.children) > 1:
            pass

        # Leaf node
        else:
            # Make a possible move
            pass

    def selection(self):
        pass

    def expansion(self):
        pass

    def simulation(self):
        pass

    def backpropagation(self):
        pass


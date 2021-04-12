import pydealer
import random

class Player:
    def __init__(self, name, is_ai=False):
        self.scale_fact = 3
        self.hand = pydealer.Stack()
        self.name = name
        self.cards_observed = []
        self.is_ai = is_ai
    
    def make_bid(self, state, is_dealer):
        self.cards_observed = []
        size = len(self.hand) + 1
        bid_dist = [size-i-1 for i in range(size) for j in range(self.scale_fact*i+1)]
        if is_dealer:
            num_tricks = state.curr_hand_size
            tricks_out = sum(list(state.bids.values()))
            bad_bid = num_tricks - tricks_out
            if bad_bid >= 0:
                bid_dist = [i for i in bid_dist if i != bad_bid]
        bid = random.sample(bid_dist, k=1)[0]
        return bid

    def play_card(self, state, leading_suit=None):
        if leading_suit:
            poss_cards = [card for i, card in enumerate(self.hand) if i in self.hand.find_list([leading_suit])]
            if len(poss_cards) == 0:
                poss_cards = self.hand
        else:
            poss_cards = self.hand
        card_str = str(random.sample(list(poss_cards), 1)[0])
        card_to_play = self.hand.get(card_str)[0]
        return card_to_play
    
    def observe(self, cards_played):
        """
        Record cards played during round
        """
        self.cards_observed.append(cards_played)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

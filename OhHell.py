import pydealer
import numpy as np
from OhHellCardGame.TrickTracker import TrickTracker
from OhHellCardGame.GameState import GameState


class OhHell:
    total_cards = 52

    def __init__(self, players, max_hand=None, ask=lambda *args: None, inform=lambda *args: None):
        self.ask = ask
        self.inform = inform
        self.state = GameState(players, max_hand)
        self.players = players

    def play(self):
        """

        :return:
        """

        curr_hand_size, dealer = self.state.begin_round()

        # Output dealer
        self.display_dealer(dealer)
        # print('Dealer is', dealer)
        deck = pydealer.Deck()
        deck.shuffle()

        # Deal hand
        for player in self.players:
            player.hand += deck.deal(curr_hand_size)

        # Output player hands
        self.display_hands(self.players)

        # Set trump card
        trump_card = deck.deal(1)[0]

        self.state.set_trump_suit(trump_card)

        # Output trump card
        self.display_trump(trump_card)

        # Collect bids
        for player in self.state.get_bid_order():
            if not player.is_ai:
                bid = self.ask('bid_request', {player.name: bid for (player, bid) in
                                               self.state.bids.items()})
            else:
                bid = player.make_bid(self.state, player is dealer)

            self.state.collect_bid(player, bid)

        # Output current bids
        self.display_bids(self.state.bids)

        # Play tricks in round
        for i in range(curr_hand_size):
            # Single trick
            current_player = self.state.get_next_player()
            p_count = 0
            while current_player is not None:
                if not current_player.is_ai:
                    card = self.ask('card_request', {
                        'hand': [str(c) for c in current_player.hand],
                        'plays': {player.name: str(card) for (player, card) in
                                  self.state.trick_cards.items()}
                    })
                    card = current_player.hand.get(card)[0]
                else:
                    card = current_player.play_card(self.state)

                # Check if first player to display leading suit

                self.state = self.state.play_card(current_player, card)
                if p_count == 0:
                    self.display_leading_suit(card.suit)

                # Display card played
                self.display_card_played(current_player, card)

                current_player = self.state.get_next_player()
                p_count += 1
            p_count = 0
            trick_winner = self.state.finish_trick()

            # Output winner
            self.display_trick_winner(trick_winner)

        tracker_data = self.state.calculate_scores()

        # Output round data
        self.display_round_info(tracker_data)

        scoreboard = self.state.get_scoreboard(self.players)
        self.display_scoreboard(self.players, scoreboard, self.state.curr_round)

        # Shift dealer one over and set up for next round
        self.players = self.state.finish_round()

    def display_dealer(self, dealer):
        self.inform('dealer', dealer.name)

    def display_hands(self, players):
        hands = {}
        for player in players:
            hands[player.name] = [str(c) for c in player.hand]
        self.inform('hands', hands)

    def display_trump(self, trump_card):
        self.inform('trump', str(trump_card))

    def display_bids(self, bids):
        self.inform('bids', {player.name: bid for (player, bid) in bids.items()})

    def display_leading_suit(self, suit):
        self.inform('lead_suit', suit)

    def display_card_played(self, player, card):
        self.inform('play', { 'player': player.name, 'card': str(card) })

    def display_trick_winner(self, player):
        if any([not player.is_ai for player in self.players]):
            self.ask('trick_winner', player.name)
        else:
            self.inform('trick_winner', player.name)

    def display_round_info(self, tracker_output):
        self.inform('round_end', {player.name: info for player, info in tracker_output.items()})
        # for player, info in tracker_output.items():
        #     if info[0] == info[1]:
        #         print('{} made their bid of {}'.format(player, info[0]))
        #     else:
        #         print('{} missed their bid of {}, getting {} tricks'.format(player, info[1], info[0]))

    def display_scoreboard(self, players, scoreboard, curr_round):
        self.inform('scores', {player.name: score_row[curr_round] for player, score_row in zip(players, scoreboard)})

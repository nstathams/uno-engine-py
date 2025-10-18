from __future__ import annotations

import random
from random import getrandbits
from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class RandomBot(Player):
    """
    An extremely rudimentary bot that makes a random move each turn.
    """

    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)
        self._top_card: Optional[Card] = None
        self._current_color: Optional[CardColor] = None

    def update_game_state(
        self, playable_cards: List[Card], top_card: Card, current_color: CardColor
    ) -> None:
        """
        Update bot's knowledge of current game state
        """
        self._top_card = top_card
        self._current_color = current_color

    def choose_action(self) -> PlayerAction:
        """
        Returns a random card action or draw action.
        """
        while True:
            selection = random.randint(0, len(self.hand))

            if selection == len(self.hand):
                return PlayerAction(draw_card=True)
            elif self.hand[selection].can_play_on(self._top_card, self._current_color):
                card_to_play = self.hand[selection]
                new_color = None

                if card_to_play.is_wild:
                    new_color = self.choose_color(card_to_play)

                return self.play_card(card_to_play, new_color)
            else:
                # Card not playable, continue searching
                continue

    def choose_color(self, wild_card: Card) -> CardColor:
        """
        Returns a random color for a wild card.
        """
        # Choose randomly from the four main colors (excluding WILD)
        return random.choice(
            [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]
        )

    def decide_say_uno(self) -> bool:
        """
        Randomly decide whether to say UNO (50% chance)
        """
        return not getrandbits(1)  # Equivalent to random.choice([True, False])

    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        """
        Returns a random response to decide if the player would like to play the valid card they just drew.
        """
        # Only consider playing if the card is actually playable
        if drawn_card.can_play_on(self._top_card, self._current_color):
            return not getrandbits(1)  # 50%
        return False

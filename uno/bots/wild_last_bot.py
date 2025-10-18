from __future__ import annotations

import random
from random import getrandbits
from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class WildLastBot(Player):
    """
    A bot that saves its wild cards for last, granting them freedom in the late game.
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
        Returns a valid card or draw action. Excludes wild cards unless player has "UNO."
        """
        has_uno = self.has_uno()

        # Create a list of valid selections with (index, card) tuples
        valid_selections = []
        for index, card in enumerate(self.hand):
            if card.can_play_on(self._top_card, self._current_color):
                valid_selections.append((index, card))

        if valid_selections and has_uno:
            # Special case where we play the valid card no matter what (UNO situation)
            index, card = valid_selections[0]
            new_color = self.choose_color(card) if card.is_wild else None
            return self.play_card(card, new_color)

        elif valid_selections:
            # Count our normal cards (non-wilds)
            non_wilds = [
                selection for selection in valid_selections if not selection[1].is_wild
            ]

            # Did we find any non-wild cards?
            if non_wilds:
                # Play a random non-wild card
                index, card = random.choice(non_wilds)
                return self.play_card(card)

            # We have no non-wilds available. How many wild cards do we have?
            # Do we have more than one? We can still save one for later.
            elif len(valid_selections) > 1:
                # Play a random wild card (but save some for later)
                index, card = random.choice(valid_selections)
                new_color = self.choose_color(card) if card.is_wild else None
                return self.play_card(card, new_color)

            # If we only have one wild or no wilds, there's nothing to do but draw.
            else:
                return PlayerAction(draw_card=True)

        else:
            return PlayerAction(draw_card=True)

    def choose_color(self, wild_card: Card) -> CardColor:
        """
        Returns an advantageous color for a wild card.
        """
        color_counts = {
            color: 0
            for color in [
                CardColor.RED,
                CardColor.BLUE,
                CardColor.GREEN,
                CardColor.YELLOW,
            ]
        }

        # Count non-wild cards by color
        for card in self.hand:
            if not card.is_wild:
                color_counts[card.color] += 1

        # Return the color with the most cards
        return max(color_counts, key=color_counts.get)

    def decide_say_uno(self) -> bool:
        """
        Randomly decide whether to say UNO (50% chance)
        """
        return not getrandbits(1)

    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        """
        If the drawn card is wild, return false. Otherwise, return true.
        """
        return not drawn_card.is_wild and drawn_card.can_play_on(
            self._top_card, self._current_color
        )

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..engine.card import Card, CardColor


class PlayerAction:
    """Represents a player's action in the game"""

    def __init__(
        self,
        card: Optional[Card] = None,
        new_color: Optional[CardColor] = None,
        draw_card: bool = False,
        say_uno: bool = False,
    ):
        self.card = card
        self.new_color = new_color
        self.draw_card = draw_card
        self.say_uno = say_uno

    def is_valid(self) -> bool:
        """Check if this is a valid action"""
        if self.draw_card:
            return self.card is None and self.new_color is None
        elif self.card is not None:
            return True
        return False


class Player(ABC):
    """
    Base class for all UNO players (human and bots)
    Handles common player functionality and defines abstract methods for AI
    """

    def __init__(self, name: str, player_id: int):
        self.name = name
        self.player_id = player_id
        self.hand: List[Card] = []
        self.has_said_uno = False
        self.score = 0

    # Core player methods
    def add_card_to_hand(self, card: Card) -> None:
        """Add a card to player's hand"""
        self.hand.append(card)
        self.has_said_uno = False  # Reset UNO status when getting new cards
        self._sort_hand()  # Keep hand organized

    def add_cards_to_hand(self, cards: List[Card]) -> None:
        """Add multiple cards to player's hand"""
        self.hand.extend(cards)
        self.has_said_uno = False
        self._sort_hand()

    def play_card(
        self, card: Card, new_color: Optional[CardColor] = None
    ) -> PlayerAction:
        """Play a card from hand"""
        if card not in self.hand:
            raise ValueError(f"Card {card} not in player's hand")

        self.__remove_card_from_hand(card)
        action = PlayerAction(card=card, new_color=new_color)
        self._last_action = action
        return action

    def __remove_card_from_hand(self, card: Card):
        self.hand.remove(card)

    def say_uno(self) -> None:
        """Mark that player has said UNO"""
        if len(self.hand) == 1:
            self.has_said_uno = True

    def has_uno(self) -> bool:
        """Check if player has UNO (one card left)"""
        return len(self.hand) == 1

    def has_won(self) -> bool:
        """Check if player has won (no cards left)"""
        return len(self.hand) == 0

    def get_hand_size(self) -> int:
        """Get current hand size"""
        return len(self.hand)

    def calculate_hand_score(self) -> int:
        """Calculate total points in hand (for scoring)"""
        return sum(card.points for card in self.hand)

    def _sort_hand(self) -> None:
        """Sort hand by color and then by label for better organization"""
        self.hand.sort(key=lambda card: (card.color.value, card.label.value))

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def choose_action(self) -> PlayerAction:
        """
        Choose which action to take
        Must be implemented by subclasses
        """
        pass

    @abstractmethod
    def choose_color(self, wild_card: Card) -> CardColor:
        """
        Choose a color when playing a wild card
        Must be implemented by subclasses
        """
        pass

    @abstractmethod
    def decide_say_uno(self) -> bool:
        """
        Decide whether to say UNO when down to one card
        Must be implemented by subclasses
        """
        pass

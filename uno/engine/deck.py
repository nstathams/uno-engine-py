from __future__ import annotations

import math
import random
from collections import deque
from typing import Deque, Iterator, List

from .card import Card, CardColor, CardFactory, CardLabel


class Deck:
    """
    UNO Deck implementation using collections.deque for efficient operations.
    Follows standard 108-card UNO configuration.
    """

    # Class constants for deck composition
    _NUMBERS = list(range(10))
    _ACTIONS = [CardLabel.SKIP, CardLabel.REVERSE, CardLabel.DRAW_TWO]
    _WILDS = [CardLabel.WILD, CardLabel.WILD_DRAW_FOUR]
    _COLORS = [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]

    def __init__(self, initialize: bool = True) -> None:
        """
        Initialize a new UNO deck using deque for efficient pop/append operations.

        Args:
            initialize: If True, creates a standard 108-card UNO deck.
                       If False, creates an empty deck.
        """
        self._cards: Deque[Card] = deque()

        if initialize:
            self._initialize_standard_deck()

        self.shuffle()

    def _initialize_standard_deck(self) -> None:
        """Initialize the deck with standard UNO card distribution"""
        self._cards.clear()
        cards_to_add: List[Card] = []

        # Add number cards (one 0, two of each 1-9 per color)
        for color in self._COLORS:
            # One zero card per color
            cards_to_add.append(CardFactory.create_number_card(color, 0))

            # Two of each number 1-9 per color
            for number in range(1, 10):
                cards_to_add.append(CardFactory.create_number_card(color, number))
                cards_to_add.append(CardFactory.create_number_card(color, number))

        # Add action cards (two of each per color)
        for color in self._COLORS:
            for action in self._ACTIONS:
                cards_to_add.append(CardFactory.create_action_card(color, action))
                cards_to_add.append(CardFactory.create_action_card(color, action))

        # Add wild cards (four of each type)
        for wild_type in self._WILDS:
            for _ in range(4):
                cards_to_add.append(CardFactory.create_wild_card(wild_type))

        # Use extend for bulk addition (more efficient than multiple appends)
        self._cards.extend(cards_to_add)

    def all_cards_from_deck(self) -> Deque:
        return self._cards

    def shuffle(self) -> None:
        """
        Shuffle the deck using random.shuffle on a temporary list.
        More efficient than shuffling deque directly.
        """
        cards_list = list(self._cards)
        deck_size = len(cards_list)
        num_shuffles = math.ceil(1.5 * math.log2(deck_size))
        for i in range(num_shuffles):
            random.shuffle(cards_list)
        self._cards = deque(cards_list)

    def draw(self, count: int = 1) -> List[Card]:
        """
        Draw specified number of cards from the top of the deck.

        Args:
            count: Number of cards to draw

        Returns:
            List of drawn cards

        Raises:
            ValueError: If count is negative or exceeds deck size
        """
        if self.is_empty():
            return None

        if count < 0:
            raise ValueError(f"Cannot draw negative number of cards: {count}")

        if count > len(self._cards):
            raise ValueError(
                f"Cannot draw {count} cards from deck with {len(self._cards)} cards"
            )

        return [self._cards.popleft() for _ in range(count)]

    def add_card(self, card: Card) -> None:
        """
        Add a single card to the bottom of the deck.

        Args:
            card: Card to add
        """
        self._cards.append(card)

    def add_cards(self, cards: List[Card]) -> None:
        """
        Add multiple cards to the bottom of the deck.

        Args:
            cards: List of cards to add
        """
        self._cards.extend(cards)

    def add_to_top(self, card: Card) -> None:
        """
        Add a card to the top of the deck (will be drawn next).
        Args:
            card: Card to add to top
        """
        self._cards.appendleft(card)

    def add_cards_to_top(self, cards: List[Card]) -> None:
        """
        Add multiple cards to the top of the deck.
        Cards will be drawn in reverse order of the input list.

        Args:
            cards: List of cards to add to top
        """
        for card in reversed(cards):
            self._cards.appendleft(card)

    def is_empty(self) -> bool:
        """
        Check if deck is empty.

        Returns:
            True if deck has no cards, False otherwise
        """
        return len(self._cards) == 0

    def size(self) -> int:
        """
        Get current number of cards in deck.

        Returns:
            Number of cards in deck
        """
        return len(self._cards)

    def peek(self, count: int = 1) -> List[Card]:
        """
        Peek at top cards without removing them.

        Args:
            count: Number of cards to peek at

        Returns:
            List of top cards

        Raises:
            ValueError: If count is negative or exceeds deck size
        """
        if count < 0:
            raise ValueError(f"Cannot peek negative number of cards: {count}")

        if count > len(self._cards):
            raise ValueError(
                f"Cannot peek at {count} cards from deck with {len(self._cards)} cards"
            )

        # Convert to list slice for the first 'count' elements
        return list(self._cards)[:count]

    def clear(self) -> None:
        """Remove all cards from the deck."""
        self._cards.clear()

    def rotate(self, positions: int) -> None:
        """
        Rotate the deck by specified number of positions.
        Positive values rotate right, negative values rotate left.

        Args:
            positions: Number of positions to rotate
        """
        self._cards.rotate(positions)

    def __len__(self) -> int:
        """Support for len(deck). O(1) time complexity."""
        return len(self._cards)

    def __bool__(self) -> bool:
        """Support for truth value testing. O(1) time complexity."""
        return not self.is_empty()

    def __iter__(self) -> Iterator[Card]:
        """Support for iteration over the deck."""
        return iter(self._cards)

    def __contains__(self, card: Card) -> bool:
        """Support for 'in' operator. O(n) time complexity."""
        return card in self._cards

    def __str__(self) -> str:
        return f"UNO Deck with {self.size()} cards"

    def __repr__(self) -> str:
        return f"Deck(cards={self.size()})"

    def get_card_distribution(self) -> dict:
        """
        Get distribution of cards in the deck by type.
        How many cards in deck.

        Returns:
            Dictionary with card type counts
        """
        distribution = {
            "total": self.size(),
            "number_cards": 0,
            "action_cards": 0,
            "wild_cards": 0,
            "by_color": {color.name: 0 for color in CardColor},
            "by_label": {label.name: 0 for label in CardLabel},
        }

        for card in self._cards:
            distribution["by_color"][card.color.name] += 1
            distribution["by_label"][card.label.name] += 1

            if card.is_number_card:
                distribution["number_cards"] += 1
            elif card.is_action_card:
                distribution["action_cards"] += 1
            elif card.is_wild:
                distribution["wild_cards"] += 1

        return distribution

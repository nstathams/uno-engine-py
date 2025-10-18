from __future__ import annotations

from enum import IntEnum
from typing import Optional


class CardColor(IntEnum):
    """
    Enum class for the color of the card
    """

    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3
    WILD = 4


class CardLabel(IntEnum):
    """
    Enum class for the value/number of the card
    """

    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    SKIP = 10
    REVERSE = 11
    DRAW_TWO = 12
    WILD = 13
    WILD_DRAW_FOUR = 14


class EffectState(IntEnum):
    """
    State machine states for card effects
    """

    NO_EFFECT = 0
    PENDING = 1
    APPLIED = 2
    RESOLVED = 3


class CardEffect:
    """
    State machine for UNO card effects with numeric state management
    """

    def __init__(self) -> None:
        # Effect state
        self._state: EffectState = EffectState.NO_EFFECT

        # Effect properties
        self._color_change: Optional[CardColor] = None
        self._draw_count: int = 0
        self._skip_count: int = 0
        self._reverse_direction: bool = False

        # Stacking effects (for multiple DRAW cards)
        self._stackable: bool = False

    # State management
    @property
    def state(self) -> EffectState:
        return self._state

    # Some usefull methods 

    def set_pending(self) -> None:
        """Set effect to pending state"""
        if self._state == EffectState.NO_EFFECT:
            self._state = EffectState.PENDING

    def set_applied(self) -> None:
        """Set effect to applied state"""
        if self._state == EffectState.PENDING:
            self._state = EffectState.APPLIED

    def set_resolved(self) -> None:
        """Set effect to resolved state"""
        if self._state == EffectState.APPLIED:
            self._state = EffectState.RESOLVED

    def reset_state(self) -> None:
        """Reset effect to no effect state"""
        self._state = EffectState.NO_EFFECT
        self.clear_effects()

    def is_active(self) -> bool:
        """Check if effect is active (pending or applied)"""
        return self._state in (EffectState.PENDING, EffectState.APPLIED)

    def is_pending(self) -> bool:
        """Check if effect is pending"""
        return self._state == EffectState.PENDING

    def is_applied(self) -> bool:
        """Check if effect is applied"""
        return self._state == EffectState.APPLIED

    def is_resolved(self) -> bool:
        """Check if effect is resolved"""
        return self._state == EffectState.RESOLVED

    # Effect properties with state transitions
    @property
    def color_change(self) -> Optional[CardColor]:
        return self._color_change

    @color_change.setter
    def color_change(self, color: Optional[CardColor]) -> None:
        if color is not None:
            if not isinstance(color, CardColor):
                raise ValueError("color_change must be a CardColor or None")
            if color == CardColor.WILD:
                raise ValueError("Cannot change to WILD color")
            self.set_pending()
        self._color_change = color

    @property
    def draw_count(self) -> int:
        return self._draw_count

    @draw_count.setter
    def draw_count(self, count: int) -> None:
        if not isinstance(count, int) or count < 0:
            raise ValueError("draw_count must be a non-negative integer")
        if count > 0:
            self.set_pending()
        self._draw_count = count

    @property
    def skip_count(self) -> int:
        return self._skip_count

    @skip_count.setter
    def skip_count(self, count: int) -> None:
        if not isinstance(count, int) or count < 0:
            raise ValueError("skip_count must be a non-negative integer")
        if count > 0:
            self.set_pending()
        self._skip_count = count

    @property
    def reverse_direction(self) -> bool:
        return self._reverse_direction

    @reverse_direction.setter
    def reverse_direction(self, reverse: bool) -> None:
        if not isinstance(reverse, bool):
            raise ValueError("reverse_direction must be a boolean")
        if reverse:
            self.set_pending()
        self._reverse_direction = reverse

    @property
    def stackable(self) -> bool:
        return self._stackable

    @stackable.setter
    def stackable(self, stackable: bool) -> None:
        self._stackable = stackable

    # Effect operations
    def has_effects(self) -> bool:
        """Check if there are any effects configured"""
        return (
            self._color_change is not None
            or self._draw_count > 0
            or self._skip_count > 0
            or self._reverse_direction
        )

    def clear_effects(self) -> None:
        """Clear all effects and reset state"""
        self._color_change = None
        self._draw_count = 0
        self._skip_count = 0
        self._reverse_direction = False
        self._stackable = False
        self.reset_state()

    def combine(self, other: CardEffect) -> None:
        """
        Combine effects with another CardEffect (state machine aware)
        """
        if other.state != EffectState.NO_EFFECT:
            self.set_pending()

        # Color change takes precedence
        if other.color_change is not None:
            self.color_change = other.color_change

        # Additive effects
        self.draw_count += other.draw_count
        self.skip_count += other.skip_count

        # Boolean effects (OR logic)
        if other.reverse_direction:
            self.reverse_direction = True

        # Stacking logic
        if other.stackable:
            self.stackable = True

    def execute_draw(self) -> int:
        """Execute draw effect and return number of cards drawn"""
        if self.is_applied() and self._draw_count > 0:
            drawn = self._draw_count
            self._draw_count = 0
            return drawn
        return 0

    def execute_skip(self) -> int:
        """Execute skip effect and return number of turns skipped"""
        if self.is_applied() and self._skip_count > 0:
            skipped = self._skip_count
            self._skip_count = 0
            return skipped
        return 0


class Card:
    """
    Represents an UNO card with color and label properties.
    Handles card validation and game logic.
    """

    # Class constants for special cards
    ACTION_CARDS = {CardLabel.SKIP, CardLabel.REVERSE, CardLabel.DRAW_TWO}
    WILD_CARDS = {CardLabel.WILD, CardLabel.WILD_DRAW_FOUR}

    def __init__(self, color: CardColor, label: CardLabel) -> None:
        self._validate_card(color, label)
        self._color = color
        self._label = label
        self._is_wild = label in self.WILD_CARDS

    def _validate_card(self, color: CardColor, label: CardLabel) -> None:
        """Validate if the card combination is legal"""
        # Wild cards must have WILD color
        if label in self.WILD_CARDS and color != CardColor.WILD:
            raise ValueError(f"Wild cards ({label.name}) must have WILD color")

        # Non-wild cards cannot have WILD color
        if label not in self.WILD_CARDS and color == CardColor.WILD:
            raise ValueError(f"Non-wild cards cannot have WILD color")

        # Number cards must be 0-9
        if (
            not self._is_number_card(label)
            and not self._is_action_card(label)
            and not self._is_wild_card(label)
        ):
            raise ValueError(f"Invalid card label: {label}")

    @property
    def color(self) -> CardColor:
        return self._color

    @property
    def label(self) -> CardLabel:
        return self._label

    @property
    def is_wild(self) -> bool:
        return self._is_wild

    @property
    def is_action_card(self) -> bool:
        return self._label in self.ACTION_CARDS

    @property
    def is_number_card(self) -> bool:
        return self._is_number_card(self._label)

    @property
    def points(self) -> int:
        """Calculate point value of the card according to UNO rules"""
        if self.is_number_card:
            return self._label.value
        elif self.is_action_card:
            return 20
        elif self.is_wild:
            return 50
        return 0

    def can_play_on(
        self, other: "Card", current_color: Optional[CardColor] = None
    ) -> bool:
        """
        Check if this card can be played on another card
        """
        if self.is_wild:
            return True

        # Same color
        if self.color == (current_color or other.color):
            return True

        # Same label/number (but not for wild cards)
        if self.label == other.label and not other.is_wild:
            return True

        return False

    def play(self, new_color: Optional[CardColor] = None) -> dict:
        """
        Play the card and return effects
        """
        effects = {
            "color_change": None,
            "draw_cards": 0,
            "skip_turn": False,
            "reverse": False,
        }

        if self.is_wild and new_color:
            if new_color == CardColor.WILD:
                raise ValueError("Cannot change to WILD color")
            effects["color_change"] = new_color

        if self.label == CardLabel.DRAW_TWO:
            effects["draw_cards"] = 2
        elif self.label == CardLabel.WILD_DRAW_FOUR:
            effects["draw_cards"] = 4
        elif self.label == CardLabel.SKIP:
            effects["skip_turn"] = True
        elif self.label == CardLabel.REVERSE:
            effects["reverse"] = True

        return effects

    @classmethod
    def _is_number_card(cls, label: CardLabel) -> bool:
        return label.value <= 9

    @classmethod
    def _is_action_card(cls, label: CardLabel) -> bool:
        return label in cls.ACTION_CARDS

    @classmethod
    def _is_wild_card(cls, label: CardLabel) -> bool:
        return label in cls.WILD_CARDS

    def __str__(self) -> str:
        return f"{self.color.name} {self.label.name}"

    def __repr__(self) -> str:
        return f"Card({self.color.name}, {self.label.name})"

    # Comparison methods for sorting
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.color == other.color and self.label == other.label

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        if self.color == other.color:
            return self.label < other.label
        return self.color < other.color

    def __hash__(self) -> int:
        return hash((self.color, self.label))


class CardFactory:
    """
    Factory class to create UNO cards and decks
    """

    @staticmethod
    def create_number_card(color: CardColor, number: int) -> Card:
        """Create a number card (0-9)"""
        if not 0 <= number <= 9:
            raise ValueError("Number must be between 0 and 9")
        return Card(color, CardLabel(number))

    @staticmethod
    def create_action_card(color: CardColor, action: CardLabel) -> Card:
        """Create an action card (Skip, Reverse, Draw Two)"""
        if action not in Card.ACTION_CARDS:
            raise ValueError(f"Invalid action card: {action}")
        return Card(color, action)

    @staticmethod
    def create_wild_card(wild_type: CardLabel) -> Card:
        """Create a wild card (Wild or Wild Draw Four)"""
        if wild_type not in Card.WILD_CARDS:
            raise ValueError(f"Invalid wild card: {wild_type}")
        return Card(CardColor.WILD, wild_type)

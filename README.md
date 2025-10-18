# UNO Engine & Bot Framework

A comprehensive UNO card game engine with multiple AI bot implementations, designed for simulating and analyzing UNO gameplay strategies at scale.

## Available Bot Types

| Bot Type | Strategy Description | Play Style |
|----------|---------------------|------------|
| **RandomBot** | Completely random valid moves | Chaotic |
| **WildFirstBot** | Plays wild cards immediately | Aggressive |
| **WildLastBot** | Saves wild cards for endgame | Conservative |

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd uno-engine-py

# Install dependencies
uv sync

# Install development dependencies
uv sync --dev
```

### Running Simulations

```bash
# Run the main simulation interface
uv run main.py
```

## Usage Examples

### Large-scale Simulation
```python
from uno.simulation.runner import UnoSimulation
from uno.bots import *

bots = [
    RandomBot("Random1", 1),
    OffensiveBot("Offensive", 2),
    DefensiveBot("Defensive", 3),
    BalancedBot("Balanced", 4)
]

simulation = UnoSimulation(bots, num_games=10000)
stats = simulation.run_simulation()
simulation.plot_statistics(stats)
```


Example output from 10,000 game simulation:
```
Win Statistics:
----------------------------------------
WildFirst (WildFirstBot):  3357 wins ( 33.57%)
WildLast (WildLastBot):  1872 wins ( 18.72%)
Random4 (RandomBot):  1225 wins ( 12.25%)
Random2 (RandomBot):  1223 wins ( 12.23%)
Random1 (RandomBot):  1188 wins ( 11.88%)
Random3 (RandomBot):  1135 wins ( 11.35%)
```

## Project Structure

```
uno-engine-py/
├── uno/
│   ├── engine/
│   │   ├── engine.py          # Main game engine
│   │   ├── deck.py            # Deck management
│   │   └── card.py            # Card classes and logic
│   ├── bots/
│   │   ├── random_bot.py      # Random strategy
│   │   ├── wild_first_bot.py  # Wild-first strategy
│   │   └── wild_last_bot.py   # Wild-last strategy
|   └── player/
|       └── player.py # Player Abstract class
├── main.py                    # Entry point
├── pyproject.toml            # Project configuration
└── README.md
```


### Creating New Bots

1. Extend the `Player` base class:
```python
from uno.player.player import Player

class MyCustomBot(Player):
    def choose_action(self) -> PlayerAction:
        # Implement your strategy here
        pass
    
    def choose_color(self, wild_card: Card) -> CardColor:
        # Color selection logic
        pass
```

2. Implement the required abstract methods
3. Add your bot to the simulation runner






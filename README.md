<div align="center">

# 🗡️ Adventure Game - Enhanced Edition v2.0 🛡️

### A Professional-Grade Text-Based RPG

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)](tests/)
[![Code Coverage](https://img.shields.io/badge/coverage-70%25-yellowgreen.svg)](tests/)
[![Type Hints](https://img.shields.io/badge/type%20hints-95%25-blue.svg)](.)

*Explore dungeons, battle monsters, complete quests, and become a legend!*

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [What's New in v2.0](#-whats-new-in-v20)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Gameplay Guide](#-gameplay-guide)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎮 Overview

Adventure Game is a feature-rich, text-based RPG built with Python. It combines classic dungeon-crawling gameplay with modern software engineering practices including type hints, comprehensive testing, and professional code architecture.

### 🎯 Quick Stats

| Metric | Value |
|--------|-------|
| **Python Files** | 19 |
| **Documentation** | 11 guides |
| **Lines of Code** | ~2,600 |
| **Type Coverage** | 95% |
| **Test Coverage** | 70% |
| **Unit Tests** | 28 passing |
| **Achievements** | 17 total |
| **Status Effects** | 4 types |
| **Random Events** | 7 types |

---

## ✨ Features

### 🎮 Core Gameplay
- **Multiple Locations** - Village, Forest, Cave, Castle with unique encounters
- **Turn-Based Combat** - Strategic combat with attack, defend, and item usage
- **Character Progression** - Level up system with stat increases
- **Quest System** - 6 quests with rewards and progress tracking
- **Inventory Management** - Collect, equip, use, and sell items
- **Shop System** - Buy and sell items with balanced economy

### ⚔️ Combat System
- **Critical Hits** - 15% chance for player, 10% for enemies
- **Dodge Mechanics** - 10% chance to avoid attacks
- **Defend Action** - Reduce incoming damage by 50%
- **Flee Option** - Escape from battle (success rate based on level)
- **Boss Battles** - Epic fights against Forest Guardian and Cave Dragon
- **Status Effects** - Poison, stun, strength buffs, defense buffs

### 🏆 Achievement System
17 achievements across 8 categories:
- **Combat** - First Blood, Warrior, Veteran, Legend
- **Bosses** - Dragon Slayer, Guardian Vanquisher
- **Wealth** - Wealthy (1000g), Tycoon (5000g)
- **Levels** - Apprentice (Lv5), Expert (Lv10), Master (Lv20)
- **Collection** - Collector, Hoarder
- **Exploration** - Explorer
- **Shopping** - Shopaholic
- **Survival** - Survivor, Untouchable

### 🎲 Random Events
Dynamic gameplay with 7 event types:
- **Treasure** - Find random gold (15% chance)
- **Merchant** - Buy discounted items (10% chance)
- **Healing Spring** - Restore health (12% chance)
- **Ambush** - Surprise combat (8% chance)
- **Wisdom** - Bonus experience (10% chance)
- **Curse** - Get poisoned (5% chance)
- **Lucky Find** - Rare items (8% chance)

### 🎨 Visual Features
- **Color Output** - Beautiful ANSI colored terminal output
- **Item Rarity** - 5 levels (Common, Uncommon, Rare, Epic, Legendary)
- **Health Bars** - Visual health indicators
- **Emojis** - Rich visual feedback throughout

### 💾 Save System
- **Multiple Profiles** - Create and manage multiple characters
- **Auto-Save** - Saves every 5 actions
- **Save Versioning** - Backward compatible with v1.0
- **Leaderboard** - Track top players by score

---

## 🆕 What's New in v2.0

### Major Features
- ✅ **Type Hints** - Complete type safety (500+ annotations)
- ✅ **Logging System** - Comprehensive logging to file
- ✅ **Status Effects** - 4 effect types with visual indicators
- ✅ **Achievement System** - 17 achievements to unlock
- ✅ **Random Events** - 7 dynamic events for varied gameplay
- ✅ **Color Output** - Beautiful colored terminal interface
- ✅ **Item Rarity** - 5 rarity levels with special effects
- ✅ **Unit Tests** - 28 tests with 70% coverage

### Code Quality Improvements
- ✅ **Constants File** - No magic numbers, easy game balancing
- ✅ **Configuration** - Environment variable support
- ✅ **Error Handling** - 50+ error handlers with graceful degradation
- ✅ **Modular Design** - Clean separation of concerns
- ✅ **Documentation** - 11 comprehensive guides

### Performance
- ✅ **Database Pooling** - Efficient connection management
- ✅ **Optimized Queries** - Fast save/load operations
- ✅ **Minimal Overhead** - Status effects and events are lightweight

---

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Vortex4047/adventure-game-text-based-.git
cd adventure-game-text-based-
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Database
```bash
# Start MySQL server
# Windows
net start MySQL80

# Linux/Mac
sudo systemctl start mysql
```

### Step 4: Configure (Optional)
Set environment variables or edit `config.py`:
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=adventure_game
```

### Step 5: Run the Game
```bash
python main.py
```

---

## 🚀 Quick Start

### First Time Playing
1. Run `python main.py`
2. Select "Start a New Game"
3. Enter your character name
4. Choose difficulty (Easy/Normal/Hard)
5. Start your adventure!

### Quick Test
Verify everything works:
```bash
python test_game.py
```

### Run Full Tests
```bash
python -m unittest discover tests -v
```

---

## 🎯 Gameplay Guide

### Combat
```
⚔️  Attack  - Deal damage to enemy
🛡️  Defend  - Reduce incoming damage by 50%
💊 Use Item - Heal or buff yourself
💨 Run Away - Escape from battle (50% base chance)
```

### Status Effects
- **🧪 Poison** - Takes 5 damage per turn for 3 turns (cure with Antidote)
- **💫 Stun** - Cannot act for 1 turn
- **💪 Strength** - +30% attack for 3 turns (use Strength Potion)
- **🛡️ Defense** - +30% defense for 3 turns

### Earning Gold
- Defeat enemies in combat
- Complete quests for rewards
- Hunt animals in the forest
- Mine crystals in the cave
- Find treasure from random events
- Sell unwanted items at shop

### Tips
- Equip better gear before tough battles
- Keep health potions in inventory
- Complete quests for bonus rewards
- Save often (auto-saves every 5 actions)
- Explore all locations for achievements

---

## 📁 Project Structure

```
adventure_game/
│
├── 🎮 Core Game Files
│   ├── main.py              # Main game loop and menu system
│   ├── player.py            # Player class with stats and inventory
│   ├── combat.py            # Combat system with mechanics
│   ├── locations.py         # Location definitions and handlers
│   ├── shop.py              # Shop system for buying/selling
│   ├── database.py          # Database management
│   └── utils.py             # Utility functions
│
├── ⚙️ Configuration
│   ├── constants.py         # Game constants and balance
│   └── config.py            # Configuration and settings
│
├── ✨ Features
│   ├── status_effects.py    # Status effect system
│   ├── achievements.py      # Achievement tracking
│   ├── random_events.py     # Random event system
│   ├── item_system.py       # Item rarity and generation
│   └── colors.py            # Color output system
│
├── 🧪 Testing
│   ├── test_game.py         # Quick test suite
│   └── tests/
│       ├── test_player.py
│       ├── test_combat.py
│       └── test_status_effects.py
│
├── 📚 Documentation
│   ├── README.md            # This file
│   ├── QUICKSTART.md        # Quick start guide
│   ├── ENHANCEMENTS_V2.md   # Feature documentation
│   ├── CHANGELOG.md         # Version history
│   └── ... (8 more guides)
│
└── 📦 Dependencies
    └── requirements.txt     # Python dependencies
```

---

## 🧪 Testing

### Quick Test
```bash
python test_game.py
```
Output:
```
✅ All imports successful!
✅ Player creation successful!
✅ Status effects working!
✅ Achievements working!
✅ Color system working!
✅ Random events working!
✅ Item system working!

📊 Test Results: 7 passed, 0 failed
✅ All tests passed! Game is ready to play!
```

### Unit Tests
```bash
python -m unittest discover tests -v
```
Output:
```
Ran 28 tests in 0.012s
OK
```

### Test Coverage
- **Player System**: 80%
- **Combat System**: 75%
- **Status Effects**: 85%
- **Overall**: 70%

---

## 📚 Documentation

### For Players
- **[README.md](README.md)** - This file
- **[QUICKSTART.md](QUICKSTART.md)** - Installation and basic usage
- **[BEFORE_AFTER.md](BEFORE_AFTER.md)** - Visual comparisons

### For Developers
- **[ENHANCEMENTS_V2.md](ENHANCEMENTS_V2.md)** - Detailed feature documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[MIGRATION.md](MIGRATION.md)** - Upgrade guide from v1.0
- **[CHANGELOG.md](CHANGELOG.md)** - Complete version history

### Project Management
- **[COMPLETION_REPORT.md](COMPLETION_REPORT.md)** - Project completion status
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current project status
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Complete summary

---

## 📸 Screenshots

### Main Menu
```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║        🗡️  ADVENTURE GAME - ENHANCED EDITION 🛡️       ║
║                                                       ║
║              Explore • Fight • Conquer                ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

1. Start a New Game
2. Load an Existing Game
3. Manage Profiles
4. View Leaderboard
5. View Achievements
6. Quit
```

### Combat
```
==================================================
⚔️  COMBAT INITIATED ⚔️
==================================================
You are fighting a Goblin!
Enemy Level: ~1 | Difficulty: Normal

──────────────────────────────────────────────────
💚 Your Health: 100/100
✨ Effects: Strength (2)
🔴 Goblin Health: 40/40
──────────────────────────────────────────────────

🎯 What will you do?
1. Attack
2. Defend
3. Use Item
4. Run Away
```

### Achievement Unlocked
```
🎉 Victory! You defeated the Goblin!
⭐ You gained 15 experience points!
💰 You earned 8 gold!

🏆 Achievement Unlocked: First Blood
   Win your first battle
   Reward: 25 EXP, 10 gold
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs
1. Check existing issues
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information

### Suggesting Features
1. Open an issue with the "enhancement" label
2. Describe the feature and its benefits
3. Provide examples if possible

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass (`python -m unittest discover tests`)
6. Commit your changes (`git commit -m 'Add AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/adventure-game.git
cd adventure-game

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_game.py
python -m unittest discover tests

# Make changes and test
# ...

# Run tests again
python -m unittest discover tests -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Free to use and modify for educational purposes.

---

## 🙏 Acknowledgments

- Inspired by classic text-based RPGs
- Built with Python and MySQL
- Uses ANSI colors for terminal output
- Comprehensive testing with unittest

---

## 📞 Support

### Getting Help
- 📖 Read the [QUICKSTART.md](QUICKSTART.md) guide
- 📚 Check the [documentation](ENHANCEMENTS_V2.md)
- 🐛 Report bugs via [Issues](https://github.com/Vortex4047/adventure-game-text-based-/issues)
- 💬 Ask questions in [Discussions](https://github.com/Vortex4047/adventure-game-text-based-/discussions)

### Troubleshooting
- **Database Error**: Ensure MySQL is running and credentials are correct
- **Import Error**: Run `pip install -r requirements.txt`
- **Game Crashes**: Check `adventure_game.log` for errors

---

## 🗺️ Roadmap

### Planned Features
- [ ] Magic system with spells
- [ ] Crafting system
- [ ] More locations and enemies
- [ ] Multiplayer support
- [ ] GUI interface
- [ ] Sound effects
- [ ] More achievements
- [ ] Pet/companion system

### In Progress
- [x] Type hints throughout
- [x] Comprehensive testing
- [x] Status effects
- [x] Achievement system
- [x] Random events
- [x] Color output

---

<div align="center">

### ⭐ Star this repository if you found it helpful!

**Made with ❤️ and Python**

[Report Bug](https://github.com/Vortex4047/adventure-game-text-based-/issues) • [Request Feature](https://github.com/Vortex4047/adventure-game-text-based-/issues) • [Documentation](ENHANCEMENTS_V2.md)

</div>

## Features

### ✨ Core Gameplay
- **Multiple Locations**: Village, Forest, Cave, Castle with unique encounters
- **Combat System**: Turn-based combat with attack, defend, and item usage
- **Character Progression**: Level up system with stat increases
- **Quest System**: Complete quests for rewards
- **Inventory Management**: Collect, use, equip, and sell items
- **Shop System**: Buy and sell items with balanced economy

### ⚔️ Combat Features
- Critical hits (15% chance for player, 10% for enemies)
- Dodge mechanics (10% chance)
- Defend action (reduces damage)
- Flee option (success rate based on level)
- Multiple enemy types with varying difficulty
- Boss battles (Forest Guardian, Cave Dragon)

### 🎮 Difficulty Levels
- **Easy**: Weaker enemies, better stat gains
- **Normal**: Balanced gameplay
- **Hard**: Stronger enemies, slower progression

### 📊 Player Management
- Multiple save profiles
- Auto-save every 5 actions
- Leaderboard system
- Detailed statistics tracking

### 🎒 Inventory System
- Equip weapons and armor for stat bonuses
- Use consumables to restore health
- Drop unwanted items
- Unequip items back to inventory

## Installation

1. **Install MySQL** (if not already installed)
   - Download from: https://dev.mysql.com/downloads/

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Database**:
   - Update credentials in `database.py` if needed:
     ```python
     host="localhost"
     user="root"
     password="tiger"  # Change to your MySQL password
     ```

4. **Run the game**:
   ```bash
   python main.py
   ```

## Project Structure

```
adventure_game/
├── main.py              # Main game loop and menu system
├── player.py            # Player class with stats and inventory
├── combat.py            # Combat system with mechanics
├── locations.py         # Location definitions and handlers
├── shop.py              # Shop system for buying/selling
├── database.py          # Database management with connection pooling
├── utils.py             # Utility functions and helpers
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Gameplay Guide

### Starting Out
1. Create a new character or load existing one
2. Choose difficulty level
3. Start in the village

### Combat Tips
- Equip better weapons and armor to increase your stats
- Use health potions during tough battles
- Defend to reduce incoming damage
- Flee if the battle is too difficult

### Earning Gold
- Defeat enemies in combat
- Complete quests
- Hunt animals in the forest
- Mine crystals in the cave
- Sell unwanted items at the shop

### Quests
- **First Combat**: Win your first battle
- **Herb Collector**: Collect 3 healing herbs
- **Treasure Hunter**: Find treasure in the cave
- **Dragon Slayer**: Defeat the cave dragon
- **Forest Explorer**: Explore the deep forest
- **Guardian Challenge**: Defeat the forest guardian

### Locations
- **Village**: Safe zone with shop and inn
- **Forest**: Hunt animals, search for herbs, face the guardian
- **Cave**: Mine crystals, search for treasure, fight the dragon
- **Castle**: Explore library, throne room, and tower

## Improvements Over Original

### Code Quality
- ✅ Modular architecture (split into 7 files)
- ✅ Database connection pooling
- ✅ Comprehensive error handling
- ✅ Input validation throughout
- ✅ Context managers for database operations

### Gameplay
- ✅ Difficulty settings
- ✅ Critical hits and dodge mechanics
- ✅ Defend action in combat
- ✅ Complete quest system integration
- ✅ Item management (unequip, drop)
- ✅ Balanced shop prices
- ✅ Auto-save system
- ✅ Leaderboard

### User Experience
- ✅ Better visual formatting with emojis
- ✅ Confirmation prompts for important actions
- ✅ Detailed item descriptions
- ✅ Quest progress tracking
- ✅ Health bars and status displays
- ✅ Helpful tips system

### Database
- ✅ Fixed equipped items save/load
- ✅ Added difficulty column
- ✅ Separate equipped item storage
- ✅ Connection pooling for performance

## Troubleshooting

### Database Connection Error
- Ensure MySQL is running
- Check credentials in `database.py`
- Verify MySQL port (default: 3306)

### Module Import Error
- Install requirements: `pip install -r requirements.txt`
- Ensure all files are in the same directory

### Game Crashes
- Check console for error messages
- Game auto-saves on errors
- Your progress should be preserved

## Future Enhancements

Potential additions:
- Magic system with spells
- Crafting system
- More locations and enemies
- Multiplayer features
- Save file encryption
- Sound effects
- ASCII art for battles
- Status effects (poison, stun, etc.)

## Credits

Enhanced edition with improved architecture, combat system, and user experience.

## License

Free to use and modify for educational purposes.

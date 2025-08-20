# 🎮 Text-Based Adventure Game

A feature-rich, MySQL-powered text-based adventure game built in Python. Explore mystical locations, engage in tactical combat, complete quests, and build your character in this immersive RPG experience!

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![MySQL](https://img.shields.io/badge/mysql-v8.0+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [How to Play](#-how-to-play)
- [Game Features](#-game-features)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🗡️ **Combat System**
- Turn-based tactical combat
- Multiple enemy types with unique stats
- Strategic options: Attack, Use Items, Flee
- Experience and gold rewards
- Random loot drops

### 🎒 **Inventory & Equipment**
- Comprehensive inventory management
- Weapon and armor equipment system
- Consumable items (health potions, herbs)
- Buy/sell items at the village shop
- Equipment bonuses affect combat stats

### 📊 **Character Progression**
- Level-up system with stat increases
- Experience points and skill development
- Health, attack, and defense progression
- Character statistics tracking

### 🗺️ **Rich World Exploration**
- Multiple interconnected locations
- Dynamic random events
- Hidden treasures and secrets
- Progressive difficulty areas

### 🎯 **Quest System**
- Multiple quests with clear objectives
- Progress tracking and completion rewards
- Expandable quest framework
- Achievement-style goals

### 💾 **Save System**
- MySQL database persistence
- Multiple character profiles
- Auto-save functionality
- Load/save game states

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- MySQL Server 8.0+
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Vortex4047/adventure-game-text-based-.git
cd adventure-game-text-based-
```

### Step 2: Install Python Dependencies
```bash
pip install mysql-connector-python
```

**Alternative (if authentication issues occur):**
```bash
pip install PyMySQL
```

### Step 3: Set Up MySQL
Ensure MySQL server is running on your system. The game will automatically create the required database and tables.

## 🗄️ Database Setup

### Option 1: Default Setup (Recommended)
The game automatically creates the `adventure` database and required tables on first run.

### Option 2: Manual Setup (If needed)
```sql
CREATE DATABASE adventure;
USE adventure;

-- The game will create these tables automatically:
-- - players (character data)
-- - game_items (item definitions)
```

### Authentication Issues Fix
If you encounter authentication errors:

```sql
-- Method 1: Change authentication for existing user
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
FLUSH PRIVILEGES;

-- Method 2: Create new user with native password
CREATE USER 'gameuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'gamepass';
GRANT ALL PRIVILEGES ON *.* TO 'gameuser'@'localhost';
FLUSH PRIVILEGES;
```

## 🎮 How to Play

### Starting the Game
```bash
python adventure_game_enhanced.py
```

### Main Menu Options
1. **Start New Game** - Create a fresh character
2. **Load Game** - Continue with existing character
3. **Manage Profiles** - View/delete saved characters
4. **Quit** - Exit the game

### Game Controls
- Use **numbers** or **type action names**
- Type `check stats` anytime to view character info
- Game auto-saves periodically
- Choose `quit` from any location to save and exit

### Basic Gameplay Loop
1. **Explore** different locations (village, forest, cave, castle)
2. **Combat** enemies to gain experience and gold
3. **Collect** items and equipment
4. **Complete** quests for rewards
5. **Shop** for better gear and supplies
6. **Level up** your character's abilities

## 🎯 Game Features

### 🏘️ **Locations**
- **Village** - Safe hub with shop and inn
- **Forest** - Hunt animals and gather herbs
- **Deep Forest** - Face the Forest Guardian
- **Cave** - Mine crystals and search for treasure
- **Deep Cave** - Challenge the mighty Dragon
- **Castle** - Explore library, throne room, and tower

### ⚔️ **Combat Encounters**
- **Goblin** - Common forest enemy
- **Wolf** - Pack hunters in the wilderness
- **Bandit** - Human adversaries
- **Skeleton Warrior** - Undead castle guardian
- **Forest Guardian** - Mystical forest protector
- **Cave Dragon** - Ultimate boss challenge

### 🛍️ **Items & Equipment**
- **Weapons**: Iron Sword, Steel Blade
- **Armor**: Steel Shield, Dragon Scale Armor
- **Consumables**: Health Potions, Magic Herbs
- **Miscellaneous**: Ancient Keys, Spell Books

### 🎖️ **Quest Examples**
- Win your first battle
- Collect healing herbs
- Defeat the cave dragon
- Explore mysterious locations
- Gather treasure and artifacts

## 🔧 Troubleshooting

### Common Issues

**MySQL Connection Error**
```
Error: Authentication plugin 'caching_sha2_password' is not supported
```
**Solution:**
```bash
pip install --upgrade mysql-connector-python
# OR
pip install PyMySQL
```

**Database Permission Error**
```
Error: Access denied for user 'root'@'localhost'
```
**Solution:** Update MySQL credentials in the code or create a new user with proper permissions.

**Module Import Error**
```
ModuleNotFoundError: No module named 'mysql.connector'
```
**Solution:**
```bash
pip install mysql-connector-python
```

### Configuration

Edit these variables in the code if needed:
```python
# Database configuration
conn = mysql.connector.connect(
    host="localhost",        # Change if MySQL is on different host
    user="root",            # Change username if needed
    password="mypass",      # Update with your MySQL password
    auth_plugin='mysql_native_password'
)
```

## 🎲 Gameplay Tips

1. **Start Safe** - Begin in the village and explore gradually
2. **Manage Resources** - Keep health potions handy for tough fights
3. **Equipment Matters** - Better gear significantly improves combat
4. **Quest Rewards** - Complete quests for substantial experience bonuses
5. **Strategic Combat** - Sometimes running away is the smart choice
6. **Shop Wisely** - Sell unwanted items to fund better equipment
7. **Save Often** - Use the quit option regularly to save progress

## 🔮 Future Enhancements

Planned features for future versions:
- [ ] Magic spells and mana system
- [ ] Crafting and item creation
- [ ] Multiple character classes
- [ ] Multiplayer support
- [ ] Enhanced graphics/ASCII art
- [ ] Story-driven campaign mode
- [ ] Achievement system
- [ ] Random dungeon generation

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add comments for complex game mechanics
- Test new features thoroughly
- Update documentation for new features

## 🙏 Acknowledgments

- Inspired by classic text-based adventure games
- Built with Python and MySQL for learning purposes
- Community feedback and suggestions welcome

## 📞 Contact

- **GitHub**: [@Vortex4047](https://github.com/Vortex4047)
- **Project Link**: [Adventure Game Repository](https://github.com/Vortex4047/adventure-game-text-based-)


**Happy Adventuring!** 🗡️✨

*May your blade stay sharp and your health potions plenty!*

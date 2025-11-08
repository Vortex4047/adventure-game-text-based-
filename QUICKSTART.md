# Quick Start Guide - Adventure Game v2.0

## Installation

### 1. Prerequisites
- Python 3.7 or higher
- MySQL 5.7 or higher

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
Edit `config.py` or set environment variables:

```bash
# Option 1: Environment Variables (Recommended)
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=adventure_game
export DB_PORT=3306

# Option 2: Edit config.py directly
# Change the DATABASE_CONFIG dictionary
```

### 4. Run the Game
```bash
python main.py
```

## First Time Setup

1. **Start MySQL Server**
   ```bash
   # Windows
   net start MySQL80
   
   # Linux/Mac
   sudo systemctl start mysql
   # or
   sudo service mysql start
   ```

2. **Create Database** (Optional - auto-created)
   ```sql
   CREATE DATABASE adventure_game;
   ```

3. **Run Game**
   ```bash
   python main.py
   ```

## Quick Play Guide

### Creating Your Character
1. Select "Start a New Game"
2. Enter your character name
3. Choose difficulty:
   - **Easy**: Weaker enemies, better stat gains
   - **Normal**: Balanced gameplay
   - **Hard**: Stronger enemies, slower progression

### Basic Controls
- Use **numbers** or **type action names**
- Type `check stats` anytime to view your character
- Type `quit` to save and exit

### Combat Tips
- **Attack**: Deal damage to enemy
- **Defend**: Reduce incoming damage by 50%
- **Use Item**: Heal or buff yourself
- **Run Away**: Escape from battle (50% base chance)

### Status Effects
- **Poison** 🧪: Deals 5 damage per turn (cure with Antidote)
- **Stun** 💫: Cannot act for 1 turn
- **Strength** 💪: +30% attack for 3 turns (use Strength Potion)
- **Defense** 🛡️: +30% defense for 3 turns

### Earning Gold
- Defeat enemies in combat
- Complete quests
- Hunt animals in forest
- Mine crystals in cave
- Sell unwanted items at shop

### Achievements
View achievements from main menu to see:
- What you've unlocked
- What's available
- Rewards for each achievement

## Common Commands

### In Village
```
1. Explore Forest
2. Enter Cave
3. Enter Castle
4. Visit Shop
5. Rest (10 gold - restores full health)
6. Check Stats
7. Manage Inventory
8. Quit
```

### In Combat
```
1. Attack
2. Defend
3. Use Item
4. Run Away
```

### In Shop
```
1. Buy Items
2. Sell Items
3. Leave Shop
```

## Useful Items

### Consumables
- **Health Potion** (25g): Restores 50 HP
- **Magic Herb** (15g): Restores 30 HP
- **Antidote** (20g): Cures poison
- **Strength Potion** (40g): +30% attack for 3 turns

### Equipment
- **Iron Sword** (100g): +15 attack
- **Steel Sword** (250g): +25 attack
- **Steel Shield** (80g): +10 defense
- **Iron Armor** (150g): +15 defense

## Quest List

1. **First Combat**: Win your first battle
2. **Herb Collector**: Collect 3 healing herbs
3. **Treasure Hunter**: Find treasure in cave
4. **Dragon Slayer**: Defeat the cave dragon
5. **Forest Explorer**: Explore the deep forest
6. **Guardian Challenge**: Defeat the forest guardian

## Tips & Tricks

### Combat
- Equip better gear before tough fights
- Keep health potions in inventory
- Defend when low on health
- Critical hits deal 50% more damage
- You have 10% chance to dodge attacks

### Economy
- Sell items you don't need
- Buy health potions early
- Save gold for better equipment
- Complete quests for bonus gold

### Progression
- Level up by gaining experience
- Higher level = better stats
- Difficulty affects stat gains
- Complete quests for bonus EXP

### Achievements
- Check achievements menu regularly
- Some achievements give significant rewards
- Track your progress toward goals
- Achievements are saved automatically

## Troubleshooting

### "Database connection failed"
```bash
# Check MySQL is running
sudo systemctl status mysql

# Check credentials in config.py
# Verify password is correct
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.7+
```

### "Permission denied"
```bash
# Check file permissions
chmod +x main.py

# Or run with python explicitly
python main.py
```

### Game crashes
- Check `adventure_game.log` for errors
- Your progress is auto-saved every 5 actions
- Game auto-saves on errors

## Advanced Features

### Running Tests
```bash
# Run all tests
python -m unittest discover tests

# Run specific test
python -m unittest tests.test_player

# Verbose output
python -m unittest discover tests -v
```

### Viewing Logs
```bash
# View recent logs
tail -f adventure_game.log

# Search for errors
grep ERROR adventure_game.log

# View specific player logs
grep "PlayerName" adventure_game.log
```

### Customizing Game Balance
Edit `constants.py`:
```python
# Make combat easier
CRIT_CHANCE_PLAYER = 0.25  # 25% instead of 15%
DODGE_CHANCE = 0.20  # 20% instead of 10%

# Faster leveling
EXP_PER_LEVEL_MULTIPLIER = 50  # 50 instead of 100

# More gold
RANDOM_GOLD_MIN = 10  # 10 instead of 5
RANDOM_GOLD_MAX = 50  # 50 instead of 20
```

### Adding Custom Shop Items
Edit `config.py` SHOP_ITEMS:
```python
{
    "name": "Super Potion",
    "type": "consumable",
    "value": 100,
    "price": 50,
    "description": "Restores 100 health points"
}
```

## Keyboard Shortcuts

- **Ctrl+C**: Interrupt (prompts to save)
- **Enter**: Confirm default choice
- **Numbers**: Quick action selection
- **Text**: Type action names

## Save System

### Auto-Save
- Every 5 actions
- On quit
- On error
- On interrupt (Ctrl+C)

### Manual Save
- Select "Quit" from menu
- Confirm save prompt

### Multiple Profiles
- Create multiple characters
- Switch between profiles
- Delete old profiles
- View all profiles

## Getting Help

### In-Game
- Random tips displayed during play
- Check stats for current status
- View quests for objectives
- Achievements show goals

### Documentation
- `README.md` - Overview
- `ENHANCEMENTS_V2.md` - Detailed features
- `IMPROVEMENTS.md` - Change summary
- `BEFORE_AFTER.md` - Visual comparisons
- `MIGRATION.md` - Upgrade guide

### Logs
- `adventure_game.log` - Detailed game log
- Check for errors and warnings
- Track player actions
- Debug issues

## Performance Tips

### Database
- Use SSD for database storage
- Regular database optimization
- Connection pooling (automatic)

### Game
- Close other applications
- Ensure MySQL has enough memory
- Regular log file cleanup

## Next Steps

1. **Create your character**
2. **Complete first quest** (Win first battle)
3. **Buy equipment** from shop
4. **Explore all locations**
5. **Defeat bosses** (Dragon, Guardian)
6. **Unlock achievements**
7. **Reach level 20** (Master achievement)

## Support

For issues or questions:
1. Check `adventure_game.log`
2. Review documentation
3. Verify MySQL connection
4. Check Python version
5. Ensure dependencies installed

## Have Fun!

Enjoy your adventure! Remember:
- Save often (auto-saves every 5 actions)
- Explore everywhere
- Complete quests for rewards
- Unlock achievements
- Try different difficulties

Good luck, adventurer! 🗡️🛡️

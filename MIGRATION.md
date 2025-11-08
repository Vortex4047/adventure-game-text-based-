# Migration Guide - v1.0 to v2.0

## Overview
This guide helps you migrate from Adventure Game v1.0 to v2.0, whether you're a player or developer.

## For Players

### Your Save Files Are Safe! ✅
All your v1.0 save files will work automatically in v2.0. No action needed!

### What Happens When You Load Old Saves
1. Your character data loads normally
2. New features are initialized:
   - Achievement system (starts empty)
   - Status effects (none active)
   - Tracking stats (start at 0)
3. Your progress is preserved:
   - Level, stats, equipment
   - Inventory and gold
   - Quest completion
   - Current location

### New Features Available
After loading your old save, you can immediately:
- Unlock achievements
- Use status effects (buy potions)
- Track your statistics
- View comprehensive logs

## For Developers

### Breaking Changes
**None!** v2.0 is 100% backward compatible.

### New Dependencies
```bash
# No new external dependencies
# Still just mysql-connector-python
pip install -r requirements.txt
```

### Database Schema Changes
New columns added (auto-created):
```sql
ALTER TABLE players ADD COLUMN achievements TEXT;
ALTER TABLE players ADD COLUMN status_effects TEXT;
ALTER TABLE players ADD COLUMN stats TEXT;
ALTER TABLE players ADD COLUMN save_version VARCHAR(10) DEFAULT '2.0';
```

### Code Migration

#### 1. Import Changes
**Before:**
```python
from player import Player
from combat import start_combat
```

**After:**
```python
from player import Player
from combat import start_combat
from achievements import AchievementManager
from status_effects import StatusEffectManager
from constants import CRIT_CHANCE_PLAYER
from config import DATABASE_CONFIG
```

#### 2. Type Hints
**Before:**
```python
def my_function(player, damage):
    return damage * 2
```

**After:**
```python
def my_function(player: Player, damage: int) -> int:
    return damage * 2
```

#### 3. Logging
**Before:**
```python
print(f"Player dealt {damage} damage")
```

**After:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Player dealt {damage} damage")
print(f"Player dealt {damage} damage")
```

#### 4. Constants
**Before:**
```python
if random.random() < 0.15:  # Magic number
    damage = int(damage * 1.5)
```

**After:**
```python
from constants import CRIT_CHANCE_PLAYER, CRIT_DAMAGE_MULTIPLIER

if random.random() < CRIT_CHANCE_PLAYER:
    damage = int(damage * CRIT_DAMAGE_MULTIPLIER)
```

#### 5. Configuration
**Before:**
```python
db = DatabaseManager(
    host="localhost",
    user="root",
    password="tiger"
)
```

**After:**
```python
# Option 1: Use defaults from config
db = DatabaseManager()

# Option 2: Environment variables
export DB_PASSWORD=secure_password
db = DatabaseManager()

# Option 3: Override specific values
db = DatabaseManager(password="custom_password")
```

### Adding New Features

#### New Achievement
```python
# In achievements.py, add to _initialize_achievements():
{
    "id": "my_achievement",
    "name": "My Achievement",
    "description": "Do something cool",
    "reward_exp": 100,
    "reward_gold": 50
}

# Add check logic in check_achievement():
elif achievement_id == "my_achievement":
    if player.some_condition:
        unlocked = True
```

#### New Status Effect
```python
# In status_effects.py:
class MyEffect(StatusEffect):
    def __init__(self, duration: int = 3):
        super().__init__("MyEffect", duration, "Description")
    
    def apply(self, target: Any) -> None:
        # Your effect logic
        print(f"✨ {target.name} is affected!")
    
    def remove(self, target: Any) -> None:
        # Cleanup logic
        print(f"⏱️  Effect wore off.")
```

#### New Constant
```python
# In constants.py:
MY_NEW_CONSTANT = 42

# Use in code:
from constants import MY_NEW_CONSTANT

if value > MY_NEW_CONSTANT:
    # Do something
```

#### New Shop Item
```python
# In config.py SHOP_ITEMS:
{
    "name": "My Item",
    "type": "consumable",
    "value": 50,
    "price": 25,
    "description": "Does something cool"
}
```

### Testing Your Changes

#### Run Unit Tests
```bash
# All tests
python -m unittest discover tests

# Specific test
python -m unittest tests.test_player

# With verbose output
python -m unittest discover tests -v
```

#### Add New Tests
```python
# In tests/test_my_feature.py:
import unittest
from my_module import MyClass

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        self.obj = MyClass()
    
    def test_something(self):
        result = self.obj.do_something()
        self.assertEqual(result, expected)
```

### Logging Best Practices

```python
import logging
logger = logging.getLogger(__name__)

# Info level - normal operations
logger.info(f"Player {name} performed action")

# Warning level - unexpected but handled
logger.warning(f"Player tried invalid action")

# Error level - errors that need attention
logger.error(f"Database operation failed: {e}")

# Debug level - detailed debugging info
logger.debug(f"Variable value: {value}")
```

### Error Handling Pattern

```python
try:
    # Your operation
    result = risky_operation()
    logger.info("Operation successful")
    return result
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    print(f"❌ User-friendly message")
    return default_value
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    print(f"❌ Something went wrong")
    return None
```

## Migration Checklist

### For Players
- [ ] Backup your save files (optional, but recommended)
- [ ] Install v2.0
- [ ] Load your character
- [ ] Verify your progress is intact
- [ ] Explore new features

### For Developers
- [ ] Update imports for new modules
- [ ] Add type hints to your code
- [ ] Add logging to your functions
- [ ] Replace magic numbers with constants
- [ ] Update configuration usage
- [ ] Add error handling
- [ ] Write unit tests
- [ ] Update documentation
- [ ] Test backward compatibility
- [ ] Run full test suite

## Common Issues

### "Module not found: constants"
```bash
# Ensure constants.py is in same directory
ls constants.py

# Check Python path
python -c "import sys; print(sys.path)"
```

### "Database column not found"
```bash
# Run game once to auto-create columns
python main.py

# Or manually add columns (see Database Schema Changes above)
```

### "Old saves not loading"
```python
# Check utils.py load_player_from_data()
# Should handle both old and new formats
if len(player_data) >= 16:
    # New format
else:
    # Old format - initialize new features
```

### "Tests failing"
```bash
# Ensure test files are in tests/ directory
ls tests/

# Check imports in test files
# Run with verbose output to see which test fails
python -m unittest discover tests -v
```

## Performance Considerations

### Status Effects
- Minimal overhead (O(n) where n = active effects)
- Typically 0-3 effects active
- Cleaned up automatically

### Achievements
- O(1) checks with early returns
- Only checked when relevant
- Cached in memory

### Logging
- Async file writes
- Minimal performance impact
- Can be disabled if needed

### Database
- Connection pooling maintained
- New fields use efficient JSON
- Indexes on player names
- No additional queries

## Rollback Plan

If you need to rollback to v1.0:

### For Players
1. Your v1.0 saves still work in v1.0
2. v2.0 saves work in v1.0 (new fields ignored)
3. No data loss

### For Developers
1. Keep v1.0 code in separate branch
2. v2.0 database works with v1.0 code
3. New columns are ignored by v1.0

## Support

### Documentation
- `README.md` - Overview
- `QUICKSTART.md` - Getting started
- `ENHANCEMENTS_V2.md` - Feature details
- `IMPLEMENTATION_SUMMARY.md` - Technical summary

### Logs
- Check `adventure_game.log` for errors
- Enable DEBUG level for detailed logs
- Search for ERROR or WARNING

### Testing
- Run unit tests to verify functionality
- Check test output for failures
- Add tests for your changes

## Conclusion

Migration from v1.0 to v2.0 is seamless for players and straightforward for developers. The new features enhance the game while maintaining full backward compatibility.

**Key Points:**
- ✅ 100% backward compatible
- ✅ No breaking changes
- ✅ Old saves work automatically
- ✅ Easy to extend
- ✅ Well documented
- ✅ Fully tested

Happy adventuring! 🗡️🛡️

## Migration Guide

## Upgrading from Original Version

If you have save data from the original `adventure_game_enhanced.py`, here's how to migrate:

### Option 1: Automatic Migration (Recommended)

The new version is **backward compatible** with old save files!

1. Keep your old database intact
2. Run the new version: `python main.py`
3. Load your existing character
4. The game will automatically update the database schema

**Note**: The first time you load an old character, you may see:
- Equipped items in inventory (just re-equip them)
- Default difficulty set to "normal"
- Missing quest progress (will start fresh)

### Option 2: Fresh Start

If you want to start completely fresh:

1. **Backup old database** (optional):
   ```sql
   mysqldump -u root -p adventure > adventure_backup.sql
   ```

2. **Drop old database**:
   ```sql
   DROP DATABASE adventure;
   ```

3. **Run new version**:
   ```bash
   python main.py
   ```
   The database will be recreated automatically.

### Option 3: Manual Migration

If you want to preserve all data perfectly:

1. **Add new columns to players table**:
   ```sql
   USE adventure;
   
   ALTER TABLE players 
   ADD COLUMN equipped_weapon TEXT AFTER inventory,
   ADD COLUMN equipped_armor TEXT AFTER equipped_weapon,
   ADD COLUMN difficulty VARCHAR(20) DEFAULT 'normal' AFTER gold;
   ```

2. **Update existing records**:
   ```sql
   UPDATE players SET difficulty = 'normal' WHERE difficulty IS NULL;
   ```

3. **Run new version**:
   ```bash
   python main.py
   ```

## What's Preserved

When migrating, these are preserved:
- ✅ Character name
- ✅ Level and experience
- ✅ Health and stats
- ✅ Gold and score
- ✅ Inventory items
- ✅ Current location

## What's New/Reset

These will be new or reset:
- 🆕 Difficulty (set to "normal")
- 🆕 Equipped items (need to re-equip)
- 🆕 Quest progress (starts fresh)

## Verifying Migration

After migration, check your character:

1. Load your character
2. Type "check stats"
3. Verify:
   - Level and experience are correct
   - Gold amount is correct
   - Inventory items are present
   - Health is correct

If anything is wrong, you can:
- Restore from backup
- Contact support
- Start a new character

## Database Schema Changes

### Old Schema
```sql
CREATE TABLE players(
    id INT PRIMARY KEY AUTO_INCREMENT, 
    name VARCHAR(255) UNIQUE, 
    health INT, 
    max_health INT, 
    attack INT, 
    defense INT,
    level INT, 
    experience INT, 
    score INT,
    current_location VARCHAR(255),
    inventory TEXT,
    quests TEXT,
    gold INT
);
```

### New Schema
```sql
CREATE TABLE players(
    id INT PRIMARY KEY AUTO_INCREMENT, 
    name VARCHAR(255) UNIQUE, 
    health INT, 
    max_health INT, 
    attack INT, 
    defense INT,
    level INT, 
    experience INT, 
    score INT,
    current_location VARCHAR(255),
    inventory TEXT,
    equipped_weapon TEXT,      -- NEW
    equipped_armor TEXT,       -- NEW
    quests TEXT,
    gold INT,
    difficulty VARCHAR(20)     -- NEW
);
```

## Troubleshooting

### "Column 'equipped_weapon' doesn't exist"

Run this SQL:
```sql
ALTER TABLE players 
ADD COLUMN equipped_weapon TEXT AFTER inventory,
ADD COLUMN equipped_armor TEXT AFTER equipped_weapon;
```

### "Column 'difficulty' doesn't exist"

Run this SQL:
```sql
ALTER TABLE players 
ADD COLUMN difficulty VARCHAR(20) DEFAULT 'normal' AFTER gold;
```

### "Can't load old character"

The new version should handle this automatically, but if it fails:

1. Check database connection
2. Verify table structure matches new schema
3. Try loading a different character
4. Check error messages in console

### "Lost equipped items"

Old version didn't save equipped items properly. You'll need to:
1. Check your inventory
2. Re-equip your weapon and armor
3. They should still be there, just not equipped

## Rolling Back

If you need to go back to the old version:

1. **Restore database backup**:
   ```bash
   mysql -u root -p adventure < adventure_backup.sql
   ```

2. **Use old file**:
   ```bash
   python adventure_game_enhanced.py
   ```

## Support

If you encounter issues during migration:

1. Check the error message
2. Verify MySQL is running
3. Check database credentials
4. Review this guide
5. Try a fresh start if needed

## Recommendation

For the best experience:
- **New players**: Start fresh with the new version
- **Existing players with low-level characters**: Start fresh
- **Existing players with high-level characters**: Migrate and re-equip items

The new version offers so many improvements that starting fresh is often the best choice!

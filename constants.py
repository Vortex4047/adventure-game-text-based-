"""
Game constants and configuration values
"""

# Combat Constants
CRIT_CHANCE_PLAYER = 0.15
CRIT_CHANCE_ENEMY = 0.10
DODGE_CHANCE = 0.10
CRIT_DAMAGE_MULTIPLIER = 1.5
DEFEND_DAMAGE_REDUCTION = 0.5
BASE_FLEE_CHANCE = 0.5
FLEE_LEVEL_BONUS = 0.02
MAX_FLEE_CHANCE = 0.8

# Difficulty Multipliers
DIFFICULTY_MULTIPLIERS = {
    "easy": {"enemy": 0.7, "player": 1.2},
    "normal": {"enemy": 1.0, "player": 1.0},
    "hard": {"enemy": 1.3, "player": 0.8}
}

# Level Up Constants
LEVEL_UP_HEALTH_BONUS = 20
LEVEL_UP_ATTACK_BONUS = 3
LEVEL_UP_DEFENSE_BONUS = 2
EXP_PER_LEVEL_MULTIPLIER = 100

# Player Starting Stats
STARTING_HEALTH = 100
STARTING_ATTACK = 20
STARTING_DEFENSE = 5
STARTING_GOLD = 50
STARTING_LEVEL = 1

# Game Settings
AUTO_SAVE_INTERVAL = 5
LOOT_DROP_CHANCE = 0.5
RANDOM_GOLD_MIN = 5
RANDOM_GOLD_MAX = 20

# Shop Settings
SELL_PRICE_MULTIPLIER = 0.5

# Defeat Penalties
DEFEAT_HEALTH_RESTORE = 0.25  # 25% of max health
DEFEAT_GOLD_PENALTY = 0.10    # 10% gold loss

# Status Effect Durations
POISON_DURATION = 3
POISON_DAMAGE = 5
STUN_DURATION = 1
BUFF_DURATION = 3
BUFF_MULTIPLIER = 1.3

# Save File Version
SAVE_FILE_VERSION = "2.0"

# Database Settings
DB_POOL_SIZE = 5
DB_POOL_NAME = "adventure_game_pool"

# UI Constants
SEPARATOR_LENGTH = 50
LEADERBOARD_MAX_ENTRIES = 10

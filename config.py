"""
Configuration file for database and game settings
"""
import os
from typing import Dict, Any

# Database Configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "tiger"),
    "database": os.getenv("DB_NAME", "adventure_game"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "pool_size": 5,
    "pool_name": "adventure_game_pool"
}

# Game Balance Configuration
GAME_BALANCE: Dict[str, Any] = {
    "combat": {
        "crit_chance_player": 0.15,
        "crit_chance_enemy": 0.10,
        "dodge_chance": 0.10,
        "crit_multiplier": 1.5,
        "defend_reduction": 0.5
    },
    "progression": {
        "exp_per_level": 100,
        "health_per_level": 20,
        "attack_per_level": 3,
        "defense_per_level": 2
    },
    "economy": {
        "sell_multiplier": 0.5,
        "defeat_gold_penalty": 0.10
    }
}

# Shop Items Configuration
SHOP_ITEMS = [
    {
        "name": "Health Potion",
        "type": "consumable",
        "value": 50,
        "price": 25,
        "description": "Restores 50 health points"
    },
    {
        "name": "Magic Herb",
        "type": "consumable",
        "value": 30,
        "price": 15,
        "description": "A mystical herb. Restores 30 health"
    },
    {
        "name": "Iron Sword",
        "type": "weapon",
        "value": 15,
        "price": 100,
        "description": "A sturdy iron sword. +15 attack"
    },
    {
        "name": "Steel Sword",
        "type": "weapon",
        "value": 25,
        "price": 250,
        "description": "A sharp steel sword. +25 attack"
    },
    {
        "name": "Steel Shield",
        "type": "armor",
        "value": 10,
        "price": 80,
        "description": "A reliable steel shield. +10 defense"
    },
    {
        "name": "Iron Armor",
        "type": "armor",
        "value": 15,
        "price": 150,
        "description": "Sturdy iron armor. +15 defense"
    },
    {
        "name": "Antidote",
        "type": "consumable",
        "value": 0,
        "price": 20,
        "description": "Cures poison status effect"
    },
    {
        "name": "Strength Potion",
        "type": "consumable",
        "value": 0,
        "price": 40,
        "description": "Increases attack by 30% for 3 turns"
    }
]

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "adventure_game.log",
            "formatter": "standard",
            "level": "INFO"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "WARNING"
        }
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO"
    }
}

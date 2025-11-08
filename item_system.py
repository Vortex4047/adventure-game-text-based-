"""
Enhanced item system with rarity and special effects
"""
import random
import logging
from typing import Dict, Any, Optional
from colors import rarity_color, colored, Colors

logger = logging.getLogger(__name__)


class ItemRarity:
    """Item rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    
    @staticmethod
    def get_multiplier(rarity: str) -> float:
        """Get stat multiplier for rarity"""
        multipliers = {
            "common": 1.0,
            "uncommon": 1.2,
            "rare": 1.5,
            "epic": 2.0,
            "legendary": 3.0
        }
        return multipliers.get(rarity, 1.0)
    
    @staticmethod
    def get_color(rarity: str) -> str:
        """Get color for rarity"""
        return rarity_color(rarity)


class EnhancedItem:
    """Enhanced item with rarity and special effects"""
    
    def __init__(self, name: str, item_type: str, value: int, 
                 description: str, rarity: str = "common", 
                 special_effect: Optional[str] = None):
        self.name = name
        self.type = item_type
        self.base_value = value
        self.description = description
        self.rarity = rarity
        self.special_effect = special_effect
        
        # Apply rarity multiplier
        multiplier = ItemRarity.get_multiplier(rarity)
        self.value = int(value * multiplier)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "description": self.description,
            "rarity": self.rarity,
            "special_effect": self.special_effect
        }
    
    def display_name(self) -> str:
        """Get colored display name"""
        color = ItemRarity.get_color(self.rarity)
        return colored(self.name, color)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'EnhancedItem':
        """Create from dictionary"""
        return EnhancedItem(
            name=data.get("name", "Unknown"),
            item_type=data.get("type", "misc"),
            value=data.get("value", 0),
            description=data.get("description", ""),
            rarity=data.get("rarity", "common"),
            special_effect=data.get("special_effect")
        )


class ItemGenerator:
    """Generate random items with rarity"""
    
    @staticmethod
    def generate_weapon(level: int) -> EnhancedItem:
        """Generate a random weapon based on level"""
        # Determine rarity based on level
        rarity = ItemGenerator._determine_rarity(level)
        
        # Base weapons
        weapons = {
            "common": [
                ("Rusty Sword", 10, "An old, rusty sword"),
                ("Wooden Club", 8, "A simple wooden club"),
                ("Dagger", 12, "A basic dagger"),
            ],
            "uncommon": [
                ("Iron Sword", 15, "A sturdy iron sword"),
                ("Battle Axe", 18, "A heavy battle axe"),
                ("Spear", 16, "A sharp spear"),
            ],
            "rare": [
                ("Steel Sword", 25, "A sharp steel sword"),
                ("War Hammer", 28, "A powerful war hammer"),
                ("Enchanted Blade", 30, "A blade with magical properties"),
            ],
            "epic": [
                ("Dragon Slayer", 40, "A legendary dragon-slaying sword"),
                ("Thunder Axe", 42, "An axe that crackles with lightning"),
                ("Shadow Dagger", 38, "A dagger that strikes from shadows"),
            ],
            "legendary": [
                ("Excalibur", 60, "The legendary sword of kings"),
                ("Mjolnir", 65, "The hammer of thunder gods"),
                ("Gungnir", 62, "The spear that never misses"),
            ]
        }
        
        weapon_data = random.choice(weapons.get(rarity, weapons["common"]))
        name, base_value, description = weapon_data
        
        # Add special effects for rare+ items
        special_effect = None
        if rarity in ["rare", "epic", "legendary"]:
            effects = ["lifesteal", "critical_boost", "armor_pierce"]
            special_effect = random.choice(effects)
        
        return EnhancedItem(name, "weapon", base_value, description, rarity, special_effect)
    
    @staticmethod
    def generate_armor(level: int) -> EnhancedItem:
        """Generate random armor based on level"""
        rarity = ItemGenerator._determine_rarity(level)
        
        armors = {
            "common": [
                ("Leather Vest", 5, "Basic leather protection"),
                ("Cloth Armor", 4, "Simple cloth armor"),
            ],
            "uncommon": [
                ("Chainmail", 10, "Interlocking metal rings"),
                ("Steel Shield", 12, "A reliable steel shield"),
            ],
            "rare": [
                ("Plate Armor", 20, "Heavy plate armor"),
                ("Enchanted Shield", 22, "A magically enhanced shield"),
            ],
            "epic": [
                ("Dragon Scale Armor", 35, "Armor made from dragon scales"),
                ("Aegis Shield", 38, "A shield blessed by gods"),
            ],
            "legendary": [
                ("Invincible Armor", 55, "Armor that makes you nearly invincible"),
                ("Mirror Shield", 58, "A shield that reflects magic"),
            ]
        }
        
        armor_data = random.choice(armors.get(rarity, armors["common"]))
        name, base_value, description = armor_data
        
        special_effect = None
        if rarity in ["rare", "epic", "legendary"]:
            effects = ["damage_reduction", "health_boost", "regen"]
            special_effect = random.choice(effects)
        
        return EnhancedItem(name, "armor", base_value, description, rarity, special_effect)
    
    @staticmethod
    def _determine_rarity(level: int) -> str:
        """Determine item rarity based on level"""
        roll = random.random()
        
        # Adjust chances based on level
        level_bonus = min(level * 0.02, 0.3)  # Max 30% bonus
        
        if roll < 0.50 - level_bonus:
            return "common"
        elif roll < 0.75 - level_bonus / 2:
            return "uncommon"
        elif roll < 0.90:
            return "rare"
        elif roll < 0.98:
            return "epic"
        else:
            return "legendary"
    
    @staticmethod
    def generate_loot(level: int) -> Optional[EnhancedItem]:
        """Generate random loot drop"""
        roll = random.random()
        
        if roll < 0.4:
            return ItemGenerator.generate_weapon(level)
        elif roll < 0.7:
            return ItemGenerator.generate_armor(level)
        else:
            # Consumable
            consumables = [
                ("Health Potion", "consumable", 50, "Restores 50 health points"),
                ("Magic Herb", "consumable", 30, "Restores 30 health"),
                ("Strength Elixir", "consumable", 0, "Temporarily increases attack"),
            ]
            name, item_type, value, desc = random.choice(consumables)
            return EnhancedItem(name, item_type, value, desc, "common")


def display_item_with_rarity(item: Dict[str, Any]) -> str:
    """Display item with colored rarity"""
    rarity = item.get("rarity", "common")
    color = ItemRarity.get_color(rarity)
    name = item.get("name", "Unknown")
    
    return colored(name, color)

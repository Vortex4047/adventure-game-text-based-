import json
import logging
from typing import Dict, Any, Optional, List
from constants import (
    STARTING_HEALTH, STARTING_ATTACK, STARTING_DEFENSE,
    STARTING_GOLD, STARTING_LEVEL, LEVEL_UP_HEALTH_BONUS,
    LEVEL_UP_ATTACK_BONUS, LEVEL_UP_DEFENSE_BONUS,
    EXP_PER_LEVEL_MULTIPLIER, SAVE_FILE_VERSION
)
from status_effects import StatusEffectManager

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, name: str, health: int = STARTING_HEALTH, 
                 max_health: int = STARTING_HEALTH, attack: int = STARTING_ATTACK, 
                 defense: int = STARTING_DEFENSE, level: int = STARTING_LEVEL, 
                 experience: int = 0, score: int = 0, gold: int = STARTING_GOLD, 
                 difficulty: str = "normal"):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.base_attack = attack
        self.base_defense = defense
        self.level = level
        self.experience = experience
        self.score = score
        self.gold = gold
        self.inventory: List[Dict[str, Any]] = []
        self.equipped_weapon: Optional[Dict[str, Any]] = None
        self.equipped_armor: Optional[Dict[str, Any]] = None
        self.quests = self._initialize_quests()
        self.current_location = "village"
        self.difficulty = difficulty
        self.status_effect_manager = StatusEffectManager()
        
        # Achievement tracking
        self.enemies_defeated = 0
        self.items_purchased = 0
        self.battles_won_flawless = 0
        self.locations_visited: set = {"village"}
        
        logger.info(f"Player '{name}' created with difficulty '{difficulty}'")

    def _initialize_quests(self) -> Dict[str, Any]:
        """Initialize default quests"""
        return {
            "first_combat": {
                "description": "Win your first battle", 
                "completed": False, 
                "reward_exp": 50,
                "reward_gold": 20
            },
            "herb_collector": {
                "description": "Collect 3 healing herbs", 
                "progress": 0, 
                "target": 3, 
                "completed": False, 
                "reward_exp": 30,
                "reward_gold": 15
            },
            "treasure_hunter": {
                "description": "Find treasure in the cave", 
                "completed": False, 
                "reward_exp": 75,
                "reward_gold": 30
            },
            "dragon_slayer": {
                "description": "Defeat the cave dragon", 
                "completed": False, 
                "reward_exp": 200,
                "reward_gold": 100
            },
            "forest_explorer": {
                "description": "Explore the deep forest", 
                "completed": False, 
                "reward_exp": 40,
                "reward_gold": 25
            },
            "guardian_challenge": {
                "description": "Defeat the forest guardian",
                "completed": False,
                "reward_exp": 150,
                "reward_gold": 75
            }
        }

    @property
    def attack(self) -> int:
        """Calculate total attack with equipment bonus"""
        bonus = 0
        if self.equipped_weapon:
            bonus = self.equipped_weapon.get("value", 0)
        return self.base_attack + bonus

    @property
    def defense(self) -> int:
        """Calculate total defense with equipment bonus"""
        bonus = 0
        if self.equipped_armor:
            bonus = self.equipped_armor.get("value", 0)
        return self.base_defense + bonus

    def add_item(self, item: Dict[str, Any]) -> None:
        """Add item to inventory"""
        self.inventory.append(item)
        print(f"✨ You obtained: {item['name']}")
        logger.info(f"{self.name} obtained {item['name']}")

    def remove_item(self, item_name: str) -> bool:
        """Remove item from inventory"""
        for item in self.inventory:
            if item["name"].lower() == item_name.lower():
                self.inventory.remove(item)
                logger.info(f"{self.name} removed {item_name}")
                return True
        return False

    def use_item(self, item_name: str) -> bool:
        """Use a consumable item"""
        for item in self.inventory:
            if item["name"].lower() == item_name.lower():
                if item["type"] == "consumable":
                    # Health restoration items
                    if "Health" in item["name"] or "Herb" in item["name"]:
                        heal_amount = item["value"]
                        old_health = self.health
                        self.health = min(self.max_health, self.health + heal_amount)
                        actual_heal = self.health - old_health
                        print(f"💚 You used {item['name']} and restored {actual_heal} health!")
                        self.inventory.remove(item)
                        logger.info(f"{self.name} used {item_name} and healed {actual_heal} HP")
                        return True
                    # Antidote
                    elif "Antidote" in item["name"]:
                        if self.status_effect_manager.remove_effect_by_name("Poison", self):
                            print(f"💊 You used {item['name']} and cured poison!")
                            self.inventory.remove(item)
                            logger.info(f"{self.name} cured poison")
                            return True
                        else:
                            print("❌ You are not poisoned!")
                            return False
                    # Strength Potion
                    elif "Strength" in item["name"]:
                        from status_effects import StrengthBuffEffect
                        buff = StrengthBuffEffect()
                        self.status_effect_manager.add_effect(buff, self)
                        buff.apply(self)
                        self.inventory.remove(item)
                        logger.info(f"{self.name} used strength potion")
                        return True
                    else:
                        print(f"You used {item['name']}!")
                        self.inventory.remove(item)
                        logger.info(f"{self.name} used {item_name}")
                        return True
                else:
                    print(f"❌ {item['name']} is not a consumable item.")
                    return False
        print(f"❌ You don't have {item_name}.")
        return False

    def equip_item(self, item_name: str) -> bool:
        """Equip a weapon or armor"""
        for item in self.inventory:
            if item["name"].lower() == item_name.lower():
                if item["type"] == "weapon":
                    if self.equipped_weapon:
                        self.inventory.append(self.equipped_weapon)
                        print(f"Unequipped {self.equipped_weapon['name']}")
                    self.equipped_weapon = item
                    self.inventory.remove(item)
                    print(f"⚔️  Equipped {item['name']}! (+{item['value']} attack)")
                    logger.info(f"{self.name} equipped {item_name}")
                    return True
                elif item["type"] == "armor":
                    if self.equipped_armor:
                        self.inventory.append(self.equipped_armor)
                        print(f"Unequipped {self.equipped_armor['name']}")
                    self.equipped_armor = item
                    self.inventory.remove(item)
                    print(f"🛡️  Equipped {item['name']}! (+{item['value']} defense)")
                    logger.info(f"{self.name} equipped {item_name}")
                    return True
                else:
                    print(f"❌ {item['name']} cannot be equipped.")
                    return False
        print(f"❌ You don't have {item_name}.")
        return False

    def unequip_item(self, slot: str) -> bool:
        """Unequip weapon or armor"""
        if slot.lower() == "weapon":
            if self.equipped_weapon:
                self.inventory.append(self.equipped_weapon)
                print(f"Unequipped {self.equipped_weapon['name']}")
                logger.info(f"{self.name} unequipped weapon")
                self.equipped_weapon = None
                return True
            else:
                print("❌ No weapon equipped.")
                return False
        elif slot.lower() == "armor":
            if self.equipped_armor:
                self.inventory.append(self.equipped_armor)
                print(f"Unequipped {self.equipped_armor['name']}")
                logger.info(f"{self.name} unequipped armor")
                self.equipped_armor = None
                return True
            else:
                print("❌ No armor equipped.")
                return False
        else:
            print("❌ Invalid slot. Use 'weapon' or 'armor'.")
            return False

    def drop_item(self, item_name: str) -> bool:
        """Drop an item from inventory"""
        if self.remove_item(item_name):
            print(f"🗑️  Dropped {item_name}")
            return True
        print(f"❌ You don't have {item_name}.")
        return False

    def gain_experience(self, exp: int) -> None:
        """Gain experience points and check for level up"""
        self.experience += exp
        print(f"⭐ You gained {exp} experience points!")
        logger.info(f"{self.name} gained {exp} EXP")
        
        exp_needed = self.level * EXP_PER_LEVEL_MULTIPLIER
        if self.experience >= exp_needed:
            self.level_up()

    def level_up(self) -> None:
        """Level up the player"""
        self.level += 1
        
        # Difficulty modifiers
        from constants import DIFFICULTY_MULTIPLIERS
        multiplier = DIFFICULTY_MULTIPLIERS.get(self.difficulty, {}).get("player", 1.0)
        
        health_bonus = int(LEVEL_UP_HEALTH_BONUS * multiplier)
        attack_bonus = int(LEVEL_UP_ATTACK_BONUS * multiplier)
        defense_bonus = int(LEVEL_UP_DEFENSE_BONUS * multiplier)
        
        self.max_health += health_bonus
        self.health = self.max_health
        self.base_attack += attack_bonus
        self.base_defense += defense_bonus
        
        print(f"\n🎉 LEVEL UP! You are now level {self.level}!")
        print(f"💚 Health increased by {health_bonus} (now {self.max_health})")
        print(f"⚔️  Attack increased by {attack_bonus} (now {self.base_attack})")
        print(f"🛡️  Defense increased by {defense_bonus} (now {self.base_defense})")
        logger.info(f"{self.name} leveled up to {self.level}")

    def check_quest_completion(self, quest_type: str, **kwargs) -> None:
        """Check and complete quests"""
        if quest_type == "combat" and not self.quests["first_combat"]["completed"]:
            self.quests["first_combat"]["completed"] = True
            quest = self.quests["first_combat"]
            self.gain_experience(quest["reward_exp"])
            self.gold += quest["reward_gold"]
            print(f"🏆 Quest completed: {quest['description']}!")
            print(f"💰 Reward: {quest['reward_gold']} gold")
            
        elif quest_type == "herb" and not self.quests["herb_collector"]["completed"]:
            self.quests["herb_collector"]["progress"] += 1
            progress = self.quests["herb_collector"]["progress"]
            target = self.quests["herb_collector"]["target"]
            print(f"📋 Quest progress: Herb Collector ({progress}/{target})")
            
            if progress >= target:
                self.quests["herb_collector"]["completed"] = True
                quest = self.quests["herb_collector"]
                self.gain_experience(quest["reward_exp"])
                self.gold += quest["reward_gold"]
                print(f"🏆 Quest completed: {quest['description']}!")
                print(f"💰 Reward: {quest['reward_gold']} gold")
                
        elif quest_type == "treasure" and not self.quests["treasure_hunter"]["completed"]:
            self.quests["treasure_hunter"]["completed"] = True
            quest = self.quests["treasure_hunter"]
            self.gain_experience(quest["reward_exp"])
            self.gold += quest["reward_gold"]
            print(f"🏆 Quest completed: {quest['description']}!")
            print(f"💰 Reward: {quest['reward_gold']} gold")
            
        elif quest_type == "dragon" and not self.quests["dragon_slayer"]["completed"]:
            self.quests["dragon_slayer"]["completed"] = True
            quest = self.quests["dragon_slayer"]
            self.gain_experience(quest["reward_exp"])
            self.gold += quest["reward_gold"]
            print(f"🏆 Quest completed: {quest['description']}!")
            print(f"💰 Reward: {quest['reward_gold']} gold")
            
        elif quest_type == "forest_exploration" and not self.quests["forest_explorer"]["completed"]:
            self.quests["forest_explorer"]["completed"] = True
            quest = self.quests["forest_explorer"]
            self.gain_experience(quest["reward_exp"])
            self.gold += quest["reward_gold"]
            print(f"🏆 Quest completed: {quest['description']}!")
            print(f"💰 Reward: {quest['reward_gold']} gold")
            
        elif quest_type == "guardian" and not self.quests["guardian_challenge"]["completed"]:
            self.quests["guardian_challenge"]["completed"] = True
            quest = self.quests["guardian_challenge"]
            self.gain_experience(quest["reward_exp"])
            self.gold += quest["reward_gold"]
            print(f"🏆 Quest completed: {quest['description']}!")
            print(f"💰 Reward: {quest['reward_gold']} gold")

    def show_stats(self) -> None:
        """Display player statistics"""
        from constants import SEPARATOR_LENGTH, EXP_PER_LEVEL_MULTIPLIER
        
        print(f"\n{'='*SEPARATOR_LENGTH}")
        print(f"📊 {self.name}'s Statistics")
        print(f"{'='*SEPARATOR_LENGTH}")
        print(f"⚡ Level: {self.level} | Difficulty: {self.difficulty.title()}")
        print(f"💚 Health: {self.health}/{self.max_health}")
        print(f"⚔️  Attack: {self.attack}", end="")
        if self.equipped_weapon:
            print(f" (Base: {self.base_attack} + {self.equipped_weapon['value']})")
        else:
            print()
        print(f"🛡️  Defense: {self.defense}", end="")
        if self.equipped_armor:
            print(f" (Base: {self.base_defense} + {self.equipped_armor['value']})")
        else:
            print()
        print(f"⭐ Experience: {self.experience}/{self.level * EXP_PER_LEVEL_MULTIPLIER}")
        print(f"💰 Gold: {self.gold}")
        print(f"🏆 Score: {self.score}")
        print(f"⚔️  Enemies Defeated: {self.enemies_defeated}")
        
        # Show active status effects
        if self.status_effect_manager.effects:
            print(f"\n✨ Active Effects:")
            for effect_name in self.status_effect_manager.get_active_effects():
                print(f"  • {effect_name}")
        
        print(f"\n🎒 Equipment:")
        if self.equipped_weapon:
            print(f"  ⚔️  Weapon: {self.equipped_weapon['name']}")
        else:
            print(f"  ⚔️  Weapon: None")
        if self.equipped_armor:
            print(f"  🛡️  Armor: {self.equipped_armor['name']}")
        else:
            print(f"  🛡️  Armor: None")
            
        print(f"\n🎒 Inventory ({len(self.inventory)} items):")
        if self.inventory:
            for item in self.inventory:
                print(f"  • {item['name']} ({item['type']})")
        else:
            print("  (empty)")
            
        print(f"\n📋 Quests:")
        for quest_name, quest_data in self.quests.items():
            status = "✅" if quest_data["completed"] else "⏳"
            if "progress" in quest_data:
                progress_str = f" ({quest_data['progress']}/{quest_data['target']})"
            else:
                progress_str = ""
            print(f"  {status} {quest_data['description']}{progress_str}")
        print(f"{'='*SEPARATOR_LENGTH}\n")

    def show_inventory(self) -> None:
        """Display inventory in detail"""
        from constants import SEPARATOR_LENGTH
        
        print(f"\n{'='*SEPARATOR_LENGTH}")
        print(f"🎒 {self.name}'s Inventory")
        print(f"{'='*SEPARATOR_LENGTH}")
        
        if self.equipped_weapon:
            print(f"⚔️  Equipped Weapon: {self.equipped_weapon['name']} (+{self.equipped_weapon['value']} attack)")
        if self.equipped_armor:
            print(f"🛡️  Equipped Armor: {self.equipped_armor['name']} (+{self.equipped_armor['value']} defense)")
        
        if self.inventory:
            print(f"\n📦 Items ({len(self.inventory)}):")
            for i, item in enumerate(self.inventory, 1):
                desc = item.get('description', 'No description')
                print(f"  {i}. {item['name']} ({item['type']}) - {desc}")
        else:
            print("\n📦 No items in inventory")
        print(f"{'='*SEPARATOR_LENGTH}\n")

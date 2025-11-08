import random
import logging
from typing import Dict, Any, Tuple, Optional
from constants import (
    CRIT_CHANCE_PLAYER, CRIT_CHANCE_ENEMY, DODGE_CHANCE,
    CRIT_DAMAGE_MULTIPLIER, DEFEND_DAMAGE_REDUCTION,
    BASE_FLEE_CHANCE, FLEE_LEVEL_BONUS, MAX_FLEE_CHANCE,
    LOOT_DROP_CHANCE, RANDOM_GOLD_MIN, RANDOM_GOLD_MAX,
    DEFEAT_HEALTH_RESTORE, DEFEAT_GOLD_PENALTY,
    DIFFICULTY_MULTIPLIERS
)
from status_effects import PoisonEffect

logger = logging.getLogger(__name__)


class CombatSystem:
    def __init__(self, player: Any, enemy_data: Dict[str, Any], difficulty: str = "normal"):
        self.player = player
        self.enemy = enemy_data.copy()
        self.difficulty = difficulty
        self.turn_count = 0
        self.player_damage_taken = 0
        
        # Apply difficulty modifiers to enemy
        mult = DIFFICULTY_MULTIPLIERS.get(difficulty, {}).get("enemy", 1.0)
        self.enemy["health"] = int(self.enemy["health"] * mult)
        self.enemy["max_health"] = self.enemy["health"]
        self.enemy["attack"] = int(self.enemy["attack"] * mult)
        self.enemy["defense"] = int(self.enemy["defense"] * mult)
        
        logger.info(f"Combat started: {player.name} vs {enemy_data['name']} (difficulty: {difficulty})")

    def calculate_damage(self, attacker_attack: int, defender_defense: int, 
                        is_player: bool = True) -> Tuple[int, bool]:
        """Calculate damage with variance and critical hits"""
        base_damage = max(1, attacker_attack - defender_defense)
        variance = random.randint(-2, 3)
        damage = base_damage + variance
        
        # Critical hit chance
        crit_chance = CRIT_CHANCE_PLAYER if is_player else CRIT_CHANCE_ENEMY
        is_critical = random.random() < crit_chance
        
        if is_critical:
            damage = int(damage * CRIT_DAMAGE_MULTIPLIER)
            logger.debug(f"Critical hit! Damage: {damage}")
            return damage, True
        
        return max(1, damage), False

    def player_attack(self) -> bool:
        """Player attacks enemy"""
        damage, is_crit = self.calculate_damage(self.player.attack, self.enemy["defense"], True)
        self.enemy["health"] -= damage
        
        if is_crit:
            print(f"💥 CRITICAL HIT! You deal {damage} damage to the {self.enemy['name']}!")
        else:
            print(f"⚔️  You deal {damage} damage to the {self.enemy['name']}!")
        
        logger.info(f"{self.player.name} dealt {damage} damage (crit: {is_crit})")
        
        # Small chance to poison enemy (5%)
        if random.random() < 0.05 and hasattr(self.enemy, 'status_effect_manager'):
            print(f"🧪 The {self.enemy['name']} is poisoned!")
        
        return self.enemy["health"] <= 0

    def enemy_attack(self) -> bool:
        """Enemy attacks player"""
        # Check if player can dodge
        if random.random() < DODGE_CHANCE:
            print(f"💨 You dodged the {self.enemy['name']}'s attack!")
            logger.info(f"{self.player.name} dodged attack")
            return False
        
        damage, is_crit = self.calculate_damage(self.enemy["attack"], self.player.defense, False)
        self.player.health -= damage
        self.player_damage_taken += damage
        
        if is_crit:
            print(f"💢 CRITICAL HIT! The {self.enemy['name']} deals {damage} damage to you!")
        else:
            print(f"🗡️  The {self.enemy['name']} deals {damage} damage to you!")
        
        logger.info(f"{self.enemy['name']} dealt {damage} damage to {self.player.name} (crit: {is_crit})")
        
        return self.player.health <= 0

    def player_defend(self) -> bool:
        """Player defends, reducing next attack damage"""
        print(f"🛡️  You brace yourself for the next attack!")
        
        # Enemy attacks with reduced damage
        if random.random() < DODGE_CHANCE:
            print(f"💨 You dodged the {self.enemy['name']}'s attack!")
            logger.info(f"{self.player.name} dodged while defending")
            return False
        
        damage = max(1, int((self.enemy["attack"] - self.player.defense) * DEFEND_DAMAGE_REDUCTION))
        self.player.health -= damage
        self.player_damage_taken += damage
        print(f"🗡️  The {self.enemy['name']} deals {damage} damage (reduced by defense)!")
        
        logger.info(f"{self.player.name} defended, took {damage} damage")
        
        return self.player.health <= 0

    def attempt_flee(self) -> bool:
        """Attempt to flee from combat"""
        # Flee chance based on player level
        level_bonus = self.player.level * FLEE_LEVEL_BONUS
        flee_chance = min(MAX_FLEE_CHANCE, BASE_FLEE_CHANCE + level_bonus)
        
        if random.random() < flee_chance:
            print("💨 You successfully escaped!")
            logger.info(f"{self.player.name} fled from combat")
            return True
        else:
            print("❌ You couldn't escape!")
            logger.info(f"{self.player.name} failed to flee")
            # Enemy gets a free attack
            self.enemy_attack()
            return False

    def use_item_in_combat(self, item_name: str) -> bool:
        """Use an item during combat"""
        return self.player.use_item(item_name)

    def display_combat_status(self) -> None:
        """Display current combat status"""
        from constants import SEPARATOR_LENGTH
        
        print(f"\n{'─'*SEPARATOR_LENGTH}")
        print(f"💚 Your Health: {self.player.health}/{self.player.max_health}")
        
        # Show active status effects
        if self.player.status_effect_manager.effects:
            effects = ", ".join(self.player.status_effect_manager.get_active_effects())
            print(f"✨ Effects: {effects}")
        
        print(f"🔴 {self.enemy['name']} Health: {self.enemy['health']}/{self.enemy['max_health']}")
        print(f"{'─'*SEPARATOR_LENGTH}")

    def victory(self) -> bool:
        """Handle combat victory"""
        print(f"\n🎉 Victory! You defeated the {self.enemy['name']}!")
        
        # Award experience and gold
        exp_reward = self.enemy["exp_reward"]
        gold_reward = self.enemy["gold_reward"]
        
        self.player.gain_experience(exp_reward)
        self.player.gold += gold_reward
        self.player.score += exp_reward
        self.player.enemies_defeated += 1
        print(f"💰 You earned {gold_reward} gold!")
        
        # Check for flawless victory achievement
        if self.player_damage_taken == 0:
            self.player.battles_won_flawless += 1
            print("✨ Flawless Victory! You took no damage!")
            logger.info(f"{self.player.name} won flawlessly")
        
        # Random loot drop
        if random.random() < LOOT_DROP_CHANCE:
            self.drop_loot()
        
        logger.info(f"{self.player.name} defeated {self.enemy['name']}")
        
        return True

    def drop_loot(self) -> None:
        """Drop random loot after combat"""
        loot_table = [
            {"name": "Health Potion", "type": "consumable", "value": 50, "description": "Restores 50 health points"},
            {"name": "Magic Herb", "type": "consumable", "value": 30, "description": "A mystical herb. Restores 30 health"},
        ]
        
        # Add gold coins with random amount
        gold_amount = random.randint(RANDOM_GOLD_MIN, RANDOM_GOLD_MAX)
        
        if random.choice([True, False]):
            loot = random.choice(loot_table)
            self.player.add_item(loot)
            logger.info(f"{self.player.name} received loot: {loot['name']}")
        else:
            self.player.gold += gold_amount
            print(f"✨ You found {gold_amount} gold coins!")
            logger.info(f"{self.player.name} received {gold_amount} gold")

    def defeat(self) -> bool:
        """Handle player defeat"""
        print("\n💀 You have been defeated!")
        self.player.health = max(1, int(self.player.max_health * DEFEAT_HEALTH_RESTORE))
        print(f"You wake up back in the village with {self.player.health} health.")
        self.player.current_location = "village"
        
        # Lose some gold
        gold_lost = int(self.player.gold * DEFEAT_GOLD_PENALTY)
        self.player.gold -= gold_lost
        if gold_lost > 0:
            print(f"💸 You lost {gold_lost} gold.")
        
        # Clear status effects
        self.player.status_effect_manager.clear_all(self.player)
        
        logger.info(f"{self.player.name} was defeated by {self.enemy['name']}")
        
        return False

    def run_combat(self) -> bool:
        """Main combat loop"""
        from constants import SEPARATOR_LENGTH
        
        print(f"\n{'='*SEPARATOR_LENGTH}")
        print(f"⚔️  COMBAT INITIATED ⚔️")
        print(f"{'='*SEPARATOR_LENGTH}")
        print(f"You are fighting a {self.enemy['name']}!")
        print(f"Enemy Level: ~{self.player.level} | Difficulty: {self.difficulty.title()}")
        
        while self.enemy["health"] > 0 and self.player.health > 0:
            self.turn_count += 1
            
            # Process status effects at start of turn
            if self.player.status_effect_manager.effects:
                print(f"\n--- Turn {self.turn_count} ---")
                self.player.status_effect_manager.process_effects(self.player)
                
                # Check if player died from status effects
                if self.player.health <= 0:
                    return self.defeat()
            
            self.display_combat_status()
            
            print("\n🎯 What will you do?")
            print("1. Attack")
            print("2. Defend")
            print("3. Use Item")
            print("4. Run Away")
            
            try:
                choice = input("\nEnter your choice (1-4): ").strip()
                
                if choice == '1':
                    if self.player_attack():
                        return self.victory()
                    # Enemy counterattacks
                    if self.enemy["health"] > 0:
                        if self.enemy_attack():
                            return self.defeat()
                
                elif choice == '2':
                    if self.player_defend():
                        return self.defeat()
                
                elif choice == '3':
                    consumables = [item for item in self.player.inventory if item["type"] == "consumable"]
                    if not consumables:
                        print("❌ No usable items!")
                        continue
                    
                    print("\n🎒 Available items:")
                    for i, item in enumerate(consumables, 1):
                        print(f"{i}. {item['name']} - {item.get('description', 'No description')}")
                    
                    item_choice = input("Enter item number or '0' to go back: ").strip()
                    if item_choice.isdigit() and item_choice != '0':
                        item_idx = int(item_choice) - 1
                        if 0 <= item_idx < len(consumables):
                            self.use_item_in_combat(consumables[item_idx]["name"])
                            # Enemy attacks after item use
                            if self.enemy_attack():
                                return self.defeat()
                        else:
                            print("❌ Invalid item number!")
                            continue
                    elif item_choice == '0':
                        continue
                    else:
                        print("❌ Invalid input!")
                        continue
                
                elif choice == '4':
                    if self.attempt_flee():
                        return False
                
                else:
                    print("❌ Invalid choice! Please enter 1-4.")
                    continue
                    
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Invalid input. Please try again.")
                continue
        
        return False


def start_combat(player: Any, enemy_key: str, enemies_data: Dict[str, Any]) -> bool:
    """Start a combat encounter"""
    if enemy_key not in enemies_data:
        print(f"Error: Enemy '{enemy_key}' not found!")
        logger.error(f"Enemy '{enemy_key}' not found in enemies_data")
        return False
    
    combat = CombatSystem(player, enemies_data[enemy_key], player.difficulty)
    result = combat.run_combat()
    
    # Check quest completion
    if result:
        player.check_quest_completion("combat")
        
        # Check specific enemy quests
        if enemy_key == "cave_dragon":
            player.check_quest_completion("dragon")
        elif enemy_key == "forest_guardian":
            player.check_quest_completion("guardian")
        
        # Check achievements
        try:
            from achievements import AchievementManager
            if hasattr(player, 'achievement_manager'):
                player.achievement_manager.check_achievement("first_blood", player)
                player.achievement_manager.check_achievement("warrior", player)
                player.achievement_manager.check_achievement("veteran", player)
                player.achievement_manager.check_achievement("legend", player)
                
                if enemy_key == "cave_dragon":
                    player.achievement_manager.check_achievement("dragon_slayer", player)
                elif enemy_key == "forest_guardian":
                    player.achievement_manager.check_achievement("guardian_vanquisher", player)
                
                # Check survivor achievement (won with < 10% health)
                if player.health < player.max_health * 0.1:
                    player.achievement_manager.check_achievement("survivor", player)
                
                # Check untouchable achievement
                if player.battles_won_flawless >= 5:
                    player.achievement_manager.check_achievement("untouchable", player)
        except Exception as e:
            logger.warning(f"Achievement check failed: {e}")
    
    return result

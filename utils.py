import json
import logging
from typing import Optional, Any, List
from player import Player
from achievements import AchievementManager
from status_effects import StatusEffectManager

logger = logging.getLogger(__name__)


def safe_input(prompt: str, valid_options: Optional[List] = None, input_type: type = str) -> Any:
    """Safely get user input with validation"""
    while True:
        try:
            user_input = input(prompt).strip()
            
            if input_type == int:
                value = int(user_input)
                if valid_options and value not in valid_options:
                    print(f"❌ Please enter one of: {valid_options}")
                    continue
                return value
            else:
                if valid_options and user_input.lower() not in [opt.lower() for opt in valid_options]:
                    print(f"❌ Please enter one of: {', '.join(valid_options)}")
                    continue
                return user_input
                
        except ValueError:
            print(f"❌ Invalid input. Please enter a valid {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\n⚠️  Input cancelled.")
            return None


def load_player_from_data(player_data: tuple) -> Optional[Player]:
    """Load a player object from database data"""
    try:
        # Handle both old and new save formats
        if len(player_data) >= 16:
            (id, name, health, max_health, attack, defense, level, experience, 
             score, current_location, inventory_json, equipped_weapon_json, 
             equipped_armor_json, quests_json, gold, difficulty, *extra) = player_data
        else:
            (id, name, health, max_health, attack, defense, level, experience, 
             score, current_location, inventory_json, equipped_weapon_json, 
             equipped_armor_json, quests_json, gold, difficulty) = player_data
            extra = []
        
        # Create player object
        player = Player(name, health, max_health, attack, defense, level, 
                       experience, score, gold, difficulty or "normal")
        player.current_location = current_location or "village"
        
        # Load inventory from JSON
        if inventory_json:
            try:
                player.inventory = json.loads(inventory_json)
            except json.JSONDecodeError:
                player.inventory = []
                logger.warning(f"Failed to load inventory for {name}")
        
        # Load equipped items from JSON
        if equipped_weapon_json:
            try:
                player.equipped_weapon = json.loads(equipped_weapon_json)
            except json.JSONDecodeError:
                player.equipped_weapon = None
                logger.warning(f"Failed to load equipped weapon for {name}")
        
        if equipped_armor_json:
            try:
                player.equipped_armor = json.loads(equipped_armor_json)
            except json.JSONDecodeError:
                player.equipped_armor = None
                logger.warning(f"Failed to load equipped armor for {name}")
        
        # Load quests from JSON
        if quests_json:
            try:
                player.quests = json.loads(quests_json)
            except json.JSONDecodeError:
                player.quests = player._initialize_quests()
                logger.warning(f"Failed to load quests for {name}")
        
        # Load extended data if available
        if len(extra) >= 3:
            achievements_json, status_effects_json, stats_json = extra[:3]
            
            # Load achievements
            if achievements_json:
                try:
                    player.achievement_manager = AchievementManager()
                    achievements_data = json.loads(achievements_json)
                    player.achievement_manager.from_dict(achievements_data)
                except (json.JSONDecodeError, Exception) as e:
                    player.achievement_manager = AchievementManager()
                    logger.warning(f"Failed to load achievements for {name}: {e}")
            else:
                player.achievement_manager = AchievementManager()
            
            # Load status effects
            if status_effects_json:
                try:
                    effects_data = json.loads(status_effects_json)
                    player.status_effect_manager = StatusEffectManager.from_dict(effects_data)
                except (json.JSONDecodeError, Exception) as e:
                    player.status_effect_manager = StatusEffectManager()
                    logger.warning(f"Failed to load status effects for {name}: {e}")
            
            # Load additional stats
            if stats_json:
                try:
                    stats_data = json.loads(stats_json)
                    player.enemies_defeated = stats_data.get("enemies_defeated", 0)
                    player.items_purchased = stats_data.get("items_purchased", 0)
                    player.battles_won_flawless = stats_data.get("battles_won_flawless", 0)
                    player.locations_visited = set(stats_data.get("locations_visited", ["village"]))
                except (json.JSONDecodeError, Exception) as e:
                    logger.warning(f"Failed to load stats for {name}: {e}")
        else:
            # Initialize new features for old saves
            player.achievement_manager = AchievementManager()
            player.status_effect_manager = StatusEffectManager()
        
        logger.info(f"Player {name} loaded successfully")
        return player
        
    except Exception as e:
        print(f"Error loading player data: {e}")
        logger.error(f"Error loading player data: {e}")
        return None


def display_banner() -> None:
    """Display game banner"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║        🗡️  ADVENTURE GAME - ENHANCED EDITION 🛡️      ║
║                                                       ║
║              Explore • Fight • Conquer                ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""
    print(banner)


def display_welcome_message(player: Player) -> None:
    """Display welcome message for returning player"""
    from constants import SEPARATOR_LENGTH
    
    print(f"\n{'='*SEPARATOR_LENGTH}")
    print(f"🌟 Welcome back, {player.name}! 🌟")
    print(f"{'='*50}")
    print(f"⚡ Level: {player.level} | Difficulty: {player.difficulty.title()}")
    print(f"💚 Health: {player.health}/{player.max_health}")
    print(f"💰 Gold: {player.gold}")
    print(f"📍 Location: {player.current_location.replace('_', ' ').title()}")
    print(f"{'='*SEPARATOR_LENGTH}\n")


def display_tips() -> None:
    """Display helpful tips"""
    tips = [
        "💡 Tip: You can use numbers or type action names!",
        "💡 Tip: Type 'check stats' anytime to see your character info!",
        "💡 Tip: Rest at the inn to restore health for 10 gold.",
        "💡 Tip: Complete quests for bonus rewards!",
        "💡 Tip: Equip better weapons and armor to increase your stats.",
        "💡 Tip: Save your game regularly by quitting properly.",
        "💡 Tip: Difficulty affects enemy strength and your stat gains.",
        "💡 Tip: You have a 10% chance to dodge enemy attacks!",
        "💡 Tip: Critical hits deal 50% more damage!"
    ]
    import random
    print(random.choice(tips))


def confirm_action(prompt: str) -> bool:
    """Ask for confirmation"""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("❌ Please enter 'y' or 'n'.")


def clear_screen() -> None:
    """Clear the console screen (optional, for better UX)"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def format_health_bar(current: int, maximum: int, width: int = 20) -> str:
    """Create a visual health bar"""
    filled = int((current / maximum) * width)
    bar = '█' * filled + '░' * (width - filled)
    percentage = int((current / maximum) * 100)
    return f"[{bar}] {current}/{maximum} ({percentage}%)"


def display_quest_progress(player: Player) -> None:
    """Display quest progress summary"""
    from constants import SEPARATOR_LENGTH
    
    print(f"\n{'='*SEPARATOR_LENGTH}")
    print("📋 Quest Progress")
    print(f"{'='*50}")
    
    completed = sum(1 for q in player.quests.values() if q["completed"])
    total = len(player.quests)
    
    print(f"Completed: {completed}/{total}\n")
    
    for quest_name, quest_data in player.quests.items():
        status = "✅" if quest_data["completed"] else "⏳"
        if "progress" in quest_data and not quest_data["completed"]:
            progress_str = f" ({quest_data['progress']}/{quest_data['target']})"
        else:
            progress_str = ""
        print(f"{status} {quest_data['description']}{progress_str}")
    
    print(f"{'='*SEPARATOR_LENGTH}\n")

import sys
import random
import logging
import logging.config
from typing import Optional, Any
from database import DatabaseManager
from player import Player
from locations import LOCATIONS, ENEMIES, LocationHandler
from shop import open_shop
from combat import start_combat
from achievements import AchievementManager
from random_events import RandomEventManager
from colors import colored, Colors, success, error, warning, info
from utils import (
    safe_input, load_player_from_data, display_banner, 
    display_welcome_message, display_tips, confirm_action,
    display_quest_progress
)
from config import LOGGING_CONFIG
from constants import AUTO_SAVE_INTERVAL, SAVE_FILE_VERSION

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class AdventureGame:
    def __init__(self):
        try:
            self.db = DatabaseManager()
            print("✅ Database connected successfully!")
            logger.info("Database connected successfully")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            print("Please ensure MySQL is running and credentials are correct.")
            logger.error(f"Database connection failed: {e}")
            sys.exit(1)
        
        self.current_player: Optional[Player] = None
        self.location_handler: Optional[LocationHandler] = None
        self.event_manager = RandomEventManager()
        self.action_count = 0

    def start_menu(self) -> Optional[Player]:
        """Display main menu"""
        display_banner()
        
        print("1. Start a New Game")
        print("2. Load an Existing Game")
        print("3. Manage Profiles")
        print("4. View Leaderboard")
        print("5. View Achievements")
        print("6. Quit")
        
        choice = safe_input("\nEnter your choice (1-6): ", input_type=int)
        
        if choice == 1:
            return self.create_profile()
        elif choice == 2:
            return self.select_profile()
        elif choice == 3:
            self.manage_profiles()
            return self.start_menu()
        elif choice == 4:
            self.view_leaderboard()
            return self.start_menu()
        elif choice == 5:
            self.view_achievements_menu()
            return self.start_menu()
        elif choice == 6:
            print("👋 Thanks for playing!")
            logger.info("Game exited normally")
            self.db.close()
            sys.exit(0)
        else:
            print("❌ Invalid choice.")
            return self.start_menu()

    def create_profile(self) -> Optional[Player]:
        """Create a new player profile"""
        from constants import SEPARATOR_LENGTH
        
        print(f"\n{'='*SEPARATOR_LENGTH}")
        print("🆕 Create New Character")
        print(f"{'='*SEPARATOR_LENGTH}")
        
        name = input("Enter your character's name: ").strip()
        
        if not name:
            print("❌ Name cannot be empty!")
            return self.create_profile()
        
        # Check if name already exists
        existing = self.db.load_player(name)
        if existing:
            print(f"❌ A character named '{name}' already exists!")
            if confirm_action("Load this character instead?"):
                player_data = existing
                player = load_player_from_data(player_data)
                return player
            return self.create_profile()
        
        # Select difficulty
        print("\n🎮 Select Difficulty:")
        print("1. Easy (Enemies weaker, better stat gains)")
        print("2. Normal (Balanced gameplay)")
        print("3. Hard (Enemies stronger, slower progression)")
        
        diff_choice = safe_input("Enter difficulty (1-3): ", input_type=int)
        difficulty_map = {1: "easy", 2: "normal", 3: "hard"}
        difficulty = difficulty_map.get(diff_choice, "normal")
        
        player = Player(name, difficulty=difficulty)
        player.achievement_manager = AchievementManager()
        print(f"\n✅ Welcome to the adventure, {name}!")
        print(f"⚡ Difficulty: {difficulty.title()}")
        
        # Save initial profile
        self.db.save_player(player)
        logger.info(f"New player created: {name} (difficulty: {difficulty})")
        
        return player

    def select_profile(self):
        """Select an existing profile"""
        players = self.db.get_all_players()
        
        if not players:
            print("\n❌ No saved profiles found.")
            if confirm_action("Create a new character?"):
                return self.create_profile()
            return self.start_menu()
        
        print(f"\n{'='*50}")
        print("📁 Select a Profile")
        print(f"{'='*50}")
        
        for i, (name, level, score) in enumerate(players, 1):
            print(f"{i}. {name} (Level {level}, Score: {score})")
        
        print("0. Go Back")
        
        choice = safe_input("\nEnter profile number: ", input_type=int)
        
        if choice == 0:
            return self.start_menu()
        elif 1 <= choice <= len(players):
            name = players[choice - 1][0]
            player_data = self.db.load_player(name)
            if player_data:
                player = load_player_from_data(player_data)
                print(f"✅ Loaded character: {name}")
                return player
            else:
                print("❌ Error loading profile.")
                return self.select_profile()
        else:
            print("❌ Invalid profile number.")
            return self.select_profile()

    def manage_profiles(self):
        """Manage player profiles"""
        while True:
            print(f"\n{'='*50}")
            print("⚙️  Profile Management")
            print(f"{'='*50}")
            print("1. List Profiles")
            print("2. Delete Profile")
            print("3. Go Back")
            
            choice = safe_input("Enter your choice (1-3): ", input_type=int)
            
            if choice == 1:
                self.list_profiles()
            elif choice == 2:
                self.delete_profile()
            elif choice == 3:
                break
            else:
                print("❌ Invalid choice.")

    def list_profiles(self):
        """List all profiles"""
        players = self.db.get_all_players()
        
        if not players:
            print("\n❌ No profiles found.")
            return
        
        print(f"\n{'='*50}")
        print("📋 All Profiles")
        print(f"{'='*50}")
        
        for i, (name, level, score) in enumerate(players, 1):
            print(f"{i}. {name} - Level {level}, Score: {score}")

    def delete_profile(self):
        """Delete a player profile"""
        players = self.db.get_all_players()
        
        if not players:
            print("\n❌ No profiles to delete.")
            return
        
        print(f"\n{'='*50}")
        print("🗑️  Delete Profile")
        print(f"{'='*50}")
        
        for i, (name, level, score) in enumerate(players, 1):
            print(f"{i}. {name} (Level {level})")
        
        print("0. Cancel")
        
        choice = safe_input("\nEnter profile number to delete: ", input_type=int)
        
        if choice == 0:
            return
        elif 1 <= choice <= len(players):
            name = players[choice - 1][0]
            if confirm_action(f"⚠️  Delete '{name}' permanently?"):
                if self.db.delete_player(name):
                    print(f"✅ Profile '{name}' deleted.")
                else:
                    print("❌ Error deleting profile.")
        else:
            print("❌ Invalid profile number.")

    def view_leaderboard(self) -> None:
        """Display leaderboard"""
        from constants import SEPARATOR_LENGTH, LEADERBOARD_MAX_ENTRIES
        
        players = self.db.get_all_players()
        
        if not players:
            print("\n❌ No players found.")
            return
        
        print(f"\n{'='*SEPARATOR_LENGTH}")
        print("🏆 Leaderboard - Top Players")
        print(f"{'='*SEPARATOR_LENGTH}")
        
        for i, (name, level, score) in enumerate(players[:LEADERBOARD_MAX_ENTRIES], 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            print(f"{medal} {name} - Level {level}, Score: {score}")
        
        print(f"{'='*SEPARATOR_LENGTH}")
        input("\nPress Enter to continue...")
    
    def view_achievements_menu(self) -> None:
        """View achievements menu"""
        from constants import SEPARATOR_LENGTH
        
        print(f"\n{'='*SEPARATOR_LENGTH}")
        print("🏆 Achievements")
        print(f"{'='*SEPARATOR_LENGTH}")
        print("1. View All Achievements")
        print("2. View Player Achievements")
        print("3. Go Back")
        
        choice = safe_input("\nEnter your choice (1-3): ", input_type=int)
        
        if choice == 1:
            # Show all possible achievements
            temp_manager = AchievementManager()
            temp_manager.display_achievements()
            input("\nPress Enter to continue...")
        elif choice == 2:
            # Show specific player achievements
            player = self.select_profile()
            if player and hasattr(player, 'achievement_manager'):
                player.achievement_manager.display_achievements()
                input("\nPress Enter to continue...")
            elif player:
                print("❌ This player has no achievement data.")
        elif choice == 3:
            return
        else:
            print("❌ Invalid choice.")

    def handle_action(self, location, action):
        """Handle player actions"""
        if action == "quit":
            if confirm_action("💾 Save and quit?"):
                self.save_game()
                print("👋 Thanks for playing!")
                return None
            return location

        elif action == "check stats":
            self.current_player.show_stats()
            return location

        elif action == "manage inventory":
            self.manage_inventory()
            return location

        elif action == "rest" and location == "village":
            return self.location_handler.rest_at_inn()

        elif action == "visit shop" and location == "village":
            open_shop(self.current_player)
            return location

        # Location transitions
        elif location == "village":
            if action == "explore forest":
                return self.location_handler.explore_forest()
            elif action == "enter cave":
                return self.location_handler.enter_cave()
            elif action == "enter castle":
                return self.location_handler.enter_castle()

        elif location == "forest":
            if action == "return to village":
                return "village"
            elif action == "explore deeper":
                self.current_player.check_quest_completion("forest_exploration")
                return "deep_forest"
            elif action == "search for herbs":
                return self.location_handler.search_herbs()
            elif action == "hunt animals":
                return self.location_handler.hunt_animals()

        elif location == "deep_forest":
            if action == "return to forest":
                return "forest"
            elif action == "investigate shrine":
                return self.location_handler.investigate_shrine()
            elif action == "challenge guardian":
                if start_combat(self.current_player, "forest_guardian", ENEMIES):
                    print("🌟 The forest guardian nods with respect and disappears into the mist.")
                return "deep_forest"

        elif location == "cave":
            if action == "return to village":
                return "village"
            elif action == "explore deeper":
                return "deep_cave"
            elif action == "search for treasure":
                return self.location_handler.search_treasure()
            elif action == "mine crystals":
                return self.location_handler.mine_crystals()

        elif location == "deep_cave":
            if action == "return to cave":
                return "cave"
            elif action == "fight dragon":
                if start_combat(self.current_player, "cave_dragon", ENEMIES):
                    print("🐉 You have slain the mighty dragon! The cave is now safe.")
                return "deep_cave"
            elif action == "collect treasure":
                return self.location_handler.collect_dragon_treasure()

        elif location == "castle":
            if action == "return to village":
                return "village"
            elif action == "enter throne room":
                return self.location_handler.enter_throne_room()
            elif action == "explore library":
                return self.location_handler.explore_library()
            elif action == "climb tower":
                return self.location_handler.climb_tower()

        elif location == "shop":
            if action == "return to village":
                return "village"

        return location

    def manage_inventory(self) -> None:
        """Manage player inventory"""
        while True:
            self.current_player.show_inventory()
            
            # Check inventory achievements
            if hasattr(self.current_player, 'achievement_manager'):
                self.current_player.achievement_manager.check_achievement("collector", self.current_player)
                self.current_player.achievement_manager.check_achievement("hoarder", self.current_player)
            
            print("1. Use Item")
            print("2. Equip Item")
            print("3. Unequip Item")
            print("4. Drop Item")
            print("5. View Quests")
            print("6. Go Back")
            
            choice = safe_input("\nEnter your choice (1-6): ", input_type=int)
            
            if choice == 1:
                self.use_item_menu()
            elif choice == 2:
                self.equip_item_menu()
            elif choice == 3:
                self.unequip_item_menu()
            elif choice == 4:
                self.drop_item_menu()
            elif choice == 5:
                display_quest_progress(self.current_player)
            elif choice == 6:
                break

    def use_item_menu(self):
        """Use item from inventory"""
        consumables = [item for item in self.current_player.inventory if item["type"] == "consumable"]
        
        if not consumables:
            print("\n❌ No usable items!")
            return
        
        print("\n🎒 Select item to use:")
        for i, item in enumerate(consumables, 1):
            print(f"{i}. {item['name']} - {item.get('description', '')}")
        print("0. Cancel")
        
        choice = safe_input("Enter item number: ", input_type=int)
        
        if choice and 1 <= choice <= len(consumables):
            self.current_player.use_item(consumables[choice - 1]["name"])

    def equip_item_menu(self):
        """Equip item from inventory"""
        equippable = [item for item in self.current_player.inventory if item["type"] in ["weapon", "armor"]]
        
        if not equippable:
            print("\n❌ No equippable items!")
            return
        
        print("\n⚔️  Select item to equip:")
        for i, item in enumerate(equippable, 1):
            print(f"{i}. {item['name']} ({item['type']}) - {item.get('description', '')}")
        print("0. Cancel")
        
        choice = safe_input("Enter item number: ", input_type=int)
        
        if choice and 1 <= choice <= len(equippable):
            self.current_player.equip_item(equippable[choice - 1]["name"])

    def unequip_item_menu(self):
        """Unequip weapon or armor"""
        print("\n🔓 Unequip:")
        print("1. Weapon")
        print("2. Armor")
        print("0. Cancel")
        
        choice = safe_input("Enter your choice: ", input_type=int)
        
        if choice == 1:
            self.current_player.unequip_item("weapon")
        elif choice == 2:
            self.current_player.unequip_item("armor")

    def drop_item_menu(self):
        """Drop item from inventory"""
        if not self.current_player.inventory:
            print("\n❌ No items to drop!")
            return
        
        print("\n🗑️  Select item to drop:")
        for i, item in enumerate(self.current_player.inventory, 1):
            print(f"{i}. {item['name']}")
        print("0. Cancel")
        
        choice = safe_input("Enter item number: ", input_type=int)
        
        if choice and 1 <= choice <= len(self.current_player.inventory):
            item_name = self.current_player.inventory[choice - 1]["name"]
            if confirm_action(f"Drop {item_name}?"):
                self.current_player.drop_item(item_name)

    def get_player_input(self, location):
        """Get player action input"""
        print(f"\n{'='*50}")
        print(f"📍 Current Location: {location.replace('_', ' ').title()}")
        print(f"{'='*50}")
        print(LOCATIONS[location]["text"])
        print(f"\n🎯 Available actions:")
        
        valid_actions = LOCATIONS.get(location, {}).get("actions", {})
        for i, (action, description) in enumerate(valid_actions.items(), 1):
            print(f"{i}. {action.title()}")
        
        while True:
            try:
                choice = input("\n➤ Enter your choice (number or action name): ").strip()
                
                # Handle numeric input
                if choice.isdigit():
                    choice_num = int(choice)
                    action_list = list(valid_actions.keys())
                    
                    if 1 <= choice_num <= len(action_list):
                        return action_list[choice_num - 1]
                    else:
                        print("❌ Invalid choice number!")
                        continue
                
                # Handle text input
                choice_lower = choice.lower()
                if choice_lower in valid_actions:
                    return choice_lower
                else:
                    # Try to match partial input
                    matches = [action for action in valid_actions if choice_lower in action.lower()]
                    if len(matches) == 1:
                        return matches[0]
                    elif len(matches) > 1:
                        print(f"❌ Multiple matches: {', '.join(matches)}")
                        print("Please be more specific.")
                    else:
                        print("❌ Invalid action. Please try again.")
            
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Invalid input. Please try again.")

    def save_game(self):
        """Save the current game"""
        if self.current_player:
            if self.db.save_player(self.current_player):
                print("💾 Game saved successfully!")
            else:
                print("❌ Error saving game!")

    def main_game_loop(self):
        """Main game loop"""
        while True:
            try:
                self.current_player = self.start_menu()
                
                if self.current_player:
                    self.location_handler = LocationHandler(self.current_player)
                    display_welcome_message(self.current_player)
                    display_tips()
                    
                    self.action_count = 0
                    
                    while True:
                        # Check for random events (10% chance per action)
                        if random.random() < 0.10:
                            is_ambush = self.event_manager.trigger_event(
                                self.current_player, 
                                self.current_player.current_location
                            )
                            if is_ambush:
                                # Trigger combat from ambush
                                enemy_key = random.choice(list(ENEMIES.keys()))
                                start_combat(self.current_player, enemy_key, ENEMIES)
                        
                        action = self.get_player_input(self.current_player.current_location)
                        
                        new_location = self.handle_action(self.current_player.current_location, action)
                        
                        if new_location is None:
                            break
                        
                        self.current_player.current_location = new_location
                        self.action_count += 1
                        
                        # Track location visits
                        if hasattr(self.current_player, 'locations_visited'):
                            self.current_player.locations_visited.add(new_location)
                        
                        # Check level and gold achievements
                        if hasattr(self.current_player, 'achievement_manager'):
                            self.current_player.achievement_manager.check_achievement("apprentice", self.current_player)
                            self.current_player.achievement_manager.check_achievement("expert", self.current_player)
                            self.current_player.achievement_manager.check_achievement("master", self.current_player)
                            self.current_player.achievement_manager.check_achievement("wealthy", self.current_player)
                            self.current_player.achievement_manager.check_achievement("tycoon", self.current_player)
                        
                        # Auto-save every N actions
                        if self.action_count % AUTO_SAVE_INTERVAL == 0:
                            self.save_game()
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Game interrupted.")
                if self.current_player and confirm_action("Save progress?"):
                    self.save_game()
                print("👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                if self.current_player:
                    self.save_game()
                    print("💾 Game saved due to error.")


def main():
    """Main entry point"""
    try:
        game = AdventureGame()
        game.main_game_loop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        print("\n👋 Thanks for playing Adventure Game!")


if __name__ == "__main__":
    main()

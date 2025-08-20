import mysql.connector
import random
import json

# Initialize the database connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="tiger"
    )
except mysql.connector.Error as err:
    print("Error connecting to MySQL:", err)
    exit()

# Initialize the cursor
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS adventure")
cursor.execute("USE adventure")

# Create enhanced tables
cursor.execute('''CREATE TABLE IF NOT EXISTS players(
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
);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS game_items(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    type VARCHAR(50),
    value INT,
    description TEXT
);''')

# Initialize game items
game_items = [
    ("Health Potion", "consumable", 50, "Restores 50 health points"),
    ("Iron Sword", "weapon", 15, "A sturdy iron sword. +15 attack"),
    ("Steel Shield", "armor", 10, "A reliable steel shield. +10 defense"),
    ("Magic Herb", "consumable", 30, "A mystical herb. Restores 30 health"),
    ("Gold Coin", "currency", 1, "Standard currency"),
    ("Ancient Key", "key", 0, "An old key that might unlock something special")
]

# Insert items if they don't exist
for item in game_items:
    cursor.execute("INSERT IGNORE INTO game_items (name, type, value, description) VALUES (%s, %s, %s, %s)", item)
conn.commit()

# Enhanced locations with more depth
locations = {
    "village": {
        "text": "You are in the peaceful village. The sun shines warmly on the cobblestone streets.",
        "actions": {
            "explore forest": "Venture into the mysterious forest",
            "enter cave": "Explore the dark cave system",
            "enter castle": "Approach the ancient castle",
            "visit shop": "Visit the village shop",
            "rest": "Rest at the inn to restore health",
            "check stats": "Check your character statistics",
            "quit": "Save and quit the game"
        }
    },
    "forest": {
        "text": "You are deep in the enchanted forest. Strange sounds echo through the trees.",
        "actions": {
            "return to village": "Return to the safety of the village",
            "explore deeper": "Venture deeper into the forest",
            "search for herbs": "Search for medicinal herbs",
            "hunt animals": "Hunt for food and experience",
            "check stats": "Check your character statistics",
            "quit": "Save and quit the game"
        }
    },
    "deep_forest": {
        "text": "You are in the heart of the forest. Ancient magic flows through this place.",
        "actions": {
            "return to forest": "Return to the forest entrance",
            "investigate shrine": "Examine the mysterious shrine",
            "challenge guardian": "Face the forest guardian",
            "check stats": "Check your character statistics",
            "quit": "Save and quit the game"
        }
    },
    "cave": {
        "text": "The cave is dark and damp. You can hear water dripping in the distance.",
        "actions": {
            "return to village": "Return to the village",
            "explore deeper": "Go deeper into the cave system",
            "search for treasure": "Search for hidden treasure",
            "mine crystals": "Mine valuable crystals",
            "check stats": "Check your character statistics",
            "quit": "Save and quit the game"
        }
    },
    "deep_cave": {
        "text": "You are in the deepest part of the cave. Precious gems glitter in the darkness.",
        "actions": {
            "return to cave": "Return to the cave entrance",
            "fight dragon": "Challenge the cave dragon",
            "collect treasure": "Gather the dragon's treasure",
            "check stats": "Check your character statistics",
            "quit": "Save and quit the game"
        }
    },
    "castle": {
        "text": "The ancient castle looms before you. Its towers reach toward the cloudy sky.",
        "actions": {
            "return to village": "Return to the village",
            "enter throne room": "Enter the grand throne room",
            "explore library": "Visit the castle library",
            "climb tower": "Climb the highest tower",
            "check stats": "Check your character statistics",
            "quit": "Save and quit the game"
        }
    },
    "shop": {
        "text": "Welcome to the village shop! The merchant greets you with a friendly smile.",
        "actions": {
            "buy items": "Purchase items from the merchant",
            "sell items": "Sell items from your inventory",
            "return to village": "Return to the village square",
            "check stats": "Check your character statistics",
            "quit": "Save and quit the game"
        }
    }
}

# Define enemies with balanced stats
enemies = {
    "goblin": {"name": "Goblin", "health": 40, "attack": 12, "defense": 3, "exp_reward": 15, "gold_reward": 8},
    "wolf": {"name": "Wolf", "health": 35, "attack": 15, "defense": 2, "exp_reward": 12, "gold_reward": 5},
    "bandit": {"name": "Bandit", "health": 50, "attack": 18, "defense": 5, "exp_reward": 20, "gold_reward": 15},
    "forest_guardian": {"name": "Forest Guardian", "health": 120, "attack": 25, "defense": 8, "exp_reward": 100, "gold_reward": 50},
    "cave_dragon": {"name": "Cave Dragon", "health": 200, "attack": 35, "defense": 15, "exp_reward": 200, "gold_reward": 100},
    "skeleton": {"name": "Skeleton Warrior", "health": 45, "attack": 20, "defense": 6, "exp_reward": 25, "gold_reward": 12}
}

# Quest system
default_quests = {
    "first_combat": {"description": "Win your first battle", "completed": False, "reward": 50},
    "herb_collector": {"description": "Collect 3 healing herbs", "progress": 0, "target": 3, "completed": False, "reward": 30},
    "treasure_hunter": {"description": "Find treasure in the cave", "completed": False, "reward": 75},
    "dragon_slayer": {"description": "Defeat the cave dragon", "completed": False, "reward": 200},
    "forest_explorer": {"description": "Explore the deep forest", "completed": False, "reward": 40}
}

class Player:
    def __init__(self, name, health=100, max_health=100, attack=20, defense=5, level=1, experience=0, score=0, gold=50):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.base_attack = attack
        self.base_defense = defense
        self.level = level
        self.experience = experience
        self.score = score
        self.gold = gold
        self.inventory = []
        self.equipped_weapon = None
        self.equipped_armor = None
        self.quests = default_quests.copy()
        self.current_location = "village"

    @property
    def attack(self):
        bonus = 0
        if self.equipped_weapon:
            bonus = self.equipped_weapon.get("value", 0)
        return self.base_attack + bonus

    @property
    def defense(self):
        bonus = 0
        if self.equipped_armor:
            bonus = self.equipped_armor.get("value", 0)
        return self.base_defense + bonus

    def add_item(self, item):
        self.inventory.append(item)
        print(f"You obtained: {item['name']}")

    def use_item(self, item_name):
        for item in self.inventory:
            if item["name"].lower() == item_name.lower():
                if item["type"] == "consumable":
                    if "Health" in item["name"]:
                        heal_amount = item["value"]
                        old_health = self.health
                        self.health = min(self.max_health, self.health + heal_amount)
                        print(f"You used {item['name']} and restored {self.health - old_health} health!")
                        self.inventory.remove(item)
                        return True
                break
        print(f"You don't have {item_name} or it can't be used.")
        return False

    def equip_item(self, item_name):
        for item in self.inventory:
            if item["name"].lower() == item_name.lower():
                if item["type"] == "weapon":
                    if self.equipped_weapon:
                        self.inventory.append(self.equipped_weapon)
                    self.equipped_weapon = item
                    self.inventory.remove(item)
                    print(f"You equipped {item['name']}!")
                    return True
                elif item["type"] == "armor":
                    if self.equipped_armor:
                        self.inventory.append(self.equipped_armor)
                    self.equipped_armor = item
                    self.inventory.remove(item)
                    print(f"You equipped {item['name']}!")
                    return True
                break
        print(f"You don't have {item_name} or it can't be equipped.")
        return False

    def gain_experience(self, exp):
        self.experience += exp
        print(f"You gained {exp} experience points!")
        
        # Level up check
        exp_needed = self.level * 100
        if self.experience >= exp_needed:
            self.level_up()

    def level_up(self):
        self.level += 1
        health_bonus = 20
        attack_bonus = 3
        defense_bonus = 2
        
        self.max_health += health_bonus
        self.health = self.max_health  # Full heal on level up
        self.base_attack += attack_bonus
        self.base_defense += defense_bonus
        
        print(f"\n🎉 LEVEL UP! You are now level {self.level}!")
        print(f"Health increased by {health_bonus} (now {self.max_health})")
        print(f"Attack increased by {attack_bonus} (now {self.base_attack})")
        print(f"Defense increased by {defense_bonus} (now {self.base_defense})")

    def check_quest_completion(self, quest_type, **kwargs):
        if quest_type == "combat" and not self.quests["first_combat"]["completed"]:
            self.quests["first_combat"]["completed"] = True
            self.gain_experience(self.quests["first_combat"]["reward"])
            print("Quest completed: Win your first battle!")
            
        elif quest_type == "herb" and not self.quests["herb_collector"]["completed"]:
            self.quests["herb_collector"]["progress"] += 1
            if self.quests["herb_collector"]["progress"] >= self.quests["herb_collector"]["target"]:
                self.quests["herb_collector"]["completed"] = True
                self.gain_experience(self.quests["herb_collector"]["reward"])
                print("Quest completed: Collect 3 healing herbs!")

    def show_stats(self):
        print(f"\n📊 {self.name}'s Statistics:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack} (Base: {self.base_attack})")
        print(f"Defense: {self.defense} (Base: {self.base_defense})")
        print(f"Experience: {self.experience}")
        print(f"Gold: {self.gold}")
        print(f"Score: {self.score}")
        
        if self.equipped_weapon:
            print(f"Weapon: {self.equipped_weapon['name']}")
        if self.equipped_armor:
            print(f"Armor: {self.equipped_armor['name']}")
            
        print(f"Inventory ({len(self.inventory)} items):")
        if self.inventory:
            for item in self.inventory:
                print(f"  - {item['name']}")
        else:
            print("  (empty)")

def start_menu():
    print("""
========================
    ADVENTURE GAME - V2
========================
""")
    print("1. Start a New Game")
    print("2. Load an Existing Game")
    print("3. Manage Profiles")
    print("4. Quit")

    while True:
        choice = input("Enter your choice (1/2/3/4): ")
        if choice == '1':
            return create_profile()
        elif choice == '2':
            return select_profile()
        elif choice == '3':
            manage_profiles()
        elif choice == '4':
            print("Thanks for playing!")
            conn.close()
            exit()
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

def create_profile():
    name = input("Enter your character's name: ")
    player = Player(name)
    print(f"Welcome to the adventure, {name}!")
    return player

def select_profile():
    cursor.execute("SELECT name FROM players")
    profiles = [row[0] for row in cursor.fetchall()]

    if not profiles:
        print("No saved profiles found. Creating a new game...")
        return create_profile()

    print("Select a profile:")
    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile}")

    while True:
        choice = input("Enter the profile number or '0' to go back: ")
        if choice == '0':
            return start_menu()
        elif choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(profiles):
                name = profiles[choice - 1]
                player = load_game(name)
                if player:
                    return player
                else:
                    print("Error loading profile. Please try again.")
            else:
                print("Invalid profile number. Please try again.")
        else:
            print("Invalid input. Please enter a number or '0'.")

def manage_profiles():
    while True:
        print("\n=== Profile Management ===")
        print("1. List Profiles")
        print("2. Delete Profile")
        print("3. Go Back")
        choice = input("Enter your choice (1/2/3): ")
        if choice == '1':
            list_profiles()
        elif choice == '2':
            delete_profile()
        elif choice == '3':
            return start_menu()
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def list_profiles():
    cursor.execute("SELECT name, level, score FROM players")
    profiles = cursor.fetchall()

    print("=== Existing Profiles ===")
    for i, (name, level, score) in enumerate(profiles, 1):
        print(f"{i}. {name} (Level {level}, Score: {score})")

def delete_profile():
    cursor.execute("SELECT name FROM players")
    profiles = [row[0] for row in cursor.fetchall()]
    
    if not profiles:
        print("No profiles to delete.")
        return

    print("Select a profile to delete:")
    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile}")

    choice = input("Enter the profile number to delete or '0' to cancel: ")
    if choice == '0':
        return
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(profiles):
            name = profiles[choice - 1]
            cursor.execute("DELETE FROM players WHERE name = %s", (name,))
            conn.commit()
            print(f"Profile '{name}' has been deleted.")
        else:
            print("Invalid profile number. Please try again.")
    else:
        print("Invalid input. Please enter a number or '0'.")

def combat_system(player, enemy_key):
    enemy = enemies[enemy_key].copy()
    print(f"\n⚔️  COMBAT INITIATED ⚔️")
    print(f"You are fighting a {enemy['name']}!")
    print(f"Enemy Health: {enemy['health']}")

    while enemy["health"] > 0 and player.health > 0:
        print(f"\nYour Health: {player.health}/{player.max_health}")
        print(f"{enemy['name']} Health: {enemy['health']}")
        print("\nWhat will you do?")
        print("1. Attack")
        print("2. Use Item")
        print("3. Run Away")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            # Player attacks
            damage = max(1, player.attack - enemy["defense"] + random.randint(-3, 3))
            enemy["health"] -= damage
            print(f"You deal {damage} damage to the {enemy['name']}!")

            if enemy["health"] <= 0:
                print(f"You defeated the {enemy['name']}!")
                player.gain_experience(enemy["exp_reward"])
                player.gold += enemy["gold_reward"]
                player.score += enemy["exp_reward"]
                player.check_quest_completion("combat")
                
                # Random loot drop
                if random.choice([True, False]):
                    loot_items = [
                        {"name": "Health Potion", "type": "consumable", "value": 50},
                        {"name": "Gold Coin", "type": "currency", "value": random.randint(5, 15)}
                    ]
                    loot = random.choice(loot_items)
                    if loot["name"] == "Gold Coin":
                        player.gold += loot["value"]
                        print(f"You found {loot['value']} gold coins!")
                    else:
                        player.add_item(loot)
                
                return True

        elif choice == '2':
            print("Available items:")
            consumables = [item for item in player.inventory if item["type"] == "consumable"]
            if not consumables:
                print("No usable items!")
                continue
            
            for i, item in enumerate(consumables, 1):
                print(f"{i}. {item['name']}")
            
            item_choice = input("Enter item number or '0' to go back: ")
            if item_choice.isdigit() and item_choice != '0':
                item_choice = int(item_choice)
                if 1 <= item_choice <= len(consumables):
                    player.use_item(consumables[item_choice - 1]["name"])
                else:
                    print("Invalid item number!")
                    continue
            elif item_choice == '0':
                continue
            else:
                print("Invalid input!")
                continue

        elif choice == '3':
            if random.choice([True, False]):
                print("You successfully ran away!")
                return False
            else:
                print("You couldn't escape!")

        else:
            print("Invalid choice!")
            continue

        # Enemy attacks if still alive
        if enemy["health"] > 0:
            damage = max(1, enemy["attack"] - player.defense + random.randint(-2, 2))
            player.health -= damage
            print(f"The {enemy['name']} deals {damage} damage to you!")

            if player.health <= 0:
                print("💀 You have been defeated!")
                player.health = 1  # Don't let player die completely
                print("You wake up back in the village with 1 health.")
                player.current_location = "village"
                return False

    return False

def shop_system(player):
    shop_items = [
        {"name": "Health Potion", "type": "consumable", "value": 50, "price": 25},
        {"name": "Iron Sword", "type": "weapon", "value": 15, "price": 100},
        {"name": "Steel Shield", "type": "armor", "value": 10, "price": 80},
        {"name": "Magic Herb", "type": "consumable", "value": 30, "price": 15}
    ]

    while True:
        print(f"\n🏪 Village Shop (Your gold: {player.gold})")
        print("1. Buy Items")
        print("2. Sell Items")
        print("3. Leave Shop")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            print("\nItems for sale:")
            for i, item in enumerate(shop_items, 1):
                print(f"{i}. {item['name']} - {item['price']} gold ({item['description'] if 'description' in item else 'No description'})")

            buy_choice = input("Enter item number to buy or '0' to go back: ")
            if buy_choice.isdigit() and buy_choice != '0':
                buy_choice = int(buy_choice)
                if 1 <= buy_choice <= len(shop_items):
                    item = shop_items[buy_choice - 1]
                    if player.gold >= item["price"]:
                        player.gold -= item["price"]
                        player.add_item({"name": item["name"], "type": item["type"], "value": item["value"]})
                        print(f"You bought {item['name']} for {item['price']} gold!")
                    else:
                        print("Not enough gold!")
                else:
                    print("Invalid item number!")

        elif choice == '2':
            if not player.inventory:
                print("You have no items to sell!")
                continue
            
            print("Your items:")
            for i, item in enumerate(player.inventory, 1):
                sell_price = max(1, item.get("value", 0) // 2)
                print(f"{i}. {item['name']} - {sell_price} gold")

            sell_choice = input("Enter item number to sell or '0' to go back: ")
            if sell_choice.isdigit() and sell_choice != '0':
                sell_choice = int(sell_choice)
                if 1 <= sell_choice <= len(player.inventory):
                    item = player.inventory[sell_choice - 1]
                    sell_price = max(1, item.get("value", 0) // 2)
                    player.gold += sell_price
                    player.inventory.remove(item)
                    print(f"You sold {item['name']} for {sell_price} gold!")

        elif choice == '3':
            break

def handle_action(location, action, player):
    if action == "quit":
        save_game(player)
        print("Game saved successfully!")
        print("Thanks for playing!")
        return None

    elif action == "check stats":
        player.show_stats()
        return location

    elif action == "rest" and location == "village":
        cost = 10
        if player.gold >= cost:
            player.gold -= cost
            old_health = player.health
            player.health = player.max_health
            print(f"You rest at the inn and restore {player.max_health - old_health} health for {cost} gold!")
        else:
            print("You don't have enough gold to rest at the inn (10 gold required).")
        return location

    elif action == "visit shop" and location == "village":
        shop_system(player)
        return location

    # Location transitions
    elif location == "village":
        if action == "explore forest":
            return explore_forest(player)
        elif action == "enter cave":
            return enter_cave(player)
        elif action == "enter castle":
            return enter_castle(player)

    elif location == "forest":
        if action == "return to village":
            return "village"
        elif action == "explore deeper":
            player.check_quest_completion("forest_exploration")
            return "deep_forest"
        elif action == "search for herbs":
            return search_herbs(player)
        elif action == "hunt animals":
            return hunt_animals(player)

    elif location == "deep_forest":
        if action == "return to forest":
            return "forest"
        elif action == "investigate shrine":
            return investigate_shrine(player)
        elif action == "challenge guardian":
            if combat_system(player, "forest_guardian"):
                print("The forest guardian nods with respect and disappears into the mist.")
                return "deep_forest"
            return "deep_forest"

    elif location == "cave":
        if action == "return to village":
            return "village"
        elif action == "explore deeper":
            return "deep_cave"
        elif action == "search for treasure":
            return search_treasure(player)
        elif action == "mine crystals":
            return mine_crystals(player)

    elif location == "deep_cave":
        if action == "return to cave":
            return "cave"
        elif action == "fight dragon":
            if combat_system(player, "cave_dragon"):
                print("You have slain the mighty dragon! The cave is now safe.")
                player.check_quest_completion("dragon")
                return "deep_cave"
            return "deep_cave"
        elif action == "collect treasure":
            return collect_dragon_treasure(player)

    elif location == "castle":
        if action == "return to village":
            return "village"
        elif action == "enter throne room":
            return enter_throne_room(player)
        elif action == "explore library":
            return explore_library(player)
        elif action == "climb tower":
            return climb_tower(player)

    elif location == "shop":
        if action == "buy items" or action == "sell items":
            shop_system(player)
        elif action == "return to village":
            return "village"

    return location

# Enhanced location functions
def explore_forest(player):
    print("You venture into the mysterious forest...")
    
    if random.random() < 0.4:  # 40% chance of encounter
        enemy_types = ["goblin", "wolf"]
        enemy = random.choice(enemy_types)
        print(f"A wild {enemies[enemy]['name']} appears!")
        combat_system(player, enemy)
    
    return "forest"

def search_herbs(player):
    print("You search the forest floor for medicinal herbs...")
    if random.random() < 0.7:  # 70% chance of finding herbs
        herb = {"name": "Magic Herb", "type": "consumable", "value": 30}
        player.add_item(herb)
        player.check_quest_completion("herb")
        print("You found a magical healing herb!")
    else:
        print("You couldn't find any herbs this time.")
    return "forest"

def hunt_animals(player):
    print("You hunt for small game in the forest...")
    if random.random() < 0.6:  # 60% chance of successful hunt
        exp_gain = random.randint(8, 15)
        gold_gain = random.randint(3, 8)
        player.gain_experience(exp_gain)
        player.gold += gold_gain
        print(f"Successful hunt! You gained {exp_gain} experience and {gold_gain} gold.")
    else:
        print("The animals were too quick this time.")
    return "forest"

def investigate_shrine(player):
    print("You approach the ancient shrine...")
    print("The shrine glows with mystical energy.")
    
    if random.random() < 0.5:  # 50% chance of blessing
        bonus_exp = 25
        player.gain_experience(bonus_exp)
        print(f"The shrine blesses you with {bonus_exp} experience points!")
    else:
        heal_amount = 20
        player.health = min(player.max_health, player.health + heal_amount)
        print(f"The shrine's energy heals you for {heal_amount} health!")
    
    return "deep_forest"

def enter_cave(player):
    print("You enter the dark, echoing cave...")
    
    if random.random() < 0.3:  # 30% chance of encounter
        if combat_system(player, "skeleton"):
            print("The skeleton crumbles to dust.")
    
    return "cave"

def search_treasure(player):
    print("You search the cave walls for hidden treasure...")
    if random.random() < 0.6:  # 60% chance of finding something
        treasures = [
            {"name": "Gold Coin", "amount": random.randint(10, 25)},
            {"name": "Health Potion", "type": "consumable", "value": 50}
        ]
        treasure = random.choice(treasures)
        
        if treasure["name"] == "Gold Coin":
            player.gold += treasure["amount"]
            print(f"You found {treasure['amount']} gold coins!")
        else:
            player.add_item(treasure)
        
        player.check_quest_completion("treasure")
    else:
        print("You found nothing of value this time.")
    return "cave"

def mine_crystals(player):
    print("You mine the crystal formations...")
    if random.random() < 0.4:  # 40% chance of success
        gold_gain = random.randint(15, 30)
        exp_gain = random.randint(10, 20)
        player.gold += gold_gain
        player.gain_experience(exp_gain)
        print(f"You successfully mined crystals! Gained {gold_gain} gold and {exp_gain} experience.")
    else:
        print("The crystals were too hard to extract.")
    return "cave"

def collect_dragon_treasure(player):
    print("You carefully approach the dragon's treasure hoard...")
    if any(quest["completed"] for quest in player.quests.values() if "dragon" in quest.get("description", "").lower()):
        treasure_gold = random.randint(100, 200)
        player.gold += treasure_gold
        player.score += 500
        legendary_item = {"name": "Dragon Scale Armor", "type": "armor", "value": 25}
        player.add_item(legendary_item)
        print(f"You collect {treasure_gold} gold and find legendary Dragon Scale Armor!")
    else:
        print("The sleeping dragon stirs... you dare not approach without defeating it first.")
    return "deep_cave"

def enter_castle(player):
    print("You approach the ancient castle...")
    print("The massive doors creak open as you near them.")
    return "castle"

def enter_throne_room(player):
    print("You enter the grand throne room...")
    print("An ancient spirit materializes before the throne!")
    
    if random.random() < 0.7:  # 70% chance of friendly encounter
        exp_bonus = 50
        player.gain_experience(exp_bonus)
        print(f"The spirit shares ancient wisdom with you! (+{exp_bonus} experience)")
    else:
        if combat_system(player, "skeleton"):
            print("The spirit finds peace and vanishes.")
    
    return "castle"

def explore_library(player):
    print("You explore the vast library...")
    print("Ancient books line the walls from floor to ceiling.")
    
    knowledge_gained = random.randint(20, 40)
    player.gain_experience(knowledge_gained)
    print(f"You study ancient texts and gain {knowledge_gained} experience!")
    
    # Chance to find a rare book
    if random.random() < 0.3:  # 30% chance
        rare_book = {"name": "Ancient Spell Book", "type": "misc", "value": 100}
        player.add_item(rare_book)
        print("You found a rare Ancient Spell Book!")
    
    return "castle"

def climb_tower(player):
    print("You climb the winding stairs of the highest tower...")
    print("From the top, you can see the entire realm spread out below you.")
    
    # Chance of finding something special
    if random.random() < 0.5:  # 50% chance
        if random.choice([True, False]):
            # Find treasure
            gold_found = random.randint(25, 50)
            player.gold += gold_found
            print(f"You found a hidden cache with {gold_found} gold coins!")
        else:
            # Gain insight
            exp_gained = 30
            player.gain_experience(exp_gained)
            print(f"The breathtaking view inspires you! (+{exp_gained} experience)")
    
    return "castle"

def save_game(player):
    try:
        # Convert complex data to JSON strings
        inventory_json = json.dumps(player.inventory)
        quests_json = json.dumps(player.quests)
        
        # Use INSERT ... ON DUPLICATE KEY UPDATE for MySQL
        cursor.execute("""
            INSERT INTO players (name, health, max_health, attack, defense, level, experience, score, current_location, inventory, quests, gold)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            health=%s, max_health=%s, attack=%s, defense=%s, level=%s, experience=%s, score=%s, current_location=%s, inventory=%s, quests=%s, gold=%s
        """, (
            player.name, player.health, player.max_health, player.base_attack, player.base_defense,
            player.level, player.experience, player.score, player.current_location, inventory_json, quests_json, player.gold,
            # Update values (same as insert values)
            player.health, player.max_health, player.base_attack, player.base_defense,
            player.level, player.experience, player.score, player.current_location, inventory_json, quests_json, player.gold
        ))
        conn.commit()
        print("Game saved successfully!")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game(player_name):
    try:
        cursor.execute("SELECT * FROM players WHERE name = %s", (player_name,))
        player_data = cursor.fetchone()

        if player_data:
            # Unpack player data
            (id, name, health, max_health, attack, defense, level, experience, 
             score, current_location, inventory_json, quests_json, gold) = player_data
            
            # Create player object
            player = Player(name, health, max_health, attack, defense, level, experience, score, gold)
            player.current_location = current_location or "village"
            
            # Load inventory and quests from JSON
            if inventory_json:
                try:
                    player.inventory = json.loads(inventory_json)
                except json.JSONDecodeError:
                    player.inventory = []
            
            if quests_json:
                try:
                    player.quests = json.loads(quests_json)
                except json.JSONDecodeError:
                    player.quests = default_quests.copy()
            
            # Handle equipped items (find them in inventory)
            for item in player.inventory[:]:  # Create a copy to iterate over
                if item.get("equipped", False):
                    if item["type"] == "weapon":
                        player.equipped_weapon = item
                        player.inventory.remove(item)
                    elif item["type"] == "armor":
                        player.equipped_armor = item
                        player.inventory.remove(item)
            
            print(f"Game loaded successfully! Welcome back, {name}!")
            return player
        else:
            print("No save data found for this player.")
            return None
    except Exception as e:
        print(f"Error loading game: {e}")
        return None

def get_player_input(location, player):
    while True:
        print(f"\n📍 Current Location: {location.title()}")
        print("=" * 50)
        print(locations[location]["text"])
        print("\n🎯 Available actions:")
        
        valid_actions = locations.get(location, {}).get("actions", {})
        for i, (action, description) in enumerate(valid_actions.items(), 1):
            print(f"{i}. {action.title()}: {description}")
        
        # Additional options
        print(f"{len(valid_actions) + 1}. Use Item")
        print(f"{len(valid_actions) + 2}. Equip Item")
        print(f"{len(valid_actions) + 3}. Show Inventory")

        try:
            choice = input("\nEnter your choice (number or action name): ").strip()
            
            # Handle numeric input
            if choice.isdigit():
                choice_num = int(choice)
                action_list = list(valid_actions.keys())
                
                if 1 <= choice_num <= len(action_list):
                    return action_list[choice_num - 1]
                elif choice_num == len(valid_actions) + 1:
                    # Use item
                    if not player.inventory:
                        print("Your inventory is empty!")
                        continue
                    
                    consumables = [item for item in player.inventory if item["type"] == "consumable"]
                    if not consumables:
                        print("No usable items in inventory!")
                        continue
                    
                    print("Select an item to use:")
                    for i, item in enumerate(consumables, 1):
                        print(f"{i}. {item['name']}")
                    
                    item_choice = input("Enter item number: ")
                    if item_choice.isdigit():
                        item_num = int(item_choice)
                        if 1 <= item_num <= len(consumables):
                            player.use_item(consumables[item_num - 1]["name"])
                    continue
                    
                elif choice_num == len(valid_actions) + 2:
                    # Equip item
                    equippable = [item for item in player.inventory if item["type"] in ["weapon", "armor"]]
                    if not equippable:
                        print("No equippable items in inventory!")
                        continue
                    
                    print("Select an item to equip:")
                    for i, item in enumerate(equippable, 1):
                        print(f"{i}. {item['name']} ({item['type']})")
                    
                    item_choice = input("Enter item number: ")
                    if item_choice.isdigit():
                        item_num = int(item_choice)
                        if 1 <= item_num <= len(equippable):
                            player.equip_item(equippable[item_num - 1]["name"])
                    continue
                    
                elif choice_num == len(valid_actions) + 3:
                    # Show inventory
                    print(f"\n🎒 {player.name}'s Inventory:")
                    if player.inventory:
                        for item in player.inventory:
                            print(f"  - {item['name']} ({item['type']})")
                    else:
                        print("  (empty)")
                    
                    if player.equipped_weapon:
                        print(f"🗡️  Equipped Weapon: {player.equipped_weapon['name']}")
                    if player.equipped_armor:
                        print(f"🛡️  Equipped Armor: {player.equipped_armor['name']}")
                    continue
                else:
                    print("Invalid choice number!")
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
                    print(f"Multiple matches found: {', '.join(matches)}")
                    print("Please be more specific.")
                else:
                    print("Invalid action. Please try again.")
        
        except (ValueError, KeyboardInterrupt):
            print("Invalid input. Please try again.")

def display_welcome_message(player):
    print(f"\n🌟 Welcome back, {player.name}! 🌟")
    print(f"Level {player.level} Adventurer")
    print(f"Health: {player.health}/{player.max_health}")
    print(f"Location: {player.current_location.title()}")
    print("=" * 50)

def main_game_loop():
    while True:
        try:
            current_player = start_menu()
            if current_player:
                display_welcome_message(current_player)
                
                while True:
                    action = get_player_input(current_player.current_location, current_player)
                    
                    if action is None:  # Quit game
                        break
                    
                    new_location = handle_action(current_player.current_location, action, current_player)
                    
                    if new_location is None:  # Quit game
                        break
                    
                    current_player.current_location = new_location
                    
                    # Auto-save every few actions
                    if random.random() < 0.1:  # 10% chance each action
                        save_game(current_player)
        
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Saving progress...")
            if 'current_player' in locals():
                save_game(current_player)
            print("Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            if 'current_player' in locals():
                save_game(current_player)
            print("Game saved due to error.")

# Initialize database with sample data if needed
def initialize_game_data():
    try:
        # Check if we need to populate initial data
        cursor.execute("SELECT COUNT(*) FROM game_items")
        item_count = cursor.fetchone()[0]
        
        if item_count == 0:
            print("Initializing game database...")
            for item in game_items:
                cursor.execute(
                    "INSERT INTO game_items (name, type, value, description) VALUES (%s, %s, %s, %s)", 
                    item
                )
            conn.commit()
            print("Game database initialized!")
    except Exception as e:
        print(f"Error initializing game data: {e}")

# Main execution
if __name__ == "__main__":
    try:
        initialize_game_data()
        print("🎮 Enhanced Adventure Game Starting...")
        print("💡 Tip: You can use numbers or type action names!")
        print("💡 Tip: Type 'check stats' anytime to see your character info!")
        main_game_loop()
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        # Ensure database connection is closed
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

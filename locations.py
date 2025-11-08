import random
from combat import start_combat

# Game locations with actions
LOCATIONS = {
    "village": {
        "text": "🏘️  You are in the peaceful village. The sun shines warmly on the cobblestone streets.",
        "actions": {
            "explore forest": "Venture into the mysterious forest",
            "enter cave": "Explore the dark cave system",
            "enter castle": "Approach the ancient castle",
            "visit shop": "Visit the village shop",
            "rest": "Rest at the inn to restore health (10 gold)",
            "check stats": "Check your character statistics",
            "manage inventory": "View and manage your inventory",
            "quit": "Save and quit the game"
        }
    },
    "forest": {
        "text": "🌲 You are deep in the enchanted forest. Strange sounds echo through the trees.",
        "actions": {
            "return to village": "Return to the safety of the village",
            "explore deeper": "Venture deeper into the forest",
            "search for herbs": "Search for medicinal herbs",
            "hunt animals": "Hunt for food and experience",
            "check stats": "Check your character statistics",
            "manage inventory": "View and manage your inventory",
            "quit": "Save and quit the game"
        }
    },
    "deep_forest": {
        "text": "🌳 You are in the heart of the forest. Ancient magic flows through this place.",
        "actions": {
            "return to forest": "Return to the forest entrance",
            "investigate shrine": "Examine the mysterious shrine",
            "challenge guardian": "Face the forest guardian (BOSS)",
            "check stats": "Check your character statistics",
            "manage inventory": "View and manage your inventory",
            "quit": "Save and quit the game"
        }
    },
    "cave": {
        "text": "🕳️  The cave is dark and damp. You can hear water dripping in the distance.",
        "actions": {
            "return to village": "Return to the village",
            "explore deeper": "Go deeper into the cave system",
            "search for treasure": "Search for hidden treasure",
            "mine crystals": "Mine valuable crystals",
            "check stats": "Check your character statistics",
            "manage inventory": "View and manage your inventory",
            "quit": "Save and quit the game"
        }
    },
    "deep_cave": {
        "text": "⛏️  You are in the deepest part of the cave. Precious gems glitter in the darkness.",
        "actions": {
            "return to cave": "Return to the cave entrance",
            "fight dragon": "Challenge the cave dragon (BOSS)",
            "collect treasure": "Gather the dragon's treasure",
            "check stats": "Check your character statistics",
            "manage inventory": "View and manage your inventory",
            "quit": "Save and quit the game"
        }
    },
    "castle": {
        "text": "🏰 The ancient castle looms before you. Its towers reach toward the cloudy sky.",
        "actions": {
            "return to village": "Return to the village",
            "enter throne room": "Enter the grand throne room",
            "explore library": "Visit the castle library",
            "climb tower": "Climb the highest tower",
            "check stats": "Check your character statistics",
            "manage inventory": "View and manage your inventory",
            "quit": "Save and quit the game"
        }
    },
    "shop": {
        "text": "🏪 Welcome to the village shop! The merchant greets you with a friendly smile.",
        "actions": {
            "buy items": "Purchase items from the merchant",
            "sell items": "Sell items from your inventory",
            "return to village": "Return to the village square",
            "check stats": "Check your character statistics",
            "manage inventory": "View and manage your inventory",
            "quit": "Save and quit the game"
        }
    }
}

# Enemy definitions
ENEMIES = {
    "goblin": {
        "name": "Goblin", 
        "health": 40, 
        "attack": 12, 
        "defense": 3, 
        "exp_reward": 15, 
        "gold_reward": 8
    },
    "wolf": {
        "name": "Wolf", 
        "health": 35, 
        "attack": 15, 
        "defense": 2, 
        "exp_reward": 12, 
        "gold_reward": 5
    },
    "bandit": {
        "name": "Bandit", 
        "health": 50, 
        "attack": 18, 
        "defense": 5, 
        "exp_reward": 20, 
        "gold_reward": 15
    },
    "forest_guardian": {
        "name": "Forest Guardian", 
        "health": 120, 
        "attack": 25, 
        "defense": 8, 
        "exp_reward": 100, 
        "gold_reward": 50
    },
    "cave_dragon": {
        "name": "Cave Dragon", 
        "health": 200, 
        "attack": 35, 
        "defense": 15, 
        "exp_reward": 200, 
        "gold_reward": 100
    },
    "skeleton": {
        "name": "Skeleton Warrior", 
        "health": 45, 
        "attack": 20, 
        "defense": 6, 
        "exp_reward": 25, 
        "gold_reward": 12
    },
    "bear": {
        "name": "Wild Bear",
        "health": 60,
        "attack": 22,
        "defense": 7,
        "exp_reward": 30,
        "gold_reward": 18
    }
}


class LocationHandler:
    def __init__(self, player):
        self.player = player

    def explore_forest(self):
        """Enter the forest with random encounters"""
        print("🌲 You venture into the mysterious forest...")
        
        if random.random() < 0.4:
            enemy_types = ["goblin", "wolf"]
            enemy = random.choice(enemy_types)
            print(f"⚠️  A wild {ENEMIES[enemy]['name']} appears!")
            start_combat(self.player, enemy, ENEMIES)
        
        return "forest"

    def search_herbs(self):
        """Search for healing herbs"""
        print("🌿 You search the forest floor for medicinal herbs...")
        if random.random() < 0.7:
            herb = {"name": "Magic Herb", "type": "consumable", "value": 30, "description": "A mystical herb. Restores 30 health"}
            self.player.add_item(herb)
            self.player.check_quest_completion("herb")
        else:
            print("❌ You couldn't find any herbs this time.")
        return "forest"

    def hunt_animals(self):
        """Hunt for experience and gold"""
        print("🏹 You hunt for small game in the forest...")
        if random.random() < 0.6:
            exp_gain = random.randint(8, 15)
            gold_gain = random.randint(3, 8)
            self.player.gain_experience(exp_gain)
            self.player.gold += gold_gain
            print(f"✅ Successful hunt! You gained {gold_gain} gold.")
        else:
            print("❌ The animals were too quick this time.")
        return "forest"

    def investigate_shrine(self):
        """Investigate the forest shrine"""
        print("⛩️  You approach the ancient shrine...")
        print("The shrine glows with mystical energy.")
        
        if random.random() < 0.5:
            bonus_exp = 25
            self.player.gain_experience(bonus_exp)
            print(f"✨ The shrine blesses you with wisdom!")
        else:
            heal_amount = 20
            old_health = self.player.health
            self.player.health = min(self.player.max_health, self.player.health + heal_amount)
            actual_heal = self.player.health - old_health
            print(f"💚 The shrine's energy heals you for {actual_heal} health!")
        
        return "deep_forest"

    def enter_cave(self):
        """Enter the cave with possible encounters"""
        print("🕳️  You enter the dark, echoing cave...")
        
        if random.random() < 0.3:
            if start_combat(self.player, "skeleton", ENEMIES):
                print("The skeleton crumbles to dust.")
        
        return "cave"

    def search_treasure(self):
        """Search for treasure in the cave"""
        print("💎 You search the cave walls for hidden treasure...")
        if random.random() < 0.6:
            if random.choice([True, False]):
                gold_amount = random.randint(10, 25)
                self.player.gold += gold_amount
                print(f"✨ You found {gold_amount} gold coins!")
            else:
                potion = {"name": "Health Potion", "type": "consumable", "value": 50, "description": "Restores 50 health points"}
                self.player.add_item(potion)
            
            self.player.check_quest_completion("treasure")
        else:
            print("❌ You found nothing of value this time.")
        return "cave"

    def mine_crystals(self):
        """Mine crystals for gold and experience"""
        print("⛏️  You mine the crystal formations...")
        if random.random() < 0.4:
            gold_gain = random.randint(15, 30)
            exp_gain = random.randint(10, 20)
            self.player.gold += gold_gain
            self.player.gain_experience(exp_gain)
            print(f"✅ You successfully mined crystals! Gained {gold_gain} gold.")
        else:
            print("❌ The crystals were too hard to extract.")
        return "cave"

    def collect_dragon_treasure(self):
        """Collect treasure from dragon's hoard"""
        print("💰 You carefully approach the dragon's treasure hoard...")
        if self.player.quests["dragon_slayer"]["completed"]:
            treasure_gold = random.randint(100, 200)
            self.player.gold += treasure_gold
            self.player.score += 500
            legendary_item = {
                "name": "Dragon Scale Armor", 
                "type": "armor", 
                "value": 25,
                "description": "Legendary armor forged from dragon scales. +25 defense"
            }
            self.player.add_item(legendary_item)
            print(f"✨ You collect {treasure_gold} gold and find legendary Dragon Scale Armor!")
        else:
            print("🐉 The sleeping dragon stirs... you dare not approach without defeating it first.")
        return "deep_cave"

    def enter_castle(self):
        """Enter the castle"""
        print("🏰 You approach the ancient castle...")
        print("The massive doors creak open as you near them.")
        return "castle"

    def enter_throne_room(self):
        """Enter the throne room"""
        print("👑 You enter the grand throne room...")
        print("An ancient spirit materializes before the throne!")
        
        if random.random() < 0.7:
            exp_bonus = random.randint(30, 50)
            self.player.gain_experience(exp_bonus)
            print(f"✨ The spirit shares ancient wisdom with you!")
        else:
            if start_combat(self.player, "skeleton", ENEMIES):
                print("The spirit finds peace and vanishes.")
        
        return "castle"

    def explore_library(self):
        """Explore the castle library"""
        print("📚 You explore the vast library...")
        print("Ancient books line the walls from floor to ceiling.")
        
        knowledge_gained = random.randint(20, 40)
        self.player.gain_experience(knowledge_gained)
        print(f"✨ You study ancient texts!")
        
        if random.random() < 0.3:
            rare_book = {
                "name": "Ancient Spell Book", 
                "type": "misc", 
                "value": 100,
                "description": "A rare book containing ancient magical knowledge"
            }
            self.player.add_item(rare_book)
        
        return "castle"

    def climb_tower(self):
        """Climb the castle tower"""
        print("🗼 You climb the winding stairs of the highest tower...")
        print("From the top, you can see the entire realm spread out below you.")
        
        if random.random() < 0.5:
            if random.choice([True, False]):
                gold_found = random.randint(25, 50)
                self.player.gold += gold_found
                print(f"✨ You found a hidden cache with {gold_found} gold coins!")
            else:
                exp_gained = 30
                self.player.gain_experience(exp_gained)
                print(f"✨ The breathtaking view inspires you!")
        
        return "castle"

    def rest_at_inn(self):
        """Rest at the village inn"""
        cost = 10
        if self.player.gold >= cost:
            self.player.gold -= cost
            old_health = self.player.health
            self.player.health = self.player.max_health
            healed = self.player.health - old_health
            print(f"💚 You rest at the inn and restore {healed} health for {cost} gold!")
        else:
            print("❌ You don't have enough gold to rest at the inn (10 gold required).")
        return "village"

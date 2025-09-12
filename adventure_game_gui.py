import sqlite3
import random
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Canvas
import threading
import time
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Optional imports with fallbacks
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Some graphics features will be disabled.")

try:
    import pygame
    pygame.mixer.pre_init()  # Initialize pygame mixer quietly
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: Pygame not available. Audio features will be disabled.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available. Some animation features will be disabled.")

class CombatAction(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    SPECIAL = "special"
    USE_ITEM = "use_item"
    RUN = "run"

@dataclass
class CombatResult:
    player_damage: int
    enemy_damage: int
    player_action: str
    enemy_action: str
    special_effects: List[str]
    combat_ended: bool
    victory: bool

class Database:
    def __init__(self, db_name="adventure.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT UNIQUE, 
            health INTEGER, 
            max_health INTEGER, 
            attack INTEGER, 
            defense INTEGER,
            level INTEGER, 
            experience INTEGER, 
            score INTEGER,
            current_location TEXT,
            inventory TEXT,
            quests TEXT,
            gold INTEGER,
            skills TEXT,
            achievements TEXT
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS game_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            value INTEGER,
            description TEXT,
            rarity TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS locations_visited(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            location TEXT,
            visit_count INTEGER,
            FOREIGN KEY (player_name) REFERENCES players (name)
        )''')
        
        # Initialize game items
        self.init_game_items(cursor)
        conn.commit()
        conn.close()
    
    def init_game_items(self, cursor):
        game_items = [
            ("Health Potion", "consumable", 50, "Restores 50 health points", "common"),
            ("Greater Health Potion", "consumable", 100, "Restores 100 health points", "uncommon"),
            ("Iron Sword", "weapon", 15, "A sturdy iron sword. +15 attack", "common"),
            ("Steel Sword", "weapon", 25, "A sharp steel sword. +25 attack", "uncommon"),
            ("Legendary Blade", "weapon", 50, "A legendary weapon. +50 attack", "legendary"),
            ("Leather Armor", "armor", 8, "Basic leather protection. +8 defense", "common"),
            ("Steel Shield", "armor", 15, "A reliable steel shield. +15 defense", "uncommon"),
            ("Dragon Scale Armor", "armor", 30, "Armor made from dragon scales. +30 defense", "legendary"),
            ("Magic Herb", "consumable", 30, "A mystical herb. Restores 30 health", "common"),
            ("Mana Potion", "consumable", 0, "Restores magical energy for special attacks", "uncommon"),
            ("Ancient Key", "key", 0, "An old key that might unlock something special", "rare"),
            ("Treasure Map", "misc", 0, "Shows the location of hidden treasure", "rare"),
            ("Lucky Charm", "accessory", 0, "Increases critical hit chance", "uncommon")
        ]
        
        cursor.execute("SELECT COUNT(*) FROM game_items")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO game_items (name, type, value, description, rarity) VALUES (?, ?, ?, ?, ?)", 
                game_items
            )

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
        self.equipped_accessory = None
        self.quests = self.get_default_quests()
        self.current_location = "village"
        self.skills = {"critical_chance": 0.1, "dodge_chance": 0.1, "magic_power": 0}
        self.achievements = []
        self.mana = 50
        self.max_mana = 50

    def get_default_quests(self):
        return {
            "first_combat": {"description": "Win your first battle", "completed": False, "reward": 50},
            "herb_collector": {"description": "Collect 5 healing herbs", "progress": 0, "target": 5, "completed": False, "reward": 75},
            "treasure_hunter": {"description": "Find treasure in the cave", "completed": False, "reward": 100},
            "dragon_slayer": {"description": "Defeat the cave dragon", "completed": False, "reward": 300},
            "forest_explorer": {"description": "Explore all forest areas", "completed": False, "reward": 60},
            "master_trader": {"description": "Earn 500 gold through trading", "progress": 0, "target": 500, "completed": False, "reward": 100},
            "legendary_warrior": {"description": "Reach level 10", "completed": False, "reward": 200}
        }

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
        return f"You obtained: {item['name']}"

    def use_item(self, item_name):
        for item in self.inventory:
            if item["name"].lower() == item_name.lower():
                if item["type"] == "consumable":
                    if "Health" in item["name"]:
                        heal_amount = item["value"]
                        old_health = self.health
                        self.health = min(self.max_health, self.health + heal_amount)
                        self.inventory.remove(item)
                        return f"You used {item['name']} and restored {self.health - old_health} health!"
                    elif "Mana" in item["name"]:
                        self.mana = min(self.max_mana, self.mana + 30)
                        self.inventory.remove(item)
                        return f"You used {item['name']} and restored mana!"
                break
        return f"You don't have {item_name} or it can't be used."

    def equip_item(self, item_name):
        for item in self.inventory:
            if item["name"].lower() == item_name.lower():
                if item["type"] == "weapon":
                    if self.equipped_weapon:
                        self.inventory.append(self.equipped_weapon)
                    self.equipped_weapon = item
                    self.inventory.remove(item)
                    return f"You equipped {item['name']}!"
                elif item["type"] == "armor":
                    if self.equipped_armor:
                        self.inventory.append(self.equipped_armor)
                    self.equipped_armor = item
                    self.inventory.remove(item)
                    return f"You equipped {item['name']}!"
                elif item["type"] == "accessory":
                    if self.equipped_accessory:
                        self.inventory.append(self.equipped_accessory)
                    self.equipped_accessory = item
                    self.inventory.remove(item)
                    if "Lucky Charm" in item["name"]:
                        self.skills["critical_chance"] += 0.1
                    return f"You equipped {item['name']}!"
                break
        return f"You don't have {item_name} or it can't be equipped."

    def gain_experience(self, exp):
        self.experience += exp
        exp_needed = self.level * 100
        if self.experience >= exp_needed:
            self.level_up()
        return f"You gained {exp} experience points!"

    def level_up(self):
        self.level += 1
        health_bonus = 20
        attack_bonus = 3
        defense_bonus = 2
        mana_bonus = 10
        
        self.max_health += health_bonus
        self.health = self.max_health
        self.base_attack += attack_bonus
        self.base_defense += defense_bonus
        self.max_mana += mana_bonus
        self.mana = self.max_mana
        
        # Check legendary warrior quest
        if self.level >= 10 and not self.quests["legendary_warrior"]["completed"]:
            self.quests["legendary_warrior"]["completed"] = True
            self.gain_experience(self.quests["legendary_warrior"]["reward"])
        
        return f"LEVEL UP! You are now level {self.level}!\nHealth +{health_bonus}, Attack +{attack_bonus}, Defense +{defense_bonus}, Mana +{mana_bonus}"

    def calculate_combat_damage(self, action: CombatAction, enemy_defense: int) -> Tuple[int, List[str]]:
        effects = []
        base_damage = self.attack
        
        if action == CombatAction.ATTACK:
            # Check for critical hit
            if random.random() < self.skills["critical_chance"]:
                base_damage *= 2
                effects.append("Critical Hit!")
            
            damage = max(1, base_damage - enemy_defense + random.randint(-3, 3))
            
        elif action == CombatAction.SPECIAL:
            if self.mana >= 20:
                self.mana -= 20
                base_damage = int(self.attack * 1.5 + self.skills["magic_power"])
                damage = max(1, base_damage - enemy_defense // 2)
                effects.append("Special Attack!")
            else:
                damage = 0
                effects.append("Not enough mana!")
                
        else:
            damage = 0
            
        return damage, effects

class Enemy:
    def __init__(self, name, health, attack, defense, exp_reward, gold_reward, special_abilities=None):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.special_abilities = special_abilities or []
        self.ai_pattern = random.choice(["aggressive", "defensive", "balanced"])

    def choose_action(self) -> str:
        if self.health < self.max_health * 0.3 and "heal" in self.special_abilities:
            if random.random() < 0.4:
                return "heal"
        
        if self.ai_pattern == "aggressive":
            return random.choice(["attack", "attack", "special"] if self.special_abilities else ["attack", "attack"])
        elif self.ai_pattern == "defensive":
            return random.choice(["attack", "defend", "special"] if self.special_abilities else ["attack", "defend"])
        else:
            return random.choice(["attack", "defend", "special"] if self.special_abilities else ["attack"])

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        return self.health <= 0

# Enhanced locations with more depth and connections
LOCATIONS = {
    "village": {
        "name": "Peaceful Village",
        "description": "You are in the peaceful village. The sun shines warmly on the cobblestone streets. Merchants hawk their wares while children play in the square.",
        "connections": ["forest", "cave", "castle", "mountain_path", "riverside"],
        "special_actions": ["shop", "inn", "tavern", "blacksmith"],
        "encounter_chance": 0.0
    },
    "forest": {
        "name": "Enchanted Forest",
        "description": "You are in the enchanted forest. Ancient trees tower above you, their branches forming a canopy that filters the sunlight into dancing patterns.",
        "connections": ["village", "deep_forest", "forest_clearing", "abandoned_cabin"],
        "special_actions": ["search_herbs", "hunt_animals", "climb_tree"],
        "encounter_chance": 0.3
    },
    "deep_forest": {
        "name": "Heart of the Forest",
        "description": "You are in the heart of the ancient forest. Mystical energy flows through this sacred place, and you can hear the whispers of nature spirits.",
        "connections": ["forest", "forest_shrine", "treehouse_village"],
        "special_actions": ["meditate", "commune_with_spirits"],
        "encounter_chance": 0.4
    },
    "forest_clearing": {
        "name": "Sunlit Clearing",
        "description": "A beautiful clearing where sunlight streams through the canopy. Wildflowers bloom in abundance, and a gentle breeze carries the scent of pine.",
        "connections": ["forest", "hidden_grove"],
        "special_actions": ["pick_flowers", "rest"],
        "encounter_chance": 0.2
    },
    "forest_shrine": {
        "name": "Ancient Forest Shrine",
        "description": "An ancient shrine dedicated to the forest spirits. Moss-covered stones form a circle around a glowing crystal.",
        "connections": ["deep_forest"],
        "special_actions": ["pray", "offer_tribute"],
        "encounter_chance": 0.1
    },
    "cave": {
        "name": "Mysterious Cave",
        "description": "The cave entrance yawns before you like a great mouth. Cool air flows from within, carrying the scent of minerals and mystery.",
        "connections": ["village", "deep_cave", "underground_lake", "crystal_cavern"],
        "special_actions": ["mine_crystals", "search_treasure"],
        "encounter_chance": 0.4
    },
    "deep_cave": {
        "name": "Dragon's Lair",
        "description": "The deepest part of the cave system. Precious gems glitter in the darkness, and the air is thick with the presence of ancient power.",
        "connections": ["cave", "treasure_chamber"],
        "special_actions": ["challenge_dragon", "collect_treasure"],
        "encounter_chance": 0.6
    },
    "castle": {
        "name": "Ancient Castle",
        "description": "The ancient castle looms majestically before you. Its weathered stones tell tales of glory and tragedy from ages past.",
        "connections": ["village", "throne_room", "castle_library", "tower", "dungeon"],
        "special_actions": ["explore_grounds", "seek_audience"],
        "encounter_chance": 0.3
    },
    "mountain_path": {
        "name": "Mountain Path",
        "description": "A winding path leads up the mountainside. The air grows thinner as you climb, and the view becomes more spectacular.",
        "connections": ["village", "mountain_peak", "mountain_cave", "hermit_hut"],
        "special_actions": ["climb_higher", "rest_at_viewpoint"],
        "encounter_chance": 0.3
    },
    "mountain_peak": {
        "name": "Mountain Peak",
        "description": "You stand at the highest point for miles around. The world spreads out below you like a living map.",
        "connections": ["mountain_path", "sky_temple"],
        "special_actions": ["survey_land", "signal_fire"],
        "encounter_chance": 0.2
    },
    "riverside": {
        "name": "Peaceful Riverside",
        "description": "A gentle river flows past, its waters crystal clear. Fish dart between the rocks, and water birds call from the reeds.",
        "connections": ["village", "waterfall", "fishing_village", "old_bridge"],
        "special_actions": ["fish", "swim", "follow_river"],
        "encounter_chance": 0.2
    },
    "fishing_village": {
        "name": "Fishing Village",
        "description": "A small village built on stilts over the water. Fishing boats bob in the harbor, and the smell of fresh fish fills the air.",
        "connections": ["riverside", "harbor", "lighthouse"],
        "special_actions": ["buy_fish", "hire_boat", "talk_to_fishermen"],
        "encounter_chance": 0.1
    }
}

# Enhanced enemy roster
ENEMIES = {
    "goblin": Enemy("Goblin Scout", 40, 12, 3, 15, 8),
    "wolf": Enemy("Gray Wolf", 35, 15, 2, 12, 5),
    "bandit": Enemy("Highway Bandit", 50, 18, 5, 20, 15),
    "orc": Enemy("Orc Warrior", 70, 22, 8, 35, 20),
    "troll": Enemy("Cave Troll", 120, 28, 12, 60, 35, ["regenerate"]),
    "forest_guardian": Enemy("Forest Guardian", 150, 25, 10, 100, 50, ["nature_heal", "entangle"]),
    "cave_dragon": Enemy("Ancient Dragon", 300, 45, 20, 250, 150, ["fire_breath", "wing_attack"]),
    "skeleton": Enemy("Skeleton Warrior", 45, 20, 6, 25, 12),
    "ghost": Enemy("Restless Spirit", 60, 18, 15, 40, 0, ["phase", "drain_life"]),
    "giant_spider": Enemy("Giant Spider", 55, 16, 4, 30, 18, ["web", "poison"]),
    "mountain_bear": Enemy("Mountain Bear", 90, 30, 8, 45, 25, ["charge"]),
    "ice_elemental": Enemy("Ice Elemental", 80, 20, 12, 50, 30, ["freeze", "ice_shard"]),
    "fire_salamander": Enemy("Fire Salamander", 65, 25, 6, 35, 22, ["fire_spit"]),
    "shadow_assassin": Enemy("Shadow Assassin", 50, 35, 8, 60, 40, ["stealth", "poison_blade"])
}

class AnimationEngine:
    def __init__(self, canvas):
        self.canvas = canvas
        self.animations = []
        self.running = True
        
    def add_animation(self, obj_id, start_pos, end_pos, duration=1000, easing="ease_out"):
        animation = {
            'obj_id': obj_id,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'duration': duration,
            'start_time': time.time() * 1000,
            'easing': easing
        }
        self.animations.append(animation)
    
    def update(self):
        if not self.running:
            return
            
        current_time = time.time() * 1000
        completed = []
        
        for i, anim in enumerate(self.animations):
            elapsed = current_time - anim['start_time']
            progress = min(elapsed / anim['duration'], 1.0)
            
            if anim['easing'] == "ease_out":
                progress = 1 - (1 - progress) ** 3
            elif anim['easing'] == "bounce":
                if progress < 0.5:
                    progress = 2 * progress * progress
                else:
                    progress = 1 - 2 * (1 - progress) ** 2
            
            start_x, start_y = anim['start_pos']
            end_x, end_y = anim['end_pos']
            
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            try:
                self.canvas.coords(anim['obj_id'], current_x, current_y)
            except:
                completed.append(i)
                continue
                
            if progress >= 1.0:
                completed.append(i)
        
        for i in reversed(completed):
            self.animations.pop(i)
        
        if self.running:
            self.canvas.after(16, self.update)  # ~60 FPS

class ParticleSystem:
    def __init__(self, canvas):
        self.canvas = canvas
        self.particles = []
        
    def create_explosion(self, x, y, color="#ff6b6b", count=20):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'max_life': 30,
                'color': color,
                'size': random.uniform(2, 6)
            }
            self.particles.append(particle)
    
    def create_healing_effect(self, x, y):
        for _ in range(15):
            particle = {
                'x': x + random.uniform(-20, 20),
                'y': y + random.uniform(-20, 20),
                'vx': 0,
                'vy': random.uniform(-2, -0.5),
                'life': 40,
                'max_life': 40,
                'color': "#27ae60",
                'size': random.uniform(3, 8)
            }
            self.particles.append(particle)
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
            
            alpha = particle['life'] / particle['max_life']
            size = particle['size'] * alpha
            
            if size > 0.5:
                self.canvas.create_oval(
                    particle['x'] - size, particle['y'] - size,
                    particle['x'] + size, particle['y'] + size,
                    fill=particle['color'], outline="", tags="particle"
                )
        
        self.canvas.delete("particle")
        if self.particles:
            self.canvas.after(50, self.update)

class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.create_default_sprites()
    
    def create_default_sprites(self):
        if PIL_AVAILABLE:
            # Create character sprites programmatically
            self.sprites['warrior'] = self.create_character_sprite("#e74c3c", "⚔️")
            self.sprites['mage'] = self.create_character_sprite("#9b59b6", "🔮")
            self.sprites['ranger'] = self.create_character_sprite("#27ae60", "🏹")
            self.sprites['paladin'] = self.create_character_sprite("#f39c12", "🛡️")
            
            # Enemy sprites
            self.sprites['goblin'] = self.create_enemy_sprite("#8e44ad", "👹")
            self.sprites['dragon'] = self.create_enemy_sprite("#c0392b", "🐉")
            self.sprites['wolf'] = self.create_enemy_sprite("#34495e", "�")
            self.sprites['skeleton'] = self.create_enemy_sprite("#95a5a6", "💀")
            
            # Environment sprites
            self.sprites['forest'] = self.create_environment_sprite("#27ae60", "🌲")
            self.sprites['castle'] = self.create_environment_sprite("#7f8c8d", "🏰")
            self.sprites['cave'] = self.create_environment_sprite("#34495e", "🕳️")
            self.sprites['village'] = self.create_environment_sprite("#e67e22", "🏘️")
        else:
            # Fallback: create simple text-based sprites
            self.create_text_sprites()
    
    def create_text_sprites(self):
        """Fallback method when PIL is not available"""
        # Create simple placeholder sprites using text
        for sprite_name in ['warrior', 'mage', 'ranger', 'paladin', 'goblin', 'dragon', 'wolf', 'skeleton']:
            self.sprites[sprite_name] = None  # Will be handled in the UI
    
    def create_character_sprite(self, color, emoji):
        if not PIL_AVAILABLE:
            return None
            
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Body
        draw.ellipse([16, 20, 48, 52], fill=color)
        # Head
        draw.ellipse([20, 8, 44, 32], fill="#fdbcb4")
        # Equipment indicator
        try:
            draw.text((24, 24), emoji, fill="white")
        except:
            # Fallback if emoji rendering fails
            draw.rectangle([24, 24, 40, 40], fill="white")
        
        return ImageTk.PhotoImage(img)
    
    def create_enemy_sprite(self, color, emoji):
        if not PIL_AVAILABLE:
            return None
            
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Body (more menacing)
        draw.ellipse([12, 16, 52, 56], fill=color)
        # Eyes
        draw.ellipse([20, 20, 24, 24], fill="red")
        draw.ellipse([40, 20, 44, 24], fill="red")
        # Emoji overlay
        try:
            draw.text((20, 28), emoji, fill="white")
        except:
            # Fallback if emoji rendering fails
            draw.rectangle([20, 28, 44, 44], fill="white")
        
        return ImageTk.PhotoImage(img)
    
    def create_environment_sprite(self, color, emoji):
        if not PIL_AVAILABLE:
            return None
            
        img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background (without alpha for better compatibility)
        draw.rectangle([0, 0, 128, 128], fill=color)
        
        # Border
        draw.rectangle([0, 0, 128, 128], outline=color, width=3)
        # Icon
        try:
            draw.text((40, 50), emoji, fill=color)
        except:
            # Fallback if emoji rendering fails
            draw.rectangle([40, 50, 88, 78], fill=color)
        
        return ImageTk.PhotoImage(img)

class ModernUI:
    @staticmethod
    def create_gradient_frame(parent, width, height, color1="#2c3e50", color2="#34495e"):
        canvas = Canvas(parent, width=width, height=height, highlightthickness=0)
        
        # Create gradient effect
        for i in range(height):
            ratio = i / height
            r1, g1, b1 = ModernUI.hex_to_rgb(color1)
            r2, g2, b2 = ModernUI.hex_to_rgb(color2)
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, fill=color, width=1)
        
        return canvas
    
    @staticmethod
    def hex_to_rgb(hex_color):
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            # Fallback to white if color parsing fails
            return (255, 255, 255)
    
    @staticmethod
    def create_modern_button(parent, text, command, bg_color="#3498db", hover_color="#2980b9", 
                           text_color="white", width=200, height=50):
        frame = tk.Frame(parent, bg=parent['bg'] if hasattr(parent, '__getitem__') else "#2c3e50")
        
        canvas = Canvas(frame, width=width, height=height, highlightthickness=0, bg=bg_color)
        canvas.pack()
        
        # Rounded rectangle effect
        canvas.create_rectangle(5, 5, width-5, height-5, fill=bg_color, outline="", width=0)
        canvas.create_text(width//2, height//2, text=text, fill=text_color, 
                          font=("Arial", 12, "bold"))
        
        def on_enter(e):
            canvas.configure(bg=hover_color)
            canvas.delete("all")
            canvas.create_rectangle(5, 5, width-5, height-5, fill=hover_color, outline="", width=0)
            canvas.create_text(width//2, height//2, text=text, fill=text_color, 
                              font=("Arial", 12, "bold"))
        
        def on_leave(e):
            canvas.configure(bg=bg_color)
            canvas.delete("all")
            canvas.create_rectangle(5, 5, width-5, height-5, fill=bg_color, outline="", width=0)
            canvas.create_text(width//2, height//2, text=text, fill=text_color, 
                              font=("Arial", 12, "bold"))
        
        canvas.bind("<Button-1>", lambda e: command())
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        
        return frame

class AdventureGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏰 Epic Adventure Quest - Modern Edition")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        # Initialize systems
        self.db = Database()
        self.current_player = None
        self.current_enemy = None
        self.combat_active = False
        self.sprite_manager = SpriteManager()
        
        # Animation and effects
        self.animation_engine = None
        self.particle_system = None
        
        # UI State
        self.current_screen = "main_menu"
        self.ui_animations = []
        
        self.setup_modern_styles()
        self.create_main_menu()
    
    def setup_modern_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Modern color palette
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#1a1a1a',
            'gradient_start': '#667eea',
            'gradient_end': '#764ba2'
        }
        
        # Configure modern styles
        self.style.configure('Modern.TLabel', 
                           font=('Segoe UI', 12), 
                           background=self.colors['primary'], 
                           foreground=self.colors['light'])
        
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 24, 'bold'), 
                           background=self.colors['dark'], 
                           foreground=self.colors['light'])
        
        self.style.configure('Subtitle.TLabel', 
                           font=('Segoe UI', 14), 
                           background=self.colors['dark'], 
                           foreground=self.colors['accent'])
        
        self.style.configure('Modern.TProgressbar',
                           background=self.colors['success'],
                           troughcolor=self.colors['secondary'],
                           borderwidth=0,
                           lightcolor=self.colors['success'],
                           darkcolor=self.colors['success'])
        
        # Configure modern button styles
        self.style.configure('Modern.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(20, 10),
                           background=self.colors['accent'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Modern.TButton',
                     background=[('active', self.colors['gradient_start']),
                               ('pressed', self.colors['gradient_end'])])
    
    def create_main_menu(self):
        self.clear_window()
        self.current_screen = "main_menu"
        
        # Create main canvas for background effects
        self.main_canvas = Canvas(self.root, width=1400, height=900, bg=self.colors['dark'], highlightthickness=0)
        self.main_canvas.pack(fill='both', expand=True)
        
        # Animated background
        self.create_animated_background()
        
        # Title with glow effect
        title_frame = tk.Frame(self.main_canvas, bg=self.colors['dark'])
        title_window = self.main_canvas.create_window(700, 200, window=title_frame)
        
        # Main title with gradient effect
        title_canvas = Canvas(title_frame, width=800, height=120, bg=self.colors['dark'], highlightthickness=0)
        title_canvas.pack()
        
        # Create gradient text effect
        self.create_gradient_text(title_canvas, 400, 40, "🏰 EPIC ADVENTURE QUEST 🏰", 
                                 font_size=28, gradient_colors=['#667eea', '#764ba2', '#f093fb'])
        
        subtitle_canvas = Canvas(title_frame, width=600, height=60, bg=self.colors['dark'], highlightthickness=0)
        subtitle_canvas.pack()
        
        self.create_gradient_text(subtitle_canvas, 300, 30, "✨ Embark on a Legendary Journey ✨", 
                                 font_size=16, gradient_colors=['#ffecd2', '#fcb69f'])
        
        # Modern menu buttons with animations
        button_frame = tk.Frame(self.main_canvas, bg=self.colors['dark'])
        button_window = self.main_canvas.create_window(700, 500, window=button_frame)
        
        buttons = [
            ("🆕 Start New Adventure", self.create_character, "#27ae60", "#2ecc71"),
            ("📁 Continue Journey", self.load_game_menu, "#3498db", "#5dade2"),
            ("👤 Hero Management", self.manage_profiles, "#9b59b6", "#bb8fce"),
            ("⚙️ Settings", self.show_settings, "#f39c12", "#f7dc6f"),
            ("❌ Exit Realm", self.root.quit, "#e74c3c", "#ec7063")
        ]
        
        self.menu_buttons = []
        for i, (text, command, bg_color, hover_color) in enumerate(buttons):
            btn_frame = ModernUI.create_modern_button(
                button_frame, text, command, bg_color, hover_color, width=300, height=60
            )
            btn_frame.pack(pady=15)
            self.menu_buttons.append(btn_frame)
            
            # Add entrance animation
            self.animate_button_entrance(btn_frame, i * 100)
        
        # Add floating particles
        self.create_floating_particles()
        
        # Start background animation loop (disabled for stability)
        # self.animate_background()
    
    def create_animated_background(self):
        # Create animated stars/particles in background
        self.bg_particles = []
        for _ in range(50):
            x = random.randint(0, 1400)
            y = random.randint(0, 900)
            size = random.randint(1, 3)
            speed = random.uniform(0.1, 0.5)
            
            particle_id = self.main_canvas.create_oval(
                x, y, x + size, y + size,
                fill="#ffffff", outline="", tags="bg_particle"
            )
            
            self.bg_particles.append({
                'id': particle_id,
                'x': x, 'y': y, 'size': size, 'speed': speed,
                'alpha': random.uniform(0.3, 1.0)
            })
    
    def create_gradient_text(self, canvas, x, y, text, font_size=20, gradient_colors=None):
        if gradient_colors is None:
            gradient_colors = ['#667eea', '#764ba2']
        
        # Create text with gradient effect (simplified)
        canvas.create_text(x, y, text=text, fill=gradient_colors[0], 
                          font=('Segoe UI', font_size, 'bold'), anchor='center')
        
        # Add glow effect (without alpha channel for tkinter compatibility)
        glow_color = gradient_colors[-1] if len(gradient_colors) > 1 else gradient_colors[0]
        for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
            canvas.create_text(x + offset[0], y + offset[1], text=text, 
                              fill=glow_color, 
                              font=('Segoe UI', font_size, 'bold'), anchor='center')
    
    def animate_button_entrance(self, button, delay):
        # Start buttons off-screen and animate them in
        button.place(x=-300, y=100 + len(self.menu_buttons) * 80)
        
        def animate_in():
            target_x = 550
            current_x = -300
            
            def move_step():
                nonlocal current_x
                current_x += (target_x - current_x) * 0.15
                button.place(x=current_x)
                
                if abs(target_x - current_x) > 1:
                    self.root.after(16, move_step)
                else:
                    button.place(x=target_x)
            
            move_step()
        
        self.root.after(delay, animate_in)
    
    def create_floating_particles(self):
        self.floating_particles = []
        for _ in range(20):
            x = random.randint(0, 1400)
            y = random.randint(0, 900)
            
            particle = self.main_canvas.create_text(
                x, y, text=random.choice(['✨', '⭐', '🌟', '💫']),
                fill=random.choice(['#ffd700', '#ff69b4', '#00ffff', '#ff6347']),
                font=('Arial', random.randint(12, 20))
            )
            
            self.floating_particles.append({
                'id': particle,
                'x': x, 'y': y,
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5)
            })
    
    def animate_background(self):
        if self.current_screen != "main_menu" or not hasattr(self, 'main_canvas'):
            return
        
        try:
            # Animate background particles
            if hasattr(self, 'bg_particles'):
                for particle in self.bg_particles:
                    particle['y'] += particle['speed']
                    if particle['y'] > 900:
                        particle['y'] = -10
                        particle['x'] = random.randint(0, 1400)
                    
                    try:
                        self.main_canvas.coords(particle['id'], 
                                               particle['x'], particle['y'],
                                               particle['x'] + particle['size'], 
                                               particle['y'] + particle['size'])
                    except:
                        continue
            
            # Animate floating particles
            if hasattr(self, 'floating_particles'):
                for particle in self.floating_particles:
                    particle['x'] += particle['vx']
                    particle['y'] += particle['vy']
                    
                    # Bounce off edges
                    if particle['x'] <= 0 or particle['x'] >= 1400:
                        particle['vx'] *= -1
                    if particle['y'] <= 0 or particle['y'] >= 900:
                        particle['vy'] *= -1
                    
                    try:
                        self.main_canvas.coords(particle['id'], particle['x'], particle['y'])
                    except:
                        continue
            
            # Continue animation
            if self.current_screen == "main_menu":
                self.root.after(50, self.animate_background)
                
        except Exception as e:
            # If animation fails, just stop it
            pass
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Game Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg=self.colors['dark'])
        settings_window.grab_set()
        
        # Settings content
        title_label = tk.Label(settings_window, text="⚙️ Game Settings", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=self.colors['dark'], fg=self.colors['light'])
        title_label.pack(pady=20)
        
        # Volume control
        volume_frame = tk.Frame(settings_window, bg=self.colors['dark'])
        volume_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(volume_frame, text="🔊 Sound Volume:", 
                font=('Segoe UI', 12), bg=self.colors['dark'], fg=self.colors['light']).pack(anchor='w')
        
        volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient='horizontal',
                               bg=self.colors['secondary'], fg=self.colors['light'],
                               highlightthickness=0, troughcolor=self.colors['primary'])
        volume_scale.set(75)
        volume_scale.pack(fill='x', pady=5)
        
        # Graphics quality
        graphics_frame = tk.Frame(settings_window, bg=self.colors['dark'])
        graphics_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(graphics_frame, text="🎨 Graphics Quality:", 
                font=('Segoe UI', 12), bg=self.colors['dark'], fg=self.colors['light']).pack(anchor='w')
        
        quality_var = tk.StringVar(value="High")
        for quality in ["Low", "Medium", "High", "Ultra"]:
            tk.Radiobutton(graphics_frame, text=quality, variable=quality_var, value=quality,
                          bg=self.colors['dark'], fg=self.colors['light'], 
                          selectcolor=self.colors['accent']).pack(anchor='w')
        
        # Close button
        close_btn = ModernUI.create_modern_button(
            settings_window, "Close", settings_window.destroy,
            self.colors['danger'], "#c0392b", width=150, height=40
        )
        close_btn.pack(pady=20)    
  
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_character(self):
        self.clear_window()
        
        # Character creation frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="Create Your Character", 
                              font=('Arial', 18, 'bold'), bg='#2c3e50', fg='#e74c3c')
        title_label.pack(pady=20)
        
        # Name input
        name_frame = tk.Frame(main_frame, bg='#2c3e50')
        name_frame.pack(pady=10)
        
        tk.Label(name_frame, text="Character Name:", font=('Arial', 12), 
                bg='#2c3e50', fg='#ecf0f1').pack(side='left')
        
        self.name_entry = tk.Entry(name_frame, font=('Arial', 12), width=20)
        self.name_entry.pack(side='left', padx=10)
        self.name_entry.focus()
        
        # Character class selection
        class_frame = tk.Frame(main_frame, bg='#2c3e50')
        class_frame.pack(pady=20)
        
        tk.Label(class_frame, text="Choose Your Class:", font=('Arial', 12, 'bold'), 
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.character_class = tk.StringVar(value="warrior")
        
        classes = [
            ("⚔️ Warrior", "warrior", "High attack and defense, moderate health"),
            ("🏹 Ranger", "ranger", "Balanced stats with high critical chance"),
            ("🔮 Mage", "mage", "High mana and magic power, lower physical stats"),
            ("🛡️ Paladin", "paladin", "High defense and health, healing abilities")
        ]
        
        for name, value, description in classes:
            frame = tk.Frame(class_frame, bg='#34495e', relief='raised', bd=2)
            frame.pack(fill='x', pady=5, padx=20)
            
            radio = tk.Radiobutton(frame, text=name, variable=self.character_class, value=value,
                                  font=('Arial', 11, 'bold'), bg='#34495e', fg='#ecf0f1',
                                  selectcolor='#3498db', activebackground='#34495e')
            radio.pack(anchor='w', padx=10, pady=5)
            
            desc_label = tk.Label(frame, text=description, font=('Arial', 9), 
                                 bg='#34495e', fg='#bdc3c7')
            desc_label.pack(anchor='w', padx=30, pady=(0, 5))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(pady=30)
        
        create_btn = tk.Button(button_frame, text="Create Character", command=self.start_new_game,
                              font=('Arial', 12, 'bold'), bg='#27ae60', fg='white', 
                              width=15, height=2)
        create_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="Back", command=self.create_main_menu,
                            font=('Arial', 12), bg='#95a5a6', fg='white', width=10, height=2)
        back_btn.pack(side='left', padx=10)
    
    def start_new_game(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a character name!")
            return
        
        # Check if name already exists
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM players WHERE name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            messagebox.showerror("Error", "Character name already exists!")
            return
        conn.close()
        
        # Create player based on class
        char_class = self.character_class.get()
        if char_class == "warrior":
            self.current_player = Player(name, health=120, attack=25, defense=8, gold=75)
        elif char_class == "ranger":
            self.current_player = Player(name, health=100, attack=22, defense=6, gold=60)
            self.current_player.skills["critical_chance"] = 0.2
            self.current_player.skills["dodge_chance"] = 0.15
        elif char_class == "mage":
            self.current_player = Player(name, health=80, attack=15, defense=4, gold=50)
            self.current_player.max_mana = 100
            self.current_player.mana = 100
            self.current_player.skills["magic_power"] = 20
        elif char_class == "paladin":
            self.current_player = Player(name, health=140, attack=20, defense=12, gold=80)
            self.current_player.skills["healing_power"] = 1.5
        
        # Add starting items based on class
        starting_items = {
            "warrior": [{"name": "Iron Sword", "type": "weapon", "value": 15}, 
                       {"name": "Leather Armor", "type": "armor", "value": 8}],
            "ranger": [{"name": "Hunter's Bow", "type": "weapon", "value": 18}, 
                      {"name": "Lucky Charm", "type": "accessory", "value": 0}],
            "mage": [{"name": "Magic Staff", "type": "weapon", "value": 12}, 
                    {"name": "Mana Potion", "type": "consumable", "value": 0}],
            "paladin": [{"name": "Holy Sword", "type": "weapon", "value": 20}, 
                       {"name": "Steel Shield", "type": "armor", "value": 15}]
        }
        
        for item in starting_items.get(char_class, []):
            self.current_player.inventory.append(item)
        
        self.save_game()
        self.create_game_interface()
    
    def load_game_menu(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, level, score FROM players ORDER BY level DESC, score DESC")
        profiles = cursor.fetchall()
        conn.close()
        
        if not profiles:
            messagebox.showinfo("No Saves", "No saved games found!")
            return
        
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="Load Game", font=('Arial', 18, 'bold'), 
                              bg='#2c3e50', fg='#e74c3c')
        title_label.pack(pady=20)
        
        # Profiles list
        list_frame = tk.Frame(main_frame, bg='#34495e', relief='sunken', bd=2)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.profile_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                         font=('Arial', 11), bg='#ecf0f1', fg='#2c3e50',
                                         selectbackground='#3498db')
        self.profile_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.profile_listbox.yview)
        
        for name, level, score in profiles:
            self.profile_listbox.insert('end', f"{name} - Level {level} - Score: {score}")
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        load_btn = tk.Button(button_frame, text="Load Selected", command=self.load_selected_game,
                            font=('Arial', 12, 'bold'), bg='#27ae60', fg='white', width=15, height=2)
        load_btn.pack(side='left', padx=10)
        
        delete_btn = tk.Button(button_frame, text="Delete Selected", command=self.delete_selected_profile,
                              font=('Arial', 12), bg='#e74c3c', fg='white', width=15, height=2)
        delete_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="Back", command=self.create_main_menu,
                            font=('Arial', 12), bg='#95a5a6', fg='white', width=10, height=2)
        back_btn.pack(side='left', padx=10)
    
    def load_selected_game(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a profile to load!")
            return
        
        profile_text = self.profile_listbox.get(selection[0])
        name = profile_text.split(' - ')[0]
        
        self.current_player = self.load_player(name)
        if self.current_player:
            self.create_game_interface()
        else:
            messagebox.showerror("Error", "Failed to load the selected profile!")
    
    def delete_selected_profile(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a profile to delete!")
            return
        
        profile_text = self.profile_listbox.get(selection[0])
        name = profile_text.split(' - ')[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players WHERE name = ?", (name,))
            cursor.execute("DELETE FROM locations_visited WHERE player_name = ?", (name,))
            conn.commit()
            conn.close()
            
            self.load_game_menu()  # Refresh the list
    
    def manage_profiles(self):
        # For now, just redirect to load game menu
        self.load_game_menu()
    
    def create_game_interface(self):
        self.clear_window()
        self.current_screen = "game"
        
        # Create main game canvas
        self.game_canvas = Canvas(self.root, width=1400, height=900, bg=self.colors['dark'], highlightthickness=0)
        self.game_canvas.pack(fill='both', expand=True)
        
        # Initialize animation systems
        self.animation_engine = AnimationEngine(self.game_canvas)
        self.particle_system = ParticleSystem(self.game_canvas)
        
        # Create modern game layout
        self.create_modern_hud()
        self.create_3d_world_view()
        self.create_modern_sidebar()
        
        # Start animation loops
        self.animation_engine.update()
        self.particle_system.update()
        
        # Update the display
        self.update_display()
    
    def create_modern_hud(self):
        # Top HUD bar with glass morphism effect
        hud_frame = tk.Frame(self.game_canvas, bg=self.colors['dark'])
        hud_window = self.game_canvas.create_window(700, 60, window=hud_frame, width=1380, height=120)
        
        # Player avatar and info
        avatar_frame = tk.Frame(hud_frame, bg=self.colors['secondary'], relief='raised', bd=2)
        avatar_frame.pack(side='left', padx=10, pady=10, fill='y')
        
        # Character portrait with animation
        portrait_canvas = Canvas(avatar_frame, width=80, height=80, bg=self.colors['primary'], highlightthickness=0)
        portrait_canvas.pack(padx=10, pady=5)
        
        # Add character sprite
        char_class = getattr(self.current_player, 'character_class', 'warrior')
        if char_class in self.sprite_manager.sprites and self.sprite_manager.sprites[char_class]:
            portrait_canvas.create_image(40, 40, image=self.sprite_manager.sprites[char_class])
        else:
            # Fallback: draw character emoji
            portrait_canvas.create_text(40, 40, text="⚔️", font=('Arial', 24), fill="white")
        
        # Player name with glow effect
        name_label = tk.Label(avatar_frame, text=f"⚔️ {self.current_player.name}", 
                             font=('Segoe UI', 14, 'bold'), bg=self.colors['secondary'], fg=self.colors['light'])
        name_label.pack()
        
        level_label = tk.Label(avatar_frame, text=f"Level {self.current_player.level}", 
                              font=('Segoe UI', 10), bg=self.colors['secondary'], fg=self.colors['accent'])
        level_label.pack()
        
        # Modern status bars
        stats_frame = tk.Frame(hud_frame, bg=self.colors['secondary'])
        stats_frame.pack(side='left', padx=20, pady=10, fill='both', expand=True)
        
        # Health bar with gradient
        health_frame = tk.Frame(stats_frame, bg=self.colors['secondary'])
        health_frame.pack(fill='x', pady=5)
        
        tk.Label(health_frame, text="❤️ Health", font=('Segoe UI', 10, 'bold'), 
                bg=self.colors['secondary'], fg='#e74c3c').pack(anchor='w')
        
        self.health_canvas = Canvas(health_frame, width=300, height=20, bg=self.colors['primary'], highlightthickness=0)
        self.health_canvas.pack(fill='x', pady=2)
        
        # Mana bar with gradient
        mana_frame = tk.Frame(stats_frame, bg=self.colors['secondary'])
        mana_frame.pack(fill='x', pady=5)
        
        tk.Label(mana_frame, text="🔮 Mana", font=('Segoe UI', 10, 'bold'), 
                bg=self.colors['secondary'], fg='#3498db').pack(anchor='w')
        
        self.mana_canvas = Canvas(mana_frame, width=300, height=20, bg=self.colors['primary'], highlightthickness=0)
        self.mana_canvas.pack(fill='x', pady=2)
        
        # Experience bar
        exp_frame = tk.Frame(stats_frame, bg=self.colors['secondary'])
        exp_frame.pack(fill='x', pady=5)
        
        tk.Label(exp_frame, text="⭐ Experience", font=('Segoe UI', 10, 'bold'), 
                bg=self.colors['secondary'], fg='#f39c12').pack(anchor='w')
        
        self.exp_canvas = Canvas(exp_frame, width=300, height=15, bg=self.colors['primary'], highlightthickness=0)
        self.exp_canvas.pack(fill='x', pady=2)
        
        # Resources display
        resources_frame = tk.Frame(hud_frame, bg=self.colors['secondary'])
        resources_frame.pack(side='right', padx=10, pady=10)
        
        self.gold_label = tk.Label(resources_frame, text=f"💰 {self.current_player.gold}", 
                                  font=('Segoe UI', 12, 'bold'), bg=self.colors['secondary'], fg='#f1c40f')
        self.gold_label.pack(pady=5)
        
        self.score_label = tk.Label(resources_frame, text=f"🏆 {self.current_player.score}", 
                                   font=('Segoe UI', 11), bg=self.colors['secondary'], fg=self.colors['light'])
        self.score_label.pack(pady=2)
        
        # Store references
        self.hud_frame = hud_frame
        self.portrait_canvas = portrait_canvas
    
    def create_3d_world_view(self):
        # Main world view with 3D-like perspective
        world_frame = tk.Frame(self.game_canvas, bg=self.colors['primary'])
        world_window = self.game_canvas.create_window(500, 450, window=world_frame, width=900, height=600)
        
        # World canvas for location rendering
        self.world_canvas = Canvas(world_frame, width=880, height=580, bg='#1e3a8a', highlightthickness=0)
        self.world_canvas.pack(padx=10, pady=10)
        
        # Create location background
        self.render_current_location()
        
        # Character sprite in world
        warrior_sprite = self.sprite_manager.sprites.get('warrior')
        if warrior_sprite:
            self.player_sprite_id = self.world_canvas.create_image(440, 400, image=warrior_sprite)
        else:
            # Fallback: create text-based character
            self.player_sprite_id = self.world_canvas.create_text(440, 400, text="🧙‍♂️", 
                                                                 font=('Arial', 32), fill="white")
        
        # Add breathing animation to character (disabled for stability)
        # self.animate_character_idle()
        
        # Location title overlay
        location_overlay = tk.Frame(world_frame, bg=self.colors['dark'] + "AA")
        location_overlay.place(x=20, y=20, width=300, height=60)
        
        self.location_title = tk.Label(location_overlay, text="", font=('Segoe UI', 16, 'bold'), 
                                      bg=self.colors['dark'] + "AA", fg=self.colors['light'])
        self.location_title.pack(expand=True)
        
        # Adventure log with modern styling
        log_frame = tk.Frame(world_frame, bg=self.colors['secondary'])
        log_frame.place(x=20, y=480, width=860, height=90)
        
        tk.Label(log_frame, text="📜 Adventure Log", font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['secondary'], fg=self.colors['light']).pack(anchor='w', padx=10, pady=5)
        
        self.game_log = scrolledtext.ScrolledText(log_frame, height=3, font=('Consolas', 10),
                                                 bg=self.colors['dark'], fg=self.colors['light'], 
                                                 wrap='word', relief='flat', bd=0)
        self.game_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Add welcome message with typewriter effect
        self.typewriter_text(f"Welcome, {self.current_player.name}! Your epic adventure begins...")
    
    def create_modern_sidebar(self):
        # Right sidebar with actions and inventory
        sidebar_frame = tk.Frame(self.game_canvas, bg=self.colors['secondary'])
        sidebar_window = self.game_canvas.create_window(1150, 450, window=sidebar_frame, width=400, height=600)
        
        # Movement section with map-like interface
        movement_section = tk.LabelFrame(sidebar_frame, text="🗺️ Travel", font=('Segoe UI', 12, 'bold'),
                                        bg=self.colors['secondary'], fg=self.colors['light'], bd=2)
        movement_section.pack(fill='x', padx=10, pady=10)
        
        # Mini-map canvas
        self.minimap_canvas = Canvas(movement_section, width=360, height=120, 
                                    bg=self.colors['primary'], highlightthickness=0)
        self.minimap_canvas.pack(padx=10, pady=10)
        
        self.create_minimap()
        
        # Action buttons with modern styling
        actions_section = tk.LabelFrame(sidebar_frame, text="⚡ Actions", font=('Segoe UI', 12, 'bold'),
                                       bg=self.colors['secondary'], fg=self.colors['light'], bd=2)
        actions_section.pack(fill='x', padx=10, pady=10)
        
        self.action_buttons_frame = tk.Frame(actions_section, bg=self.colors['secondary'])
        self.action_buttons_frame.pack(fill='x', padx=10, pady=10)
        
        # Inventory with drag-and-drop styling
        inventory_section = tk.LabelFrame(sidebar_frame, text="🎒 Inventory", font=('Segoe UI', 12, 'bold'),
                                         bg=self.colors['secondary'], fg=self.colors['light'], bd=2)
        inventory_section.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Inventory grid
        self.inventory_canvas = Canvas(inventory_section, width=360, height=200, 
                                      bg=self.colors['primary'], highlightthickness=0)
        self.inventory_canvas.pack(padx=10, pady=10)
        
        # Inventory action buttons
        inv_actions = tk.Frame(inventory_section, bg=self.colors['secondary'])
        inv_actions.pack(fill='x', padx=10, pady=(0, 10))
        
        use_btn = ModernUI.create_modern_button(inv_actions, "Use Item", self.use_selected_item,
                                               self.colors['success'], "#2ecc71", width=110, height=35)
        use_btn.pack(side='left', padx=5)
        
        equip_btn = ModernUI.create_modern_button(inv_actions, "Equip", self.equip_selected_item,
                                                 self.colors['accent'], "#5dade2", width=110, height=35)
        equip_btn.pack(side='left', padx=5)
        
        drop_btn = ModernUI.create_modern_button(inv_actions, "Drop", self.drop_selected_item,
                                                self.colors['warning'], "#f7dc6f", width=110, height=35)
        drop_btn.pack(side='left', padx=5)
        
        # Menu buttons
        menu_section = tk.Frame(sidebar_frame, bg=self.colors['secondary'])
        menu_section.pack(fill='x', padx=10, pady=10)
        
        menu_buttons = [
            ("💾 Save Game", self.save_game, self.colors['success']),
            ("📊 Character Stats", self.show_character_stats, self.colors['accent']),
            ("⚙️ Settings", self.show_settings, self.colors['warning']),
            ("🚪 Main Menu", self.return_to_main_menu, self.colors['danger'])
        ]
        
        for text, command, color in menu_buttons:
            btn = ModernUI.create_modern_button(menu_section, text, command, color, width=360, height=40)
            btn.pack(pady=3)
    
    def render_current_location(self):
        self.world_canvas.delete("location_bg")
        
        location_key = self.current_player.current_location
        location = LOCATIONS.get(location_key, {})
        
        # Create location-specific background
        if location_key == "village":
            self.render_village_scene()
        elif location_key == "forest":
            self.render_forest_scene()
        elif location_key == "cave":
            self.render_cave_scene()
        elif location_key == "castle":
            self.render_castle_scene()
        else:
            self.render_generic_scene(location_key)
    
    def render_village_scene(self):
        # Sky gradient
        for i in range(200):
            color_ratio = i / 200
            r = int(135 + (255 - 135) * color_ratio)
            g = int(206 + (255 - 206) * color_ratio)
            b = int(235 + (255 - 235) * color_ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.world_canvas.create_line(0, i, 880, i, fill=color, tags="location_bg")
        
        # Ground
        self.world_canvas.create_rectangle(0, 400, 880, 580, fill="#8FBC8F", tags="location_bg")
        
        # Buildings
        buildings = [(100, 250, 200, 400), (300, 200, 450, 400), (600, 220, 750, 400)]
        for x1, y1, x2, y2 in buildings:
            self.world_canvas.create_rectangle(x1, y1, x2, y2, fill="#D2B48C", outline="#8B7355", width=2, tags="location_bg")
            # Roof
            self.world_canvas.create_polygon(x1-10, y1, (x1+x2)//2, y1-50, x2+10, y1, fill="#8B4513", tags="location_bg")
        
        # Add some details
        self.world_canvas.create_text(440, 450, text="🏘️ Peaceful Village", font=('Segoe UI', 16, 'bold'), 
                                     fill="#2c3e50", tags="location_bg")
    
    def render_forest_scene(self):
        # Forest background
        self.world_canvas.create_rectangle(0, 0, 880, 580, fill="#228B22", tags="location_bg")
        
        # Trees
        for _ in range(15):
            x = random.randint(50, 830)
            y = random.randint(200, 500)
            self.world_canvas.create_oval(x-30, y-60, x+30, y, fill="#006400", tags="location_bg")
            self.world_canvas.create_rectangle(x-5, y, x+5, y+40, fill="#8B4513", tags="location_bg")
        
        # Path
        self.world_canvas.create_oval(300, 350, 580, 450, fill="#DEB887", tags="location_bg")
        
        self.world_canvas.create_text(440, 100, text="🌲 Enchanted Forest", font=('Segoe UI', 16, 'bold'), 
                                     fill="#FFFFFF", tags="location_bg")
    
    def render_cave_scene(self):
        # Cave background
        self.world_canvas.create_rectangle(0, 0, 880, 580, fill="#2F4F4F", tags="location_bg")
        
        # Cave walls
        self.world_canvas.create_arc(0, 100, 880, 600, start=0, extent=180, fill="#1C1C1C", tags="location_bg")
        
        # Stalactites
        for i in range(0, 880, 100):
            self.world_canvas.create_polygon(i+50, 0, i+30, 80, i+70, 80, fill="#696969", tags="location_bg")
        
        # Crystals
        for _ in range(8):
            x = random.randint(100, 780)
            y = random.randint(400, 550)
            self.world_canvas.create_polygon(x, y-20, x-10, y, x+10, y, fill="#9370DB", tags="location_bg")
        
        self.world_canvas.create_text(440, 300, text="🕳️ Mysterious Cave", font=('Segoe UI', 16, 'bold'), 
                                     fill="#FFFFFF", tags="location_bg")
    
    def render_castle_scene(self):
        # Castle background
        self.world_canvas.create_rectangle(0, 0, 880, 580, fill="#4682B4", tags="location_bg")
        
        # Castle structure
        self.world_canvas.create_rectangle(200, 150, 680, 450, fill="#708090", tags="location_bg")
        
        # Towers
        towers = [(180, 100, 220, 450), (660, 100, 700, 450), (420, 80, 460, 450)]
        for x1, y1, x2, y2 in towers:
            self.world_canvas.create_rectangle(x1, y1, x2, y2, fill="#696969", tags="location_bg")
            # Tower tops
            self.world_canvas.create_polygon(x1-5, y1, (x1+x2)//2, y1-30, x2+5, y1, fill="#2F4F4F", tags="location_bg")
        
        # Gate
        self.world_canvas.create_rectangle(420, 350, 460, 450, fill="#8B4513", tags="location_bg")
        
        self.world_canvas.create_text(440, 500, text="🏰 Ancient Castle", font=('Segoe UI', 16, 'bold'), 
                                     fill="#FFFFFF", tags="location_bg")
    
    def render_generic_scene(self, location_key):
        # Generic background based on location type
        colors = {
            'mountain_path': '#8B7355',
            'riverside': '#4682B4',
            'deep_forest': '#006400',
            'deep_cave': '#1C1C1C'
        }
        
        bg_color = colors.get(location_key, '#2F4F4F')
        self.world_canvas.create_rectangle(0, 0, 880, 580, fill=bg_color, tags="location_bg")
        
        location_name = LOCATIONS.get(location_key, {}).get('name', 'Unknown Location')
        self.world_canvas.create_text(440, 290, text=location_name, font=('Segoe UI', 16, 'bold'), 
                                     fill="#FFFFFF", tags="location_bg")
    
    def create_minimap(self):
        self.minimap_canvas.delete("all")
        
        # Draw minimap background
        self.minimap_canvas.create_rectangle(0, 0, 360, 120, fill=self.colors['primary'], outline=self.colors['light'])
        
        # Draw location nodes
        locations_pos = {
            'village': (180, 60),
            'forest': (120, 40),
            'cave': (240, 40),
            'castle': (180, 20),
            'mountain_path': (300, 30),
            'riverside': (60, 80)
        }
        
        current_loc = self.current_player.current_location
        
        for loc_key, (x, y) in locations_pos.items():
            color = self.colors['accent'] if loc_key == current_loc else self.colors['light']
            size = 8 if loc_key == current_loc else 5
            
            self.minimap_canvas.create_oval(x-size, y-size, x+size, y+size, 
                                           fill=color, outline=self.colors['dark'], width=2)
            
            # Draw connections
            location = LOCATIONS.get(loc_key, {})
            for connected in location.get('connections', []):
                if connected in locations_pos:
                    cx, cy = locations_pos[connected]
                    self.minimap_canvas.create_line(x, y, cx, cy, fill=self.colors['secondary'], width=1)
        
        # Add location labels
        for loc_key, (x, y) in locations_pos.items():
            if loc_key == current_loc:
                name = LOCATIONS.get(loc_key, {}).get('name', loc_key.title())
                self.minimap_canvas.create_text(x, y+15, text=name, font=('Segoe UI', 8), 
                                               fill=self.colors['light'], anchor='center')
    
    def animate_character_idle(self):
        if not hasattr(self, 'player_sprite_id') or not hasattr(self, 'world_canvas'):
            return
        
        # Simple breathing animation
        def breathe():
            try:
                if (self.current_screen == "game" and 
                    hasattr(self, 'world_canvas') and 
                    hasattr(self, 'player_sprite_id')):
                    
                    current_coords = self.world_canvas.coords(self.player_sprite_id)
                    if current_coords and len(current_coords) >= 2:
                        x, y = current_coords[0], current_coords[1]
                        offset = math.sin(time.time() * 2) * 2
                        self.world_canvas.coords(self.player_sprite_id, x, y + offset)
                        
                        # Schedule next animation frame
                        self.root.after(50, breathe)
            except:
                # If animation fails, just stop it
                pass
        
        breathe()
    
    def typewriter_text(self, text, delay=50):
        self.game_log.delete(1.0, 'end')
        
        def type_char(index=0):
            if index < len(text):
                self.game_log.insert('end', text[index])
                self.game_log.see('end')
                self.root.after(delay, lambda: type_char(index + 1))
            else:
                self.game_log.insert('end', '\n')
        
        type_char()
    
    def drop_selected_item(self):
        # Placeholder for drop item functionality
        messagebox.showinfo("Drop Item", "Drop item functionality coming soon!")
    
    def create_player_info_panel(self, parent):
        # Player name and level
        name_frame = tk.Frame(parent, bg='#34495e')
        name_frame.pack(side='left', padx=10, pady=10)
        
        self.name_label = tk.Label(name_frame, text=f"👤 {self.current_player.name}", 
                                  font=('Arial', 14, 'bold'), bg='#34495e', fg='#e74c3c')
        self.name_label.pack()
        
        self.level_label = tk.Label(name_frame, text=f"Level {self.current_player.level}", 
                                   font=('Arial', 10), bg='#34495e', fg='#ecf0f1')
        self.level_label.pack()
        
        # Health bar
        health_frame = tk.Frame(parent, bg='#34495e')
        health_frame.pack(side='left', padx=20, pady=10)
        
        tk.Label(health_frame, text="❤️ Health", font=('Arial', 10, 'bold'), 
                bg='#34495e', fg='#e74c3c').pack()
        
        self.health_var = tk.StringVar()
        self.health_bar = ttk.Progressbar(health_frame, length=150, mode='determinate')
        self.health_bar.pack()
        
        self.health_label = tk.Label(health_frame, textvariable=self.health_var, 
                                    font=('Arial', 9), bg='#34495e', fg='#ecf0f1')
        self.health_label.pack()
        
        # Mana bar
        mana_frame = tk.Frame(parent, bg='#34495e')
        mana_frame.pack(side='left', padx=20, pady=10)
        
        tk.Label(mana_frame, text="🔮 Mana", font=('Arial', 10, 'bold'), 
                bg='#34495e', fg='#3498db').pack()
        
        self.mana_var = tk.StringVar()
        self.mana_bar = ttk.Progressbar(mana_frame, length=150, mode='determinate')
        self.mana_bar.pack()
        
        self.mana_label = tk.Label(mana_frame, textvariable=self.mana_var, 
                                  font=('Arial', 9), bg='#34495e', fg='#ecf0f1')
        self.mana_label.pack()
        
        # Gold and experience
        stats_frame = tk.Frame(parent, bg='#34495e')
        stats_frame.pack(side='right', padx=10, pady=10)
        
        self.gold_label = tk.Label(stats_frame, text=f"💰 {self.current_player.gold}", 
                                  font=('Arial', 11, 'bold'), bg='#34495e', fg='#f1c40f')
        self.gold_label.pack()
        
        self.exp_label = tk.Label(stats_frame, text=f"⭐ EXP: {self.current_player.experience}", 
                                 font=('Arial', 10), bg='#34495e', fg='#ecf0f1')
        self.exp_label.pack()
        
        self.score_label = tk.Label(stats_frame, text=f"🏆 Score: {self.current_player.score}", 
                                   font=('Arial', 10), bg='#34495e', fg='#ecf0f1')
        self.score_label.pack()
    
    def create_location_panel(self, parent):
        # Location title
        self.location_title = tk.Label(parent, text="", font=('Arial', 16, 'bold'), 
                                      bg='#34495e', fg='#e74c3c', wraplength=480)
        self.location_title.pack(pady=10)
        
        # Location description
        desc_frame = tk.Frame(parent, bg='#2c3e50', relief='sunken', bd=2)
        desc_frame.pack(fill='x', padx=10, pady=5)
        
        self.location_desc = tk.Label(desc_frame, text="", font=('Arial', 11), 
                                     bg='#2c3e50', fg='#ecf0f1', wraplength=460, justify='left')
        self.location_desc.pack(padx=10, pady=10)
        
        # Game log
        log_frame = tk.Frame(parent, bg='#34495e')
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(log_frame, text="📜 Adventure Log", font=('Arial', 12, 'bold'), 
                bg='#34495e', fg='#ecf0f1').pack()
        
        self.game_log = scrolledtext.ScrolledText(log_frame, height=15, font=('Arial', 10),
                                                 bg='#ecf0f1', fg='#2c3e50', wrap='word')
        self.game_log.pack(fill='both', expand=True, pady=5)
        
        # Add welcome message
        self.add_to_log(f"Welcome, {self.current_player.name}! Your adventure begins...")
    
    def create_action_panel(self, parent):
        # Movement actions
        movement_frame = tk.LabelFrame(parent, text="🗺️ Movement", font=('Arial', 11, 'bold'),
                                      bg='#34495e', fg='#ecf0f1', bd=2, relief='raised')
        movement_frame.pack(fill='x', padx=5, pady=5)
        
        self.movement_buttons = []
        
        # Special actions
        special_frame = tk.LabelFrame(parent, text="⚡ Actions", font=('Arial', 11, 'bold'),
                                     bg='#34495e', fg='#ecf0f1', bd=2, relief='raised')
        special_frame.pack(fill='x', padx=5, pady=5)
        
        self.special_buttons = []
        
        # Inventory
        inventory_frame = tk.LabelFrame(parent, text="🎒 Inventory", font=('Arial', 11, 'bold'),
                                       bg='#34495e', fg='#ecf0f1', bd=2, relief='raised')
        inventory_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Inventory listbox
        self.inventory_listbox = tk.Listbox(inventory_frame, height=8, font=('Arial', 9),
                                           bg='#ecf0f1', fg='#2c3e50', selectbackground='#3498db')
        self.inventory_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Inventory buttons
        inv_button_frame = tk.Frame(inventory_frame, bg='#34495e')
        inv_button_frame.pack(fill='x', padx=5, pady=5)
        
        use_btn = tk.Button(inv_button_frame, text="Use", command=self.use_selected_item,
                           font=('Arial', 9), bg='#27ae60', fg='white', width=8)
        use_btn.pack(side='left', padx=2)
        
        equip_btn = tk.Button(inv_button_frame, text="Equip", command=self.equip_selected_item,
                             font=('Arial', 9), bg='#3498db', fg='white', width=8)
        equip_btn.pack(side='left', padx=2)
        
        # Game menu buttons
        menu_frame = tk.Frame(parent, bg='#34495e')
        menu_frame.pack(fill='x', padx=5, pady=10)
        
        save_btn = tk.Button(menu_frame, text="💾 Save", command=self.save_game,
                            font=('Arial', 10), bg='#27ae60', fg='white', width=12)
        save_btn.pack(pady=2)
        
        stats_btn = tk.Button(menu_frame, text="📊 Stats", command=self.show_character_stats,
                             font=('Arial', 10), bg='#3498db', fg='white', width=12)
        stats_btn.pack(pady=2)
        
        quit_btn = tk.Button(menu_frame, text="🚪 Main Menu", command=self.return_to_main_menu,
                            font=('Arial', 10), bg='#e74c3c', fg='white', width=12)
        quit_btn.pack(pady=2)
        
        # Store references to frames for dynamic updates
        self.movement_frame = movement_frame
        self.special_frame = special_frame
    
    def update_display(self):
        if self.current_screen != "game":
            return
        
        # Update modern health bar with gradient
        self.update_gradient_bar(self.health_canvas, 
                                self.current_player.health, 
                                self.current_player.max_health,
                                "#e74c3c", "#c0392b")
        
        # Update modern mana bar with gradient
        self.update_gradient_bar(self.mana_canvas,
                                self.current_player.mana,
                                self.current_player.max_mana,
                                "#3498db", "#2980b9")
        
        # Update experience bar
        exp_needed = self.current_player.level * 100
        exp_progress = self.current_player.experience % 100
        self.update_gradient_bar(self.exp_canvas,
                                exp_progress,
                                100,
                                "#f39c12", "#e67e22")
        
        # Update resource labels with animations
        self.animate_number_change(self.gold_label, f"💰 {self.current_player.gold}")
        self.animate_number_change(self.score_label, f"🏆 {self.current_player.score}")
        
        # Update location info
        location = LOCATIONS.get(self.current_player.current_location, {})
        self.location_title.config(text=location.get("name", "Unknown Location"))
        
        # Re-render location if changed
        self.render_current_location()
        
        # Update minimap
        self.create_minimap()
        
        # Update action buttons
        self.update_action_buttons()
        self.update_modern_inventory()
    
    def update_gradient_bar(self, canvas, current, maximum, color1, color2):
        try:
            canvas.delete("all")
            width = canvas.winfo_width() or 300
            height = canvas.winfo_height() or 20
            
            if width <= 1 or height <= 1:
                return
            
            # Background
            canvas.create_rectangle(0, 0, width, height, fill=self.colors['primary'], outline="")
            
            # Calculate fill width
            if maximum > 0:
                fill_width = int((current / maximum) * width)
                
                # Create gradient fill (simplified for better compatibility)
                if fill_width > 0:
                    canvas.create_rectangle(0, 0, fill_width, height, fill=color1, outline="")
                    
                    # Add shine effect if possible
                    try:
                        shine_width = max(1, fill_width // 3)
                        canvas.create_rectangle(2, 2, shine_width, height//2, 
                                               fill="white", stipple="gray25")
                    except:
                        pass  # Skip shine effect if it fails
            
            # Text overlay
            text = f"{current}/{maximum}"
            canvas.create_text(width//2, height//2, text=text, fill="white", 
                              font=('Arial', 8, 'bold'))
                              
        except Exception as e:
            # Fallback: simple rectangle
            try:
                canvas.delete("all")
                canvas.create_rectangle(0, 0, 300, 20, fill=color1, outline="white")
                canvas.create_text(150, 10, text=f"{current}/{maximum}", fill="white")
            except:
                pass  # If even the fallback fails, just skip
    
    def animate_number_change(self, label, new_text):
        # Simple animation for number changes
        current_text = label.cget("text")
        if current_text != new_text:
            # Flash effect
            original_bg = label.cget("bg")
            label.config(bg=self.colors['accent'])
            self.root.after(100, lambda: label.config(bg=original_bg))
            label.config(text=new_text)
    
    def update_action_buttons(self):
        # Clear existing buttons
        for widget in self.action_buttons_frame.winfo_children():
            widget.destroy()
        
        location = LOCATIONS.get(self.current_player.current_location, {})
        special_actions = location.get("special_actions", [])
        
        # Create modern action buttons
        for i, action in enumerate(special_actions):
            btn_text = action.replace("_", " ").title()
            
            # Choose color based on action type
            if "shop" in action or "inn" in action:
                color = self.colors['warning']
            elif "combat" in action or "challenge" in action:
                color = self.colors['danger']
            elif "search" in action or "hunt" in action:
                color = self.colors['success']
            else:
                color = self.colors['accent']
            
            btn = ModernUI.create_modern_button(
                self.action_buttons_frame, btn_text,
                lambda act=action: self.perform_special_action(act),
                color, width=340, height=35
            )
            btn.pack(pady=3)
            
            # Add entrance animation
            self.animate_button_slide_in(btn, i * 50)
        
        # Movement buttons in minimap
        self.create_movement_buttons_on_minimap()
    
    def create_movement_buttons_on_minimap(self):
        # Add clickable areas on minimap for movement
        location = LOCATIONS.get(self.current_player.current_location, {})
        connections = location.get("connections", [])
        
        locations_pos = {
            'village': (180, 60),
            'forest': (120, 40),
            'cave': (240, 40),
            'castle': (180, 20),
            'mountain_path': (300, 30),
            'riverside': (60, 80)
        }
        
        for connection in connections:
            if connection in locations_pos:
                x, y = locations_pos[connection]
                # Create clickable area
                area_id = self.minimap_canvas.create_oval(
                    x-12, y-12, x+12, y+12, 
                    fill="", outline=self.colors['accent'], width=2, tags="clickable"
                )
                
                # Bind click event
                self.minimap_canvas.tag_bind(area_id, "<Button-1>", 
                                           lambda e, loc=connection: self.move_to_location(loc))
                
                # Add hover effect
                def on_enter(e, area=area_id):
                    self.minimap_canvas.itemconfig(area, outline=self.colors['light'], width=3)
                
                def on_leave(e, area=area_id):
                    self.minimap_canvas.itemconfig(area, outline=self.colors['accent'], width=2)
                
                self.minimap_canvas.tag_bind(area_id, "<Enter>", on_enter)
                self.minimap_canvas.tag_bind(area_id, "<Leave>", on_leave)
    
    def update_modern_inventory(self):
        self.inventory_canvas.delete("all")
        
        # Grid layout for inventory
        slot_size = 45
        slots_per_row = 8
        padding = 5
        
        # Draw inventory grid
        for row in range(4):
            for col in range(slots_per_row):
                x = col * (slot_size + padding) + padding
                y = row * (slot_size + padding) + padding
                
                self.inventory_canvas.create_rectangle(
                    x, y, x + slot_size, y + slot_size,
                    fill=self.colors['primary'], outline=self.colors['light'], width=1
                )
        
        # Add items to grid
        all_items = []
        
        # Add equipped items first
        if self.current_player.equipped_weapon:
            all_items.append(('weapon', self.current_player.equipped_weapon, True))
        if self.current_player.equipped_armor:
            all_items.append(('armor', self.current_player.equipped_armor, True))
        if self.current_player.equipped_accessory:
            all_items.append(('accessory', self.current_player.equipped_accessory, True))
        
        # Add inventory items
        for item in self.current_player.inventory:
            all_items.append((item['type'], item, False))
        
        # Display items in grid
        for i, (item_type, item, equipped) in enumerate(all_items):
            if i >= 32:  # Max 32 slots
                break
            
            row = i // slots_per_row
            col = i % slots_per_row
            x = col * (slot_size + padding) + padding
            y = row * (slot_size + padding) + padding
            
            # Item background
            bg_color = self.colors['accent'] if equipped else self.colors['secondary']
            self.inventory_canvas.create_rectangle(
                x+2, y+2, x + slot_size-2, y + slot_size-2,
                fill=bg_color, outline="", width=0
            )
            
            # Item icon
            icons = {
                "weapon": "⚔️", "armor": "🛡️", "consumable": "🧪", 
                "key": "🗝️", "misc": "📦", "accessory": "💍"
            }
            icon = icons.get(item_type, "📦")
            
            self.inventory_canvas.create_text(
                x + slot_size//2, y + slot_size//2 - 5,
                text=icon, font=('Arial', 16), fill="white"
            )
            
            # Item name (truncated)
            name = item['name'][:8] + "..." if len(item['name']) > 8 else item['name']
            self.inventory_canvas.create_text(
                x + slot_size//2, y + slot_size - 8,
                text=name, font=('Arial', 6), fill="white"
            )
            
            # Equipped indicator
            if equipped:
                self.inventory_canvas.create_text(
                    x + slot_size - 8, y + 8,
                    text="E", font=('Arial', 8, 'bold'), fill="#f1c40f"
                )
    
    def animate_button_slide_in(self, button, delay):
        # Animate button sliding in from the right
        original_x = button.winfo_x()
        button.place(x=400)  # Start off-screen
        
        def slide_in():
            current_x = button.winfo_x()
            target_x = 0
            new_x = current_x + (target_x - current_x) * 0.2
            
            button.place(x=new_x)
            
            if abs(new_x - target_x) > 1:
                self.root.after(16, slide_in)
            else:
                button.place(x=target_x)
        
        self.root.after(delay, slide_in)
    
    def update_movement_buttons(self):
        # Clear existing buttons
        for btn in self.movement_buttons:
            btn.destroy()
        self.movement_buttons.clear()
        
        location = LOCATIONS.get(self.current_player.current_location, {})
        connections = location.get("connections", [])
        
        for connection in connections:
            connected_location = LOCATIONS.get(connection, {})
            btn_text = connected_location.get("name", connection.title())
            
            btn = tk.Button(self.movement_frame, text=btn_text, 
                           command=lambda loc=connection: self.move_to_location(loc),
                           font=('Arial', 9), bg='#95a5a6', fg='white', width=20)
            btn.pack(pady=2, padx=5)
            self.movement_buttons.append(btn)
    
    def update_special_buttons(self):
        # Clear existing buttons
        for btn in self.special_buttons:
            btn.destroy()
        self.special_buttons.clear()
        
        location = LOCATIONS.get(self.current_player.current_location, {})
        special_actions = location.get("special_actions", [])
        
        for action in special_actions:
            btn_text = action.replace("_", " ").title()
            
            btn = tk.Button(self.special_frame, text=btn_text,
                           command=lambda act=action: self.perform_special_action(act),
                           font=('Arial', 9), bg='#f39c12', fg='white', width=20)
            btn.pack(pady=2, padx=5)
            self.special_buttons.append(btn)
    
    def update_inventory_display(self):
        self.inventory_listbox.delete(0, 'end')
        
        # Add equipped items first
        if self.current_player.equipped_weapon:
            self.inventory_listbox.insert('end', f"🗡️ {self.current_player.equipped_weapon['name']} (equipped)")
        if self.current_player.equipped_armor:
            self.inventory_listbox.insert('end', f"🛡️ {self.current_player.equipped_armor['name']} (equipped)")
        if self.current_player.equipped_accessory:
            self.inventory_listbox.insert('end', f"💍 {self.current_player.equipped_accessory['name']} (equipped)")
        
        # Add inventory items
        for item in self.current_player.inventory:
            icon = {"weapon": "⚔️", "armor": "🛡️", "consumable": "🧪", "key": "🗝️", "misc": "📦", "accessory": "💍"}.get(item["type"], "📦")
            self.inventory_listbox.insert('end', f"{icon} {item['name']}")
    
    def move_to_location(self, location):
        if location in LOCATIONS:
            self.current_player.current_location = location
            self.add_to_log(f"You travel to {LOCATIONS[location]['name']}")
            
            # Check for random encounters
            encounter_chance = LOCATIONS[location].get("encounter_chance", 0)
            if random.random() < encounter_chance:
                self.trigger_random_encounter()
            
            self.update_display()
            self.save_game()
    
    def perform_special_action(self, action):
        location = self.current_player.current_location
        
        if action == "shop":
            self.open_shop()
        elif action == "inn":
            self.rest_at_inn()
        elif action == "search_herbs":
            self.search_for_herbs()
        elif action == "hunt_animals":
            self.hunt_animals()
        elif action == "mine_crystals":
            self.mine_crystals()
        elif action == "challenge_dragon":
            self.challenge_boss("cave_dragon")
        elif action == "pray":
            self.pray_at_shrine()
        else:
            self.add_to_log(f"You {action.replace('_', ' ')}...")
            # Generic action with random outcome
            if random.random() < 0.6:
                reward = random.choice(["experience", "gold", "item"])
                if reward == "experience":
                    exp = random.randint(10, 30)
                    result = self.current_player.gain_experience(exp)
                    self.add_to_log(result)
                elif reward == "gold":
                    gold = random.randint(5, 20)
                    self.current_player.gold += gold
                    self.add_to_log(f"You found {gold} gold!")
                else:
                    # Random item
                    items = [
                        {"name": "Health Potion", "type": "consumable", "value": 50},
                        {"name": "Magic Herb", "type": "consumable", "value": 30}
                    ]
                    item = random.choice(items)
                    result = self.current_player.add_item(item)
                    self.add_to_log(result)
            else:
                self.add_to_log("Nothing interesting happens.")
        
        self.update_display()
        self.save_game()
    
    def trigger_random_encounter(self):
        location = LOCATIONS[self.current_player.current_location]
        
        # Choose appropriate enemies based on location
        location_enemies = {
            "forest": ["goblin", "wolf"],
            "deep_forest": ["orc", "forest_guardian"],
            "cave": ["skeleton", "giant_spider"],
            "deep_cave": ["troll", "cave_dragon"],
            "mountain_path": ["mountain_bear", "bandit"],
            "riverside": ["bandit", "wolf"]
        }
        
        possible_enemies = location_enemies.get(self.current_player.current_location, ["goblin", "wolf"])
        enemy_key = random.choice(possible_enemies)
        
        self.current_enemy = ENEMIES[enemy_key]
        self.add_to_log(f"⚔️ A wild {self.current_enemy.name} appears!")
        
        self.start_combat()
    
    def challenge_boss(self, boss_key):
        if boss_key in ENEMIES:
            self.current_enemy = ENEMIES[boss_key]
            self.add_to_log(f"⚔️ You challenge the mighty {self.current_enemy.name}!")
            self.start_combat()
    
    def start_combat(self):
        self.combat_active = True
        self.create_combat_interface()
    
    def create_combat_interface(self):
        # Create modern combat window
        self.combat_window = tk.Toplevel(self.root)
        self.combat_window.title("⚔️ Epic Battle Arena")
        self.combat_window.geometry("1000x700")
        self.combat_window.configure(bg=self.colors['dark'])
        self.combat_window.grab_set()
        
        # Combat canvas for animations
        self.combat_canvas = Canvas(self.combat_window, width=1000, height=700, 
                                   bg=self.colors['dark'], highlightthickness=0)
        self.combat_canvas.pack(fill='both', expand=True)
        
        # Initialize combat particle system
        self.combat_particles = ParticleSystem(self.combat_canvas)
        
        # Create dramatic background
        self.create_combat_background()
        
        # Player and enemy sprites
        self.create_combat_sprites()
        
        # Modern combat UI
        self.create_modern_combat_ui()
        
        # Start combat animations
        self.animate_combat_entrance()
        self.combat_particles.update()
        
        self.add_to_combat_log(f"⚔️ Epic battle begins! You face the mighty {self.current_enemy.name}!")
    
    def create_combat_background(self):
        # Dramatic gradient background
        for i in range(700):
            ratio = i / 700
            r = int(139 + (75 - 139) * ratio)  # Dark red gradient
            g = int(0 + (0 - 0) * ratio)
            b = int(0 + (130 - 0) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.combat_canvas.create_line(0, i, 1000, i, fill=color, tags="bg")
        
        # Add lightning effects
        for _ in range(5):
            x = random.randint(0, 1000)
            self.combat_canvas.create_line(x, 0, x + random.randint(-50, 50), 700, 
                                          fill="#ffffff", width=2, tags="lightning")
        
        # Battle arena floor
        self.combat_canvas.create_oval(100, 500, 900, 650, fill="#2c3e50", outline="#34495e", width=3, tags="arena")
    
    def create_combat_sprites(self):
        # Player sprite (left side)
        warrior_sprite = self.sprite_manager.sprites.get('warrior')
        if warrior_sprite:
            self.player_combat_sprite = self.combat_canvas.create_image(
                250, 400, image=warrior_sprite, tags="player_sprite"
            )
        else:
            self.player_combat_sprite = self.combat_canvas.create_text(
                250, 400, text="🧙‍♂️", font=('Arial', 48), fill="white", tags="player_sprite"
            )
        
        # Enemy sprite (right side)
        enemy_sprite_key = self.get_enemy_sprite_key()
        enemy_sprite = self.sprite_manager.sprites.get(enemy_sprite_key)
        if enemy_sprite:
            self.enemy_combat_sprite = self.combat_canvas.create_image(
                750, 400, image=enemy_sprite, tags="enemy_sprite"
            )
        else:
            # Fallback to text-based enemy
            enemy_emojis = {'dragon': '🐉', 'wolf': '🐺', 'skeleton': '💀', 'goblin': '👹'}
            enemy_emoji = enemy_emojis.get(enemy_sprite_key, '👹')
            self.enemy_combat_sprite = self.combat_canvas.create_text(
                750, 400, text=enemy_emoji, font=('Arial', 48), fill="red", tags="enemy_sprite"
            )
        
        # Add breathing animations (disabled for stability)
        # self.animate_combat_sprites()
    
    def get_enemy_sprite_key(self):
        enemy_name = self.current_enemy.name.lower()
        if 'dragon' in enemy_name:
            return 'dragon'
        elif 'wolf' in enemy_name:
            return 'wolf'
        elif 'skeleton' in enemy_name:
            return 'skeleton'
        else:
            return 'goblin'
    
    def create_modern_combat_ui(self):
        # Top UI panel
        ui_frame = tk.Frame(self.combat_canvas, bg=self.colors['dark'] + "DD")
        ui_window = self.combat_canvas.create_window(500, 80, window=ui_frame, width=960, height=140)
        
        # Player info (left)
        player_frame = tk.Frame(ui_frame, bg=self.colors['secondary'], relief='raised', bd=2)
        player_frame.pack(side='left', padx=10, pady=10, fill='y')
        
        tk.Label(player_frame, text=f"⚔️ {self.current_player.name}", 
                font=('Segoe UI', 14, 'bold'), bg=self.colors['secondary'], fg=self.colors['light']).pack(pady=5)
        
        # Player health with modern bar
        self.player_health_canvas = Canvas(player_frame, width=200, height=25, 
                                          bg=self.colors['primary'], highlightthickness=0)
        self.player_health_canvas.pack(pady=5)
        
        # Player mana bar
        self.player_mana_canvas = Canvas(player_frame, width=200, height=20, 
                                        bg=self.colors['primary'], highlightthickness=0)
        self.player_mana_canvas.pack(pady=2)
        
        # Enemy info (right)
        enemy_frame = tk.Frame(ui_frame, bg=self.colors['secondary'], relief='raised', bd=2)
        enemy_frame.pack(side='right', padx=10, pady=10, fill='y')
        
        tk.Label(enemy_frame, text=f"🐉 {self.current_enemy.name}", 
                font=('Segoe UI', 14, 'bold'), bg=self.colors['secondary'], fg='#e74c3c').pack(pady=5)
        
        # Enemy health bar
        self.enemy_health_canvas = Canvas(enemy_frame, width=200, height=25, 
                                         bg=self.colors['primary'], highlightthickness=0)
        self.enemy_health_canvas.pack(pady=5)
        
        # Combat log in center
        log_frame = tk.Frame(ui_frame, bg=self.colors['secondary'])
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(log_frame, text="⚔️ Battle Log", font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['secondary'], fg=self.colors['light']).pack()
        
        self.combat_log = scrolledtext.ScrolledText(log_frame, height=4, font=('Consolas', 10),
                                                   bg=self.colors['dark'], fg=self.colors['light'], 
                                                   wrap='word', relief='flat', bd=0)
        self.combat_log.pack(fill='both', expand=True, pady=5)
        
        # Bottom action panel
        action_frame = tk.Frame(self.combat_canvas, bg=self.colors['secondary'])
        action_window = self.combat_canvas.create_window(500, 600, window=action_frame, width=800, height=120)
        
        # Combat action buttons with modern styling
        actions = [
            ("⚔️ Attack", lambda: self.combat_action(CombatAction.ATTACK), self.colors['danger']),
            ("🛡️ Defend", lambda: self.combat_action(CombatAction.DEFEND), self.colors['accent']),
            ("✨ Special Attack", lambda: self.combat_action(CombatAction.SPECIAL), self.colors['warning']),
            ("🧪 Use Item", lambda: self.combat_action(CombatAction.USE_ITEM), self.colors['success']),
            ("🏃 Retreat", lambda: self.combat_action(CombatAction.RUN), "#95a5a6")
        ]
        
        button_container = tk.Frame(action_frame, bg=self.colors['secondary'])
        button_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.combat_action_buttons = []
        for i, (text, command, color) in enumerate(actions):
            btn = ModernUI.create_modern_button(
                button_container, text, command, color, width=140, height=60
            )
            btn.grid(row=0, column=i, padx=10, pady=10)
            self.combat_action_buttons.append(btn)
    
    def animate_combat_entrance(self):
        # Dramatic entrance animation
        # Player slides in from left
        self.combat_canvas.coords(self.player_combat_sprite, -100, 400)
        self.animate_sprite_slide(self.player_combat_sprite, 250, 400, 1000)
        
        # Enemy slides in from right
        self.combat_canvas.coords(self.enemy_combat_sprite, 1100, 400)
        self.animate_sprite_slide(self.enemy_combat_sprite, 750, 400, 1200)
        
        # Screen shake effect
        self.screen_shake(5, 500)
    
    def animate_sprite_slide(self, sprite_id, target_x, target_y, duration):
        start_time = time.time() * 1000
        start_coords = self.combat_canvas.coords(sprite_id)
        start_x, start_y = start_coords[0], start_coords[1]
        
        def slide_step():
            current_time = time.time() * 1000
            elapsed = current_time - start_time
            progress = min(elapsed / duration, 1.0)
            
            # Ease out animation
            progress = 1 - (1 - progress) ** 3
            
            current_x = start_x + (target_x - start_x) * progress
            current_y = start_y + (target_y - start_y) * progress
            
            self.combat_canvas.coords(sprite_id, current_x, current_y)
            
            if progress < 1.0:
                self.combat_window.after(16, slide_step)
        
        slide_step()
    
    def animate_combat_sprites(self):
        if not hasattr(self, 'combat_canvas'):
            return
        
        def animate_breathing():
            try:
                # Player breathing
                player_coords = self.combat_canvas.coords(self.player_combat_sprite)
                if player_coords:
                    x, y = player_coords
                    offset = math.sin(time.time() * 1.5) * 3
                    self.combat_canvas.coords(self.player_combat_sprite, x, y + offset)
                
                # Enemy breathing (different rhythm)
                enemy_coords = self.combat_canvas.coords(self.enemy_combat_sprite)
                if enemy_coords:
                    x, y = enemy_coords
                    offset = math.sin(time.time() * 2) * 2
                    self.combat_canvas.coords(self.enemy_combat_sprite, x, y + offset)
                
            except:
                return
            
            if hasattr(self, 'combat_window') and self.combat_window.winfo_exists():
                self.combat_window.after(50, animate_breathing)
        
        animate_breathing()
    
    def screen_shake(self, intensity, duration):
        start_time = time.time() * 1000
        original_pos = (500, 350)  # Center of screen
        
        def shake_step():
            current_time = time.time() * 1000
            elapsed = current_time - start_time
            
            if elapsed < duration:
                # Random shake offset
                shake_x = random.randint(-intensity, intensity)
                shake_y = random.randint(-intensity, intensity)
                
                # Apply shake to all combat elements
                for item in self.combat_canvas.find_all():
                    if "bg" not in self.combat_canvas.gettags(item):
                        coords = self.combat_canvas.coords(item)
                        if len(coords) >= 2:
                            self.combat_canvas.move(item, shake_x, shake_y)
                
                self.combat_window.after(16, shake_step)
            else:
                # Reset positions
                pass
        
        shake_step()
    
    def update_combat_display(self):
        if not hasattr(self, 'combat_window') or not self.combat_window.winfo_exists():
            return
        
        # Update player health bar
        self.update_gradient_bar(self.player_health_canvas,
                                self.current_player.health,
                                self.current_player.max_health,
                                "#27ae60", "#2ecc71")
        
        # Update player mana bar
        self.update_gradient_bar(self.player_mana_canvas,
                                self.current_player.mana,
                                self.current_player.max_mana,
                                "#3498db", "#5dade2")
        
        # Update enemy health bar
        self.update_gradient_bar(self.enemy_health_canvas,
                                self.current_enemy.health,
                                self.current_enemy.max_health,
                                "#e74c3c", "#c0392b")
    
    def update_combat_display(self):
        if not hasattr(self, 'combat_window') or not self.combat_window.winfo_exists():
            return
        
        # Update enemy health bar
        health_percent = (self.current_enemy.health / self.current_enemy.max_health) * 100
        self.enemy_health_bar['value'] = health_percent
        self.enemy_health_var.set(f"{self.current_enemy.health}/{self.current_enemy.max_health}")
    
    def add_to_combat_log(self, message):
        if hasattr(self, 'combat_log') and self.combat_log.winfo_exists():
            self.combat_log.insert('end', message + '\n')
            self.combat_log.see('end')
    
    def combat_action(self, action: CombatAction):
        if not self.combat_active:
            return
        
        result = self.process_combat_turn(action)
        
        # Display results
        if result.player_action:
            self.add_to_combat_log(f"You {result.player_action}")
        
        for effect in result.special_effects:
            self.add_to_combat_log(effect)
        
        if result.player_damage > 0:
            self.add_to_combat_log(f"You deal {result.player_damage} damage!")
        
        if result.enemy_damage > 0:
            self.add_to_combat_log(f"The {self.current_enemy.name} deals {result.enemy_damage} damage to you!")
        
        if result.combat_ended:
            self.end_combat(result.victory)
        else:
            self.update_combat_display()
            self.update_display()  # Update main window health/mana
    
    def process_combat_turn(self, player_action: CombatAction) -> CombatResult:
        special_effects = []
        player_damage = 0
        enemy_damage = 0
        combat_ended = False
        victory = False
        
        # Process player action
        action_text = ""
        if player_action == CombatAction.ATTACK:
            player_damage, effects = self.current_player.calculate_combat_damage(player_action, self.current_enemy.defense)
            special_effects.extend(effects)
            action_text = "attack with your weapon!"
            
        elif player_action == CombatAction.DEFEND:
            self.current_player.defense_bonus = self.current_player.defense // 2
            action_text = "take a defensive stance!"
            special_effects.append("Defense increased for this turn!")
            
        elif player_action == CombatAction.SPECIAL:
            player_damage, effects = self.current_player.calculate_combat_damage(player_action, self.current_enemy.defense)
            special_effects.extend(effects)
            action_text = "use a special attack!"
            
        elif player_action == CombatAction.USE_ITEM:
            # For now, just use a health potion if available
            consumables = [item for item in self.current_player.inventory if item["type"] == "consumable"]
            if consumables:
                item = consumables[0]
                result = self.current_player.use_item(item["name"])
                special_effects.append(result)
                action_text = f"use {item['name']}!"
            else:
                special_effects.append("No usable items!")
                action_text = "search for items but find none!"
                
        elif player_action == CombatAction.RUN:
            if random.random() < 0.6:  # 60% chance to escape
                special_effects.append("You successfully escaped!")
                combat_ended = True
                victory = False
                return CombatResult(0, 0, "run away!", "", special_effects, combat_ended, victory)
            else:
                special_effects.append("You couldn't escape!")
                action_text = "try to run but fail!"
        
        # Apply player damage to enemy
        if player_damage > 0:
            if self.current_enemy.take_damage(player_damage):
                combat_ended = True
                victory = True
                return CombatResult(player_damage, 0, action_text, "", special_effects, combat_ended, victory)
        
        # Enemy turn (if combat continues)
        if not combat_ended:
            enemy_action = self.current_enemy.choose_action()
            
            if enemy_action == "attack":
                base_damage = self.current_enemy.attack
                defense = self.current_player.defense
                if hasattr(self.current_player, 'defense_bonus'):
                    defense += self.current_player.defense_bonus
                    delattr(self.current_player, 'defense_bonus')
                
                # Check for dodge
                if random.random() < self.current_player.skills["dodge_chance"]:
                    special_effects.append("You dodged the attack!")
                    enemy_damage = 0
                else:
                    enemy_damage = max(1, base_damage - defense + random.randint(-2, 2))
                    self.current_player.health -= enemy_damage
                    
                    if self.current_player.health <= 0:
                        self.current_player.health = 1  # Don't let player die completely
                        combat_ended = True
                        victory = False
                        special_effects.append("You have been defeated!")
                        
            elif enemy_action == "defend":
                special_effects.append(f"The {self.current_enemy.name} takes a defensive stance!")
                
            elif enemy_action == "special":
                # Enemy special attacks
                if "fire_breath" in self.current_enemy.special_abilities:
                    enemy_damage = int(self.current_enemy.attack * 1.5)
                    self.current_player.health -= enemy_damage
                    special_effects.append(f"The {self.current_enemy.name} breathes fire!")
                elif "heal" in self.current_enemy.special_abilities:
                    heal_amount = min(30, self.current_enemy.max_health - self.current_enemy.health)
                    self.current_enemy.health += heal_amount
                    special_effects.append(f"The {self.current_enemy.name} heals for {heal_amount} health!")
        
        return CombatResult(player_damage, enemy_damage, action_text, enemy_action, special_effects, combat_ended, victory)
    
    def end_combat(self, victory: bool):
        self.combat_active = False
        
        if victory:
            self.add_to_combat_log(f"🎉 Victory! You defeated the {self.current_enemy.name}!")
            
            # Rewards
            exp_reward = self.current_enemy.exp_reward
            gold_reward = self.current_enemy.gold_reward
            
            exp_result = self.current_player.gain_experience(exp_reward)
            self.current_player.gold += gold_reward
            self.current_player.score += exp_reward
            
            self.add_to_combat_log(f"Rewards: {exp_reward} EXP, {gold_reward} gold")
            self.add_to_log(f"🎉 Victory! Defeated {self.current_enemy.name}!")
            self.add_to_log(exp_result)
            
            # Check quest completion
            if not self.current_player.quests["first_combat"]["completed"]:
                self.current_player.quests["first_combat"]["completed"] = True
                bonus_exp = self.current_player.quests["first_combat"]["reward"]
                self.current_player.gain_experience(bonus_exp)
                self.add_to_log("Quest completed: Win your first battle!")
            
            # Random loot
            if random.random() < 0.4:  # 40% chance
                loot_items = [
                    {"name": "Health Potion", "type": "consumable", "value": 50},
                    {"name": "Magic Herb", "type": "consumable", "value": 30},
                    {"name": "Iron Sword", "type": "weapon", "value": 15}
                ]
                loot = random.choice(loot_items)
                self.current_player.add_item(loot)
                self.add_to_combat_log(f"You found: {loot['name']}!")
                self.add_to_log(f"Found loot: {loot['name']}")
        else:
            self.add_to_combat_log("💀 Defeat! You retreat to safety...")
            self.add_to_log("💀 You were defeated and retreated to the village.")
            self.current_player.current_location = "village"
        
        # Close combat window after a delay
        self.combat_window.after(3000, self.close_combat_window)
    
    def close_combat_window(self):
        if hasattr(self, 'combat_window') and self.combat_window.winfo_exists():
            self.combat_window.destroy()
        self.update_display()
        self.save_game()
    
    def search_for_herbs(self):
        if random.random() < 0.7:  # 70% success rate
            herb = {"name": "Magic Herb", "type": "consumable", "value": 30}
            result = self.current_player.add_item(herb)
            self.add_to_log(result)
            
            # Update herb collector quest
            if not self.current_player.quests["herb_collector"]["completed"]:
                self.current_player.quests["herb_collector"]["progress"] += 1
                if self.current_player.quests["herb_collector"]["progress"] >= self.current_player.quests["herb_collector"]["target"]:
                    self.current_player.quests["herb_collector"]["completed"] = True
                    bonus_exp = self.current_player.quests["herb_collector"]["reward"]
                    exp_result = self.current_player.gain_experience(bonus_exp)
                    self.add_to_log("Quest completed: Collect 5 healing herbs!")
                    self.add_to_log(exp_result)
        else:
            self.add_to_log("You search but find no herbs this time.")
    
    def hunt_animals(self):
        if random.random() < 0.6:  # 60% success rate
            exp_gain = random.randint(10, 20)
            gold_gain = random.randint(5, 15)
            
            exp_result = self.current_player.gain_experience(exp_gain)
            self.current_player.gold += gold_gain
            
            self.add_to_log(f"Successful hunt! Gained {gold_gain} gold.")
            self.add_to_log(exp_result)
        else:
            self.add_to_log("The animals were too quick this time.")
    
    def mine_crystals(self):
        if random.random() < 0.5:  # 50% success rate
            gold_gain = random.randint(15, 35)
            exp_gain = random.randint(8, 18)
            
            self.current_player.gold += gold_gain
            exp_result = self.current_player.gain_experience(exp_gain)
            
            self.add_to_log(f"Successfully mined crystals! Gained {gold_gain} gold.")
            self.add_to_log(exp_result)
        else:
            self.add_to_log("The crystals were too hard to extract.")
    
    def rest_at_inn(self):
        cost = 15
        if self.current_player.gold >= cost:
            self.current_player.gold -= cost
            old_health = self.current_player.health
            self.current_player.health = self.current_player.max_health
            self.current_player.mana = self.current_player.max_mana
            
            healed = self.current_player.max_health - old_health
            self.add_to_log(f"You rest at the inn. Restored {healed} health and full mana for {cost} gold.")
        else:
            self.add_to_log(f"You need {cost} gold to rest at the inn.")
    
    def pray_at_shrine(self):
        if random.random() < 0.6:  # 60% chance of blessing
            blessing_type = random.choice(["health", "mana", "experience"])
            
            if blessing_type == "health":
                heal_amount = random.randint(20, 40)
                self.current_player.health = min(self.current_player.max_health, 
                                               self.current_player.health + heal_amount)
                self.add_to_log(f"The shrine blesses you with {heal_amount} health!")
            elif blessing_type == "mana":
                mana_amount = random.randint(15, 30)
                self.current_player.mana = min(self.current_player.max_mana,
                                             self.current_player.mana + mana_amount)
                self.add_to_log(f"The shrine restores {mana_amount} mana!")
            else:
                exp_amount = random.randint(25, 50)
                exp_result = self.current_player.gain_experience(exp_amount)
                self.add_to_log(f"The shrine grants you wisdom!")
                self.add_to_log(exp_result)
        else:
            self.add_to_log("The shrine remains silent.")
    
    def open_shop(self):
        shop_window = tk.Toplevel(self.root)
        shop_window.title("Village Shop")
        shop_window.geometry("500x400")
        shop_window.configure(bg='#8b4513')
        shop_window.grab_set()
        
        # Shop title
        title_label = tk.Label(shop_window, text="🏪 Village Shop", 
                              font=('Arial', 18, 'bold'), bg='#8b4513', fg='#ffff00')
        title_label.pack(pady=10)
        
        # Player gold
        gold_label = tk.Label(shop_window, text=f"Your Gold: {self.current_player.gold}", 
                             font=('Arial', 12, 'bold'), bg='#8b4513', fg='#ffffff')
        gold_label.pack(pady=5)
        
        # Shop items
        shop_items = [
            {"name": "Health Potion", "type": "consumable", "value": 50, "price": 25},
            {"name": "Greater Health Potion", "type": "consumable", "value": 100, "price": 50},
            {"name": "Mana Potion", "type": "consumable", "value": 0, "price": 30},
            {"name": "Iron Sword", "type": "weapon", "value": 15, "price": 100},
            {"name": "Steel Sword", "type": "weapon", "value": 25, "price": 200},
            {"name": "Steel Shield", "type": "armor", "value": 15, "price": 120},
            {"name": "Lucky Charm", "type": "accessory", "value": 0, "price": 150}
        ]
        
        # Items frame
        items_frame = tk.Frame(shop_window, bg='#8b4513')
        items_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Items listbox
        items_listbox = tk.Listbox(items_frame, font=('Arial', 10), height=10,
                                  bg='#f5deb3', fg='#8b4513', selectbackground='#daa520')
        items_listbox.pack(fill='both', expand=True)
        
        for item in shop_items:
            items_listbox.insert('end', f"{item['name']} - {item['price']} gold")
        
        # Buttons
        button_frame = tk.Frame(shop_window, bg='#8b4513')
        button_frame.pack(pady=10)
        
        def buy_item():
            selection = items_listbox.curselection()
            if selection:
                item = shop_items[selection[0]]
                if self.current_player.gold >= item["price"]:
                    self.current_player.gold -= item["price"]
                    shop_item = {"name": item["name"], "type": item["type"], "value": item["value"]}
                    result = self.current_player.add_item(shop_item)
                    self.add_to_log(f"Bought {item['name']} for {item['price']} gold!")
                    gold_label.config(text=f"Your Gold: {self.current_player.gold}")
                    
                    # Update master trader quest
                    if "master_trader" in self.current_player.quests:
                        quest = self.current_player.quests["master_trader"]
                        if not quest["completed"]:
                            quest["progress"] += item["price"]
                            if quest["progress"] >= quest["target"]:
                                quest["completed"] = True
                                exp_result = self.current_player.gain_experience(quest["reward"])
                                self.add_to_log("Quest completed: Master Trader!")
                                self.add_to_log(exp_result)
                else:
                    messagebox.showwarning("Insufficient Gold", "You don't have enough gold!")
        
        buy_btn = tk.Button(button_frame, text="Buy Selected", command=buy_item,
                           font=('Arial', 11), bg='#228b22', fg='white', width=12)
        buy_btn.pack(side='left', padx=10)
        
        close_btn = tk.Button(button_frame, text="Close", command=shop_window.destroy,
                             font=('Arial', 11), bg='#dc143c', fg='white', width=12)
        close_btn.pack(side='left', padx=10)
    
    def use_selected_item(self):
        selection = self.inventory_listbox.curselection()
        if selection:
            item_text = self.inventory_listbox.get(selection[0])
            if "(equipped)" in item_text:
                messagebox.showinfo("Cannot Use", "This item is currently equipped!")
                return
            
            # Extract item name (remove icon and equipped status)
            item_name = item_text.split(' ', 1)[1] if ' ' in item_text else item_text
            
            # Find the item in inventory
            for item in self.current_player.inventory:
                if item["name"] == item_name:
                    if item["type"] == "consumable":
                        result = self.current_player.use_item(item["name"])
                        self.add_to_log(result)
                        self.update_display()
                        self.save_game()
                        return
                    else:
                        messagebox.showinfo("Cannot Use", "This item cannot be used directly!")
                        return
            
            messagebox.showwarning("Item Not Found", "Selected item not found in inventory!")
    
    def equip_selected_item(self):
        selection = self.inventory_listbox.curselection()
        if selection:
            item_text = self.inventory_listbox.get(selection[0])
            if "(equipped)" in item_text:
                messagebox.showinfo("Already Equipped", "This item is already equipped!")
                return
            
            # Extract item name (remove icon)
            item_name = item_text.split(' ', 1)[1] if ' ' in item_text else item_text
            
            # Find the item in inventory
            for item in self.current_player.inventory:
                if item["name"] == item_name:
                    if item["type"] in ["weapon", "armor", "accessory"]:
                        result = self.current_player.equip_item(item["name"])
                        self.add_to_log(result)
                        self.update_display()
                        self.save_game()
                        return
                    else:
                        messagebox.showinfo("Cannot Equip", "This item cannot be equipped!")
                        return
            
            messagebox.showwarning("Item Not Found", "Selected item not found in inventory!")
    
    def show_character_stats(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Character Statistics")
        stats_window.geometry("400x500")
        stats_window.configure(bg='#2c3e50')
        stats_window.grab_set()
        
        # Title
        title_label = tk.Label(stats_window, text=f"📊 {self.current_player.name}'s Stats", 
                              font=('Arial', 16, 'bold'), bg='#2c3e50', fg='#e74c3c')
        title_label.pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(stats_window, bg='#34495e', relief='raised', bd=2)
        stats_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        stats_text = f"""
Level: {self.current_player.level}
Health: {self.current_player.health}/{self.current_player.max_health}
Mana: {self.current_player.mana}/{self.current_player.max_mana}
Attack: {self.current_player.attack} (Base: {self.current_player.base_attack})
Defense: {self.current_player.defense} (Base: {self.current_player.base_defense})
Experience: {self.current_player.experience}
Gold: {self.current_player.gold}
Score: {self.current_player.score}

Equipment:
Weapon: {self.current_player.equipped_weapon['name'] if self.current_player.equipped_weapon else 'None'}
Armor: {self.current_player.equipped_armor['name'] if self.current_player.equipped_armor else 'None'}
Accessory: {self.current_player.equipped_accessory['name'] if self.current_player.equipped_accessory else 'None'}

Skills:
Critical Chance: {self.current_player.skills['critical_chance']:.1%}
Dodge Chance: {self.current_player.skills['dodge_chance']:.1%}
Magic Power: {self.current_player.skills['magic_power']}

Active Quests:
"""
        
        for quest_name, quest_data in self.current_player.quests.items():
            if not quest_data["completed"]:
                progress = ""
                if "progress" in quest_data and "target" in quest_data:
                    progress = f" ({quest_data['progress']}/{quest_data['target']})"
                stats_text += f"• {quest_data['description']}{progress}\n"
        
        stats_label = tk.Label(stats_frame, text=stats_text, font=('Arial', 10), 
                              bg='#34495e', fg='#ecf0f1', justify='left')
        stats_label.pack(padx=20, pady=20)
        
        # Close button
        close_btn = tk.Button(stats_window, text="Close", command=stats_window.destroy,
                             font=('Arial', 12), bg='#95a5a6', fg='white', width=10)
        close_btn.pack(pady=10)
    
    def add_to_log(self, message):
        self.game_log.insert('end', message + '\n')
        self.game_log.see('end')
    
    def save_game(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Convert complex data to JSON
            inventory_json = json.dumps(self.current_player.inventory)
            quests_json = json.dumps(self.current_player.quests)
            skills_json = json.dumps(self.current_player.skills)
            achievements_json = json.dumps(self.current_player.achievements)
            
            # Save player data
            cursor.execute("""
                INSERT OR REPLACE INTO players 
                (name, health, max_health, attack, defense, level, experience, score, 
                 current_location, inventory, quests, gold, skills, achievements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_player.name, self.current_player.health, self.current_player.max_health,
                self.current_player.base_attack, self.current_player.base_defense,
                self.current_player.level, self.current_player.experience, self.current_player.score,
                self.current_player.current_location, inventory_json, quests_json, 
                self.current_player.gold, skills_json, achievements_json
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save game: {e}")
    
    def load_player(self, player_name):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players WHERE name = ?", (player_name,))
            player_data = cursor.fetchone()
            conn.close()
            
            if player_data:
                # Unpack data
                (id, name, health, max_health, attack, defense, level, experience, 
                 score, current_location, inventory_json, quests_json, gold, 
                 skills_json, achievements_json) = player_data
                
                # Create player
                player = Player(name, health, max_health, attack, defense, level, experience, score, gold)
                player.current_location = current_location or "village"
                
                # Load JSON data
                if inventory_json:
                    player.inventory = json.loads(inventory_json)
                if quests_json:
                    player.quests = json.loads(quests_json)
                if skills_json:
                    player.skills = json.loads(skills_json)
                if achievements_json:
                    player.achievements = json.loads(achievements_json)
                
                # Handle equipped items
                for item in player.inventory[:]:
                    if item.get("equipped", False):
                        if item["type"] == "weapon":
                            player.equipped_weapon = item
                            player.inventory.remove(item)
                        elif item["type"] == "armor":
                            player.equipped_armor = item
                            player.inventory.remove(item)
                        elif item["type"] == "accessory":
                            player.equipped_accessory = item
                            player.inventory.remove(item)
                
                return player
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load player: {e}")
        
        return None
    
    def return_to_main_menu(self):
        if messagebox.askyesno("Confirm", "Return to main menu? (Game will be saved)"):
            self.save_game()
            self.create_main_menu()

def main():
    root = tk.Tk()
    app = AdventureGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
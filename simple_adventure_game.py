#!/usr/bin/env python3
"""
Simple Adventure Game - Fallback Version
A simplified version that works without advanced dependencies
"""

import sqlite3
import random
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

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
        self.quests = self.get_default_quests()
        self.current_location = "village"
        self.skills = {"critical_chance": 0.1, "dodge_chance": 0.1, "magic_power": 0}
        self.mana = 50
        self.max_mana = 50

    def get_default_quests(self):
        return {
            "first_combat": {"description": "Win your first battle", "completed": False, "reward": 50},
            "herb_collector": {"description": "Collect 5 healing herbs", "progress": 0, "target": 5, "completed": False, "reward": 75},
            "treasure_hunter": {"description": "Find treasure in the cave", "completed": False, "reward": 100},
            "dragon_slayer": {"description": "Defeat the cave dragon", "completed": False, "reward": 300},
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
        
        self.max_health += health_bonus
        self.health = self.max_health
        self.base_attack += attack_bonus
        self.base_defense += defense_bonus
        
        return f"LEVEL UP! You are now level {self.level}!\nHealth +{health_bonus}, Attack +{attack_bonus}, Defense +{defense_bonus}"

class Enemy:
    def __init__(self, name, health, attack, defense, exp_reward, gold_reward):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        return self.health <= 0

# Locations
LOCATIONS = {
    "village": {
        "name": "Peaceful Village",
        "description": "You are in the peaceful village. The sun shines warmly on the cobblestone streets.",
        "connections": ["forest", "cave", "castle"],
        "special_actions": ["shop", "inn"],
        "encounter_chance": 0.0
    },
    "forest": {
        "name": "Enchanted Forest",
        "description": "You are in the enchanted forest. Ancient trees tower above you.",
        "connections": ["village", "deep_forest"],
        "special_actions": ["search_herbs", "hunt_animals"],
        "encounter_chance": 0.3
    },
    "deep_forest": {
        "name": "Heart of the Forest",
        "description": "You are in the heart of the ancient forest. Mystical energy flows through this place.",
        "connections": ["forest"],
        "special_actions": ["pray"],
        "encounter_chance": 0.4
    },
    "cave": {
        "name": "Mysterious Cave",
        "description": "The cave entrance yawns before you like a great mouth.",
        "connections": ["village", "deep_cave"],
        "special_actions": ["mine_crystals", "search_treasure"],
        "encounter_chance": 0.4
    },
    "deep_cave": {
        "name": "Dragon's Lair",
        "description": "The deepest part of the cave system. Precious gems glitter in the darkness.",
        "connections": ["cave"],
        "special_actions": ["challenge_dragon"],
        "encounter_chance": 0.6
    },
    "castle": {
        "name": "Ancient Castle",
        "description": "The ancient castle looms majestically before you.",
        "connections": ["village"],
        "special_actions": ["explore_grounds"],
        "encounter_chance": 0.3
    }
}

# Enemies
ENEMIES = {
    "goblin": Enemy("Goblin Scout", 40, 12, 3, 15, 8),
    "wolf": Enemy("Gray Wolf", 35, 15, 2, 12, 5),
    "bandit": Enemy("Highway Bandit", 50, 18, 5, 20, 15),
    "cave_dragon": Enemy("Ancient Dragon", 300, 45, 20, 250, 150),
    "skeleton": Enemy("Skeleton Warrior", 45, 20, 6, 25, 12),
}

class SimpleAdventureGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🏰 Adventure Game - Simple Edition")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        self.db = Database()
        self.current_player = None
        self.current_enemy = None
        self.combat_active = False
        
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#1a1a1a'
        }
        
        self.create_main_menu()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_main_menu(self):
        self.clear_window()
        
        # Title
        title_frame = tk.Frame(self.root, bg=self.colors['primary'])
        title_frame.pack(pady=50)
        
        title_label = tk.Label(title_frame, text="🏰 ADVENTURE GAME 🏰", 
                              font=('Arial', 28, 'bold'), bg=self.colors['primary'], fg=self.colors['light'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Simple & Reliable Edition", 
                                 font=('Arial', 16), bg=self.colors['primary'], fg=self.colors['accent'])
        subtitle_label.pack(pady=10)
        
        # Menu buttons
        button_frame = tk.Frame(self.root, bg=self.colors['primary'])
        button_frame.pack(pady=50)
        
        buttons = [
            ("🆕 Start New Game", self.create_character),
            ("📁 Load Game", self.load_game_menu),
            ("❌ Quit", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command,
                           font=('Arial', 14, 'bold'), width=20, height=2,
                           bg=self.colors['accent'], fg='white', relief='raised', bd=3)
            btn.pack(pady=10)
    
    def create_character(self):
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="Create Your Character", 
                              font=('Arial', 20, 'bold'), bg=self.colors['primary'], fg=self.colors['light'])
        title_label.pack(pady=30)
        
        # Name input
        name_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        name_frame.pack(pady=20)
        
        tk.Label(name_frame, text="Character Name:", font=('Arial', 14), 
                bg=self.colors['primary'], fg=self.colors['light']).pack()
        
        self.name_entry = tk.Entry(name_frame, font=('Arial', 14), width=25)
        self.name_entry.pack(pady=10)
        self.name_entry.focus()
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        button_frame.pack(pady=40)
        
        create_btn = tk.Button(button_frame, text="Create Character", command=self.start_new_game,
                              font=('Arial', 12, 'bold'), bg=self.colors['success'], fg='white', 
                              width=15, height=2)
        create_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="Back", command=self.create_main_menu,
                            font=('Arial', 12), bg=self.colors['secondary'], fg='white', width=10, height=2)
        back_btn.pack(side='left', padx=10)
    
    def start_new_game(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a character name!")
            return
        
        self.current_player = Player(name)
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
        
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="Load Game", font=('Arial', 18, 'bold'), 
                              bg=self.colors['primary'], fg=self.colors['light'])
        title_label.pack(pady=20)
        
        # Profiles list
        list_frame = tk.Frame(main_frame, bg=self.colors['secondary'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.profile_listbox = tk.Listbox(list_frame, font=('Arial', 12), height=10,
                                         bg=self.colors['light'], fg=self.colors['primary'])
        self.profile_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        for name, level, score in profiles:
            self.profile_listbox.insert('end', f"{name} - Level {level} - Score: {score}")
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        button_frame.pack(pady=20)
        
        load_btn = tk.Button(button_frame, text="Load Selected", command=self.load_selected_game,
                            font=('Arial', 12, 'bold'), bg=self.colors['success'], fg='white', width=15, height=2)
        load_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="Back", command=self.create_main_menu,
                            font=('Arial', 12), bg=self.colors['secondary'], fg='white', width=10, height=2)
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
    
    def create_game_interface(self):
        self.clear_window()
        
        # Main game frame
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(fill='both', expand=True)
        
        # Top frame for player info
        top_frame = tk.Frame(main_frame, bg=self.colors['secondary'], height=100)
        top_frame.pack(fill='x', padx=5, pady=5)
        top_frame.pack_propagate(False)
        
        self.create_player_info_panel(top_frame)
        
        # Middle frame
        middle_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        middle_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left side - location and log
        left_frame = tk.Frame(middle_frame, bg=self.colors['secondary'], width=600)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.create_location_panel(left_frame)
        
        # Right side - actions and inventory
        right_frame = tk.Frame(middle_frame, bg=self.colors['secondary'], width=300)
        right_frame.pack(side='right', fill='y', padx=(5, 0))
        right_frame.pack_propagate(False)
        
        self.create_action_panel(right_frame)
        
        self.update_display()
    
    def create_player_info_panel(self, parent):
        # Player info
        info_frame = tk.Frame(parent, bg=self.colors['secondary'])
        info_frame.pack(side='left', padx=10, pady=10)
        
        self.name_label = tk.Label(info_frame, text=f"👤 {self.current_player.name}", 
                                  font=('Arial', 14, 'bold'), bg=self.colors['secondary'], fg=self.colors['light'])
        self.name_label.pack()
        
        self.level_label = tk.Label(info_frame, text=f"Level {self.current_player.level}", 
                                   font=('Arial', 10), bg=self.colors['secondary'], fg=self.colors['accent'])
        self.level_label.pack()
        
        # Stats
        stats_frame = tk.Frame(parent, bg=self.colors['secondary'])
        stats_frame.pack(side='left', padx=20, pady=10, fill='both', expand=True)
        
        self.health_label = tk.Label(stats_frame, text="", font=('Arial', 11), 
                                    bg=self.colors['secondary'], fg=self.colors['light'])
        self.health_label.pack(anchor='w')
        
        self.mana_label = tk.Label(stats_frame, text="", font=('Arial', 11), 
                                  bg=self.colors['secondary'], fg=self.colors['light'])
        self.mana_label.pack(anchor='w')
        
        # Resources
        resources_frame = tk.Frame(parent, bg=self.colors['secondary'])
        resources_frame.pack(side='right', padx=10, pady=10)
        
        self.gold_label = tk.Label(resources_frame, text="", font=('Arial', 12, 'bold'), 
                                  bg=self.colors['secondary'], fg='#f1c40f')
        self.gold_label.pack()
        
        self.score_label = tk.Label(resources_frame, text="", font=('Arial', 10), 
                                   bg=self.colors['secondary'], fg=self.colors['light'])
        self.score_label.pack()
    
    def create_location_panel(self, parent):
        # Location info
        self.location_title = tk.Label(parent, text="", font=('Arial', 16, 'bold'), 
                                      bg=self.colors['secondary'], fg=self.colors['light'])
        self.location_title.pack(pady=10)
        
        desc_frame = tk.Frame(parent, bg=self.colors['primary'])
        desc_frame.pack(fill='x', padx=10, pady=5)
        
        self.location_desc = tk.Label(desc_frame, text="", font=('Arial', 11), 
                                     bg=self.colors['primary'], fg=self.colors['light'], 
                                     wraplength=550, justify='left')
        self.location_desc.pack(padx=10, pady=10)
        
        # Game log
        log_frame = tk.Frame(parent, bg=self.colors['secondary'])
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(log_frame, text="📜 Adventure Log", font=('Arial', 12, 'bold'), 
                bg=self.colors['secondary'], fg=self.colors['light']).pack()
        
        self.game_log = scrolledtext.ScrolledText(log_frame, height=12, font=('Arial', 10),
                                                 bg=self.colors['light'], fg=self.colors['primary'], wrap='word')
        self.game_log.pack(fill='both', expand=True, pady=5)
        
        self.add_to_log(f"Welcome, {self.current_player.name}! Your adventure begins...")
    
    def create_action_panel(self, parent):
        # Movement
        movement_frame = tk.LabelFrame(parent, text="🗺️ Travel", font=('Arial', 11, 'bold'),
                                      bg=self.colors['secondary'], fg=self.colors['light'])
        movement_frame.pack(fill='x', padx=5, pady=5)
        
        self.movement_buttons = []
        self.movement_frame = movement_frame
        
        # Actions
        action_frame = tk.LabelFrame(parent, text="⚡ Actions", font=('Arial', 11, 'bold'),
                                    bg=self.colors['secondary'], fg=self.colors['light'])
        action_frame.pack(fill='x', padx=5, pady=5)
        
        self.action_buttons = []
        self.action_frame = action_frame
        
        # Inventory
        inventory_frame = tk.LabelFrame(parent, text="🎒 Inventory", font=('Arial', 11, 'bold'),
                                       bg=self.colors['secondary'], fg=self.colors['light'])
        inventory_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.inventory_listbox = tk.Listbox(inventory_frame, height=8, font=('Arial', 9),
                                           bg=self.colors['light'], fg=self.colors['primary'])
        self.inventory_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Inventory buttons
        inv_button_frame = tk.Frame(inventory_frame, bg=self.colors['secondary'])
        inv_button_frame.pack(fill='x', padx=5, pady=5)
        
        use_btn = tk.Button(inv_button_frame, text="Use", command=self.use_selected_item,
                           font=('Arial', 9), bg=self.colors['success'], fg='white', width=8)
        use_btn.pack(side='left', padx=2)
        
        equip_btn = tk.Button(inv_button_frame, text="Equip", command=self.equip_selected_item,
                             font=('Arial', 9), bg=self.colors['accent'], fg='white', width=8)
        equip_btn.pack(side='left', padx=2)
        
        # Menu buttons
        menu_frame = tk.Frame(parent, bg=self.colors['secondary'])
        menu_frame.pack(fill='x', padx=5, pady=10)
        
        save_btn = tk.Button(menu_frame, text="💾 Save", command=self.save_game,
                            font=('Arial', 10), bg=self.colors['success'], fg='white', width=12)
        save_btn.pack(pady=2)
        
        stats_btn = tk.Button(menu_frame, text="📊 Stats", command=self.show_character_stats,
                             font=('Arial', 10), bg=self.colors['accent'], fg='white', width=12)
        stats_btn.pack(pady=2)
        
        quit_btn = tk.Button(menu_frame, text="🚪 Main Menu", command=self.return_to_main_menu,
                            font=('Arial', 10), bg=self.colors['danger'], fg='white', width=12)
        quit_btn.pack(pady=2)
    
    def update_display(self):
        # Update player info
        self.name_label.config(text=f"👤 {self.current_player.name}")
        self.level_label.config(text=f"Level {self.current_player.level}")
        
        self.health_label.config(text=f"❤️ Health: {self.current_player.health}/{self.current_player.max_health}")
        self.mana_label.config(text=f"🔮 Mana: {self.current_player.mana}/{self.current_player.max_mana}")
        
        self.gold_label.config(text=f"💰 {self.current_player.gold}")
        self.score_label.config(text=f"🏆 Score: {self.current_player.score}")
        
        # Update location
        location = LOCATIONS.get(self.current_player.current_location, {})
        self.location_title.config(text=location.get("name", "Unknown Location"))
        self.location_desc.config(text=location.get("description", "You are in an unknown place."))
        
        self.update_movement_buttons()
        self.update_action_buttons()
        self.update_inventory_display()
    
    def update_movement_buttons(self):
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
                           font=('Arial', 9), bg=self.colors['accent'], fg='white', width=18)
            btn.pack(pady=2, padx=5)
            self.movement_buttons.append(btn)
    
    def update_action_buttons(self):
        for btn in self.action_buttons:
            btn.destroy()
        self.action_buttons.clear()
        
        location = LOCATIONS.get(self.current_player.current_location, {})
        special_actions = location.get("special_actions", [])
        
        for action in special_actions:
            btn_text = action.replace("_", " ").title()
            
            btn = tk.Button(self.action_frame, text=btn_text,
                           command=lambda act=action: self.perform_special_action(act),
                           font=('Arial', 9), bg=self.colors['warning'], fg='white', width=18)
            btn.pack(pady=2, padx=5)
            self.action_buttons.append(btn)
    
    def update_inventory_display(self):
        self.inventory_listbox.delete(0, 'end')
        
        # Add equipped items
        if self.current_player.equipped_weapon:
            self.inventory_listbox.insert('end', f"🗡️ {self.current_player.equipped_weapon['name']} (equipped)")
        if self.current_player.equipped_armor:
            self.inventory_listbox.insert('end', f"🛡️ {self.current_player.equipped_armor['name']} (equipped)")
        
        # Add inventory items
        for item in self.current_player.inventory:
            icon = {"weapon": "⚔️", "armor": "🛡️", "consumable": "🧪"}.get(item["type"], "📦")
            self.inventory_listbox.insert('end', f"{icon} {item['name']}")
    
    def move_to_location(self, location):
        if location in LOCATIONS:
            self.current_player.current_location = location
            self.add_to_log(f"You travel to {LOCATIONS[location]['name']}")
            
            # Check for encounters
            encounter_chance = LOCATIONS[location].get("encounter_chance", 0)
            if random.random() < encounter_chance:
                self.trigger_random_encounter()
            
            self.update_display()
            self.save_game()
    
    def perform_special_action(self, action):
        if action == "shop":
            self.open_shop()
        elif action == "inn":
            self.rest_at_inn()
        elif action == "search_herbs":
            self.search_for_herbs()
        elif action == "challenge_dragon":
            self.challenge_boss("cave_dragon")
        else:
            self.add_to_log(f"You {action.replace('_', ' ')}...")
            if random.random() < 0.6:
                exp = random.randint(10, 30)
                result = self.current_player.gain_experience(exp)
                self.add_to_log(result)
        
        self.update_display()
        self.save_game()
    
    def trigger_random_encounter(self):
        location_enemies = {
            "forest": ["goblin", "wolf"],
            "cave": ["skeleton"],
            "deep_cave": ["cave_dragon"],
            "castle": ["skeleton"]
        }
        
        possible_enemies = location_enemies.get(self.current_player.current_location, ["goblin"])
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
        self.combat_window = tk.Toplevel(self.root)
        self.combat_window.title("⚔️ Combat!")
        self.combat_window.geometry("600x500")
        self.combat_window.configure(bg=self.colors['danger'])
        self.combat_window.grab_set()
        
        # Combat UI
        title_label = tk.Label(self.combat_window, text="⚔️ COMBAT ⚔️", 
                              font=('Arial', 20, 'bold'), bg=self.colors['danger'], fg='white')
        title_label.pack(pady=10)
        
        # Enemy info
        enemy_frame = tk.Frame(self.combat_window, bg=self.colors['danger'])
        enemy_frame.pack(pady=10)
        
        enemy_label = tk.Label(enemy_frame, text=f"🐉 {self.current_enemy.name}", 
                              font=('Arial', 16, 'bold'), bg=self.colors['danger'], fg='white')
        enemy_label.pack()
        
        self.enemy_health_label = tk.Label(enemy_frame, text="", font=('Arial', 12), 
                                          bg=self.colors['danger'], fg='white')
        self.enemy_health_label.pack()
        
        # Combat log
        log_frame = tk.Frame(self.combat_window, bg=self.colors['danger'])
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.combat_log = scrolledtext.ScrolledText(log_frame, height=10, font=('Arial', 10),
                                                   bg=self.colors['light'], fg=self.colors['primary'], wrap='word')
        self.combat_log.pack(fill='both', expand=True)
        
        # Combat actions
        action_frame = tk.Frame(self.combat_window, bg=self.colors['danger'])
        action_frame.pack(pady=10)
        
        actions = [
            ("⚔️ Attack", lambda: self.combat_action(CombatAction.ATTACK)),
            ("🛡️ Defend", lambda: self.combat_action(CombatAction.DEFEND)),
            ("🧪 Use Item", lambda: self.combat_action(CombatAction.USE_ITEM)),
            ("🏃 Run Away", lambda: self.combat_action(CombatAction.RUN))
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = tk.Button(action_frame, text=text, command=command,
                           font=('Arial', 11, 'bold'), width=12, height=2,
                           bg=self.colors['secondary'], fg='white')
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)
        
        self.update_combat_display()
        self.add_to_combat_log(f"Combat begins! You face the {self.current_enemy.name}!")
    
    def update_combat_display(self):
        if hasattr(self, 'enemy_health_label'):
            self.enemy_health_label.config(text=f"Health: {self.current_enemy.health}/{self.current_enemy.max_health}")
    
    def add_to_combat_log(self, message):
        if hasattr(self, 'combat_log'):
            self.combat_log.insert('end', message + '\n')
            self.combat_log.see('end')
    
    def combat_action(self, action: CombatAction):
        if not self.combat_active:
            return
        
        # Player action
        if action == CombatAction.ATTACK:
            damage = max(1, self.current_player.attack - self.current_enemy.defense + random.randint(-3, 3))
            self.current_enemy.take_damage(damage)
            self.add_to_combat_log(f"You attack for {damage} damage!")
            
        elif action == CombatAction.USE_ITEM:
            consumables = [item for item in self.current_player.inventory if item["type"] == "consumable"]
            if consumables:
                item = consumables[0]
                result = self.current_player.use_item(item["name"])
                self.add_to_combat_log(result)
            else:
                self.add_to_combat_log("No usable items!")
                
        elif action == CombatAction.RUN:
            if random.random() < 0.6:
                self.add_to_combat_log("You successfully escaped!")
                self.end_combat(False)
                return
            else:
                self.add_to_combat_log("You couldn't escape!")
        
        # Check if enemy is defeated
        if self.current_enemy.health <= 0:
            self.end_combat(True)
            return
        
        # Enemy turn
        damage = max(1, self.current_enemy.attack - self.current_player.defense + random.randint(-2, 2))
        self.current_player.health -= damage
        self.add_to_combat_log(f"The {self.current_enemy.name} attacks for {damage} damage!")
        
        if self.current_player.health <= 0:
            self.current_player.health = 1
            self.add_to_combat_log("You have been defeated!")
            self.end_combat(False)
            return
        
        self.update_combat_display()
    
    def end_combat(self, victory: bool):
        self.combat_active = False
        
        if victory:
            self.add_to_combat_log(f"🎉 Victory! You defeated the {self.current_enemy.name}!")
            
            exp_reward = self.current_enemy.exp_reward
            gold_reward = self.current_enemy.gold_reward
            
            exp_result = self.current_player.gain_experience(exp_reward)
            self.current_player.gold += gold_reward
            self.current_player.score += exp_reward
            
            self.add_to_combat_log(f"Rewards: {exp_reward} EXP, {gold_reward} gold")
            self.add_to_log(f"🎉 Victory! Defeated {self.current_enemy.name}!")
            self.add_to_log(exp_result)
            
            # Quest completion
            if not self.current_player.quests["first_combat"]["completed"]:
                self.current_player.quests["first_combat"]["completed"] = True
                bonus_exp = self.current_player.quests["first_combat"]["reward"]
                self.current_player.gain_experience(bonus_exp)
                self.add_to_log("Quest completed: Win your first battle!")
        else:
            self.add_to_combat_log("💀 Defeat! You retreat to safety...")
            self.add_to_log("💀 You were defeated and retreated to the village.")
            self.current_player.current_location = "village"
        
        self.combat_window.after(3000, self.close_combat_window)
    
    def close_combat_window(self):
        if hasattr(self, 'combat_window'):
            self.combat_window.destroy()
        self.update_display()
        self.save_game()
    
    def search_for_herbs(self):
        if random.random() < 0.7:
            herb = {"name": "Magic Herb", "type": "consumable", "value": 30}
            result = self.current_player.add_item(herb)
            self.add_to_log(result)
            
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
    
    def open_shop(self):
        shop_window = tk.Toplevel(self.root)
        shop_window.title("🏪 Village Shop")
        shop_window.geometry("400x300")
        shop_window.configure(bg=self.colors['warning'])
        shop_window.grab_set()
        
        title_label = tk.Label(shop_window, text="🏪 Village Shop", 
                              font=('Arial', 16, 'bold'), bg=self.colors['warning'], fg='white')
        title_label.pack(pady=10)
        
        gold_label = tk.Label(shop_window, text=f"Your Gold: {self.current_player.gold}", 
                             font=('Arial', 12), bg=self.colors['warning'], fg='white')
        gold_label.pack(pady=5)
        
        shop_items = [
            {"name": "Health Potion", "type": "consumable", "value": 50, "price": 25},
            {"name": "Iron Sword", "type": "weapon", "value": 15, "price": 100},
            {"name": "Steel Shield", "type": "armor", "value": 15, "price": 120}
        ]
        
        items_frame = tk.Frame(shop_window, bg=self.colors['warning'])
        items_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        items_listbox = tk.Listbox(items_frame, font=('Arial', 10), height=6)
        items_listbox.pack(fill='both', expand=True)
        
        for item in shop_items:
            items_listbox.insert('end', f"{item['name']} - {item['price']} gold")
        
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
                else:
                    messagebox.showwarning("Insufficient Gold", "You don't have enough gold!")
        
        button_frame = tk.Frame(shop_window, bg=self.colors['warning'])
        button_frame.pack(pady=10)
        
        buy_btn = tk.Button(button_frame, text="Buy Selected", command=buy_item,
                           font=('Arial', 11), bg=self.colors['success'], fg='white')
        buy_btn.pack(side='left', padx=10)
        
        close_btn = tk.Button(button_frame, text="Close", command=shop_window.destroy,
                             font=('Arial', 11), bg=self.colors['danger'], fg='white')
        close_btn.pack(side='left', padx=10)
    
    def use_selected_item(self):
        selection = self.inventory_listbox.curselection()
        if selection:
            item_text = self.inventory_listbox.get(selection[0])
            if "(equipped)" in item_text:
                messagebox.showinfo("Cannot Use", "This item is currently equipped!")
                return
            
            item_name = item_text.split(' ', 1)[1] if ' ' in item_text else item_text
            
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
    
    def equip_selected_item(self):
        selection = self.inventory_listbox.curselection()
        if selection:
            item_text = self.inventory_listbox.get(selection[0])
            if "(equipped)" in item_text:
                messagebox.showinfo("Already Equipped", "This item is already equipped!")
                return
            
            item_name = item_text.split(' ', 1)[1] if ' ' in item_text else item_text
            
            for item in self.current_player.inventory:
                if item["name"] == item_name:
                    if item["type"] in ["weapon", "armor"]:
                        result = self.current_player.equip_item(item["name"])
                        self.add_to_log(result)
                        self.update_display()
                        self.save_game()
                        return
                    else:
                        messagebox.showinfo("Cannot Equip", "This item cannot be equipped!")
                        return
    
    def show_character_stats(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Character Statistics")
        stats_window.geometry("400x500")
        stats_window.configure(bg=self.colors['primary'])
        stats_window.grab_set()
        
        title_label = tk.Label(stats_window, text=f"📊 {self.current_player.name}'s Stats", 
                              font=('Arial', 16, 'bold'), bg=self.colors['primary'], fg=self.colors['light'])
        title_label.pack(pady=10)
        
        stats_frame = tk.Frame(stats_window, bg=self.colors['secondary'])
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

Active Quests:
"""
        
        for quest_name, quest_data in self.current_player.quests.items():
            if not quest_data["completed"]:
                progress = ""
                if "progress" in quest_data and "target" in quest_data:
                    progress = f" ({quest_data['progress']}/{quest_data['target']})"
                stats_text += f"• {quest_data['description']}{progress}\n"
        
        stats_label = tk.Label(stats_frame, text=stats_text, font=('Arial', 10), 
                              bg=self.colors['secondary'], fg=self.colors['light'], justify='left')
        stats_label.pack(padx=20, pady=20)
        
        close_btn = tk.Button(stats_window, text="Close", command=stats_window.destroy,
                             font=('Arial', 12), bg=self.colors['accent'], fg='white')
        close_btn.pack(pady=10)
    
    def add_to_log(self, message):
        self.game_log.insert('end', message + '\n')
        self.game_log.see('end')
    
    def save_game(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            inventory_json = json.dumps(self.current_player.inventory)
            quests_json = json.dumps(self.current_player.quests)
            skills_json = json.dumps(self.current_player.skills)
            
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
                self.current_player.gold, skills_json, "[]"
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
                (id, name, health, max_health, attack, defense, level, experience, 
                 score, current_location, inventory_json, quests_json, gold, 
                 skills_json, achievements_json) = player_data
                
                player = Player(name, health, max_health, attack, defense, level, experience, score, gold)
                player.current_location = current_location or "village"
                
                if inventory_json:
                    player.inventory = json.loads(inventory_json)
                if quests_json:
                    player.quests = json.loads(quests_json)
                if skills_json:
                    player.skills = json.loads(skills_json)
                
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
    app = SimpleAdventureGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
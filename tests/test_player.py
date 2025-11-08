"""
Unit tests for Player class
"""
import unittest
import sys
sys.path.insert(0, '..')

from player import Player


class TestPlayer(unittest.TestCase):
    """Test cases for Player class"""
    
    def setUp(self):
        """Set up test player"""
        self.player = Player("TestHero")
    
    def test_player_initialization(self):
        """Test player is initialized correctly"""
        self.assertEqual(self.player.name, "TestHero")
        self.assertEqual(self.player.health, 100)
        self.assertEqual(self.player.max_health, 100)
        self.assertEqual(self.player.base_attack, 20)
        self.assertEqual(self.player.base_defense, 5)
        self.assertEqual(self.player.level, 1)
        self.assertEqual(self.player.gold, 50)
    
    def test_add_item(self):
        """Test adding items to inventory"""
        item = {"name": "Health Potion", "type": "consumable", "value": 50}
        self.player.add_item(item)
        self.assertEqual(len(self.player.inventory), 1)
        self.assertEqual(self.player.inventory[0]["name"], "Health Potion")
    
    def test_remove_item(self):
        """Test removing items from inventory"""
        item = {"name": "Health Potion", "type": "consumable", "value": 50}
        self.player.add_item(item)
        result = self.player.remove_item("Health Potion")
        self.assertTrue(result)
        self.assertEqual(len(self.player.inventory), 0)
    
    def test_use_consumable(self):
        """Test using consumable items"""
        self.player.health = 50
        item = {"name": "Health Potion", "type": "consumable", "value": 50}
        self.player.add_item(item)
        self.player.use_item("Health Potion")
        self.assertEqual(self.player.health, 100)
        self.assertEqual(len(self.player.inventory), 0)
    
    def test_equip_weapon(self):
        """Test equipping weapons"""
        weapon = {"name": "Iron Sword", "type": "weapon", "value": 15}
        self.player.add_item(weapon)
        self.player.equip_item("Iron Sword")
        self.assertEqual(self.player.attack, 35)  # 20 base + 15 weapon
        self.assertIsNotNone(self.player.equipped_weapon)
    
    def test_equip_armor(self):
        """Test equipping armor"""
        armor = {"name": "Steel Shield", "type": "armor", "value": 10}
        self.player.add_item(armor)
        self.player.equip_item("Steel Shield")
        self.assertEqual(self.player.defense, 15)  # 5 base + 10 armor
        self.assertIsNotNone(self.player.equipped_armor)
    
    def test_unequip_weapon(self):
        """Test unequipping weapons"""
        weapon = {"name": "Iron Sword", "type": "weapon", "value": 15}
        self.player.add_item(weapon)
        self.player.equip_item("Iron Sword")
        self.player.unequip_item("weapon")
        self.assertEqual(self.player.attack, 20)  # Back to base
        self.assertIsNone(self.player.equipped_weapon)
        self.assertEqual(len(self.player.inventory), 1)
    
    def test_gain_experience(self):
        """Test gaining experience"""
        initial_exp = self.player.experience
        self.player.gain_experience(50)
        self.assertEqual(self.player.experience, initial_exp + 50)
    
    def test_level_up(self):
        """Test leveling up"""
        self.player.experience = 100
        initial_level = self.player.level
        self.player.level_up()
        self.assertEqual(self.player.level, initial_level + 1)
        self.assertGreater(self.player.max_health, 100)
        self.assertGreater(self.player.base_attack, 20)
        self.assertGreater(self.player.base_defense, 5)
    
    def test_drop_item(self):
        """Test dropping items"""
        item = {"name": "Gold Coin", "type": "currency", "value": 1}
        self.player.add_item(item)
        self.player.drop_item("Gold Coin")
        self.assertEqual(len(self.player.inventory), 0)
    
    def test_quest_completion(self):
        """Test quest completion"""
        self.assertFalse(self.player.quests["first_combat"]["completed"])
        self.player.check_quest_completion("combat")
        self.assertTrue(self.player.quests["first_combat"]["completed"])


if __name__ == '__main__':
    unittest.main()

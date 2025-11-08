"""
Unit tests for Combat System
"""
import unittest
import sys
sys.path.insert(0, '..')

from player import Player
from combat import CombatSystem


class TestCombatSystem(unittest.TestCase):
    """Test cases for Combat System"""
    
    def setUp(self):
        """Set up test player and enemy"""
        self.player = Player("TestHero")
        self.enemy_data = {
            "name": "Goblin",
            "health": 40,
            "attack": 10,
            "defense": 2,
            "exp_reward": 15,
            "gold_reward": 8
        }
        self.combat = CombatSystem(self.player, self.enemy_data, "normal")
    
    def test_combat_initialization(self):
        """Test combat system initializes correctly"""
        self.assertEqual(self.combat.player.name, "TestHero")
        self.assertEqual(self.combat.enemy["name"], "Goblin")
        self.assertEqual(self.combat.turn_count, 0)
    
    def test_calculate_damage(self):
        """Test damage calculation"""
        damage, is_crit = self.combat.calculate_damage(20, 5, True)
        self.assertGreater(damage, 0)
        self.assertIsInstance(is_crit, bool)
    
    def test_player_attack(self):
        """Test player attack"""
        initial_enemy_health = self.combat.enemy["health"]
        self.combat.player_attack()
        self.assertLess(self.combat.enemy["health"], initial_enemy_health)
    
    def test_enemy_attack(self):
        """Test enemy attack"""
        initial_player_health = self.player.health
        self.combat.enemy_attack()
        # Player might dodge, so health could be same or less
        self.assertLessEqual(self.player.health, initial_player_health)
    
    def test_player_defend(self):
        """Test player defend action"""
        initial_health = self.player.health
        self.combat.player_defend()
        # Damage should be reduced
        damage_taken = initial_health - self.player.health
        self.assertLessEqual(damage_taken, 10)  # Should be less than normal attack
    
    def test_difficulty_modifiers(self):
        """Test difficulty affects enemy stats"""
        easy_combat = CombatSystem(self.player, self.enemy_data.copy(), "easy")
        hard_combat = CombatSystem(self.player, self.enemy_data.copy(), "hard")
        
        self.assertLess(easy_combat.enemy["health"], hard_combat.enemy["health"])
        self.assertLess(easy_combat.enemy["attack"], hard_combat.enemy["attack"])
    
    def test_victory_rewards(self):
        """Test victory grants rewards"""
        initial_exp = self.player.experience
        initial_gold = self.player.gold
        
        self.combat.victory()
        
        self.assertGreater(self.player.experience, initial_exp)
        self.assertGreater(self.player.gold, initial_gold)
    
    def test_defeat_penalty(self):
        """Test defeat applies penalties"""
        self.player.gold = 100
        initial_gold = self.player.gold
        
        self.combat.defeat()
        
        self.assertLess(self.player.gold, initial_gold)
        self.assertEqual(self.player.current_location, "village")


if __name__ == '__main__':
    unittest.main()

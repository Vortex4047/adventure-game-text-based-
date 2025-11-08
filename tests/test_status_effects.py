"""
Unit tests for Status Effects System
"""
import unittest
import sys
sys.path.insert(0, '..')

from player import Player
from status_effects import (
    PoisonEffect, StunEffect, StrengthBuffEffect,
    DefenseBuffEffect, StatusEffectManager
)


class TestStatusEffects(unittest.TestCase):
    """Test cases for Status Effects"""
    
    def setUp(self):
        """Set up test player"""
        self.player = Player("TestHero")
    
    def test_poison_effect(self):
        """Test poison effect deals damage"""
        poison = PoisonEffect(damage=5, duration=3)
        initial_health = self.player.health
        poison.apply(self.player)
        self.assertEqual(self.player.health, initial_health - 5)
    
    def test_poison_duration(self):
        """Test poison effect duration"""
        poison = PoisonEffect(damage=5, duration=3)
        self.assertTrue(poison.tick())
        self.assertTrue(poison.tick())
        self.assertFalse(poison.tick())
    
    def test_strength_buff(self):
        """Test strength buff increases attack"""
        buff = StrengthBuffEffect(multiplier=1.3, duration=3)
        initial_attack = self.player.base_attack
        buff.apply(self.player)
        self.assertGreater(self.player.base_attack, initial_attack)
    
    def test_strength_buff_removal(self):
        """Test strength buff removal restores attack"""
        buff = StrengthBuffEffect(multiplier=1.3, duration=3)
        initial_attack = self.player.base_attack
        buff.apply(self.player)
        buff.remove(self.player)
        self.assertEqual(self.player.base_attack, initial_attack)
    
    def test_defense_buff(self):
        """Test defense buff increases defense"""
        buff = DefenseBuffEffect(multiplier=1.3, duration=3)
        initial_defense = self.player.base_defense
        buff.apply(self.player)
        self.assertGreater(self.player.base_defense, initial_defense)
    
    def test_status_effect_manager(self):
        """Test status effect manager"""
        manager = StatusEffectManager()
        poison = PoisonEffect(damage=5, duration=3)
        
        manager.add_effect(poison, self.player)
        self.assertEqual(len(manager.effects), 1)
        self.assertTrue(manager.has_effect("Poison"))
    
    def test_manager_process_effects(self):
        """Test manager processes effects"""
        manager = StatusEffectManager()
        poison = PoisonEffect(damage=5, duration=2)
        manager.add_effect(poison, self.player)
        
        initial_health = self.player.health
        manager.process_effects(self.player)
        self.assertLess(self.player.health, initial_health)
        
        # After 2 ticks, effect should be removed
        manager.process_effects(self.player)
        self.assertEqual(len(manager.effects), 0)
    
    def test_manager_clear_all(self):
        """Test clearing all effects"""
        manager = StatusEffectManager()
        manager.add_effect(PoisonEffect(), self.player)
        manager.add_effect(StunEffect(), self.player)
        
        manager.clear_all(self.player)
        self.assertEqual(len(manager.effects), 0)
    
    def test_effect_serialization(self):
        """Test effect can be saved and loaded"""
        poison = PoisonEffect(damage=5, duration=3)
        data = poison.to_dict()
        
        self.assertEqual(data["name"], "Poison")
        self.assertEqual(data["duration"], 3)
        self.assertEqual(data["damage"], 5)


if __name__ == '__main__':
    unittest.main()

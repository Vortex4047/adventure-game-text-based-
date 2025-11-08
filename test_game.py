"""
Quick test script to verify game functionality
"""
import sys

def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    try:
        import constants
        import config
        import colors
        import status_effects
        import achievements
        import random_events
        import item_system
        import player
        import combat
        import shop
        import database
        import utils
        import main
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_player_creation():
    """Test player creation"""
    print("\nTesting player creation...")
    try:
        from player import Player
        from achievements import AchievementManager
        
        player = Player("TestHero", difficulty="normal")
        player.achievement_manager = AchievementManager()
        
        assert player.name == "TestHero"
        assert player.health == 100
        assert player.level == 1
        print("✅ Player creation successful!")
        return True
    except Exception as e:
        print(f"❌ Player creation error: {e}")
        return False

def test_status_effects():
    """Test status effects"""
    print("\nTesting status effects...")
    try:
        from player import Player
        from status_effects import PoisonEffect, StrengthBuffEffect
        
        player = Player("TestHero")
        
        # Test poison
        poison = PoisonEffect(damage=5, duration=3)
        player.status_effect_manager.add_effect(poison, player)
        assert player.status_effect_manager.has_effect("Poison")
        
        # Test strength buff
        buff = StrengthBuffEffect()
        initial_attack = player.base_attack
        buff.apply(player)
        assert player.base_attack > initial_attack
        
        print("✅ Status effects working!")
        return True
    except Exception as e:
        print(f"❌ Status effects error: {e}")
        return False

def test_achievements():
    """Test achievements"""
    print("\nTesting achievements...")
    try:
        from player import Player
        from achievements import AchievementManager
        
        player = Player("TestHero")
        player.achievement_manager = AchievementManager()
        player.enemies_defeated = 10
        
        # Check achievement
        result = player.achievement_manager.check_achievement("warrior", player)
        
        print("✅ Achievements working!")
        return True
    except Exception as e:
        print(f"❌ Achievements error: {e}")
        return False

def test_colors():
    """Test color system"""
    print("\nTesting color system...")
    try:
        from colors import colored, Colors, success, error
        
        text = colored("Test", Colors.GREEN)
        success_text = success("Success")
        error_text = error("Error")
        
        print("✅ Color system working!")
        return True
    except Exception as e:
        print(f"❌ Color system error: {e}")
        return False

def test_random_events():
    """Test random events"""
    print("\nTesting random events...")
    try:
        from player import Player
        from random_events import RandomEventManager, TreasureEvent
        
        player = Player("TestHero")
        manager = RandomEventManager()
        
        # Test treasure event
        event = TreasureEvent()
        initial_gold = player.gold
        event.trigger(player)
        assert player.gold > initial_gold
        
        print("✅ Random events working!")
        return True
    except Exception as e:
        print(f"❌ Random events error: {e}")
        return False

def test_item_system():
    """Test item system"""
    print("\nTesting item system...")
    try:
        from item_system import ItemGenerator, EnhancedItem
        
        # Generate weapon
        weapon = ItemGenerator.generate_weapon(level=5)
        assert weapon.type == "weapon"
        assert weapon.value > 0
        
        # Generate armor
        armor = ItemGenerator.generate_armor(level=5)
        assert armor.type == "armor"
        
        print("✅ Item system working!")
        return True
    except Exception as e:
        print(f"❌ Item system error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("🧪 Running Adventure Game Tests")
    print("="*50)
    
    tests = [
        test_imports,
        test_player_creation,
        test_status_effects,
        test_achievements,
        test_colors,
        test_random_events,
        test_item_system,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*50)
    
    if failed == 0:
        print("✅ All tests passed! Game is ready to play!")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

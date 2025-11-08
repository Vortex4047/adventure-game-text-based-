"""
Random events system for dynamic gameplay
"""
import random
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RandomEvent:
    """Base class for random events"""
    
    def __init__(self, name: str, description: str, chance: float = 0.1):
        self.name = name
        self.description = description
        self.chance = chance
    
    def can_trigger(self, player: Any, location: str) -> bool:
        """Check if event can trigger"""
        return random.random() < self.chance
    
    def trigger(self, player: Any) -> None:
        """Execute the event"""
        print(f"\n✨ Random Event: {self.name}")
        print(f"   {self.description}")
        logger.info(f"Random event triggered: {self.name}")


class TreasureEvent(RandomEvent):
    """Find random treasure"""
    
    def __init__(self):
        super().__init__(
            "Hidden Treasure",
            "You stumble upon a hidden treasure!",
            chance=0.15
        )
    
    def trigger(self, player: Any) -> None:
        super().trigger(player)
        gold = random.randint(20, 50)
        player.gold += gold
        print(f"   💰 You found {gold} gold!")
        logger.info(f"{player.name} found {gold} gold from random event")


class MerchantEvent(RandomEvent):
    """Encounter traveling merchant"""
    
    def __init__(self):
        super().__init__(
            "Traveling Merchant",
            "A traveling merchant offers you a special deal!",
            chance=0.10
        )
    
    def trigger(self, player: Any) -> None:
        super().trigger(player)
        
        items = [
            {"name": "Health Potion", "price": 15, "value": 50, "type": "consumable"},
            {"name": "Magic Herb", "price": 10, "value": 30, "type": "consumable"},
        ]
        
        item = random.choice(items)
        print(f"   🛒 {item['name']} for only {item['price']} gold (normally 25g)!")
        
        if player.gold >= item["price"]:
            choice = input("   Buy it? (y/n): ").strip().lower()
            if choice == 'y':
                player.gold -= item["price"]
                player.add_item({
                    "name": item["name"],
                    "type": item["type"],
                    "value": item["value"],
                    "description": f"Bought from traveling merchant"
                })
                print(f"   ✅ Purchased {item['name']}!")
                logger.info(f"{player.name} bought {item['name']} from merchant")
        else:
            print(f"   ❌ Not enough gold!")


class HealingSpringEvent(RandomEvent):
    """Find healing spring"""
    
    def __init__(self):
        super().__init__(
            "Healing Spring",
            "You discover a magical healing spring!",
            chance=0.12
        )
    
    def trigger(self, player: Any) -> None:
        super().trigger(player)
        
        if player.health < player.max_health:
            heal_amount = min(30, player.max_health - player.health)
            player.health += heal_amount
            print(f"   💚 You restored {heal_amount} health!")
            logger.info(f"{player.name} healed {heal_amount} HP from spring")
        else:
            print(f"   💚 You're already at full health!")


class AmbushEvent(RandomEvent):
    """Enemy ambush"""
    
    def __init__(self):
        super().__init__(
            "Ambush!",
            "You've been ambushed by enemies!",
            chance=0.08
        )
    
    def can_trigger(self, player: Any, location: str) -> bool:
        """Only trigger in dangerous locations"""
        dangerous_locations = ["forest", "deep_forest", "cave", "deep_cave"]
        return location in dangerous_locations and super().can_trigger(player, location)
    
    def trigger(self, player: Any) -> None:
        print(f"\n⚠️  Random Event: {self.name}")
        print(f"   {self.description}")
        print(f"   💢 Prepare for combat!")
        logger.info(f"Ambush event triggered for {player.name}")
        # Combat will be handled by the caller


class WisdomEvent(RandomEvent):
    """Gain bonus experience"""
    
    def __init__(self):
        super().__init__(
            "Ancient Wisdom",
            "You find an ancient tome and gain knowledge!",
            chance=0.10
        )
    
    def trigger(self, player: Any) -> None:
        super().trigger(player)
        exp = random.randint(15, 30)
        player.gain_experience(exp)
        print(f"   📚 You gained {exp} bonus experience!")
        logger.info(f"{player.name} gained {exp} EXP from wisdom event")


class CurseEvent(RandomEvent):
    """Temporary debuff"""
    
    def __init__(self):
        super().__init__(
            "Ancient Curse",
            "You trigger an ancient curse!",
            chance=0.05
        )
    
    def trigger(self, player: Any) -> None:
        super().trigger(player)
        
        from status_effects import PoisonEffect
        
        poison = PoisonEffect(damage=3, duration=2)
        player.status_effect_manager.add_effect(poison, player)
        print(f"   🧪 You've been poisoned!")
        logger.info(f"{player.name} cursed with poison")


class LuckyFindEvent(RandomEvent):
    """Find rare item"""
    
    def __init__(self):
        super().__init__(
            "Lucky Find",
            "You found something valuable!",
            chance=0.08
        )
    
    def trigger(self, player: Any) -> None:
        super().trigger(player)
        
        items = [
            {"name": "Rare Gem", "type": "misc", "value": 100, "description": "A valuable gemstone"},
            {"name": "Ancient Coin", "type": "currency", "value": 50, "description": "An old but valuable coin"},
            {"name": "Magic Crystal", "type": "misc", "value": 75, "description": "A glowing crystal"},
        ]
        
        item = random.choice(items)
        player.add_item(item)
        print(f"   ✨ You found: {item['name']}!")
        logger.info(f"{player.name} found {item['name']} from lucky event")


class RandomEventManager:
    """Manages random events"""
    
    def __init__(self):
        self.events = [
            TreasureEvent(),
            MerchantEvent(),
            HealingSpringEvent(),
            AmbushEvent(),
            WisdomEvent(),
            CurseEvent(),
            LuckyFindEvent(),
        ]
        logger.info("Random event manager initialized")
    
    def check_for_event(self, player: Any, location: str) -> Optional[RandomEvent]:
        """Check if a random event should trigger"""
        # Shuffle events for randomness
        events = self.events.copy()
        random.shuffle(events)
        
        for event in events:
            if event.can_trigger(player, location):
                return event
        
        return None
    
    def trigger_event(self, player: Any, location: str) -> bool:
        """Try to trigger a random event"""
        event = self.check_for_event(player, location)
        
        if event:
            event.trigger(player)
            
            # Special handling for ambush
            if isinstance(event, AmbushEvent):
                return True  # Signal that combat should start
        
        return False

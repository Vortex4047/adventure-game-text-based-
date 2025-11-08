"""
Achievement system for tracking player accomplishments
"""
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class Achievement:
    """Represents a single achievement"""
    
    def __init__(self, id: str, name: str, description: str, 
                 reward_exp: int = 0, reward_gold: int = 0):
        self.id = id
        self.name = name
        self.description = description
        self.reward_exp = reward_exp
        self.reward_gold = reward_gold
        self.unlocked = False
        self.progress = 0
        self.target = 1
    
    def unlock(self) -> bool:
        """Unlock the achievement"""
        if not self.unlocked:
            self.unlocked = True
            logger.info(f"Achievement unlocked: {self.name}")
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "unlocked": self.unlocked,
            "progress": self.progress,
            "target": self.target
        }


class AchievementManager:
    """Manages all achievements"""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self._initialize_achievements()
    
    def _initialize_achievements(self) -> None:
        """Initialize all achievements"""
        achievements_data = [
            # Combat Achievements
            {
                "id": "first_blood",
                "name": "First Blood",
                "description": "Win your first battle",
                "reward_exp": 25,
                "reward_gold": 10
            },
            {
                "id": "warrior",
                "name": "Warrior",
                "description": "Defeat 10 enemies",
                "reward_exp": 100,
                "reward_gold": 50
            },
            {
                "id": "veteran",
                "name": "Veteran",
                "description": "Defeat 50 enemies",
                "reward_exp": 300,
                "reward_gold": 150
            },
            {
                "id": "legend",
                "name": "Legend",
                "description": "Defeat 100 enemies",
                "reward_exp": 500,
                "reward_gold": 300
            },
            
            # Boss Achievements
            {
                "id": "dragon_slayer",
                "name": "Dragon Slayer",
                "description": "Defeat the Cave Dragon",
                "reward_exp": 200,
                "reward_gold": 100
            },
            {
                "id": "guardian_vanquisher",
                "name": "Guardian Vanquisher",
                "description": "Defeat the Forest Guardian",
                "reward_exp": 150,
                "reward_gold": 75
            },
            
            # Wealth Achievements
            {
                "id": "wealthy",
                "name": "Wealthy",
                "description": "Accumulate 1000 gold",
                "reward_exp": 100,
                "reward_gold": 0
            },
            {
                "id": "tycoon",
                "name": "Tycoon",
                "description": "Accumulate 5000 gold",
                "reward_exp": 300,
                "reward_gold": 0
            },
            
            # Level Achievements
            {
                "id": "apprentice",
                "name": "Apprentice",
                "description": "Reach level 5",
                "reward_exp": 50,
                "reward_gold": 25
            },
            {
                "id": "expert",
                "name": "Expert",
                "description": "Reach level 10",
                "reward_exp": 150,
                "reward_gold": 75
            },
            {
                "id": "master",
                "name": "Master",
                "description": "Reach level 20",
                "reward_exp": 500,
                "reward_gold": 250
            },
            
            # Collection Achievements
            {
                "id": "collector",
                "name": "Collector",
                "description": "Have 10 items in inventory",
                "reward_exp": 50,
                "reward_gold": 25
            },
            {
                "id": "hoarder",
                "name": "Hoarder",
                "description": "Have 20 items in inventory",
                "reward_exp": 100,
                "reward_gold": 50
            },
            
            # Exploration Achievements
            {
                "id": "explorer",
                "name": "Explorer",
                "description": "Visit all locations",
                "reward_exp": 100,
                "reward_gold": 50
            },
            
            # Shopping Achievements
            {
                "id": "shopaholic",
                "name": "Shopaholic",
                "description": "Buy 20 items from the shop",
                "reward_exp": 75,
                "reward_gold": 0
            },
            
            # Survival Achievements
            {
                "id": "survivor",
                "name": "Survivor",
                "description": "Win a battle with less than 10% health",
                "reward_exp": 100,
                "reward_gold": 50
            },
            {
                "id": "untouchable",
                "name": "Untouchable",
                "description": "Win 5 battles without taking damage",
                "reward_exp": 200,
                "reward_gold": 100
            },
        ]
        
        for data in achievements_data:
            achievement = Achievement(**data)
            self.achievements[achievement.id] = achievement
    
    def check_achievement(self, achievement_id: str, player: Any) -> bool:
        """Check and unlock achievement if conditions met"""
        if achievement_id not in self.achievements:
            return False
        
        achievement = self.achievements[achievement_id]
        
        if achievement.unlocked:
            return False
        
        # Check conditions based on achievement type
        unlocked = False
        
        if achievement_id == "first_blood":
            unlocked = True  # Called after first combat win
        
        elif achievement_id == "warrior":
            if hasattr(player, 'enemies_defeated') and player.enemies_defeated >= 10:
                unlocked = True
        
        elif achievement_id == "veteran":
            if hasattr(player, 'enemies_defeated') and player.enemies_defeated >= 50:
                unlocked = True
        
        elif achievement_id == "legend":
            if hasattr(player, 'enemies_defeated') and player.enemies_defeated >= 100:
                unlocked = True
        
        elif achievement_id == "wealthy":
            if player.gold >= 1000:
                unlocked = True
        
        elif achievement_id == "tycoon":
            if player.gold >= 5000:
                unlocked = True
        
        elif achievement_id == "apprentice":
            if player.level >= 5:
                unlocked = True
        
        elif achievement_id == "expert":
            if player.level >= 10:
                unlocked = True
        
        elif achievement_id == "master":
            if player.level >= 20:
                unlocked = True
        
        elif achievement_id == "collector":
            if len(player.inventory) >= 10:
                unlocked = True
        
        elif achievement_id == "hoarder":
            if len(player.inventory) >= 20:
                unlocked = True
        
        elif achievement_id == "shopaholic":
            if hasattr(player, 'items_purchased') and player.items_purchased >= 20:
                unlocked = True
        
        if unlocked:
            achievement.unlock()
            self._grant_rewards(achievement, player)
            print(f"\n🏆 Achievement Unlocked: {achievement.name}")
            print(f"   {achievement.description}")
            return True
        
        return False
    
    def _grant_rewards(self, achievement: Achievement, player: Any) -> None:
        """Grant achievement rewards"""
        if achievement.reward_exp > 0:
            player.gain_experience(achievement.reward_exp)
            print(f"   Reward: {achievement.reward_exp} EXP", end="")
        
        if achievement.reward_gold > 0:
            player.gold += achievement.reward_gold
            if achievement.reward_exp > 0:
                print(f", {achievement.reward_gold} gold")
            else:
                print(f"   Reward: {achievement.reward_gold} gold")
        
        if achievement.reward_exp == 0 and achievement.reward_gold == 0:
            print()
    
    def get_unlocked_count(self) -> int:
        """Get number of unlocked achievements"""
        return sum(1 for a in self.achievements.values() if a.unlocked)
    
    def get_total_count(self) -> int:
        """Get total number of achievements"""
        return len(self.achievements)
    
    def display_achievements(self) -> None:
        """Display all achievements"""
        print(f"\n{'='*50}")
        print(f"🏆 Achievements ({self.get_unlocked_count()}/{self.get_total_count()})")
        print(f"{'='*50}")
        
        categories = {
            "Combat": ["first_blood", "warrior", "veteran", "legend"],
            "Bosses": ["dragon_slayer", "guardian_vanquisher"],
            "Wealth": ["wealthy", "tycoon"],
            "Levels": ["apprentice", "expert", "master"],
            "Collection": ["collector", "hoarder"],
            "Exploration": ["explorer"],
            "Shopping": ["shopaholic"],
            "Survival": ["survivor", "untouchable"]
        }
        
        for category, achievement_ids in categories.items():
            print(f"\n{category}:")
            for aid in achievement_ids:
                if aid in self.achievements:
                    achievement = self.achievements[aid]
                    status = "✅" if achievement.unlocked else "🔒"
                    print(f"  {status} {achievement.name}")
                    print(f"     {achievement.description}")
        
        print(f"{'='*50}\n")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving"""
        return {
            aid: achievement.to_dict() 
            for aid, achievement in self.achievements.items()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load from dictionary"""
        for aid, achievement_data in data.items():
            if aid in self.achievements:
                self.achievements[aid].unlocked = achievement_data.get("unlocked", False)
                self.achievements[aid].progress = achievement_data.get("progress", 0)

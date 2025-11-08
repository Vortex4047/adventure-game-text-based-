"""
Status effects system for the adventure game
"""
from typing import Dict, Any, Optional
from constants import (
    POISON_DURATION, POISON_DAMAGE,
    STUN_DURATION, BUFF_DURATION, BUFF_MULTIPLIER
)
import logging

logger = logging.getLogger(__name__)


class StatusEffect:
    """Base class for status effects"""
    
    def __init__(self, name: str, duration: int, description: str):
        self.name = name
        self.duration = duration
        self.description = description
        self.initial_duration = duration
    
    def apply(self, target: Any) -> None:
        """Apply the effect to the target"""
        pass
    
    def tick(self) -> bool:
        """Decrease duration and return True if effect is still active"""
        self.duration -= 1
        return self.duration > 0
    
    def remove(self, target: Any) -> None:
        """Remove the effect from the target"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving"""
        return {
            "name": self.name,
            "duration": self.duration,
            "description": self.description
        }


class PoisonEffect(StatusEffect):
    """Poison effect - deals damage over time"""
    
    def __init__(self, damage: int = POISON_DAMAGE, duration: int = POISON_DURATION):
        super().__init__("Poison", duration, f"Takes {damage} damage per turn")
        self.damage = damage
    
    def apply(self, target: Any) -> None:
        """Apply poison damage"""
        target.health -= self.damage
        print(f"🧪 {target.name} takes {self.damage} poison damage!")
        logger.info(f"{target.name} took {self.damage} poison damage")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["damage"] = self.damage
        return data


class StunEffect(StatusEffect):
    """Stun effect - prevents action for duration"""
    
    def __init__(self, duration: int = STUN_DURATION):
        super().__init__("Stun", duration, "Cannot act")
    
    def apply(self, target: Any) -> None:
        """Stun message"""
        print(f"💫 {target.name} is stunned and cannot act!")
        logger.info(f"{target.name} is stunned")


class StrengthBuffEffect(StatusEffect):
    """Strength buff - increases attack"""
    
    def __init__(self, multiplier: float = BUFF_MULTIPLIER, duration: int = BUFF_DURATION):
        super().__init__("Strength", duration, f"Attack increased by {int((multiplier-1)*100)}%")
        self.multiplier = multiplier
        self.original_attack: Optional[int] = None
    
    def apply(self, target: Any) -> None:
        """Apply strength buff"""
        if self.original_attack is None:
            self.original_attack = target.base_attack
            target.base_attack = int(target.base_attack * self.multiplier)
            print(f"💪 {target.name}'s attack increased to {target.base_attack}!")
            logger.info(f"{target.name} gained strength buff")
    
    def remove(self, target: Any) -> None:
        """Remove strength buff"""
        if self.original_attack is not None:
            target.base_attack = self.original_attack
            print(f"⏱️  {target.name}'s strength buff wore off.")
            logger.info(f"{target.name} lost strength buff")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["multiplier"] = self.multiplier
        data["original_attack"] = self.original_attack
        return data


class DefenseBuffEffect(StatusEffect):
    """Defense buff - increases defense"""
    
    def __init__(self, multiplier: float = BUFF_MULTIPLIER, duration: int = BUFF_DURATION):
        super().__init__("Defense", duration, f"Defense increased by {int((multiplier-1)*100)}%")
        self.multiplier = multiplier
        self.original_defense: Optional[int] = None
    
    def apply(self, target: Any) -> None:
        """Apply defense buff"""
        if self.original_defense is None:
            self.original_defense = target.base_defense
            target.base_defense = int(target.base_defense * self.multiplier)
            print(f"🛡️  {target.name}'s defense increased to {target.base_defense}!")
            logger.info(f"{target.name} gained defense buff")
    
    def remove(self, target: Any) -> None:
        """Remove defense buff"""
        if self.original_defense is not None:
            target.base_defense = self.original_defense
            print(f"⏱️  {target.name}'s defense buff wore off.")
            logger.info(f"{target.name} lost defense buff")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["multiplier"] = self.multiplier
        data["original_defense"] = self.original_defense
        return data


class StatusEffectManager:
    """Manages status effects for a character"""
    
    def __init__(self):
        self.effects: list[StatusEffect] = []
    
    def add_effect(self, effect: StatusEffect, target: Any) -> None:
        """Add a status effect"""
        # Remove existing effect of same type
        self.remove_effect_by_name(effect.name, target)
        self.effects.append(effect)
        logger.info(f"Added {effect.name} effect to {target.name}")
    
    def remove_effect(self, effect: StatusEffect, target: Any) -> None:
        """Remove a specific effect"""
        if effect in self.effects:
            effect.remove(target)
            self.effects.remove(effect)
            logger.info(f"Removed {effect.name} effect from {target.name}")
    
    def remove_effect_by_name(self, name: str, target: Any) -> bool:
        """Remove effect by name"""
        for effect in self.effects[:]:
            if effect.name == name:
                self.remove_effect(effect, target)
                return True
        return False
    
    def has_effect(self, name: str) -> bool:
        """Check if has specific effect"""
        return any(effect.name == name for effect in self.effects)
    
    def process_effects(self, target: Any) -> None:
        """Process all active effects"""
        for effect in self.effects[:]:
            # Apply effect
            if effect.name != "Stun":  # Stun doesn't apply damage
                effect.apply(target)
            
            # Tick duration
            if not effect.tick():
                self.remove_effect(effect, target)
    
    def clear_all(self, target: Any) -> None:
        """Clear all effects"""
        for effect in self.effects[:]:
            self.remove_effect(effect, target)
    
    def get_active_effects(self) -> list[str]:
        """Get list of active effect names"""
        return [f"{effect.name} ({effect.duration})" for effect in self.effects]
    
    def to_dict(self) -> list[Dict[str, Any]]:
        """Convert to dictionary for saving"""
        return [effect.to_dict() for effect in self.effects]
    
    @staticmethod
    def from_dict(data: list[Dict[str, Any]]) -> 'StatusEffectManager':
        """Load from dictionary"""
        manager = StatusEffectManager()
        for effect_data in data:
            effect_name = effect_data.get("name")
            duration = effect_data.get("duration", 0)
            
            if effect_name == "Poison":
                effect = PoisonEffect(
                    damage=effect_data.get("damage", POISON_DAMAGE),
                    duration=duration
                )
            elif effect_name == "Stun":
                effect = StunEffect(duration=duration)
            elif effect_name == "Strength":
                effect = StrengthBuffEffect(
                    multiplier=effect_data.get("multiplier", BUFF_MULTIPLIER),
                    duration=duration
                )
                effect.original_attack = effect_data.get("original_attack")
            elif effect_name == "Defense":
                effect = DefenseBuffEffect(
                    multiplier=effect_data.get("multiplier", BUFF_MULTIPLIER),
                    duration=duration
                )
                effect.original_defense = effect_data.get("original_defense")
            else:
                continue
            
            manager.effects.append(effect)
        
        return manager

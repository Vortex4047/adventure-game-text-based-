import logging
from typing import Any, Dict, List
from config import SHOP_ITEMS
from constants import SELL_PRICE_MULTIPLIER, SEPARATOR_LENGTH

logger = logging.getLogger(__name__)


class ShopSystem:
    def __init__(self, player: Any):
        self.player = player
        self.shop_items: List[Dict[str, Any]] = SHOP_ITEMS

    def display_shop_menu(self) -> None:
        """Display the shop main menu"""
        while True:
            print(f"\n{'='*SEPARATOR_LENGTH}")
            print(f"🏪 Village Shop")
            print(f"{'='*SEPARATOR_LENGTH}")
            print(f"💰 Your gold: {self.player.gold}")
            print("\n1. Buy Items")
            print("2. Sell Items")
            print("3. Leave Shop")
            
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == '1':
                    self.buy_items()
                elif choice == '2':
                    self.sell_items()
                elif choice == '3':
                    print("👋 Thanks for visiting!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-3.")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Invalid input.")
                continue

    def buy_items(self) -> None:
        """Buy items from the shop"""
        while True:
            print(f"\n{'─'*SEPARATOR_LENGTH}")
            print(f"🛒 Items for Sale (Your gold: {self.player.gold})")
            print(f"{'─'*SEPARATOR_LENGTH}")
            
            for i, item in enumerate(self.shop_items, 1):
                affordable = "✅" if self.player.gold >= item["price"] else "❌"
                print(f"{i}. {affordable} {item['name']} - {item['price']} gold")
                print(f"   {item['description']}")
            
            print("\n0. Go Back")
            
            try:
                choice = input("\nEnter item number to buy: ").strip()
                
                if choice == '0':
                    break
                
                if not choice.isdigit():
                    print("❌ Please enter a valid number.")
                    continue
                
                item_idx = int(choice) - 1
                
                if 0 <= item_idx < len(self.shop_items):
                    item = self.shop_items[item_idx]
                    
                    if self.player.gold >= item["price"]:
                        # Confirm purchase
                        confirm = input(f"Buy {item['name']} for {item['price']} gold? (y/n): ").strip().lower()
                        if confirm == 'y':
                            self.player.gold -= item["price"]
                            new_item = {
                                "name": item["name"],
                                "type": item["type"],
                                "value": item["value"],
                                "description": item["description"]
                            }
                            self.player.add_item(new_item)
                            self.player.items_purchased += 1
                            print(f"✅ Purchased {item['name']} for {item['price']} gold!")
                            logger.info(f"{self.player.name} purchased {item['name']}")
                            
                            # Check achievements
                            try:
                                if hasattr(self.player, 'achievement_manager'):
                                    self.player.achievement_manager.check_achievement("shopaholic", self.player)
                            except Exception as e:
                                logger.warning(f"Achievement check failed: {e}")
                        else:
                            print("❌ Purchase cancelled.")
                    else:
                        needed = item["price"] - self.player.gold
                        print(f"❌ Not enough gold! You need {needed} more gold.")
                else:
                    print("❌ Invalid item number!")
                    
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Invalid input.")
                continue

    def sell_items(self) -> None:
        """Sell items from inventory"""
        while True:
            if not self.player.inventory:
                print("\n❌ You have no items to sell!")
                break
            
            print(f"\n{'─'*SEPARATOR_LENGTH}")
            print(f"💼 Your Items (Sell for {int(SELL_PRICE_MULTIPLIER*100)}% value)")
            print(f"{'─'*SEPARATOR_LENGTH}")
            
            for i, item in enumerate(self.player.inventory, 1):
                sell_price = max(1, int(item.get("value", 0) * SELL_PRICE_MULTIPLIER))
                print(f"{i}. {item['name']} - {sell_price} gold")
                print(f"   {item.get('description', 'No description')}")
            
            print("\n0. Go Back")
            
            try:
                choice = input("\nEnter item number to sell: ").strip()
                
                if choice == '0':
                    break
                
                if not choice.isdigit():
                    print("❌ Please enter a valid number.")
                    continue
                
                item_idx = int(choice) - 1
                
                if 0 <= item_idx < len(self.player.inventory):
                    item = self.player.inventory[item_idx]
                    sell_price = max(1, int(item.get("value", 0) * SELL_PRICE_MULTIPLIER))
                    
                    # Confirm sale
                    confirm = input(f"Sell {item['name']} for {sell_price} gold? (y/n): ").strip().lower()
                    if confirm == 'y':
                        self.player.gold += sell_price
                        self.player.inventory.remove(item)
                        print(f"✅ Sold {item['name']} for {sell_price} gold!")
                        logger.info(f"{self.player.name} sold {item['name']} for {sell_price} gold")
                    else:
                        print("❌ Sale cancelled.")
                else:
                    print("❌ Invalid item number!")
                    
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Invalid input.")
                continue


def open_shop(player: Any) -> None:
    """Open the shop interface"""
    shop = ShopSystem(player)
    shop.display_shop_menu()

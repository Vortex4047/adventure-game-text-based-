import mysql.connector
from mysql.connector import pooling
import json
import logging
from contextlib import contextmanager
from typing import Optional, List, Tuple, Any
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, host: Optional[str] = None, user: Optional[str] = None, 
                 password: Optional[str] = None, database: Optional[str] = None):
        # Use provided values or fall back to config
        self.config = {
            "host": host or DATABASE_CONFIG["host"],
            "user": user or DATABASE_CONFIG["user"],
            "password": password or DATABASE_CONFIG["password"],
            "database": database or DATABASE_CONFIG["database"],
            "pool_name": DATABASE_CONFIG["pool_name"],
            "pool_size": DATABASE_CONFIG["pool_size"]
        }
        self.connection_pool: Optional[pooling.MySQLConnectionPool] = None
        self.initialize()

    def initialize(self) -> None:
        """Initialize database connection and create tables"""
        try:
            # First connect without database to create it
            temp_conn = mysql.connector.connect(
                host=self.config["host"],
                user=self.config["user"],
                password=self.config["password"]
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor.close()
            temp_conn.close()

            # Create connection pool
            self.connection_pool = pooling.MySQLConnectionPool(**self.config)
            logger.info("Database connection pool created")
            
            # Create tables
            self._create_tables()
            self._initialize_game_items()
            
        except mysql.connector.Error as err:
            logger.error(f"Database initialization error: {err}")
            print(f"Database initialization error: {err}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.connection_pool.get_connection()
            yield conn
            conn.commit()
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            print(f"Database error: {err}")
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()

    def _create_tables(self) -> None:
        """Create all necessary database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create players table with new fields
            cursor.execute('''CREATE TABLE IF NOT EXISTS players(
                id INT PRIMARY KEY AUTO_INCREMENT, 
                name VARCHAR(255) UNIQUE, 
                health INT, 
                max_health INT, 
                attack INT, 
                defense INT,
                level INT, 
                experience INT, 
                score INT,
                current_location VARCHAR(255),
                inventory TEXT,
                equipped_weapon TEXT,
                equipped_armor TEXT,
                quests TEXT,
                gold INT,
                difficulty VARCHAR(20) DEFAULT 'normal',
                achievements TEXT,
                status_effects TEXT,
                stats TEXT,
                save_version VARCHAR(10) DEFAULT '2.0'
            );''')
            
            # Add new columns to existing tables (for migration)
            try:
                cursor.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS achievements TEXT")
            except mysql.connector.Error:
                pass
            
            try:
                cursor.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS status_effects TEXT")
            except mysql.connector.Error:
                pass
            
            try:
                cursor.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS stats TEXT")
            except mysql.connector.Error:
                pass
            
            try:
                cursor.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS save_version VARCHAR(10) DEFAULT '2.0'")
            except mysql.connector.Error:
                pass

            cursor.execute('''CREATE TABLE IF NOT EXISTS game_items(
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) UNIQUE,
                type VARCHAR(50),
                value INT,
                description TEXT
            );''')
            
            cursor.close()
            logger.info("Database tables created/verified")

    def _initialize_game_items(self):
        """Initialize game items in database"""
        game_items = [
            ("Health Potion", "consumable", 50, "Restores 50 health points"),
            ("Iron Sword", "weapon", 15, "A sturdy iron sword. +15 attack"),
            ("Steel Shield", "armor", 10, "A reliable steel shield. +10 defense"),
            ("Magic Herb", "consumable", 30, "A mystical herb. Restores 30 health"),
            ("Gold Coin", "currency", 1, "Standard currency"),
            ("Ancient Key", "key", 0, "An old key that might unlock something special"),
            ("Dragon Scale Armor", "armor", 25, "Legendary armor from dragon scales. +25 defense"),
            ("Ancient Spell Book", "misc", 100, "A rare book of ancient magic")
        ]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            for item in game_items:
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO game_items (name, type, value, description) VALUES (%s, %s, %s, %s)", 
                        item
                    )
                except mysql.connector.Error:
                    pass  # Item already exists
            cursor.close()

    def save_player(self, player: Any) -> bool:
        """Save player data to database"""
        try:
            from constants import SAVE_FILE_VERSION
            
            inventory_json = json.dumps(player.inventory)
            quests_json = json.dumps(player.quests)
            equipped_weapon_json = json.dumps(player.equipped_weapon) if player.equipped_weapon else None
            equipped_armor_json = json.dumps(player.equipped_armor) if player.equipped_armor else None
            
            # Save achievements
            achievements_json = None
            if hasattr(player, 'achievement_manager'):
                achievements_json = json.dumps(player.achievement_manager.to_dict())
            
            # Save status effects
            status_effects_json = None
            if hasattr(player, 'status_effect_manager'):
                status_effects_json = json.dumps(player.status_effect_manager.to_dict())
            
            # Save additional stats
            stats_data = {
                "enemies_defeated": getattr(player, 'enemies_defeated', 0),
                "items_purchased": getattr(player, 'items_purchased', 0),
                "battles_won_flawless": getattr(player, 'battles_won_flawless', 0),
                "locations_visited": list(getattr(player, 'locations_visited', {"village"}))
            }
            stats_json = json.dumps(stats_data)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO players (name, health, max_health, attack, defense, level, experience, 
                                       score, current_location, inventory, equipped_weapon, equipped_armor, 
                                       quests, gold, difficulty, achievements, status_effects, stats, save_version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    health=%s, max_health=%s, attack=%s, defense=%s, level=%s, experience=%s, 
                    score=%s, current_location=%s, inventory=%s, equipped_weapon=%s, 
                    equipped_armor=%s, quests=%s, gold=%s, difficulty=%s, achievements=%s, 
                    status_effects=%s, stats=%s, save_version=%s
                """, (
                    player.name, player.health, player.max_health, player.base_attack, player.base_defense,
                    player.level, player.experience, player.score, player.current_location, 
                    inventory_json, equipped_weapon_json, equipped_armor_json, quests_json, 
                    player.gold, player.difficulty, achievements_json, status_effects_json, 
                    stats_json, SAVE_FILE_VERSION,
                    # Update values
                    player.health, player.max_health, player.base_attack, player.base_defense,
                    player.level, player.experience, player.score, player.current_location, 
                    inventory_json, equipped_weapon_json, equipped_armor_json, quests_json, 
                    player.gold, player.difficulty, achievements_json, status_effects_json,
                    stats_json, SAVE_FILE_VERSION
                ))
                cursor.close()
            logger.info(f"Player {player.name} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving player: {e}")
            print(f"Error saving player: {e}")
            return False

    def load_player(self, player_name: str) -> Optional[Tuple]:
        """Load player data from database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM players WHERE name = %s", (player_name,))
                player_data = cursor.fetchone()
                cursor.close()
                
                if player_data:
                    logger.info(f"Player {player_name} loaded from database")
                    return player_data
                return None
        except Exception as e:
            logger.error(f"Error loading player: {e}")
            print(f"Error loading player: {e}")
            return None

    def get_all_players(self) -> List[Tuple[str, int, int]]:
        """Get list of all players"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, level, score FROM players ORDER BY score DESC")
                players = cursor.fetchall()
                cursor.close()
                return players
        except Exception as e:
            logger.error(f"Error fetching players: {e}")
            print(f"Error fetching players: {e}")
            return []

    def delete_player(self, player_name: str) -> bool:
        """Delete a player from database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM players WHERE name = %s", (player_name,))
                cursor.close()
            logger.info(f"Player {player_name} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting player: {e}")
            print(f"Error deleting player: {e}")
            return False

    def close(self) -> None:
        """Close all database connections"""
        if self.connection_pool:
            # Connection pools don't have a direct close method
            # Connections are closed when they're returned to the pool
            logger.info("Database connections closed")
            pass

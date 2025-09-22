"""
Database models and configuration using SQLite
"""

from typing import Optional, Dict, Any
from datetime import datetime
import os
import sqlite3
import aiosqlite
import json
import uuid
from urllib.parse import urlparse


# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "scraper.db")
DB_TYPE = "sqlite"  # Only SQLite supported


class TemplateStore:
    """SQLite template storage implementation"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        # Create database file if it doesn't exist
        if not os.path.exists(self.db_path):
            # Create directory if needed
            os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
    
    async def _create_tables(self):
        """Create tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if templates table exists and has user_id column
            cursor = await db.execute("PRAGMA table_info(templates)")
            columns = await cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            # If templates table exists but doesn't have user_id, add it
            if columns and 'user_id' not in column_names:
                print("🔄 Migrating templates table to add user_id column...")
                await db.execute("ALTER TABLE templates ADD COLUMN user_id TEXT")
                print("✅ Templates table migration completed")
            
            # Templates table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    selectors TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 1.0,
                    last_used TIMESTAMP,
                    user_id TEXT
                )
            """)
            
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    train_count INTEGER DEFAULT 0,
                    scrape_count INTEGER DEFAULT 0,
                    max_trains INTEGER DEFAULT 1,
                    max_scrapes INTEGER DEFAULT 10
                )
            """)
            
            # API tokens table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS api_tokens (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create indexes
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_templates_domain ON templates(domain)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_templates_user_id ON templates(user_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_tokens_token ON api_tokens(token)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_tokens_user_id ON api_tokens(user_id)
            """)
            
            await db.commit()
    
    async def save_template(
        self, 
        domain: str, 
        template: Dict[str, str],
        confidence_score: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Save a template to SQLite database"""
        
        await self._create_tables()
        
        template_id = str(uuid.uuid4())
        selectors_json = json.dumps(template)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO templates (id, domain, selectors, confidence_score, usage_count, success_rate, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                template_id,
                domain,
                selectors_json,
                confidence_score,
                0,
                1.0,
                user_id
            ))
            
            await db.commit()
            
        return template_id
    
    async def get_template_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get template for a specific domain"""
        
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute("""
                SELECT id, domain, selectors, created_at, confidence_score, usage_count, success_rate, last_used
                FROM templates 
                WHERE domain = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (domain,))
            
            row = await cursor.fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "domain": row["domain"],
                    "selectors": json.loads(row["selectors"]),
                    "created_at": row["created_at"],
                    "confidence_score": row["confidence_score"],
                    "usage_count": row["usage_count"],
                    "success_rate": row["success_rate"],
                    "last_used": row["last_used"]
                }
            return None
    
    async def update_template_usage(self, template_id: str, success: bool = True):
        """Update template usage statistics"""
        
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get current stats
            cursor = await db.execute("""
                SELECT usage_count, success_rate FROM templates WHERE id = ?
            """, (template_id,))
            
            row = await cursor.fetchone()
            if not row:
                return
            
            current_usage = row[0] or 0
            current_success_rate = row[1] or 1.0
            
            # Calculate new stats
            new_usage = current_usage + 1
            if success:
                new_success_rate = (current_success_rate * current_usage + 1) / new_usage
            else:
                new_success_rate = (current_success_rate * current_usage) / new_usage
            
            # Update database
            await db.execute("""
                UPDATE templates 
                SET usage_count = ?,
                    success_rate = ?,
                    last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_usage, new_success_rate, template_id))
            
            await db.commit()
    
    async def get_all_templates(self) -> list[Dict[str, Any]]:
        """Get all templates"""
        
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute("""
                SELECT id, domain, selectors, created_at, confidence_score, usage_count, success_rate, last_used, user_id
                FROM templates 
                ORDER BY created_at DESC
            """)
            
            rows = await cursor.fetchall()
            
            templates = []
            for row in rows:
                templates.append({
                    "id": row["id"],
                    "domain": row["domain"],
                    "selectors": json.loads(row["selectors"]),
                    "created_at": row["created_at"],
                    "confidence_score": row["confidence_score"],
                    "usage_count": row["usage_count"],
                    "success_rate": row["success_rate"],
                    "last_used": row["last_used"],
                    "user_id": row["user_id"]
                })
            
            return templates
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM templates WHERE id = ?
            """, (template_id,))
            
            await db.commit()
            
            return cursor.rowcount > 0

    # User management methods
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (id, username, email, password_hash, role, is_active, 
                                 created_at, train_count, scrape_count, max_trains, max_scrapes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data["id"],
                user_data["username"],
                user_data["email"],
                user_data["password_hash"],
                user_data.get("role", "user"),
                user_data.get("is_active", True),
                user_data["created_at"],
                user_data.get("train_count", 0),
                user_data.get("scrape_count", 0),
                user_data.get("max_trains", 1),
                user_data.get("max_scrapes", 10)
            ))
            await db.commit()
            return user_data["id"]

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username,))
            row = await cursor.fetchone()
            
            if row:
                return dict(row)
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM users WHERE id = ?
            """, (user_id,))
            row = await cursor.fetchone()
            
            if row:
                return dict(row)
            return None

    async def update_user_usage(self, user_id: str, increment_trains: int = 0, increment_scrapes: int = 0) -> bool:
        """Update user usage counts"""
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users 
                SET train_count = train_count + ?, 
                    scrape_count = scrape_count + ?
                WHERE id = ?
            """, (increment_trains, increment_scrapes, user_id))
            await db.commit()
            return True

    async def create_api_token(self, token_data: Dict[str, Any]) -> str:
        """Create an API token"""
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO api_tokens (id, name, token, user_id, created_at, expires_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                token_data["id"],
                token_data["name"],
                token_data["token"],
                token_data["user_id"],
                token_data["created_at"],
                token_data.get("expires_at"),
                token_data.get("is_active", True)
            ))
            await db.commit()
            return token_data["id"]

    async def get_user_by_api_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by API token"""
        await self._create_tables()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT u.* FROM users u
                JOIN api_tokens t ON u.id = t.user_id
                WHERE t.token = ? AND t.is_active = 1
                AND (t.expires_at IS NULL OR t.expires_at > CURRENT_TIMESTAMP)
            """, (token,))
            row = await cursor.fetchone()
            
            if row:
                # Update last_used for the token
                await db.execute("""
                    UPDATE api_tokens SET last_used = CURRENT_TIMESTAMP WHERE token = ?
                """, (token,))
                await db.commit()
                return dict(row)
            return None

    async def initialize_superadmin(self):
        """Initialize superadmin user if not exists"""
        from .models.auth import get_password_hash
        
        # Default admin user
        SUPERADMIN_USER = {
            "id": str(uuid.uuid4()),
            "username": "nasri",
            "email": "admin@example.com",  # Use valid email domain
            "password_hash": get_password_hash("UtyCantik12"),  # Use current hash method
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "train_count": 0,
            "scrape_count": 0,
            "max_trains": -1,  # Unlimited
            "max_scrapes": -1,  # Unlimited
        }
        
        existing = await self.get_user_by_username(SUPERADMIN_USER["username"])
        if not existing:
            await self.create_user(SUPERADMIN_USER)
            print(f"✅ Superadmin user created: {SUPERADMIN_USER['username']}")
        else:
            # Update existing user with correct password hash if needed
            await self.update_user_password(SUPERADMIN_USER["username"], "UtyCantik12")
            print(f"✅ Superadmin user already exists: {SUPERADMIN_USER['username']}")

    async def update_user_password(self, username: str, password: str):
        """Update user password"""
        from .models.auth import get_password_hash
        
        await self._create_tables()
        password_hash = get_password_hash(password)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users SET password_hash = ? WHERE username = ?
            """, (password_hash, username))
            await db.commit()


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc


# Global template store instance
template_store = TemplateStore()
#!/usr/bin/env python3
"""
Reset superadmin user with correct password hash
"""

import asyncio
import aiosqlite
import uuid
import hashlib
from datetime import datetime

async def reset_superadmin():
    """Reset superadmin user with SHA256 hash"""
    
    try:
        print("🔄 Starting superadmin reset...")
        
        # Fallback SHA256 hash for "UtyCantik12"
        salt = "fallback_salt_for_testing"
        password_hash = hashlib.sha256(("UtyCantik12" + salt).encode()).hexdigest()
        
        user_data = {
            "id": str(uuid.uuid4()),
            "username": "nasri",
            "email": "admin@example.com",
            "password_hash": password_hash,
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "train_count": 0,
            "scrape_count": 0,
            "max_trains": -1,
            "max_scrapes": -1,
        }
        
        print(f"📂 Connecting to database: ./scraper.db")
        async with aiosqlite.connect('./scraper.db') as db:
            # Delete existing user
            print(f"🗑️ Deleting existing user: {user_data['username']}")
            await db.execute('DELETE FROM users WHERE username = ?', (user_data["username"],))
            
            # Insert new user
            print(f"➕ Creating new user...")
            await db.execute("""
                INSERT INTO users (
                    id, username, email, password_hash, role, is_active, 
                    created_at, train_count, scrape_count, max_trains, max_scrapes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data["id"],
                user_data["username"],
                user_data["email"],
                user_data["password_hash"],
                user_data["role"],
                user_data["is_active"],
                user_data["created_at"],
                user_data["train_count"],
                user_data["scrape_count"],
                user_data["max_trains"],
                user_data["max_scrapes"]
            ))
            
            await db.commit()
            print(f"✅ Superadmin user reset: {user_data['username']}")
            print(f"📧 Email: {user_data['email']}")
            print(f"🔐 Password: UtyCantik12")
            print(f"🔑 Hash: {password_hash[:20]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reset_superadmin())
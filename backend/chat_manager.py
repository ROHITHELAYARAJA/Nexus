"""
Chat History Manager for NEXUS
SQLite-based persistent storage for conversations
"""

import aiosqlite
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ChatManager:
    """Manages chat history with SQLite"""
    
    def __init__(self, db_path: str = "nexus_history.db"):
        self.db_path = db_path
        
    async def initialize(self):
        """Create database and tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model TEXT,
                    message_count INTEGER DEFAULT 0
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    model TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_id 
                ON messages(conversation_id)
            """)
            
            await db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts 
                USING fts5(content, conversation_id UNINDEXED)
            """)
            
            await db.commit()
    
    async def create_conversation(self, title: str, model: str = None) -> int:
        """Create a new conversation"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO conversations (title, model) VALUES (?, ?)",
                (title, model)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def add_message(self, conversation_id: int, role: str, content: str, model: str = None):
        """Add a message to a conversation"""
        async with aiosqlite.connect(self.db_path) as db:
            # Insert message
            await db.execute(
                "INSERT INTO messages (conversation_id, role, content, model) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, model)
            )
            
            # Update FTS index
            await db.execute(
                "INSERT INTO messages_fts (content, conversation_id) VALUES (?, ?)",
                (content, conversation_id)
            )
            
            # Update conversation
            await db.execute(
                """UPDATE conversations 
                   SET updated_at = CURRENT_TIMESTAMP,
                       message_count = message_count + 1
                   WHERE id = ?""",
                (conversation_id,)
            )
            
            await db.commit()
    
    async def get_conversations(self, limit: int = 50) -> List[Dict]:
        """Get all conversations"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT id, title, created_at, updated_at, model, message_count
                   FROM conversations
                   ORDER BY updated_at DESC
                   LIMIT ?""",
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_conversation(self, conversation_id: int) -> Dict:
        """Get a specific conversation with all messages"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get conversation info
            async with db.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,)
            ) as cursor:
                conv = await cursor.fetchone()
                if not conv:
                    return None
                
                conversation = dict(conv)
            
            # Get messages
            async with db.execute(
                """SELECT role, content, model, timestamp
                   FROM messages
                   WHERE conversation_id = ?
                   ORDER BY timestamp ASC""",
                (conversation_id,)
            ) as cursor:
                messages = await cursor.fetchall()
                conversation['messages'] = [dict(msg) for msg in messages]
            
            return conversation
    
    async def delete_conversation(self, conversation_id: int):
        """Delete a conversation and all its messages"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            await db.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            await db.execute("DELETE FROM messages_fts WHERE conversation_id = ?", (conversation_id,))
            await db.commit()
    
    async def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Search across all conversations"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute(
                """SELECT DISTINCT c.id, c.title, c.created_at, c.updated_at, c.message_count
                   FROM conversations c
                   JOIN messages_fts fts ON c.id = fts.conversation_id
                   WHERE messages_fts MATCH ?
                   ORDER BY c.updated_at DESC
                   LIMIT ?""",
                (query, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def clear_all_history(self):
        """Delete all conversations and messages"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM conversations")
            await db.execute("DELETE FROM messages")
            await db.execute("DELETE FROM messages_fts")
            await db.commit()


# Global instance
chat_manager = ChatManager()

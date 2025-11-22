from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, Dict, List
import json

DB_PATH = Path(__file__).resolve().parents[1] 

@dataclass
class Quest:
    id: Optional[int]
    title: str
    difficulty: str
    reward: int
    description: str
    deadline: str
    created_at: Optional[str] = None



class Database:
    def __init__(self, path: Path = DB_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema() 


    def create_tables(self):
        cur = self.conn.cursor()

        # Таблица квестов
        cur.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            difficulty TEXT CHECK(difficulty IN ('Легкий','Средний','Сложный','Эпический')),
            reward INTEGER,
            description TEXT,
            deadline TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Таблица версий
        cur.execute("""
        CREATE TABLE IF NOT EXISTS quest_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_id INTEGER,
            title TEXT,
            difficulty TEXT,
            reward INTEGER,
            description TEXT,
            deadline TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quest_id) REFERENCES quests(id)
        );
        """)

        # Таблица объектов карты
        cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quest_id) REFERENCES quests(id)
        );
        """)

        self.conn.commit()


    def create_quest(self, data):
        """
        data = {
            "title": "...",
            "difficulty": "...",
            "reward": 100,
            "description": "...",
            "deadline": "..."
        }
        """
        cur = self.conn.cursor()

        cur.execute("""
        INSERT INTO quests(title, difficulty, reward, description, deadline)
        VALUES (?, ?, ?, ?, ?)
        """, (
            data["title"],
            data["difficulty"],
            data["reward"],
            data["description"],
            data["deadline"]
        ))

        quest_id = cur.lastrowid
        self.conn.commit()

        quest = self.get_quest(quest_id)
        self.save_version(quest)
        return quest
    



    def update_quest_fields(self, quest_id, fields):
        """
        fields = {"title": "...", "reward": 500}
        """

        if not fields:
            return

        keys = ", ".join([f"{k}=?" for k in fields])
        values = list(fields.values())
        values.append(quest_id)

        cur = self.conn.cursor()
        cur.execute(f"UPDATE quests SET {keys} WHERE id=?", values)
        self.conn.commit()

        quest = self.get_quest(quest_id)
        self.save_version(quest)







    def save_version(self, q):
        cur = self.conn.cursor()

        cur.execute("""
        INSERT INTO quest_versions(quest_id, title, difficulty, reward, description, deadline)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            q["id"],
            q["title"],
            q["difficulty"],
            q["reward"],
            q["description"],
            q["deadline"]
        ))

        self.conn.commit()





    def get_quest(self, quest_id):
        cur = self.conn.cursor()
        row = cur.execute("SELECT * FROM quests WHERE id=?", (quest_id,)).fetchone()

        if row:
            return dict(row)
        return None
    



    def list_quests(self):
        cur = self.conn.cursor()
        rows = cur.execute("SELECT * FROM quests ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    




    def add_location(self, quest_id, kind, payload):
        cur = self.conn.cursor()

        cur.execute("""
        INSERT INTO locations(quest_id, kind, payload)
        VALUES (?, ?, ?)
        """, (quest_id, kind, json.dumps(payload)))

        self.conn.commit()



    def list_locations(self, quest_id):
        cur = self.conn.cursor()
        rows = cur.execute("SELECT * FROM locations WHERE quest_id=?", (quest_id,)).fetchall()

        result = []
        for r in rows:
            item = dict(r)
            item["payload"] = json.loads(item["payload"])
            result.append(item)

        return result
    



    def clear_locations(self, quest_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM locations WHERE quest_id=?", (quest_id,))
        self.conn.commit()

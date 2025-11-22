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



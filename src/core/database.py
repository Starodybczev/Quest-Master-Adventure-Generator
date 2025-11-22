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
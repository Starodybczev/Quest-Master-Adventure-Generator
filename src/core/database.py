from __future__ import annotations

import sqlite3
from typing import Optional, List, Dict, Any


class Database:
	def __init__(self, db_path: str = "adventures.db"):
		"""Open (or create) the SQLite database.

		Use `:memory:` for an in-memory DB (useful in tests).
		"""
		self.db_path = db_path
		self.conn = sqlite3.connect(db_path, check_same_thread=False)
		self.conn.row_factory = sqlite3.Row
		self._create_tables()

	def _create_tables(self) -> None:
		cur = self.conn.cursor()
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS quests (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT UNIQUE NOT NULL,
				difficulty TEXT,
				reward INTEGER,
				description TEXT,
				deadline TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
			"""
		)

		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS quest_versions (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				quest_id INTEGER NOT NULL,
				title TEXT,
				difficulty TEXT,
				reward INTEGER,
				description TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
			)
			"""
		)

		self.conn.commit()

	def create_quest(self, title: str, difficulty: str, reward: int, description: str, deadline: str) -> Optional[int]:
		"""Insert a new quest and return its ID or None on failure."""
		try:
			cur = self.conn.cursor()
			cur.execute(
				"""
				INSERT INTO quests (title, difficulty, reward, description, deadline)
				VALUES (?, ?, ?, ?, ?)
				""",
				(title, difficulty, reward, description, deadline),
			)
			self.conn.commit()
			return cur.lastrowid
		except sqlite3.IntegrityError:
			# e.g., duplicate title
			return None

	def update_quest(self, quest_id: int, title: str, difficulty: str, reward: int, description: str, deadline: str) -> bool:
		"""Update quest and store a version snapshot. Returns True if updated."""
		cur = self.conn.cursor()
		cur.execute(
			"""
			UPDATE quests
			SET title = ?, difficulty = ?, reward = ?, description = ?, deadline = ?
			WHERE id = ?
			""",
			(title, difficulty, reward, description, deadline, quest_id),
		)

		if cur.rowcount == 0:
			return False

		# store version
		cur.execute(
			"""
			INSERT INTO quest_versions (quest_id, title, difficulty, reward, description)
			VALUES (?, ?, ?, ?, ?)
			""",
			(quest_id, title, difficulty, reward, description),
		)

		self.conn.commit()
		return True

	def get_quest(self, quest_id: int) -> Optional[Dict[str, Any]]:
		cur = self.conn.cursor()
		cur.execute("SELECT * FROM quests WHERE id = ?", (quest_id,))
		row = cur.fetchone()
		if row is None:
			return None
		return dict(row)

	def get_all_quests(self) -> List[Dict[str, Any]]:
		cur = self.conn.cursor()
		cur.execute("SELECT * FROM quests ORDER BY created_at DESC")
		rows = cur.fetchall()
		return [dict(r) for r in rows]

	def delete_quest(self, quest_id: int) -> bool:
		cur = self.conn.cursor()
		cur.execute("DELETE FROM quests WHERE id = ?", (quest_id,))
		self.conn.commit()
		return cur.rowcount > 0

	def close(self) -> None:
		try:
			self.conn.commit()
		except Exception:
			pass
		try:
			self.conn.close()
		except Exception:
			pass


__all__ = ["Database"]

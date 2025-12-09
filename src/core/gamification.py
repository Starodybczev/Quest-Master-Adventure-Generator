from __future__ import annotations

from typing import Dict, Any, List, Tuple


class GamificationEngine:
	def __init__(self):
		# total XP collected
		self.total_xp: int = 0

		# simple stats counters
		self.stats: Dict[str, int] = {
			"quests_created": 0,
			"pdfs_exported": 0,
			"docx_exported": 0,
			"maps_saved": 0,
			"boss_fights_won": 0,
		}

		# achievements definitions
		# Each achievement has id, name, desc, xp reward, condition type and threshold
		self._achievements: List[Dict[str, Any]] = [
			{"id": "speed_demon", "name": "Демон скорости", "desc": "Генерация 100 квестов за короткое время", "xp": 200, "unlocked": False},
			{"id": "quest_maker_10", "name": "Составитель квестов", "desc": "Создать 10 квестов", "xp": 20, "unlocked": False, "stat": "quests_created", "threshold": 10},
			{"id": "quest_maker_100", "name": "Гильдмастер", "desc": "Создать 100 квестов", "xp": 200, "unlocked": False, "stat": "quests_created", "threshold": 100},
			{"id": "exporter_10", "name": "Печатник", "desc": "Сделать 10 экспортов в PDF", "xp": 30, "unlocked": False, "stat": "pdfs_exported", "threshold": 10},
		]

		# XP per action
		self._xp_by_action = {
			"create_quest": 10,
			"export_pdf": 5,
			"export_docx": 5,
			"save_map": 8,
			"win_boss": 50,
		}

	def add_xp(self, action: str = "") -> Tuple[int, bool]:
		"""Add XP for an action and return (xp_gained, leveled_up).

		leveled_up is True if the level increased after adding XP.
		"""
		xp = self._xp_by_action.get(action, 1)
		prev_level = self.get_current_level()
		self.total_xp += xp
		new_level = self.get_current_level()
		leveled_up = new_level > prev_level

		# check XP-based achievements (simple)
		self._check_achievements()

		return xp, leveled_up

	def update_stats(self, stat_name: str) -> None:
		"""Increment a named stat and evaluate achievements."""
		self.stats[stat_name] = self.stats.get(stat_name, 0) + 1
		self._check_achievements()

	def get_current_level(self) -> int:
		"""Compute level from total_xp. Level 1 starts at 0 XP. Every 100 XP = +1 level."""
		return 1 + (self.total_xp // 100)

	def get_progress_to_next_level(self) -> Tuple[int, int, int]:
		"""Return (xp_into_current_level, xp_required_for_next_level, percent).

		percent is an integer 0-100 used for display.
		"""
		xp_per_level = 100
		current_level = self.get_current_level()
		xp_into = self.total_xp - (current_level - 1) * xp_per_level
		required = xp_per_level
		percent = int((xp_into / required) * 100) if required > 0 else 0
		return xp_into, required, percent

	def get_unlocked_achievements(self) -> List[Dict[str, Any]]:
		return [a for a in self._achievements if a.get("unlocked")]

	def get_locked_achievements(self) -> List[Dict[str, Any]]:
		return [a for a in self._achievements if not a.get("unlocked")]

	def _check_achievements(self) -> None:
		"""Internal: check and unlock achievements based on stats or XP."""
		for ach in self._achievements:
			if ach.get("unlocked"):
				continue

			stat = ach.get("stat")
			threshold = ach.get("threshold")

			if stat and threshold is not None:
				if self.stats.get(stat, 0) >= threshold:
					self._unlock(ach)
			else:
				# fallback: XP-based or manual achievements can be unlocked elsewhere
				if ach.get("id") == "speed_demon":
					# this one is intended to be unlocked externally by tests/tools
					continue

	def _unlock(self, ach: Dict[str, Any]) -> None:
		ach["unlocked"] = True
		xp = ach.get("xp", 0)
		if xp:
			self.total_xp += xp

	def get_stats(self) -> Dict[str, int]:
		return dict(self.stats)


__all__ = ["GamificationEngine"]


from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QProgressBar, QListWidget, QListWidgetItem, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class GamificationPanel(QWidget):
    """Панель геймификации"""

    def __init__(self, gamification, parent=None):
        super().__init__(parent)
        self.gamification = gamification
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("⚔️ Прогресс приключенца")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Текущий уровень
        self.level_label = QLabel()
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_font = QFont()
        level_font.setPointSize(12)
        self.level_label.setFont(level_font)
        layout.addWidget(self.level_label)

        # Прогресс-бар XP
        self.xp_progress = QProgressBar()
        self.xp_progress.setTextVisible(True)
        self.xp_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #8B4513;
                border-radius: 5px;
                text-align: center;
                background-color: #f4e4bc;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFD700, stop:1 #FFA500
                );
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.xp_progress)

        # Статистика
        stats_group = QGroupBox("📊 Статистика")
        stats_layout = QVBoxLayout()

        self.stats_labels = {
            "quests_created": QLabel("Квестов создано: 0"),
            "pdfs_exported": QLabel("PDF экспортов: 0"),
            "docx_exported": QLabel("DOCX экспортов: 0"),
            "maps_saved": QLabel("Карт сохранено: 0"),
            "boss_fights_won": QLabel("Босс-файтов пройдено: 0")
        }

        for label in self.stats_labels.values():
            stats_layout.addWidget(label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Достижения
        achievements_group = QGroupBox("🏆 Достижения")
        achievements_layout = QVBoxLayout()

        self.achievements_list = QListWidget()
        self.achievements_list.setStyleSheet("""
            QListWidget {
                background-color: #fff8e7;
                border: 2px solid #8B4513;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #d4a76a;
            }
            QListWidget::item:selected {
                background-color: #FFD700;
                color: black;
            }
        """)
        achievements_layout.addWidget(self.achievements_list)

        achievements_group.setLayout(achievements_layout)
        layout.addWidget(achievements_group)

        layout.addStretch()

        self.setLayout(layout)
        self.update_display()

    def update_display(self):
        """Обновление отображения"""
        # Обновление уровня
        current_level = self.gamification.get_current_level()
        total_xp = self.gamification.total_xp
        self.level_label.setText(f"🎖️ {current_level} (XP: {total_xp})")

        # Обновление прогресс-бара
        progress, required, percent = self.gamification.get_progress_to_next_level()
        self.xp_progress.setMaximum(required)
        self.xp_progress.setValue(progress)
        self.xp_progress.setFormat(f"{progress} / {required} XP ({percent}%)")

        # Обновление статистики
        for stat_name, label in self.stats_labels.items():
            value = self.gamification.stats.get(stat_name, 0)

            stat_names_ru = {
                "quests_created": "Квестов создано",
                "pdfs_exported": "PDF экспортов",
                "docx_exported": "DOCX экспортов",
                "maps_saved": "Карт сохранено",
                "boss_fights_won": "Босс-файтов пройдено"
            }

            label.setText(f"{stat_names_ru.get(stat_name, stat_name)}: {value}")

        # Обновление достижений
        self.achievements_list.clear()

        # Разблокированные достижения
        unlocked = self.gamification.get_unlocked_achievements()
        for ach in unlocked:
            item = QListWidgetItem(f"✅ {ach['name']} (+{ach['xp']} XP)")
            item.setToolTip(ach['desc'])
            item.setForeground(Qt.GlobalColor.darkGreen)
            self.achievements_list.addItem(item)

        # Заблокированные достижения
        locked = self.gamification.get_locked_achievements()
        for ach in locked:
            item = QListWidgetItem(f"🔒 {ach['name']} (+{ach['xp']} XP)")
            item.setToolTip(ach['desc'])
            item.setForeground(Qt.GlobalColor.gray)
            self.achievements_list.addItem(item)

    def show_xp_gain(self, xp: int, leveled_up: bool = False):
        """Показать получение XP (можно добавить анимацию)"""
        self.update_display()
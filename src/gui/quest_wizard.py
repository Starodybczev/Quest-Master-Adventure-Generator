from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QSpinBox, QTextEdit,
                             QDateTimeEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence
from typing import Optional, Dict, Any


class QuestWizard(QWidget):
    """Виджет для создания и редактирования квестов"""

    quest_created = pyqtSignal(int)  # Сигнал с ID созданного квеста
    quest_updated = pyqtSignal(int)  # Сигнал с ID обновленного квеста

    def __init__(self, db, gamification, parent=None):
        super().__init__(parent)
        self.db = db
        self.gamification = gamification
        self.current_quest_id: Optional[int] = None
        self.auto_save_enabled = True

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()

        # Форма
        form_layout = QFormLayout()

        # Название квеста
        self.title_input = QLineEdit()
        self.title_input.setMaxLength(50)
        self.title_input.setPlaceholderText("Введите название квеста...")
        self.title_input.textChanged.connect(self.on_field_changed)
        form_layout.addRow("Название:", self.title_input)

        # Сложность
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Легкий", "Средний", "Сложный", "Эпический"])
        self.difficulty_combo.currentTextChanged.connect(self.on_field_changed)
        form_layout.addRow("Сложность:", self.difficulty_combo)

        # Награда
        reward_layout = QHBoxLayout()
        self.reward_spin = QSpinBox()
        self.reward_spin.setRange(10, 10000)
        self.reward_spin.setValue(100)
        self.reward_spin.setSuffix(" золотых")
        self.reward_spin.valueChanged.connect(self.on_field_changed)
        reward_layout.addWidget(self.reward_spin)
        reward_layout.addStretch()
        form_layout.addRow("Награда:", reward_layout)

        # Описание
        desc_label = QLabel("Описание:")
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Подробное описание квеста (минимум 50 слов)...")
        self.description_edit.setMinimumHeight(150)
        self.description_edit.textChanged.connect(self.on_description_changed)

        # Счетчик слов
        self.word_counter = QLabel("Слов: 0 / 50")

        form_layout.addRow(desc_label, self.description_edit)
        form_layout.addRow("", self.word_counter)

        # Дедлайн
        self.deadline_edit = QDateTimeEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.deadline_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.deadline_edit.dateTimeChanged.connect(self.on_field_changed)
        form_layout.addRow("Дедлайн:", self.deadline_edit)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()

        self.create_button = QPushButton("Создать квест")
        self.create_button.clicked.connect(self.create_or_update_quest)
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_form)

        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        create_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        create_shortcut.activated.connect(self.create_or_update_quest)

    def on_description_changed(self):
        """Обработка изменения описания"""
        text = self.description_edit.toPlainText()
        words = len(text.split())

        self.word_counter.setText(f"Слов: {words} / 50")

        if words < 50:
            self.word_counter.setStyleSheet("color: red;")
        else:
            self.word_counter.setStyleSheet("color: green;")

        self.on_field_changed()

    def on_field_changed(self):
        """Обработка изменения полей (автосохранение)"""
        if self.auto_save_enabled and self.current_quest_id is not None:
            self.auto_save()

    def auto_save(self):
        """Автоматическое сохранение изменений"""
        if not self.validate_fields(show_errors=False):
            return

        title = self.title_input.text().strip()
        difficulty = self.difficulty_combo.currentText()
        reward = self.reward_spin.value()
        description = self.description_edit.toPlainText().strip()
        deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        self.db.update_quest(self.current_quest_id, title, difficulty,
                           reward, description, deadline)

    def validate_fields(self, show_errors: bool = True) -> bool:
        """Валидация полей формы"""
        errors = []

        # Проверка названия
        if not self.title_input.text().strip():
            errors.append("Название квеста не может быть пустым")
            self.title_input.setStyleSheet("border: 2px solid red;")
        else:
            self.title_input.setStyleSheet("")

        # Проверка описания
        words = len(self.description_edit.toPlainText().split())
        if words < 50:
            errors.append(f"Описание должно содержать минимум 50 слов (сейчас: {words})")
            self.description_edit.setStyleSheet("border: 2px solid red;")
        else:
            self.description_edit.setStyleSheet("")

        if errors and show_errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))

        return len(errors) == 0

    def create_or_update_quest(self):
        """Создание или обновление квеста"""
        if not self.validate_fields():
            return

        title = self.title_input.text().strip()
        difficulty = self.difficulty_combo.currentText()
        reward = self.reward_spin.value()
        description = self.description_edit.toPlainText().strip()
        deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        if self.current_quest_id is None:
            # Создание нового квеста
            quest_id = self.db.create_quest(title, difficulty, reward, description, deadline)

            if quest_id:
                self.current_quest_id = quest_id

                # Геймификация
                xp, leveled_up = self.gamification.add_xp("create_quest")
                self.gamification.update_stats("quests_created")

                msg = f"✅ Квест '{title}' успешно создан!\n+{xp} XP"
                if leveled_up:
                    msg += f"\n🎉 Новый уровень: {self.gamification.get_current_level()}!"

                QMessageBox.information(self, "Успех", msg)
                self.quest_created.emit(quest_id)
                self.clear_form()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось создать квест")
        else:
            # Обновление существующего квеста
            if self.db.update_quest(self.current_quest_id, title, difficulty,
                                   reward, description, deadline):
                QMessageBox.information(self, "Успех", f"✅ Квест '{title}' обновлен!")
                self.quest_updated.emit(self.current_quest_id)
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить квест")

    def load_quest(self, quest_id: int):
        """Загрузка квеста для редактирования"""
        quest = self.db.get_quest(quest_id)

        if quest:
            self.auto_save_enabled = False

            self.current_quest_id = quest_id
            self.title_input.setText(quest['title'])
            self.difficulty_combo.setCurrentText(quest['difficulty'])
            self.reward_spin.setValue(quest['reward'])
            self.description_edit.setPlainText(quest['description'])

            deadline_dt = QDateTime.fromString(quest['deadline'], "yyyy-MM-dd HH:mm:ss")
            self.deadline_edit.setDateTime(deadline_dt)

            self.create_button.setText("Обновить квест")

            self.auto_save_enabled = True

    def clear_form(self):
        """Очистка формы"""
        self.auto_save_enabled = False

        self.current_quest_id = None
        self.title_input.clear()
        self.difficulty_combo.setCurrentIndex(0)
        self.reward_spin.setValue(100)
        self.description_edit.clear()
        self.deadline_edit.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.create_button.setText("Создать квест")

        # Сброс стилей
        self.title_input.setStyleSheet("")
        self.description_edit.setStyleSheet("")

        self.auto_save_enabled = True
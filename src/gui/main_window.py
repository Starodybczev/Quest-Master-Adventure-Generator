from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QPushButton, QFileDialog, QMessageBox,
                             QListWidget, QListWidgetItem, QSplitter, QLabel,
                             QComboBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from core.database import Database
from core.gamification import GamificationEngine
from core.template_engine import TemplateEngine
from gui.quest_wizard import QuestWizard
from gui.map_editor import MapEditor
from gui.gamification_panel import GamificationPanel


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()

        # Инициализация компонентов
        self.db = Database()
        self.gamification = GamificationEngine()
        self.template_engine = TemplateEngine()

        self.init_ui()
        self.setup_menu()
        self.load_quests_list()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("⚔️ Quest Master - Генератор приключений")
        self.setMinimumSize(1200, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        # Левая панель - список квестов
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        left_layout.addWidget(QLabel("📜 Список квестов:"))

        self.quests_list = QListWidget()
        self.quests_list.itemClicked.connect(self.on_quest_selected)
        left_layout.addWidget(self.quests_list)

        refresh_btn = QPushButton("🔄 Обновить список")
        refresh_btn.clicked.connect(self.load_quests_list)
        left_layout.addWidget(refresh_btn)

        delete_btn = QPushButton("🗑️ Удалить квест")
        delete_btn.clicked.connect(self.delete_selected_quest)
        left_layout.addWidget(delete_btn)

        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)

        # Центральная панель - вкладки
        self.tabs = QTabWidget()

        # Вкладка 1: Quest Wizard
        self.quest_wizard = QuestWizard(self.db, self.gamification)
        self.quest_wizard.quest_created.connect(self.on_quest_created)
        self.quest_wizard.quest_updated.connect(self.on_quest_updated)
        self.tabs.addTab(self.quest_wizard, "📝 Создание квеста")

        # Вкладка 2: Map Editor
        self.map_editor = MapEditor(self.gamification)
        self.tabs.addTab(self.map_editor, "🗺️ Редактор карт")

        # Вкладка 3: Экспорт
        export_tab = self.create_export_tab()
        self.tabs.addTab(export_tab, "📄 Экспорт документов")

        # Правая панель - геймификация
        self.gamification_panel = GamificationPanel(self.gamification)
        self.gamification_panel.setMaximumWidth(350)

        # Сборка layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.gamification_panel)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

        # Статус бар
        self.statusBar().showMessage("Готов к созданию приключений! ⚔️")

    def setup_menu(self):
        """Настройка меню"""
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu("&Файл")

        new_action = QAction("&Новый квест", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        exit_action = QAction("&Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Помощь"
        help_menu = menubar.addMenu("&Помощь")

        about_action = QAction("&О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_export_tab(self) -> QWidget:
        """Создание вкладки экспорта"""
        export_widget = QWidget()
        layout = QVBoxLayout()

        # Выбор шаблона
        template_group = QGroupBox("Шаблон документа")
        template_layout = QVBoxLayout()

        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "royal_decree.html - Королевский указ",
            "guild_contract.html - Контракт гильдии",
            "ancient_scroll.html - Древний свиток"
        ])
        template_layout.addWidget(self.template_combo)

        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        # Кнопки экспорта
        export_buttons_layout = QHBoxLayout()

        pdf_btn = QPushButton("📕 Экспорт в PDF")
        pdf_btn.clicked.connect(self.export_to_pdf)
        pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        export_buttons_layout.addWidget(pdf_btn)

        docx_btn = QPushButton("📘 Экспорт в DOCX")
        docx_btn.clicked.connect(self.export_to_docx)
        docx_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0d47a1;
            }
        """)
        export_buttons_layout.addWidget(docx_btn)

        layout.addLayout(export_buttons_layout)

        layout.addStretch()

        export_widget.setLayout(layout)
        return export_widget

    def load_quests_list(self):
        """Загрузка списка квестов"""
        self.quests_list.clear()
        quests = self.db.get_all_quests()

        for quest in quests:
            difficulty_icon = {
                "Легкий": "🟢",
                "Средний": "🟡",
                "Сложный": "🔴",
                "Эпический": "🟣"
            }.get(quest['difficulty'], "⚪")

            item_text = f"{difficulty_icon} {quest['title']} ({quest['reward']} 💰)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, quest['id'])
            self.quests_list.addItem(item)

    def on_quest_selected(self, item: QListWidgetItem):
        """Обработка выбора квеста из списка"""
        quest_id = item.data(Qt.ItemDataRole.UserRole)
        self.quest_wizard.load_quest(quest_id)
        self.map_editor.set_quest_id(quest_id)
        self.tabs.setCurrentIndex(0)

    def on_quest_created(self, quest_id: int):
        """Обработка создания квеста"""
        self.load_quests_list()
        self.gamification_panel.update_display()
        self.map_editor.set_quest_id(quest_id)
        self.statusBar().showMessage(f"✅ Квест #{quest_id} создан!", 3000)

    def on_quest_updated(self, quest_id: int):
        """Обработка обновления квеста"""
        self.load_quests_list()
        self.statusBar().showMessage(f"✅ Квест #{quest_id} обновлен!", 3000)

    def delete_selected_quest(self):
        """Удаление выбранного квеста"""
        current_item = self.quests_list.currentItem()

        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите квест для удаления")
            return

        quest_id = current_item.data(Qt.ItemDataRole.UserRole)
        quest = self.db.get_quest(quest_id)

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить квест '{quest['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_quest(quest_id):
                self.load_quests_list()
                self.quest_wizard.clear_form()
                QMessageBox.information(self, "Успех", "Квест удален")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить квест")

    def export_to_pdf(self):
        """Экспорт текущего квеста в PDF"""
        quest_id = self.quest_wizard.current_quest_id

        if not quest_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Сначала создайте или выберите квест")
            return

        quest = self.db.get_quest(quest_id)
        template_text = self.template_combo.currentText()
        template_name = template_text.split(" - ")[0]

        try:
            output_path = self.template_engine.export_to_pdf(template_name, quest)

            # Геймификация
            xp, leveled_up = self.gamification.add_xp("export_pdf")
            self.gamification.update_stats("pdfs_exported")
            self.gamification_panel.update_display()

            msg = f"✅ PDF сохранен в {output_path}\n+{xp} XP"
            if leveled_up:
                msg += f"\n🎉 Новый уровень: {self.gamification.get_current_level()}!"

            QMessageBox.information(self, "Успех", msg)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    def export_to_docx(self):
        """Экспорт текущего квеста в DOCX"""
        quest_id = self.quest_wizard.current_quest_id

        if not quest_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Сначала создайте или выберите квест")
            return

        quest = self.db.get_quest(quest_id)

        try:
            output_path = self.template_engine.export_to_docx(quest)

            # Геймификация
            xp, leveled_up = self.gamification.add_xp("export_docx")
            self.gamification.update_stats("docx_exported")
            self.gamification_panel.update_display()

            msg = f"✅ DOCX сохранен в {output_path}\n+{xp} XP"
            if leveled_up:
                msg += f"\n🎉 Новый уровень: {self.gamification.get_current_level()}!"

            QMessageBox.information(self, "Успех", msg)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    def show_about(self):
        """Показать окно "О программе" """
        about_text = """
        <h2>⚔️ Quest Master</h2>
        <p><b>Генератор приключений v1.0</b></p>
        <p>Создавайте эпические квесты с помощью магии технологий!</p>
        <hr>
        <p>Технологии: PyQt6, Jinja2, WeasyPrint, python-docx</p>
        <p>Автор: Маг-Источник Гильдии Приключенцев</p>
        """
        QMessageBox.about(self, "О программе", about_text)

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.db.close()
        event.accept()
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                             QGraphicsTextItem, QFileDialog, QMessageBox, QLabel,
                             QButtonGroup, QRadioButton, QInputDialog, QColorDialog)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPixmap, QImage
from typing import Optional, List, Dict
import os


class MapEditor(QWidget):
    """Редактор карт локаций"""

    MARKER_COLORS = {
        "Город": QColor(34, 139, 34),      # Зеленый
        "Логово": QColor(220, 20, 60),     # Красный
        "Таверна": QColor(255, 215, 0),    # Желтый
        "Лес": QColor(0, 128, 0),          # Темно-зеленый
        "Подземелье": QColor(139, 69, 19), # Коричневый
    }

    def __init__(self, gamification, parent=None):
        super().__init__(parent)
        self.gamification = gamification
        self.current_quest_id: Optional[int] = None
        self.current_tool = "path"
        self.current_marker_type = "Город"
        self.drawing = False
        self.last_point: Optional[QPointF] = None
        self.markers: List[QGraphicsEllipseItem] = []
        self.labels: List[QGraphicsTextItem] = []

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()

        # Панель инструментов
        tools_layout = QHBoxLayout()

        tool_group = QButtonGroup(self)

        self.path_radio = QRadioButton("🖌️ Кисть")
        self.path_radio.setChecked(True)
        self.path_radio.toggled.connect(lambda: self.set_tool("path"))
        tool_group.addButton(self.path_radio)
        tools_layout.addWidget(self.path_radio)

        self.marker_radio = QRadioButton("📍 Маркер")
        self.marker_radio.toggled.connect(lambda: self.set_tool("marker"))
        tool_group.addButton(self.marker_radio)
        tools_layout.addWidget(self.marker_radio)

        self.label_radio = QRadioButton("📝 Текст")
        self.label_radio.toggled.connect(lambda: self.set_tool("label"))
        tool_group.addButton(self.label_radio)
        tools_layout.addWidget(self.label_radio)

        self.eraser_radio = QRadioButton("🧹 Ластик")
        self.eraser_radio.toggled.connect(lambda: self.set_tool("eraser"))
        tool_group.addButton(self.eraser_radio)
        tools_layout.addWidget(self.eraser_radio)

        tools_layout.addStretch()

        # Кнопки для файлов
        load_bg_btn = QPushButton("📂 Загрузить фон")
        load_bg_btn.clicked.connect(self.load_background)
        tools_layout.addWidget(load_bg_btn)

        save_btn = QPushButton("💾 Сохранить PNG")
        save_btn.clicked.connect(self.save_map)
        tools_layout.addWidget(save_btn)

        clear_btn = QPushButton("🗑️ Очистить")
        clear_btn.clicked.connect(self.clear_canvas)
        tools_layout.addWidget(clear_btn)

        layout.addLayout(tools_layout)

        # Панель выбора типа маркера
        marker_layout = QHBoxLayout()
        marker_layout.addWidget(QLabel("Тип маркера:"))

        marker_group = QButtonGroup(self)
        for i, (marker_type, color) in enumerate(self.MARKER_COLORS.items()):
            radio = QRadioButton(marker_type)
            if i == 0:
                radio.setChecked(True)
            radio.toggled.connect(lambda checked, mt=marker_type:
                                self.set_marker_type(mt) if checked else None)
            marker_group.addButton(radio)
            marker_layout.addWidget(radio)

        marker_layout.addStretch()
        layout.addLayout(marker_layout)

        # Холст для рисования
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 600)

        # Фон пергамента
        self.scene.setBackgroundBrush(QBrush(QColor(244, 228, 188)))

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.on_mouse_press
        self.view.mouseMoveEvent = self.on_mouse_move
        self.view.mouseReleaseEvent = self.on_mouse_release

        layout.addWidget(self.view)

        self.setLayout(layout)

    def set_tool(self, tool: str):
        """Установка текущего инструмента"""
        self.current_tool = tool

    def set_marker_type(self, marker_type: str):
        """Установка типа маркера"""
        self.current_marker_type = marker_type

    def on_mouse_press(self, event):
        """Обработка нажатия мыши"""
        scene_pos = self.view.mapToScene(event.pos())

        if self.current_tool == "path":
            self.drawing = True
            self.last_point = scene_pos

        elif self.current_tool == "marker":
            self.add_marker(scene_pos)

        elif self.current_tool == "label":
            text, ok = QInputDialog.getText(self, "Текстовая метка",
                                           "Введите текст:")
            if ok and text:
                self.add_label(scene_pos, text)

        elif self.current_tool == "eraser":
            self.erase_at_point(scene_pos)

        QGraphicsView.mousePressEvent(self.view, event)

    def on_mouse_move(self, event):
        """Обработка движения мыши"""
        if self.drawing and self.current_tool == "path":
            scene_pos = self.view.mapToScene(event.pos())

            if self.last_point:
                # Рисуем линию
                pen = QPen(QColor(139, 69, 19), 3, Qt.PenStyle.SolidLine)
                self.scene.addLine(self.last_point.x(), self.last_point.y(),
                                 scene_pos.x(), scene_pos.y(), pen)
                self.last_point = scene_pos

        QGraphicsView.mouseMoveEvent(self.view, event)

    def on_mouse_release(self, event):
        """Обработка отпускания мыши"""
        self.drawing = False
        self.last_point = None
        QGraphicsView.mouseReleaseEvent(self.view, event)

    def add_marker(self, pos: QPointF):
        """Добавление маркера локации"""
        color = self.MARKER_COLORS.get(self.current_marker_type, QColor(0, 0, 255))

        marker = QGraphicsEllipseItem(pos.x() - 15, pos.y() - 15, 30, 30)
        marker.setBrush(QBrush(color))
        marker.setPen(QPen(Qt.GlobalColor.black, 2))

        self.scene.addItem(marker)
        self.markers.append(marker)

    def add_label(self, pos: QPointF, text: str):
        """Добавление текстовой метки"""
        label = QGraphicsTextItem(text)
        label.setFont(QFont("Serif", 12, QFont.Weight.Bold))
        label.setDefaultTextColor(QColor(80, 40, 20))
        label.setPos(pos)

        self.scene.addItem(label)
        self.labels.append(label)

    def erase_at_point(self, pos: QPointF):
        """Стирание объекта в точке"""
        items = self.scene.items(QRectF(pos.x() - 5, pos.y() - 5, 10, 10))

        if items:
            item = items[0]
            self.scene.removeItem(item)

            if item in self.markers:
                self.markers.remove(item)
            elif item in self.labels:
                self.labels.remove(item)

    def load_background(self):
        """Загрузка фонового изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение карты",
            "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)

            # Очищаем предыдущий фон
            self.scene.clear()
            self.markers.clear()
            self.labels.clear()

            # Добавляем новый фон
            self.scene.addPixmap(pixmap)

    def save_map(self):
        """Сохранение карты как PNG"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить карту",
            f"map_quest_{self.current_quest_id or 'new'}.png",
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )

        if file_path:
            # Создаем изображение
            image = QImage(800, 600, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)

            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.scene.render(painter)
            painter.end()

            if image.save(file_path):
                # Геймификация
                xp, leveled_up = self.gamification.add_xp("save_map")
                self.gamification.update_stats("maps_saved")

                msg = f"✅ Карта сохранена в {file_path}\n+{xp} XP"
                if leveled_up:
                    msg += f"\n🎉 Новый уровень: {self.gamification.get_current_level()}!"

                QMessageBox.information(self, "Успех", msg)
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить карту")

    def clear_canvas(self):
        """Очистка холста"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите очистить карту?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.scene.clear()
            self.scene.setBackgroundBrush(QBrush(QColor(244, 228, 188)))
            self.markers.clear()
            self.labels.clear()

    def set_quest_id(self, quest_id: int):
        """Привязка карты к квесту"""
        self.current_quest_id = quest_id
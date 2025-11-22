import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from PyQt6.QtGui import QFontDatabase
from pathlib import Path

def load_fonts():
    fonts_dir = Path(__file__).parent / "assets" / "fonts"
    if fonts_dir.exists():
        for font_path in fonts_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_path))

def main():
    app = QApplication(sys.argv)
    load_fonts()
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
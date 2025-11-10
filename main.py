import sys
import os
from app.config import BASE_DIR
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qss_path = os.path.join(BASE_DIR, "app", "ui", "style_gray.qss")  # или свой путь
    try:
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
    except Exception as e:
        print("QSS load error:", e)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

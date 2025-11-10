from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox  # только ради enum кнопок

PALETTE = {
    "bg": "#2E3B3A",      # фон
    "panel": "#3F4D4B",   # карточка
    "text": "#EAE7DC",
    "accent": "#A3D9A5",
    "muted": "#5B615E"
}

class FancyMessageBox(QDialog):
    def __init__(self, parent, title, text, buttons, icon: QIcon | None = None):
        super().__init__(parent)
        self._result = QMessageBox.StandardButton.NoButton

        # Окно без рамки, строго модальное
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # --- Контент ---------------------------------------------------------
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        card = QWidget(self)
        card.setObjectName("card")
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(16, 14, 16, 14)
        card_l.setSpacing(12)

        # Заголовок (как «шапка» — за неё можно таскать окно)
        header = QHBoxLayout()
        self.lblTitle = QLabel(title)
        self.lblTitle.setObjectName("title")
        header.addWidget(self.lblTitle)
        header.addStretch(1)
        card_l.addLayout(header)

        # Текст
        self.lblText = QLabel(text)
        self.lblText.setWordWrap(True)
        self.lblText.setObjectName("text")
        card_l.addWidget(self.lblText)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        for caption, std_btn in buttons:
            b = QPushButton(caption)
            b.setProperty("stdBtn", int(std_btn))
            b.clicked.connect(self._on_clicked)
            btn_row.addWidget(b)
        card_l.addLayout(btn_row)

        root.addWidget(card)

        # Стили под твою палитру
        self.setStyleSheet(f"""
        QDialog {{
            background: transparent;
        }}
        QWidget#card {{
            background: {PALETTE["panel"]};
            border: 1px solid {PALETTE["muted"]};
            border-radius: 12px;
        }}
        QLabel#title {{
            color: {PALETTE["text"]};
            font-size: 16px;
            font-weight: 700;
        }}
        QLabel#text {{
            color: {PALETTE["text"]};
            font-size: 13px;
        }}
        QPushButton {{
            background: {PALETTE["accent"]};
            color: {PALETTE["bg"]};
            border: 1px solid {PALETTE["accent"]};
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            border-color: #8CCF90; /* чуть темнее акцента */
        }}
        QPushButton:pressed {{
            background: #8CCF90;
        }}
        
        QDialog {{
            background: transparent;
        }}
        QWidget#card {{
            background-color: #3F4D4B;
            border: 3px solid #c42b1c;
            border-radius: 14px;
        }}
        """)

        self.resize(420, self.sizeHint().height())

    # — запрет «закрыть чем-то кроме кнопок»
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Escape,):
            return  # игнор
        super().keyPressEvent(e)

    def reject(self):
        # блокируем закрытие Alt+F4 / программное reject()
        return

    def _on_clicked(self):
        btn = self.sender()
        self._result = QMessageBox.StandardButton(btn.property("stdBtn"))
        self.accept()

    # — Перетаскивание окна за заголовок
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            self.move(e.globalPosition().toPoint() - self._drag_pos)
            e.accept()

    # ---- Удобные статические вызовы, похожие на QMessageBox ----
    @staticmethod
    def _run(parent, title, text, buttons):
        dlg = FancyMessageBox(parent, title, text, buttons, None)
        # центрируем над родителем
        if parent:
            geo = parent.frameGeometry()
            dlg.move(geo.center() - dlg.rect().center())
        dlg.exec()
        return dlg._result

    @staticmethod
    def question(parent, title, text,
                 buttons=(("Да", QMessageBox.StandardButton.Yes),
                          ("Нет", QMessageBox.StandardButton.No))):
        return FancyMessageBox._run(parent, title, text, buttons)

    @staticmethod
    def information(parent, title, text,
                    buttons=(("OK", QMessageBox.StandardButton.Ok),)):
        return FancyMessageBox._run(parent, title, text, buttons)

    @staticmethod
    def warning(parent, title, text,
                buttons=(("OK", QMessageBox.StandardButton.Ok),)):
        return FancyMessageBox._run(parent, title, text, buttons)

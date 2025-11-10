from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QLabel, QPushButton, QFileDialog, QFrame, QMessageBox
)
from PyQt6 import QtCore, QtGui
import os, shutil

from app.config import ASSETS_DIR, BASE_DIR


class EditBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать книгу")
        # self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setFixedSize(560, 700)
        self._cover = None
        self._orig_cover_rel = None


        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)


        coverCol = QVBoxLayout()
        coverCol.setSpacing(8)
        coverCol.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.lblCover = QLabel("Обложка\nне выбрана", self)
        self.lblCover.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblCover.setFixedSize(200, 260)
        self.lblCover.setFrameShape(QFrame.Shape.Box)
        self.lblCover.setObjectName("lblCover")

        self.btnPick = QPushButton("Выбрать новую обложку…", self)
        self.btnPick.clicked.connect(self._pick_cover)

        coverCol.addWidget(self.lblCover, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        coverCol.addWidget(self.btnPick, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        root.addLayout(coverCol)


        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        root.addWidget(line)


        form = QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        form.setSpacing(10)

        self.edTitle = QLineEdit(self)
        self.edAuthor = QLineEdit(self)
        self.edDesc = QTextEdit(self)
        self.edDesc.setFixedHeight(160)

        self.edTitle.setPlaceholderText("Название…")
        self.edAuthor.setPlaceholderText("Автор…")
        self.edDesc.setPlaceholderText("Краткое описание…")

        form.addRow("Название:", self.edTitle)
        form.addRow("Автор:", self.edAuthor)
        form.addRow("Описание:", self.edDesc)

        root.addLayout(form)


        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btnOk = QPushButton("Сохранить изменения", self)
        self.btnCancel = QPushButton("Отмена", self)
        self.btnOk.clicked.connect(self._accept)
        self.btnCancel.clicked.connect(self.reject)
        btns.addWidget(self.btnOk)
        btns.addWidget(self.btnCancel)

        root.addLayout(btns)


        self.setObjectName("editBookDialog")
        self.btnPick.setObjectName("btnPickCover")
        self.btnOk.setObjectName("btnOk")
        self.btnCancel.setObjectName("btnCancel")


    def set_book(self, book):
        self.edTitle.setText(book.get("title", "") or "")
        self.edAuthor.setText(book.get("author", "") or "")
        self.edDesc.setPlainText(book.get("description", "") or "")

        rel = book.get("cover")
        if rel:
            self._orig_cover_rel = rel
            self._cover = rel

        px = book.get("cover_pixmap")
        if isinstance(px, QtGui.QPixmap) and not px.isNull():
            self._set_cover_preview(px)
        else:
            if rel:
                abs_path = os.path.join(BASE_DIR, rel)
                if os.path.exists(abs_path):
                    p = QtGui.QPixmap(abs_path)
                    if not p.isNull():
                        self._set_cover_preview(p)

    def data(self):
        return {
            "title": self.edTitle.text().strip(),
            "author": self.edAuthor.text().strip(),
            "description": self.edDesc.toPlainText().strip(),
            "cover": self._cover,
        }


    def _accept(self):
        if not self.edTitle.text().strip() or not self.edAuthor.text().strip():
            QMessageBox.warning(self, "Проверка", "Укажите как минимум название и автора.")
            return
        self.accept()

    def _set_cover_preview(self, px):
        scaled = px.scaled(
            self.lblCover.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        self.lblCover.setPixmap(scaled)
        self.lblCover.setText("")

    def _pick_cover(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Выбрать обложку", os.path.expanduser("~"),
            "Изображения (*.png *.jpg *.jpeg *.webp *.bmp *.gif)"
        )
        if not file:
            return

        px = QtGui.QPixmap(file)
        if px.isNull():
            QMessageBox.warning(self, "Обложка", "Не удалось загрузить изображение.")
            return

        self._set_cover_preview(px)

        covers_dir = os.path.join(ASSETS_DIR, "covers")

        base_name, ext = os.path.splitext(os.path.basename(file))
        ext = ext.lower() or ".png"
        target_abs = os.path.join(covers_dir, base_name + ext)

        #!!!
        counter = 1
        while os.path.exists(target_abs):
            target_abs = os.path.join(covers_dir, f"{base_name} ({counter}){ext}")
            counter += 1

        try:
            shutil.copy2(file, target_abs)
            self._cover = os.path.relpath(target_abs, BASE_DIR)
        except Exception as e:
            QMessageBox.warning(self, "Обложка", f"Не удалось сохранить файл: {e}")
            self._cover = None

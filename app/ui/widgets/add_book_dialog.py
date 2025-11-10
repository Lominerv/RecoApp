import sys
import os
import shutil
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QHBoxLayout, QLabel, QPushButton, \
    QFileDialog, QMessageBox, QApplication, QFrame

from PyQt6 import QtCore, QtGui
from app.config import ASSETS_DIR, BASE_DIR


class AddBookDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Добавить книгу")
        self._cover = None

        # фиксированный размер окна
        self.setFixedSize(560, 640)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Блок обложки сверху: картинка + кнопка под ней, по центру
        coverCol = QVBoxLayout()
        coverCol.setSpacing(8)
        coverCol.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.lblCover = QLabel("Обложка\nне выбрана", self)
        self.lblCover.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblCover.setFixedSize(200, 260)
        self.lblCover.setFrameShape(QFrame.Shape.Box)
        self.lblCover.setStyleSheet("background: #f5f5f5;")

        btnPick = QPushButton("Выбрать обложку…", self)
        btnPick.clicked.connect(self._pick_cover)

        coverCol.addWidget(self.lblCover, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        coverCol.addWidget(btnPick, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        root.addLayout(coverCol)

        # Поля формы под блоком обложки
        form = QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        form.setSpacing(10)

        self.edTitle = QLineEdit(self)
        self.edAuthor = QLineEdit(self)
        self.edTags = QLineEdit(self)
        self.edDesc = QTextEdit(self)
        self.edDesc.setFixedHeight(140)

        self.edTitle.setPlaceholderText("Название... (обязательно)")
        self.edAuthor.setPlaceholderText("Автор... (обязательно)")
        self.edTags.setPlaceholderText("фэнтези, приключения... (обязательно)")
        self.edDesc.setPlaceholderText("Краткое описание... (обязательно)")


        form.addRow("Название", self.edTitle)
        form.addRow("Автор", self.edAuthor)
        form.addRow("Теги (через запятую)", self.edTags)
        form.addRow("Описание", self.edDesc)

        root.addLayout(form)

        # Кнопки сохранения внизу
        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btnOk = QPushButton("Сохранить", self)
        self.btnCancel = QPushButton("Отмена", self)
        self.btnOk.clicked.connect(self._accept)
        self.btnCancel.clicked.connect(self.reject)
        btns.addWidget(self.btnOk)
        btns.addWidget(self.btnCancel)

        root.addLayout(btns)

        self.setObjectName("addBookDialog")
        self.lblCover.setObjectName("lblCover")
        btnPick.setObjectName("btnPickCover")
        self.edTitle.setObjectName("edTitle")
        self.edAuthor.setObjectName("edAuthor")
        self.edTags.setObjectName("edTags")
        self.edDesc.setObjectName("edDesc")
        self.btnOk.setObjectName("btnOk")
        self.btnCancel.setObjectName("btnCancel")

    def data(self) -> dict:
        tags_list = [t.strip() for t in self.edTags.text().split(",") if t.strip()]
        return {
            "title": self.edTitle.text().strip(),
            "author": self.edAuthor.text().strip(),
            "description": self.edDesc.toPlainText().strip(),
            "tags_list": tags_list,
            "cover": self._cover,
        }

    def _pick_cover(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выбрать обложку", os.path.expanduser("~"),
                                              "Изображения (*.png *.jpg *.jpeg *.webp *.bmp *.gif)"
        )
        if not file:
            return

        px = QtGui.QPixmap(file)
        if px.isNull():
            QMessageBox.warning(self, "Обложка", "Не удалось загрузить изображение.")
            return
        scaled = px.scaled(self.lblCover.size(),
                           QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                           QtCore.Qt.TransformationMode.SmoothTransformation)
        self.lblCover.setPixmap(scaled)
        self.lblCover.setText("")

        covers_dir = os.path.join(ASSETS_DIR, "covers")
        base_name, ext = os.path.splitext(os.path.basename(file))
        ext =  ext.lower()
        target_abs = os.path.join(covers_dir, base_name + ext)

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

    def _accept(self):
        if not self.edTitle.text().strip() or not self.edAuthor.text().strip() or not self.edDesc.toPlainText().strip():
            QMessageBox.warning(self, "Проверка", "Поля «Название», «Автор» и «Описание» обязательны.")
            return
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddBookDialog()
    window.show()
    sys.exit(app.exec())
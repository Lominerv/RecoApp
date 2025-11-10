import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QLabel, QSpacerItem, QPushButton, QApplication

CARD_WIDTH = 240
COVER_HEIGHT = 180

class BookCard(QFrame):
    openRequested = QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(320)

        self._book_id = None
        self._cover_px = None

        self.setFixedWidth(CARD_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setProperty("card", True)

        self.lblCover = QLabel("Обложка", self)
        self.lblCover.setFrameShape(QFrame.Shape.Box)
        self.lblCover.setFixedHeight(COVER_HEIGHT)
        self.lblCover.setFrameShape(QFrame.Shape.NoFrame)

        self.lblTitle = QLabel(self)
        self.lblTitle.setWordWrap(True)
        f = self.lblTitle.font()
        f.setPointSize(11)
        f.setBold(True)
        self.lblTitle.setFont(f)
        self.lblTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblTitle.setText("Название книги")

        fm = QtGui.QFontMetrics(self.lblTitle.font())
        self._title_max_h = fm.lineSpacing() * 2
        self.lblTitle.setFixedHeight(self._title_max_h)
        self.lblTitle.setWordWrap(True)

        self.lblAuthor = QLabel(self)
        f = self.lblAuthor.font()
        f.setPointSize(10)
        self.lblAuthor.setFont(f)
        self.lblAuthor.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.lblAuthor.setText("Автор")

        self.lblTags = QLabel(self)
        f = self.lblTags.font()
        f.setPointSize(10)
        self.lblTags.setFont(f)
        self.lblTags.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.lblTags.setText("теги... теги ...")
        self.lblTags.setWordWrap(False)


        self.btnOpen = QPushButton("Подробнее", self)
        self.btnOpen.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btnOpen.clicked.connect(self._emit_open)

        root = QVBoxLayout(self)
        root.addWidget(self.lblCover)
        root.addWidget(self.lblTitle)
        root.addWidget(self.lblAuthor)
        root.addWidget(self.lblTags)
        root.addWidget(self.btnOpen, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        self._object_name()

    def set_book(self, book: dict):
        self.setBookId(book.get("id"))
        self.setTitle(book.get("title", ""))
        self.setAuthor(book.get("author", ""))
        self.setTags(book.get("tags", ""))
        px = book.get("cover_pixmap")
        if isinstance(px, QtGui.QPixmap):
            self.setCoverPixmap(px)

    def setBookId(self, book_id): self._book_id = book_id
    def setTitle(self, title): self._set_title_2lines_elide(title)
    def setAuthor(self, author): self.lblAuthor.setText(f"Автор: {author}")
    def setTags(self, tags: list[str] | str):
        if isinstance(tags, (list, tuple)):
            formatted = [t.capitalize() for t in tags if t.strip()]
            text = ", ".join(formatted) if formatted else "—"
        else:
            text = str(tags).capitalize() if tags else "—"
        self.lblTags.setText(f"Категории: {text}")
    def setCoverPixmap(self, px):
        self._cover_px = px
        self._apply_cover_scaled()


    def _emit_open(self):
        if self._book_id is not None:
            self.openRequested.emit(self._book_id)

    def _elide_single_line(self, label, text):
        fm = QtGui.QFontMetrics(label.font())
        # ширина текста с учётом внутренних отступов карточки
        avail_w = CARD_WIDTH - 16
        return fm.elidedText(text, QtCore.Qt.TextElideMode.ElideRight, avail_w)

    def _set_title_2lines_elide(self, text):
        lbl = self.lblTitle
        fm = QtGui.QFontMetrics(lbl.font())
        # доступная ширина с учётом внутренних отступов карточки
        avail_w = CARD_WIDTH - 16
        max_h = fm.lineSpacing() * 2

        # Быстрый путь: и так помещается в две строки
        r = fm.boundingRect(0, 0, avail_w, 1000,
                            QtCore.Qt.TextFlag.TextWordWrap,
                            text)
        if r.height() <= max_h:
            lbl.setText(text)
            lbl.setToolTip("")
            return

        # Иначе укорачиваем до тех пор, пока не влезет в 2 строки
        lo, hi = 0, len(text)
        best = "…"
        while lo <= hi:
            mid = (lo + hi) // 2
            candidate = (text[:mid].rstrip() + "…") if mid < len(text) else text
            r = fm.boundingRect(0, 0, avail_w, 1000,
                                QtCore.Qt.TextFlag.TextWordWrap,
                                candidate)
            if r.height() <= max_h:
                best = candidate
                lo = mid + 1
            else:
                hi = mid - 1

        lbl.setText(best)
        lbl.setToolTip(text)

    def _apply_cover_scaled(self):
        if not self._cover_px:
            return

        scaled = self._cover_px.scaled(
            CARD_WIDTH - 16, COVER_HEIGHT,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        self.lblCover.setPixmap(scaled)
        self.lblCover.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def _object_name(self):
        self.lblCover.setObjectName("lblCover")
        self.lblTitle.setObjectName("lblTitle")
        self.lblAuthor.setObjectName("lblAuthor")
        self.lblTags.setObjectName("lblTags")
        self.btnOpen.setObjectName("btnOpen")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookCard()
    window.show()
    sys.exit(app.exec())
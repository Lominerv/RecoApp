import os
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox, QLabel, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon





from app.config import icon_path
from app.services import favorites_service as fav_service
from app.services import rating_service
from app.ui.widgets.fancy_message_box import FancyMessageBox

_UI_DIR = os.path.dirname(__file__)
_BOOK_DLG_UI = os.path.join(_UI_DIR, "BookDetailsDialog.ui")


class BookDetailsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(_BOOK_DLG_UI, self)
        self.setFixedSize(750, 550)


        # self.lblCover = QLabel("Обложка", self)
        # self.lblCover.setObjectName("cover")  # <— добавь
        # self.lblCover.setFrameShape(QFrame.Shape.NoFrame)

        self._book_id = None
        self._my_rating = 0

        self.btnAddFav.setCheckable(True)
        self.btnAddFav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btnAddFav.setAutoRaise(True)
        # self.btnAddFav.setStyleSheet("""
        # QToolButton {
        #     border: none;
        #     background: transparent;
        # }
        # """)

        self._icon_state()
        self._connect_signal()

    def set_book(self, book: dict):
        self._book_id = int(book.get("id"))

        self.lblTitle.setText(book.get("title", "") or "")
        f = self.lblTitle.font()
        f.setBold(True)
        self.lblTitle.setFont(f)

        author = book.get("author") or ""
        self.lblAuthor.setText(f"Автор: {author}" if author else "Автор: —")
        f = self.lblAuthor.font()
        f.setBold(True)
        self.lblAuthor.setFont(f)

        tags = book.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        pretty_tags = " · ".join(t.capitalize() for t in tags) if tags else "—"
        self.lblTags.setText(f"Категории: {pretty_tags}")

        desc = book.get("description", "") or ""
        self.teDescription.setOpenExternalLinks(True)
        self.teDescription.setHtml(desc)

        px = book.get("cover_pixmap")
        self.lblCover.setFrameShape(QFrame.Shape.NoFrame)
        if isinstance(px, QPixmap) and not px.isNull():
            self.lblCover.setPixmap(px)
            self.lblCover.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        else:
            self.lblCover.setText("Нет обложки")

        try:
            fav = bool(fav_service.is_favorite(self._book_id))
        except fav_service.NotAuthenticatedError:
            fav = False

        try:
            my = rating_service.get_my_rating(self._book_id)
        except rating_service.NotAuthenticatedError:
            my = 0
        self._render_stars(my or 0)

        old_block = self.btnAddFav.blockSignals(True)
        self.btnAddFav.setChecked(fav)
        self.btnAddFav.blockSignals(old_block)
        self._update_fav_icon(fav)


    def _render_stars(self, rating):
        self._my_rating = max(0, min(5, int(rating or 0)))
        for idx, btn in enumerate(self._stars, start=1):
            on = idx <= self._my_rating
            btn.setChecked(on)
            btn.setIcon(self._icon_star_on if on else self._icon_star_off)

    def _on_rate_clicked(self, rating):
        if not self._book_id:
            return
        try:
            if rating == self._my_rating:
                rating_service.remove_my_rating(self._book_id)
                self._render_stars(0)
            else:
                rating_service.set_rating(self._book_id, rating)
                self._render_stars(rating)
        except rating_service.NotAuthenticatedError:
            self._render_stars(0)
            FancyMessageBox.information(
                self,
                "Требуется вход",
                "Чтобы поставить оценку, войдите в аккаунт."
            )




    def _on_favorite_toggled(self, checked: bool):
        if not self._book_id:
            return
        try:
            new_state = fav_service.set_favorite(self._book_id, checked)
            self._update_fav_icon(new_state)
        except fav_service.NotAuthenticatedError:
            old_block = self.btnAddFav.blockSignals(True)
            self.btnAddFav.setChecked(False)
            self.btnAddFav.blockSignals(old_block)
            self._update_fav_icon(False)
            FancyMessageBox.information(self, "Требуется вход", "Чтобы добавлять в избранное, войдите в аккаунт.")

    def _update_fav_icon(self, is_checked: bool):
        if is_checked:
            icon = QIcon(icon_path("heart_minus.svg"))
            self.btnAddFav.setToolTip("Убрать из избранного")
        else:
            icon = QIcon(icon_path("heart_plus.svg"))
            self.btnAddFav.setToolTip("Добавить в избранное")
        self.btnAddFav.setIcon(icon)

    def _connect_signal(self):
        self.btnAddFav.toggled.connect(self._on_favorite_toggled)

    def _icon_state(self):
        add_favorite = QIcon(icon_path("heart_plus.svg"))
        self.btnAddFav.setIcon(add_favorite)
        self.btnAddFav.setIconSize(QSize(32, 32))

        self._icon_star_on = QIcon(icon_path("star_grade_on.svg"))
        self._icon_star_off = QIcon(icon_path("star_grade_off.svg"))

        self._stars = [self.btnStar1, self.btnStar2, self.btnStar3, self.btnStar4, self.btnStar5]
        for i, btn in enumerate(self._stars, start=1):
            btn.setCheckable(True)
            btn.setAutoExclusive(False)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setStyleSheet("""QToolButton { border: none; background: transparent; } """)
            btn.clicked.connect(lambda _=False, v=i: self._on_rate_clicked(v))



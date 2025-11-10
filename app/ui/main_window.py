import os
from PyQt6 import uic, QtCore
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QActionGroup, QPixmap
from PyQt6.QtWidgets import QMainWindow, QPushButton, QMessageBox, QDialog, QGridLayout, QWidget, QVBoxLayout, \
    QHBoxLayout, QLabel, QSizePolicy, QFrame, QInputDialog

from app.config import icon_path
from app.services import recommendation_service, rating_service, favorites_service
from app.services.admin_service import get_dashboard_stats, add_book, delete_book, edit_book
from app.services.guard import require_admin
from app.services.rating_service import get_book_avg
from app.ui.book_details_dialog import BookDetailsDialog
from app.ui.widgets.add_book_dialog import AddBookDialog
from app.ui.widgets.book_card import BookCard
from app.ui.widgets.edit_book_dialog import EditBookDialog
from app.ui.widgets.fancy_message_box import FancyMessageBox
from app.ui.widgets.flow_layout import FlowLayout
from app.services.auth_service import login, create_user, logout, get_current_user
from app.services.catalog_service import get_books
from app.services.catalog_service import get_book_details


_UI_DIR = os.path.dirname(__file__)
_MAIN_UI = os.path.join(_UI_DIR, "MainWindow.ui")
_BOOK_DLG_UI = os.path.join(_UI_DIR, "BookDetailsDialog.ui")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(_MAIN_UI, self)
        self.setWindowIcon(QIcon(icon_path('app.svg')))
        self.flowFav = FlowLayout(self.favFlowHost, margin=8, spacing=8)
        self.favFlowHost.setLayout(self.flowFav)
        for w in [self.centralwidget, self.pageCatalog, self.pageRecommendations, self.pageAuth]:
            w.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumWidth(850)


        print(hasattr(self, "gridCatalog"))

        self._pages = {
            "catalog": self.pageCatalog,
            "recomendations": self.pageRecommendations,
            "auth": self.pageAuth,
            "favorites": self.pageFavorites,
            "about": self.pageAbout
        }
        self._init_state()
        self._setup_toolbar_icons()
        self._connect_signal()


    def _open_edit_book_dialog(self):
        dlg = EditBookDialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        payload = dlg.data()
        try:
            n = edit_book(title=payload["title"], author=payload["author"], description=payload["description"],
                          cover=payload["cover"])
            self.load_catalog(None)
            self._refresh_admin_dashboard()
            FancyMessageBox.information(self, "Успех", f"Обновленно записей {n}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обновить книгу: {e}")


    def show_favorites(self):
        if get_current_user() is None:
            ans = FancyMessageBox.question(
                self, "Вход",
                "Чтобы увидеть избранное, войдите в аккаунт. Перейти к входу?",
            )
            if ans == QMessageBox.StandardButton.Yes:
                self.navigate("auth")
            return

        self.navigate("favorites")
        self.load_favorites()

    def load_favorites(self):
        try:
            ids = favorites_service.get_favorite_book_ids()
        except favorites_service.NotAuthenticatedError:
            self.navigate("auth")
            return

        # очистить старые карточки
        while self.flowFav.count():
            it = self.flowFav.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        # добавить карточки
        for bid in ids:
            try:
                book = get_book_details(bid)
            except Exception:
                continue
            card = BookCard()
            card.set_book(book)
            card.openRequested.connect(self.show_book_details)
            self.flowFav.addWidget(card)

    def click_recommendation(self):
        if get_current_user() is None:
            if get_current_user() is None:
                res = FancyMessageBox.question(
                    self,
                    "Вход",
                    "Для получения рекомендаций требуется вход, желаете войти?"
                )
                if res == QMessageBox.StandardButton.Yes:
                    self.navigate('auth')
                return
            else:
                self.navigate('recomendations')

        self.navigate('recomendations')
        try:
            n = rating_service.get_my_rated_count()
        except rating_service.NotAuthenticatedError:
            n = 0
        if n < 3:
            self.contentStack.setCurrentWidget(self.pageEmpty)
            if hasattr(self, "lblEmpty") and self.lblEmpty:
                self.lblEmpty.setText(f"Для рекомендаций нужно минимум 3 оценки.\nУ вас сейчас: {n}/3")
            return
        self.load_recommendations()

    def load_recommendations(self):
        self._clear_rec_grid()
        try:
            books = recommendation_service.get_recommendations(limit=15)
        except recommendation_service.NotEnoughData:
            self.contentStack.setCurrentWidget(self.pageEmpty)
            try:
                n = rating_service.get_my_rated_count()
            except rating_service.NotAuthenticatedError:
                n = 0
            if hasattr(self, "lblEmpty") and self.lblEmpty:
                self.lblEmpty.setText(f"Для рекомендаций нужно минимум 3 оценки.\nУ вас сейчас: {n}/3")
            return

        if not books:
            self.contentStack.setCurrentWidget(self.pageList)
            self.flowRec.addWidget(QLabel("Пока нет рекомендаций по вашим тегам"))
            return

        self.contentStack.setCurrentWidget(self.pageList)
        for book in books:
            card = BookCard()
            card.set_book(book)
            card.openRequested.connect(self.show_book_details)
            self.flowRec.addWidget(card)

    def _clear_rec_grid(self):
        while self.flowRec.count():
            item = self.flowRec.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def _init_recommendations_ui(self):
        self.flowRec = FlowLayout(self.cardsContainer_rec, margin=0, spacing=8)
        self.cardsContainer_rec.setLayout(self.flowRec)

        self.btnGoCatalog.clicked.connect(lambda: self.navigate('catalog'))

    def _delete_book_dialog(self):
        title, ok = QInputDialog.getText(self, "Удалить книгу", "Введите название книги: ")
        if not ok or not title.strip():
            return
        try:
            deleted = delete_book(title)
            self.load_catalog(None)
            self._refresh_admin_dashboard()
            QMessageBox.information(self, "Удалено", f"Удалено книг - {deleted}")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось удалить книгу: {e}")

    def _open_add_book_dialog(self):
        dlg = AddBookDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        payload = dlg.data()
        try:
            new_id = add_book(
                title=payload['title'],
                author=payload['author'],
                description=payload['description'],
                tags=payload['tags_list'],
                cover=payload['cover'],
            )
            self.load_catalog(None)
            self._refresh_admin_dashboard()
            QMessageBox.information(self, "Книга", f"Книга добавлена (id={new_id}).")
            self.load_catalog(None)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить книгу: {e}")

    def _is_admin_current(self):
        user = get_current_user()
        return bool(user and user.get("is_admin") == 1)

    def _current_sort_mode(self):
        txt = (self.cbSort.currentText() or "").lower()
        return "popular" if "популяр" in txt else "alpha"

    def load_catalog(self, tag = None, q = None):
        books = get_books(tag = tag, q = q)
        mode = self._current_sort_mode()

        if mode == 'alpha':
            books.sort(key = lambda x: (x.get("title", "").casefold(), x.get("author", "").casefold()))
        else:
            for b in books:
                try:
                    avg = rating_service.get_book_avg(int(b.get("id", 0)))
                except Exception:
                    avg = 0.0
                b["_avg"] = float(avg or 0.0)

            books.sort(
                key=lambda x: (x.get("_avg", 0.0), str(x.get("title", "")).casefold()),
                reverse=True
            )

        while self.flow.count():
            item = self.flow.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)  # отцепить от родителя
                w.deleteLater()

        for book in books:
            card = BookCard()
            card.set_book(book)
            card.openRequested.connect(self.show_book_details)
            self.flow.addWidget(card)

    def show_book_details(self, book_id):
        try:
            book = get_book_details(book_id)
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить книгу: {e}")
            return

        dlg = BookDetailsDialog(self)
        dlg.set_book(book)
        dlg.exec()

    def _connect_signal(self):
        self.actionViewCatalog.triggered.connect(lambda: self.navigate('catalog'))
        self.actionViewRecommendations.triggered.connect(self.click_recommendation)
        self.actionSignInOut.triggered.connect(self._on_sign_in_out_clicked)
        self.actionAbout.triggered.connect(lambda: self.navigate('about'))

        self.actionExit_door.triggered.connect(self.logout_user)

        self.btnRegister.clicked.connect(self._show_register)
        self.btnBackToLogin.clicked.connect(self._show_login)
        self.btnLogin.clicked.connect(self.login_user)
        self.btnDoRegister.clicked.connect(self.on_register_clicked)

        print("selected:", self.comboCategory.currentText())
        self.comboCategory.currentTextChanged.connect(
            lambda text: self.load_catalog(
                None if text == "Все категории" else text.lower(),
                q = self.leSearch.text().strip()
                )
        )
        print("selected_2:", self.comboCategory.currentText())

        self.btnfav.clicked.connect(self.show_favorites)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)

        def _apply_search():
            text = self.leSearch.text().strip()
            q = text or None
            tag = None
            v = self.comboCategory.currentText()
            tag = None if v in (None, "", "Все категории") else v.lower()
            self.load_catalog(tag = tag, q=q)

        self.leSearch.textChanged.connect(lambda _: self._search_timer.start())
        self._search_timer.timeout.connect(_apply_search)
        self.leSearch.returnPressed.connect(_apply_search)

        self.cbSort.currentIndexChanged.connect(lambda _:
                                               self.load_catalog(
                                                   None if self.comboCategory.currentText() == "Все категории" else
                                                   self.comboCategory.currentText().lower(),
                                                   q = self.leSearch.text().strip()))


    def logout_user(self):
        user = get_current_user()

        if user is None:
            FancyMessageBox.information(
                self,
                "Выход",
                "Вы не вошли в систему."
            )
            return

        reply = FancyMessageBox.question(
            self,
            "Выход",
            "Вы уверены, что хотите выйти из аккаунта?"
        )

        if reply == QMessageBox.StandardButton.No:
            return

        logout()

        self.navigate('auth')

        self.actionSignInOut.setEnabled(True)

        FancyMessageBox.information(self, "Выход", "Вы вышли из аккаунта.")

    def login_user(self):
        email = self.leEmail.text().strip()
        password = self.lePassword.text().strip()

        self.lblAuthError.setText("")

        try:
            user = login(email, password)
            self.leEmail.clear()
            self.lePassword.clear()
            self.navigate('catalog')
            self.actionViewRecommendations.setEnabled(True)
            self._refresh_admin_dashboard()
        except ValueError as e:
            self.lblAuthError.setText(str(e))

    def on_register_clicked(self):
        email = self.leRegEmail.text()
        username = self.leRegUsername.text()
        password = self.leRegPassword.text()
        password_con = self.leRegConfirm.text()

        self.lblRegisterError.setText("")
        try:
            user = create_user(email, username, password, password_con)
            self.leRegEmail.clear()
            self.leRegUsername.clear()
            self.leRegPassword.clear()
            self.leRegConfirm.clear()
            self.navigate('catalog')
            self.actionViewRecommendations.setEnabled(True)
        except ValueError as e:
            self.lblRegisterError.setText(str(e))

    def _on_sign_in_out_clicked(self):
        user = get_current_user()
        if not user:
            self.navigate('auth')
            return

        if self._is_admin_current():
            self.navigate('admin')
        else:
            self.navigate('catalog')


    def _show_login(self):
        self.stackedAuth.setCurrentWidget(self.pageLogin)

    def _show_register(self):
        self.stackedAuth.setCurrentWidget(self.pageRegister)

    def navigate(self, name):
        if name == "admin" and not self._is_admin_current():
            QMessageBox.warning(self, "Доступ", "Требуются права администратора.")
            return

        page = self._pages.get(name)
        if page is None:
            QMessageBox.warning(self, 'Навигация', f'Несуществующая страница {name}')
            return

        self.stackMain.setCurrentWidget(page)

        self.actionViewCatalog.setChecked(name == "catalog")
        if name == "auth":
            self.actionViewCatalog.setChecked(False)
            self.actionViewRecommendations.setChecked(False)

    def _init_state(self):
        self.stackMain.setCurrentWidget(self.pageCatalog)
        self.stackedAuth.setCurrentWidget(self.pageLogin)

        #Жирный текст
        font = self.lblAuthError.font()
        font.setBold(True)
        self.lblAuthError.setFont(font)

        font = self.lblTitleLogin.font()
        font.setBold(True)
        self.lblTitleLogin.setFont(font)

        font = self.lblRegisterTitle.font()
        font.setBold(True)
        self.lblRegisterTitle.setFont(font)


        self.scrollCatalog.setWidgetResizable(True)
        self.flow = FlowLayout(self.cardsContainer, spacing=8)
        self.cardsContainer.setLayout(self.flow)
        self.cardsContainer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.scrollCatalog.viewport().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.load_catalog(None)

        self._build_admin_page()

        self._init_recommendations_ui()

    def _set_icon(self, action, file_name):
        action.setIcon(QIcon(icon_path(file_name)))

    def _setup_toolbar_icons(self):
        self._set_icon(self.actionViewCatalog, "cataloge.svg")
        self._set_icon(self.actionViewRecommendations, "star.svg")
        self._set_icon(self.actionSignInOut, "user.svg")
        self._set_icon(self.actionAbout, "info.svg")
        self._set_icon(self.actionExit_door, "exit_door.svg")

        group = QActionGroup(self)
        group.setExclusive(True)

        group.addAction(self.actionViewCatalog)
        group.addAction(self.actionViewRecommendations)

        self._toolbar_group = group

    def _build_admin_page(self):
        print("SignInOut clicked")

        self.pageAdmin = QWidget(self)
        self.pageAdmin.setObjectName("pageAdmin")


        root = QVBoxLayout(self.pageAdmin)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(16)

        self.lblCrown = QLabel(self.pageAdmin)
        self.lblCrown.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblCrown.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

        crown_path = os.path.join("assets", "icons", "crown.svg")
        pix = QPixmap()
        crown_loaded = False
        if os.path.isfile(crown_path):
            crown_loaded = pix.load(crown_path)
        if crown_loaded and not pix.isNull():
            self.lblCrown.setPixmap(pix.scaled(96, 96, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                               QtCore.Qt.TransformationMode.SmoothTransformation))
            self.lblCrown.setMinimumSize(96, 96)
        else:
            self.lblCrown.setText("👑")
            f = self.lblCrown.font()
            f.setPointSize(48)
            self.lblCrown.setFont(f)
            self.lblCrown.setMinimumSize(96, 96)

        self.lblAdminTitle = QLabel("Админ панель", self.pageAdmin)
        f = self.lblAdminTitle.font()
        f.setPointSize(40)
        f.setBold(True)
        self.lblAdminTitle.setFont(f)

        header.addWidget(self.lblCrown)
        header.addWidget(self.lblAdminTitle, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

        root.addLayout(header)

        metricsWrap = QGridLayout()
        metricsWrap.setHorizontalSpacing(16)
        metricsWrap.setVerticalSpacing(16)

        def _make_stat_card(title):
            frame = QFrame(self.pageAdmin)
            frame.setFixedSize(420, 300)
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setProperty("card_metrics", True)

            lay = QVBoxLayout(frame)
            lay.setContentsMargins(16, 16, 16, 16)
            lay.setSpacing(8)

            lblTit = QLabel(title, frame)
            ft = lblTit.font()
            ft.setPointSize(24)
            ft.setBold(True)
            lblTit.setFont(ft)
            lblTit.setWordWrap(True)
            lblTit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            lblN = QLabel("—", frame)
            fn = lblN.font()
            fn.setPointSize(40)
            fn.setBold(True)
            lblN.setFont(fn)
            lblN.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            lay.addWidget(lblTit)
            lay.addWidget(lblN)

            return frame, lblN

        cardBooks, self.lblStatBooks = _make_stat_card("Книг в каталоге")
        cardUsers, self.lblStatUsers = _make_stat_card("Зарегистрированных пользователей")
        cardActive, self.lblStatActive = _make_stat_card("Активных сейчас")

        cardBooks.setObjectName("cardBooks")
        cardUsers.setObjectName("cardUsers")
        cardActive.setObjectName("cardActive")

        self.lblStatBooks.setObjectName("lblStatBooks")
        self.lblStatUsers.setObjectName("lblStatUsers")
        self.lblStatActive.setObjectName("lblStatActive")

        for w in (self.lblStatBooks, self.lblStatUsers, self.lblStatActive):
            w.setObjectName("style_test_admin")
            w.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # задать стиль только внутри admin-страницы
        self.pageAdmin.setStyleSheet("""
            QLabel#style_test_admin {
                font-size: 40px;
                font-weight: 700;
            }
        """)


        metricsWrap.addWidget(cardBooks, 0, 0)
        metricsWrap.addWidget(cardUsers, 0, 1)
        metricsWrap.addWidget(cardActive, 0, 2)

        btnAdd = QPushButton(self)
        self._set_icon(btnAdd, 'add.svg')
        btnAdd.setIconSize(QtCore.QSize(32,32))
        btnAdd.setText("Добавить книгу")
        btnAdd.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        f = btnAdd.font()
        f.setBold(True)
        f.setPointSize(16)
        btnAdd.setFont(f)
        btnAdd.setFixedWidth(260)

        btnEditBook = QPushButton(self)
        self._set_icon(btnEditBook, 'rect.svg')
        btnEditBook.setIconSize(QtCore.QSize(32, 32))
        btnEditBook.setText("Редактировать книгу")
        btnEditBook.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        f = btnEditBook.font()
        f.setBold(True)
        f.setPointSize(16)
        btnEditBook.setFont(f)
        btnEditBook.setFixedWidth(260)

        btnDel = QPushButton(self)
        self._set_icon(btnDel, 'del.svg')
        btnDel.setIconSize(QtCore.QSize(32, 32))
        btnDel.setText("Удалить книгу")
        btnDel.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        f = btnDel.font()
        f.setBold(True)
        f.setPointSize(16)
        btnDel.setFont(f)
        btnDel.setFixedWidth(260)

        root.addSpacing(100)
        root.addLayout(metricsWrap)
        root.addSpacing(100)
        root.addWidget(btnAdd)
        root.addWidget(btnEditBook)
        root.addWidget(btnDel)
        root.addStretch(1)

        self.stackMain.addWidget(self.pageAdmin)
        self._pages["admin"] = self.pageAdmin
        btnAdd.clicked.connect(self._open_add_book_dialog)
        btnDel.clicked.connect(self._delete_book_dialog)
        btnEditBook.clicked.connect(self._open_edit_book_dialog)

    def _refresh_admin_dashboard(self):
        is_admin = self._is_admin_current()

        if not is_admin:
            self.lblStatBooks.setText("—")
            self.lblStatUsers.setText("—")
            self.lblStatActive.setText("—")
            return

        try:
            stats = get_dashboard_stats()
            self.lblStatBooks.setText(str(stats.get("books", "—")))
            self.lblStatUsers.setText(str(stats.get("users", "—")))
            self.lblStatActive.setText(str(stats.get("active", "—")))
        except Exception as e:
            pass


from PyQt6.QtWidgets import QLayout
from PyQt6.QtCore import QPoint, QRect, Qt, QSize


class FlowLayout(QLayout):
    def __init__(self, parent = None, margin = 0, spacing = 0):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing


        #--API--
    def addItem(self, item): self._items.append(item)
    def count(self): return len(self._items)
    def itemAt(self, i): return self._items[i] if i < len(self._items) else None
    def takeAt(self, i): return self._items.pop(i) if i < len(self._items) else None

    #запрет самостоятельного увеличения
    def expandingDirections(self): return Qt.Orientations(0)
    # Высота зависит от ширины
    def hasHeightForWidth(self): return True

    # Высота лейаута при заданной ширине
    def heightForWidth(self, width):
        return self._doLayout(QRect(0, 0, width, 0), test_only = True)

    # Рекомендуемый размер
    def sizeHint(self):
        left, top, right, bottom = self.getContentsMargins()
        # Ширина родительского виджета
        base_width = max(320, self.parentWidget().width())
        #виртуально раскладываем карточки, без реальной расстановки
        h = self._doLayout(QRect(0, 0, base_width - (left + right), 0), test_only = True)
        # Ориентир для построения интерфейса
        return QSize(base_width, h + top + bottom)

    # Минимально возможный размер, максимальная высота 1 карточки
    def minimumSize(self):
        left, top, right, bottom = self.getContentsMargins()
        one_row_height = 0
        for it in self._items:
            one_row_height = max(one_row_height, it.sizeHint().height())
        if one_row_height == 0:
            one_row_height = 1
        return QSize(left + right + 1, top + bottom + one_row_height)


    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, test_only = False)

    # Разметка
    def _doLayout(self, rect, test_only):
        #отступы
        left, top, right, bottom = self.getContentsMargins()
        #начальные координаты
        x = rect.x() + left
        y = rect.y() + top
        #высота текущей строки карточек
        line_height = 0

        #доступная шерина для размещения (без отступов)
        eff_width = rect.width() - (left + right)

        for item in self._items:
            #пропускае скрытые и пустые виджеты
            if item.widget() and not item.widget().isVisible():
                continue

            # Предпочтительный размер каждой карточки
            iw = item.sizeHint().width()
            ih = item.sizeHint().height()

            #
            if (x > rect.x() + left) and (x + iw > rect.x() + left + eff_width):
                x = rect.x() + left
                y += line_height + self._spacing
                line_height = 0


            if not test_only:
                item.setGeometry(QRect(x,y, iw, ih))

            #Двигаем для следующей карточки
            x += iw + self._spacing
            line_height = max(line_height, ih)

        # Общая высота (от верхнего края, до последнеё строки)
        total_height = (y + line_height + bottom) - rect.y()
        return total_height


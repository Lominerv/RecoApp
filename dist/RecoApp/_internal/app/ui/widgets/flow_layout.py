from PyQt6.QtWidgets import QLayout
from PyQt6.QtCore import QPoint, QRect, Qt, QSize


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=8):
        super().__init__(parent)
        self._items = []
        self._spacing = spacing
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)
        self.invalidate()

    def count(self):
        return len(self._items)

    def itemAt(self, i):
        return self._items[i] if 0 <= i < len(self._items) else None

    def takeAt(self, i):
        if 0 <= i < len(self._items):
            item = self._items.pop(i)
            self.invalidate()
            return item
        return None

    def invalidate(self):
        super().invalidate()
        parent = self.parentWidget()
        if parent is not None:
            parent.updateGeometry()

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        rect = QRect(0, 0, width, 0)
        return self._doLayout(rect, True)

    def sizeHint(self):
        left, top, right, bottom = self.getContentsMargins()
        parent_width = self.parentWidget().width() if self.parentWidget() else 800
        h = self._doLayout(QRect(0, 0, parent_width - left - right, 0), True)
        return QSize(parent_width, h + top + bottom)

    def minimumSize(self):
        left, top, right, bottom = self.getContentsMargins()
        row_h = max((it.sizeHint().height() for it in self._items), default=1)
        return QSize(left + right + 1, top + bottom + row_h)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def _doLayout(self, rect, test_only):
        left, top, right, bottom = self.getContentsMargins()

        eff_width = rect.width() - (left + right)

        x = left
        y = top
        line_h = 0

        for item in self._items:
            iw = item.sizeHint().width()
            ih = item.sizeHint().height()

            # Перенос строки
            if x > left and (x + iw) > (left + eff_width):
                x = left
                y += line_h + self._spacing
                line_h = 0

            if not test_only:
                item.setGeometry(QRect(x, y, iw, ih))

            x += iw + self._spacing
            line_h = max(line_h, ih)

        return y + line_h + bottom

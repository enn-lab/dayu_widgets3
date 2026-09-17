"""Tokenized line edit with inline tags."""

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

from dayu_widgets import dayu_theme
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.tag import MTag


class _FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, spacing=4):
        super(_FlowLayout, self).__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing
        self._items = []

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation.Horizontal)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(_FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        margins = self.contentsMargins()
        effective = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        x = effective.x()
        y = effective.y()
        line_height = 0
        for item in self._items:
            item_size = item.sizeHint()
            next_x = x + item_size.width() + self._spacing
            if next_x - self._spacing > effective.right() and line_height:
                x = effective.x()
                y += line_height + self._spacing
                next_x = x + item_size.width() + self._spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item_size))
            x = next_x
            line_height = max(line_height, item_size.height())
        return y + line_height - rect.y() + margins.bottom()


class MTagLineEdit(QtWidgets.QWidget):
    """An inline token editor that keeps the input after all tags."""

    sig_tag_added = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(MTagLineEdit, self).__init__(parent)
        self.setObjectName("tag_line_edit")
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self._tags = []
        self._layout = _FlowLayout(self, spacing=4)
        self._editor = MLineEdit().small()
        self._editor.setObjectName("tag_line_edit_editor")
        self._editor.setFrame(False)
        self._editor.setMinimumWidth(96)
        self._apply_editor_palette()
        self._editor.textChanged.connect(self._update_editor_width)
        self._layout.addWidget(self._editor)

    @property
    def line_edit(self):
        return self._editor

    def tags(self):
        return tuple(self._tags)

    def add_tag(self, text):
        text = str(text).strip()
        if not text or any(tag.get_dayu_text() == text for tag in self._tags):
            QtCore.QTimer.singleShot(0, self._reset_editor)
            return
        editor_item = self._layout.takeAt(self._layout.count() - 1)
        tag = MTag(text).closeable()
        tag.sig_closed.connect(lambda current=tag: self.remove_tag(current))
        self._tags.append(tag)
        self._layout.addWidget(tag)
        self._layout.addItem(editor_item)
        QtCore.QTimer.singleShot(0, self._reset_editor)
        self.sig_tag_added.emit(text)
        self._refresh_layout()

    def remove_tag(self, tag):
        if tag not in self._tags:
            return
        self._tags.remove(tag)
        self._layout.removeWidget(tag)
        tag.deleteLater()
        self._refresh_layout()

    def _update_editor_width(self, text):
        if not self._tags:
            width = max(96, self.width() - 8)
        else:
            width = max(96, self._editor.fontMetrics().horizontalAdvance(text) + 24)
        self._editor.setFixedWidth(width)
        self._refresh_layout()

    def _apply_editor_palette(self):
        palette = self._editor.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(dayu_theme.text_primary_color))
        palette.setColor(
            QtGui.QPalette.ColorRole.PlaceholderText,
            QtGui.QColor(dayu_theme.text_secondary_color),
        )
        self._editor.setPalette(palette)

    def _reset_editor(self):
        self._editor.clear()
        self._editor.setFocus(QtCore.Qt.OtherFocusReason)
        self._refresh_layout()

    def _refresh_layout(self):
        self._layout.invalidate()
        width = max(1, self.width())
        self.setMinimumHeight(self.heightForWidth(width))
        self.updateGeometry()

    def sizeHint(self):
        width = max(320, self._layout.minimumSize().width())
        return QtCore.QSize(width, self.heightForWidth(width))

    def heightForWidth(self, width):
        return self._layout.heightForWidth(width)

    def hasHeightForWidth(self):
        return True

    def resizeEvent(self, event):
        super(MTagLineEdit, self).resizeEvent(event)
        self._update_editor_width(self._editor.text())
        self._layout.invalidate()

    def showEvent(self, event):
        self._apply_editor_palette()
        super(MTagLineEdit, self).showEvent(event)

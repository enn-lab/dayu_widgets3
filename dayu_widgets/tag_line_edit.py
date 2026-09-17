"""Tokenized line edit with inline tags."""

from qtpy import QtCore
from qtpy import QtWidgets

from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.menu import MMenu
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
        self._menu = None
        self._max_rows = 3
        self._layout = _FlowLayout(self, spacing=4)
        self._editor = MLineEdit().small()
        self._editor.setObjectName("tag_line_edit_editor")
        self._editor.setFrame(False)
        self._editor.setMinimumWidth(96)
        self._editor.installEventFilter(self)
        self._editor.textChanged.connect(self._update_editor_width)
        self._layout.addWidget(self._editor)

    @property
    def line_edit(self):
        return self._editor

    def tags(self):
        return tuple(self._tags)

    def set_options(self, options):
        """Set selectable values used by the multi-select popup menu."""
        self._menu = MMenu(exclusive=False, parent=self)
        self._menu.set_data([str(option) for option in options])
        self._menu.sig_value_changed.connect(self._set_selected_values)
        return self

    def selected_values(self):
        return [tag.get_dayu_text() for tag in self._tags]

    def _set_selected_values(self, values):
        values = values if isinstance(values, list) else [values]
        selected = {str(value) for value in values}
        for tag in tuple(self._tags):
            if tag.get_dayu_text() not in selected:
                self.remove_tag(tag)
        for value in values:
            if not any(tag.get_dayu_text() == str(value) for tag in self._tags):
                self._insert_tag(str(value))
        self._editor.clear()
        self._editor.setFocus(QtCore.Qt.OtherFocusReason)
        self._refresh_layout()

    def _insert_tag(self, text):
        tag = MTag(text).closeable()
        tag.sig_closed.connect(lambda current=tag: self.remove_tag(current))
        self._tags.append(tag)
        editor_item = self._layout.takeAt(self._layout.count() - 1)
        self._layout.addWidget(tag)
        self._layout.addItem(editor_item)

    def add_tag(self, text):
        text = str(text).strip()
        if not text or any(tag.get_dayu_text() == text for tag in self._tags):
            QtCore.QTimer.singleShot(0, self._reset_editor)
            return
        if self._menu:
            values = self.selected_values() + [text]
            self._menu.set_value(values)
            self._set_selected_values(values)
        else:
            self._insert_tag(text)
        QtCore.QTimer.singleShot(0, self._reset_editor)
        self.sig_tag_added.emit(text)
        self._refresh_layout()

    def remove_tag(self, tag):
        if tag not in self._tags:
            return
        self._tags.remove(tag)
        self._layout.removeWidget(tag)
        tag.deleteLater()
        if self._menu:
            self._menu.set_value(self.selected_values())
        self._refresh_layout()

    def _update_editor_width(self, text):
        if not self._tags:
            width = max(96, self.width() - 8)
        else:
            width = max(96, self._editor.fontMetrics().horizontalAdvance(text) + 24)
        self._editor.setFixedWidth(width)
        self._refresh_layout()

    def _reset_editor(self):
        self._editor.clear()
        self._editor.setFocus(QtCore.Qt.OtherFocusReason)
        self._refresh_layout()

    def _refresh_layout(self):
        self._layout.invalidate()
        width = max(1, self.width())
        row_height = self._editor.sizeHint().height() + self._layout._spacing
        height = min(self.heightForWidth(width), row_height * self._max_rows)
        self.setFixedHeight(height)
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

    def focusInEvent(self, event):
        super(MTagLineEdit, self).focusInEvent(event)
        self._editor.setFocus(QtCore.Qt.OtherFocusReason)

    def mousePressEvent(self, event):
        super(MTagLineEdit, self).mousePressEvent(event)
        if self._menu and event.button() == QtCore.Qt.LeftButton:
            self._menu.set_value(self.selected_values())
            self._menu.popup(self.mapToGlobal(QtCore.QPoint(0, self.height())))

    def eventFilter(self, watched, event):
        if watched is self._editor and event.type() == QtCore.QEvent.FocusIn:
            self.setProperty("dayu_tag_line_focus", event.type() == QtCore.QEvent.FocusIn)
            self.style().polish(self)
            if self._menu:
                QtCore.QTimer.singleShot(0, self._show_menu)
        elif watched is self._editor and event.type() == QtCore.QEvent.FocusOut:
            self.setProperty("dayu_tag_line_focus", False)
            self.style().polish(self)
        return super(MTagLineEdit, self).eventFilter(watched, event)

    def _show_menu(self):
        if self._menu and self._editor.hasFocus():
            self._menu.set_value(self.selected_values())
            self._menu.popup(self.mapToGlobal(QtCore.QPoint(0, self.height())))

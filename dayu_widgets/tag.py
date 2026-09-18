"""Modern tag components."""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.mixin import cursor_mixin
from dayu_widgets.qt import MIcon


@cursor_mixin
class MTag(QtWidgets.QWidget):
    """A compact semantic tag with optional close and click actions."""

    sig_closed = QtCore.Signal()
    sig_clicked = QtCore.Signal()

    def __init__(self, text="", parent=None):
        super(MTag, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.setProperty("dayu_tag_style", "outline")
        self.setProperty("dayu_tag_color", dayu_theme.secondary_text_color)
        self._pressed = False

        self._label = QtWidgets.QLabel(str(text), self)
        self._label.setObjectName("tag_text")
        self._label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self._icon_label = QtWidgets.QLabel(self)
        self._icon_label.setObjectName("tag_icon")
        self._icon_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self._icon_label.setVisible(False)
        self._close_button = QtWidgets.QToolButton(self)
        self._close_button.setObjectName("tag_close_button")
        self._close_button.setIcon(MIcon("close_line.svg"))
        self._close_button.setIconSize(QtCore.QSize(12, 12))
        self._close_button.setFixedSize(16, 16)
        self._close_button.setCursor(QtCore.Qt.PointingHandCursor)
        self._close_button.setAutoRaise(True)
        self._close_button.setVisible(False)
        self._close_button.clicked.connect(self._close)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(4)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._label)
        layout.addWidget(self._close_button)

    def _close(self):
        self.sig_closed.emit()
        self.close()

    def get_dayu_text(self):
        return self._label.text()

    def set_dayu_text(self, value):
        self._label.setText(str(value or ""))

    def get_dayu_color(self):
        return self.property("dayu_tag_color")

    def set_dayu_color(self, value):
        """Store the semantic color; the QSS owns how it is painted.

        ``MTag`` deliberately raises no local stylesheet: a widget-level
        stylesheet wins over the application one and would freeze the tag on
        the colors captured at construction time, so a later
        ``dayu_theme.apply()`` / theme switch could never restyle it.
        """
        color = QtGui.QColor(value)
        if not color.isValid():
            raise ValueError("tag color should be a valid QColor value")
        self.setProperty("dayu_tag_color", color.name())

    dayu_text = QtCore.Property(str, get_dayu_text, set_dayu_text)
    dayu_color = QtCore.Property(str, get_dayu_color, set_dayu_color)

    def setIcon(self, icon):
        """Show an optional leading icon."""
        if icon is None or icon.isNull():
            self._icon_label.clear()
            self._icon_label.setVisible(False)
            return
        self._icon_label.setPixmap(icon.pixmap(12, 12))
        self._icon_label.setFixedSize(12, 12)
        self._icon_label.setVisible(True)

    def closeable(self):
        self.setProperty("dayu_closeable", "true")
        self._close_button.setVisible(True)
        return self

    def clickable(self):
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setProperty("dayu_clickable", True)
        return self

    def no_border(self):
        self.setProperty("dayu_tag_style", "filled")
        return self

    def coloring(self, color):
        self.set_dayu_color(color)
        return self

    def mousePressEvent(self, event):
        self._pressed = event.button() == QtCore.Qt.LeftButton
        super(MTag, self).mousePressEvent(event)
        # Keep the press from bubbling up to a parent token editor, which
        # would otherwise treat a click on a tag as a click on the container
        # and open its popup.
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._pressed and event.button() == QtCore.Qt.LeftButton and self.property("dayu_clickable"):
            self.sig_clicked.emit()
        self._pressed = False
        super(MTag, self).mouseReleaseEvent(event)
        event.accept()


@cursor_mixin
class MCheckableTag(QtWidgets.QCheckBox):
    """A compact checkable tag with modern selected and hover states."""

    def __init__(self, text="", parent=None):
        super(MCheckableTag, self).__init__(str(text), parent)
        self.setCheckable(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setProperty("dayu_tag_color", dayu_theme.accent_color)


class MNewTag(QtWidgets.QWidget):
    """Inline control that turns into an editor for creating a tag."""

    sig_add_tag = QtCore.Signal(str)

    def __init__(self, text="New tag", parent=None):
        super(MNewTag, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self._add_button = QtWidgets.QToolButton(self)
        self._add_button.setObjectName("new_tag_add_button")
        self._add_button.setText(str(text))
        self._add_button.setIcon(MIcon("add_line.svg"))
        self._add_button.clicked.connect(self._show_editor)
        self._line_edit = QtWidgets.QLineEdit(self)
        self._line_edit.setPlaceholderText(str(text))
        self._line_edit.setVisible(False)
        self._line_edit.returnPressed.connect(self._commit)
        self._line_edit.installEventFilter(self)

        layout = QtWidgets.QStackedLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self._add_button)
        layout.addWidget(self._line_edit)

    def _show_editor(self):
        self.layout().setCurrentWidget(self._line_edit)
        self._line_edit.setFocus(QtCore.Qt.MouseFocusReason)

    def _commit(self):
        text = self._line_edit.text().strip()
        if text:
            self.sig_add_tag.emit(text)
        self._line_edit.clear()
        self.layout().setCurrentWidget(self._add_button)

    def focusOutEvent(self, event):
        self.layout().setCurrentWidget(self._add_button)
        super(MNewTag, self).focusOutEvent(event)

    def eventFilter(self, watched, event):
        if watched is self._line_edit and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self._line_edit.clear()
                self.layout().setCurrentWidget(self._add_button)
                return True
        return super(MNewTag, self).eventFilter(watched, event)

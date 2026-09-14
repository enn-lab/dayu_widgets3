"""Icon menu with optional secondary text for modern popup menus."""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.qt import MIcon


class MIconMenuItem(QtWidgets.QWidget):
    """A QWidgetAction body with icon, title, description and check state."""

    def __init__(self, icon=None, text="", description="", checked=False, parent=None):
        super(MIconMenuItem, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setProperty("dayu_checked", bool(checked))

        self._icon_label = QtWidgets.QLabel(self)
        self._icon_label.setFixedSize(32, 32)
        self._icon_label.setAlignment(QtCore.Qt.AlignCenter)
        if icon:
            icon = icon if isinstance(icon, QtGui.QIcon) else QtGui.QIcon(icon)
            self._icon_label.setPixmap(icon.pixmap(32, 32))

        self._text_label = QtWidgets.QLabel(str(text), self)
        self._text_label.setObjectName("icon_menu_text")
        self._description_label = QtWidgets.QLabel(str(description), self)
        self._description_label.setObjectName("icon_menu_description")
        self._description_label.setVisible(bool(description))

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        text_layout.addWidget(self._text_label)
        text_layout.addWidget(self._description_label)

        self._check_label = QtWidgets.QLabel(self)
        self._check_label.setObjectName("icon_menu_check")
        self._check_label.setFixedWidth(16)
        self._check_label.setAlignment(QtCore.Qt.AlignCenter)
        self._check_label.setPixmap(MIcon("check.svg").pixmap(14, 14))
        self._check_label.setVisible(bool(checked))

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(9)
        layout.addWidget(self._icon_label)
        layout.addLayout(text_layout, 1)
        layout.addWidget(self._check_label)
        self.setMinimumHeight(48 if description else 46)

    def set_checked(self, checked):
        checked = bool(checked)
        self.setProperty("dayu_checked", checked)
        self._check_label.setVisible(checked)
        self.style().polish(self)


class MIconMenu(QtWidgets.QMenu):
    """Modern popup menu for icon-based choices with secondary descriptions."""

    sig_item_triggered = QtCore.Signal(object)

    def __init__(self, parent=None, exclusive=False):
        super(MIconMenu, self).__init__(parent)
        self._action_group = QtWidgets.QActionGroup(self)
        self._action_group.setExclusive(bool(exclusive))

    def add_item(self, text, icon=None, description="", checked=False, data=None):
        action = QtWidgets.QWidgetAction(self)
        action.setText(str(text))
        action.setCheckable(True)
        action.setChecked(bool(checked))
        action.setData(data)
        widget = MIconMenuItem(icon, text, description, checked, self)
        action.setDefaultWidget(widget)
        action.toggled.connect(widget.set_checked)
        action.triggered.connect(lambda _checked=False, act=action: self.sig_item_triggered.emit(act))
        self._action_group.addAction(action)
        self.addAction(action)
        return action

    def add_icon_item(self, text, icon=None, description="", checked=False, data=None):
        """Alias with an explicit name for callers building icon-only menus."""
        return self.add_item(text, icon, description, checked, data)

    def clear_items(self):
        self.clear()
        for action in self._action_group.actions():
            self._action_group.removeAction(action)

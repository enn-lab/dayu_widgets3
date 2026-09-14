"""Example for icon menus with secondary descriptions."""

# Import third-party modules
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.divider import MDivider
from dayu_widgets.icon_menu import MIconMenu
from dayu_widgets.qt import MIcon
from dayu_widgets.tool_button import MToolButton


class IconMenuExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(IconMenuExample, self).__init__(parent)
        self.setWindowTitle("Example for MIconMenu")
        self.resize(420, 180)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(MDivider("Icon choices"))

        button = MToolButton().text_only()
        button.setText("Choose Maya version")
        menu = MIconMenu(parent=button, exclusive=True)
        menu.add_item("2026", MIcon("app-maya.png"), "Recommended", checked=True, data="2026")
        menu.add_item("2025", MIcon("app-maya.png"), "Stable", data="2025")
        menu.add_item("2024", MIcon("app-maya.png"), "Legacy", data="2024")
        menu.sig_item_triggered.connect(lambda action: button.setText(action.text()))
        button.setMenu(menu)
        layout.addWidget(button)
        layout.addStretch()


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        test = IconMenuExample()
        dayu_theme.apply(test)
        test.show()

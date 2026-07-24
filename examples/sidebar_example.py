# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.avatar import MAvatar
from dayu_widgets.divider import MDivider
from dayu_widgets.label import MLabel
from dayu_widgets.qt import MPixmap
from dayu_widgets.sidebar import MSidebar
from dayu_widgets.tool_button import MToolButton


class SidebarExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SidebarExample, self).__init__(parent)
        self.setWindowTitle("Examples for MSidebar")
        self.resize(900, 600)
        self._init_ui()

    def _init_ui(self):
        # -- Build the sidebar --
        sidebar = MSidebar()

        # Top brand area.
        brand_label = MLabel("Trae Work").h4()
        sidebar.set_top_widget(brand_label)

        # Leaf navigation items.
        sidebar.add_item({"text": "Home", "icon": "home_line.svg"})
        sidebar.add_item({"text": "Projects", "icon": "folder_line.svg", "badge": "12"})
        sidebar.add_item({"text": "Search", "icon": "search_line.svg"})

        sidebar.add_divider()

        # Collapsible menu group with sub items.
        sidebar.add_menu({
            "title": "Workspace",
            "items": [
                {"text": "Tasks", "icon": "check.svg", "badge": "5"},
                {"text": "Calendar", "icon": "calendar_line.svg"},
                {"text": "Messages", "icon": "user_line.svg", "badge": "9+"},
            ],
        })

        sidebar.add_menu({
            "title": "Library",
            "items": [
                {"text": "Components", "icon": "list_view.svg"},
                {"text": "Templates", "icon": "tree_view.svg"},
            ],
        })

        sidebar.add_divider()

        sidebar.add_item({"text": "Settings", "icon": "edit_line.svg"})

        # Bottom user area.
        user_widget = QtWidgets.QWidget()
        user_lay = QtWidgets.QHBoxLayout()
        user_lay.setContentsMargins(0, 0, 0, 0)
        user_lay.setSpacing(8)
        avatar = MAvatar()
        avatar.set_dayu_image(MPixmap("avatar.png"))
        avatar.set_dayu_size(28)
        user_name = MLabel("Alice")
        user_lay.addWidget(avatar)
        user_lay.addWidget(user_name)
        user_lay.addStretch()
        user_widget.setLayout(user_lay)
        sidebar.set_bottom_widget(user_widget)

        # Select the first item by default.
        first_item = sidebar._navigation_widgets[0]
        sidebar.set_current_item(first_item)

        sidebar.sig_current_changed.connect(self._on_current_changed)

        # -- Right side: demo controls + content --
        self._content_label = MLabel("Click an item on the left.").secondary()
        self._content_label.setWordWrap(True)
        self._content_label.setAlignment(QtCore.Qt.AlignCenter)

        compact_button = MToolButton().text_beside_icon().svg("left_line.svg")
        compact_button.setText("Toggle Compact")
        compact_button.clicked.connect(lambda: sidebar.set_dayu_compact(not sidebar.get_dayu_compact()))

        right_panel = QtWidgets.QWidget()
        right_lay = QtWidgets.QVBoxLayout()
        right_lay.setContentsMargins(20, 20, 20, 20)
        right_lay.addWidget(MDivider("Content"))
        right_lay.addWidget(self._content_label, 1)
        right_lay.addWidget(MDivider("Controls"))
        right_lay.addWidget(compact_button)
        right_lay.addStretch()
        right_panel.setLayout(right_lay)

        main_lay = QtWidgets.QHBoxLayout()
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(sidebar)
        main_lay.addWidget(right_panel, 1)
        self.setLayout(main_lay)

    def _on_current_changed(self, item):
        self._content_label.setText("Current: {}".format(item.get_dayu_text()))


if __name__ == "__main__":
    # Import local modules
    from dayu_widgets.qt import application

    with application() as app:
        test = SidebarExample()
        dayu_theme.apply(test)
        test.show()

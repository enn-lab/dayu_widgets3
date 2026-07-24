"""
Trae Theme Demo

Demonstrates the Trae-inspired dark theme with sidebar.
"""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.divider import MDivider
from dayu_widgets.label import MLabel
from dayu_widgets.push_button import MPushButton
from dayu_widgets.sidebar import MSidebar
from dayu_widgets.theme import MTheme


class ThemeDemo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ThemeDemo, self).__init__(parent)
        self.setWindowTitle("Trae Theme Demo")
        self.resize(1100, 700)
        self._init_ui()

    def _init_ui(self):
        # -- Left: Sidebar with sample items --
        self.sidebar = MSidebar()
        self.sidebar.add_item({"text": "Home", "icon": "home_line.svg"})
        self.sidebar.add_item({"text": "Projects", "icon": "folder_line.svg", "badge": "3"})
        self.sidebar.add_item({"text": "Search", "icon": "search_line.svg"})
        self.sidebar.add_divider()
        self.sidebar.add_menu({
            "title": "Workspace",
            "items": [
                {"text": "Tasks", "icon": "check.svg", "badge": "5"},
                {"text": "Calendar", "icon": "calendar_line.svg"},
            ],
        })
        self.sidebar.add_item({"text": "Settings", "icon": "edit_line.svg"})
        self.sidebar.set_current_item(self.sidebar._navigation_widgets[0])

        # -- Right: Content area --
        header = MLabel("Theme Showcase").h3()

        info_card = QtWidgets.QWidget()
        info_card.setObjectName("card")
        info_lay = QtWidgets.QVBoxLayout()
        info_lay.setContentsMargins(16, 16, 16, 16)
        info_lay.setSpacing(8)
        info_lay.addWidget(MLabel("Current Theme").h4())
        info_lay.addWidget(MLabel("Trae Theme (Dark + Blue)"))
        info_card.setLayout(info_lay)

        # Color swatches
        swatches = QtWidgets.QWidget()
        swatch_lay = QtWidgets.QGridLayout()
        swatch_lay.setSpacing(8)
        colors = [
            ("Background", "background_color"),
            ("Background In", "background_in_color"),
            ("Background Out", "background_out_color"),
            ("Primary", "primary_color"),
            ("Title Text", "title_color"),
            ("Primary Text", "primary_text_color"),
            ("Secondary Text", "secondary_text_color"),
            ("Border", "border_color"),
        ]
        for idx, (name, attr) in enumerate(colors):
            lbl = MLabel(name).secondary()
            val = MLabel(str(getattr(dayu_theme, attr, "N/A"))).code()
            swatch_lay.addWidget(lbl, idx, 0)
            swatch_lay.addWidget(val, idx, 1)
        swatches.setLayout(swatch_lay)

        # Action buttons
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(MPushButton("Default"))
        btn_row.addWidget(MPushButton("Primary").primary())
        btn_row.addWidget(MPushButton("Success").success())
        btn_row.addWidget(MPushButton("Warning").warning())
        btn_row.addWidget(MPushButton("Danger").danger())
        btn_row.addStretch()

        right_lay = QtWidgets.QVBoxLayout()
        right_lay.setContentsMargins(24, 24, 24, 24)
        right_lay.setSpacing(16)
        right_lay.addWidget(header)
        right_lay.addWidget(MDivider())
        right_lay.addWidget(info_card)
        right_lay.addWidget(MLabel("Color Palette").h4())
        right_lay.addWidget(swatches)
        right_lay.addWidget(MDivider())
        right_lay.addWidget(MLabel("Buttons").h4())
        right_lay.addLayout(btn_row)
        right_lay.addStretch()

        right_panel = QtWidgets.QWidget()
        right_panel.setLayout(right_lay)

        # -- Main layout --
        main_lay = QtWidgets.QHBoxLayout()
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.sidebar)
        main_lay.addWidget(right_panel, 1)
        self.setLayout(main_lay)


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        demo = ThemeDemo()
        thm = MTheme("trae", primary_color="red")
        thm.apply(demo)
        demo.show()

"""
Trae Theme Demo

Demonstrates the Trae-inspired dark theme alongside the default dayu theme.
Use the toggle button to switch between themes.
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
from dayu_widgets.tool_button import MToolButton
from dayu_widgets.themes.trae import MTraeTheme
from dayu_widgets.themes.trae import apply_trae_theme


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

        # -- Right: Content area with theme showcase --
        header = MLabel("Theme Showcase").h3()

        # Theme info card
        info_card = QtWidgets.QWidget()
        info_card.setObjectName("card")
        info_lay = QtWidgets.QVBoxLayout()
        info_lay.setContentsMargins(16, 16, 16, 16)
        info_lay.setSpacing(8)
        info_lay.addWidget(MLabel("Current Theme").h4())
        self._theme_label = MLabel("Default Dayu (Dark + Orange)")
        info_lay.addWidget(self._theme_label)
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
        self._swatch_labels = []
        for idx, (name, attr) in enumerate(colors):
            lbl = MLabel(name).secondary()
            val = MLabel("").code()
            val.setObjectName("swatch_" + attr)
            swatch_lay.addWidget(lbl, idx, 0)
            swatch_lay.addWidget(val, idx, 1)
            self._swatch_labels.append((attr, val))
        swatches.setLayout(swatch_lay)

        # Toggle button
        self._toggle_btn = MPushButton().primary()
        self._toggle_btn.setText("Switch to Trae Theme")
        self._toggle_btn.clicked.connect(self._toggle_theme)

        # Action buttons showcase
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
        right_lay.addWidget(self._toggle_btn)

        right_panel = QtWidgets.QWidget()
        right_panel.setLayout(right_lay)

        # -- Main layout --
        main_lay = QtWidgets.QHBoxLayout()
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.sidebar)
        main_lay.addWidget(right_panel, 1)
        self.setLayout(main_lay)

        self._is_trae = False
        self._update_swatches()

    def _toggle_theme(self):
        import dayu_widgets
        if self._is_trae:
            # Restore default dayu theme
            default = dayu_widgets.theme.MTheme("dark", primary_color=dayu_widgets.theme.MTheme.orange)
            dayu_widgets.dayu_theme = default
            default.apply(self)
            self._theme_label.setText("Default Dayu (Dark + Orange)")
            self._toggle_btn.setText("Switch to Trae Theme")
        else:
            # Apply Trae theme globally
            trae = MTraeTheme()
            dayu_widgets.dayu_theme = trae
            trae.apply(self)
            self._theme_label.setText("Trae Theme (Dark + Teal)")
            self._toggle_btn.setText("Switch to Dayu Theme")
        self._is_trae = not self._is_trae
        # Refresh sidebar items to pick up new theme colors
        self.sidebar.update()
        for menu in self.sidebar._navigation_widgets:
            menu.update()
            if hasattr(menu, 'items'):
                for item in menu.items():
                    item.update()
        self._update_swatches()

    def _update_swatches(self):
        import dayu_widgets
        theme = dayu_widgets.dayu_theme
        for attr, lbl in self._swatch_labels:
            val = getattr(theme, attr, "N/A")
            lbl.setText(val)


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        demo = ThemeDemo()
        dayu_theme.apply(demo)
        demo.show()

"""Show the three navigation container levels used by the modern theme."""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.item_view import MListView
from dayu_widgets.label import MLabel
from dayu_widgets.sidebar import MSidebar


class SidebarHierarchyExample(QtWidgets.QWidget):
    """Primary sidebar, secondary content sidebar and tertiary list navigation."""

    def __init__(self, parent=None):
        super(SidebarHierarchyExample, self).__init__(parent)
        self.setWindowTitle("Sidebar hierarchy")
        self.resize(960, 560)

        primary = MSidebar().primary()
        primary.add_item({"text": "Overview", "icon": "home_line.svg", "level": 1})
        primary.add_item({"text": "Projects", "icon": "folder_line.svg", "badge": "12", "level": 1})
        primary.add_item({"text": "Activity", "icon": "time_line.svg", "level": 2})
        primary.set_current_item(primary._navigation_widgets[0])

        secondary = MSidebar().secondary()
        secondary.add_item({"text": "General", "icon": "settings_line.svg", "level": 2})
        secondary.add_item({"text": "Members", "icon": "user_line.svg", "level": 3})
        secondary.add_item({"text": "Integrations", "icon": "link.svg", "level": 3})
        secondary.set_current_item(secondary._navigation_widgets[0])

        tertiary = MListView().tertiary()
        tertiary.setModel(QtCore.QStringListModel(["Details", "Versions", "Comments", "Files"]))
        tertiary.setCurrentIndex(tertiary.model().index(0, 0))

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(12)
        content_layout.addWidget(MLabel("Modern navigation hierarchy").h2())
        content_layout.addWidget(
            MLabel(
                "Primary separates application areas; secondary organizes the current area; "
                "tertiary keeps local categories compact."
            ).secondary()
        )
        content_layout.addWidget(tertiary)
        content_layout.addStretch()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(primary)
        layout.addWidget(secondary)
        layout.addWidget(content, 1)


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        test = SidebarHierarchyExample()
        dayu_theme.apply(test)
        test.show()

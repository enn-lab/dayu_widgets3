"""
MSidebar
"""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.divider import MDivider
from dayu_widgets.qt import get_scale_factor
from dayu_widgets.sidebar_item import MSidebarItem
from dayu_widgets.sidebar_menu import MSidebarMenu


class MSidebar(QtWidgets.QWidget):
    """A vertical navigation sidebar.

    Layout::

        +------------------+
        | top widget       |  <- optional header (logo / brand)
        +------------------+
        | item / menu ...  |  <- scrollable navigation area
        |                  |
        |                  |
        +------------------+
        | bottom widget    |  <- optional footer (user / settings)
        +------------------+

    Navigation entries are :class:`MSidebarItem` (leaf) or
    :class:`MSidebarMenu` (collapsible group).  The sidebar keeps track of
    the currently selected item and keeps the selection exclusive.

    Properties:
        dayu_compact: bool, compact mode shows icons only
        dayu_width: int, normal mode width
    """

    sig_current_changed = QtCore.Signal(object)

    CompactWidth = 56
    NormalWidth = 220

    def __init__(self, parent=None):
        super(MSidebar, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setObjectName("sidebar")

        self._dayu_compact = False
        self._current_item = None
        self._navigation_widgets = []  # flat list of items/menus for selection

        scale_x, _ = get_scale_factor()
        self._normal_width = int(MSidebar.NormalWidth * scale_x)
        self._compact_width = int(MSidebar.CompactWidth * scale_x)

        # -- Top area --
        self._top_widget = QtWidgets.QWidget(self)
        self._top_widget.setStyleSheet("background-color: transparent;")
        self._top_layout = QtWidgets.QHBoxLayout()
        self._top_layout.setContentsMargins(12, 12, 12, 12)
        self._top_layout.setSpacing(8)
        self._top_widget.setLayout(self._top_layout)
        self._top_widget.setVisible(False)

        # -- Scrollable navigation area --
        self._content_widget = QtWidgets.QWidget(self)
        self._content_widget.setStyleSheet("background-color: transparent;")
        self._content_layout = QtWidgets.QVBoxLayout()
        self._content_layout.setContentsMargins(8, 8, 8, 8)
        self._content_layout.setSpacing(2)
        self._content_layout.addStretch()
        self._content_widget.setLayout(self._content_layout)

        self._scroll_area = QtWidgets.QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scroll_area.setWidget(self._content_widget)

        # -- Bottom area --
        self._bottom_widget = QtWidgets.QWidget(self)
        self._bottom_widget.setStyleSheet("background-color: transparent;")
        self._bottom_layout = QtWidgets.QHBoxLayout()
        self._bottom_layout.setContentsMargins(12, 8, 12, 12)
        self._bottom_layout.setSpacing(8)
        self._bottom_widget.setLayout(self._bottom_layout)
        self._bottom_widget.setVisible(False)

        # -- Main layout --
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self._top_widget)
        main_lay.addWidget(MDivider())
        main_lay.addWidget(self._scroll_area, 1)
        main_lay.addWidget(MDivider())
        main_lay.addWidget(self._bottom_widget)
        self.setLayout(main_lay)

        self.setFixedWidth(self._normal_width)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    def get_dayu_compact(self):
        return self._dayu_compact

    def set_dayu_compact(self, value):
        self._dayu_compact = bool(value)
        self.setFixedWidth(self._compact_width if self._dayu_compact else self._normal_width)
        for widget in self._navigation_widgets:
            widget.set_dayu_compact(self._dayu_compact)

    def get_dayu_width(self):
        return self._normal_width

    def set_dayu_width(self, value):
        self._normal_width = int(value)
        if not self._dayu_compact:
            self.setFixedWidth(self._normal_width)

    dayu_compact = QtCore.Property(bool, get_dayu_compact, set_dayu_compact)
    dayu_width = QtCore.Property(int, get_dayu_width, set_dayu_width)

    # ------------------------------------------------------------------
    # Fluent API
    # ------------------------------------------------------------------
    def compact(self):
        self.set_dayu_compact(True)
        return self

    def set_normal_width(self, width):
        self.set_dayu_width(width)
        return self

    # ------------------------------------------------------------------
    # Public API: building the sidebar
    # ------------------------------------------------------------------
    def add_item(self, item):
        """Append a navigation item.

        ``item`` can be a :class:`MSidebarItem` instance or a dict with
        keys ``text`` / ``icon`` / ``badge``.
        """
        if isinstance(item, dict):
            item = MSidebarItem(
                text=item.get("text", ""),
                icon=item.get("icon", ""),
                badge=item.get("badge", ""),
            )
        item.sig_clicked.connect(self._handle_item_clicked)
        item.set_dayu_compact(self._dayu_compact)
        # Insert before the trailing stretch.
        self._content_layout.insertWidget(self._content_layout.count() - 1, item)
        self._navigation_widgets.append(item)
        return item

    def add_menu(self, menu):
        """Append a collapsible menu group.

        ``menu`` can be a dict ``{"title": str, "items": [...]}`` or an
        :class:`MSidebarMenu` instance.
        """
        if isinstance(menu, dict):
            inst = MSidebarMenu(title=menu.get("title", ""))
            inst.add_items(menu.get("items", []))
            menu = inst
        else:
            menu.set_dayu_compact(self._dayu_compact)
        menu.sig_item_clicked.connect(self._handle_item_clicked)
        menu.set_dayu_compact(self._dayu_compact)
        self._content_layout.insertWidget(self._content_layout.count() - 1, menu)
        self._navigation_widgets.append(menu)
        return menu

    def add_divider(self):
        divider = MDivider()
        self._content_layout.insertWidget(self._content_layout.count() - 1, divider)
        return divider

    def set_top_widget(self, widget):
        self._clear_layout(self._top_layout)
        if widget is not None:
            self._top_layout.addWidget(widget)
            self._top_widget.setVisible(True)
        else:
            self._top_widget.setVisible(False)
        return self

    def set_bottom_widget(self, widget):
        self._clear_layout(self._bottom_layout)
        if widget is not None:
            self._bottom_layout.addWidget(widget)
            self._bottom_widget.setVisible(True)
        else:
            self._bottom_widget.setVisible(False)
        return self

    def clear(self):
        """Remove all navigation entries (top/bottom widgets are kept)."""
        self._current_item = None
        self._navigation_widgets = []
        self._clear_layout(self._content_layout)
        self._content_layout.addStretch()

    def current_item(self):
        return self._current_item

    def set_current_item(self, item):
        """Programmatically select an item."""
        self._handle_item_clicked(item)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _handle_item_clicked(self, item):
        if not isinstance(item, MSidebarItem):
            return
        if self._current_item is item:
            return
        if self._current_item is not None:
            self._current_item.set_dayu_selected(False)
        self._current_item = item
        item.set_dayu_selected(True)
        self.sig_current_changed.emit(item)

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None and widget is not layout.parent():
                widget.setParent(None)
                widget.deleteLater()

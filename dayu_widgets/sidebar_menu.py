"""
MSidebarMenu
"""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.qt import MIcon
from dayu_widgets.sidebar_item import MSidebarItem


class MSidebarMenu(QtWidgets.QWidget):
    """A collapsible group inside the sidebar.

    Renders a clickable title with an expand/collapse arrow and stacks
    :class:`MSidebarItem` children underneath.  Children are indented to
    visually convey the hierarchy.

    Properties:
        dayu_title: str, group title
        dayu_expanded: bool, whether children are visible
        dayu_compact: bool, compact mode hides the title text
    """

    sig_expanded_changed = QtCore.Signal(bool)
    sig_item_clicked = QtCore.Signal(object)

    def __init__(self, title="", parent=None):
        super(MSidebarMenu, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet("background-color: transparent;")

        self._dayu_title = title
        self._dayu_expanded = True
        self._dayu_compact = False
        self._hovered = False

        # -- Header --
        self._arrow_label = QtWidgets.QLabel(self)
        self._arrow_label.setFixedSize(16, 16)
        self._arrow_label.setStyleSheet("background-color: transparent;")
        self._title_label = QtWidgets.QLabel(self)
        self._title_label.setObjectName("sidebar_menu_title")
        self._title_label.setStyleSheet(
            "color: {}; font-size: 12px; font-weight: 600; background-color: transparent;".format(dayu_theme.secondary_text_color)
        )

        header_lay = QtWidgets.QHBoxLayout()
        header_lay.setContentsMargins(12, 8, 12, 8)
        header_lay.setSpacing(6)
        header_lay.addWidget(self._arrow_label)
        header_lay.addWidget(self._title_label)
        header_lay.addStretch()

        self._header_widget = QtWidgets.QWidget(self)
        self._header_widget.setAttribute(QtCore.Qt.WA_StyledBackground)
        self._header_widget.setObjectName("sidebar_menu_header")
        self._header_widget.setLayout(header_lay)
        self._header_widget.setFixedHeight(32)
        self._header_widget.installEventFilter(self)
        self._header_widget.setStyleSheet("background-color: transparent;")

        # -- Children container --
        self._content_widget = QtWidgets.QWidget(self)
        self._content_widget.setStyleSheet("background-color: transparent;")
        self._content_layout = QtWidgets.QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 4)
        self._content_layout.setSpacing(0)
        self._content_widget.setLayout(self._content_layout)

        # -- Main layout --
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self._header_widget)
        main_lay.addWidget(self._content_widget)
        self.setLayout(main_lay)

        self._title_label.setText(title)
        self._update_arrow()
        self._apply_compact()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    def get_dayu_title(self):
        return self._dayu_title

    def set_dayu_title(self, value):
        self._dayu_title = value or ""
        self._title_label.setText(self._dayu_title)
        self._title_label.setToolTip(self._dayu_title if self._dayu_compact else "")

    def get_dayu_expanded(self):
        return self._dayu_expanded

    def set_dayu_expanded(self, value):
        self._dayu_expanded = bool(value)
        self._content_widget.setVisible(self._dayu_expanded)
        self._update_arrow()
        self.sig_expanded_changed.emit(self._dayu_expanded)

    def get_dayu_compact(self):
        return self._dayu_compact

    def set_dayu_compact(self, value):
        self._dayu_compact = bool(value)
        self._apply_compact()

    dayu_title = QtCore.Property(str, get_dayu_title, set_dayu_title)
    dayu_expanded = QtCore.Property(bool, get_dayu_expanded, set_dayu_expanded)
    dayu_compact = QtCore.Property(bool, get_dayu_compact, set_dayu_compact)

    # ------------------------------------------------------------------
    # Fluent API
    # ------------------------------------------------------------------
    def set_title(self, title):
        self.set_dayu_title(title)
        return self

    def set_expanded(self, expanded):
        self.set_dayu_expanded(expanded)
        return self

    # ------------------------------------------------------------------
    # Child items management
    # ------------------------------------------------------------------
    def add_item(self, item):
        """Add a :class:`MSidebarItem` (or a dict describing one) into the group."""
        if isinstance(item, dict):
            item = MSidebarItem(
                text=item.get("text", ""),
                icon=item.get("icon", ""),
                badge=item.get("badge", ""),
            )
        item.set_indent(16)
        item.sig_clicked.connect(self._relay_item_clicked)
        self._content_layout.addWidget(item)
        return item

    def add_items(self, items):
        for item in items:
            self.add_item(item)
        return self

    def items(self):
        items = []
        for index in range(self._content_layout.count()):
            widget = self._content_layout.itemAt(index).widget()
            if isinstance(widget, MSidebarItem):
                items.append(widget)
        return items

    def clear(self):
        while self._content_layout.count():
            widget = self._content_layout.takeAt(0).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _relay_item_clicked(self, item):
        self.sig_item_clicked.emit(item)

    def _update_arrow(self):
        icon_name = "down_line.svg" if self._dayu_expanded else "right_line.svg"
        color = dayu_theme.primary_color if self._hovered else dayu_theme.icon_color
        self._arrow_label.setPixmap(MIcon(icon_name, color).pixmap(12, 12))

    def _apply_compact(self):
        self._title_label.setVisible(not self._dayu_compact)
        if self._dayu_compact:
            self._header_widget.setToolTip(self._dayu_title)
        else:
            self._header_widget.setToolTip("")
        # Propagate compact flag to children.
        for item in self.items():
            item.set_dayu_compact(self._dayu_compact)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def eventFilter(self, watched, event):
        if watched is self._header_widget:
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                self.set_dayu_expanded(not self._dayu_expanded)
            elif event.type() == QtCore.QEvent.Enter:
                self._hovered = True
                self._update_arrow()
            elif event.type() == QtCore.QEvent.Leave:
                self._hovered = False
                self._update_arrow()
        return super(MSidebarMenu, self).eventFilter(watched, event)

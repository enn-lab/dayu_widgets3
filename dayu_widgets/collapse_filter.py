from qtpy import QtWidgets, QtCore, QtGui
from dayu_widgets import dayu_theme
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.item_model import MTableModel, MSortFilterModel
from dayu_widgets.item_view import MTableView
from dayu_widgets.tool_button import MToolButton
from dayu_widgets.qt import MPixmap
from dayu_widgets.mixin import property_mixin


class MFilterModel(MTableModel):
    def __init__(self, parent=None):
        super(MFilterModel, self).__init__(parent)
        self.set_header_list([
            {"key": "name", "label": "Name", "checkable": True, "searchable": True},
            {"key": "count", "label": "Count", "searchable": False}
        ])


@property_mixin
class MFilterSection(QtWidgets.QWidget):
    sig_changed = QtCore.Signal()

    def __init__(self, title, parent=None):
        super(MFilterSection, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self._dayu_size = dayu_theme.small
        
        # --- Title Bar ---
        self.title_label = MLabel(parent=self)
        self.expand_icon = MLabel(parent=self)
        self.expand_icon.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
        header_lay = QtWidgets.QHBoxLayout()
        header_lay.addWidget(self.expand_icon)
        header_lay.addWidget(self.title_label)
        header_lay.addStretch()
        
        self.header_widget = QtWidgets.QWidget(parent=self)
        self.header_widget.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.header_widget.setObjectName("title")
        self.header_widget.setLayout(header_lay)
        policy = QtWidgets.QSizePolicy.Minimum
        self.header_widget.setSizePolicy(policy, policy)
        self.header_widget.setCursor(QtCore.Qt.PointingHandCursor)
        self.title_label.setCursor(QtCore.Qt.PointingHandCursor)
        self.header_widget.installEventFilter(self)
        self.title_label.installEventFilter(self)

        # --- Content ---
        self.search_input = MLineEdit().search().small()
        self.search_input.setPlaceholderText("Filter...")
        
        self.model = MFilterModel()
        self.proxy = MSortFilterModel()
        self.proxy.setSourceModel(self.model)
        self.proxy.set_header_list(self.model.header_list)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.search_input.textChanged.connect(self.proxy.set_search_pattern)
        
        self.view = MTableView(size=dayu_theme.small, show_row_count=False)
        self.view.setShowGrid(False)
        self.view.horizontalHeader().setVisible(False)
        self.view.verticalHeader().setVisible(False)
        self.view.verticalHeader().setDefaultSectionSize(22) # Compact rows
        self.view.setModel(self.proxy)
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection) # Checkbox only
        
        # Resize columns
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        
        self.model.dataChanged.connect(self.sig_changed)
        
        content_lay = QtWidgets.QVBoxLayout()
        content_lay.setContentsMargins(10, 2, 2, 2)
        content_lay.setSpacing(2)
        content_lay.addWidget(self.search_input)
        content_lay.addWidget(self.view)
        content_lay.addStretch() # Ensure content is pushed to top if section is stretched
        
        self.content_widget = QtWidgets.QWidget(parent=self)
        self.content_widget.setLayout(content_lay)
        
        # --- Main Layout ---
        self.main_lay = QtWidgets.QVBoxLayout()
        self.main_lay.setContentsMargins(0, 0, 0, 0)
        self.main_lay.setSpacing(0)
        self.main_lay.addWidget(self.header_widget)
        self.main_lay.addWidget(self.content_widget)
        self.setLayout(self.main_lay)
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setMouseTracking(True)
        
        self.set_title(title)
        self.set_expand(True) # Default expand
        
        # Initial size setup
        self.set_dayu_size(self._dayu_size)

    def set_expand(self, value):
        self.setProperty("expand", value)

    def _set_expand(self, value):
        self.content_widget.setVisible(value)
        self._update_expand_icon()

    def set_title(self, value):
        self.setProperty("title", value)

    def _set_title(self, value):
        self.title_label.setText(value)

    def eventFilter(self, widget, event):
        if widget in [self.header_widget, self.title_label]:
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                self.set_expand(not self.property("expand"))
        return super(QtWidgets.QWidget, self).eventFilter(widget, event)

    def set_data(self, data_list):
        for item in data_list:
            state = item.get("checked", 0)
            item["name_checked"] = state
            item["checked"] = state
        self.model.set_data_list(data_list)
        
        # Auto-height
        row_count = len(data_list)
        max_rows = 10
        height = min(row_count, max_rows) * 25 + 5
        self.view.setMinimumHeight(height)
        self.view.setMaximumHeight(height if row_count <= max_rows else 300)

    def get_checked_ids(self):
        ids = []
        for item in self.model.get_data_list():
            if item.get("name_checked") == 2:
                ids.append(item.get("id"))
        return ids

    def clear_selection(self):
        data = self.model.get_data_list()
        for item in data:
            item["name_checked"] = 0
            item["checked"] = 0
        self.model.set_data_list(data)

    def set_dayu_size(self, value):
        self._dayu_size = value
        self._update_expand_icon()
        if hasattr(self, 'header_widget'):
            header_height = value + 4 
            self.header_widget.setFixedHeight(header_height)
            padding = 5 if value <= dayu_theme.small else 8
            if self.header_widget.layout():
                self.header_widget.layout().setContentsMargins(padding, 0, padding, 0)
                self.header_widget.layout().setSpacing(padding)
        if hasattr(self, 'title_label'):
            font_size = 12
            if value == dayu_theme.tiny: font_size = 11
            elif value == dayu_theme.small: font_size = 12
            elif value == dayu_theme.medium: font_size = 14
            elif value == dayu_theme.large: font_size = 16
            self.title_label.setStyleSheet(f"font-size: {font_size}px")

    def _update_expand_icon(self):
        if not hasattr(self, 'expand_icon'):
            return
        value = self.property("expand")
        icon_name = "down_line.svg" if value else "right_line.svg"
        icon_size = 12
        if self._dayu_size > dayu_theme.small:
            icon_size = int(self._dayu_size * 0.5)
        self.expand_icon.setPixmap(MPixmap(icon_name).scaledToHeight(icon_size))


@property_mixin
class _MCollapseFilterContent(QtWidgets.QWidget):
    """Internal content widget containing all sections"""
    filter_changed = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super(_MCollapseFilterContent, self).__init__(parent)
        self._sections = {}
        self._dayu_size = dayu_theme.small
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(1)
        self.main_layout.addStretch(1)

    def set_dayu_size(self, value):
        self._dayu_size = value
        for section in self._sections.values():
            if hasattr(section, 'set_dayu_size'):
                section.set_dayu_size(value)

    def add_section(self, key, label, data_list, expanded=True):
        section = MFilterSection(label)
        section.set_data(data_list)
        section.set_expand(expanded)
        section.set_dayu_size(self._dayu_size)
        section.sig_changed.connect(lambda: self._on_section_changed(key))
        
        self.main_layout.insertWidget(self.main_layout.count() - 1, section)
        self._sections[key] = section

    def _on_section_changed(self, key):
        state = self.get_filter_state()
        self.filter_changed.emit(state)

    def get_filter_state(self):
        state = {}
        for key, section in self._sections.items():
            state[key] = section.get_checked_ids()
        return state

    def clear_all(self):
        for section in self._sections.values():
            section.clear_selection()

    def expand_all(self):
        for section in self._sections.values():
            section.set_expand(True)

    def collapse_all(self):
        for section in self._sections.values():
            section.set_expand(False)


@property_mixin
class MCollapseFilter(QtWidgets.QWidget):
    """
    Main Filter Component.
    Includes a Top Bar (Clear/Expand/Collapse) and a Scrollable Content Area.
    """
    filter_changed = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super(MCollapseFilter, self).__init__(parent)
        self._content = _MCollapseFilterContent()
        self._content.filter_changed.connect(self.filter_changed)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- Top Bar ---
        self.top_bar_layout = QtWidgets.QHBoxLayout()
        self.top_bar_layout.setContentsMargins(5, 5, 5, 5)
        
        self.clear_btn = MToolButton().text_only().small()
        self.clear_btn.setText("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        
        self.expand_btn = MToolButton().icon_only().small().svg("expand_line_dark.svg")
        self.expand_btn.setToolTip("Expand All")
        self.expand_btn.clicked.connect(self.expand_all)
        
        self.collapse_btn = MToolButton().icon_only().small().svg("collapse_line_dark.svg")
        self.collapse_btn.setToolTip("Collapse All")
        self.collapse_btn.clicked.connect(self.collapse_all)
        
        self.top_bar_layout.addWidget(self.clear_btn)
        self.top_bar_layout.addStretch()
        self.top_bar_layout.addWidget(self.expand_btn)
        self.top_bar_layout.addWidget(self.collapse_btn)
        
        # --- Scroll Area ---
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self._content)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        self.main_layout.addLayout(self.top_bar_layout)
        self.main_layout.addWidget(self.scroll)

    # --- API Forwarding ---

    def add_section(self, key, label, data_list, expanded=True):
        self._content.add_section(key, label, data_list, expanded)

    def get_filter_state(self):
        return self._content.get_filter_state()

    def clear_all(self):
        self._content.clear_all()

    def expand_all(self):
        self._content.expand_all()

    def collapse_all(self):
        self._content.collapse_all()

    def set_dayu_size(self, value):
        # Update Top Bar buttons
        self.clear_btn.setProperty("dayu_size", value)
        self.expand_btn.setProperty("dayu_size", value)
        self.collapse_btn.setProperty("dayu_size", value)
        self.style().polish(self.clear_btn)
        self.style().polish(self.expand_btn)
        self.style().polish(self.collapse_btn)
        
        # Update Content
        self._content.set_dayu_size(value)
        
    def tiny(self):
        self.set_dayu_size(dayu_theme.tiny)
        return self
        
    def small(self):
        self.set_dayu_size(dayu_theme.small)
        return self
        
    def medium(self):
        self.set_dayu_size(dayu_theme.medium)
        return self
        
    def large(self):
        self.set_dayu_size(dayu_theme.large)
        return self
        
    def huge(self):
        self.set_dayu_size(dayu_theme.huge)
        return self

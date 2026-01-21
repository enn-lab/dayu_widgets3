# Import third-party modules
from itertools import groupby
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.button_group import MToolButtonGroup
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.item_model import MSortFilterModel
from dayu_widgets.item_model import MTableModel
from dayu_widgets.item_view import MBigView
from dayu_widgets.item_view import MListView
from dayu_widgets.item_view import MTableView
from dayu_widgets.item_view import MTreeView
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.tool_button import MToolButton


class MItemViewMultiSet(QtWidgets.QWidget):
    sig_double_clicked = QtCore.Signal(QtCore.QModelIndex)
    sig_left_clicked = QtCore.Signal(QtCore.QModelIndex)
    sig_current_changed = QtCore.Signal(QtCore.QModelIndex, QtCore.QModelIndex)
    sig_current_row_changed = QtCore.Signal(QtCore.QModelIndex, QtCore.QModelIndex)
    sig_current_column_changed = QtCore.Signal(QtCore.QModelIndex, QtCore.QModelIndex)
    sig_selection_changed = QtCore.Signal(QtCore.QItemSelection, QtCore.QItemSelection)
    sig_context_menu = QtCore.Signal(object)

    def __init__(self, table_view=True, big_view=False, tree_view=False, list_view=False, parent=None):
        super(MItemViewMultiSet, self).__init__(parent)
        self.sort_filter_model = MSortFilterModel()
        self.source_model = MTableModel()
        self.sort_filter_model.setSourceModel(self.source_model)
        self.raw_data_list = []
        self._is_grouped = False
        self._pre_group_view_index = 0

        self.stack_widget = QtWidgets.QStackedWidget()

        self.view_button_grp = MToolButtonGroup(exclusive=True)
        data_group = []
        if table_view:
            self.table_view = MTableView(show_row_count=True)
            self.table_view.doubleClicked.connect(self.sig_double_clicked)
            self.table_view.pressed.connect(self.slot_left_clicked)
            self.table_view.setModel(self.sort_filter_model)
            self.stack_widget.addWidget(self.table_view)
            data_group.append({"svg": "table_view.svg", "checkable": True, "tooltip": "Table View"})
        if tree_view:
            self.tree_view = MTreeView()
            self.tree_view.doubleClicked.connect(self.sig_double_clicked)
            self.tree_view.pressed.connect(self.slot_left_clicked)
            self.tree_view.setModel(self.sort_filter_model)
            self.stack_widget.addWidget(self.tree_view)
            data_group.append({"svg": "tree_view.svg", "checkable": True, "tooltip": "Tree View"})
        if list_view:
            self.list_view = MListView()
            self.list_view.doubleClicked.connect(self.sig_double_clicked)
            self.list_view.pressed.connect(self.slot_left_clicked)
            self.list_view.setModel(self.sort_filter_model)
            self.stack_widget.addWidget(self.list_view)
            data_group.append({"svg": "list_view.svg", "checkable": True, "tooltip": "List View"})
        if big_view:
            self.big_view = MBigView()
            self.big_view.doubleClicked.connect(self.sig_double_clicked)
            self.big_view.pressed.connect(self.slot_left_clicked)
            self.big_view.setModel(self.sort_filter_model)
            self.stack_widget.addWidget(self.big_view)
            data_group.append({"svg": "big_view.svg", "checkable": True, "tooltip": "Big View"})

        # 设置多个view 共享 MItemSelectionModel
        leader_view = self.stack_widget.widget(0)
        self.selection_model = leader_view.selectionModel()
        for index in range(self.stack_widget.count()):
            if index == 0:
                continue
            other_view = self.stack_widget.widget(index)
            other_view.setSelectionModel(self.selection_model)

        self.selection_model.currentChanged.connect(self.sig_current_changed)
        self.selection_model.currentRowChanged.connect(self.sig_current_row_changed)
        self.selection_model.currentColumnChanged.connect(self.sig_current_column_changed)
        self.selection_model.selectionChanged.connect(self.sig_selection_changed)

        self.tool_bar = QtWidgets.QWidget()
        self.top_lay = QtWidgets.QHBoxLayout()
        self.top_lay.setContentsMargins(0, 0, 0, 0)
        if data_group and len(data_group) > 1:
            self.view_button_grp.sig_checked_changed.connect(self.stack_widget.setCurrentIndex)
            self.view_button_grp.set_button_list(data_group)
            self.view_button_grp.set_dayu_checked(0)
            self.top_lay.addWidget(self.view_button_grp)

        self.group_label = MLabel("Group By:").secondary()
        self.group_combo = MComboBox().small()
        self.group_combo.setFixedWidth(120)
        self.group_combo.currentIndexChanged.connect(self._slot_group_changed)
        self.group_label.setVisible(False)
        self.group_combo.setVisible(False)
        
        self.search_line_edit = MLineEdit().search().small()
        self.search_attr_button = MToolButton().icon_only().svg("down_fill.svg").small()
        self.search_line_edit.set_prefix_widget(self.search_attr_button)
        self.search_line_edit.textChanged.connect(self.sort_filter_model.set_search_pattern)
        self.search_line_edit.setVisible(False)

        self.top_lay.addStretch()
        self.top_lay.addWidget(self.group_label)
        self.top_lay.addWidget(self.group_combo)
        self.top_lay.addSpacing(10)
        self.top_lay.addWidget(self.search_line_edit)
        self.tool_bar.setLayout(self.top_lay)

        self.main_lay = QtWidgets.QVBoxLayout()
        self.main_lay.setSpacing(5)
        self.main_lay.setContentsMargins(0, 0, 0, 0)
        self.main_lay.addWidget(self.tool_bar)
        self.main_lay.addWidget(self.stack_widget)

        self.setLayout(self.main_lay)

    def enable_context_menu(self):
        for index in range(self.stack_widget.count()):
            view = self.stack_widget.widget(index)
            view.enable_context_menu(True)
            view.sig_context_menu.connect(self.sig_context_menu)

    def set_no_data_text(self, text):
        for index in range(self.stack_widget.count()):
            view = self.stack_widget.widget(index)
            view.set_no_data_text(text)

    def set_selection_mode(self, mode):
        for index in range(self.stack_widget.count()):
            view = self.stack_widget.widget(index)
            view.setSelectionMode(mode)

    def tool_bar_visible(self, flag):
        self.tool_bar.setVisible(flag)

    @QtCore.Slot(QtCore.QModelIndex)
    def slot_left_clicked(self, start_index):
        button = QtWidgets.QApplication.mouseButtons()
        if button == QtCore.Qt.LeftButton:
            real_index = self.sort_filter_model.mapToSource(start_index)
            self.sig_left_clicked.emit(real_index)

    def set_header_list(self, header_list):
        self.header_list = header_list
        self.source_model.set_header_list(header_list)
        self.sort_filter_model.set_header_list(header_list)
        self.sort_filter_model.setSourceModel(self.source_model)
        self.source_model.clear()
        
        self.group_combo.clear()
        self.group_combo.addItem("None")
        for h in header_list:
            if h.get("label") and h.get("key"):
                self.group_combo.addItem(h.get("label"), h.get("key"))
                
        for index in range(self.stack_widget.count()):
            view = self.stack_widget.widget(index)
            view.set_header_list(header_list)

    def tool_bar_append_widget(self, widget):
        self.top_lay.addWidget(widget)

    def tool_bar_insert_widget(self, widget):
        self.top_lay.insertWidget(0, widget)

    @QtCore.Slot()
    def setup_data(self, data_list):
        self.raw_data_list = data_list
        self._apply_grouping()

    def _flatten(self, data_list):
        out = []
        for x in data_list:
            new_x = x.copy()
            new_x.pop("_parent", None) # Clean up old parent reference to avoid crash
            children = new_x.pop("children", [])
            out.append(new_x)
            if children:
                out.extend(self._flatten(children))
        return out

    def _group_by(self, data_list, key):
        # Sort first for groupby
        # Handle missing keys or None values by converting to string
        data_list.sort(key=lambda x: str(x.get(key, "")))
        groups = []
        
        # Determine the primary key for displaying group title
        primary_key = "name"
        if hasattr(self, 'header_list') and self.header_list:
            # Usually the first column is the primary column
            primary_key = self.header_list[0].get("key", "name")

        for k, g in groupby(data_list, key=lambda x: x.get(key, "")):
            children = list(g)
            group_label = "{} ({})".format(k, len(children))
            
            group_node = {
                primary_key: group_label,
                "children": children,
                # Optional: Make group row distinct if needed, e.g. bold font
                # But MTableModel relies on specific roles for styling.
                # If we want custom styling for group row, we'd need to add it to data.
            }
            # Set the grouping key's value too, so it shows in that column if visible
            group_node[key] = k
            groups.append(group_node)
        return groups

    def _apply_grouping(self):
        index = self.group_combo.currentIndex()
        key = self.group_combo.itemData(index)
        
        if not key or key == "None" or not self.raw_data_list:
            self.source_model.clear()
            if self.raw_data_list:
                self.source_model.set_data_list(self.raw_data_list)
        else:
             # Flatten and group
             flat_data = self._flatten(self.raw_data_list)
             grouped_data = self._group_by(flat_data, key)
             self.source_model.clear()
             self.source_model.set_data_list(grouped_data)
             
    @QtCore.Slot(int)
    def _slot_group_changed(self, index):
        self._apply_grouping()
        
        current_text = self.group_combo.currentText()
        if current_text != "None":
            # Switch to Group Mode
            if not self._is_grouped:
                # Save current view index only if we are transitioning from None
                self._pre_group_view_index = self.stack_widget.currentIndex()
                self._is_grouped = True

            # Force switch to Tree View if available
            if hasattr(self, 'tree_view'):
                tree_view_index = self.stack_widget.indexOf(self.tree_view)
                if tree_view_index != -1 and self.stack_widget.currentIndex() != tree_view_index:
                    self.view_button_grp.set_dayu_checked(tree_view_index)
            
            # Expand all for TreeView when grouped
            if hasattr(self, 'tree_view'):
                 self.tree_view.expandAll()
        else:
            # Restore to previous view if we were grouped
            if self._is_grouped:
                self.view_button_grp.set_dayu_checked(self._pre_group_view_index)
                self._is_grouped = False

    def get_data(self):
        return self.source_model.get_data_list()

    def searchable(self):
        """Enable search line edit visible."""
        self.search_line_edit.setVisible(True)
        return self

    def groupable(self):
        """Enable group combo box visible."""
        self.group_label.setVisible(True)
        self.group_combo.setVisible(True)
        return self

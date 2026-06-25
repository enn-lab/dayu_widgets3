# Import built-in modules
import functools

# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.menu import MMenu
import dayu_widgets.utils as utils


class MHeaderView(QtWidgets.QHeaderView):
    def __init__(self, orientation, parent=None, show_sort_indicator=True):
        super(MHeaderView, self).__init__(orientation, parent)
        self.setMovable(True)
        self.setClickable(True)
        self.setSortIndicatorShown(show_sort_indicator)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._slot_context_menu)
        self.setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setProperty(
            "orientation",
            "horizontal" if orientation == QtCore.Qt.Horizontal else "vertical",
        )

    # def enterEvent(self, *args, **kwargs):
    #     # 调整表头宽度的 cursor 就被覆盖了
    #     QApplication.setOverrideCursor(Qt.PointingHandCursor)
    #     return super(MHeaderViewPrivate, self).enterEvent(*args, **kwargs)
    #
    # def leaveEvent(self, *args, **kwargs):
    #     QApplication.restoreOverrideCursor()
    #     return super(MHeaderViewPrivate, self).leaveEvent(*args, **kwargs)

    @QtCore.Slot(QtCore.QPoint)
    def _slot_context_menu(self, point):
        # 优先从父视图获取 model，避免 QHeaderView.model() 在 PySide6 中返回 None
        parent_view = self.parent()
        view_model = None
        if hasattr(parent_view, "model"):
            view_model = parent_view.model()
        if view_model is None:
            view_model = self.model()
        model = utils.real_model(view_model)
        if model is None or not getattr(model, "header_list", None):
            # model 不可用时降级展示：仅显示 Fit Size 和列可见性 (从 header 自身获取列数)
            context_menu = MMenu(parent=self)
            fit_action = context_menu.addAction(self.tr("Fit Size"))
            fit_action.triggered.connect(functools.partial(self._slot_set_resize_mode, True))
            if self.count() > 0:
                context_menu.addSeparator()
                for column in range(self.count()):
                    section_text = self.tr("Column {}").format(column + 1)
                    action = context_menu.addAction(section_text)
                    action.setCheckable(True)
                    action.setChecked(not self.isSectionHidden(column))
                    action.toggled.connect(
                        functools.partial(self._slot_set_section_visible, column)
                    )
            context_menu.exec_(QtGui.QCursor.pos() + QtCore.QPoint(10, 10))
            return

        context_menu = MMenu(parent=self)
        logical_column = self.logicalIndexAt(point)
        if logical_column >= 0 and model.header_list[logical_column].get("checkable", False):
            action_select_all = context_menu.addAction(self.tr("Select All"))
            action_select_none = context_menu.addAction(self.tr("Select None"))
            action_select_invert = context_menu.addAction(self.tr("Select Invert"))
            action_select_all.triggered.connect(
                functools.partial(self._slot_set_select, logical_column, QtCore.Qt.Checked)
            )
            action_select_none.triggered.connect(
                functools.partial(
                    self._slot_set_select, logical_column, QtCore.Qt.Unchecked
                )
            )
            action_select_invert.triggered.connect(
                functools.partial(self._slot_set_select, logical_column, None)
            )
            context_menu.addSeparator()

        fit_action = context_menu.addAction(self.tr("Fit Size"))
        fit_action.triggered.connect(functools.partial(self._slot_set_resize_mode, True))
        context_menu.addSeparator()
        for column in range(self.count()):
            header_text = model.headerData(
                column, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole
            )
            # 防止 headerData 返回 None 传入 addAction 触发 Shiboken 报错
            if header_text is None:
                header_text = self.tr("Column {}").format(column + 1)
            action = context_menu.addAction(header_text)
            action.setCheckable(True)
            action.setChecked(not self.isSectionHidden(column))
            action.toggled.connect(functools.partial(self._slot_set_section_visible, column))
        context_menu.exec_(QtGui.QCursor.pos() + QtCore.QPoint(10, 10))

    @QtCore.Slot(int, int)
    def _slot_set_select(self, column, state):
        """Set the check state of *all* items in the given column.

        - ``QtCore.Qt.Checked``   → Select All   (every node = Checked)
        - ``QtCore.Qt.Unchecked`` → Unselect All (every node = Unchecked)
        - ``None``                → Invert       (toggle leaves, recalc parents)

        For Select All / Unselect All every node (parent + children) is set
        uniformly so the tree is self-consistent.

        For Invert only **leaf** nodes are toggled; parent states are then
        recomputed bottom‑up from their children.  This guarantees that a
        parent never gets an independent value that contradicts its children,
        and that ``PartiallyChecked`` appears whenever siblings disagree.
        """
        current_model = self.model()
        source_model = utils.real_model(current_model)
        header_list = source_model.header_list
        if column < 0 or column >= len(header_list):
            return
        attr = "{}_checked".format(header_list[column].get("key"))

        # ---- helper: normalise None / int → CheckState enum -----------------
        # PySide6 uses a *regular* Enum (not IntEnum) for CheckState, so
        # ``int(1)  !=  Qt.CheckState.PartiallyChecked``.
        # setData() stores a plain int ("1") for partially-checked parents;
        # our own setters use the Enum.  Normalising on read makes comparisons
        # reliable regardless of which code wrote the value.
        def _norm(val):
            if val is None:
                return QtCore.Qt.Unchecked
            try:
                return QtCore.Qt.CheckState(val)
            except (ValueError, TypeError):
                return val   # already a CheckState enum

        # ---- invert: toggle leaves, derive parents bottom‑up ----------------
        if state is None:

            def _invert_tree(data_obj):
                children = utils.get_obj_value(data_obj, "children", [])
                if children:
                    # post‑order: children first, then derive parent
                    for child in children:
                        _invert_tree(child)
                    child_states = [
                        _norm(utils.get_obj_value(c, attr)) for c in children
                    ]
                    if all(s == child_states[0] for s in child_states):
                        utils.set_obj_value(data_obj, attr, child_states[0])
                    else:
                        utils.set_obj_value(
                            data_obj, attr, QtCore.Qt.PartiallyChecked
                        )
                else:
                    # Leaf node: binary toggle (Unchecked ↔ Checked)
                    old = _norm(utils.get_obj_value(data_obj, attr))
                    utils.set_obj_value(
                        data_obj,
                        attr,
                        QtCore.Qt.Unchecked
                        if old == QtCore.Qt.Checked
                        else QtCore.Qt.Checked,
                    )

            for row in range(current_model.rowCount()):
                proxy_index = current_model.index(row, column)
                if not proxy_index.isValid():
                    continue
                real_index = utils.real_index(proxy_index)
                data_obj = real_index.internalPointer()
                if data_obj is None:
                    continue
                _invert_tree(data_obj)

        # ---- select‑all / unselect‑all: set every node uniformly -----------
        else:

            def _set_all(data_obj):
                utils.set_obj_value(data_obj, attr, state)
                for child in utils.get_obj_value(data_obj, "children", []):
                    _set_all(child)

            for row in range(current_model.rowCount()):
                proxy_index = current_model.index(row, column)
                if not proxy_index.isValid():
                    continue
                real_index = utils.real_index(proxy_index)
                data_obj = real_index.internalPointer()
                if data_obj is None:
                    continue
                _set_all(data_obj)

        # Notify views that all data may have changed.
        # Using two *invalid* QModelIndex means "everything changed".
        # We deliberately avoid beginResetModel / endResetModel so the
        # tree's expand/collapse state is preserved.
        source_model.dataChanged.emit(
            QtCore.QModelIndex(), QtCore.QModelIndex()
        )

    @QtCore.Slot(QtCore.QModelIndex, int)
    def _slot_set_section_visible(self, index, flag):
        self.setSectionHidden(index, not flag)

    @QtCore.Slot(bool)
    def _slot_set_resize_mode(self, flag):
        if flag:
            self.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        else:
            self.resizeSections(QtWidgets.QHeaderView.Interactive)

    def setClickable(self, flag):
        try:
            QtWidgets.QHeaderView.setSectionsClickable(self, flag)
        except AttributeError:
            QtWidgets.QHeaderView.setClickable(self, flag)

    def setMovable(self, flag):
        try:
            QtWidgets.QHeaderView.setSectionsMovable(self, flag)
        except AttributeError:
            QtWidgets.QHeaderView.setMovable(self, flag)

    def resizeMode(self, index):
        try:
            QtWidgets.QHeaderView.sectionResizeMode(self, index)
        except AttributeError:
            QtWidgets.QHeaderView.resizeMode(self, index)

    def setResizeMode(self, mode):
        try:
            QtWidgets.QHeaderView.setResizeMode(self, mode)
        except AttributeError:
            QtWidgets.QHeaderView.setSectionResizeMode(self, mode)

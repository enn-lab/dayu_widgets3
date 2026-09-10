"""Modern splitter with animated collapse and restore controls."""

from qtpy import QtCore
from qtpy import QtWidgets

from dayu_widgets import dayu_theme
from dayu_widgets.mixin import property_mixin


class _MSplitterHandle(QtWidgets.QSplitterHandle):
    """Minimal draggable handle with a delayed hover highlight."""

    def __init__(self, orientation, splitter):
        super(_MSplitterHandle, self).__init__(orientation, splitter)
        self.setObjectName("dayuSplitterHandle")
        self.setAttribute(QtCore.Qt.WA_Hover, True)
        self.setCursor(
            QtCore.Qt.SplitHCursor
            if orientation == QtCore.Qt.Horizontal
            else QtCore.Qt.SplitVCursor
        )
        self._hover_timer = QtCore.QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.setInterval(1000)
        self._hover_timer.timeout.connect(self._activate_hover)

    def _activate_hover(self):
        self.setProperty("hover_active", True)
        self.style().polish(self)

    def enterEvent(self, event):
        self._hover_timer.start()
        return super(_MSplitterHandle, self).enterEvent(event)

    def leaveEvent(self, event):
        self._hover_timer.stop()
        self.setProperty("hover_active", False)
        self.style().polish(self)
        return super(_MSplitterHandle, self).leaveEvent(event)


@property_mixin
class MSplitter(QtWidgets.QSplitter):
    """A themed splitter with compact collapse/restore controls.

    ``index`` in :meth:`slot_splitter_click` identifies the handle.  ``first``
    collapses the panel before it and ``False`` collapses the panel after it.
    """

    def __init__(self, Orientation=QtCore.Qt.Horizontal, parent=None):
        super(MSplitter, self).__init__(Orientation, parent=parent)
        self.setHandleWidth(4)
        self.setChildrenCollapsible(True)
        self.setProperty("animatable", True)
        self.setProperty("default_size", 100)
        self.setProperty("anim_move_duration", 220)
        self._collapsed_sizes = {}
        self._size_animation = None
        dayu_theme.apply(self)

    def _handle_index(self, handle):
        for index in range(1, self.count()):
            if self.handle(index) is handle:
                return index
        return -1

    def _animate_sizes(self, start_sizes, end_sizes):
        if self._size_animation is not None:
            self._size_animation.stop()
        if not self.property("animatable"):
            self.setSizes(end_sizes)
            return

        animation = QtCore.QVariantAnimation(self)
        animation.setDuration(self.property("anim_move_duration"))
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)

        def update_sizes(progress):
            sizes = [
                round(start + (end - start) * progress)
                for start, end in zip(start_sizes, end_sizes)
            ]
            self.setSizes(sizes)

        animation.valueChanged.connect(update_sizes)
        animation.finished.connect(lambda: self.setSizes(end_sizes))
        self._size_animation = animation
        animation.start()

    def _change_panel_size(self, panel_index, target_size):
        sizes = self.sizes()
        if not 0 <= panel_index < len(sizes):
            return
        receiver = panel_index - 1 if panel_index else panel_index + 1
        if receiver >= len(sizes):
            return
        target_size = max(0, target_size)
        delta = target_size - sizes[panel_index]
        end_sizes = list(sizes)
        end_sizes[panel_index] = target_size
        end_sizes[receiver] = max(0, sizes[receiver] - delta)
        end_sizes[receiver] += sum(sizes) - sum(end_sizes)
        self._animate_sizes(sizes, end_sizes)

    def slot_splitter_click(self, index, first=True):
        """Collapse or restore the panel adjacent to a splitter handle."""
        if index <= 0 or index >= self.count():
            return
        panel_index = index - 1 if first else index
        sizes = self.sizes()
        if sizes[panel_index] > 0:
            self._collapsed_sizes[panel_index] = sizes[panel_index]
            self._change_panel_size(panel_index, 0)
            return

        total_size = sum(sizes)
        saved_size = self._collapsed_sizes.get(
            panel_index, self.property("default_size")
        )
        self._change_panel_size(panel_index, min(saved_size, max(1, total_size - 1)))
        self._collapsed_sizes.pop(panel_index, None)

    def _reset_sizes(self):
        if self.count():
            self._collapsed_sizes.clear()
            self._animate_sizes(self.sizes(), [1] * self.count())

    def createHandle(self):
        handle = _MSplitterHandle(self.orientation(), self)
        handle.mouseDoubleClickEvent = lambda event: self._reset_sizes()
        return handle

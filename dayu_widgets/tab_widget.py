# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.qt import get_scale_factor
from dayu_widgets.mixin import cursor_mixin
from dayu_widgets.mixin import stacked_animation_mixin


@cursor_mixin
class MTabBar(QtWidgets.QTabBar):
    """QTabBar with configurable dayu_size for tab height control.

    When ``_dayu_size`` is set (via ``.small()`` / ``.medium()`` etc.) the
    tab height is pinned to the given pixel value.  When ``_dayu_size`` is
    ``None`` the original font-based calculation is used for backward
    compatibility.
    """

    def __init__(self, size=None, parent=None):
        super(MTabBar, self).__init__(parent=parent)
        self.setDrawBase(False)
        self._dayu_size = size

    def get_dayu_size(self):
        return self._dayu_size

    def set_dayu_size(self, value):
        self._dayu_size = value
        self.style().polish(self)

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def huge(self):
        self.set_dayu_size(dayu_theme.huge)
        return self

    def large(self):
        self.set_dayu_size(dayu_theme.large)
        return self

    def medium(self):
        self.set_dayu_size(dayu_theme.medium)
        return self

    def small(self):
        self.set_dayu_size(dayu_theme.small)
        return self

    def tiny(self):
        self.set_dayu_size(dayu_theme.tiny)
        return self

    def tabSizeHint(self, index):
        tab_text = self.tabText(index)
        scale_x, _ = get_scale_factor()

        # Width: font-based (same as before), scaled for HiDPI
        width_pad = 70 if self.tabsClosable() else 50
        tab_width = self.fontMetrics().width(tab_text) + int(width_pad * scale_x)

        # Height: use dayu_size when set, otherwise fall back to font-based
        if self._dayu_size is not None:
            tab_height = self._dayu_size
        else:
            tab_height = self.fontMetrics().height() + int(20 * scale_x)

        return QtCore.QSize(tab_width, tab_height)


@stacked_animation_mixin
class MTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(MTabWidget, self).__init__(parent=parent)
        self.bar = MTabBar()
        self.setTabBar(self.bar)

    def disable_animation(self):
        self.currentChanged.disconnect(self._play_anim)

    # ---- chain API: delegate to the internal MTabBar -----------------------
    def huge(self):
        self.bar.huge()
        return self

    def large(self):
        self.bar.large()
        return self

    def medium(self):
        self.bar.medium()
        return self

    def small(self):
        self.bar.small()
        return self

    def tiny(self):
        self.bar.tiny()
        return self

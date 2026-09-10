"""Hover-revealed scroll bars for modern dayu widgets."""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets


class MHoverScrollBar(QtWidgets.QScrollBar):
    """A scroll bar that fades in while its scroll area is being used."""

    def __init__(self, orientation, parent=None, duration=140):
        self._opacity = 0.0
        super(MHoverScrollBar, self).__init__(orientation, parent)
        self._duration = duration
        self._animation = QtCore.QPropertyAnimation(self, b"_dayu_opacity", self)
        self._animation.setDuration(duration)
        self._animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self._effect = QtWidgets.QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)
        self.setMouseTracking(True)
        self.setProperty("dayu_hover_scrollbar", True)

    def get_opacity(self):
        return getattr(self, "_opacity", 0.0)

    def set_opacity(self, value):
        self._opacity = float(value)
        if hasattr(self, "_effect"):
            self._effect.setOpacity(self._opacity)

    _dayu_opacity = QtCore.Property(float, get_opacity, set_opacity)

    def reveal(self):
        if self.maximum() <= 0:
            return
        self._animate_to(1.0)

    def conceal(self):
        self._animate_to(0.0)

    def _animate_to(self, value):
        self._animation.stop()
        self._animation.setStartValue(self._opacity)
        self._animation.setEndValue(value)
        self._animation.start()

    def enterEvent(self, event):
        self.reveal()
        super(MHoverScrollBar, self).enterEvent(event)

    def leaveEvent(self, event):
        self.conceal()
        super(MHoverScrollBar, self).leaveEvent(event)


class _HoverScrollAreaFilter(QtCore.QObject):
    def __init__(self, scroll_area, parent=None):
        super(_HoverScrollAreaFilter, self).__init__(parent)
        self._scroll_area = scroll_area

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.Enter:
            self._scroll_area.reveal_scrollbars()
        elif event.type() == QtCore.QEvent.Leave:
            self._scroll_area.conceal_scrollbars()
        return super(_HoverScrollAreaFilter, self).eventFilter(watched, event)


def install_hover_scrollbars(scroll_area, duration=140):
    """Install animated scroll bars on a ``QAbstractScrollArea``.

    The helper is idempotent and returns ``scroll_area`` for fluent setup.
    The scroll bars remain functional when faded out and retain their normal
    geometry, so enabling the effect does not cause content to jump.
    """
    if not isinstance(scroll_area, QtWidgets.QAbstractScrollArea):
        raise TypeError("scroll_area must be a QAbstractScrollArea")
    if getattr(scroll_area, "_dayu_hover_scrollbars", None):
        return scroll_area

    vertical = MHoverScrollBar(QtCore.Qt.Vertical, scroll_area, duration)
    horizontal = MHoverScrollBar(QtCore.Qt.Horizontal, scroll_area, duration)
    scroll_area.setVerticalScrollBar(vertical)
    scroll_area.setHorizontalScrollBar(horizontal)
    scroll_area._dayu_hover_scrollbars = (vertical, horizontal)
    scroll_area._dayu_hover_filter = _HoverScrollAreaFilter(scroll_area, scroll_area.viewport())
    scroll_area.viewport().installEventFilter(scroll_area._dayu_hover_filter)

    def reveal_scrollbars():
        for bar in scroll_area._dayu_hover_scrollbars:
            bar.reveal()

    def conceal_scrollbars():
        for bar in scroll_area._dayu_hover_scrollbars:
            bar.conceal()

    scroll_area.reveal_scrollbars = reveal_scrollbars
    scroll_area.conceal_scrollbars = conceal_scrollbars
    return scroll_area

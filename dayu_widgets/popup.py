# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.mixin import hover_shadow_mixin
from dayu_widgets.mixin import property_mixin


@hover_shadow_mixin
@property_mixin
class MPopup(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(MPopup, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Popup)
        self.mouse_pos = None
        # The deferred initialisation and mask updates must be scheduled on
        # timers the popup *owns*.  The module-level ``QTimer.singleShot``
        # helper keeps the callback alive after the widget is gone, so
        # destroying a popup (or a menu/page that parents one) before the
        # event loop drained the timer ran ``post_init`` / ``update_mask``
        # against a deleted C++ object: PySide6 6.11.1 reported
        # ``Internal C++ object (MPopup) already deleted`` and killed the
        # whole process with an access violation.
        # A timer parented to ``self`` is destroyed together with the widget,
        # which cancels any pending callback — the pattern ``menu.py`` already
        # uses for ``scrollTimer`` / ``delayTimer``.
        self._init_timer = QtCore.QTimer(self)
        self._init_timer.setSingleShot(True)
        self._init_timer.timeout.connect(self.post_init)

        self._mask_timer = QtCore.QTimer(self)
        self._mask_timer.setSingleShot(True)
        self._mask_timer.timeout.connect(self.update_mask)

        self.setProperty("movable", True)
        self.setProperty("animatable", True)
        self._init_timer.start(0)

        self._opacity_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.setProperty("anim_opacity_duration", 300)
        self.setProperty("anim_opacity_curve", "OutCubic")
        self.setProperty("anim_opacity_start", 0)
        self.setProperty("anim_opacity_end", 1)

        self._size_anim = QtCore.QPropertyAnimation(self, b"size")
        self.setProperty("anim_size_duration", 300)
        self.setProperty("anim_size_curve", "OutCubic")
        self.setProperty("border_radius", 15)

    def post_init(self):
        start_size = self.property("anim_size_start")
        size = self.sizeHint()
        start_size = start_size if start_size else QtCore.QSize(0, size.height())
        end_size = self.property("anim_size_end")
        end_size = end_size if end_size else size
        self.setProperty("anim_size_start", start_size)
        self.setProperty("anim_size_end", end_size)

    def update_mask(self):
        rectPath = QtGui.QPainterPath()
        end_size = self.property("anim_size_end")
        rect = QtCore.QRectF(0, 0, end_size.width(), end_size.height())
        radius = self.property("border_radius")
        rectPath.addRoundedRect(rect, radius, radius)
        self.setMask(QtGui.QRegion(rectPath.toFillPolygon().toPolygon()))

    def _get_curve(self, value):
        curve = getattr(QtCore.QEasingCurve, value, None)
        if not curve:
            raise TypeError("Invalid QEasingCurve")
        return curve

    def _set_border_radius(self, value):
        self._mask_timer.start(0)

    def _set_anim_opacity_duration(self, value):
        self._opacity_anim.setDuration(value)

    def _set_anim_opacity_curve(self, value):
        self._opacity_anim.setEasingCurve(self._get_curve(value))

    def _set_anim_opacity_start(self, value):
        self._opacity_anim.setStartValue(value)

    def _set_anim_opacity_end(self, value):
        self._opacity_anim.setEndValue(value)

    def _set_anim_size_duration(self, value):
        self._size_anim.setDuration(value)

    def _set_anim_size_curve(self, value):
        self._size_anim.setEasingCurve(self._get_curve(value))

    def _set_anim_size_start(self, value):
        self._size_anim.setStartValue(value)

    def _set_anim_size_end(self, value):
        self._size_anim.setEndValue(value)
        self._mask_timer.start(0)

    def start_anim(self):
        self._size_anim.start()
        self._opacity_anim.start()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pos = event.pos()
        return super(MPopup, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouse_pos = None
        return super(MPopup, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.mouse_pos and self.property("movable"):
            self.move(self.mapToGlobal(event.pos() - self.mouse_pos))
        return super(MPopup, self).mouseMoveEvent(event)

    def show(self):
        if self.property("animatable"):
            self.start_anim()
        self.move(QtGui.QCursor.pos())
        super(MPopup, self).show()
        # NOTES(timmyliang): for chinese input
        self.activateWindow()

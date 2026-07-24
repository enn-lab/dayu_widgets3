"""
MSidebarItem
"""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.mixin import cursor_mixin
from dayu_widgets.qt import MIcon


@cursor_mixin
class MSidebarItem(QtWidgets.QWidget):
    """A single navigation item for sidebar.

    Renders icon, label and badge with hover/selected highlight.
    The paint logic is ported from the original sidebar delegate so the
    visual style stays consistent with the rest of the library.

    Properties:
        dayu_icon: str, svg file name looked up via :func:`MIcon`
        dayu_text: str, item label
        dayu_badge: str, badge text (number or short text), empty to hide
        dayu_selected: bool, whether this item is the active one
        dayu_compact: bool, compact mode only shows the icon
    """

    sig_clicked = QtCore.Signal(object)

    def __init__(self, text="", icon=None, badge="", parent=None):
        super(MSidebarItem, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMouseTracking(True)

        self._dayu_icon = icon or ""
        self._dayu_text = text
        self._dayu_badge = badge
        self._dayu_selected = False
        self._dayu_compact = False
        self._hovered = False

        self._item_height = 36
        self._padding_h = 12
        self._icon_size = 18
        self._spacing = 8
        self._indent = 0
        self._badge_h_padding = 6
        self._badge_radius = 8
        self._badge_font_size = 10
        self._label_font_size = 13
        self._bg_radius = 6

        self.setFixedHeight(self._item_height)
        self.setMinimumWidth(0)

    # ------------------------------------------------------------------
    # Properties (dayu_* style)
    # ------------------------------------------------------------------
    def get_dayu_icon(self):
        return self._dayu_icon

    def set_dayu_icon(self, value):
        self._dayu_icon = value or ""
        self.update()

    def get_dayu_text(self):
        return self._dayu_text

    def set_dayu_text(self, value):
        self._dayu_text = value or ""
        self.setToolTip(self._dayu_text if self._dayu_compact else "")
        self.update()

    def get_dayu_badge(self):
        return self._dayu_badge

    def set_dayu_badge(self, value):
        self._dayu_badge = "" if value is None else str(value)
        self.update()

    def get_dayu_selected(self):
        return self._dayu_selected

    def set_dayu_selected(self, value):
        self._dayu_selected = bool(value)
        self.update()

    def get_dayu_compact(self):
        return self._dayu_compact

    def set_dayu_compact(self, value):
        self._dayu_compact = bool(value)
        self.setToolTip(self._dayu_text if self._dayu_compact else "")
        self.update()

    dayu_icon = QtCore.Property(str, get_dayu_icon, set_dayu_icon)
    dayu_text = QtCore.Property(str, get_dayu_text, set_dayu_text)
    dayu_badge = QtCore.Property(str, get_dayu_badge, set_dayu_badge)
    dayu_selected = QtCore.Property(bool, get_dayu_selected, set_dayu_selected)
    dayu_compact = QtCore.Property(bool, get_dayu_compact, set_dayu_compact)

    # ------------------------------------------------------------------
    # Fluent setters (consistent with MToolButton / MPushButton style)
    # ------------------------------------------------------------------
    def set_icon(self, path):
        self.set_dayu_icon(path)
        return self

    def set_text(self, text):
        self.set_dayu_text(text)
        return self

    def set_badge(self, value):
        self.set_dayu_badge(value)
        return self

    def set_indent(self, indent):
        """Left indent in pixels (used for sub-items inside a menu group)."""
        self._indent = max(0, int(indent))
        self.update()
        return self

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super(MSidebarItem, self).enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super(MSidebarItem, self).leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.sig_clicked.emit(self)
        super(MSidebarItem, self).mousePressEvent(event)

    def sizeHint(self):
        return QtCore.QSize(max(160, self.width()), self._item_height)

    # ------------------------------------------------------------------
    # Paint (ported from the original sidebar delegate)
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        # Import dynamically so theme switches are picked up at runtime
        from dayu_widgets import dayu_theme

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = QtCore.QRectF(self.rect())
        is_hover = self._hovered
        is_selected = self._dayu_selected

        # -- Background --
        if is_selected or is_hover:
            bg_color = QtGui.QColor(dayu_theme.background_selected_color)
            text_color = QtGui.QColor(dayu_theme.title_color)
            icon_color = QtGui.QColor(dayu_theme.primary_color)
        else:
            bg_color = None
            text_color = QtGui.QColor(dayu_theme.secondary_text_color)
            icon_color = QtGui.QColor(dayu_theme.icon_color)

        if bg_color is not None:
            bg_rect = rect.adjusted(4, 2, -4, -2)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(bg_rect, self._bg_radius, self._bg_radius)

        # Compact mode: only draw the icon centered.
        if self._dayu_compact:
            self._draw_icon(painter, rect, icon_color)
            painter.end()
            return

        # -- Icon --
        text_x = rect.x() + self._padding_h + self._indent
        if self._dayu_icon:
            icon = MIcon(self._dayu_icon, icon_color.name())
            icon_y = rect.center().y() - self._icon_size / 2.0
            if not icon.isNull():
                painter.drawPixmap(
                    QtCore.QPointF(text_x, icon_y),
                    icon.pixmap(self._icon_size, self._icon_size),
                )
            text_x += self._icon_size + self._spacing

        # -- Badge --
        badge_text = self._dayu_badge or ""
        badge_width = 0.0
        if badge_text:
            badge_font = QtGui.QFont()
            badge_font.setPixelSize(self._badge_font_size)
            painter.setFont(badge_font)
            fm = QtGui.QFontMetrics(badge_font)
            text_w = fm.horizontalAdvance(badge_text)
            badge_width = max(text_w + self._badge_h_padding * 2, self._badge_radius * 2)
            badge_rect = QtCore.QRectF(
                rect.right() - self._padding_h - badge_width,
                rect.center().y() - self._badge_radius,
                badge_width,
                self._badge_radius * 2,
            )
            badge_bg = QtGui.QColor(dayu_theme.primary_color)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(badge_bg)
            painter.drawRoundedRect(badge_rect, self._badge_radius, self._badge_radius)

            painter.setPen(QtGui.QColor("#ffffff"))
            painter.drawText(badge_rect, QtCore.Qt.AlignCenter, badge_text)

        # -- Label --
        label_text = self._dayu_text or ""
        if label_text:
            label_font = QtGui.QFont()
            label_font.setPixelSize(self._label_font_size)
            painter.setFont(label_font)
            painter.setPen(text_color)

            available_right = rect.right() - self._padding_h
            if badge_width:
                available_right -= badge_width + self._spacing
            text_rect = QtCore.QRectF(
                text_x, rect.y(),
                available_right - text_x, rect.height(),
            )
            painter.drawText(
                text_rect,
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                label_text,
            )

        painter.end()

    def _draw_icon(self, painter, rect, icon_color):
        """Draw the icon centered (used in compact mode)."""
        if not self._dayu_icon:
            return
        icon = MIcon(self._dayu_icon, icon_color.name())
        if icon.isNull():
            return
        icon_x = rect.center().x() - self._icon_size / 2.0
        icon_y = rect.center().y() - self._icon_size / 2.0
        painter.drawPixmap(
            QtCore.QPointF(icon_x, icon_y),
            icon.pixmap(self._icon_size, self._icon_size),
        )

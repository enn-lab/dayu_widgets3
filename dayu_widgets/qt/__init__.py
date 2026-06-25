# Import built-in modules
import contextlib
import signal
import sys

# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtSvg import QSvgRenderer


class MCacheDict(object):
    _render = QSvgRenderer()

    def __init__(self, cls):
        super(MCacheDict, self).__init__()
        self.cls = cls
        self._cache_pix_dict = {}

    def _render_svg(self, svg_path, replace_color=None):
        # Import local modules
        from dayu_widgets import dayu_theme

        replace_color = replace_color or dayu_theme.icon_color
        if (self.cls is QtGui.QIcon) and (replace_color is None):
            return QtGui.QIcon(svg_path)
        with open(svg_path, "r") as f:
            data_content = f.read()
            if replace_color is not None:
                data_content = data_content.replace("#555555", replace_color)
            self._render.load(QtCore.QByteArray(data_content.encode()))
            pix = QtGui.QPixmap(128, 128)
            pix.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pix)
            self._render.render(painter)
            painter.end()
            if self.cls is QtGui.QPixmap:
                return pix
            else:
                return self.cls(pix)

    def __call__(self, path, color=None):
        # Import local modules
        from dayu_widgets import utils

        full_path = utils.get_static_file(path)
        if full_path is None:
            return self.cls()
        key = "{}{}".format(full_path.lower(), color or "")
        pix_map = self._cache_pix_dict.get(key, None)
        if pix_map is None:
            if full_path.endswith("svg"):
                pix_map = self._render_svg(full_path, color)
            else:
                pix_map = self.cls(full_path)
            self._cache_pix_dict.update({key: pix_map})
        return pix_map


def get_scale_factor():
    if not QtWidgets.QApplication.instance():
        QtWidgets.QApplication([])
    standard_dpi = 96.0

    # For PySide6
    if hasattr(QtWidgets.QApplication, 'primaryScreen'):
        screen = QtWidgets.QApplication.primaryScreen()
        scale_factor_x = screen.logicalDotsPerInchX() / standard_dpi
        scale_factor_y = screen.logicalDotsPerInchY() / standard_dpi
        return scale_factor_x, scale_factor_y
    # For PySide2
    elif hasattr(QtWidgets.QApplication, 'desktop'):
        scale_factor_x = QtWidgets.QApplication.desktop().logicalDpiX() / standard_dpi
        scale_factor_y = QtWidgets.QApplication.desktop().logicalDpiY() / standard_dpi
        return scale_factor_x, scale_factor_y
    else:
        return 1, 1


@contextlib.contextmanager
def application(*args):
    app = QtWidgets.QApplication.instance()

    if not app:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        app = QtWidgets.QApplication(sys.argv)
        yield app
        app.exec_()
    else:
        yield app


MPixmap = MCacheDict(QtGui.QPixmap)
MIcon = MCacheDict(QtGui.QIcon)


class MDayuBranchStyle(QtWidgets.QProxyStyle):
    """Custom QProxyStyle that draws QTreeView branch indicators using
    ``right_line.svg`` / ``down_line.svg`` with proper theme colors.

    Standard Qt / Ant-Design tree convention:
        collapsed → ▶ right_line   (click to expand)
        expanded  → ▼ down_line    (click to collapse)

    Icon size is derived from the row height (``rect.height()``) so it
    stays proportional when ``dayu_size`` changes (tiny/small/medium/large).

    In PySide6, the default system branch icons do not respect the application
    stylesheet and render with OS-native colors.  This style intercepts
    ``PE_IndicatorBranch`` to draw custom SVG-based arrows instead.
    """

    # Minimum icon size in pixels (avoids unclickable tiny indicators)
    MIN_BRANCH_ICON_SIZE = 12

    def drawPrimitive(self, element, option, painter, widget=None):
        if element != QtWidgets.QStyle.PE_IndicatorBranch:
            super().drawPrimitive(element, option, painter, widget)
            return

        # Only customise branch indicators for items that actually have children
        if not (option.state & QtWidgets.QStyle.State_Children):
            super().drawPrimitive(element, option, painter, widget)
            return

        # Import local modules
        from dayu_widgets import dayu_theme

        # Collapsed → right arrow (click to expand); Expanded → down arrow (click to collapse)
        icon_name = "down_line.svg" if (option.state & QtWidgets.QStyle.State_Open) else "right_line.svg"

        # Hover uses primary_color; normal uses icon_color
        color = (
            dayu_theme.primary_color
            if (option.state & QtWidgets.QStyle.State_MouseOver)
            else dayu_theme.icon_color
        )

        icon = MIcon(icon_name, color=color)
        if icon.isNull():
            # Fallback to system drawing if the icon cannot be loaded
            super().drawPrimitive(element, option, painter, widget)
            return

        rect = option.rect
        # Icon size follows row height (matching theme convention: icon ≈ height - 10).
        # Cap at indentation width minus padding so the icon never overflows.
        row_height = rect.height()
        indent_width = rect.width()
        ideal = max(int(row_height * 0.55), self.MIN_BRANCH_ICON_SIZE)
        size = min(ideal, indent_width - 4)
        pm = icon.pixmap(size, size)
        x = rect.center().x() - pm.width() // 2 + rect.center().x() % 2
        y = rect.center().y() - pm.height() // 2 + rect.center().y() % 2
        painter.drawPixmap(x, y, pm)

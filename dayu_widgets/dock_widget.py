"""MDockWidget"""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

from dayu_widgets.tool_button import MToolButton


class _MDockTitleBar(QtWidgets.QWidget):
    """Modern, deterministic title bar for :class:`MDockWidget`."""

    def __init__(self, dock_widget):
        super(_MDockTitleBar, self).__init__(dock_widget)
        self._dock_widget = dock_widget
        self.setObjectName("dayuDockTitleBar")

        self.title_label = QtWidgets.QLabel(dock_widget.windowTitle(), self)
        self.title_label.setObjectName("dayuDockTitle")
        self.title_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.float_button = MToolButton(self).icon_only().small().svg("float.svg")
        self.float_button.setObjectName("dayuDockFloatButton")
        self.float_button.setToolTip(self.tr("Float").capitalize())
        self.float_button.clicked.connect(self._toggle_floating)

        self.close_button = MToolButton(self).icon_only().small().svg("close_line.svg")
        self.close_button.setObjectName("dayuDockCloseButton")
        self.close_button.setToolTip(self.tr("Close"))
        self.close_button.clicked.connect(dock_widget.close)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 4, 2)
        layout.setSpacing(2)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.float_button)
        layout.addWidget(self.close_button)
        self.setLayout(layout)
        dock_widget.windowTitleChanged.connect(self.title_label.setText)
        dock_widget.featuresChanged.connect(self._update_buttons)
        dock_widget.topLevelChanged.connect(self._update_float_icon)
        self._update_buttons(dock_widget.features())

    def _toggle_floating(self):
        self._dock_widget.setFloating(not self._dock_widget.isFloating())

    def _update_float_icon(self, floating):
        self.float_button.svg("float.svg")

    def _update_buttons(self, features):
        self.close_button.setVisible(bool(features & QtWidgets.QDockWidget.DockWidgetClosable))
        self.float_button.setVisible(bool(features & QtWidgets.QDockWidget.DockWidgetFloatable))


class MDockWidget(QtWidgets.QDockWidget):
    """
    Just apply the qss. No more extend.
    """

    def __init__(self, title="", parent=None, flags=QtCore.Qt.Widget):
        super(MDockWidget, self).__init__(title, parent=parent, flags=flags)
        self.setTitleBarWidget(_MDockTitleBar(self))

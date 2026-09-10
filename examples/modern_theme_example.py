"""Modern theme component showcase.

Run with a Qt binding installed, for example:
    python examples/modern_theme_example.py
"""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.card import MCard
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.push_button import MPushButton
from dayu_widgets.radio_button import MRadioButton
from dayu_widgets.switch import MSwitch
from dayu_widgets.theme import MTheme


class ModernThemeExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ModernThemeExample, self).__init__(parent)
        self.setWindowTitle("Modern Theme Showcase")
        self.resize(760, 560)
        self._build_ui()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        root.addWidget(MLabel("Modern Theme").h2())
        root.addWidget(MLabel("Semantic colors and interaction states").secondary())

        card = MCard()
        layout = QtWidgets.QGridLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(12)

        layout.addWidget(MLabel("Buttons").h4(), 0, 0)
        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(MPushButton("Default"))
        buttons.addWidget(MPushButton("Primary").primary())
        buttons.addWidget(MPushButton("Success").success())
        buttons.addWidget(MPushButton("Warning").warning())
        buttons.addWidget(MPushButton("Danger").danger())
        layout.addLayout(buttons, 0, 1)

        layout.addWidget(MLabel("Inputs").h4(), 1, 0)
        inputs = QtWidgets.QHBoxLayout()
        inputs.addWidget(MLineEdit(placeholder="Search or type..."))
        combo = MComboBox()
        combo.addItems(["Surface", "Elevated", "Inset"])
        inputs.addWidget(combo)
        layout.addLayout(inputs, 1, 1)

        layout.addWidget(MLabel("Selection").h4(), 2, 0)
        selection = QtWidgets.QHBoxLayout()
        selection.addWidget(MCheckBox("Remember choice"))
        selection.addWidget(MRadioButton("Option A"))
        selection.addWidget(MSwitch().small())
        layout.addLayout(selection, 2, 1)

        layout.addWidget(MLabel("Disabled").h4(), 3, 0)
        disabled = MPushButton("Disabled")
        disabled.setEnabled(False)
        layout.addWidget(disabled, 3, 1, alignment=QtCore.Qt.AlignLeft)

        root.addWidget(card)
        root.addStretch()


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        demo = ModernThemeExample()
        MTheme("modern_dark").apply(demo)
        demo.show()

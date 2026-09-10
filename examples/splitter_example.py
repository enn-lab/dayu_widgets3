"""
Example code for MSplitter
"""
# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.label import MLabel
from dayu_widgets.splitter import MSplitter
from dayu_widgets.text_edit import MTextEdit


class SplitterExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SplitterExample, self).__init__(parent)

        main_splitter = MSplitter(QtCore.Qt.Vertical)

        workspace = MSplitter()
        workspace.addWidget(self._editor("Explorer", "Assets\n  scenes\n  materials\n  characters"))
        workspace.addWidget(self._editor("Editor", "Drag a handle to resize panels.\nHold the pointer for one second to highlight it.\nDouble-click a handle to reset the layout."))
        workspace.addWidget(self._editor("Preview", "Preview output\n\nThe splitter keeps each panel responsive."))
        workspace.setStretchFactor(0, 1)
        workspace.setStretchFactor(1, 3)
        workspace.setStretchFactor(2, 2)
        main_splitter.addWidget(workspace)

        output = MSplitter(QtCore.Qt.Horizontal)
        output.addWidget(self._editor("Console", "Build started\nNo errors"))
        output.addWidget(self._editor("Properties", "Selection\nNone"))
        main_splitter.addWidget(output)
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([560, 200])

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(main_splitter)
        self.setLayout(layout)

        self.resize(800, 800)

    @staticmethod
    def _editor(title, content):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.addWidget(MLabel(title).secondary())
        editor = MTextEdit()
        editor.setPlainText(content)
        editor.setReadOnly(True)
        layout.addWidget(editor)
        return container


if __name__ == "__main__":
    # Import local modules
    from dayu_widgets.qt import application

    with application() as app:
        test = SplitterExample()
        dayu_theme.apply(test)
        test.show()

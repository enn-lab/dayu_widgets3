"""Example for modern tag components."""

# Import third-party modules
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import MCheckableTag, MNewTag, MTag, dayu_theme
from dayu_widgets.divider import MDivider


class TagExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TagExample, self).__init__(parent)
        self.setWindowTitle("Example for MTag")
        self.resize(620, 260)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(MDivider("Semantic tags"))
        tags = QtWidgets.QHBoxLayout()
        tags.addWidget(MTag("Default"))
        tags.addWidget(MTag("Primary").coloring(dayu_theme.accent_color))
        tags.addWidget(MTag("Filled").coloring(dayu_theme.accent_color).no_border())
        tags.addWidget(MTag("Closable").closeable())
        tags.addWidget(MTag("Clickable").clickable())
        tags.addStretch()
        layout.addLayout(tags)

        layout.addWidget(MDivider("Checkable tags"))
        checkable = QtWidgets.QHBoxLayout()
        for text in ("Maya", "Houdini", "Nuke", "Blender"):
            tag = MCheckableTag(text)
            tag.setChecked(text == "Maya")
            checkable.addWidget(tag)
        checkable.addStretch()
        layout.addLayout(checkable)

        layout.addWidget(MDivider("Add tag"))
        new_tag = MNewTag("Add category")
        new_tag.sig_add_tag.connect(lambda text: tags.insertWidget(tags.count() - 1, MTag(text).closeable()))
        layout.addWidget(new_tag, 0)
        layout.addStretch()


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        test = TagExample()
        dayu_theme.apply(test)
        test.show()

"""Tag selector driven by MMenu's searchable multi-select list."""

from qtpy import QtWidgets

from dayu_widgets import dayu_theme
from dayu_widgets.divider import MDivider
from dayu_widgets.label import MLabel
from dayu_widgets.tag_line_edit import MTagLineEdit


class TagSoftwareListExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TagSoftwareListExample, self).__init__(parent)
        self._software = [
            "Maya 2026", "Maya 2025", "Maya 2024", "Houdini 20.5",
            "Houdini 20.0", "Blender 4.3", "Blender 4.2", "Nuke 16",
            "Nuke 15", "Substance Painter", "Unreal Engine 5.6",
            "Unreal Engine 5.5",
        ]
        self.tag_selector = MTagLineEdit().set_options(self._software)
        self.tag_selector.line_edit.setPlaceholderText("点击选择软件，可在菜单中搜索")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(MDivider("软件多选 Tag"))
        layout.addWidget(MLabel("激活输入框打开全部选项；菜单搜索支持连续输入"))
        layout.addWidget(self.tag_selector)
        layout.addWidget(MLabel("支持多选、取消选择、删除 Tag，最多显示三行"))


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        test = TagSoftwareListExample()
        dayu_theme.apply(test)
        test.show()

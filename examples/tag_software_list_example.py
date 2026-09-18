"""Tag selector driven by MMenu's searchable multi-select list."""

from qtpy import QtCore
from qtpy import QtWidgets

from dayu_widgets import dayu_theme
from dayu_widgets.divider import MDivider
from dayu_widgets.label import MLabel
from dayu_widgets.tag_line_edit import MTagLineEdit


SOFTWARE = [
    "Maya 2026", "Maya 2025", "Maya 2024", "Houdini 20.5",
    "Houdini 20.0", "Blender 4.3", "Blender 4.2", "Nuke 16",
    "Nuke 15", "Substance Painter", "Unreal Engine 5.6",
    "Unreal Engine 5.5",
]


class TagSoftwareListExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TagSoftwareListExample, self).__init__(parent)
        self.setWindowTitle("Tag software list")

        self.tag_selector = MTagLineEdit().set_options(SOFTWARE)
        self.tag_selector.line_edit.setPlaceholderText("点击选择软件，或直接输入后回车")
        self.tag_selector.set_value(["Maya 2026", "Houdini 20.5"])
        self.tag_selector.sig_value_changed.connect(self._slot_value_changed)

        self._result = MLabel()
        self._result.setProperty("dayu_mark", "true")
        self._slot_value_changed(self.tag_selector.selected_values())

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(MDivider("软件多选 Tag"))
        layout.addWidget(MLabel(
            "点击组件打开选项菜单；菜单保持展开，可连续勾选/取消多个条目，Esc 或点击别处才关闭"
        ).secondary())
        layout.addWidget(self.tag_selector)
        layout.addWidget(MLabel(
            "输入文字可过滤选项，回车添加自定义项；点击 tag 上的关闭按钮移除，退格删除末项"
        ).secondary())
        layout.addWidget(self._result)
        layout.addStretch()

    @QtCore.Slot(list)
    def _slot_value_changed(self, values):
        self._result.setText("已选 {} 项：{}".format(len(values), "、".join(values) or "无"))


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        test = TagSoftwareListExample()
        dayu_theme.apply(test)
        test.show()

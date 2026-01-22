
# Import third-party modules
from qtpy import QtWidgets, QtCore, QtGui

# Import local modules
from dayu_widgets.divider import MDivider
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.label import MLabel
from dayu_widgets.menu import MMenu
from dayu_widgets.tool_button import MToolButton
from dayu_widgets import dayu_theme


class ToolMenuExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(ToolMenuExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        # 1. Multi-select Menu with MToolButton
        self.register_field("multi_selected", ["Apple"])
        self.register_field("multi_selected_text", lambda: ", ".join(self.field("multi_selected")))

        # 创建工具按钮，设置图标和文字位置
        tool_button = MToolButton().svg("group_by_dark.svg").text_beside_icon()
        tool_button.setText("group_by_dark")
        
        # 计算并设置按钮的最小宽度，以确保文字显示完整
        fm = tool_button.fontMetrics()
        tool_button_text = tool_button.text()
        text_width = fm.horizontalAdvance(tool_button_text) if hasattr(fm, "horizontalAdvance") \
            else fm.width(tool_button_text)
        min_width = 24 + 4 + text_width + 15
        print(min_width)
        tool_button.setMinimumWidth(min_width)

        # 创建多选菜单 (exclusive=False)
        menu = MMenu(exclusive=False, parent=self)
        menu.setStyleSheet("""
            MCheckBox::indicator {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 现在可以直接使用 set_data 设置带有 icon 的数据
        # MMenu 内部会自动处理 Checkbox + Icon 的布局
        menu.set_data([
            {"label": "Apple", "value": "Apple", "icon": "check.svg"},
            {"label": "Banana", "value": "Banana", "icon": "cloud_line.svg"},
            {"label": "Orange", "value": "Orange", "icon": "calendar_line.svg"},
            {"label": "Pear", "value": "Pear", "icon": "folder_line.svg"},
            {"label": "man", "value": "man", "icon": "user_fill.svg"},
        ])
        
        # 将菜单设置给工具按钮
        tool_button.setMenu(menu)
        # 设置弹出模式为 InstantPopup，这样点击按钮会直接弹出菜单
        tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        label = MLabel()

        
        # Bindings
        self.bind("multi_selected", menu, "value", signal="sig_value_changed")
        self.bind("multi_selected_text", label, "text")

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Multi Select Tool Menu"))
        
        h_lay = QtWidgets.QHBoxLayout()
        h_lay.addWidget(tool_button)
        h_lay.addWidget(label)
        h_lay.addStretch()
        
        main_lay.addLayout(h_lay)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from dayu_widgets.qt import application

    with application() as app:
        test = ToolMenuExample()
        dayu_theme.apply(test)
        test.show()

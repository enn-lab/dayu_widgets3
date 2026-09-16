# Import built-in modules
import functools

# Import third-party modules
from qtpy import QtCore
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.divider import MDivider
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.completer import MCompleter
from dayu_widgets.menu import MMenu
from dayu_widgets.message import MMessage
from dayu_widgets.push_button import MPushButton
from dayu_widgets.tool_button import MToolButton
from dayu_widgets.tag import MTag


class TagLineEditExample(QtWidgets.QWidget):
    """Compose MLineEdit, MCompleter and MTag into a tokenized file field."""

    def __init__(self, parent=None):
        super(TagLineEditExample, self).__init__(parent)
        self._tags = []
        self._tag_container = QtWidgets.QWidget(self)
        self._tag_container.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        tag_layout = QtWidgets.QHBoxLayout(self._tag_container)
        tag_layout.setContentsMargins(4, 0, 4, 0)
        tag_layout.setSpacing(4)
        self._tag_layout = tag_layout
        self._tag_layout.addStretch()

        self.line_edit = MLineEdit().small()
        self.line_edit.setPlaceholderText("输入文件名以显示补全选项")
        self.line_edit.set_prefix_widget(self._tag_container)
        self._files = [
            "character_rig.ma",
            "environment_layout.ma",
            "hero_texture.1001.exr",
            "lighting_scene.nk",
            "shot010_animation.blend",
        ]
        self._completer = MCompleter(self.line_edit)
        self._completer.setModel(QtCore.QStringListModel(self._files, self._completer))
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self._completer.activated.connect(self._add_tag)
        self.line_edit.setCompleter(self._completer)
        self.line_edit.textChanged.connect(self._resize_tag_container)
        self._resize_tag_container()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)

    def _add_tag(self, text):
        text = str(text).strip()
        if not text or any(tag.get_dayu_text() == text for tag in self._tags):
            self.line_edit.clear()
            return
        tag = MTag(text).closeable()
        tag.sig_closed.connect(lambda current=tag: self._remove_tag(current))
        self._tags.append(tag)
        self._tag_layout.insertWidget(self._tag_layout.count() - 1, tag)
        self.line_edit.clear()
        self._resize_tag_container()

    def _remove_tag(self, tag):
        if tag in self._tags:
            self._tags.remove(tag)
        self._tag_layout.removeWidget(tag)
        tag.deleteLater()
        self._resize_tag_container()

    def _resize_tag_container(self, *_args):
        tag_width = sum(tag.sizeHint().width() for tag in self._tags)
        spacing = self._tag_layout.spacing() * max(0, len(self._tags) - 1)
        margins = self._tag_layout.contentsMargins()
        width = max(8, tag_width + spacing + margins.left() + margins.right())
        self._tag_container.setFixedWidth(width)
        margins = self.line_edit.textMargins()
        margins.setLeft(width + 2)
        self.line_edit.setTextMargins(margins)


class LineEditExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LineEditExample, self).__init__(parent)
        self.setWindowTitle("Examples for MLineEdit")
        self._init_ui()

    def _init_ui(self):
        size_lay = QtWidgets.QHBoxLayout()
        line_edit_l = MLineEdit().large()
        line_edit_l.setPlaceholderText("large size")
        line_edit_m = MLineEdit().medium()
        line_edit_m.setPlaceholderText("default size")
        line_edit_s = MLineEdit().small()
        line_edit_s.setPlaceholderText("small size")
        size_lay.addWidget(line_edit_l)
        size_lay.addWidget(line_edit_m)
        size_lay.addWidget(line_edit_s)

        line_edit_tool_button = MLineEdit(text="MToolButton")
        line_edit_tool_button.set_prefix_widget(MToolButton().svg("user_line.svg").icon_only())

        line_edit_label = MLineEdit(text="MLabel")
        tool_button = MLabel(text="User").mark().secondary()
        tool_button.setAlignment(QtCore.Qt.AlignCenter)
        tool_button.setFixedWidth(80)
        line_edit_label.set_prefix_widget(tool_button)

        line_edit_push_button = MLineEdit(text="MPushButton")
        push_button = MPushButton(text="Go").primary()
        push_button.setFixedWidth(40)
        line_edit_push_button.set_suffix_widget(push_button)

        search_engine_line_edit = MLineEdit().search_engine().large()
        search_engine_line_edit.returnPressed.connect(self.slot_search)

        line_edit_options = MLineEdit()
        combobox = MComboBox()
        option_menu = MMenu()
        option_menu.set_separator("|")
        option_menu.set_data([r"http://", r"https://"])
        combobox.set_menu(option_menu)
        combobox.set_value("http://")
        combobox.setFixedWidth(100)
        line_edit_options.set_prefix_widget(combobox)

        delay_line_editor = MLineEdit()
        delay_display_label = MLabel()
        delay_button = MPushButton("Click to Edit Text")
        delay_line_editor.sig_delay_text_changed.connect(delay_display_label.setText)
        delay_button.clicked.connect(functools.partial(delay_line_editor.setText, "Edited from code"))

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("different size"))
        main_lay.addLayout(size_lay)
        main_lay.addWidget(MDivider("custom prefix and suffix widget"))
        main_lay.addWidget(line_edit_tool_button)
        main_lay.addWidget(line_edit_label)
        main_lay.addWidget(line_edit_push_button)
        main_lay.addWidget(MDivider("tags + completion"))
        main_lay.addWidget(TagLineEditExample())
        main_lay.addWidget(MDivider("preset"))

        main_lay.addWidget(MLabel("error"))
        main_lay.addWidget(MLineEdit(text="waring: file d:/ddd/ccc.jpg not exists.").error())
        main_lay.addWidget(MLabel("search"))
        main_lay.addWidget(MLineEdit().search().small())
        main_lay.addWidget(MLabel("search_engine"))
        main_lay.addWidget(search_engine_line_edit)
        main_lay.addWidget(MLabel("file"))
        main_lay.addWidget(MLineEdit().file().small())
        main_lay.addWidget(MLabel("folder"))
        main_lay.addWidget(MLineEdit().folder().small())
        main_lay.addWidget(MLabel("MLineEdit.options()"))
        main_lay.addWidget(line_edit_options)
        main_lay.addWidget(MDivider("Test delay Signal"))
        main_lay.addWidget(delay_line_editor)
        main_lay.addWidget(delay_display_label)
        main_lay.addWidget(delay_button)
        main_lay.addStretch()
        self.setLayout(main_lay)

    @QtCore.Slot()
    def slot_search(self):
        MMessage.info("查无此人", parent=self)


if __name__ == "__main__":
    # Import local modules
    from dayu_widgets import dayu_theme
    from dayu_widgets.qt import application

    with application() as app:
        test = LineEditExample()
        dayu_theme.apply(test)
        test.show()

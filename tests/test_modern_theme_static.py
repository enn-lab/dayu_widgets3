"""Static regression checks for the modern theme assets.

These checks intentionally use only the Python standard library so they can
run in environments without qtpy, PySide2, or PySide6.
"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "dayu_widgets" / "static"


class ModernThemeStaticTest(unittest.TestCase):
    def test_modern_theme_json_files_are_valid_and_complete(self):
        required = {
            "canvas_color",
            "surface_color",
            "surface_hover_color",
            "surface_pressed_color",
            "surface_selected_color",
            "surface_in_color",
            "surface_out_color",
            "elevated_color",
            "input_color",
            "border_subtle_color",
            "border_color",
            "border_strong_color",
            "text_primary_color",
            "text_secondary_color",
            "text_disabled_color",
            "accent_color",
            "accent_hover_color",
            "accent_pressed_color",
        }
        for filename, palette_name in (
            ("modern_dark.json", "dark"),
            ("modern_light.json", "light"),
        ):
            with self.subTest(filename=filename):
                data = json.loads((STATIC / filename).read_text(encoding="utf-8"))
                self.assertIn("primary_color", data)
                self.assertTrue(required.issubset(data[palette_name]))

    def test_completion_layer_covers_remaining_component_groups(self):
        qss = (STATIC / "main.qss").read_text(encoding="utf-8")
        marker = "/* Modern theme completion:"
        self.assertIn(marker, qss)
        completion = qss[qss.index(marker) :]
        for selector in (
            "MHeaderView::section:hover",
            "MTableView::item:selected",
            "MMenu::separator",
            "MMessage",
            "MToast",
            "MProgressBar::chunk",
            "QSplitter::handle:hover",
            "MMenuTabWidget QWidget#bar_widget",
            "MDockWidget::title",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, completion)
        for selector in (
            "QComboBox QAbstractItemView",
            "QComboBox QAbstractItemView::item:hover",
            "QComboBox QAbstractItemView::indicator:checked",
            'MComboBox[dayu_size="@small"] QAbstractItemView::item',
            "QFrame#dayuDividerLine",
            "QLabel#dayuDividerLabel",
            'MSidebar[dayu_navigation_level="1"]',
            'MSidebar[dayu_navigation_level="2"]',
            'MListView[dayu_navigation_level="3"]::item:selected',
            "MUnderlineButton:checked",
            "MUnderlineButton:checked:hover",
            'MPushButton[dayu_type="primary"]',
            'MPushButton[dayu_type="success"]:hover',
            'MPushButton[dayu_type="warning"]:pressed',
            'MPushButton[dayu_type]:disabled',
            'MLabel[dayu_mark="true"]',
            "MTag[dayu_tag_style=\"filled\"]",
            'MTag[dayu_closeable="true"]',
            "MCheckableTag:checked",
            "MNewTag",
            "MTag QToolButton#tag_close_button:hover",
            "MTableView::item:selected",
            "MTreeView::item:selected",
            'MBigView[dayu_tile_style="launcher"]::item:selected',
            "MIconMenu::item:selected",
            "MIconMenuItem QLabel#icon_menu_description",
            'MBigView[dayu_tile_style="launcher"]',
            "MIconGridMenu",
            "MIconGridItem[dayu_checked=\"true\"]",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, qss)

    def test_completion_layer_uses_declared_theme_tokens(self):
        qss = (STATIC / "main.qss").read_text(encoding="utf-8")
        completion = qss[qss.index("/* Modern theme completion:") :]
        tokens = set(re.findall(r"@([a-z_][a-z0-9_]*)", completion))
        known = set()
        for filename, palette_name in (
            ("modern_dark.json", "dark"),
            ("modern_light.json", "light"),
        ):
            data = json.loads((STATIC / filename).read_text(encoding="utf-8"))
            known.update(data[palette_name])
        known.update(
            {
                "accent_color",
                "accent_hover_color",
                "accent_pressed_color",
                "accent_8_color",
                "accent_12_color",
                "accent_20_color",
                "accent_35_color",
                "background_out_color",
                "border_radius_base",
                "border_radius_large",
                "border_radius_small",
                "error_6",
                "error_1",
                "error_3",
                "error_5",
                "error_7",
                "font_size_base",
                "font_size_small",
                "text_color_inverse",
                "font_unit",
                "icon_close",
                "icon_float",
                "icon_check",
                "icon_menu_right",
                "progress_bar_radius",
                "success_6",
                "success_1",
                "success_3",
                "success_5",
                "success_7",
                "warning_1",
                "warning_3",
                "warning_5",
                "warning_6",
                "warning_7",
                "unit",
            }
        )
        self.assertFalse(tokens - known, sorted(tokens - known))

    def test_line_tab_selected_state_keeps_hover_surface(self):
        qss = (STATIC / "main.qss").read_text(encoding="utf-8")
        selected = qss[qss.index("MUnderlineButton:checked {") :]
        selected = selected[: selected.index("}") + 1]
        self.assertIn("background-color: @surface_hover_color;", selected)

    def test_icon_menu_example_contains_version_choices(self):
        example = (ROOT / "examples" / "icon_menu_example.py").read_text(encoding="utf-8")
        for version in ("2026", "2025", "2024", "2023", "2022"):
            with self.subTest(version=version):
                self.assertIn('"{}"'.format(version), example)
        self.assertIn("InstantPopup", example)
        self.assertIn("MIconGridMenu", example)
        self.assertIn("columns=4", example)
        self.assertIn("description", example)

    def test_tag_software_list_example_supports_multi_select_tags(self):
        example = (ROOT / "examples" / "tag_software_list_example.py").read_text(encoding="utf-8")
        self.assertIn("class TagSoftwareListExample", example)
        self.assertIn("MTagLineEdit", example)
        self.assertIn("set_options", example)
        component = (ROOT / "dayu_widgets" / "tag_line_edit.py").read_text(encoding="utf-8")
        self.assertIn("class _FlowLayout", component)
        self.assertIn("class MTagLineEdit", component)
        self.assertIn("self._layout.addWidget(self._editor)", component)
        self.assertIn("self.width() - 8", component)
        self.assertIn("self._menu = MMenu(exclusive=False, parent=self)", component)
        self.assertIn('self._menu.setProperty("keep_open", True)', component)
        self.assertIn("self._menu.popup", component)
        self.assertIn("self._menu.hide()", component)
        self.assertIn("self._max_rows = 3", component)
        self.assertNotIn("setPlaceholderText(\"\")", component)

        # The editor is the caret of the container, not an editable field:
        # a free token is typed into it and committed with Enter.
        self.assertNotIn("setReadOnly(True)", component)
        self.assertIn("def _commit_editor_text", component)

        # The height is derived from the measured content on every resize
        # instead of being frozen from a stale measurement: an unlaid-out
        # widget (width 0/1) must not clamp the container to a bogus height.
        self.assertIn("def _apply_height", component)
        self.assertIn("def minimumSizeHint", component)
        self.assertIn("if width > 1 else 0", component)
        self.assertNotIn("min(self.heightForWidth(width)", component)

        # The popup is a picker: it must survive its own selection change.
        self.assertNotIn("self._suppress_menu_on_focus", component)
        self.assertIn("def _filter_menu_event", component)
        self.assertIn("self._menu_dispatching", component)
        self.assertIn("def _pointer_inside_interaction", component)
        self.assertIn("search_popup = self._menu.search_popup", component)
        self.assertIn("def _widget_contains_pointer", component)
        example = (ROOT / "examples" / "tag_software_list_example.py").read_text(encoding="utf-8")
        self.assertIn(").secondary())", example)

        qss = (STATIC / "main.qss").read_text(encoding="utf-8")
        self.assertIn("QWidget#tag_line_edit[dayu_tag_line_focus=true]", qss)
        self.assertIn("background-color: @input_color;", qss)
        self.assertIn("QLineEdit#menu_search_bar:focus", qss)
        menu = (ROOT / "dayu_widgets" / "menu.py").read_text(encoding="utf-8")
        self.assertIn("self.search_bar.setCursorPosition(len(char))", menu)
        self.assertNotIn("self.search_bar.selectAll()", menu)
        editor_rule = qss[qss.index("MLineEdit#tag_line_edit_editor") :]
        editor_rule = editor_rule[: editor_rule.index("}") + 1]
        self.assertNotIn("\n    color:", editor_rule)
        self.assertNotIn("\n    padding:", editor_rule)

    def test_tag_text_and_close_button_have_transparent_surfaces(self):
        """MTag sub-controls must not paint black child-widget surfaces."""
        qss = (STATIC / "main.qss").read_text(encoding="utf-8")
        tag_block = qss[qss.index("MTag {") :]
        tag_block = tag_block[: tag_block.index("MCheckableTag {")]
        self.assertIn("MTag QLabel#tag_text", tag_block)
        self.assertIn("background-color: transparent;", tag_block)
        self.assertIn("MTag QToolButton#tag_close_button {", tag_block)
        close_rule = qss[qss.index("MTag QToolButton#tag_close_button:hover") :]
        close_rule = close_rule[: close_rule.index("}") + 1]
        declared = {
            line.strip().split(":")[0]
            for line in close_rule.splitlines()
            if ":" in line and not line.strip().startswith(("/*", "*"))
        }
        for prop in ("color", "padding"):
            with self.subTest(prop=prop):
                self.assertNotIn(prop, declared)

    def test_tag_does_not_carry_a_widget_stylesheet(self):
        """MTag must be painted by the theme, never by a local stylesheet.

        A widget-level stylesheet outranks the application stylesheet and would
        freeze the tag on the colors captured at construction time, so a later
        ``dayu_theme.apply()`` could never restyle it.  The same applies to the
        close button.
        """
        source = (ROOT / "dayu_widgets" / "tag.py").read_text(encoding="utf-8")
        self.assertNotIn("setStyleSheet", source)
        self.assertNotIn("_apply_color_style", source)

    def test_combo_popup_preserves_hover_cursor(self):
        mixin = (ROOT / "dayu_widgets" / "mixin.py").read_text(encoding="utf-8")
        combo = (ROOT / "dayu_widgets" / "combo_box.py").read_text(encoding="utf-8")
        self.assertIn('"cursor_popup_open"', mixin)
        self.assertIn('self.setProperty("cursor_popup_open", True)', combo)
        self.assertIn('self.setProperty("cursor_popup_open", False)', combo)
        self.assertIn("def hidePopup(self):", combo)
        self.assertIn("QtCore.Qt.PointingHandCursor", combo)

    def test_cursor_mixin_restores_window_cursor(self):
        mixin = (ROOT / "dayu_widgets" / "mixin.py").read_text(encoding="utf-8")
        combo = (ROOT / "dayu_widgets" / "combo_box.py").read_text(encoding="utf-8")
        self.assertIn("def _clear_window_cursor(self):", mixin)
        self.assertIn("handle.unsetCursor()", mixin)
        self.assertIn("except RuntimeError:", mixin)
        self.assertNotIn("line_edit.setCursor(QtCore.Qt.PointingHandCursor)", combo)

    def test_combo_example_includes_default_native_popup(self):
        example = (ROOT / "examples" / "combo_box_example.py").read_text(encoding="utf-8")
        self.assertIn('MLabel("默认原生下拉")', example)
        self.assertIn('default_combo.addItems(cities + ["北戴河"])', example)
        combo = (ROOT / "dayu_widgets" / "combo_box.py").read_text(encoding="utf-8")
        self.assertIn("edit.setCursor(QtCore.Qt.IBeamCursor)", combo)

    def test_cascade_submenu_inherits_parent_menu_stylesheet(self):
        menu = (ROOT / "dayu_widgets" / "menu.py").read_text(encoding="utf-8")
        self.assertIn("source.setStyleSheet(self.styleSheet())", menu)
        self.assertIn("def _effective_stylesheet(self):", menu)
        self.assertIn("style_sheet = self._effective_stylesheet()", menu)
        self.assertIn("self._position_submenu(source)", menu)
        self.assertIn("dayu_theme.elevated_color", menu)
        self.assertIn("style.drawControl(self._compat_style.CE_MenuItem", menu)
        self.assertIn("FramelessWindowHint", menu)
        self.assertIn("def _qcolor_from_theme(value):", menu)
        self.assertIn("qp.setPen(QtCore.Qt.NoPen)", menu)
        qss = (STATIC / "main.qss").read_text(encoding="utf-8")
        self.assertIn("QMenu::item", qss)
        self.assertIn("QMenu::right-arrow", qss)


if __name__ == "__main__":
    unittest.main()

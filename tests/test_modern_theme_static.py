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
                "border_radius_base",
                "border_radius_large",
                "border_radius_small",
                "error_6",
                "error_1",
                "error_3",
                "error_5",
                "error_7",
                "font_size_base",
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


if __name__ == "__main__":
    unittest.main()

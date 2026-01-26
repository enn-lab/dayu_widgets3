#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/26 21:34
# @Author  : hesen
# @File    : collapse_filter_example.py

import sys
import os
from qtpy import QtWidgets, QtCore
from dayu_widgets.qt import application
from dayu_widgets import dayu_theme

# Import new component
from dayu_widgets import MCollapseFilter


class CollapseFilterExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CollapseFilterExample, self).__init__(parent)
        self.setWindowTitle("Examples for MCollapseFilter")
        self.resize(300, 600)
        self._init_ui()

    def _init_ui(self):

        self.filter_panel = MCollapseFilter()

        # Mock Data
        status_data = [
            {"name": "In Progress", "id": "ip", "count": 5},
            {"name": "Ready", "id": "rdy", "count": 12},
            {"name": "On Hold", "id": "hld", "count": 3},
            {"name": "Approved", "id": "apr", "count": 20},
        ]

        user_data = [
            {"name": "Artist A", "id": "user_a", "count": 8},
            {"name": "Artist B", "id": "user_b", "count": 4},
            {"name": "Supervisor", "id": "sup", "count": 1},
        ]

        self.filter_panel.add_section("status", "Status", status_data)
        self.filter_panel.add_section("user", "User", user_data)

        self.filter_panel.filter_changed.connect(self._on_filter_changed)

        self.result_label = QtWidgets.QLabel("Filter Result: {}")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-family: monospace; padding: 10px; background: #222; color: #eee;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.filter_panel)
        layout.addWidget(self.result_label)

    def _on_filter_changed(self, filter_state):
        print(f"Filter Changed: {filter_state}")
        text = "{\n"
        for k, v in filter_state.items():
            text += f"  '{k}': {v},\n"
        text += "}"
        self.result_label.setText(f"Filter Result:\n{text}")


if __name__ == "__main__":
    with application() as app:
        test = CollapseFilterExample()
        dayu_theme.apply(test)
        test.show()

# -*- coding: utf-8 -*-
"""深色设置面板 Demo —— 分割线 + 卡片白边（QSS 兼容 PySide2 / PySide6）"""
import sys

try:
    from PySide2 import QtWidgets as W
    from PySide2 import QtGui as G
    from PySide2 import QtCore as C
    BIND = "PySide2"
except ImportError:
    from PySide6 import QtWidgets as W
    from PySide6 import QtGui as G
    from PySide6 import QtCore as C
    BIND = "PySide6"

QSS = """
* { font-family: "Segoe UI", "Microsoft YaHei", sans-serif; }
QWidget { color: #c9d1d9; }
QWidget#root { background-color: #0d0e10; }

/* 顶部标题区 —— 底部分割线 */
QWidget#headerPanel { background-color: #0d0e10; border-bottom: 1px solid rgba(255,255,255,0.08); }
QLabel#appTitle { color: #e6edf3; font-size: 15px; font-weight: 600; }

/* 右上 "默认" 标签 */
QPushButton#tagBtn {
    background-color: #1f2329; color: #58a6ff;
    border: 1px solid rgba(88,166,255,0.35); border-radius: 10px;
    padding: 3px 12px; font-size: 12px;
}
QPushButton#tagBtn:hover { background-color: #262b33; }

/* 左导航 —— 右侧分割线 */
QWidget#leftPanel { background-color: #0d0e10; border-right: 1px solid rgba(255,255,255,0.08); }
QPushButton#navBtn { background: transparent; border: none; color: #8b949e; font-size: 12px; border-radius: 4px; padding: 7px 0; }
QPushButton#navBtn:hover { background-color: #16191d; color: #e6edf3; }
QPushButton#navBtn:checked { background-color: #1f2329; color: #e6edf3; }

/* 中软件列表 —— 右侧分割线 */
QWidget#middlePanel { background-color: #0d0e10; border-right: 1px solid rgba(255,255,255,0.08); }
QLabel#sectionLabel { color: #8b949e; font-size: 11px; }

QListWidget#softList { background: transparent; border: none; outline: none; }
QListWidget#softList::item { color: #c9d1d9; padding: 10px 12px; border-radius: 6px; }
QListWidget#softList::item:hover { background-color: #16191d; }
QListWidget#softList::item:selected { background-color: #1f2329; color: #e6edf3; }

/* 右卡片区 */
QWidget#rightPanel { background-color: #0d0e10; }
QScrollArea#cardArea { border: none; background: transparent; }
QScrollArea#cardArea > QWidget > QWidget { background: transparent; }

/* 卡片：深底 + 1px 细白边 + 圆角 */
QFrame#configCard {
    background-color: #14161a;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
}
QLabel#cardTitle { color: #e6edf3; font-size: 14px; font-weight: 600; }
QLabel#chip { background-color: #1f2329; color: #8b949e; border: 1px solid rgba(255,255,255,0.06); border-radius: 4px; padding: 2px 8px; font-size: 11px; }
QLabel#cardDesc { color: #8b949e; font-size: 12px; }
"""


def make_card(title, chip, desc):
    card = W.QFrame()
    card.setObjectName("configCard")
    lay = W.QVBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(8)

    head = W.QHBoxLayout()
    head.setSpacing(8)
    t = W.QLabel(title)
    t.setObjectName("cardTitle")
    head.addWidget(t)
    head.addStretch(1)
    c = W.QLabel(chip)
    c.setObjectName("chip")
    head.addWidget(c)
    lay.addLayout(head)

    d = W.QLabel(desc)
    d.setObjectName("cardDesc")
    d.setWordWrap(True)
    lay.addWidget(d)
    return card


class Main(W.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("设置面板 Demo —— PySide2 分割线 / 卡片白边")
        self.resize(920, 580)
        self.setStyleSheet(QSS)
        self._build()

    def _build(self):
        root = W.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # header
        header = W.QWidget()
        header.setObjectName("headerPanel")
        header.setFixedHeight(56)
        hl = W.QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        title = W.QLabel("工作流配置")
        title.setObjectName("appTitle")
        hl.addWidget(title)
        hl.addStretch(1)
        tag = W.QPushButton("默认")
        tag.setObjectName("tagBtn")
        tag.setCheckable(True)
        tag.setChecked(True)
        hl.addWidget(tag)
        root.addWidget(header)

        # body
        body = W.QWidget()
        bl = W.QHBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(0)

        # 左导航
        left = W.QWidget()
        left.setObjectName("leftPanel")
        left.setFixedWidth(64)
        ll = W.QVBoxLayout(left)
        ll.setContentsMargins(8, 16, 8, 16)
        ll.setSpacing(6)
        for i, name in enumerate(["项目", "设置", "插件", "关于"]):
            b = W.QPushButton(name)
            b.setObjectName("navBtn")
            b.setCheckable(True)
            if i == 1:
                b.setChecked(True)
            ll.addWidget(b)
        ll.addStretch(1)
        bl.addWidget(left)

        # 中软件列表
        mid = W.QWidget()
        mid.setObjectName("middlePanel")
        mid.setFixedWidth(220)
        ml = W.QVBoxLayout(mid)
        ml.setContentsMargins(12, 16, 12, 16)
        ml.setSpacing(8)
        sec = W.QLabel("DCC 软件")
        sec.setObjectName("sectionLabel")
        ml.addWidget(sec)
        self.soft = W.QListWidget()
        self.soft.setObjectName("softList")
        for name in ["Pencil+ 4.2.4", "Yeti 5.0", "Arnold", "Maya 2024"]:
            self.soft.addItem(name)
        self.soft.setCurrentRow(0)
        ml.addWidget(self.soft, 1)
        bl.addWidget(mid)

        # 右卡片区
        right = W.QWidget()
        right.setObjectName("rightPanel")
        rl = W.QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        scroll = W.QScrollArea()
        scroll.setObjectName("cardArea")
        scroll.setWidgetResizable(True)
        container = W.QWidget()
        container.setObjectName("cardContainer")
        cl = W.QVBoxLayout(container)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(16)
        cl.addWidget(make_card(
            "启动配置", "默认",
            "指定 UE / Maya 的启动参数与入口脚本，勾选后随工作流自动拉起。"))
        cl.addWidget(make_card(
            "渲染参数", "4.2.4",
            "分辨率、采样与输出路径等渲染相关设置，按项目隔离保存。"))
        cl.addWidget(make_card(
            "插件路径", "3 项",
            "管理第三方插件的加载目录与优先级，支持拖拽排序。"))
        cl.addStretch(1)
        scroll.setWidget(container)
        rl.addWidget(scroll)
        bl.addWidget(right, 1)

        root.addWidget(body, 1)


def main():
    if BIND == "PySide2":
        W.QApplication.setAttribute(C.Qt.AA_EnableHighDpiScaling, True)
        W.QApplication.setAttribute(C.Qt.AA_UseHighDpiPixmaps, True)
    app = W.QApplication(sys.argv)
    app.setFont(G.QFont("Microsoft YaHei", 9))
    win = Main()
    win.show()
    print(f"[run] binding = {BIND}")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

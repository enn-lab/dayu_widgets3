# -*- coding: utf-8 -*-
"""
SOLO / CodeBuddy 风格深色设置面板 —— PySide6 demo
复刻截图: 深色IDE设置面板
  三段式: 左侧任务侧栏 | 中间工作区(Agent+输入框) | 右侧设置面板
运行:   python pyside6_solo_demo.py
截图:   python pyside6_solo_demo.py --shot out.png  (离屏渲染)
"""
import sys
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import (QColor, QFont, QLinearGradient, QPainter, QBrush,
                           QPixmap)
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QFrame,
                               QLabel, QPushButton, QLineEdit, QComboBox,
                               QListWidget, QListWidgetItem, QHBoxLayout,
                               QVBoxLayout, QGridLayout, QScrollArea,
                               QSpacerItem, QSizePolicy)

# ---------------------------------------------------------------- 调色板
DEEP      = "#0c0d10"
PANEL     = "#121419"
CARD      = "#15171d"
INPUT     = "#1a1d24"
BORDER    = "#252a33"
TXT       = "#e8eaed"
TXT2      = "#9aa0ad"
TXT3      = "#5f6572"
# 品牌主色 = 青绿/薄荷绿(从截图采样 @Agent Logo), 非紫色
ACCENT    = "#23d18b"
ACCENT_D  = "#1cb878"
BRAND_BG  = "#0f3d2b"   # @Agent 徽标深绿底
BRAND_FG  = "#4ce8a0"   # @Agent 徽标薄荷绿图形
HOVER     = "#1c1f27"
SELTINT   = "#24272f"   # 选中项: 中性灰高亮(非紫色)
WHITE     = "#ffffff"

FONT = 'Segoe UI, "Microsoft YaHei", sans-serif'

# ---------------------------------------------------------------- QSS
STYLE = f"""
* {{ font-family: {FONT}; }}
QMainWindow, QWidget#root {{ background-color: {DEEP}; }}

/* 顶部标签页 */
QPushButton[tab="true"] {{
    color: {TXT2}; background: transparent; border: none;
    padding: 6px 16px; border-radius: 8px; font-size: 12px;
}}
QPushButton[tab="true"]:hover {{ color: {TXT}; background: {HOVER}; }}
QPushButton[tab="true"]:checked {{ color: {WHITE}; background: {CARD}; }}

/* 通用按钮 —— 主/次 */
QPushButton[btn="primary"] {{
    color: {WHITE}; background: {ACCENT}; border: none; border-radius: 8px;
    padding: 7px 20px; font-size: 12px; font-weight: 600;
}}
QPushButton[btn="primary"]:hover {{ background: {ACCENT_D}; }}
QPushButton[btn="ghost"] {{
    color: {TXT}; background: {CARD}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 7px 16px; font-size: 12px;
}}
QPushButton[btn="ghost"]:hover {{ background: {HOVER}; }}

/* 下拉框 */
QComboBox {{
    color: {TXT}; background: {CARD}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 7px 12px; font-size: 12px; min-width: 150px;
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {PANEL}; color: {TXT}; border: 1px solid {BORDER};
    selection-background-color: {SELTINT}; selection-color: {WHITE};
    outline: none; font-size: 12px;
}}

/* 搜索框 / 文本输入 */
QLineEdit {{
    color: {TXT}; background: {INPUT}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 7px 12px; font-size: 12px;
}}
QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
QLineEdit::placeholder {{ color: {TXT3}; }}

/* 设置导航列表 */
QListWidget#nav {{ background: transparent; border: none; outline: none; }}
QListWidget#nav::item {{
    color: {TXT2}; background: transparent; border: none;
    border-radius: 7px; padding: 9px 10px; margin: 1px 4px; font-size: 12px;
}}
QListWidget#nav::item:hover {{ background: {HOVER}; color: {TXT}; }}
QListWidget#nav::item:selected {{ background: {SELTINT}; color: {WHITE}; }}

/* 左侧任务列表 */
QListWidget#tasks {{ background: transparent; border: none; outline: none; }}
QListWidget#tasks::item {{
    background: {PANEL}; border: none; border-radius: 8px;
    margin: 2px 4px; padding: 8px; color: {TXT};
}}
QListWidget#tasks::item:hover {{ background: {HOVER}; }}
QListWidget#tasks::item:selected {{ background: {SELTINT}; }}

/* 滚动条 */
QScrollBar:vertical {{
    background: transparent; width: 8px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 4px; min-height: 30px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

/* 分组卡片 */
QFrame.card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}
QFrame.subcard {{ background: {PANEL}; border-radius: 8px; }}
"""


# ---------------------------------------------------------------- 工具
def mk_lbl(text, color=TXT, size=12, bold=False, wrap=False):
    l = QLabel(text)
    l.setStyleSheet(f"color:{color}; font-size:{size}px;"
                    f"{'font-weight:600;' if bold else ''}"
                    f"{'' if not wrap else ''}")
    if wrap:
        l.setWordWrap(True)
    return l


def circle_avatar(diameter=40, color1="#a08bff", color2="#6f4df0", glyph=""):
    """渐变圆形头像"""
    pm = QPixmap(diameter, diameter)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    g = QLinearGradient(0, 0, diameter, diameter)
    g.setColorAt(0, QColor(color1)); g.setColorAt(1, QColor(color2))
    p.setBrush(QBrush(g)); p.setPen(Qt.NoPen)
    p.drawEllipse(0, 0, diameter, diameter)
    if glyph:
        f = QFont(FONT.split(",")[0].strip(), int(diameter * 0.35), QFont.Bold)
        p.setFont(f); p.setPen(QColor(WHITE))
        p.drawText(QRect(0, 0, diameter, diameter), Qt.AlignCenter, glyph)
    p.end()
    l = QLabel()
    l.setPixmap(pm)
    l.setFixedSize(diameter, diameter)
    return l


# ---------------------------------------------------------------- 左侧任务侧栏
class LeftPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(250)
        self.setStyleSheet(f"background:{PANEL}; border-right:1px solid {BORDER};")
        v = QVBoxLayout(self); v.setContentsMargins(12, 14, 12, 12); v.setSpacing(10)

        # logo
        logo_row = QHBoxLayout(); logo_row.setSpacing(8)
        box = QLabel("SOLO"); box.setStyleSheet(
            f"color:{WHITE};background:{DEEP};border:1px solid {BORDER};"
            f"border-radius:6px;padding:3px 8px;font-weight:700;font-size:12px;")
        box.setFixedSize(58, 24)
        dbox = QLabel("D"); dbox.setStyleSheet(
            f"color:{TXT2};border:1px solid {BORDER};border-radius:6px;padding:2px 8px;font-size:12px;")
        logo_row.addWidget(box); logo_row.addWidget(dbox); logo_row.addStretch()
        v.addLayout(logo_row)

        v.addSpacing(4)

        # 新建任务
        new_btn = QPushButton("+  新建任务")
        new_btn.setProperty("btn", "ghost")
        new_btn.setStyleSheet(
            f"color:{TXT2};background:{CARD};border:1px solid {BORDER};border-radius:8px;"
            f"padding:7px 10px;font-size:12px;color:{TXT2};")
        # 右侧 Ctrl+N 提示
        nb = QHBoxLayout(); nb.addWidget(new_btn); nb.addStretch()
        kb = QLabel("Ctrl+N"); kb.setStyleSheet(
            f"color:{TXT3};border:1px solid {BORDER};border-radius:5px;padding:2px 8px;font-size:10px;")
        nb.insertWidget(1, kb)
        v.addLayout(nb)

        v.addSpacing(2)

        # 任务计数 + 搜索
        rc = QHBoxLayout()
        rc.addWidget(mk_lbl("任务", TXT2, 12, bold=True))
        cnt = QLabel("7"); cnt.setStyleSheet(
            f"color:{TXT2};background:{HOVER};border-radius:8px;padding:1px 7px;font-size:11px;")
        rc.addWidget(cnt); rc.addStretch()
        search = QLabel("🔍"); search.setStyleSheet(f"color:{TXT3};font-size:12px;")
        rc.addWidget(search)
        v.addLayout(rc)

        # 任务列表
        self.tasks = QListWidget(); self.tasks.setObjectName("tasks")
        rows = [
            ("设计 Launcher UI...", "完成 8月26日 21:17", True),
            ("本地模型部署...", "完成 8月18日 15:44", True),
            ("dcc settings M7...", "完成 8月30日 14:55", True),
            ("docs settings", "完成 8月3日 10:57", True),
            ("介绍你自己", "完成 7月31日 15:18", True),
            ("Maya 编辑管理...", "任务中 7月30日 16:31", False),
            ("Review Aron Proj...", "完成 7月16日 14:16", True),
        ]
        for title, sub, done in rows:
            item = QListWidgetItem()
            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(8)
            dot = QLabel("✓" if done else "●")
            dot.setStyleSheet(
                f"color:{'#3ddc84' if done else '#e6a23c'};font-size:11px;font-weight:700;")
            col = QVBoxLayout(); col.setSpacing(2)
            col.addWidget(mk_lbl(title, TXT, 12))
            col.addWidget(mk_lbl(sub, TXT3, 10))
            h.addWidget(dot); h.addLayout(col); h.addStretch()
            item.setSizeHint(QSize(0, 46))
            self.tasks.addItem(item)
            self.tasks.setItemWidget(item, w)
        v.addWidget(self.tasks, 1)


# ---------------------------------------------------------------- 底部输入条
class PromptBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            f"background:{CARD};border:1px solid {BORDER};border-radius:12px;")
        v = QVBoxLayout(self); v.setContentsMargins(14, 12, 14, 10); v.setSpacing(12)
        ph = QLabel("帮你编写代码、调试 Bug、优化性能等开发工作、交付生产级代码产物…")
        ph.setStyleSheet(f"color:{TXT3};font-size:12px;")
        ph.setWordWrap(True)
        v.addWidget(ph)

        bar = QHBoxLayout(); bar.setSpacing(12)
        for ic in ["+", "🎤"]:
            b = QLabel(ic); b.setStyleSheet(
                f"color:{TXT2};background:{HOVER};border-radius:6px;padding:3px 10px;font-size:12px;")
            bar.addWidget(b)
        tag = QLabel("@Agent"); tag.setStyleSheet(
            f"color:{TXT2};background:{HOVER};border-radius:6px;padding:3px 10px;font-size:11px;")
        bar.addWidget(tag)
        bar.addStretch()
        auto = QLabel("Auto"); auto.setStyleSheet(
            f"color:{TXT};font-size:12px;font-weight:600;")
        bar.addWidget(auto)
        chips = QLabel("◇"); chips.setStyleSheet(
            f"color:{TXT2};font-size:12px;")
        bar.addWidget(chips)
        dot = QLabel("●"); dot.setStyleSheet(f"color:{ACCENT};font-size:11px;")
        bar.addWidget(dot)
        v.addLayout(bar)


# ---------------------------------------------------------------- 中间工作区
class CenterPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{DEEP};")
        v = QVBoxLayout(self); v.setContentsMargins(18, 12, 18, 12); v.setSpacing(0)

        # 项目名 + 顶部标签
        top = QHBoxLayout(); top.setSpacing(10)
        proj = QLabel("km-pipeline"); proj.setStyleSheet(
            f"color:{TXT};font-size:12px;font-weight:600;")
        top.addWidget(proj)
        top.addSpacing(6)
        mid = QLabel("537   🎤   ✦"); mid.setStyleSheet(
            f"color:{TXT3};font-size:12px;")
        top.addWidget(mid)
        top.addStretch()
        # 标签页
        for t in ["编辑器", "MCP", "插件市场", "设置", "+"]:
            tb = QPushButton(t)
            tb.setProperty("tab", True); tb.setCheckable(True)
            tb.setCursor(Qt.PointingHandCursor)
            if t == "设置":
                tb.setChecked(True)
            top.addWidget(tb)
        v.addLayout(top)

        # 顶部标签也放到中间标题下方横线
        v.addSpacing(4)
        hr = QFrame(); hr.setFixedHeight(1); hr.setStyleSheet(f"background:{PANEL};")
        v.addWidget(hr)
        v.addSpacing(28)

        # Agent 卡片
        card = QFrame(); card.setObjectName("agentCard")
        card.setStyleSheet(f"QFrame#agentCard{{background:transparent;}}")
        cv = QVBoxLayout(card); cv.setSpacing(14)
        brand = QHBoxLayout(); brand.setSpacing(10)
        # @Agent 徽标 = 深绿底 + 薄荷绿图形(品牌主色, 非紫色)
        b = QLabel("@Agent")
        b.setStyleSheet(
            f"background:{BRAND_BG};color:{BRAND_FG};border-radius:6px;"
            f"padding:4px 12px;font-weight:700;font-size:13px;")
        brand.addWidget(b); brand.addStretch()
        cv.addLayout(brand)
        title = mk_lbl("轻松应对复杂项目开发", TXT, 20, bold=True)
        cv.addWidget(title)
        pts = ["擅长项目迭代、问题修复与架构重构",
               "智能任务规划，确认后精准执行",
               "自主编辑智能体、AI 专家团队协同开发"]
        for p in pts:
            row = QHBoxLayout(); row.setSpacing(8)
            dot = QLabel("•"); dot.setStyleSheet(f"color:{ACCENT};font-size:14px;")
            row.addWidget(dot)
            row.addWidget(mk_lbl(p, TXT2, 12))
            row.addStretch()
            cv.addLayout(row)
        cv.addStretch()
        v.addWidget(card, 1)

        v.addWidget(PromptBar())


# ---------------------------------------------------------------- 设置导航项
def nav_row(icon, text, with_chev=False):
    w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(10)
    ic = QLabel(icon); ic.setStyleSheet(f"color:{TXT3};font-size:12px;width:18px;")
    tl = mk_lbl(text, TXT2, 12)
    h.addWidget(ic); h.addWidget(tl); h.addStretch()
    if with_chev:
        ch = QLabel("›"); ch.setStyleSheet(f"color:{TXT3};font-size:14px;")
        h.addWidget(ch)
    return w


# ---------------------------------------------------------------- 设置行
def setting_row(title, desc, control):
    """两行式设置项: 左(标题+说明) 右(控件)"""
    row = QHBoxLayout(); row.setSpacing(14)
    left = QVBoxLayout(); left.setSpacing(3)
    left.addWidget(mk_lbl(title, TXT, 12, bold=True))
    if desc:
        d = mk_lbl(desc, TXT3, 11); d.setWordWrap(True)
        left.addWidget(d)
    row.addLayout(left)
    row.addStretch(1)
    row.addWidget(control, 0, Qt.AlignVCenter)
    return row


def combo(items, sel=0):
    c = QComboBox(); c.addItems(items); c.setCurrentIndex(sel)
    c.setCursor(Qt.PointingHandCursor)
    return c


# ---------------------------------------------------------------- 右侧设置面板
class SettingsPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(720)
        self.setStyleSheet(f"background:{PANEL}; border-left:1px solid {BORDER};")
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)

        body = QHBoxLayout(); body.setContentsMargins(0, 16, 0, 0); body.setSpacing(0)

        # ---- 左: 设置导航
        navcol = QVBoxLayout(); navcol.setContentsMargins(6, 0, 0, 0); navcol.setSpacing(6)
        # 用户卡
        usercard = QFrame(); usercard.setObjectName("subcard")
        usercard.setStyleSheet(
            f"background:{PANEL}; border:1px solid {BORDER}; border-radius:10px;")
        uv = QVBoxLayout(usercard); uv.setContentsMargins(10, 12, 10, 12); uv.setSpacing(10)
        urow = QHBoxLayout(); urow.setSpacing(10)
        urow.addWidget(circle_avatar(38, glyph="U"))
        ucol = QVBoxLayout(); ucol.setSpacing(2)
        uname = mk_lbl("用户126768009…", TXT, 12, bold=True)
        uplan = mk_lbl("免费", TXT3, 11)
        ucol.addWidget(uname); ucol.addWidget(uplan)
        urow.addLayout(ucol); urow.addStretch()
        uv.addLayout(urow)
        usearch = QLineEdit(); usearch.setPlaceholderText("Ctrl+F  搜索")
        uv.addWidget(usearch)
        navcol.addWidget(usercard)

        navcol.addSpacing(2)
        nav = QListWidget()
        nav.setObjectName("nav")
        nav.setCursor(Qt.PointingHandCursor)
        nav.setStyleSheet("""
            QListWidget#nav { background: transparent; border: none; outline: none; }
        """)
        # 注入自定义 item widget(图标 + 文本 + 箭头)
        def add_item(icon, text, chev=False, selected=False):
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 38))
            if selected:
                item.setSelected(True)
            item.setData(Qt.UserRole, (icon, text, chev))
        nav_items = [
            ("⚙", "账号"), ("〰", "用量管理"), ("●", "通用"), ("▤", "TRAE 移动端"),
            ("⌁", "开发环境", True),
            ("🛡", "权限审批"), ("⚡", "智能体"), ("🧩", "插件市场"),
            ("⛓", "MCP"), ("◇", "CUE"), ("◫", "模型"), ("💬", "对话流"),
            ("🌐", "浏览器"), ("🖥", "电脑控制"), ("☰", "工作树", True),
            ("🗂", "索引与文档"), ("⌘", "技能与命令"),
            ("📋", "规则与记忆"), ("⚙", "Hooks"), ("🔶", "Beta"),
        ]
        for i, it in enumerate(nav_items):
            icon, text = it[0], it[1]
            chev = it[2] if len(it) > 2 else False
            add_item(icon, text, chev, selected=(text == "通用"))
            item = nav.item(i)
            nav.setItemWidget(item, nav_row(icon, text, chev))
        nav.setFixedWidth(168)
        navcol.addWidget(nav)
        navcol.addStretch()
        body.addLayout(navcol)

        # ---- 右: 内容区(可滚动)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        inner = QWidget(); inner.setStyleSheet("background:transparent;")
        cv = QVBoxLayout(inner); cv.setContentsMargins(16, 0, 16, 20); cv.setSpacing(16)

        # 通用 标题
        cv.addWidget(mk_lbl("通用", TXT, 18, bold=True))

        # 基础设置 卡片
        basic = QFrame(); basic.setProperty("card", True)
        basic.setStyleSheet("QFrame[card=\"true\"]{"
                            f"background:{PANEL}; border:1px solid {BORDER}; border-radius:10px;}}")
        bv = QVBoxLayout(basic); bv.setContentsMargins(16, 16, 16, 16); bv.setSpacing(4)
        bv.addWidget(mk_lbl("基础设置", TXT2, 12, bold=True))
        bv.addSpacing(8)
        g = QGridLayout(); g.setHorizontalSpacing(12); g.setVerticalSpacing(16)
        g.setColumnStretch(0, 1)
        # 主题
        g.addLayout(setting_row("主题", "选择主题", combo(["暗色", "亮色", "跟随系统"], 0)), 0, 0)
        # 语言
        g.addLayout(setting_row("语言",
                    "选择您喜欢的按钮标题和界面中其他文本的语言",
                    combo(["简体中文", "English", "繁體中文", "日本語"], 0)), 1, 0)
        bv.addLayout(g)
        cv.addWidget(basic)

        # 偏好设置
        pref = QFrame()
        pref.setStyleSheet("QFrame[card=\"true\"]{"
                           f"background:{PANEL}; border:1px solid {BORDER}; border-radius:10px;}}")
        pref.setProperty("card", True)
        pv = QVBoxLayout(pref); pv.setContentsMargins(16, 16, 16, 16); pv.setSpacing(0)
        pv.addWidget(mk_lbl("偏好设置", TXT2, 12, bold=True))
        pv.addSpacing(10)

        def ghost_btn(t):
            b = QPushButton(t); b.setProperty("btn", "ghost")
            b.setCursor(Qt.PointingHandCursor)
            return b

        # 各设置项
        rows = [
            ("Editor 设置", "Editor 中字体、word-wrap、window 设置等", ghost_btn("去设置")),
            ("快捷键设置", "对 IDE 中的各个操作的快捷键进行自定义设置",
             combo(["使用 VS Code 快捷键风格", "使用 Cursor 快捷键风格", "使用 JetBrains 快捷键风格"], 0)),
            ("导入配置", "导入 VS Code 或 Cursor 中的所有插件、设置、代码片段以及快捷键配置到 TRAE 中，需登录，导入后新增需替换 TRAE 当前配置，且不可恢复",
             ghost_btn("导入")),
            ("本地链接的默认打开方式", "选择编辑中的本地链接时，是否根据编辑规则默认打开",
             combo(["系统浏览器", "编辑器内预览", "始终询问"], 0)),
            ("Markdown 文件的默认打开方式", "Markdown 文件默认用编辑器方式打开",
             combo(["Markdown 预览模式", "代码 / 编辑模式"], 0)),
        ]
        for i, (t, d, c) in enumerate(rows):
            pv.addLayout(setting_row(t, d, c))
            if i != len(rows) - 1:
                sep = QFrame(); sep.setFixedHeight(1)
                sep.setStyleSheet(f"background:{BORDER};")
                pv.addWidget(sep)
            pv.addSpacing(8)
        cv.addWidget(pref)
        cv.addStretch()

        scroll.setWidget(inner)
        body.addWidget(scroll, 1)

        outer.addLayout(body)


# ---------------------------------------------------------------- 主窗口
class SoloWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SOLO — PySide6 Demo")
        self.resize(1280, 760)

        root = QWidget(); root.setObjectName("root")
        h = QHBoxLayout(root); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(0)
        h.addWidget(LeftPanel())
        h.addWidget(CenterPanel(), 1)
        h.addWidget(SettingsPanel())
        self.setCentralWidget(root)


def main():
    shot = "--shot" in sys.argv
    if shot:
        # 用真实 windows 平台 + 不显示到屏幕，确保加载系统中文字体
        import os
        os.environ["QT_QPA_PLATFORM"] = "windows"
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    if shot:
        win = SoloWindow()
        win.resize(1360, 820)
        win.setAttribute(Qt.WA_DontShowOnScreen, True)
        win.show()
        app.processEvents()
        out = "solo_demo_preview.png"
        idx = sys.argv.index("--shot")
        if idx + 1 < len(sys.argv):
            out = sys.argv[idx + 1]
        pm = win.grab()
        pm.save(out)
        print("saved:", out)
        return

    win = SoloWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

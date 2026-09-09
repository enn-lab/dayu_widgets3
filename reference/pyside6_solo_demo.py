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
                               QSpacerItem, QSizePolicy,
                               QGraphicsDropShadowEffect)

# ---------------------------------------------------------------- 调色板
# 表面颜色用 rgba() 半透明玻璃质感; 文字保持不透明
# 备注标注每个颜色在代码里被用到的具体位置

# 窗口/主背景 —— 不透明深黑底
DEEP      = "#0a0b0e"
#   用途: QMainWindow root 背景 | CenterPanel 背景 | SOLO logo 文本盒背景

# 面板层 —— 不透明深色, 区块(左/中/右)整体底色
PANEL     = "#0f1114"
#   用途: LeftPanel 侧栏背景 | SettingsPanel 整体背景 | QComboBox 下拉浮层背景 | 顶栏分隔线

# 玻璃表面 —— 卡片/按钮半透明底
GLASS     = "rgba(255,255,255,0.04)"
#   用途: QFrame.card/.subcard 默认背景 | ghost 按钮背景 | 下拉框(QComboBox)背景 | 任务卡片底

# 玻璃抬升/hover —— 比 GLASS 更亮的半透明白
GLASS_HI  = "rgba(255,255,255,0.07)"
#   用途: 顶部 tabBar 玻璃容器背景 | PromptBar 输入框背景 | 下拉框 hover 态

# 内凹玻璃 —— 输入槽底, 比面板更深(用黑色 alpha 营造下凹感)
GLASS_LO  = "rgba(0,0,0,0.26)"
#   用途: QLineEdit 输入框背景(搜索框 Ctrl+F)

# 边框 —— 标准淡白边
BORDER    = "rgba(255,255,255,0.10)"
#   用途: cards/subcards 边框 | PromptBar 边框 | ghost 按钮边框 | 下拉框边框 | QLineEdit 边框

# 弱化边框 —— 比 BORDER 更淡的描边
BORDER_LO = "rgba(255,255,255,0.05)"
#   用途: 卡片/按钮/PromptBar 更微弱的描边 | 设置项分隔线 | tabBar 容器边 | 任务项选中态边框

# 文字色阶
TXT       = "#e8eaed"
#   用途: 主文字 —— 标题、按钮文字、菜单/列表/输入框前景(全局默认色)
TXT2      = "#9aa0ad"
#   用途: 次级文字 —— 段落标题(基础设置/偏好设置)、按钮次级文案、设置项副标题、导航未选中文字
TXT3      = "#5f6572"
#   用途: 辅助文字 —— 占位符(搜索框 placeholder)、任务时间戳、设置项说明性小字、参数标签

# 品牌主色 —— 青绿/薄荷绿(@Agent Logo 采样, 非紫色)
ACCENT    = "#23d18b"
#   用途: Agent 项目要点小圆点 | QLineEdit focus 聚焦边框 | 主按钮(btn=primary)背景
ACCENT_D  = "#1cb878"
#   用途: 主按钮 hover 态
BRAND_BG  = "#0f3d2b"
#   用途: @Agent 徽标的深绿底色
BRAND_FG  = "#4ce8a0"
#   用途: @Agent 徽标文字色(薄荷绿图形/字符)

# 交互态
HOVER     = "rgba(255,255,255,0.07)"
#   用途: 设置导航/任务列表/ghost 按钮 hover 半透明高亮
SELTINT   = "rgba(255,255,255,0.09)"
#   用途: 导航选中项背景 | 任务选中项背景 | 下拉框浮层选中项背景(中性灰高亮, 非紫色)

# 纯白 —— 用于激活标签文字/主按钮文字等需要最高对比度的地方
WHITE     = "#ffffff"
#   用途: 激活 tab 文字 | 主按钮文字 | SOLO logo 文字 | 头像图形描边

# 头像渐变色 —— 仅用于右上方用户头像圆形的紫/品红渐变
AVATAR_C1 = "#a08bff"
#   用途: 头像渐变起点(亮紫)
AVATAR_C2 = "#6f4df0"
#   用途: 头像渐变终点(深紫)

# 任务状态色 —— 左侧任务列表前的小图标
DONE_COLOR = "#3ddc84"
#   用途: 已完成任务的对勾(✓)绿色
BUSY_COLOR = "#e6a23c"
#   用途: 进行中任务的圆点(●)琥珀色

# 兼容别名(用于底层仍引用旧变量名的场合)
CARD      = GLASS
INPUT     = GLASS_LO

FONT = 'Segoe UI, "Microsoft YaHei", sans-serif'

# ---------------------------------------------------------------- QSS
STYLE = f"""
* {{ font-family: {FONT}; }}
QMainWindow, QWidget#root {{ background-color: {DEEP}; }}
QWidget {{ color: {TXT}; }}

/* 顶部标签容器 —— 半透明玻璃条 */
QFrame#tabBar {{
    background: {GLASS_HI}; border: 1px solid {BORDER_LO};
    border-radius: 12px;
}}
QPushButton[tab="true"] {{
    color: {TXT2}; background: transparent; border: none;
    padding: 6px 16px; border-radius: 9px; font-size: 12px;
}}
QPushButton[tab="true"]:hover {{ color: {TXT}; background: {HOVER}; }}
QPushButton[tab="true"]:checked {{
    color: {WHITE}; background: {GLASS}; border: 1px solid {BORDER_LO};
}}

/* 通用按钮 —— 半透明 */
QPushButton[btn="primary"] {{
    color: {WHITE}; background: {ACCENT}; border: none; border-radius: 8px;
    padding: 7px 20px; font-size: 12px; font-weight: 600;
}}
QPushButton[btn="primary"]:hover {{ background: {ACCENT_D}; }}
QPushButton[btn="ghost"] {{
    color: {TXT}; background: {GLASS}; border: 1px solid {BORDER_LO};
    border-radius: 8px; padding: 7px 16px; font-size: 12px;
}}
QPushButton[btn="ghost"]:hover {{ background: {HOVER}; border-color: {BORDER}; }}

/* 下拉框 —— 半透明 */
QComboBox {{
    color: {TXT}; background: {GLASS}; border: 1px solid {BORDER_LO};
    border-radius: 8px; padding: 7px 12px; font-size: 12px; min-width: 150px;
}}
QComboBox:hover {{ background: {GLASS_HI}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {PANEL}; color: {TXT}; border: 1px solid {BORDER_LO};
    selection-background-color: {SELTINT}; selection-color: {WHITE};
    outline: none; font-size: 12px; border-radius: 8px;
}}

/* 搜索框 / 文本输入 —— 内凹半透明 */
QLineEdit {{
    color: {TXT}; background: {INPUT}; border: 1px solid {BORDER_LO};
    border-radius: 8px; padding: 7px 12px; font-size: 12px;
}}
QLineEdit:hover {{ border-color: {BORDER}; }}
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

/* 左侧任务列表 —— 每项带半透明玻璃卡片底; 文字靠内层透明 widget 显示, 不遮挡玻璃 */
QListWidget#tasks {{ background: transparent; border: none; outline: none; }}
QListWidget#tasks::item {{
    background: {GLASS}; border: 1px solid {BORDER_LO}; border-radius: 9px;
    margin: 2px 4px; padding: 8px; color: {TXT};
}}
QListWidget#tasks::item:hover {{ background: {GLASS_HI}; border-color: {BORDER}; }}
QListWidget#tasks::item:selected {{
    background: {SELTINT}; border: 1px solid {BORDER};
}}

/* 滚动条 */
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{
    background: {BORDER_LO}; border-radius: 4px; min-height: 30px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

/* 玻璃分组卡片 */
QFrame.card {{ background: {GLASS}; border: 1px solid {BORDER_LO}; border-radius: 12px; }}
QFrame.subcard {{ background: {GLASS}; border: 1px solid {BORDER_LO}; border-radius: 10px; }}
"""


# ---------------------------------------------------------------- 工具
def glass_shadow(widget, radius=24, alpha=70, dy=6, blur=30):
    """给卡片/容器加柔和阴影, 营造浮起玻璃感"""
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(blur)
    eff.setOffset(0, dy)
    eff.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(eff)
    return eff
def mk_lbl(text, color=TXT, size=12, bold=False, wrap=False):
    l = QLabel(text)
    l.setStyleSheet(f"color:{color}; font-size:{size}px;"
                    f"{'font-weight:600;' if bold else ''}"
                    f"{'' if not wrap else ''}")
    if wrap:
        l.setWordWrap(True)
    return l


def circle_avatar(diameter=40, color1=AVATAR_C1, color2=AVATAR_C2, glyph=""):
    """渐变圆形头像(默认用调色板的紫/品红渐变)"""
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
            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(6, 0, 6, 0); h.setSpacing(8)
            # 关键: 让内层 widget 完全透明, 背景交给 item 的 QSS 控制(默认透明)
            w.setAttribute(Qt.WA_TranslucentBackground, True)
            w.setStyleSheet("background: transparent;")
            dot = QLabel("✓" if done else "●")
            dot.setStyleSheet(
                f"color:{DONE_COLOR if done else BUSY_COLOR};font-size:11px;font-weight:700;")
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
            f"background:{GLASS_HI};border:1px solid {BORDER_LO};border-radius:14px;")
        glass_shadow(self, radius=24, alpha=80, dy=6, blur=30)
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
        top = QHBoxLayout(); top.setSpacing(12)
        proj = QLabel("km-pipeline"); proj.setStyleSheet(
            f"color:{TXT};font-size:12px;font-weight:600;")
        top.addWidget(proj)
        top.addSpacing(6)
        mid = QLabel("537   🎤   ✦"); mid.setStyleSheet(
            f"color:{TXT3};font-size:12px;")
        top.addWidget(mid)
        top.addStretch()

        # 顶部标签页 —— 放进半透明玻璃容器
        tabbar = QFrame(); tabbar.setObjectName("tabBar")
        tb_layout = QHBoxLayout(tabbar); tb_layout.setContentsMargins(4, 3, 4, 3)
        tb_layout.setSpacing(4)
        for t in ["编辑器", "MCP", "插件市场", "设置", "+"]:
            tb = QPushButton(t)
            tb.setProperty("tab", True); tb.setCheckable(True)
            tb.setCursor(Qt.PointingHandCursor)
            if t == "设置":
                tb.setChecked(True)
            tb_layout.addWidget(tb)
        glass_shadow(tabbar, radius=20, alpha=80, dy=5, blur=24)
        top.addWidget(tabbar)
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
        # 用户卡(半透明玻璃)
        usercard = QFrame(); usercard.setObjectName("subcard")
        usercard.setStyleSheet(
            f"background:{GLASS}; border:1px solid {BORDER_LO}; border-radius:12px;")
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
        glass_shadow(usercard, radius=18, alpha=60, dy=3, blur=22)
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

        # 基础设置 卡片(半透明玻璃)
        basic = QFrame(); basic.setProperty("card", True)
        basic.setStyleSheet("QFrame[card=\"true\"]{"
                            f"background:{GLASS}; border:1px solid {BORDER_LO}; border-radius:12px;}}")
        glass_shadow(basic, radius=20, alpha=70, dy=5, blur=26)
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

        # 偏好设置(半透明玻璃)
        pref = QFrame()
        pref.setStyleSheet("QFrame[card=\"true\"]{"
                           f"background:{GLASS}; border:1px solid {BORDER_LO}; border-radius:12px;}}")
        pref.setProperty("card", True)
        glass_shadow(pref, radius=20, alpha=70, dy=5, blur=26)
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
                sep.setStyleSheet(f"background:{BORDER_LO};")
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

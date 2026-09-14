# Launcher 现代 UI 组件集成说明

本文档用于将 `dayu_widgets3` 的现代图标网格和图标菜单接入 AYON launcher。
本次组件已经完成，launcher 侧只需要替换视图和菜单实现，不需要修改应用数据模型。

## 新增组件

### `MBigView` launcher tile 模式

`MBigView` 仍然是 `QListView.IconMode`，新增了稳定的 tile 尺寸和 launcher 样式：

```python
from qtpy import QtCore
from dayu_widgets import MBigView

view = MBigView().launcher().set_item_size(112, 104)
view.setIconSize(QtCore.QSize(48, 48))
```

新增 API：

| API | 作用 |
| --- | --- |
| `launcher()` | 启用现代 launcher tile 样式 |
| `set_tile_style("launcher")` | 与 `launcher()` 等价 |
| `set_item_size(width, height)` | 设置固定网格单元尺寸，避免文字变化导致布局跳动 |
| `get_item_size()` | 返回当前 `QSize` 网格单元尺寸 |

样式状态：

- 默认：透明、低对比度
- hover：`@surface_hover_color`
- selected：`@surface_selected_color` + 主题色边框
- 图标建议使用 40~48px

使用 `MItemViewSet` 时，可以通过内部 view 配置：

```python
from dayu_widgets import MItemViewSet

view_set = MItemViewSet(view_type=MItemViewSet.BigViewType)
view_set.item_view.launcher().set_item_size(112, 104)
view_set.item_view.setIconSize(QtCore.QSize(48, 48))
```

launcher 现有的 `MTableModel`、`MSortFilterModel`、header list 和数据字典可以继续使用。

## `MIconMenu` 纵向图标菜单

适合需要图标、主标题和辅助说明的纵向弹出菜单：

```python
from dayu_widgets import MIconMenu

menu = MIconMenu(parent=button, exclusive=True)
menu.add_item(
    "2026",
    icon=MIcon("app-maya.png"),
    description="Recommended",
    checked=True,
    data=variant,
)
menu.add_item(
    "2025",
    icon=MIcon("app-maya.png"),
    description="Stable",
    data=variant,
)
```

通过信号获取选择结果：

```python
def on_item_triggered(action):
    variant = action.data()
    select_variant(variant)

menu.sig_item_triggered.connect(on_item_triggered)
```

参数说明：

- `text`：主标题
- `icon`：`QIcon`，推荐传入 `MIcon(...)`
- `description`：辅助说明，可为空
- `checked`：初始选中状态
- `data`：业务对象，使用 `action.data()` 取回
- `exclusive=True`：单选模式

## `MIconGridMenu` 横向换行菜单

截图中的 Maya 版本菜单推荐使用此组件。它不是普通纵向 `QMenu`，而是将图标项目放入网格容器，按列数自动换行：

```python
from dayu_widgets import MIconGridMenu

menu = MIconGridMenu(parent=button, columns=4)
for variant in variants:
    menu.add_item(
        text=variant.version,
        icon=MIcon("app-maya.png"),
        description=variant.description,
        checked=variant is selected_variant,
        data=variant,
    )

menu.sig_item_triggered.connect(on_item_triggered)
button.setMenu(menu)
button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
```

`columns=4` 且有 5 个版本时，会显示为第一行 4 项、第二行 1 项。
项目尺寸和布局由组件内部控制，默认适合 40px 图标和两行文字。

选择结果：

```python
def on_item_triggered(action):
    selected_variant = action.data()
    update_selected_variant(selected_variant)
```

## 替换 launcher 当前 Maya 菜单

当前 launcher 中的实现类似：

```python
menu = QtWidgets.QMenu(self)
menu.setIconSize(QtCore.QSize(32, 32))
for variant in variants:
    action = menu.addAction(...)
    action.setIcon(...)
```

建议替换为：

```python
menu = MIconGridMenu(parent=self, columns=4)
for variant in variants:
    menu.add_item(
        text=variant.version or variant.label or "Maya",
        icon=_icon_for_host("maya"),
        description=variant.description or "",
        checked=variant is selected,
        data=variant,
    )
menu.sig_item_triggered.connect(
    lambda action: self._select_maya_variant_by_data(action.data())
)
```

不要再调用：

```python
menu.setIconSize(...)
```

PySide6 的 `QMenu` 没有这个方法。`MIconMenu` 和 `MIconGridMenu` 会在自身的菜单项布局中控制图标尺寸，因此不依赖该 API。

## 迁移注意事项

1. 不要修改 `ApplicationDef`、数据加载和过滤逻辑。
2. `_MayaVersionDelegate` 只负责应用网格中的下拉标记，版本弹出菜单可以单独迁移到 `MIconGridMenu`。
3. `MIconGridMenu` 的 `action.data()` 返回传入的业务对象，建议直接传入 `ApplicationDef`。
4. `MIconGridMenu` 当前每次点击项目后自动关闭菜单，并将选中状态切换到当前项目。
5. `MIconMenu` 适合纵向两行菜单；截图中的横向 4+1 布局应使用 `MIconGridMenu`。
6. 组件已在 PySide6 离屏环境验证，launcher 可继续使用自己的图标注册逻辑和 `CUSTOM_STATIC_FOLDERS`。

## 示例位置

- `examples/item_view_big_type_example.py`：launcher tile 模式
- `examples/icon_menu_example.py`：纵向图标菜单和横向换行图标菜单

本次 dayu_widgets 改动未修改 AYON launcher 工程，launcher agent 可以按本文档独立完成接入。

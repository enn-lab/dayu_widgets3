# 现代主题升级计划

## 目标

dayu_widgets 将逐步升级为现代化的深色工作台风格，视觉参考 `reference/pyside6_solo_demo.py`，但不直接复制测试脚本中的页面级 QSS。

主题目标如下：

- 使用深色画布、分层表面和低对比度边框
- 使用薄荷绿作为默认现代主题强调色
- 统一按钮、输入框、菜单、列表、Tab 和侧栏的交互状态
- 保持现有 `dayu_theme`、`dayu_type`、`dayu_size` API 兼容
- 同时支持现代深色主题和现代浅色主题
- 为主题切换建立组件展示页和截图回归

## 完成状态

截至当前现代主题分支，阶段一至阶段三的代码改造和静态回归检查已完成；阶段四的真实 Qt 渲染截图验收仍需在安装 PySide2/PySide6 的环境中执行。

## 已完成

第一阶段基础改造：

1. `MTheme` 增加语义颜色令牌，例如 `canvas_color`、`surface_color`、`text_primary_color`、`accent_color`。
2. 旧主题属性继续保留，并与新语义令牌同步。
3. 主题 JSON 加载同时兼容旧的 `dark`/`light` 结构和旧版嵌套 `color` 结构。
4. 新增 `modern_dark.json` 和 `modern_light.json`，默认强调色分别为薄荷绿和蓝色。
5. 基础 QSS 接入新的画布、表面、边框、文字和按钮状态令牌。
6. 数据视图、Header、Menu、Toast、Message、Drawer、Progress、Splitter、MenuTab 和 Dock 已接入现代语义令牌及交互状态。
7. 新增 `tests/test_modern_theme_static.py`，在无 Qt 运行时的环境中检查主题 JSON、QSS 组件覆盖范围和主题令牌引用。

使用方式：

```python
from dayu_widgets.theme import MTheme

theme = MTheme("modern_dark")
theme.apply(window)
```

展示页 `examples/modern_theme_example.py` 同时包含默认尺寸和小尺寸案例。小尺寸组件使用现有的链式 API：

```python
MPushButton("Small").small()
MLineEdit().small()
MComboBox().small()
MSwitch().small()
```

当前 `MCheckBox` 和 `MRadioButton` 尚未提供 `.small()` 链式方法，因此展示页暂不对它们伪造小尺寸 API。

## 实施阶段

### 阶段一：主题令牌和基础控件

范围：主题加载、颜色令牌、按钮、输入框、下拉框、SpinBox、CheckBox、RadioButton、Switch。

验收：普通、hover、pressed、focus、checked、disabled、error 状态完整，旧主题示例不回归。

### 阶段二：布局和导航组件

范围：Tab、LineTab、Sidebar、SidebarItem、Card、Form、Divider。

验收：可以组合出 SOLO demo 的侧栏、顶部导航和设置面板结构，间距、圆角和选中态一致。

### 阶段三：数据和浮层组件（代码已完成）

范围：Table、Tree、List、Menu、Toast、Message、Drawer、Popup、Dialog。

验收：浮层背景、选择态、滚动条和遮罩层在深色主题下没有系统白底或多余边框。

### 阶段四：展示页和视觉回归（待真实 Qt 环境）

新增 `examples/modern_theme_example.py`，覆盖基础公共组件和主要交互状态，并对 `modern_dark`、`modern_light`、旧 `dark`、旧 `light` 进行截图验证。

验收环境包括 PySide6、PySide2、Windows 原生窗口、高 DPI 和离屏渲染。当前提交只完成静态检查，不将未执行的截图渲染标记为通过。

## 兼容性约束

- 不删除旧主题属性。
- 不改变公共组件类名和 `dayu_size` 尺寸 API。
- 不把页面级半透明效果强制施加到所有控件。
- 动态绘制组件必须从当前 `dayu_widgets.dayu_theme` 读取颜色。
- 修改主题后必须运行单元测试，并进行真实 Qt 渲染验证。

## 当前限制

主题升级仍需要 Qt 运行时验证。若开发环境未安装 `qtpy` 和对应 Qt binding，只能完成静态检查，不能宣称截图和交互已经通过。建议下一步使用 `examples/modern_theme_example.py` 对现代深色主题逐组件截图，并与现有截图回归对比。

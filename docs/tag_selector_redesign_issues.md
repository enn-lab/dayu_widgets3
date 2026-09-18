# Tag selector 示例重设计任务卡

> 目标：重做 `examples/line_edit_example.py` 中的 tag 选择示例，解决当前占位文本、焦点光标、换行高度和多选交互不稳定的问题。

## 方案评估

### 推荐方案：可编辑输入框 + 多选菜单 + 三行 tag 流布局

组合现有 `MComboBox`、`MMenu(exclusive=False)`、`MTag` 和一个可复用的流式布局容器：

1. 输入框获得焦点或点击下拉按钮时，打开包含全部候选项的多选菜单。
2. 菜单项目使用复选状态，已选项目保持勾选；菜单选择变化同步为 tag。
3. 输入文字时过滤候选项，并保留键盘补全/回车选择能力。
4. tag 和输入编辑器位于同一容器，输入框永远排在最后。
5. 容器最多按三行计算高度；超过三行时保持可用高度，继续通过菜单管理已选内容。
6. 空输入时不隐藏或重绘占位文本，直接复用标准 `MLineEdit` 的焦点、文字和 placeholder 样式。

### 备选方案：`MTextEdit` + tag overlay

`MTextEdit` 能自然容纳三行内容，但它的文本编辑、光标、选区和补全 popup 需要额外同步，且 tag 不是文本内容，复制/删除语义容易混乱。因此只保留为后续扩展方向，不作为本次示例主实现。

## Issue #TAG-101：组件边界与公开 API

- [x] 设计 `MTagLineEdit` 的组件边界，明确 tag、编辑器、候选项和选中值的职责。
- [x] 提供设置候选项、读取已选值、添加/移除 tag 的 API。
- [ ] 保持 `MTag`、`MLineEdit`、`MComboBox` 和 `MMenu` 现有 API 兼容。
- [ ] 组件必须支持普通尺寸和 `.small()` 尺寸。

## Issue #TAG-102：多选菜单与搜索补全

- [x] 使用 `MMenu(exclusive=False)` 展示全部候选项和复选状态。
- [x] 点击/激活输入框时打开候选菜单；菜单选中状态同步到 tag。
- [x] 保留输入文字过滤和 `MCompleter` 键盘补全、回车确认、重复项保护。
- [x] 菜单选择与 tag、输入框文本同步，避免出现“tag + 残留文本”。

## Issue #TAG-103：三行 tag 布局与焦点样式

- [x] tag 与输入框使用同一个外层输入容器，输入框始终跟随最后一个 tag。
- [x] 标签数量增加时自动换行，默认最多展示三行，不横向撑开父组件。
- [x] 超过三行时保持固定高度，并继续通过菜单管理已选内容。
- [x] 聚焦/失焦、placeholder、光标、边框、背景与普通 `MLineEdit` 保持一致。
- [x] 删除 tag、窗口缩放、输入框重新获得焦点后布局稳定。

## Issue #TAG-104：示例、测试与文档

- [x] 在独立的 `tag_software_list_example.py` 展示点击打开全部选项、菜单搜索、多选、多个 tag 和换行。
- [x] 包含足够候选项，覆盖菜单滚动和重复选择场景。
- [x] 完成本地离屏行为验证：多选同步、输入清空、焦点、三行高度。
- [x] 记录推荐组合方式和 API 示例。

## Issue #TAG-105：独立验收

- [x] 对比普通 `MLineEdit`、可搜索 `MComboBox` 和新 tag selector 的视觉规则。
- [x] 验证激活输入框后完整候选列表可见，支持多选且复选状态正确。
- [x] 验证菜单选择、输入补全、删除 tag、重复项和焦点恢复。
- [x] 验证大量 tag 只占三行，不遮挡光标、不显示残留文本、不横向撑开父窗口。
- [x] 本地完成测试和截图验收，不等待 CI。

## Issue #TAG-106：交互回归修复（第二轮）

首轮实现把菜单当作第二个数据源，导致三个可用性缺陷。修复后 `MTagLineEdit`
的定位是**令牌编辑器**：tag 是组件内容，输入框只是跟在最后一个 tag 后面的光标，
菜单只是选择器。

- [x] **菜单每选一项就消失**：移除 `_suppress_menu_on_focus` / `_enable_menu_on_focus`
  这套焦点抑制逻辑，改为「选中项只增删一个 tag，菜单保持展开」，仅 `Esc`、
  焦点移出组件或点击外部才关闭。菜单勾选状态由 `_sync_menu()` 单向同步。
- [x] **重复激活才能继续选择**：`_open_menu()` / `popup()` / `hidePopup()` 提供显式
  开关；点击输入框区域可切换菜单，`Down` 键也可打开。
- [x] **点击 tag 关闭按钮无法移除**：`MTag.closeable()` 改为设置 `dayu_closeable`
  属性并由 `main.qss` 绘制，同时移除 `tag.py` 内所有 `setStyleSheet` 调用——
  控件级样式表优先级高于应用样式表，会把 tag 冻结在构造时的颜色上，
  导致后续 `dayu_theme.apply()` 或主题切换无法生效。
- [x] **提示文本样式多余**：删除 `MTag QLabel#tag_text` 与
  `MTag QToolButton#tag_close_button` 的 `color` / `padding` 规则，子控件继承
  tag 自身颜色，只保留 `:hover` 反馈；`MLineEdit#tag_line_edit_editor` 同样
  不再重复声明 `color` / `padding`。
- [x] **输入框可编辑**：去掉 `setReadOnly(True)`，支持输入过滤选项、`Enter`
  提交自定义项、`Backspace` 删除末项。
- [x] **高度不再冻结**：`_FlowLayout` 增加按宽度缓存的 `heightForWidth`（避免
  同一宽度下重复测量导致把 tag 误判到下一行），容器改用 `_apply_height()`
  在每次 resize 时按内容推导高度，构造期未布局（宽度 0/1）不会再定格出错误高度。
- [x] `property_mixin` 跳过动态属性的「清空」事件（值为 `None`），避免
  `setXxx` 连续触发两次回调时用过期值重建样式。
- [x] `MMenu` 新增 `set_search_text()` / `clear_search_text()`，让宿主输入框可以
  复用菜单的过滤能力。
- [x] `MTheme` 新增 `accent_8/12/20/35_color` 主题色衍生 tint 令牌。
- [x] 回归测试更新：`tests/test_modern_theme_static.py` 改为校验新契约（无控件级
  样式表、无冗余文本样式、菜单保持展开、高度推导），并新增 tag 样式表约束用例。

## Issue #TAG-107：第三轮交互回归修复

用户实际运行 `tag_software_list_example.py` 后发现第二轮修复遗漏了真实 GUI 下的
焦点/事件传递问题：

- [x] **点击输入框没有弹出菜单**：`QLineEdit` 自己消费了鼠标点击事件，
  `MTagLineEdit.mousePressEvent()` 从未被触发。修复：在 `eventFilter` 中监听
  编辑器 `MouseButtonPress`，直接切换菜单。
- [x] **输入文字没有弹出过滤菜单**：`_slot_text_changed` 用 `self.hasFocus()`
  判断，但焦点实际在内部 `QLineEdit` 上，容器 never 有焦点。修复：改为
  `self._editor.hasFocus()`。
- [x] **点击已有 tag 反而弹出菜单且无法连续勾选**：`MTag` 没有 `accept` 鼠标事件，
  点击 tag 会冒泡到父容器触发 `_open_menu()`，打开后又因为焦点异常导致菜单
  关闭。修复：`MTag.mousePressEvent` / `mouseReleaseEvent` 调用 `event.accept()`
  阻止冒泡。
- [x] **提示文本仍然样式过重**：虽然去掉了 `#tag_line_edit_editor` 的冗余
  `color` / `padding`，但 `MLineEdit` 通用规则仍把 placeholder 染成
  `text_primary_color`。修复：显式添加
  `MLineEdit#tag_line_edit_editor::placeholder { color: @text_tertiary_color; }`
  让提示文本保持低对比度，不再遮挡光标。
- [x] **closable tag 背景在 dark 主题下像“黑色”**：`accent_12_color` 在深色背景上
  几乎不可见。修复：closable tag 背景改用 `accent_20_color`，hover 用
  `accent_35_color`。
- [x] 新增回归测试覆盖：编辑器点击打开/关闭菜单、输入文字打开过滤菜单、
  点击 tag 不打开菜单。

## 执行顺序

`TAG-101` → `TAG-102` 与 `TAG-103` → `TAG-104` → `TAG-105` → `TAG-106` → `TAG-107`

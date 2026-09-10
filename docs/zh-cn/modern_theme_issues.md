# 现代 UI 主题改造任务卡

本文件是现代 UI 改造分支的本地 issue 看板。任务按依赖顺序排列，开发和验收均以本地结果为准，不等待 CI。

## 已完成

### THEME-001 默认现代暗色主题

- 状态：已完成
- 提交：`14090f1`
- 内容：默认 `dayu_theme` 切换为 `modern_dark`；增加现代深色/浅色主题文件；保留旧主题属性兼容。
- 验收：Python 语法、JSON、`git diff --check`。

### THEME-002 基础控件状态

- 状态：已完成
- 提交：`14090f1`
- 内容：按钮、输入框、SpinBox、ComboBox、CheckBox、RadioButton、Switch 接入现代语义令牌。
- 验收：静态 QSS 检查；Qt 运行时截图待环境依赖具备后执行。

### THEME-003 内容层和导航层

- 状态：已完成
- 提交：`f338461`
- 内容：Card、Meta、Tab、Sidebar、列表、表格、菜单和滚动条现代化。
- 验收：统一 surface、selected、hover、elevated 层级，移除旧的硬编码选择色。

### THEME-004 反馈与交互状态

- 状态：已完成
- 提交：`e92962c`
- 内容：Message、Drawer、Menu、Radio、Switch、Slider、Progress、Dock、拖拽按钮现代化。
- 验收：本地语法和差异检查通过。

## 待执行

### THEME-005 全组件 QSS 收口

- 状态：进行中
- 范围：Header、Table/Tree/List 细节、MenuTab、Splitter、Progress、Dock、Toast 和浮层的遗留旧令牌。
- 验收：`main.qss` 不再包含明显的旧硬编码颜色；所有新令牌可由 `MTheme` 提供。
- 交付：一个独立提交。

### THEME-006 主题回归测试

- 状态：待执行
- 范围：主题 JSON 解析、现代令牌存在性、旧属性兼容、QSS 模板可替换性。
- 验收：尽可能使用无 Qt 运行时依赖的测试；若环境具备 Qt，再增加组件实例化测试。
- 交付：测试文件和一个独立提交。

### THEME-007 主题展示与截图验收

- 状态：待执行
- 范围：`examples/modern_theme_example.py` 覆盖基础控件、Card、Tab、Sidebar、表格、菜单、反馈组件。
- 验收：`modern_dark`、`modern_light`、旧 `dark`、旧 `light` 四套主题的本地截图和人工对比。
- 说明：当前环境若缺少 `qtpy`/PySide6，只能先完成静态验收，不能宣称截图通过。

### THEME-008 文档与发布说明

- 状态：待执行
- 范围：主题使用方式、迁移说明、兼容性边界、示例运行命令和已知限制。
- 验收：中文导航可达，示例命令和主题名称与代码一致。

## 当前验收策略

开发完成后启动独立验收会话，检查：

1. Git 提交和工作区状态。
2. Python 语法、JSON、QSS 模板令牌和 `git diff --check`。
3. 可用时运行 pytest；不可用时记录缺少的依赖，不伪造通过结果。
4. 可用时运行 Qt demo 和截图；不可用时只报告静态验收结果。

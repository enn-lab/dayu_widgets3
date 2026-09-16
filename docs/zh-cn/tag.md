# MTag 标签

现代主题提供三种标签组件：

- `MTag`：分类、状态和可关闭标签。
- `MCheckableTag`：支持选中和取消选中的标签。
- `MNewTag`：点击后进入编辑状态，用于新增标签。

```python
from dayu_widgets import MCheckableTag, MNewTag, MTag

tag = MTag("Maya").coloring("#23d18b").closeable()
filled = MTag("Ready").coloring("#23d18b").no_border()
checkable = MCheckableTag("Production")
new_tag = MNewTag("Add tag")
new_tag.sig_add_tag.connect(print)
```

`MTag` 支持 `.clickable()` 和 `sig_clicked`，`.closeable()` 会显示关闭按钮并发送 `sig_closed`。`MCheckableTag` 使用现代表面、hover 背景和主题色选中态。`MNewTag.sig_add_tag` 在用户输入非空文本并按回车后发送。

完整示例见 `examples/tag_example.py`。

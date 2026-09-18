"""Tokenized line edit with inline tags.

``MTagLineEdit`` is a *token editor*: tags are the editor's own content, the
line edit is only the caret that lives after the last tag.  The companion
``MMenu`` is a picker, not a second source of truth:

* typing in the editor filters the popup and ``Enter`` commits a free token;
* picking a menu item adds/removes one token and **keeps the popup open**;
* clicking the container (or pressing ``Down`` / ``Alt+Down``) opens the
  popup again, and it only ever closes on ``Esc``, another widget taking
  focus, or the user clicking outside.
"""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.menu import MMenu
from dayu_widgets.tag import MTag


class _FlowLayout(QtWidgets.QLayout):
    """Left-to-right layout that wraps into new rows."""

    def __init__(self, parent=None, margin=0, spacing=4):
        super(_FlowLayout, self).__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing
        self._items = []
        self._dirty = True
        self._cached_width = -1
        self._cached_height = 0

    def addItem(self, item):
        self._items.append(item)
        self._invalidate()

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            self._invalidate()
            return self._items.pop(index)
        return None

    def invalidate(self):
        self._invalidate()
        super(_FlowLayout, self).invalidate()

    def _invalidate(self):
        self._dirty = True
        self._cached_width = -1

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation.Horizontal)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        # ``_do_layout`` measures real geometries, so it must not run twice for
        # the same width while nothing changed.  The container asks for a
        # height on every sync and the layout engine asks again on every
        # relayout; without this cache a tag could be measured after it was
        # already positioned on the previous row, which reported an extra row.
        if not self._dirty and width == self._cached_width:
            return self._cached_height
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        self._cached_width = width
        self._cached_height = height
        self._dirty = False
        return height

    def setGeometry(self, rect):
        super(_FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        margins = self.contentsMargins()
        effective = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        x = effective.x()
        y = effective.y()
        line_height = 0
        for item in self._items:
            item_size = self._measure(item)
            next_x = x + item_size.width() + self._spacing
            if next_x - self._spacing > effective.right() and line_height:
                x = effective.x()
                y += line_height + self._spacing
                next_x = x + item_size.width() + self._spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item_size))
            x = next_x
            line_height = max(line_height, item_size.height())
        return y + line_height - rect.y() + margins.bottom()

    @staticmethod
    def _measure(item):
        size = item.sizeHint()
        widget = item.widget()
        if widget is not None:
            width = max(size.width(), widget.minimumSizeHint().width())
            size = QtCore.QSize(width, size.height())
        return size


class MTagLineEdit(QtWidgets.QWidget):
    """An inline token editor that keeps the input after all tags."""

    sig_tag_added = QtCore.Signal(str)
    sig_tag_removed = QtCore.Signal(str)
    sig_value_changed = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(MTagLineEdit, self).__init__(parent)
        self.setObjectName("tag_line_edit")
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self._tags = []
        self._options = []
        self._menu = None
        self._max_rows = 3
        # The editor is the only focusable child.  ``_syncing_focus`` marks the
        # short window in which we move focus to it on purpose so the editor
        # does not treat its own FocusOut as "user left the widget".
        self._syncing_focus = False
        # ``_menu_dispatching`` covers the reentrant Leave that ``popup()`` can
        # deliver while the popup window is still being mapped.
        self._menu_dispatching = False
        self._pointer_over_popup = False
        self._menu_show_timer = QtCore.QTimer(self)
        self._menu_show_timer.setSingleShot(True)
        self._menu_show_timer.timeout.connect(self._show_menu)
        self._layout = _FlowLayout(self, spacing=4)
        self._editor = MLineEdit().small()
        self._editor.setObjectName("tag_line_edit_editor")
        self._editor.setFrame(False)
        self._editor.setMinimumWidth(76)
        self._editor.installEventFilter(self)
        self._editor.textChanged.connect(self._slot_text_changed)
        self._layout.addWidget(self._editor)
        self._apply_editor_width()

    # ------------------------------------------------------------------ API

    @property
    def line_edit(self):
        """The inner :class:`~dayu_widgets.line_edit.MLineEdit`."""
        return self._editor

    def tags(self):
        """Return the current tags in display order."""
        return tuple(self._tags)

    def set_options(self, options):
        """Set the candidate values used by the picker popup.

        :param options: list of str, or list of dict with
            ``value`` / ``label`` / ``icon`` keys.
        :return: self
        """
        self._options = list(options or [])
        self._menu = MMenu(exclusive=False, parent=self)
        self._menu.setProperty("keep_open", True)
        self._menu.set_data([self._normalize_option(item) for item in self._options])
        self._menu.sig_value_changed.connect(self._slot_menu_value_changed)
        self._menu.installEventFilter(self)
        if self._editor.text():
            self._filter_menu(self._editor.text())
        return self

    def selected_values(self):
        """Return the ``value`` of every selected tag."""
        return [tag.property("dayu_value") for tag in self._tags]

    def text(self):
        """Return the current uncommitted editor text."""
        return self._editor.text()

    def set_max_rows(self, rows):
        """Limit how many tag rows are visible before the height is capped."""
        self._max_rows = max(1, int(rows))
        self._refresh_layout()
        return self

    def clear(self):
        """Remove every tag and clear the editor."""
        for tag in tuple(self._tags):
            self._detach_tag(tag)
        self._editor.clear()
        self._sync_menu()
        self._refresh_layout()
        self.sig_value_changed.emit([])
        return self

    def add_tag(self, value, label=None):
        """Select one value programmatically."""
        item = self._option_for(value)
        value = item.get("value", value)
        label = label or item.get("label", value)
        if any(tag.property("dayu_value") == value for tag in self._tags):
            return self
        self._insert_tag(value, label, item.get("icon"))
        self._sync_menu()
        self._refresh_layout()
        self.sig_tag_added.emit(value)
        self.sig_value_changed.emit(self.selected_values())
        return self

    def remove_tag(self, tag):
        """Deselect the tag instance returned by :meth:`tags`."""
        if tag not in self._tags:
            return self
        value = tag.property("dayu_value")
        self._detach_tag(tag)
        self._sync_menu()
        self._refresh_layout()
        self.sig_tag_removed.emit(value)
        self.sig_value_changed.emit(self.selected_values())
        return self

    def toggle_value(self, value):
        """Add the value when it is missing, otherwise remove its tag."""
        for tag in self._tags:
            if tag.property("dayu_value") == value:
                return self.remove_tag(tag)
        return self.add_tag(value)

    def set_value(self, values):
        """Replace the whole selection with ``values``."""
        values = list(values or []) if isinstance(values, (list, tuple, set)) else [values]
        wanted = []
        for value in values:
            item = self._option_for(value)
            wanted.append((item.get("value", value), item.get("label", value), item.get("icon")))
        for tag in tuple(self._tags):
            if tag.property("dayu_value") not in [item[0] for item in wanted]:
                self._detach_tag(tag)
        for value, label, icon in wanted:
            if not any(tag.property("dayu_value") == value for tag in self._tags):
                self._insert_tag(value, label, icon)
        self._editor.clear()
        self._sync_menu()
        self._refresh_layout()
        self.sig_value_changed.emit(self.selected_values())
        return self

    # ------------------------------------------------------- option helpers

    @staticmethod
    def _normalize_option(item):
        if isinstance(item, dict):
            label = item.get("label", item.get("value", ""))
            data = dict(item)
            data.setdefault("value", label)
            data.setdefault("label", label)
            return data
        return {"value": item, "label": str(item)}

    def _option_for(self, value):
        for item in self._options:
            normalized = self._normalize_option(item)
            if normalized["value"] == value:
                return normalized
        return {}

    # -------------------------------------------------------------- editing

    def _insert_tag(self, value, label, icon=None):
        tag = MTag(str(label)).closeable()
        tag.setProperty("dayu_value", value)
        if icon:
            tag.setIcon(icon)
        tag.sig_closed.connect(lambda current=tag: self.remove_tag(current))
        self._tags.append(tag)
        editor_item = self._layout.takeAt(self._layout.count() - 1)
        self._layout.addWidget(tag)
        self._layout.addItem(editor_item)
        self._layout._invalidate()

    def _detach_tag(self, tag):
        self._tags.remove(tag)
        self._layout.removeWidget(tag)
        tag.setParent(None)
        tag.deleteLater()
        self._layout._invalidate()

    def _commit_editor_text(self):
        """Commit the editor text: a matching option if there is one, else a
        free token.  Returns True when the editor content was consumed."""
        text = self._editor.text().strip()
        if not text:
            return False
        lowered = text.lower()
        item = self._option_for(text)
        if not item:
            for candidate in self._options:
                normalized = self._normalize_option(candidate)
                if lowered in str(normalized["label"]).lower():
                    item = normalized
                    break
        value = item.get("value", text)
        if any(tag.property("dayu_value") == value for tag in self._tags):
            self._editor.clear()
            return False
        self._editor.clear()
        self.add_tag(value, item.get("label", text))
        return True

    def _filter_menu(self, text):
        """Mirror the editor text into the popup as a row filter."""
        if self._menu is None:
            return
        if text:
            self._menu.set_search_text(text)
        else:
            self._menu.clear_search_text()

    # ------------------------------------------------------------ menu glue

    def _sync_menu(self):
        """Push the current selection back into the popup check states."""
        if self._menu is not None:
            self._menu.set_value(self.selected_values())

    def _slot_menu_value_changed(self, values):
        """Handle a checkbox toggle coming from the popup.

        The popup stays open on purpose: picking several entries in a row must
        not require re-focusing the container for every single one.
        """
        values = list(values) if isinstance(values, (list, tuple)) else [values]
        for tag in tuple(self._tags):
            if tag.property("dayu_value") not in values:
                value = tag.property("dayu_value")
                self._detach_tag(tag)
                self.sig_tag_removed.emit(value)
        for value in values:
            if any(tag.property("dayu_value") == value for tag in self._tags):
                continue
            item = self._option_for(value)
            self._insert_tag(value, item.get("label", value), item.get("icon"))
            self.sig_tag_added.emit(value)
        self._editor.clear()
        self._refresh_layout()
        self.sig_value_changed.emit(self.selected_values())

    def _open_menu(self):
        if self._menu is None or not self.isEnabled():
            return
        self._sync_menu()
        self._filter_menu(self._editor.text())
        # ``popup()`` can dispatch a Leave to this filter while the window is
        # still being mapped under the parked cursor.  Retire the auto-hide
        # during the call, and let the pointer decide from the next move on.
        self._menu_dispatching = True
        try:
            self._menu.popup(self._popup_position())
        finally:
            self._menu_dispatching = False

    def _show_menu(self):
        self._open_menu()

    def _close_menu(self):
        self._menu_show_timer.stop()
        if self._menu is not None and self._menu.isVisible():
            self._menu.hide()

    def _popup_position(self):
        return self.mapToGlobal(QtCore.QPoint(0, self.height()))

    @QtCore.Slot(str)
    def _slot_text_changed(self, text):
        self._filter_menu(text)
        self._refresh_layout()
        if self._menu is not None and not self._menu.isVisible() and self._editor.hasFocus():
            self._menu_show_timer.start(0)

    def popup(self):
        """Open the picker popup below the container."""
        self._open_menu()

    def hidePopup(self):
        """Close the picker popup without changing the selection."""
        self._close_menu()

    # ----------------------------------------------------------- mouse view

    def mousePressEvent(self, event):
        if self._menu is not None and event.button() == QtCore.Qt.LeftButton:
            if self._editor.geometry().contains(event.pos()):
                # Clicking the caret area toggles the popup, ``Esc`` closes it.
                if self._menu.isVisible():
                    self._close_menu()
                else:
                    self._open_menu()
            else:
                self._editor.setFocus(QtCore.Qt.MouseFocusReason)
                self._open_menu()
            event.accept()
            return
        super(MTagLineEdit, self).mousePressEvent(event)

    def focusInEvent(self, event):
        super(MTagLineEdit, self).focusInEvent(event)
        self._move_focus_into_editor()

    def _move_focus_into_editor(self):
        self._syncing_focus = True
        try:
            self._editor.setFocus(QtCore.Qt.OtherFocusReason)
        finally:
            self._syncing_focus = False

    def _apply_focus_style(self, focused):
        self.setProperty("dayu_tag_line_focus", focused)
        self.style().polish(self)

    def eventFilter(self, watched, event):
        if watched is self._menu:
            return self._filter_menu_event(event)
        if watched is self._editor:
            if event.type() == QtCore.QEvent.FocusIn:
                self._apply_focus_style(True)
            elif event.type() == QtCore.QEvent.FocusOut:
                # ``popup()`` moves focus to the popup window, which surfaces
                # here as a FocusOut on the editor.  That is a transfer *inside*
                # the component, not the user leaving it, so the drop-down must
                # survive it.
                if self._menu_dispatching:
                    return False
                if not self._syncing_focus and not self._pointer_inside_interaction():
                    self._apply_focus_style(False)
                    self._close_menu()
            elif event.type() == QtCore.QEvent.KeyPress:
                return self._handle_editor_key(event)
            elif event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease):
                if event.button() == QtCore.Qt.LeftButton and self._menu is not None:
                    # The editor consumes mouse events itself, so the container
                    # mousePressEvent never runs for clicks inside the caret.
                    # Still, clicking the caret should toggle the picker.
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        if self._menu.isVisible():
                            self._close_menu()
                        else:
                            self._open_menu()
        return super(MTagLineEdit, self).eventFilter(watched, event)

    def _filter_menu_event(self, event):
        """Auto-close the popup once the pointer genuinely leaves the widget.

        Hiding purely on ``Leave`` is wrong: the popup is a separate window, so
        the pointer is "outside" it as soon as the selection grows tall enough
        to push the cursor off the first row.  The pointer position is the
        authority, and both the popup and the container count as inside.
        """
        if event.type() == QtCore.QEvent.MouseMove:
            self._pointer_over_popup = True
        elif event.type() == QtCore.QEvent.Leave:
            if self._menu_dispatching:
                return False
            if self._menu.underMouse():
                return False
            self._pointer_over_popup = False
            if not self._pointer_inside_interaction():
                self._close_menu()
        return False

    def _point_inside(self, rect):
        pos = self.mapFromGlobal(QtGui.QCursor.pos())
        return rect.contains(pos)

    def _pointer_inside_interaction(self):
        """Return whether the pointer remains in the selector interaction.

        ``MMenu.search_popup`` is a second popup window owned by the menu.
        Treating it as outside the selector caused the main menu to disappear
        as soon as the pointer moved from the tag editor to menu search.
        """
        if self._point_inside(self.rect()):
            return True
        if self._menu is not None:
            if self._widget_contains_pointer(self._menu):
                return True
            search_popup = self._menu.search_popup
            if self._widget_contains_pointer(search_popup):
                return True
        return False

    @staticmethod
    def _widget_contains_pointer(widget):
        if not widget.isVisible():
            return False
        return widget.rect().contains(widget.mapFromGlobal(QtGui.QCursor.pos()))

    def _handle_editor_key(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            if self._menu is not None and self._menu.isVisible():
                self._close_menu()
            else:
                self._editor.clear()
            return True
        if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            if self._commit_editor_text():
                self._filter_menu("")
            return True
        if key == QtCore.Qt.Key_Backspace and not self._editor.text() and self._tags:
            self.remove_tag(self._tags[-1])
            return True
        if key == QtCore.Qt.Key_Down and (self._menu is None or not self._menu.isVisible()):
            self._open_menu()
            return True
        return False

    # ----------------------------------------------------------- layout glue

    def _apply_editor_width(self):
        """Size the caret: fill the free space, or hug its own text."""
        text = self._editor.text()
        if self._tags and text:
            width = max(48, self._editor.fontMetrics().horizontalAdvance(text) + 16)
        else:
            width = max(self._editor.minimumWidth(), self.width() - 8)
        if width != self._editor.width():
            self._layout._invalidate()
            self._editor.setFixedWidth(width)

    def _refresh_layout(self):
        self._layout.invalidate()
        self._apply_editor_width()
        self._apply_height()

    def _apply_height(self):
        """Grow the container to fit its tags, never beyond ``_max_rows``.

        The height is *derived* on every resize instead of frozen into a
        ``setFixedHeight`` value: freezing it while the widget is still
        unlaid-out (width 0/1 during construction) would clamp the container
        to a nonsense height that survives into the real layout.
        """
        width = self.width()
        natural = self._layout.heightForWidth(width) if width > 1 else 0
        row_height = self._editor.sizeHint().height() + self._layout._spacing
        row_height = max(self._layout._spacing + self._editor.minimumSizeHint().height(), row_height)
        cap = row_height * self._max_rows
        height = max(min(natural, cap), self._layout._spacing + self._editor.minimumSizeHint().height())
        if height != self.minimumHeight() or height != self.maximumHeight():
            self.setFixedHeight(height)

    def sizeHint(self):
        width = max(320, self._layout.minimumSize().width())
        return QtCore.QSize(width, self.heightForWidth(width))

    def minimumSizeHint(self):
        width = max(160, self._layout.minimumSize().width())
        return QtCore.QSize(width, self._layout._spacing + self._editor.minimumSizeHint().height())

    def heightForWidth(self, width):
        return self._layout.heightForWidth(width)

    def hasHeightForWidth(self):
        return True

    def resizeEvent(self, event):
        super(MTagLineEdit, self).resizeEvent(event)
        self._layout.invalidate()
        self._apply_editor_width()
        self._apply_height()

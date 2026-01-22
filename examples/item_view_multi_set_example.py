# Import third-party modules
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import utils
from dayu_widgets.divider import MDivider
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.item_view_multi_set import MItemViewMultiSet
from dayu_widgets.push_button import MPushButton
import _mock_data as mock

@utils.add_settings("DaYu", "DaYuExample", event_name="hideEvent")
class ItemViewFullSetExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(ItemViewFullSetExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.header_list = mock.header_list
        # self.data_list = mock.tree_data_list
        self.data_list = mock.data_list

        item_view_multi_set_all = MItemViewMultiSet(
            table_view=True,
            big_view=True,
            tree_view=True,
            list_view=True
        )
        item_view_multi_set_all.set_header_list(self.header_list)
        item_view_multi_set_all.searchable().groupable()

        refresh_button = MPushButton("Refresh Data")
        refresh_button.clicked.connect(self.slot_update_data)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Only Table View"))
        main_lay.addWidget(refresh_button)
        # main_lay.addWidget(item_view_set_table)
        main_lay.addWidget(MDivider("All Views (Table, Tree, List, Big)"))
        main_lay.addWidget(item_view_multi_set_all)
        self.setLayout(main_lay)

        self.view = item_view_multi_set_all
        self.slot_update_data()

    def slot_update_data(self):
        self.view.setup_data(self.data_list)


if __name__ == "__main__":
    # Import local modules
    from dayu_widgets import dayu_theme
    from dayu_widgets.qt import application

    with application() as app:
        test = ItemViewFullSetExample()
        dayu_theme.apply(test)
        test.show()

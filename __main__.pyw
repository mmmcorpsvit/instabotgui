import logging
# from inspect import Parameter
from copy import deepcopy
from inspect import Parameter

from core import log_handle
from core.bot import get_actions_list, ACTIONS_LIST, InstaPyStartStageItem, InstaPyEndStageItem, insta_clone

from PyQt5.QtWidgets import QTreeView, QVBoxLayout, \
    QApplication, QListWidget, QMainWindow, QPlainTextEdit, QPushButton
from PyQt5.uic import loadUi  # noqa

from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree import Parameter as ParameterForTree
from pyqtgraph.Qt import QtCore, QtGui

app = QtGui.QApplication([])  # noqa

# stages = []


class Ui(QMainWindow):
    new_button: QPushButton = None

    load_button: QPushButton = None
    save_Button: QPushButton = None
    run_button: QPushButton = None

    actions_list: QListWidget = None
    stages_list: QListWidget = None

    properties_tree: QTreeView = None

    log_textEdit: QPlainTextEdit = None

    current_stage = None

    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        loadUi('gui.ui', self)  # Load the .ui file

        self.new_button = self.findChild(QPushButton, 'NewButton')  # noqa
        self.load_button = self.findChild(QPushButton, 'LoadButton')  # noqa
        self.load_button.setVisible(False)
        self.save_Button = self.findChild(QPushButton, 'SaveButton')  # noqa
        self.save_Button.setVisible(False)
        self.run_button = self.findChild(QPushButton, 'RunButton')  # noqa

        self.actions_list = self.findChild(QListWidget, 'actions_list')  # noqa
        self.stages_list = self.findChild(QListWidget, 'stages_list')  # noqa

        # --------------------------------
        self.properties_tree = ParameterTree()
        # self.properties_tree.setParameters(self.findChild(QVBoxLayout, 'verticalLayout_3'), showTop=False)
        self.findChild(QVBoxLayout, 'verticalLayout_3').addWidget(self.properties_tree)

        # verticalLayout_3

        # --------------------------------
        # self.properties_tree = self.findChild(QTreeView, 'properties_tree')  # noqa
        # self.properties_tree.setModel(QStandardItemModel())
        # self.properties_tree.setAlternatingRowColors(True)
        # self.properties_tree.setSortingEnabled(True)
        # self.properties_tree.setHeaderHidden(False)
        # self.properties_tree.setSelectionBehavior(QAbstractItemView.SelectItems)
        # self.properties_tree.model().setHorizontalHeaderLabels(['Parameter', 'Value'])

        self.log_textEdit = self.findChild(QPlainTextEdit, 'log_textEdit')  # noqa
        # self.log_textEdit.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # logging.getLogger().addHandler(self.log_textEdit)
        # You can control the logging level
        # logging.getLogger().setLevel(logging.DEBUG)
        self.setup_logger(self.log_textEdit)

        # ---------------------------- events ---------------------------
        self.new_button.clicked.connect(self.new_buttonClicked)
        self.load_button.clicked.connect(self.loadButtonClicked)
        self.run_button.clicked.connect(self.RunButtonClicked)

        self.actions_list.addItems(get_actions_list())
        self.actions_list.doubleClicked.connect(self.actions_listDoubleClicked)

        self.stages_list.doubleClicked.connect(self.stages_listDoubleClicked)
        self.stages_list.itemSelectionChanged.connect(self.stages_listitemSelectionChanged)

        # if not file load:
        self.new_buttonClicked()
        # self.show()  # Show the GUI

    def setup_logger(self, log_text_box):
        handler = log_handle.Handler(self)
        # log_text_box = QPlainTextEdit(self)
        # self.main_layout.addWidget(log_text_box)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
        handler.new_record.connect(log_text_box.appendPlainText)  #

    def new_buttonClicked(self):
        self.stages_list.clear()
        self.stages_list.addItem(insta_clone(InstaPyStartStageItem))
        self.stages_list.addItem(insta_clone(InstaPyEndStageItem))
        self.stages_list.setCurrentRow(0)
        self.actions_list.setCurrentRow(0)
        self.log_textEdit.clear()
        logging.info('Welcome to InstaBot v0.1')
        pass

    def RunButtonClicked(self, qmodelindex):  # noqa
        logging.info('Start working')
        # --------------------------------------------

        y = [self.stages_list[x].object for x in self.stages_list.count()]
        stages = deepcopy(y)
        pass


        # --------------------------------------------
        logging.info('End working')
        pass

    def loadButtonClicked(self, qmodelindex):  # noqa
        # This is executed when the button is pressed
        logging.info('printButtonPressed')

    # ------------------------------------------------------
    def actions_listDoubleClicked(self, qmodelindex):  # noqa
        # add new action to stages list
        index = self.actions_list.currentRow()
        _new_object = insta_clone(ACTIONS_LIST[index])

        self.stages_list.insertItem(self.stages_list.count() - 1, _new_object)
        pass

    def stages_listDoubleClicked(self, qmodelindex):  # noqa
        # remove action from stages list
        index = self.stages_list.currentRow()
        item = self.stages_list.item(index)

        if item.object.name in ['__init__', 'end']:
            logging.error(f'You cannot remove stage: {item.object.name}')
            return None
        self.stages_list.takeItem(index)
        pass

    def stages_listitemSelectionChanged(self):
        # render new propertry list table
        index = self.stages_list.currentRow()
        private_data = self.stages_list.item(index).object.anotation_call
        private_values_list = self.stages_list.item(index).object.values

        params_list = []
        for x in private_data:
            el = private_data[x]
            if el.name == 'self':
                continue
            new_el = {'name': el.name, 'default': el.default}

            if el.annotation.__name__ not in ['_empty']:
                new_el['type'] = el.annotation.__name__
            else:
                pass

            # set value from stored in Item-object list
            if el.name in private_values_list:
                new_el['value'] = private_values_list[el.name]

            if hasattr(el, 'value'):
                new_el['value'] = getattr(el, 'value')

            params_list.append(new_el)

        self.current_stage = [
            {'name': 'Basic parameter data types', 'type': 'group', 'children':
                params_list
             }]

        # params = data

        # p = ParameterForTree.create(name='params', type='group', children=self.current_stage)
        p = ParameterForTree.create(name='params', type='list', children=self.current_stage)

        # p.sigTreeStateChanged.connect(None)
        self.properties_tree.setParameters(p, showTop=False)
        p.sigTreeStateChanged.connect(self.properties_tree_change)

    ## If anything changes in the tree, print a message
    def properties_tree_change(self, param, changes):
        print("tree changes:")
        for param2, change, data in changes:
            index = self.stages_list.currentRow()
            data2 = self.stages_list.item(index).object.values

            data2[param2.opts['name']] = data


ex = Ui()
ex.show()

if __name__ == '__main__':
    import sys

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()

    # app = QApplication(sys.argv)
    # ex = Ui()
    # ex.show()
    # sys.exit(app.exec_())

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()  # noqa

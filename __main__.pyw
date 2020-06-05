import logging
# from inspect import Parameter

from pyqtgraph.Qt import QtCore, QtGui

from PyQt5.QtWidgets import QPushButton, QTreeView, QVBoxLayout, \
    QApplication, QListWidget, QMainWindow, QPlainTextEdit
from PyQt5.uic import loadUi  # noqa

from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree import Parameter as ParameterForTree

from core import log_handle
from core.bot import get_actions_list, ACTIONS_LIST, InstaPyStartStageItem, InstaPyEndStageItem, insta_clone

app = QtGui.QApplication([])  # noqa

stages = []


class Ui(QMainWindow):
    new_button: QPushButton = None

    load_button: QPushButton = None
    save_Button: QPushButton = None
    run_button: QPushButton = None

    actions_list: QListWidget = None
    stages_list: QListWidget = None

    properties_tree: QTreeView = None

    log_textEdit: QPlainTextEdit = None

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
        params = [
            {'name': 'Basic parameter data types', 'type': 'group', 'children': [
                {'name': 'Integer', 'type': 'int', 'value': 10},
                {'name': 'Float', 'type': 'float', 'value': 10.5, 'step': 0.1},
                {'name': 'String', 'type': 'str', 'value': "hi"},
                {'name': 'List', 'type': 'list', 'values': [1, 2, 3], 'value': 2},
                {'name': 'Named List', 'type': 'list', 'values': {"one": 1, "two": "twosies", "three": [3, 3, 3]},
                 'value': 2},
                {'name': 'Boolean', 'type': 'bool', 'value': True, 'tip': "This is a checkbox"},
                {'name': 'Color', 'type': 'color', 'value': "FF0", 'tip': "This is a color button"},
                {'name': 'Gradient', 'type': 'colormap'},
                {'name': 'Subgroup', 'type': 'group', 'children': [
                    {'name': 'Sub-param 1', 'type': 'int', 'value': 10},
                    {'name': 'Sub-param 2', 'type': 'float', 'value': 1.2e6},
                ]},
                {'name': 'Text Parameter', 'type': 'text', 'value': 'Some text...'},
                {'name': 'Action Parameter', 'type': 'action'},
            ]},
        ]
        p = ParameterForTree.create(name='params', type='group', children=params)

        self.properties_tree.setParameters(p, showTop=False)
        return None
        index = self.stages_list.currentRow()
        data = self.stages_list.item(index).object.anotation_call

        # y = QAbstractItemModel(d)
        # QFileSystemModel()

        # self.properties_tree.setModel(y)

        # self.properties_tree.setModel(QStandardItemModel())
        # self.properties_tree.setModel(QStandardItemModel())
        # self.properties_tree.setAlternatingRowColors(True)
        # self.properties_tree.setSortingEnabled(True)
        # self.properties_tree.setHeaderHidden(False)
        # self.properties_tree.setSelectionBehavior(QAbstractItemView.SelectItems)
        # self.properties_tree.model().setHorizontalHeaderLabels(['Parameter', 'Value'])

        # data = {}
        # # This example will be hidden (has no parameter-value pair)
        # data['example0'] = {}
        # # A set example with an integer and a string parameters
        # data['example1'] = {}
        # data['example1']['int'] = 14
        # data['example1']['str'] = 'asdf'
        # # A set example with a float and other non-conventional type
        # data['example2'] = {}
        # data['example2']['float'] = 1.2
        # # data['example2']['other'] = Other(4, 8)

        # data['required'] = {}
        # for x in anotation_call:
        #     _name = anotation_call[x].name
        #     if _name == 'self':
        #         continue
        #     data['required'][_name] = anotation_call[x].default

        # data['required'] = {x.name: x.default for x in anotation_call}
        # data['required'] = {str(x): 111 for x in anotation_call}
        # data['optional'] = {}

        parent = QStandardItem('kjkj')

        # for x in data:
        #     if not data[x]:
        #         continue
        #     parent = QStandardItem(x)
        #     parent.setFlags(QtCore.Qt.NoItemFlags)

        # self.properties_tree.model().beginInsertRows()

        for y in data:
            value: Parameter = data[y]
            if value.name == 'self':
                continue
            child0 = QStandardItem(y)
            child0.setFlags(QtCore.Qt.NoItemFlags | QtCore.Qt.ItemIsEnabled)

            # child1 = QStandardItem(str(value))
            child1 = QStandardItem(value.default)
            child1.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | ~ QtCore.Qt.ItemIsSelectable)
            child1.type = value.annotation

            parent.appendRow([child0, child1])
        self.properties_tree.model().appendRow(parent)

        self.properties_tree.expandAll()
        pass

    # def createPropertiesOfStage(self):
    #     self.properties_tree.clear()
    #     pass


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

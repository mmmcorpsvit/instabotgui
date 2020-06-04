import logging
import sys

from PyQt5 import QtGui, QtCore, uic
from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QDialog, QPushButton, QTreeView, QHBoxLayout, QAbstractItemView, QVBoxLayout, \
    QApplication, QListWidgetItem, QWidget, QListWidget, QTextEdit, QMainWindow, QPlainTextEdit

from core.bot import get_actions_list, ACTIONS_LIST, InstaPyStartStageItem, InstaPyEndStageItem, insta_clone

stages = []

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Handler(QObject, logging.Handler):
    new_record = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)
        super(logging.Handler).__init__()
        formatter = Formatter('%(asctime)s|%(levelname)s|%(message)s|', '%d/%m/%Y %H:%M:%S')
        self.setFormatter(formatter)

    def emit(self, record):
        msg = self.format(record)
        self.new_record.emit(msg)  # <---- emit signal here


class Formatter(logging.Formatter):
    def formatException(self, ei):
        result = super(Formatter, self).formatException(ei)
        return result

    def format(self, record):
        s = super(Formatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '')
        return s


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
        uic.loadUi('gui.ui', self)  # Load the .ui file

        self.new_button = self.findChild(QPushButton, 'NewButton')  # noqa

        self.load_button = self.findChild(QPushButton, 'LoadButton')  # noqa
        # self.load_button.setVisible(False)

        self.save_Button = self.findChild(QPushButton, 'SaveButton')  # noqa
        self.save_Button.setVisible(False)

        self.run_button = self.findChild(QPushButton, 'RunButton')  # noqa

        self.actions_list = self.findChild(QListWidget, 'actions_list')  # noqa
        self.stages_list = self.findChild(QListWidget, 'stages_list')  # noqa

        self.properties_tree = self.findChild(QTreeView, 'properties_tree')  # noqa

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

        # if not file load:
        self.new_buttonClicked()
        self.show()  # Show the GUI

    def setup_logger(self, log_text_box):
        handler = Handler(self)
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

    def actions_listDoubleClicked(self, qmodelindex):  # noqa
        # add new action to stages list
        # ACTIONS_LIST
        # x = self.actions_list.selectedIndexes()[0]
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

    def loadButtonClicked(self, qmodelindex):  # noqa
        # This is executed when the button is pressed
        logging.info('printButtonPressed')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Ui()
    ex.show()
    sys.exit(app.exec_())

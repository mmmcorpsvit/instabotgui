import sys
import os
import tempfile
import shutil
from shutil import copyfile

import logging
# from inspect import Parameter
from copy import deepcopy
# from inspect import Parameter
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor
from instapy import InstaPy, smart_run, set_workspace

# from core import log_handle
from core.bot import get_actions_list, ACTIONS_LIST, InstaPyStartStageItem, InstaPyEndStageItem, insta_clone

from PyQt5.QtWidgets import QTreeView, QVBoxLayout, \
    QApplication, QListWidget, QMainWindow, QPlainTextEdit, QPushButton, QTextEdit, QWidget, QGridLayout, QLabel, \
    QLineEdit
from PyQt5.uic import loadUi  # noqa

from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree import Parameter as ParameterForTree

import qdarkstyle

os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'


# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')

# from pyqtgraph.Qt import QtCore, QtGui

# app = QtGui.QApplication([])  # noqa


# stages = []

class Stream(QObject):
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


class Ui(QMainWindow):
    new_button: QPushButton = None

    load_button: QPushButton = None
    save_Button: QPushButton = None
    run_button: QPushButton = None

    actions_list: QListWidget = None
    stages_list: QListWidget = None

    properties_tree: ParameterTree = None

    log_textEdit: QTextEdit = None

    current_stage = None

    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        loadUi('gui.ui', self)  # Load the .ui file

        self.new_button = self.findChild(QPushButton, 'NewButton')  # noqa
        self.load_button = self.findChild(QPushButton, 'LoadButton')  # noqa
        # self.load_button.setVisible(False)
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

        self.log_textEdit = self.findChild(QTextEdit, 'log_textEdit')  # noqa
        # self.log_textEdit.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # logging.getLogger().addHandler(self.log_textEdit)
        # You can control the logging level
        # logging.getLogger().setLevel(logging.DEBUG)
        # self.setup_logger(self.log_textEdit)

        # ---------------------------- events ---------------------------
        self.new_button.clicked.connect(self.new_buttonClicked)
        self.load_button.clicked.connect(self.loadButtonClicked)
        self.run_button.clicked.connect(self.RunButtonClicked)

        self.actions_list.addItems(get_actions_list())
        self.actions_list.doubleClicked.connect(self.actions_listDoubleClicked)

        self.stages_list.doubleClicked.connect(self.stages_listDoubleClicked)
        self.stages_list.itemSelectionChanged.connect(self.stages_listitemSelectionChanged)

        # sys.stdout = Stream(newText=self.onUpdateText)

        sys.stdout = Stream(newText=self.onUpdateText)
        sys.stderr = Stream(newText=self.onUpdateText)

        # if not file load:
        self.new_buttonClicked()
        # self.show()  # Show the GUI

    def onUpdateText(self, text):
        cursor = self.log_textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.log_textEdit.setTextCursor(cursor)
        self.log_textEdit.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__

    # def setup_logger(self, log_text_box):
    #     handler = log_handle.Handler(self)
    #     # log_text_box = QPlainTextEdit(self)
    #     # self.main_layout.addWidget(log_text_box)
    #     logging.getLogger().addHandler(handler)
    #     logging.getLogger().setLevel(logging.INFO)
    #     handler.new_record.connect(log_text_box.appendPlainText)  #

    def new_buttonClicked(self):
        self.stages_list.clear()
        self.stages_list.addItem(insta_clone(InstaPyStartStageItem))
        self.stages_list.addItem(insta_clone(InstaPyEndStageItem))
        self.stages_list.setCurrentRow(0)
        self.actions_list.setCurrentRow(0)
        self.log_textEdit.clear()
        logging.info('Welcome to InstaBot v0.1---------------')
        print('Welcome to InstaBot v0.1**************')
        pass

    def RunButtonClicked(self, qmodelindex):  # noqa
        logging.info('Start working')
        # --------------------------------------------

        # create tasks list (just do deep copy)
        y = [self.stages_list.item(x).object for x in range(self.stages_list.count())]
        stages = deepcopy(y)

        if len(stages) < 2 or stages[0].name != '__init__' or stages[len(stages) - 1].name != 'end':
            logging.error('First stage must be init, last stage must be end')
            return None

        dir_path = os.path.dirname(os.path.realpath(__file__))
        # gecko_driver_path = None

        x = stages[0].values
        x['username'] = 'gloss_dp'
        x['password'] = 'UKJCwev'

        x['split_db'] = True

        # rewrite if default some settings
        if 'browser_executable_path' not in x:
            x['browser_executable_path'] = os.path.join(dir_path, 'firefox/firefox.exe')
            # x['browser_executable_path'] = os.path.join(dir_path, 'FirefoxPortable32\\FirefoxPortable.exe')

        if 'geckodriver_path' not in x:
            # gecko_driver_path = tempfile.mkdtemp()
            # copyfile(os.path.join(dir_path, 'geckodriver.exe'), os.path.join(gecko_driver_path, 'geckodriver.exe'))
            x['geckodriver_path'] = os.path.join(dir_path, 'geckodriver.exe')
            # x['geckodriver_path'] = os.path.join(gecko_driver_path, 'geckodriver.exe')

        if 'want_check_browser' not in x:
            x['want_check_browser'] = False

        # session = InstaPy(username='gloss_dp',
        #                   password='UKJCwev',
        #                   browser_executable_path=r"D:\Program Files444\firefox.exe")

        session = InstaPy(**x)

        # with smart_run(session, threaded=True):
        with smart_run(session):
            # Available character sets: LATIN, GREEK, CYRILLIC, ARABIC, HEBREW, CJK, HANGUL, HIRAGANA, KATAKANA and THAI
            session.set_mandatory_language(enabled=True, character_set=['LATIN', 'CYRILLIC'])

            for index, stage in enumerate(stages):
                # current_values = deepcopy(stage.values)

                # skip init and end stages
                if index == 0 or index == len(stages):
                    continue

                # convert text (valid for propretry editor) to list
                current_values = {
                    key: value.split() if stage.anotation_call[key].annotation.__name__ == 'list' else value for
                    (key, value) in stage.values.items()}

                # call function from instance
                f = getattr(session, stage.name)
                f(**current_values)  # noqa https://youtrack.jetbrains.com/issue/PY-27935
                pass

        # x = stages[len(stages)].value
        # insta.end()

        # ------------------------
        # if gecko_driver_path:
        #     shutil.rmtree(gecko_driver_path)
        # --------------------------------------------

        logging.info('End working')
        pass

    def loadButtonClicked(self, qmodelindex):  # noqa
        # This is executed when the button is pressed
        logging.info('printButtonPressed')

        logging.info('Welcome to InstaBot v0.1---------------')
        print('Welcome to InstaBot v0.1**************')

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
                if el.annotation.__name__ == 'list':
                    new_el['type'] = 'text'
                else:
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

    # If anything changes in the tree, print a message
    def properties_tree_change(self, param, changes):
        # print("tree changes:")
        for param2, change, data in changes:
            index = self.stages_list.currentRow()
            data2 = self.stages_list.item(index).object.values

            data2[param2.opts['name']] = data


# ex = Ui()
# ex.show()


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        grid = QGridLayout()
        self.setLayout(grid)

        names = ['Cls', 'Bck', '', 'Close',
                 '7', '8', '9', '/',
                 '4', '5', '6', '*',
                 '1', '2', '3', '-',
                 '0', '.', '=', '+']

        positions = [(i, j) for i in range(5) for j in range(4)]

        for position, name in zip(positions, names):

            if name == '':
                continue
            button = QPushButton(name)
            grid.addWidget(button, *position)

        self.move(300, 150)
        self.setWindowTitle('Calculator')
        self.show()


class Example2(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        title = QLabel('Title')
        author = QLabel('Author')
        review = QLabel('Review')

        titleEdit = QLineEdit()
        authorEdit = QLineEdit()
        reviewEdit = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(reviewEdit, 3, 1, 5, 1)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Review')
        self.show()


def run():
    # handler.setFormatter(logging.Formatter('%(levelname)s: %(filename)s - %(message)s'))

    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ['PYQTGRAPH_QT_LIB']))

    # ex = Ui()
    ex = Example2()
    ex.show()
    sys.exit(app.exec_())

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QApplication.instance().exec_()  # noqa


if __name__ == '__main__':
    dir_workspace = tempfile.mkdtemp()
    set_workspace(dir_workspace)

    run()

    try:
        # if dir_workspace:
        shutil.rmtree(dir_workspace)
    except:  # noqa
        pass

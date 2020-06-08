import sys
import os
import tempfile
import shutil
from shutil import copyfile

import logging
# from inspect import Parameter
from copy import deepcopy
# from inspect import Parameter
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, QUrl, Qt
from PyQt5.QtGui import QTextCursor, QIcon, QDesktopServices
from PyQt5.QtQml import QQmlApplicationEngine

# from core import log_handle
# from core.bot import get_actions_list, ACTIONS_LIST, InstaPyStartStageItem, InstaPyEndStageItem, insta_clone

from PyQt5.QtWidgets import QTreeView, QVBoxLayout, \
    QApplication, QListWidget, QMainWindow, QPlainTextEdit, QPushButton, QTextEdit, QWidget, QGridLayout, QLabel, \
    QLineEdit, QToolBar, QAction, qApp, QDesktopWidget, QSizePolicy, QFileDialog
from PyQt5.uic import loadUi  # noqa

from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree import Parameter as ParameterForTree

import qdarkstyle

from insta_bot import insta_clone, InstaPyStartStageItem, InstaPyEndStageItem, get_actions_list, ACTIONS_LIST

os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'


# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')


# stages = []

class MyLogingStream(QObject):
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


class MainWindow(QMainWindow):
    # toolbar: QToolBar

    def __init__(self):
        super().__init__()
        self.filterTypes = 'InstapyBot files (*.insta_json);;'

        # ------------------
        self.setGeometry(200, 200, 1200, 800)
        # self.setSizePolicy()
        self.setWindowTitle('InstagramBot v0.1')
        self.setWindowIcon(QIcon('assets/icon.png'))
        self.center()

        # ------------------ actions
        action_new_file = QAction(QIcon('assets/new.svg'), 'New', self)
        # action_new_file = QAction(QIcon.fromTheme("SP_FileIcon"), 'New', self)
        action_new_file.setShortcut('Ctrl+N')
        # action_new_file.triggered.connect(qApp.quit)
        action_new_file.triggered.connect(self.action_new_file)

        # action_load_file
        action_open_file = QAction(QIcon('assets/open.png'), 'Open', self)
        action_open_file.setShortcut('Ctrl+O')
        action_open_file.triggered.connect(self.action_open_file)

        action_save_file = QAction(QIcon('assets/save.png'), 'Save', self)
        action_save_file.setShortcut('Ctrl+S')
        # action_save_file.triggered.connect(qApp.save)

        action_save_as_file = QAction(QIcon('assets/save_as.png'), 'Save as', self)
        action_save_as_file.setShortcut('Ctrl+Shift+S')
        # action_save_as_file.triggered.connect(qApp.save_as)

        action_help = QAction(QIcon('assets/help.png'), 'Help', self)
        action_help.setShortcut('F1')
        action_help.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/timgrossmann/InstaPy/blob/master/DOCUMENTATION.md#actions')))

        # -----------------
        action_stage_run = QAction(QIcon('assets/run.png'), 'Run', self)
        action_stage_run.setShortcut('F5')
        action_stage_run.triggered.connect(self.action_stage_run)

        action_stage_stop = QAction(QIcon('assets/stop.png'), 'Stop', self)
        action_stage_stop.setShortcut('F9')
        action_stage_stop.setDisabled(True)
        action_stage_stop.setVisible(False)
        action_stage_stop.triggered.connect(self.action_stage_stop)

        # ---------------------
        # self.spacer = QWidget()
        # self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar = self.addToolBar('New')
        self.toolbar.setMovable(False)
        # self.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), self.toolbar)

        self.toolbar.addAction(action_new_file)
        self.toolbar.addSeparator()

        self.toolbar.addAction(action_open_file)
        self.toolbar.addSeparator()

        self.toolbar.addAction(action_save_file)
        self.toolbar.addAction(action_save_as_file)
        # self.toolbar.addWidget(self.spacer)
        self.toolbar.addSeparator()

        self.toolbar.addAction(action_stage_run)
        self.toolbar.addAction(action_stage_stop)
        # self.toolbar.addWidget(self.spacer)
        self.toolbar.addSeparator()

        self.toolbar.addAction(action_help)

        # --------------------
        self.actions_list = QListWidget()
        self.actions_list.doubleClicked.connect(self.actions_listDoubleClicked)

        self.stages_list = QListWidget()
        self.stages_list.doubleClicked.connect(self.stages_listDoubleClicked)
        self.stages_list.itemSelectionChanged.connect(self.stages_listitemSelectionChanged)

        self.properties_tree = ParameterTree()
        self.log_textEdit = QTextEdit()

        # --------------------
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(QLabel('Actions'), 0, 0)
        self.grid.addWidget(self.actions_list, 1, 0)

        self.grid.addWidget(QLabel('Stages'), 0, 1)
        self.grid.addWidget(self.stages_list, 1, 1)

        self.grid.addWidget(QLabel('Properties'), 0, 2)
        self.grid.addWidget(self.properties_tree, 1, 2)

        self.grid.addWidget(QLabel('Logs'), 2, 0)
        self.grid.addWidget(self.log_textEdit, 3, 0, 1, 3)

        self.grid.setRowStretch(1, 300)

        self.grid.setColumnStretch(0, 10)
        self.grid.setColumnStretch(2, 10)
        self.setLayout(self.grid)

        widget = QWidget()
        widget.setLayout(self.grid)
        self.setCentralWidget(widget)

        # --------------------
        # sys.stdout = MyLogingStream(newText=self.onUpdateText)
        # sys.stderr = MyLogingStream(newText=self.onUpdateText)

        self.actions_list.addItems(get_actions_list())
        self.action_new_file()

        self.show()

    def onUpdateText(self, text):
        cursor = self.log_textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.log_textEdit.setTextCursor(cursor)
        self.log_textEdit.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def action_new_file(self):
        self.stages_list.clear()
        self.stages_list.addItem(insta_clone(InstaPyStartStageItem))
        self.stages_list.addItem(insta_clone(InstaPyEndStageItem))
        self.stages_list.setCurrentRow(0)
        self.actions_list.setCurrentRow(0)
        self.log_textEdit.clear()
        logging.info('Welcome to InstaBot v0.1---------------')
        print('Welcome to InstaBot v0.1**************')
        pass

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

    def action_open_file(self):
        path, _ = QFileDialog.getOpenFileName(parent=self, caption='Open file', directory='', filter=self.filterTypes)

        if path:
            try:
                with open(path, 'r') as f:
                    text = f.read()
                    f.close()
            except Exception as e:
                self.dialog_message(str(e))
            else:
                self.path = path
                self.editor.setPlainText(text)
                self.update_title()

    def properties_tree_change(self, param, changes):
        # print("tree changes:")
        for param2, change, data in changes:
            index = self.stages_list.currentRow()
            data2 = self.stages_list.item(index).object.values

            data2[param2.opts['name']] = data

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

    def action_stage_run(self):
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
            x['browser_executable_path'] = os.path.join(dir_path, 'assets/firefox/firefox.exe')
            # x['browser_executable_path'] = os.path.join(dir_path, 'FirefoxPortable32\\FirefoxPortable.exe')

        if 'geckodriver_path' not in x:
            # gecko_driver_path = tempfile.mkdtemp()
            # copyfile(os.path.join(dir_path, 'geckodriver.exe'), os.path.join(gecko_driver_path, 'geckodriver.exe'))
            x['geckodriver_path'] = os.path.join(dir_path, 'assets/geckodriver.exe')
            # x['geckodriver_path'] = os.path.join(gecko_driver_path, 'geckodriver.exe')

        if 'want_check_browser' not in x:
            x['want_check_browser'] = False

        # session = InstaPy(username='gloss_dp',
        #                   password='UKJCwev',
        #                   browser_executable_path=r"D:\Program Files444\firefox.exe")

        from instapy import InstaPy, smart_run, set_workspace
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

    def action_stage_stop(self):
        pass


def run():
    # handler.setFormatter(logging.Formatter('%(levelname)s: %(filename)s - %(message)s'))

    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())

    engine = QQmlApplicationEngine()
    # engine.quit.connect(app.quit)
    # engine.load('main.ui.qml')
    # engine.load('main.qml')

    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ['PYQTGRAPH_QT_LIB']))

    ex = MainWindow()
    # ex.show()
    sys.exit(app.exec_())

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QApplication.instance().exec_()  # noqa


if __name__ == '__main__':
    # dir_workspace = tempfile.mkdtemp()
    # set_workspace(dir_workspace)

    run()

    try:
        pass
        # if dir_workspace:
        # shutil.rmtree(dir_workspace)
    except:  # noqa
        pass

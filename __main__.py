import sys
import os
import tempfile
import shutil
import logging
from copy import deepcopy

from PyQt5.QtCore import QUrl, QObject, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QTextCursor, QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QListWidget, QMainWindow, QTextEdit, QWidget, QGridLayout, \
    QLabel, QAction, QDesktopWidget, QFileDialog

from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree import Parameter as ParameterForTree

import qdarkstyle

from instapy import set_workspace

from insta_bot import insta_clone, InstaPyStartStageItem, InstaPyEndStageItem, get_actions_list, ACTIONS_LIST, \
    ExecuteScenario
from log_handle import MyLogHandler

os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'


#
# def trap_exc_during_debug(*args):
#     # when app raises uncaught exception, print info
#     print(args)
#
#
# # install exception hook: without this, uncaught exception would cause application to exit
# sys.excepthook = trap_exc_during_debug


# class Worker(QObject):
#     """
#     Must derive from QObject in order to emit signals, connect slots to other signals, and operate in a QThread.
#     """
#
#     sig_step = pyqtSignal(int, str)  # worker id, step description: emitted every step through work() loop
#     sig_done = pyqtSignal(int)  # worker id: emitted at end of work()
#     sig_msg = pyqtSignal(str)  # message to be shown to user
#
#     def __init__(self, id: int):
#         super().__init__()
#         self.__id = id
#         self.__abort = False
#
#     @pyqtSlot()
#     def work(self):
#         """
#         Pretend this worker method does work that takes a long time. During this time, the thread's
#         event loop is blocked, except if the application's processEvents() is called: this gives every
#         thread (incl. main) a chance to process events, which in this sample means processing signals
#         received from GUI (such as abort).
#         """
#         thread_name = QThread.currentThread().objectName()
#         thread_id = int(QThread.currentThreadId())  # cast to int() is necessary
#         self.sig_msg.emit('Running worker #{} from thread "{}" (#{})'.format(self.__id, thread_name, thread_id))
#
#         for step in range(100):
#             time.sleep(0.1)
#             self.sig_step.emit(self.__id, 'step ' + str(step))
#
#             # check if we need to abort the loop; need to process events to receive signals;
#             app.processEvents()  # this could cause change to self.__abort
#             if self.__abort:
#                 # note that "step" value will not necessarily be same for every thread
#                 self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
#                 break
#
#         self.sig_done.emit(self.__id)
#
#     def abort(self):
#         self.sig_msg.emit('Worker #{} notified to abort'.format(self.__id))
#         self.__abort = True


class MainWindow(QMainWindow):
    filterTypes = 'InstapyBot files (*.insta_json);;'

    current_stage = None
    path = ''
    get_thread = None

    def __init__(self):
        super().__init__()

        QThread.currentThread().setObjectName('main')
        # self.communicate_execution = CommunicateExecution()

        # ------------------
        self.setGeometry(200, 200, 1200, 850)
        # self.setSizePolicy()
        self.setWindowTitle('InstagramBot v0.1')
        self.setWindowIcon(QIcon('assets/icon.png'))
        self.center()

        # ------------------ actions
        self.action_new_file = QAction(QIcon('assets/new.svg'), 'New', self)
        # action_new_file = QAction(QIcon.fromTheme("SP_FileIcon"), 'New', self)
        self.action_new_file.setShortcut('Ctrl+N')
        # action_new_file.triggered.connect(qApp.quit)
        self.action_new_file.triggered.connect(self.action_new_file_trigger)

        # action_load_file
        self.action_open_file = QAction(QIcon('assets/open.png'), 'Open', self)
        self.action_open_file.setShortcut('Ctrl+O')
        self.action_open_file.triggered.connect(self.action_open_file_trigger)

        self.action_save_file = QAction(QIcon('assets/save.png'), 'Save', self)
        self.action_save_file.setShortcut('Ctrl+S')
        # action_save_file.triggered.connect(qApp.save)

        self.action_save_as_file = QAction(QIcon('assets/save_as.png'), 'Save as', self)
        self.action_save_as_file.setShortcut('Ctrl+Shift+S')
        # action_save_as_file.triggered.connect(qApp.save_as)

        self.action_help = QAction(QIcon('assets/help.png'), 'Help', self)
        self.action_help.setShortcut('F1')
        self.action_help.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/timgrossmann/InstaPy/blob/master/DOCUMENTATION.md#actions')))

        # -----------------
        self.action_stage_run = QAction(QIcon('assets/run.png'), 'Run', self)
        self.action_stage_run.setShortcut('F5')
        self.action_stage_run.triggered.connect(self.action_stage_run_trigger)

        self.action_stage_stop = QAction(QIcon('assets/stop.png'), 'Stop', self)
        self.action_stage_stop.setShortcut('F9')
        self.action_stage_stop.setDisabled(True)
        # self.action_stage_stop.setVisible(False)
        self.action_stage_stop.triggered.connect(self.action_stage_stop_trigger)

        # ---------------------
        # self.spacer = QWidget()
        # self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar = self.addToolBar('New')
        self.toolbar.setMovable(False)
        # self.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), self.toolbar)

        self.toolbar.addAction(self.action_new_file)
        self.toolbar.addSeparator()

        self.toolbar.addAction(self.action_open_file)
        self.toolbar.addSeparator()

        self.toolbar.addAction(self.action_save_file)
        self.toolbar.addAction(self.action_save_as_file)
        # self.toolbar.addWidget(self.spacer)
        self.toolbar.addSeparator()

        self.toolbar.addAction(self.action_stage_run)
        self.toolbar.addAction(self.action_stage_stop)
        # self.toolbar.addWidget(self.spacer)
        self.toolbar.addSeparator()

        self.toolbar.addAction(self.action_help)

        # --------------------
        self.actions_list = QListWidget()
        self.actions_list.setWordWrap(True)
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
        self.setup_logger()

        # --------------------
        self.actions_list.addItems(get_actions_list())
        self.action_new_file_trigger()

        self.show()

    def setup_logger(self):
        handler = MyLogHandler(self)
        # log_text_box = QPlainTextEdit(self)
        # self.main_layout.addWidget(log_text_box)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
        handler.new_record.connect(self.log_textEdit.append)  # <---- connect QPlainTextEdit.appendPlainText slot

        class Stream(QObject):
            newText = pyqtSignal(str)

            def write(self, text):
                self.newText.emit(str(text))

        sys.stdout = Stream(newText=self.onUpdateText)  # noqa

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

    def action_new_file_trigger(self):
        self.stages_list.clear()
        self.stages_list.addItem(insta_clone(InstaPyStartStageItem))
        self.stages_list.addItem(insta_clone(InstaPyEndStageItem))
        self.stages_list.setCurrentRow(0)
        self.actions_list.setCurrentRow(0)
        self.log_textEdit.clear()
        logging.info('Welcome to InstaBot v0.1---------------')
        print('Welcome to InstaBot v0.1**************')
        pass

    def action_open_file_trigger(self):
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

    def actions_listDoubleClicked(self, qmodelindex):  # noqa
        # add new action to stages list
        index = self.actions_list.currentRow()
        _new_object = insta_clone(ACTIONS_LIST[index])

        self.stages_list.insertItem(self.stages_list.count() - 1, _new_object)
        pass

    # --------------------
    def stages_listDoubleClicked(self, qmodelindex):  # noqa
        # remove action from stages list
        index = self.stages_list.currentRow()
        item = self.stages_list.item(index)

        if item.object.name in ['__init__', 'end']:
            logging.error(f'You cannot remove stage: {item.object.name}')
            return None
        self.stages_list.takeItem(index)
        pass

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

    def action_stage_run_trigger(self):
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

        # logging.info('Start working')
        # return None

        # idx = 1
        # worker = Worker(idx)
        # # self.action_stage_run.
        #
        # thread = QThread()
        # thread.setObjectName('thread_' + str(idx))
        # self.__threads.append((thread, worker))  # need to store worker too otherwise will be gc'd
        # worker.moveToThread(thread)
        #
        # # get progress messages from worker:
        # worker.sig_step.connect(self.on_worker_step)
        # worker.sig_done.connect(self.on_worker_done)
        # worker.sig_msg.connect(self.log.append)
        #
        # # control worker:
        # self.sig_abort_workers.connect(worker.abort)

        # get read to start worker:
        # self.sig_start.connect(worker.work)  # needed due to PyCharm debugger bug (!); comment out next line
        # thread.started.connect(worker.work)
        # thread.start()  # this will emit 'started' and start thread's event loop

        self.action_stage_run.setDisabled(True)
        self.action_stage_stop.setEnabled(True)

        self.get_thread = ExecuteScenario(stages=stages, instapy_start_values=x)
        self.get_thread.setTerminationEnabled(True)

        # self.get_thread.sig_step.connect(self.on_worker_step)
        self.get_thread.sig_done.connect(self.on_worker_done)
        # self.get_thread.sig_msg.connect(self.log_textEdit.append)

        # control worker:
        # self.sig_abort_workers.connect(worker.abort)
        # get read to start worker:
        # self.sig_start.connect(worker.work)  # needed due to PyCharm debugger bug (!); comment out next line
        # self.get_thread.started.connect(worker.work)
        # self.get_thread.connect(self.communicate_execution.done)
        # self.connect(self.get_thread, SIGNAL("finished()"), self.done)
        self.get_thread.start()

    # @pyqtSlot(int, str)
    # def on_worker_step(self, worker_id: int, data: str):
    #     self.log_textEdit.append('Worker #{}: {}'.format(worker_id, data))
    #     # self.progress.append('{}: {}'.format(worker_id, data))

    @pyqtSlot(int)
    def on_worker_done(self, worker_id):
        self.action_stage_run.setEnabled(True)
        self.action_stage_stop.setDisabled(True)

        # self.log_textEdit.append('worker #{} done'.format(worker_id))
        # # self.progress.append('-- Worker {} DONE'.format(worker_id))
        # self.__workers_done += 1
        # if self.__workers_done == self.NUM_THREADS:
        #     self.log_textEdit.append('No more workers active')
        #
        #     # self.action_stage_stop.setDisabled(True)
        #
        #     self.action_start_stop.setEnabled(True)
        #     self.action_stage_stop.setDisabled(True)
        #     # self.__threads = None

    def action_stage_stop_trigger(self):
        # self.get_thread.terminate()
        self.get_thread.stop()
        pass


def run():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ['PYQTGRAPH_QT_LIB']))

    ex = MainWindow()
    sys.exit(app.exec_())

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QApplication.instance().exec_()  # noqa


if __name__ == '__main__':
    run()

    dir_workspace = tempfile.mkdtemp()
    set_workspace(dir_workspace)

    try:
        # pass
        # if dir_workspace:
        shutil.rmtree(dir_workspace)
    except:  # noqa
        pass

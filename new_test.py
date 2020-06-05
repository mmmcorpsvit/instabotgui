import sys
from copy import deepcopy

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QWidget


# https://stackoverflow.com/questions/27234255/editing-a-dictionary-with-a-qtreeview
# https://gist.github.com/skriticos/5415869
# https://gist.github.com/TheKewlStore/72eacda92efde8abcd0e
class TestDialog(QtWidgets.QDialog):
    def __init__(self, data):

        super(TestDialog, self).__init__()

        self.data = deepcopy(data)

        # Layout
        btOk = QtWidgets.QPushButton("OK")
        btCancel = QtWidgets.QPushButton("Cancel")
        self.tree = QtWidgets.QTreeView()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btOk)
        hbox.addWidget(btCancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)
        self.setGeometry(300, 300, 600, 400)

        # Button signals
        btCancel.clicked.connect(self.reject)
        btOk.clicked.connect(self.accept)

        # Tree view
        self.tree.setModel(QStandardItemModel())
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.setHeaderHidden(False)
        self.tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)

        self.tree.model().setHorizontalHeaderLabels(['Parameter', 'Value'])

        for x in self.data:
            if not self.data[x]:
                continue
            parent = QStandardItem(x)
            parent.setFlags(QtCore.Qt.NoItemFlags)
            for y in self.data[x]:
                value = self.data[x][y]
                child0 = QStandardItem(y)
                child0.setFlags(QtCore.Qt.NoItemFlags |
                                QtCore.Qt.ItemIsEnabled)
                child1 = QStandardItem(str(value))
                child1.setFlags(QtCore.Qt.ItemIsEnabled |
                                QtCore.Qt.ItemIsEditable |
                                ~ QtCore.Qt.ItemIsSelectable)
                parent.appendRow([child0, child1])
            self.tree.model().appendRow(parent)

        self.tree.expandAll()

    def get_data(self):
        return self.data


class Other(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)


class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()

        btn = QtWidgets.QPushButton('Button', self)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.show_dialog)

        self.data = {}
        # This example will be hidden (has no parameter-value pair)
        self.data['example0'] = {}
        # A set example with an integer and a string parameters
        self.data['example1'] = {}
        self.data['example1']['int'] = 14
        self.data['example1']['str'] = 'asdf'
        # A set example with a float and other non-conventional type
        self.data['example2'] = {}
        self.data['example2']['float'] = 1.2
        self.data['example2']['other'] = Other(4, 8)

    def show_dialog(self):
        dialog = TestDialog(self.data)
        accepted = dialog.exec_()
        if not accepted:
            return
        self.data = deepcopy(dialog.get_data())
        print(self.data)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())

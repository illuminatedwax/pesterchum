from PyQt4 import QtGui, QtCore
from datetime import timedelta

class mysteryTime(timedelta):
    def __sub__(self, other):
        return self
    def __eq__(self, other):
        return (type(other) is mysteryTime)
    def __neq__(self, other):
        return (type(other) is not mysteryTime)

class PesterList(list):
    def __init__(self, l):
        self.extend(l)

class PesterIcon(QtGui.QIcon):
    def __init__(self, *x, **y):
        QtGui.QIcon.__init__(self, *x, **y)
        if type(x[0]) in [str, unicode]:
            self.icon_pixmap = QtGui.QPixmap(x[0])
        else:
            self.icon_pixmap = None
    def realsize(self):
        if self.icon_pixmap:
            return self.icon_pixmap.size()
        else:
            try:
                return self.availableSizes()[0]
            except IndexError:
                return None

class RightClickList(QtGui.QListWidget):
    def contextMenuEvent(self, event):
        #fuckin Qt
        if event.reason() == QtGui.QContextMenuEvent.Mouse:
            listing = self.itemAt(event.pos())
            self.setCurrentItem(listing)
            self.getOptionsMenu().popup(event.globalPos())
    def getOptionsMenu(self):
        return self.optionsMenu

class RightClickTree(QtGui.QTreeWidget):
    def contextMenuEvent(self, event):
        if event.reason() == QtGui.QContextMenuEvent.Mouse:
            listing = self.itemAt(event.pos())
            self.setCurrentItem(listing)
            self.getOptionsMenu().popup(event.globalPos())
    def getOptionsMenu(self):
        return self.optionsMenu

class MultiTextDialog(QtGui.QDialog):
    def __init__(self, title, parent, *queries):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        if len(queries) == 0:
            return
        self.inputs = {}
        layout_1 = QtGui.QHBoxLayout()
        for d in queries:
            label = d["label"]
            inputname = d["inputname"]
            value = d.get("value", "")
            l = QtGui.QLabel(label, self)
            layout_1.addWidget(l)
            self.inputs[inputname] = QtGui.QLineEdit(value, self)
            layout_1.addWidget(self.inputs[inputname])
        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        layout_ok = QtGui.QHBoxLayout()
        layout_ok.addWidget(self.cancel)
        layout_ok.addWidget(self.ok)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addLayout(layout_1)
        layout_0.addLayout(layout_ok)

        self.setLayout(layout_0)
    def getText(self):
        r = self.exec_()
        if r == QtGui.QDialog.Accepted:
            retval = {}
            for (name, widget) in self.inputs.iteritems():
                retval[name] = unicode(widget.text())
            return retval
        else:
            return None

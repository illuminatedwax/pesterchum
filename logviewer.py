import os, sys
import codecs
import re
from time import strftime, strptime
from PyQt4 import QtGui, QtCore
from generic import RightClickList
from parsetools import convertTags

class PesterLogUserSelect(QtGui.QDialog):
    def __init__(self, config, theme, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.config = config
        self.theme = theme
        self.parent = parent
        self.handle = parent.profile().handle
        if sys.platform != "darwin":
            self.logpath = "logs"
        else:
            self.logpath = _datadir+"logs"

        self.setStyleSheet(self.theme["main/defaultwindow/style"])
        self.setWindowTitle("Pesterlogs")

        instructions = QtGui.QLabel("Pick a memo or chumhandle:")

        if os.path.exists("%s/%s" % (self.logpath, self.handle)):
            chumMemoList = os.listdir("%s/%s/" % (self.logpath, self.handle))
        else:
            chumMemoList = []
        chumslist = config.chums()
        for c in chumslist:
            if not c in chumMemoList:
                chumMemoList.append(c)
        chumMemoList.sort()

        self.chumsBox = RightClickList(self)
        self.chumsBox.setStyleSheet(self.theme["main/chums/style"])
        self.chumsBox.optionsMenu = QtGui.QMenu(self)

        for (i, t) in enumerate(chumMemoList):
            item = QtGui.QListWidgetItem(t)
            item.setTextColor(QtGui.QColor(self.theme["main/chums/userlistcolor"]))
            self.chumsBox.addItem(item)

        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('viewActivatedLog()'))
        layout_ok = QtGui.QHBoxLayout()
        layout_ok.addWidget(self.cancel)
        layout_ok.addWidget(self.ok)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(instructions)
        layout_0.addWidget(self.chumsBox)
        layout_0.addLayout(layout_ok)

        self.setLayout(layout_0)

    def selectedchum(self):
        return self.chumsBox.currentItem()

    @QtCore.pyqtSlot()
    def viewActivatedLog(self):
        selectedchum = self.selectedchum().text()
        if not hasattr(self, 'pesterlogviewer'):
            self.pesterlogviewer = None
        if not self.pesterlogviewer:
            self.pesterlogviewer = PesterLogViewer(selectedchum, self.config, self.theme, self.parent)
            self.connect(self.pesterlogviewer, QtCore.SIGNAL('rejected()'),
                         self, QtCore.SLOT('closeActiveLog()'))
            self.pesterlogviewer.show()
            self.pesterlogviewer.raise_()
            self.pesterlogviewer.activateWindow()
        self.accept()

    @QtCore.pyqtSlot()
    def closeActiveLog(self):
        self.pesterlogviewer.close()
        self.pesterlogviewer = None

class PesterLogViewer(QtGui.QDialog):
    def __init__(self, chum, config, theme, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.config = config
        self.theme = theme
        self.parent = parent
        global _datadir
        self.handle = parent.profile().handle
        self.chum = chum
        self.convos = {}
        if sys.platform != "darwin":
            self.logpath = "logs"
        else:
            self.logpath = _datadir+"logs"

        self.setStyleSheet(self.theme["main/defaultwindow/style"])
        self.setWindowTitle("Pesterlogs with " + self.chum)

        self.format = "bbcode"
        if os.path.exists("%s/%s/%s/%s" % (self.logpath, self.handle, chum, self.format)):
            self.logList = os.listdir("%s/%s/%s/%s/" % (self.logpath, self.handle, self.chum, self.format))
        else:
            self.logList = []

        if not os.path.exists("%s/%s/%s/%s" % (self.logpath, self.handle, chum, self.format)) or len(self.logList) == 0:
            instructions = QtGui.QLabel("No Pesterlogs were found")

            self.ok = QtGui.QPushButton("CLOSE", self)
            self.ok.setDefault(True)
            self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                         self, QtCore.SLOT('reject()'))
            layout_ok = QtGui.QHBoxLayout()
            layout_ok.addWidget(self.ok)

            layout_0 = QtGui.QVBoxLayout()
            layout_0.addWidget(instructions)
            layout_0.addLayout(layout_ok)

            self.setLayout(layout_0)
        else:
            self.instructions = QtGui.QLabel("Pesterlog with " +self.chum+ " on")

            self.logsBox = RightClickList(self)
            self.logsBox.setFixedSize(220, 300)
            self.logsBox.setStyleSheet(self.theme["main/chums/style"])
            self.connect(self.logsBox, QtCore.SIGNAL('itemSelectionChanged()'),
                     self, QtCore.SLOT('loadSelectedLog()'))
            self.logsBox.optionsMenu = QtGui.QMenu(self)

            self.textArea = QtGui.QTextEdit(self)
            self.textArea.setReadOnly(True)
            self.textArea.setFixedWidth(600)
            if theme.has_key("convo/scrollbar"):
                self.textArea.setStyleSheet("QTextEdit { width:500px; %s } QScrollBar:vertical { %s } QScrollBar::handle:vertical { %s } QScrollBar::add-line:vertical { %s } QScrollBar::sub-line:vertical { %s } QScrollBar:up-arrow:vertical { %s } QScrollBar:down-arrow:vertical { %s }" % (theme["convo/textarea/style"], theme["convo/scrollbar/style"], theme["convo/scrollbar/handle"], theme["convo/scrollbar/downarrow"], theme["convo/scrollbar/uparrow"], theme["convo/scrollbar/uarrowstyle"], theme["convo/scrollbar/darrowstyle"] ))
            else:
                self.textArea.setStyleSheet("QTextEdit { width:500px; %s }" % (theme["convo/textarea/style"]))

            self.logList.sort()
            self.logList.reverse()

            for l in self.logList:
                item = QtGui.QListWidgetItem(self.fileToTime(l))
                item.setTextColor(QtGui.QColor(self.theme["main/chums/userlistcolor"]))
                self.logsBox.addItem(item)

            if len(self.logList) > 0: self.loadLog(self.logList[0])

            self.ok = QtGui.QPushButton("CLOSE", self)
            self.ok.setDefault(True)
            self.ok.setFixedWidth(80)
            self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                         self, QtCore.SLOT('reject()'))
            layout_ok = QtGui.QHBoxLayout()
            layout_ok.addWidget(self.ok)
            layout_ok.setAlignment(self.ok, QtCore.Qt.AlignRight)

            layout_logs = QtGui.QHBoxLayout()
            layout_logs.addWidget(self.logsBox)
            layout_logs.addWidget(self.textArea)

            layout_0 = QtGui.QVBoxLayout()
            layout_0.addWidget(self.instructions)
            layout_0.addLayout(layout_logs)
            layout_0.addLayout(layout_ok)

            self.setLayout(layout_0)

    @QtCore.pyqtSlot()
    def loadSelectedLog(self):
        self.loadLog(self.timeToFile(self.logsBox.currentItem().text()))

    def loadLog(self, fname):
        fp = codecs.open("%s/%s/%s/%s/%s" % (self.logpath, self.handle, self.chum, self.format, fname), encoding='utf-8', mode='r')
        self.textArea.clear()
        for line in fp:
            cline = line.replace("\r\n", "").replace("[/color]","</c>")
            cline = re.sub("\[color=(#.{6})]", r"<c=\1>", cline)
            self.textArea.append(convertTags(cline))
        textCur = self.textArea.textCursor()
        textCur.movePosition(1)
        self.textArea.setTextCursor(textCur)
        self.instructions.setText("Pesterlog with " +self.chum+ " on " + self.fileToTime(str(fname)))

    def fileToTime(self, fname):
        timestr = fname[(fname.index(".")+1):fname.index(".txt")]
        return strftime("%a %d %b %Y %H %M", strptime(timestr, "%Y-%m-%d.%H.%M"))
    def timeToFile(self, time):
        return self.chum + strftime(".%Y-%m-%d.%H.%M.txt", strptime(str(time), "%a %d %b %Y %H %M"))

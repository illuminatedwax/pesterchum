from string import Template
import re
from PyQt4 import QtGui, QtCore

from dataobjs import PesterProfile, Mood
from generic import PesterIcon
from convo import PesterConvo, PesterInput, PesterText

class MemoText(PesterText):
    def __init__(self, theme, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setStyleSheet(theme["memos/textarea/style"])
        self.setReadOnly(True)
        self.setMouseTracking(True)
    def addMessage(self, text, chum):
        pass
    def changeTheme(self):
        pass

class MemoInput(PesterInput):
    def __init__(self, theme, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setStyleSheet(theme["memos/input/style"])
    def changeTheme(self, theme):
        self.setStyleSheet(theme["memos/input/style"])

class PesterMemo(PesterConvo):
    def __init__(self, channel, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.channel = channel
        self.mainwindow = mainwindow
        self.setWindowTitle(channel)
        self.channelLabel = QtGui.QLabel(self)
        self.channelLabel.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding))

        self.textArea = MemoText(self.mainwindow.theme, self)
        self.textInput = MemoInput(self.mainwindow.theme, self)
        self.textInput.setFocus()

        self.userlist = QtGui.QListWidget(self)
        self.userlist.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding))

        self.timeslider = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.timeinput = QtGui.QLineEdit(self)

        self.initTheme(self.mainwindow.theme)

        # connect
        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.channelLabel)
        layout_0.addWidget(self.textArea)
        layout_0.addWidget(self.textInput)

        layout_1 = QtGui.QGridLayout()
        layout_1.addWidget(self.timeslider, 0, 1, QtCore.Qt.AlignHCenter)
        layout_1.addWidget(self.timeinput, 1, 0, 1, 3)

        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addLayout(layout_0)
        self.layout.addWidget(self.userlist)
        self.layout.addLayout(layout_1)
        self.layout.setSpacing(0)
        margins = self.mainwindow.theme["memos/margins"]
        self.layout.setContentsMargins(margins["left"], margins["top"],
                                  margins["right"], margins["bottom"])
        
        #if parent:
        #    parent.addChat(self)
        self.newmessage = False

    def updateMood(self):
        pass
    def updateBlocked(self):
        pass
    def updateColor(self):
        pass
    def addMessage(self):
        pass
    def notifyNewMessage(self):
        pass
    def clearNewMessage(self):
        pass

    def initTheme(self, theme):
        memo = theme["memos"]
        self.resize(*memo["size"])
        self.setStyleSheet(memo["style"])
        self.setWindowIcon(PesterIcon(theme["memos/memoicon"]))

        t = Template(theme["memos/label/text"])
        self.channelLabel.setText(t.safe_substitute(channel=self.channel))
        self.channelLabel.setStyleSheet(theme["memos/label/style"])
        self.channelLabel.setAlignment(self.aligndict["h"][theme["memos/label/align/h"]] | self.aligndict["v"][theme["memos/label/align/v"]])
        self.channelLabel.setMaximumHeight(theme["memos/label/maxheight"])
        self.channelLabel.setMinimumHeight(theme["memos/label/minheight"])

        self.userlist.setStyleSheet(theme["main/chums/style"])
        self.userlist.setFixedWidth(theme["memos/userlist/width"])

        self.timeinput.setFixedWidth(theme["memos/time/text/width"])
        self.timeinput.setStyleSheet(theme["memos/time/text/style"])
        slidercss = "QSlider { %s } QSlider::groove { %s } QSlider::handle { %s }" % (theme["memos/time/slider/style"], theme["memos/time/slider/groove"], theme["memos/time/slider/handle"])
        self.timeslider.setStyleSheet(slidercss) 


    def changeTheme(self, theme):
        self.initTheme(theme)
        self.textArea.changeTheme(theme)
        self.textInput.changeTheme(theme)

    def sentMessage(self):
        pass

    def closeEvent(self, event):
        self.mainwindow.waitingMessages.messageAnswered(self.channel)
#        self.windowClosed.emit(self.chum.handle)


#    messageSent - signal -> sendMessage -> sendMessage(Memo)
#    windowClosed - signal -> closeMemo

#    self.textInput
#    self.textArea

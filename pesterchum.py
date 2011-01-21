# pesterchum
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import logging
import sys
import json
from PyQt4 import QtGui, QtCore

logging.basicConfig(level=logging.INFO)

class PesterHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        # display msg, do other stuff
        print "%s: %s" % (nick, msg)
        if chan == "#pesterchum":
            # follow instructions
            self.window.newMessage()
            pass
        else:
            # private message
            pass
    def welcome(self, server, nick, msg):
        helpers.join(self.client, "#pesterchum")

class userConfig(object):
    def __init__(self):
        fp = open("pesterchum.js")
        self.config = json.load(fp)
        fp.close()
    def chums(self):
        return self.config['chums']

class exitButton(QtGui.QPushButton):
    def __init__(self, icon, parent=None):
        QtGui.QPushButton.__init__(self, icon, "", parent)
        self.setFlat(True)
    def clicked(self):
        print "X"

class chumArea(QtGui.QListWidget):
    def __init__(self, chums, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        self.setGeometry(75, 100, 350, 500)
        self.setStyleSheet("""
background-color: black;
color: white;
font: bold;
font-family: "Courier New";
""")
        self.chums = chums
        for c in self.chums:
            chumLabel = QtGui.QListWidgetItem(c)
#            chumLabel.setFont(QtGui.QFont("Courier New", pointSize=12,
#                                          weight=75))
            self.addItem(chumLabel)
        

class PesterWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent, 
                               flags=QtCore.Qt.CustomizeWindowHint)
        self.config = userConfig()
        self.setGeometry(100,100, 500, 700)
        self.setWindowIcon(QtGui.QIcon('themes/pesterchum/trayicon.gif'))
        self.setStyleSheet("""
background-color: #fdb302;
""")
        self.closeButton = exitButton(QtGui.QIcon('themes/pesterchum/x.gif'), self)
        s = self.size() - self.closeButton.icon().availableSizes()[0]
        self.closeButton.move(s.width(), 0)
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))
        self.chumList = chumArea(self.config.chums(), self)

        self.cli = IRCClient(PesterHandler, host="irc.tymoon.eu", port=6667, nick="superGhost")
        self.cli.command_handler.window = self

        self.conn = self.cli.connect()
        self.irctimer = QtCore.QTimer(self)
        self.connect(self.irctimer, QtCore.SIGNAL('timeout()'),
                     self, QtCore.SLOT('updateIRC()'))
        self.irctimer.start()
        self.moving = None
    def mouseMoveEvent(self, event):
        if self.moving:
            move = event.globalPos() - self.moving
            self.move(self.pos() + move)
            self.moving = event.globalPos()
    def mousePressEvent(self, event):
        if event.button() == 1:
            self.moving = event.globalPos()
    def mouseReleaseEvent(self, event):
        if event.button() == 1:
            self.moving = None
    @QtCore.pyqtSlot()
    def updateIRC(self):
        self.conn.next()
    def newMessage(self):
        pass


def main():

    app = QtGui.QApplication(sys.argv)
    widget = PesterWindow()
    widget.show()
    trayicon = QtGui.QSystemTrayIcon(QtGui.QIcon("themes/pesterchum/trayicon.gif"), app)
    traymenu = QtGui.QMenu()
    traymenu.addAction("Hi!! HI!!")
    trayicon.setContextMenu(traymenu)
    trayicon.show()

    sys.exit(app.exec_())


main()

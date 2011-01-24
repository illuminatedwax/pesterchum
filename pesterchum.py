# pesterchum
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import logging
import sys
import json
from PyQt4 import QtGui, QtCore

logging.basicConfig(level=logging.INFO)

class Mood(object):
    moods = ["chummy", "rancorous", "offline"]
    def __init__(self, mood):
        if type(mood) is int:
            self.mood = mood
        else:
            self.mood = self.moods.index(mood)
    def value(self):
        return self.mood
    def name(self):
        return self.moods[self.mood]

class PesterProfile(object):
    def __init__(self, handle, color=None, mood=None):
        self.handle = handle
        self.color = color
        self.mood = mood
    def initials(self):
        handle = self.handle
        caps = [l for l in handle if l.isupper()]
        if not caps:
            caps = [""]
        return (handle[0]+caps[0]).upper()
        

class pesterTheme(dict):
    def __init__(self, name):
        self.path = "themes/%s" % (name)
        fp = open(self.path+"/style.js")
        theme = json.load(fp, object_hook=self.pathHook)
        self.update(theme)
        fp.close()
    def __getitem__(self, key):
        keys = key.split("/")
        v = dict.__getitem__(self, keys.pop(0))
        for k in keys:
            v = v[k]
        return v
    def pathHook(self, d):
        from string import Template
        for (k, v) in d.iteritems():
            if type(v) is unicode:
                s = Template(v)
                d[k] = s.substitute(path=self.path)
        return d

class userConfig(object):
    def __init__(self, handle="pesterchum"):
        fp = open("%s.js" % (handle))
        self.config = json.load(fp)
        fp.close()
        self.theme = pesterTheme(self.config["theme"])
    def chums(self):
        return self.config['chums']
    def getTheme(self):
        return self.theme

class exitButton(QtGui.QPushButton):
    def __init__(self, icon, parent=None):
        QtGui.QPushButton.__init__(self, icon, "", parent)
        self.setFlat(True)
        self.setStyleSheet("QPushButton { padding: 0px; }")
        self.setAutoDefault(False)

class chumListing(QtGui.QListWidgetItem):
    def __init__(self, chum, theme):
        QtGui.QListWidgetItem.__init__(self, chum.handle)
        self.theme = theme["main/chums/moods"]
        self.chum = chum
        self.handle = chum.handle
        self.setMood(Mood("offline"))
    def setMood(self, mood):
        self.mood = mood
        self.setIcon(QtGui.QIcon(self.theme[self.mood.name()]["icon"]))
        self.setTextColor(QtGui.QColor(self.theme[self.mood.name()]["color"]))
    def __lt__(self, cl):
        h1 = self.handle.lower()
        h2 = cl.handle.lower()
        return (h1 < h2)

class chumArea(QtGui.QListWidget):
    def __init__(self, chums, theme, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        geometry = theme["main/chums/loc"] + theme["main/chums/size"]
        self.setGeometry(*geometry)
        self.setStyleSheet(theme["main/chums/style"])
        self.chums = chums
        for c in self.chums:
            chandle = c.handle
            if not self.findItems(chandle, QtCore.Qt.MatchFlags(0)):
                chumLabel = chumListing(c, theme)
                self.addItem(chumLabel)
        self.sortItems()
    def updateMood(self, handle, mood):
        chums = self.findItems(handle, QtCore.Qt.MatchFlags(0))
        for c in chums:
            c.setMood(mood)

class MovingWindow(QtGui.QFrame):
    def __init__(self, *x, **y):
        QtGui.QFrame.__init__(self, *x, **y)
        self.moving = None
        self.moveupdate = 0
    def mouseMoveEvent(self, event):
        if self.moving:
            move = event.globalPos() - self.moving
            self.move(move)
            self.moveupdate += 1
            if self.moveupdate > 5:
                self.moveupdate = 0
                self.update()
    def mousePressEvent(self, event):
        if event.button() == 1:
            self.moving = event.globalPos() - self.pos()
    def mouseReleaseEvent(self, event):
        if event.button() == 1:
            self.update()
            self.moving = None

class PesterText(QtGui.QTextEdit):
    def __init__(self, theme, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setStyleSheet(theme["convo/textarea/style"])
        self.setReadOnly(True)
    def addMessage(self, text, chum):
        if chum is None:
            chum = self.parent().mainwindow.profile
        color = chum.color
        initials = chum.initials()
        msg = str(text)
        msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.append("<span color='%s'>%s: %s</span>" % (color, initials, msg))

class PesterInput(QtGui.QLineEdit):
    def __init__(self, theme, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setStyleSheet(theme["convo/input/style"])

class PesterConvo(QtGui.QFrame):
    def __init__(self, chumlisting, initiated, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)

        self.chumlisting = chumlisting
        self.theme = mainwindow.theme
        self.mainwindow = mainwindow
        convo = self.theme["convo"]
        self.resize(*convo["size"])
        self.setStyleSheet(convo["style"])
        self.setWindowIcon(chumlisting.icon())
        self.setWindowTitle(chumlisting.handle)

        self.chumLabel = QtGui.QLabel(chumlisting.handle, self)
        self.chumLabel.setStyleSheet(self.theme["convo/chumlabel/style"])
        self.textArea = PesterText(self.theme, self)
        self.textInput = PesterInput(self.theme, self)

        self.connect(self.textInput, QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('sentMessage()'))

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.chumLabel)
        self.layout.addWidget(self.textArea)
        self.layout.addWidget(self.textInput)

        self.setLayout(self.layout)

    def updateMood(self, mood):
        icon = theme["chums/moods"][mood.name()]
        self.setWindowIcon(icon)
        # print mood update?
    def addMessage(self, text, chum=None):
        self.textArea.addMessage(text, chum)

    @QtCore.pyqtSlot()
    def sentMessage(self):
        text = self.textInput.text()
        # deal with quirks here
        self.textInput.setText("")
        self.addMessage(text, None)
        self.messageSent.emit(text, self.chumlisting)

    messageSent = QtCore.pyqtSignal(QtCore.QString, chumListing)


class PesterWindow(MovingWindow):
    def __init__(self, parent=None):
        MovingWindow.__init__(self, parent, 
                              flags=QtCore.Qt.CustomizeWindowHint)
        self.setObjectName("main")
        self.config = userConfig()
        self.theme = self.config.getTheme()
        main = self.theme["main"]
        width = int(main['width'])
        height = int(main['height'])
        self.setGeometry(100, 100, width, height)
        self.setWindowIcon(QtGui.QIcon(main["icon"]))
        self.setStyleSheet("QFrame#main { "+main["style"]+" }")

        closestyle = main["close"]
        self.closeButton = exitButton(QtGui.QIcon(closestyle["image"]), self)
        self.closeButton.move(*closestyle["loc"])
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))
        chums = [PesterProfile(c) for c in set(self.config.chums())]
        self.chumList = chumArea(chums, self.theme, self)
        self.connect(self.chumList, QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),
                     self, QtCore.SLOT('newConversation(QListWidgetItem *)'))

        self.profile = PesterProfile("superGhost", QtGui.QColor("red"), Mood(0))
        self.convos = {}
    def closeEvent(self, event):
        for c in self.convos.itervalues():
            c.close()
        event.accept()
    def newMessage(self, handle, msg):
        pass

    def updateMood(self, handle, mood):
        self.chumList.updateMood(handle, mood)
        if self.convos.has_key(handle):
            self.convos[handle].updateMood(mood)

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def newConversation(self, chum, initiated=True):
        convoWindow = PesterConvo(chum, initiated, self)
        self.connect(convoWindow, QtCore.SIGNAL('messageSent(QString, PyQt_PyObject)'),
                     self, QtCore.SIGNAL('sendMessage(QString, PyQt_PyObject)'))
        self.convos[chum.handle] = convoWindow
        
        convoWindow.show()

    sendMessage = QtCore.pyqtSignal(QtCore.QString, chumListing)

class PesterIRC(QtCore.QObject):
    def __init__(self, window):
        QtCore.QObject.__init__(self)
        self.window = window
    def IRCConnect(self):
        self.cli = IRCClient(PesterHandler, host="irc.tymoon.eu", port=6667, nick=self.window.profile.handle)
        self.cli.command_handler.window = self.window
        self.conn = self.cli.connect()
        
    @QtCore.pyqtSlot(QtCore.QString, chumListing)
    def sendMessage(self, text, chumlisting):
        handle = chumlisting.handle
        helpers.msg(self.cli, handle, text)

    @QtCore.pyqtSlot()
    def updateIRC(self):
        self.conn.next()

class PesterHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        # display msg, do other stuff
        handle = nick[0:nick.find("!")]
        if chan == "#pesterchum":
            # follow instructions
            if msg[0:6] == "MOOD >":
                try:
                    mood = Mood(int(msg[6:]))
                except ValueError:
                    mood = Mood(0)
                self.window.updateMood(handle, mood)
            elif msg[0:7] == "GETMOOD":
                mychumhandle = self.window.profile.handle
                mymood = self.window.profile.mood.value()
                if msg.find(mychumhandle, 8) != -1:
                    helpers.msg(self.client, "#pesterchum", 
                                "MOOD >%d" % (mymood))
                    
        else:
            # private message
            self.window.newMessage(handle, msg)
            pass
    def welcome(self, server, nick, msg):
        helpers.join(self.client, "#pesterchum")
        mychumhandle = self.window.profile.handle
        mymood = self.window.profile.mood.value()
        helpers.msg(self.client, "#pesterchum", "MOOD >%d" % (mymood))

        chums = self.window.chumList.chums
        chumglub = "GETMOOD "
        for c in chums:
            chandle = c.handle
            if len(chumglub+chandle) >= 510:
                helpers.msg(self.client, "#pesterchum", chumglub)
                chumglub = "GETMOOD "
            chumglub += chandle
        if chumglub != "GETMOOD ":
            helpers.msg(self.client, "#pesterchum", chumglub)


def main():

    app = QtGui.QApplication(sys.argv)
    widget = PesterWindow()
    widget.show()
    trayicon = QtGui.QSystemTrayIcon(QtGui.QIcon("themes/pesterchum/trayicon.gif"), app)
    traymenu = QtGui.QMenu()
    traymenu.addAction("Hi!! HI!!")
    trayicon.setContextMenu(traymenu)
    trayicon.show()

    irc = PesterIRC(widget)
    irc.IRCConnect()
    irc.connect(widget, QtCore.SIGNAL('sendMessage(QString, PyQt_PyObject)'),
                irc, QtCore.SLOT('sendMessage(QString, PyQt_PyObject)'))

    irctimer = QtCore.QTimer(widget)
    widget.connect(irctimer, QtCore.SIGNAL('timeout()'),
                   irc, QtCore.SLOT('updateIRC()'))
    irctimer.start()
    sys.exit(app.exec_())

main()

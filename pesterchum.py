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
    def icon(self, theme):
        f = theme["main/chums/moods"][self.name()]["icon"]
        return QtGui.QIcon(f)

class PesterProfile(object):
    def __init__(self, handle, color=QtGui.QColor("black"), 
                 mood=Mood("offline")):
        self.handle = handle
        self.color = color
        self.mood = mood
    def initials(self):
        handle = self.handle
        caps = [l for l in handle if l.isupper()]
        if not caps:
            caps = [""]
        return (handle[0]+caps[0]).upper() 
    def colorhtml(self):
        return self.color.name()
    def colorcmd(self):
        (r, g, b, a) = self.color.getRgb()
        return "%d,%d,%d" % (r,g,b)

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
        self.theme = theme
        self.chum = chum
        self.handle = chum.handle
        self.setMood(Mood("offline"))
    def setMood(self, mood):
        self.chum.mood = mood
        self.updateMood()
    def updateMood(self):
        mood = self.chum.mood
        self.mood = mood
        self.setIcon(self.mood.icon(self.theme))
        self.setTextColor(QtGui.QColor(self.theme["main/chums/moods"][self.mood.name()]["color"]))
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
        color = chum.colorhtml()
        initials = chum.initials()
        msg = str(text)
        msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.append("<span style='color:%s'>%s: %s</span>" % \
                        (color, initials, msg))

class PesterInput(QtGui.QLineEdit):
    def __init__(self, theme, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setStyleSheet(theme["convo/input/style"])

class PesterConvo(QtGui.QFrame):
    def __init__(self, chum, initiated, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)

        self.chum = chum
        self.theme = mainwindow.theme
        self.mainwindow = mainwindow
        convo = self.theme["convo"]
        self.resize(*convo["size"])
        self.setStyleSheet(convo["style"])
        self.setWindowIcon(chum.mood.icon(self.theme))
        self.setWindowTitle(chum.handle)

        self.chumLabel = QtGui.QLabel(chum.handle, self)
        self.chumLabel.setStyleSheet(self.theme["convo/chumlabel/style"])
        self.textArea = PesterText(self.theme, self)
        self.textInput = PesterInput(self.theme, self)
        self.textInput.setFocus()

        self.connect(self.textInput, QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('sentMessage()'))

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.chumLabel)
        self.layout.addWidget(self.textArea)
        self.layout.addWidget(self.textInput)

        self.setLayout(self.layout)

    def updateMood(self, mood):
        self.setWindowIcon(mood.icon(self.theme))
        # print mood update?
    def addMessage(self, text, me=True):
        if me:
            chum = self.mainwindow.profile
        else:
            chum = self.chum
        self.textArea.addMessage(text, chum)

    @QtCore.pyqtSlot()
    def sentMessage(self):
        text = self.textInput.text()
        # deal with quirks here
        self.textInput.setText("")
        self.addMessage(text, True)
        self.messageSent.emit(text, self.chum)

    messageSent = QtCore.pyqtSignal(QtCore.QString, PesterProfile)


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
                     self, QtCore.SLOT('newConversationWindow(QListWidgetItem *)'))

        self.profile = PesterProfile("superGhost", QtGui.QColor("red"), Mood(0))
        self.convos = {}
    def closeEvent(self, event):
        for c in self.convos.itervalues():
            c.close()
        event.accept()
    def newMessage(self, handle, msg):
        if not self.convos.has_key(handle):
            chum = PesterProfile(handle)
            self.newConversation(chum, False)
        convo = self.convos[handle]
        convo.addMessage(msg, False)
        # play sound here

    def changeColor(self, handle, color):
        pass

    def updateMood(self, handle, mood):
        self.chumList.updateMood(handle, mood)
        if self.convos.has_key(handle):
            self.convos[handle].updateMood(mood)
    def newConversation(self, chum, initiated=True):
        convoWindow = PesterConvo(chum, initiated, self)
        self.connect(convoWindow, QtCore.SIGNAL('messageSent(QString, PyQt_PyObject)'),
                     self, QtCore.SIGNAL('sendMessage(QString, PyQt_PyObject)'))
        self.convos[chum.handle] = convoWindow
        self.newConvoStarted.emit(QtCore.QString(chum.handle), initiated)
        convoWindow.show()

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def newConversationWindow(self, chumlisting):
        chum = chumlisting.chum
        self.newConversation(chum)

    newConvoStarted = QtCore.pyqtSignal(QtCore.QString, bool, name="newConvoStarted")
    sendMessage = QtCore.pyqtSignal(QtCore.QString, PesterProfile)

class PesterIRC(QtCore.QObject):
    def __init__(self, window):
        QtCore.QObject.__init__(self)
        self.window = window
    def IRCConnect(self):
        self.cli = IRCClient(PesterHandler, host="irc.tymoon.eu", port=6667, nick=self.window.profile.handle)
        self.cli.command_handler.window = self.window
        self.conn = self.cli.connect()

    def getMood(self, *chums):
        self.cli.command_handler.getMood(*chums)
        
    @QtCore.pyqtSlot(QtCore.QString, PesterProfile)
    def sendMessage(self, text, chum):
        handle = chum.handle
        helpers.msg(self.cli, handle, text)

    @QtCore.pyqtSlot(QtCore.QString, bool)
    def startConvo(self, handle, initiated):
        h = str(handle)
        if initiated:
            helpers.msg(self.cli, h, "PESTERCHUM:BEGIN")
        helpers.msg(self.cli, h, "COLOR >%s" % (self.window.profile.colorcmd()))

    @QtCore.pyqtSlot()
    def updateIRC(self):
        self.conn.next()

class PesterHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        # display msg, do other stuff
        # silently ignore CTCP
        if msg[0] == '\x01':
            return
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
            if msg[0:7] == "COLOR >":
                colors = msg[7:].split(",")
                try:
                    colors = [int(d) for d in colors]
                except ValueError:
                    colors = [0,0,0]
                color = QtGui.QColor(*colors)
                self.window.changeColor(handle, color)
            elif msg == "PESTERCHUM:BEGIN":
                chum = PesterProfile(handle)
                self.window.newConversation(chum, False)
            else:
                self.window.newMessage(handle, msg)


    def welcome(self, server, nick, msg):
        helpers.join(self.client, "#pesterchum")
        mychumhandle = self.window.profile.handle
        mymood = self.window.profile.mood.value()
        helpers.msg(self.client, "#pesterchum", "MOOD >%d" % (mymood))

        chums = self.window.chumList.chums
        self.getMood(*chums)
    def getMood(self, *chums):
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
    irc.connect(widget, 
                QtCore.SIGNAL('newConvoStarted(QString, bool)'),
                irc, QtCore.SLOT('startConvo(QString, bool)'))

    irctimer = QtCore.QTimer(widget)
    widget.connect(irctimer, QtCore.SIGNAL('timeout()'),
                   irc, QtCore.SLOT('updateIRC()'))
    irctimer.start()
    sys.exit(app.exec_())

main()

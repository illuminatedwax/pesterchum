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

class PesterIRC(QtCore.QObject):
    def __init__(self, window):
        QtCore.QObject.__init__(self)
        self.window = window
    def IRCConnect(self):
        self.cli = IRCClient(PesterHandler, host="irc.tymoon.eu", port=6667, nick=self.window.currentHandle)
        self.cli.command_handler.window = self.window
        self.conn = self.cli.connect()
        
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
                mychumhandle = self.window.currentHandle
                mymood = self.window.currentMood.value()
                if msg.find(mychumhandle, 8) != -1:
                    helpers.msg(self.client, "#pesterchum", 
                                "MOOD >%d" % (mymood))
                    
        else:
            # private message
            pass
    def welcome(self, server, nick, msg):
        helpers.join(self.client, "#pesterchum")
        mychumhandle = self.window.currentHandle
        mymood = self.window.currentMood.value()
        helpers.msg(self.client, "#pesterchum", "MOOD >%d" % (mymood))

        chums = self.window.chumList.chums
        chumglob = "GETMOOD "
        for c in chums:
            if len(chumglob+c) >= 510:
                helpers.msg(self.client, "#pesterchum", chumglob)
                chumglob = "GETMOOD "
            chumglob += c
        if chumglob != "GETMOOD ":
            helpers.msg(self.client, "#pesterchum", chumglob)

class pesterTheme(object):
    def __init__(self, name):
        self.path = "themes/%s" % (name)
        fp = open(self.path+"/style.js")
        self.theme = json.load(fp, object_hook=self.pathHook)
        fp.close()
    def getSection(self, section):
        return self.theme[section]
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
    def __init__(self, chumhandle, moodtheme):
        QtGui.QListWidgetItem.__init__(self, chumhandle)
        self.theme = moodtheme
        self.handle = chumhandle
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
        geometry = theme["loc"] + theme["size"]
        self.setGeometry(*geometry)
        self.setStyleSheet(theme["style"])
        self.chums = chums
        for c in self.chums:
            if not self.findItems(c, QtCore.Qt.MatchFlags(0)):
                chumLabel = chumListing(c, theme["moods"])
                self.addItem(chumLabel)
        self.sortItems()
    def updateMood(self, nick, mood):
        chums = self.findItems(nick, QtCore.Qt.MatchFlags(0))
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

class PesterWindow(MovingWindow):
    def __init__(self, parent=None):
        MovingWindow.__init__(self, parent, 
                              flags=QtCore.Qt.CustomizeWindowHint)
        self.setObjectName("main")
        self.config = userConfig()
        theme = self.config.getTheme()
        main = theme.getSection("main")
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
        self.chumList = chumArea(self.config.chums(), main["chums"], self)

        self.currentHandle = "superGhost"
        self.currentMood = Mood(0)
        self.convos = {}
    def updateMood(self, nick, mood):
        self.chumList.updateMood(nick, mood)
    def newConversation(self, nick):
        convoWindow = PesterConvo(nick, self.theme)
        self.convos[nick] = convoWindow



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
    irctimer = QtCore.QTimer(widget)
    widget.connect(irctimer, QtCore.SIGNAL('timeout()'),
                   irc, QtCore.SLOT('updateIRC()'))
    irctimer.start()
    sys.exit(app.exec_())

main()

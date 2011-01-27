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
        try:
            name = self.moods[self.mood]
        except IndexError:
            name = "chummy"
        return name
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
    def __init__(self):
        fp = open("pesterchum.js")
        self.config = json.load(fp)
        fp.close()
        self.theme = pesterTheme(self.config["theme"])
    def chums(self):
        return self.config['chums']
    def getTheme(self):
        return self.theme
    def tabs(self):
        return self.config["tabs"]
    def set(self, item, setting):
        self.config[item] = setting
        fp = open("pesterchum.js", 'w')
        json.dump(self.config, fp)
        fp.close()

class PesterOptions(QtGui.QDialog):
    def __init__(self, config, theme, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.config = config
        self.theme = theme
        self.setStyleSheet(self.theme["main/defaultwindow/style"])

        self.tabcheck = QtGui.QCheckBox(self)
        if self.config.tabs():
            self.tabcheck.setChecked(True)
        self.tablabel = QtGui.QLabel("Tabbed Conversations", self)
        layout_1 = QtGui.QHBoxLayout()
        layout_1.addWidget(self.tablabel)
        layout_1.addWidget(self.tabcheck)
        
        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addLayout(layout_1)
        layout_0.addWidget(self.ok)

        self.setLayout(layout_0)

class WMButton(QtGui.QPushButton):
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

class PesterTabWindow(QtGui.QFrame):
    def __init__(self, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.mainwindow = mainwindow
        self.theme = mainwindow.theme
        self.resize(*self.theme["convo/size"])
        self.setStyleSheet(self.theme["convo/style"])

        self.tabs = QtGui.QTabBar(self)
        self.tabs.setTabsClosable(True)
        self.connect(self.tabs, QtCore.SIGNAL('currentChanged(int)'),
                     self, QtCore.SLOT('changeTab(int)'))
        self.connect(self.tabs, QtCore.SIGNAL('tabCloseRequested(int)'),
                     self, QtCore.SLOT('tabClose(int)'))
        self.tabs.setShape(self.theme["convo/tabstyle"])


        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.convos = {}
        self.tabIndices = {}
        self.currentConvo = None
        self.changedTab = False
    def addChat(self, convo):
        self.convos[convo.chum.handle] = convo
        # either addTab or setCurrentIndex will trigger changed()
        newindex = self.tabs.addTab(convo.chum.handle)
        self.tabIndices[convo.chum.handle] = newindex
        self.tabs.setCurrentIndex(newindex)
        self.tabs.setTabIcon(newindex, convo.chum.mood.icon(self.theme))
    def showChat(self, handle):
        self.tabs.setCurrentIndex(self.tabIndices[handle])
    def keyPressEvent(self, event):
        keypress = event.key()
        mods = event.modifiers()
        if ((mods & QtCore.Qt.ControlModifier) and 
            keypress == QtCore.Qt.Key_Tab):
            nexti = (self.tabIndices[self.currentConvo.chum.handle] + 1) % self.tabs.count()
            self.tabs.setCurrentIndex(nexti)

    def updateMood(self, handle, mood):
        i = self.tabIndices[handle]
        self.tabs.setTabIcon(i, mood.icon(self.theme))
    def closeEvent(self, event):
        while self.tabs.count() > 0:
            self.tabClose(0)
        self.windowClosed.emit()

    @QtCore.pyqtSlot(int)
    def tabClose(self, i):
        handle = unicode(self.tabs.tabText(i))
        convo = self.convos[handle]
        del self.convos[handle]
        del self.tabIndices[handle]
        self.tabs.removeTab(i)
        for (h, j) in self.tabIndices.iteritems():
            if j > i:
                self.tabIndices[h] = j-1
        self.layout.removeWidget(convo)
        convo.close()
        if self.tabs.count() == 0:
            self.close()
            return
        if self.currentConvo == convo:
            currenti = self.tabs.currentIndex()
            currenth = unicode(self.tabs.tabText(currenti))
            self.currentConvo = self.convos[currenth]
        self.currentConvo.raiseChat()

    @QtCore.pyqtSlot(int)
    def changeTab(self, i):
        if i < 0:
            return
        if self.changedTab:
            self.changedTab = False
            return
        handle = unicode(self.tabs.tabText(i))
        convo = self.convos[handle]
        if self.currentConvo:
            self.layout.removeWidget(self.currentConvo)
        self.currentConvo = convo
        self.layout.addWidget(convo)
        self.setWindowIcon(convo.chum.mood.icon(self.theme))
        self.activateWindow()
        self.raise_()
        convo.raiseChat()

    windowClosed = QtCore.pyqtSignal()

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

        if parent:
            parent.addChat(self)

    def updateMood(self, mood):
        if self.parent():
            self.parent().updateMood(self.chum.handle, mood)
        else:
            self.setWindowIcon(mood.icon(self.theme))
        # print mood update?
    def addMessage(self, text, me=True):
        if me:
            chum = self.mainwindow.profile
        else:
            chum = self.chum
        self.textArea.addMessage(text, chum)
    def raiseChat(self):
        self.activateWindow()
        self.raise_()
        self.textInput.setFocus()

    def showChat(self):
        if self.parent():
            self.parent().showChat(self.chum.handle)
        self.raiseChat()

    def closeEvent(self, event):
        self.windowClosed.emit(self.chum.handle)

    @QtCore.pyqtSlot()
    def sentMessage(self):
        text = self.textInput.text()
        # deal with quirks here
        self.textInput.setText("")
        self.addMessage(text, True)
        self.messageSent.emit(text, self.chum)

    messageSent = QtCore.pyqtSignal(QtCore.QString, PesterProfile)
    windowClosed = QtCore.pyqtSignal(QtCore.QString)

class PesterWindow(MovingWindow):
    def __init__(self, parent=None):
        MovingWindow.__init__(self, parent, 
                              flags=QtCore.Qt.CustomizeWindowHint)
        self.setObjectName("main")
        self.config = userConfig()
        self.theme = self.config.getTheme()
        main = self.theme["main"]
        size = main['size']
        self.setGeometry(100, 100, size[0], size[1])
        self.setWindowIcon(QtGui.QIcon(main["icon"]))
        self.setStyleSheet("QFrame#main { "+main["style"]+" }")

        opts = QtGui.QAction("OPTIONS", self)
        self.connect(opts, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('openOpts()'))
        exitaction = QtGui.QAction("EXIT", self)
        self.connect(exitaction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('close()'))
        self.menu = QtGui.QMenuBar(self)
        qmenustyle = "QMenu { background: transparent; %s } QMenu::item::selected { %s }" % (self.theme["main/menu/style"], self.theme["main/menu/selected"])

        filemenu = self.menu.addMenu("FILE")
        filemenu.addAction(opts)
        filemenu.addAction(exitaction)
        filemenu.setStyleSheet(qmenustyle)
        self.menu.setStyleSheet("QMenuBar { background: transparent; %s } QMenuBar::item { background: transparent; } " % (self.theme["main/menubar/style"]))

        closestyle = main["close"]
        self.closeButton = WMButton(QtGui.QIcon(closestyle["image"]), self)
        self.closeButton.move(*closestyle["loc"])
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))
        self.miniButton = WMButton(QtGui.QIcon(self.theme["main/minimize/image"]), self)
        self.miniButton.move(*(self.theme["main/minimize/loc"]))
        self.connect(self.miniButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('showMinimized()'))

        chums = [PesterProfile(c) for c in set(self.config.chums())]
        self.chumList = chumArea(chums, self.theme, self)
        self.connect(self.chumList, QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),
                     self, QtCore.SLOT('newConversationWindow(QListWidgetItem *)'))

        self.profile = PesterProfile("superGhost", QtGui.QColor("red"), Mood(0))
        self.convos = {}
        self.tabconvo = None
        self.optionmenu = None
    def closeEvent(self, event):
        for c in self.convos.values():
            c.close()
        if self.tabconvo:
            self.tabconvo.close()
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
        if self.convos.has_key(chum.handle):
            self.convos[chum.handle].showChat()
            if not initiated:
                # self.convos[chum.handle]
                # add pesterchum:begin
                pass
            return
        if self.config.tabs():
            if not self.tabconvo:
                self.tabconvo = PesterTabWindow(self)
                self.connect(self.tabconvo, QtCore.SIGNAL('windowClosed()'),
                             self, QtCore.SLOT('tabsClosed()'))
            convoWindow = PesterConvo(chum, initiated, self, self.tabconvo)
            self.tabconvo.show()
        else:
            convoWindow = PesterConvo(chum, initiated, self)
        self.connect(convoWindow, QtCore.SIGNAL('messageSent(QString, PyQt_PyObject)'),
                     self, QtCore.SIGNAL('sendMessage(QString, PyQt_PyObject)'))
        self.connect(convoWindow, QtCore.SIGNAL('windowClosed(QString)'),
                     self, QtCore.SLOT('closeConvo(QString)'))
        self.convos[chum.handle] = convoWindow
        self.newConvoStarted.emit(QtCore.QString(chum.handle), initiated)
        convoWindow.show()

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def newConversationWindow(self, chumlisting):
        chum = chumlisting.chum
        self.newConversation(chum)
    @QtCore.pyqtSlot(QtCore.QString)
    def closeConvo(self, handle):
        h = str(handle)
        del self.convos[h]
        self.convoClosed.emit(handle)
    @QtCore.pyqtSlot(QtCore.QString)
    def tabsClosed(self):
        del self.tabconvo
        self.tabconvo = None

    @QtCore.pyqtSlot(QtCore.QString, Mood)
    def updateMoodSlot(self, handle, mood):
        h = str(handle)
        self.updateMood(h, mood)

    @QtCore.pyqtSlot(QtCore.QString, QtGui.QColor)
    def updateColorSlot(self, handle, color):
        h = str(handle)
        self.changeColor(h, color)

    @QtCore.pyqtSlot(PesterProfile)
    def pesterchumBeginSlot(self, chum):
        self.newConversation(chum, False)

    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString)
    def deliverMessage(self, handle, msg):
        h = str(handle)
        m = str(msg)
        self.newMessage(h, m)

    @QtCore.pyqtSlot()
    def openOpts(self):
        if not self.optionmenu:
            self.optionmenu = PesterOptions(self.config, self.theme, self)
            self.connect(self.optionmenu, QtCore.SIGNAL('accepted()'),
                         self, QtCore.SLOT('updateOptions()'))
            self.optionmenu.show()
            self.optionmenu.raise_()
            self.optionmenu.activateWindow()
    @QtCore.pyqtSlot()
    def updateOptions(self):
        # tabs
        curtab = self.config.tabs()
        tabsetting = self.optionmenu.tabcheck.isChecked()
        if curtab and not tabsetting:
            # split tabs into windows
            # save options
            self.config.set("tabs", tabsetting)
            pass
        elif tabsetting and not curtab:
            # combine
            # save options
            self.config.set("tabs", tabsetting)
            pass
        self.optionmenu = None
        
    newConvoStarted = QtCore.pyqtSignal(QtCore.QString, bool, name="newConvoStarted")
    sendMessage = QtCore.pyqtSignal(QtCore.QString, PesterProfile)
    convoClosed = QtCore.pyqtSignal(QtCore.QString)

class PesterIRC(QtCore.QObject):
    def __init__(self, profile, chums):
        QtCore.QObject.__init__(self)
        self.profile = profile
        self.chums = chums
    def IRCConnect(self):
        self.cli = IRCClient(PesterHandler, host="irc.tymoon.eu", port=6667, nick=self.profile.handle, blocking=True)
        self.cli.command_handler.parent = self
        self.cli.command_handler.profile = self.profile
        self.cli.command_handler.chums = self.chums
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
        helpers.msg(self.cli, h, "COLOR >%s" % (self.profile.colorcmd()))
    @QtCore.pyqtSlot(QtCore.QString)
    def endConvo(self, handle):
        h = str(handle)
        helpers.msg(self.cli, h, "PESTERCHUM:CEASE")

    def updateIRC(self):
        self.conn.next()

    moodUpdated = QtCore.pyqtSignal(QtCore.QString, Mood)
    colorUpdated = QtCore.pyqtSignal(QtCore.QString, QtGui.QColor)
    pesterchumBegin = QtCore.pyqtSignal(PesterProfile)
    messageReceived = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)


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
                self.parent.moodUpdated.emit(handle, mood)
            elif msg[0:7] == "GETMOOD":
                mychumhandle = self.profile.handle
                mymood = self.profile.mood.value()
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
                self.parent.colorUpdated.emit(handle, color)
            elif msg == "PESTERCHUM:BEGIN":
                chum = PesterProfile(handle)
                self.parent.pesterchumBegin.emit(chum)
            else:
                self.parent.messageReceived.emit(handle, msg)


    def welcome(self, server, nick, msg):
        helpers.join(self.client, "#pesterchum")
        mychumhandle = self.profile.handle
        mymood = self.profile.mood.value()
        helpers.msg(self.client, "#pesterchum", "MOOD >%d" % (mymood))

        chums = self.chums
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

class IRCThread(QtCore.QThread):
    def __init__(self, ircobj):
        QtCore.QThread.__init__(self)
        self.irc = ircobj
    def run(self):
        irc = self.irc
        while 1:
            irc.updateIRC()

def main():

    app = QtGui.QApplication(sys.argv)
    widget = PesterWindow()
    widget.show()
    trayicon = QtGui.QSystemTrayIcon(QtGui.QIcon("themes/pesterchum/trayicon.gif"), app)
    traymenu = QtGui.QMenu()
    traymenu.addAction("Hi!! HI!!")
    trayicon.setContextMenu(traymenu)
    trayicon.show()

    irc = PesterIRC(widget.profile, widget.chumList.chums)
    irc.IRCConnect()
    irc.connect(widget, QtCore.SIGNAL('sendMessage(QString, PyQt_PyObject)'),
                irc, QtCore.SLOT('sendMessage(QString, PyQt_PyObject)'))
    irc.connect(widget, 
                QtCore.SIGNAL('newConvoStarted(QString, bool)'),
                irc, QtCore.SLOT('startConvo(QString, bool)'))
    irc.connect(widget,
                QtCore.SIGNAL('convoClosed(QString)'),
                irc, QtCore.SLOT('endConvo(QString)'))
    irc.connect(irc, 
                QtCore.SIGNAL('moodUpdated(QString, PyQt_PyObject)'),
                widget, 
                QtCore.SLOT('updateMoodSlot(QString, PyQt_PyObject)'))
    irc.connect(irc,
                QtCore.SIGNAL('colorUpdated(QString, QColor)'),
                widget,
                QtCore.SLOT('updateColorSlot(QString, QColor)'))
    irc.connect(irc,
                QtCore.SIGNAL('pesterchumBegin(PyQt_PyObject)'),
                widget,
                QtCore.SLOT('pesterchumBeginSlot(PyQt_PyObject)'))
    irc.connect(irc,
                QtCore.SIGNAL('messageReceived(QString, QString)'),
                widget,
                QtCore.SLOT('deliverMessage(QString, QString)'))

    ircapp = IRCThread(irc)
    ircapp.start()
    sys.exit(app.exec_())

main()

# pesterchum
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import logging
import os, sys
import os.path
from datetime import *
import random
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
    def beganpestermsg(self, otherchum):
        return "<span style='color:black;'>-- %s <span style='color:%s'>[%s]</span> began pestering %s <span style='color:%s'>[%s]</span> at %s --</span>" % (self.handle, self.colorhtml(), self.initials(), otherchum.handle, otherchum.colorhtml(), otherchum.initials(), datetime.now().strftime("%H:%M"))
    def ceasedpestermsg(self, otherchum):
        return "<span style='color:black;'>-- %s <span style='color:%s'>[%s]</span> ceased pestering %s <span style='color:%s'>[%s]</span> at %s --</span>" % (self.handle, self.colorhtml(), self.initials(), otherchum.handle, otherchum.colorhtml(), otherchum.initials(), datetime.now().strftime("%H:%M"))


class pesterTheme(dict):
    def __init__(self, name):
        self.path = "themes/%s" % (name)
        self.name = name
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
        if self.config.has_key("defaultprofile"):
            self.userprofile = userProfile(self.config["defaultprofile"])
        else:
            self.userprofile = None
    def chums(self):
        return self.config['chums']
    def defaultprofile(self):
        try:
            return self.config['defaultprofile']
        except KeyError:
            return None
    def tabs(self):
        return self.config["tabs"]
    def set(self, item, setting):
        self.config[item] = setting
        fp = open("pesterchum.js", 'w')
        json.dump(self.config, fp)
        fp.close()
    def availableThemes(self):
        themes = []
        for dirname, dirnames, filenames in os.walk('themes'):
            for d in dirnames:
                themes.append(d)
        themes.sort()
        return themes
    def availableProfiles(self):
        profs = []
        for dirname, dirnames, filenames in os.walk('profiles'):
            for filename in filenames:
                l = len(filename)
                if filename[l-3:l] == ".js":
                    profs.append(filename[0:l-3])
        profs.sort()
        return [userProfile(p) for p in profs]
class userProfile(object):
    def __init__(self, user):
        if type(user) is PesterProfile:
            self.chat = user
            self.userprofile = {"handle":user.handle,
                                "color": unicode(user.color.name()),
                                "quirks": [],
                                "theme": "pesterchum"}
            self.theme = pesterTheme("pesterchum")
            self.quirks = pesterQuirks([])
        else:
            fp = open("profiles/%s.js" % (user))
            self.userprofile = json.load(fp)
            fp.close()
            self.chat = PesterProfile(self.userprofile["handle"],
                                      QtGui.QColor(self.userprofile["color"]),
                                      Mood(0))
            self.theme = pesterTheme(self.userprofile["theme"])
            self.quirks = pesterQuirks(self.userprofile["quirks"])
    def getTheme(self):
        return self.theme
    def save(self):
        handle = self.chat.handle
        fp = open("profiles/%s.js" % (handle), 'w')
        json.dump(self.userprofile, fp)
        fp.close()
    @staticmethod
    def newUserProfile(chatprofile):
        if os.path.exists("profiles/%s.js" % (chatprofile.handle)):
            newprofile = userProfile(chatprofile.handle)
        else:
            newprofile = userProfile(chatprofile)
            newprofile.save()
        return newprofile
        
class pesterQuirks(object):
    def __init__(self, quirklist):
        self.quirklist = quirklist

class PesterChooseTheme(QtGui.QDialog):
    def __init__(self, config, theme, parent):
        QtGui.QDialog.__init__(self, parent)
        self.config = config
        self.theme = theme
        self.parent = parent
        self.setStyleSheet(self.theme["main/defaultwindow/style"])
        self.setWindowTitle("Pick a theme")

        instructions = QtGui.QLabel("Pick a theme:")

        avail_themes = config.availableThemes()
        self.themeBox = QtGui.QComboBox(self)
        for (i, t) in enumerate(avail_themes):
            self.themeBox.addItem(t)
            if t == theme.name:
                self.themeBox.setCurrentIndex(i)

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
        layout_0.addWidget(instructions)
        layout_0.addWidget(self.themeBox)
        layout_0.addLayout(layout_ok)

        self.setLayout(layout_0)

        self.connect(self, QtCore.SIGNAL('accepted()'),
                     parent, QtCore.SLOT('themeSelected()'))
        self.connect(self, QtCore.SIGNAL('rejected()'),
                     parent, QtCore.SLOT('closeTheme()'))

class PesterChooseProfile(QtGui.QDialog):
    def __init__(self, userprofile, config, theme, parent, collision=None):
        QtGui.QDialog.__init__(self, parent)
        self.userprofile = userprofile
        self.theme = theme
        self.config = config
        self.parent = parent
        self.setStyleSheet(self.theme["main/defaultwindow/style"])

        self.chumHandle = QtGui.QLineEdit(self)
        self.chumHandle.setMinimumWidth(200)
        self.chumHandleLabel = QtGui.QLabel(self.theme["main/labels/mychumhandle"], self)
        self.chumColorButton = QtGui.QPushButton(self)
        self.chumColorButton.resize(50, 20)
        self.chumColorButton.setStyleSheet("background: %s" % (userprofile.chat.colorhtml()))
        self.chumcolor = userprofile.chat.color
        self.connect(self.chumColorButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('openColorDialog()'))
        layout_1 = QtGui.QHBoxLayout()
        layout_1.addWidget(self.chumHandleLabel)
        layout_1.addWidget(self.chumHandle)
        layout_1.addWidget(self.chumColorButton)

        # available profiles?
        avail_profiles = self.config.availableProfiles()
        if avail_profiles:
            self.profileBox = QtGui.QComboBox(self)
            self.profileBox.addItem("Choose a profile...")
            for p in avail_profiles:
                self.profileBox.addItem(p.chat.handle)
        else:
            self.profileBox = None

        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('validateProfile()'))
        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        layout_ok = QtGui.QHBoxLayout()
        layout_ok.addWidget(self.cancel)
        layout_ok.addWidget(self.ok)

        layout_0 = QtGui.QVBoxLayout()
        if collision:
            collision_warning = QtGui.QLabel("%s is taken already! Pick a new profile." % (collision))
            layout_0.addWidget(collision_warning)
        layout_0.addLayout(layout_1)
        if avail_profiles:
            profileLabel = QtGui.QLabel("Or choose an existing profile:", self)
            layout_0.addWidget(profileLabel)
            layout_0.addWidget(self.profileBox)
        layout_0.addLayout(layout_ok)
        self.errorMsg = QtGui.QLabel(self)
        self.errorMsg.setStyleSheet("color:red;")
        layout_0.addWidget(self.errorMsg)
        self.setLayout(layout_0)

        self.connect(self, QtCore.SIGNAL('accepted()'),
                     parent, QtCore.SLOT('profileSelected()'))
        self.connect(self, QtCore.SIGNAL('rejected()'),
                     parent, QtCore.SLOT('closeProfile()'))

    @QtCore.pyqtSlot()
    def openColorDialog(self):
        self.colorDialog = QtGui.QColorDialog(self)
        color = self.colorDialog.getColor(initial=self.userprofile.chat.color)
        self.chumColorButton.setStyleSheet("background: %s" % color.name())
        self.chumcolor = color
        self.colorDialog = None

    @QtCore.pyqtSlot()
    def validateProfile(self):
        if not self.profileBox or self.profileBox.currentIndex() == 0:
            handle = unicode(self.chumHandle.text())
            if len(handle) > 256:
                self.errorMsg.setText("PROFILE HANDLE IS TOO LONG")
                return
            caps = [l for l in handle if l.isupper()]
            if len(caps) != 1 or handle[0].isupper():
                self.errorMsg.setText("NOT A VALID CHUMTAG")
                return
        self.accept()

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
        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        layout_2 = QtGui.QHBoxLayout()
        layout_2.addWidget(self.cancel)
        layout_2.addWidget(self.ok)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addLayout(layout_1)
        layout_0.addLayout(layout_2)

        self.setLayout(layout_0)

class WMButton(QtGui.QPushButton):
    def __init__(self, icon, parent=None):
        QtGui.QPushButton.__init__(self, icon, "", parent)
        self.setFlat(True)
        self.setStyleSheet("QPushButton { padding: 0px; }")
        self.setAutoDefault(False)

class chumListing(QtGui.QListWidgetItem):
    def __init__(self, chum, window):
        QtGui.QListWidgetItem.__init__(self, chum.handle)
        self.mainwindow = window
        self.chum = chum
        self.handle = chum.handle
        self.setMood(Mood("offline"))
    def setMood(self, mood):
        self.chum.mood = mood
        self.updateMood()
    def setColor(self, color):
        self.chum.color = color
    def updateMood(self):
        mood = self.chum.mood
        self.mood = mood
        self.setIcon(self.mood.icon(self.mainwindow.theme))
        self.setTextColor(QtGui.QColor(self.mainwindow.theme["main/chums/moods"][self.mood.name()]["color"]))
    def changeTheme(self, theme):
        self.setIcon(self.mood.icon(theme))
        self.setTextColor(QtGui.QColor(theme["main/chums/moods"][self.mood.name()]["color"]))
    def __lt__(self, cl):
        h1 = self.handle.lower()
        h2 = cl.handle.lower()
        return (h1 < h2)

class chumArea(QtGui.QListWidget):
    def __init__(self, chums, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        self.mainwindow = parent
        theme = self.mainwindow.theme
        geometry = theme["main/chums/loc"] + theme["main/chums/size"]
        self.setGeometry(*geometry)
        self.setStyleSheet(theme["main/chums/style"])
        self.chums = chums
        for c in self.chums:
            chandle = c.handle
            if not self.findItems(chandle, QtCore.Qt.MatchFlags(0)):
                chumLabel = chumListing(c, self.mainwindow)
                self.addItem(chumLabel)
        self.sortItems()
    def updateMood(self, handle, mood):
        chums = self.findItems(handle, QtCore.Qt.MatchFlags(0))
        for c in chums:
            c.setMood(mood)
    def updateColor(self, handle, color):
        chums = self.findItems(handle, QtCore.Qt.MatchFlags(0))
        for c in chums:
            c.setColor(color)
    def changeTheme(self, theme):
        self.setGeometry(*(theme["main/chums/loc"]+theme["main/chums/size"]))
        self.setStyleSheet(theme["main/chums/style"])
        chums = [self.item(i) for i in range(0, self.count())]
        for c in chums:
            c.changeTheme(theme)

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
        self.resize(*self.mainwindow.theme["convo/size"])
        self.setStyleSheet(self.mainwindow.theme["convo/style"])

        self.tabs = QtGui.QTabBar(self)
        self.tabs.setTabsClosable(True)
        self.connect(self.tabs, QtCore.SIGNAL('currentChanged(int)'),
                     self, QtCore.SLOT('changeTab(int)'))
        self.connect(self.tabs, QtCore.SIGNAL('tabCloseRequested(int)'),
                     self, QtCore.SLOT('tabClose(int)'))
        self.tabs.setShape(self.mainwindow.theme["convo/tabstyle"])


        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.convos = {}
        self.tabIndices = {}
        self.currentConvo = None
        self.changedTab = False
        self.softclose = False
    def addChat(self, convo):
        self.convos[convo.chum.handle] = convo
        # either addTab or setCurrentIndex will trigger changed()
        newindex = self.tabs.addTab(convo.chum.handle)
        self.tabIndices[convo.chum.handle] = newindex
        self.tabs.setCurrentIndex(newindex)
        self.tabs.setTabIcon(newindex, convo.chum.mood.icon(self.mainwindow.theme))
    def showChat(self, handle):
        self.tabs.setCurrentIndex(self.tabIndices[handle])
    def keyPressEvent(self, event):
        keypress = event.key()
        mods = event.modifiers()
        if ((mods & QtCore.Qt.ControlModifier) and 
            keypress == QtCore.Qt.Key_Tab):
            nexti = (self.tabIndices[self.currentConvo.chum.handle] + 1) % self.tabs.count()
            self.tabs.setCurrentIndex(nexti)

    def closeSoft(self):
        self.softclose = True
        self.close()
    def updateMood(self, handle, mood):
        i = self.tabIndices[handle]
        self.tabs.setTabIcon(i, mood.icon(self.mainwindow.theme))
        if self.tabs.currentIndex() == i:
            self.setWindowIcon(mood.icon(self.mainwindow.theme))
    def closeEvent(self, event):
        if not self.softclose:
            while self.tabs.count() > 0:
                self.tabClose(0)
        self.windowClosed.emit()
    def changeTheme(self, theme):
        self.resize(*theme["convo/size"])
        self.setStyleSheet(theme["convo/style"])
        self.tabs.setShape(theme["convo/tabstyle"])
        for c in self.convos.values():
            tabi = self.tabIndices[c.chum.handle]
            self.tabs.setTabIcon(tabi, c.chum.mood.icon(theme))
        currentHandle = unicode(self.tabs.tabText(self.tabs.currentIndex()))
        self.setWindowIcon(self.convos[currentHandle].chum.mood.icon(theme))

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
        self.setWindowIcon(convo.chum.mood.icon(self.mainwindow.theme))
        self.setWindowTitle(convo.chum.handle)
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
        msg = unicode(text)
        if msg == "PESTERCHUM:BEGIN":
            parent = self.parent()
            parent.setChumOpen(True)
            window = parent.mainwindow
            me = window.profile
            msg = chum.beganpestermsg(me)
            self.append(msg)
        elif msg == "PESTERCHUM:CEASE":
            parent = self.parent()
            parent.setChumOpen(False)
            window = parent.mainwindow
            me = window.profile
            msg = chum.ceasedpestermsg(me)
            self.append(msg)
        else:
            if not self.parent().chumopen and chum is not self.parent().mainwindow.profile:
                me = self.parent().mainwindow.profile
                beginmsg = chum.beganpestermsg(me)
                self.parent().setChumOpen(True)
                self.append(beginmsg)
                
            msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            self.append("<span style='color:%s'>%s: %s</span>" % \
                            (color, initials, msg))
    def changeTheme(self, theme):
        self.setStyleSheet(theme["convo/textarea/style"])

class PesterInput(QtGui.QLineEdit):
    def __init__(self, theme, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setStyleSheet(theme["convo/input/style"])
    def changeTheme(self, theme):
        self.setStyleSheet(theme["convo/input/style"])

class PesterConvo(QtGui.QFrame):
    def __init__(self, chum, initiated, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)

        self.chum = chum
        self.mainwindow = mainwindow
        convo = self.mainwindow.theme["convo"]
        self.resize(*convo["size"])
        self.setStyleSheet(convo["style"])
        self.setWindowIcon(chum.mood.icon(self.mainwindow.theme))
        self.setWindowTitle(chum.handle)

        self.chumLabel = QtGui.QLabel(chum.handle, self)
        self.chumLabel.setStyleSheet(self.mainwindow.theme["convo/chumlabel/style"])
        self.textArea = PesterText(self.mainwindow.theme, self)
        self.textInput = PesterInput(self.mainwindow.theme, self)
        self.textInput.setFocus()

        self.connect(self.textInput, QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('sentMessage()'))

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.chumLabel)
        self.layout.addWidget(self.textArea)
        self.layout.addWidget(self.textInput)

        self.setLayout(self.layout)

        self.chumopen = False

        if parent:
            parent.addChat(self)
        if initiated:
            msg = self.mainwindow.profile.beganpestermsg(self.chum)
            self.textArea.append(msg)

    def updateMood(self, mood):
        if self.parent():
            self.parent().updateMood(self.chum.handle, mood)
        else:
            self.setWindowIcon(mood.icon(self.mainwindow.theme))
        # print mood update?
    def updateColor(self, color):
        self.chum.color = color
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
    def setChumOpen(self, o):
        self.chumopen = o
    def changeTheme(self, theme):
        self.resize(*theme["convo/size"])
        self.setStyleSheet(theme["convo/style"])
        self.setWindowIcon(self.chum.mood.icon(theme))
        self.chumLabel.setStyleSheet(theme["convo/chumlabel/style"])
        self.textArea.changeTheme(theme)
        self.textInput.changeTheme(theme)

    @QtCore.pyqtSlot()
    def sentMessage(self):
        text = self.textInput.text()
        # deal with quirks here
        self.textInput.setText("")
        self.addMessage(text, True)
        # if ceased, rebegin
        if not self.chumopen:
            self.mainwindow.newConvoStarted.emit(QtCore.QString(self.chum.handle), True)
        self.messageSent.emit(text, self.chum)

    messageSent = QtCore.pyqtSignal(QtCore.QString, PesterProfile)
    windowClosed = QtCore.pyqtSignal(QtCore.QString)

class PesterWindow(MovingWindow):
    def __init__(self, parent=None):
        MovingWindow.__init__(self, parent, 
                              flags=QtCore.Qt.CustomizeWindowHint)
        self.setObjectName("main")
        self.config = userConfig()
        if self.config.defaultprofile():
            self.userprofile = userProfile(self.config.defaultprofile())
            self.profile = self.userprofile.chat
            self.theme = self.userprofile.getTheme()
        else:
            self.userprofile = userProfile(PesterProfile("pesterClient%d" % (random.randint(100,999)), QtGui.QColor("black"), Mood(0)))
            self.profile = self.userprofile.chat
            self.theme = self.userprofile.getTheme()
            self.changeProfile()

        size = self.theme['main/size']
        self.setGeometry(100, 100, size[0], size[1])
        self.setWindowIcon(QtGui.QIcon(self.theme["main/icon"]))
        self.mainSS()

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

        switch = QtGui.QAction("SWITCH", self)
        self.connect(switch, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('switchProfile()'))
        changetheme = QtGui.QAction("THEME", self)
        self.connect(changetheme, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('pickTheme()'))
        profilemenu = self.menu.addMenu("PROFILE")
        profilemenu.addAction(switch)
        profilemenu.addAction(changetheme)

        self.menuBarSS()

        closestyle = self.theme["main/close"]
        self.closeButton = WMButton(QtGui.QIcon(closestyle["image"]), self)
        self.closeButton.move(*closestyle["loc"])
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))
        self.miniButton = WMButton(QtGui.QIcon(self.theme["main/minimize/image"]), self)
        self.miniButton.move(*(self.theme["main/minimize/loc"]))
        self.connect(self.miniButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('showMinimized()'))

        chums = [PesterProfile(c) for c in set(self.config.chums())]
        self.chumList = chumArea(chums, self)
        self.connect(self.chumList, QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),
                     self, QtCore.SLOT('newConversationWindow(QListWidgetItem *)'))

        self.convos = {}
        self.tabconvo = None
        self.optionmenu = None
    def mainSS(self):
        self.setStyleSheet("QFrame#main { "+self.theme["main/style"]+" }")
    def menuBarSS(self):
        self.menu.setStyleSheet("QMenuBar { background: transparent; %s } QMenuBar::item { background: transparent; } " % (self.theme["main/menubar/style"]) + "QMenu { background: transparent; %s } QMenu::item::selected { %s }" % (self.theme["main/menu/style"], self.theme["main/menu/selected"]))
    def closeConversations(self):
        if self.tabconvo:
            self.tabconvo.close()
        else:
            for c in self.convos.values():
                c.close()
    def closeEvent(self, event):
        self.closeConversations()
        event.accept()
    def newMessage(self, handle, msg):
        if not self.convos.has_key(handle):
            if msg == "PESTERCHUM:CEASE": # ignore cease after we hang up
                return
            matchingChums = [c for c in self.chumList.chums if c.handle == handle]
            if len(matchingChums) > 0:
                mood = matchingChums[0].mood
            else:
                mood = Mood(0)
            chum = PesterProfile(handle, mood=mood)
            self.newConversation(chum, False)
            if len(matchingChums) == 0:
                self.moodRequest.emit(chum)
        convo = self.convos[handle]
        convo.addMessage(msg, False)
        # play sound here

    def changeColor(self, handle, color):
        # pesterconvo and chumlist
        self.chumList.updateColor(handle, color)
        if self.convos.has_key(handle):
            self.convos[handle].updateColor(color)

    def updateMood(self, handle, mood):
        self.chumList.updateMood(handle, mood)
        if self.convos.has_key(handle):
            self.convos[handle].updateMood(mood)
    def newConversation(self, chum, initiated=True):
        if self.convos.has_key(chum.handle):
            self.convos[chum.handle].showChat()
            return
        if self.config.tabs():
            if not self.tabconvo:
                self.createTabWindow()
            convoWindow = PesterConvo(chum, initiated, self, self.tabconvo)
            self.tabconvo.show()
        else:
            convoWindow = PesterConvo(chum, initiated, self)
        self.connect(convoWindow, QtCore.SIGNAL('messageSent(QString, PyQt_PyObject)'),
                     self, QtCore.SIGNAL('sendMessage(QString, PyQt_PyObject)'))
        self.connect(convoWindow, QtCore.SIGNAL('windowClosed(QString)'),
                     self, QtCore.SLOT('closeConvo(QString)'))
        self.convos[chum.handle] = convoWindow
        convoWindow.setChumOpen(True)
        self.newConvoStarted.emit(QtCore.QString(chum.handle), initiated)
        convoWindow.show()
    def createTabWindow(self):
        self.tabconvo = PesterTabWindow(self)
        self.connect(self.tabconvo, QtCore.SIGNAL('windowClosed()'),
                     self, QtCore.SLOT('tabsClosed()'))

    def changeProfile(self, collision=None):
        self.chooseprofile = PesterChooseProfile(self.userprofile, self.config, self.theme, self, collision=collision)
        self.chooseprofile.exec_()

    def themePicker(self):
        self.choosetheme = PesterChooseTheme(self.config, self.theme, self)
        self.choosetheme.exec_()
    def changeTheme(self, theme):
        self.theme = theme
        # do self
        self.resize(*self.theme["main/size"])
        self.setWindowIcon(QtGui.QIcon(self.theme["main/icon"]))
        self.mainSS()
        self.menuBarSS()
        self.closeButton.setIcon(QtGui.QIcon(self.theme["main/close/image"]))
        self.closeButton.move(*self.theme["main/close/loc"])
        self.miniButton.setIcon(QtGui.QIcon(self.theme["main/minimize/image"]))
        self.miniButton.move(*self.theme["main/minimize/loc"])
        # chum area
        self.chumList.changeTheme(theme)
        # do open windows
        if self.tabconvo:
            self.tabconvo.changeTheme(theme)
        for c in self.convos.values():
            c.changeTheme(theme)

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def newConversationWindow(self, chumlisting):
        chum = chumlisting.chum
        self.newConversation(chum)
    @QtCore.pyqtSlot(QtCore.QString)
    def closeConvo(self, handle):
        h = str(handle)
        del self.convos[h]
        self.convoClosed.emit(handle)
    @QtCore.pyqtSlot()
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
            self.connect(self.optionmenu, QtCore.SIGNAL('rejected()'),
                         self, QtCore.SLOT('closeOptions()'))
            self.optionmenu.show()
            self.optionmenu.raise_()
            self.optionmenu.activateWindow()
    @QtCore.pyqtSlot()
    def closeOptions(self):
        self.optionmenu.close()
        self.optionmenu = None
    @QtCore.pyqtSlot()
    def updateOptions(self):
        # tabs
        curtab = self.config.tabs()
        tabsetting = self.optionmenu.tabcheck.isChecked()
        if curtab and not tabsetting:
            # split tabs into windows
            if self.tabconvo:
                windows = list(self.tabconvo.convos.values())
                for w in windows:
                    w.setParent(None)
                    w.show()
                    w.raiseChat()
                self.tabconvo.closeSoft()
            # save options
            self.config.set("tabs", tabsetting)
        elif tabsetting and not curtab:
            # combine
            self.createTabWindow()
            newconvos = {}
            for (h,c) in self.convos.iteritems():
                c.setParent(self.tabconvo)
                self.tabconvo.addChat(c)
                self.tabconvo.show()
                newconvos[h] = c
            self.convos = newconvos
            # save options
            self.config.set("tabs", tabsetting)
        self.optionmenu = None

    @QtCore.pyqtSlot()
    def themeSelected(self):
        themename = self.choosetheme.themeBox.currentText()
        if themename != self.theme.name:
            # update profile
            self.changeTheme(pesterTheme(themename))
        self.choosetheme = None
    @QtCore.pyqtSlot()
    def closeTheme(self):
        self.choosetheme = None
    @QtCore.pyqtSlot()
    def profileSelected(self):
        if self.chooseprofile.profileBox and \
                self.chooseprofile.profileBox.currentIndex() > 0:
            handle = unicode(self.chooseprofile.profileBox.currentText())
            self.userprofile = userProfile(handle)
            self.profile = self.userprofile.chat
            # update themes here
        else:
            profile = PesterProfile(unicode(self.chooseprofile.chumHandle.text()),
                                    self.chooseprofile.chumcolor,
                                    Mood(0))
            self.userprofile = userProfile.newUserProfile(profile)
            self.profile = self.userprofile.chat

        # this may have to be fixed
        self.closeConversations()
        self.profileChanged.emit()

        self.chooseprofile = None
    @QtCore.pyqtSlot()
    def closeProfile(self):
        self.chooseprofile = None
    @QtCore.pyqtSlot()
    def switchProfile(self):
        if self.convos:
            closeWarning = QtGui.QMessageBox()
            closeWarning.setText("WARNING: THIS WILL CLOSE ALL CONVERSATION WINDOWS!")
            closeWarning.setInformativeText("i warned you bro! i warned you about those windows")
            closeWarning.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
            closeWarning.setDefaultButton(QtGui.QMessageBox.Ok)
            ret = closeWarning.exec_()
            if ret == QtGui.QMessageBox.Cancel:
                return
        self.changeProfile()

    @QtCore.pyqtSlot(QtCore.QString)
    def nickCollision(self, handle):
        if not self.chooseprofile:
            h = unicode(handle)
            self.changeProfile(collision=h)
        
    @QtCore.pyqtSlot()
    def pickTheme(self):
        self.themePicker()

    newConvoStarted = QtCore.pyqtSignal(QtCore.QString, bool, name="newConvoStarted")
    sendMessage = QtCore.pyqtSignal(QtCore.QString, PesterProfile)
    convoClosed = QtCore.pyqtSignal(QtCore.QString)
    profileChanged = QtCore.pyqtSignal()
    moodRequest = QtCore.pyqtSignal(PesterProfile)

class PesterIRC(QtCore.QObject):
    def __init__(self, window):
        QtCore.QObject.__init__(self)
        self.mainwindow = window
    def IRCConnect(self):
        self.cli = IRCClient(PesterHandler, host="irc.tymoon.eu", port=6667, nick=self.mainwindow.profile.handle, blocking=True)
        self.cli.command_handler.parent = self
        self.cli.command_handler.mainwindow = self.mainwindow
        self.conn = self.cli.connect()

    @QtCore.pyqtSlot(PesterProfile)
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
        helpers.msg(self.cli, h, "COLOR >%s" % (self.mainwindow.profile.colorcmd()))
    @QtCore.pyqtSlot(QtCore.QString)
    def endConvo(self, handle):
        h = str(handle)
        helpers.msg(self.cli, h, "PESTERCHUM:CEASE")
    @QtCore.pyqtSlot()
    def updateProfile(self):
        me = self.mainwindow.profile
        handle = me.handle
        helpers.nick(self.cli, handle)
        helpers.msg(self.cli, "#pesterchum", "MOOD >%d" % (me.mood.value()))
    def updateIRC(self):
        self.conn.next()

    moodUpdated = QtCore.pyqtSignal(QtCore.QString, Mood)
    colorUpdated = QtCore.pyqtSignal(QtCore.QString, QtGui.QColor)
    messageReceived = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
    nickCollision = QtCore.pyqtSignal(QtCore.QString)

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
                mychumhandle = self.mainwindow.profile.handle
                mymood = self.mainwindow.profile.mood.value()
                if msg.find(mychumhandle, 8) != -1:
                    helpers.msg(self.client, "#pesterchum", 
                                "MOOD >%d" % (mymood))
                    
        else:
            # private message
            # silently ignore messages to yourself.
            if handle == self.mainwindow.profile.handle:
                return
            if msg[0:7] == "COLOR >":
                colors = msg[7:].split(",")
                try:
                    colors = [int(d) for d in colors]
                except ValueError:
                    colors = [0,0,0]
                color = QtGui.QColor(*colors)
                self.parent.colorUpdated.emit(handle, color)
            else:
                self.parent.messageReceived.emit(handle, msg)


    def welcome(self, server, nick, msg):
        helpers.join(self.client, "#pesterchum")
        mychumhandle = self.mainwindow.profile.handle
        mymood = self.mainwindow.profile.mood.value()
        helpers.msg(self.client, "#pesterchum", "MOOD >%d" % (mymood))

        chums = self.mainwindow.chumList.chums
        self.getMood(*chums)

    def nicknameinuse(self, server, cmd, nick, msg):
        helpers.nick(self.client, "pesterClient%d" % (random.randint(100,999)))
        self.parent.nickCollision.emit(nick)
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

    irc = PesterIRC(widget)
    irc.IRCConnect()
    irc.connect(widget, QtCore.SIGNAL('sendMessage(QString, PyQt_PyObject)'),
                irc, QtCore.SLOT('sendMessage(QString, PyQt_PyObject)'))
    irc.connect(widget, 
                QtCore.SIGNAL('newConvoStarted(QString, bool)'),
                irc, QtCore.SLOT('startConvo(QString, bool)'))
    irc.connect(widget,
                QtCore.SIGNAL('convoClosed(QString)'),
                irc, QtCore.SLOT('endConvo(QString)'))
    irc.connect(widget,
                QtCore.SIGNAL('profileChanged()'),
                irc,
                QtCore.SLOT('updateProfile()'))
    irc.connect(widget,
                QtCore.SIGNAL('moodRequest(PyQt_PyObject)'),
                irc,
                QtCore.SLOT('getMood(PyQt_PyObject)'))
    irc.connect(irc, 
                QtCore.SIGNAL('moodUpdated(QString, PyQt_PyObject)'),
                widget, 
                QtCore.SLOT('updateMoodSlot(QString, PyQt_PyObject)'))
    irc.connect(irc,
                QtCore.SIGNAL('colorUpdated(QString, QColor)'),
                widget,
                QtCore.SLOT('updateColorSlot(QString, QColor)'))
    irc.connect(irc,
                QtCore.SIGNAL('messageReceived(QString, QString)'),
                widget,
                QtCore.SLOT('deliverMessage(QString, QString)'))
    irc.connect(irc,
                QtCore.SIGNAL('nickCollision(QString)'),
                widget,
                QtCore.SLOT('nickCollision(QString)'))

    ircapp = IRCThread(irc)
    ircapp.start()
    sys.exit(app.exec_())

main()

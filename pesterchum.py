# pesterchum
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import logging
import os, sys
import os.path
from datetime import *
from string import Template
import random
import json
import re
from PyQt4 import QtGui, QtCore
import pygame

from pestermenus import PesterChooseQuirks, PesterChooseTheme, \
    PesterChooseProfile, PesterOptions, PesterUserlist
from pesterdata import PesterProfile, Mood, pesterQuirk, pesterQuirks
from generic import PesterIcon, RightClickList, MultiTextDialog

logging.basicConfig(level=logging.INFO)

_ctag_begin = re.compile(r'<c=(.*?)>')
_ctag_rgb = re.compile(r'\d+,\d+,\d+')

def convertColorTags(string, format="html"):
    if format not in ["html", "bbcode", "ctag"]:
        raise ValueError("Color format not recognized")
    def repfunc(matchobj):
        color = matchobj.group(1)
        if _ctag_rgb.match(color) is not None:
            if format=='ctag':
                return "<c=%s,%s,%s>"
            try:
                qc = QtGui.QColor(*[int(c) for c in color.split(",")])
            except ValueError:
                qc = QtGui.QColor("black")
        else:
            qc = QtGui.QColor(color)
        if not qc.isValid():
            qc = QtGui.QColor("black")
        if format == "html":
            return '<span style="color:%s">' % (qc.name())
        elif format == "bbcode":
            return '[color=%s]' % (qc.name())
        elif format == "ctag":
            (r,g,b,a) = qc.getRgb()
            return '<c=%s,%s,%s>' % (r,g,b)
    string = _ctag_begin.sub(repfunc, string)
    endtag = {"html": "</span>", "bbcode": "[/color]", "ctag": "</c>"}
    string = string.replace("</c>", endtag[format])
    return string

def escapeBrackets(string):
    class beginTag(object):
        def __init__(self, tag):
            self.tag = tag
    class endTag(object):
        pass
    newlist = []
    begintagpos = [(m.start(), m.end()) for m in _ctag_begin.finditer(string)]
    lasti = 0
    for (s, e) in begintagpos:
        newlist.append(string[lasti:s])
        newlist.append(beginTag(string[s:e]))
        lasti = e
    if lasti < len(string):
        newlist.append(string[lasti:])
    tmp = []
    for o in newlist:
        if type(o) is not beginTag:
            l = o.split("</c>")
            tmp.append(l[0])
            l = l[1:]
            for item in l:
                tmp.append(endTag())
                tmp.append(item)
        else:
            tmp.append(o)
    btlen = 0
    etlen = 0
    retval = ""
    newlist = tmp
    for o in newlist:
        if type(o) is beginTag:
            retval += o.tag.replace("&", "&amp;")
            btlen +=1
        elif type(o) is endTag:
            if etlen >= btlen:
                continue
            else:
                retval += "</c>"
                etlen += 1
        else:
            retval += o.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if btlen > etlen:
        for i in range(0, btlen-etlen):
            retval += "</c>"
    return retval
                

class waitingMessageHolder(object):
    def __init__(self, mainwindow, **msgfuncs):
        self.mainwindow = mainwindow
        self.funcs = msgfuncs
        self.queue = msgfuncs.keys()
        if len(self.queue) > 0:
            self.mainwindow.updateSystemTray()
    def answerMessage(self):
        func = self.funcs[self.queue[0]]
        func()
    def messageAnswered(self, handle):
        if handle not in self.queue:
            return
        self.queue = [q for q in self.queue if q != handle]
        del self.funcs[handle]
        if len(self.queue) == 0:
            self.mainwindow.updateSystemTray()
    def addMessage(self, handle, func):
        if not self.funcs.has_key(handle):
            self.queue.append(handle)
        self.funcs[handle] = func
        if len(self.queue) > 0:
            self.mainwindow.updateSystemTray()
    def __len__(self):
        return len(self.queue)

class NoneSound(object):
    def play(self): pass

class PesterLog(object):
    def __init__(self, handle):
        self.handle = handle
        if not os.path.exists("logs/%s" % (handle)):
            os.mkdir("logs/%s" % (handle))
        self.convos = {}
    def log(self, handle, msg):
        if not self.convos.has_key(handle):
            time = datetime.now().strftime("%Y-%m-%d.%H:%M")
            if not os.path.exists("logs/%s/%s" % (self.handle, handle)):
                os.mkdir("logs/%s/%s" % (self.handle, handle))
            fp = open("logs/%s/%s/%s.%s" % (self.handle, handle, handle, time), 'a')
            self.convos[handle] = fp
        self.convos[handle].write(msg+"\n")
        self.convos[handle].flush()
    def finish(self, handle):
        if not self.convos.has_key(handle):
            return
        self.convos[handle].close()
        del self.convos[handle]
    def close(self):
        for h in self.convos.keys():
            self.convos[h].close()

class PesterProfileDB(dict):
    def __init__(self):
        try:
            fp = open("logs/chums.js", 'r')
            chumdict = json.load(fp)
            fp.close()
        except IOError:
            chumdict = {}
            fp = open("logs/chums.js", 'w')
            json.dump(chumdict, fp)
            fp.close()
        converted = dict([(handle, PesterProfile(handle, color=QtGui.QColor(c['color']), mood=Mood(c['mood']))) for (handle, c) in chumdict.iteritems()])
        self.update(converted)

    def save(self):
        fp = open("logs/chums.js", 'w')
        chumdict = dict([p.plaindict() for p in self.itervalues()])
        json.dump(chumdict, fp)
        fp.close()
    def getColor(self, handle, default=None):
        if not self.has_key(handle):
            return default
        else:
            return self[handle].color
    def setColor(self, handle, color):
        if self.has_key(handle):
            self[handle].color = color
        else:
            self[handle] = PesterProfile(handle, color)
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        self.save()

class PesterList(list):
    def __init__(self, l):
        self.extend(l)

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
        for (k, v) in d.iteritems():
            if type(v) is unicode:
                s = Template(v)
                d[k] = s.safe_substitute(path=self.path)
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
    def addChum(self, chum):
        newchums = self.config['chums'] + [chum.handle]
        self.set("chums", newchums)
    def removeChum(self, chum):
        if type(chum) is PesterProfile:
            handle = chum.handle
        else:
            handle = chum
        newchums = [c for c in self.config['chums'] if c != handle]
        self.set("chums", newchums)
    def getBlocklist(self):
        if not self.config.has_key('block'):
            self.set('block', [])
        return self.config['block']
    def addBlocklist(self, handle):
        l = self.getBlocklist()
        if handle not in l:
            l.append(handle)
            self.set('block', l)
    def delBlocklist(self, handle):
        l = self.getBlocklist()
        l.pop(l.index(handle))
        self.set('block', l)
    def set(self, item, setting):
        self.config[item] = setting
        try:
            jsonoutput = json.dumps(self.config)
        except ValueError, e:
            raise e
        fp = open("pesterchum.js", 'w')
        fp.write(jsonoutput)
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
            self.chat.mood = Mood(self.theme["main/defaultmood"])
            self.quirks = pesterQuirks([])
        else:
            fp = open("profiles/%s.js" % (user))
            self.userprofile = json.load(fp)
            fp.close()
            try:
                self.theme = pesterTheme(self.userprofile["theme"])
            except ValueError, e:
                self.theme = pesterTheme("pesterchum")

            self.chat = PesterProfile(self.userprofile["handle"],
                                      QtGui.QColor(self.userprofile["color"]),
                                      Mood(self.theme["main/defaultmood"]))
            self.quirks = pesterQuirks(self.userprofile["quirks"])
    def setMood(self, mood):
        self.chat.mood = mood
    def setTheme(self, theme):
        self.theme = theme
        self.userprofile["theme"] = theme.name
        self.save()
    def setColor(self, color):
        self.chat.color = color
        self.userprofile["color"] = unicode(color.name())
        self.save()
    def setQuirks(self, quirks):
        self.quirks = quirks
        self.userprofile["quirks"] = self.quirks.plainList()
        self.save()
    def getTheme(self):
        return self.theme
    def save(self):
        handle = self.chat.handle
        try:
            jsonoutput = json.dumps(self.userprofile, fp)
        except ValueError, e:
            raise e
        fp = open("profiles/%s.js" % (handle), 'w')
        fp.write(jsonoutput)
        fp.close()
    @staticmethod
    def newUserProfile(chatprofile):
        if os.path.exists("profiles/%s.js" % (chatprofile.handle)):
            newprofile = userProfile(chatprofile.handle)
        else:
            newprofile = userProfile(chatprofile)
            newprofile.save()
        return newprofile


class WMButton(QtGui.QPushButton):
    def __init__(self, icon, parent=None):
        QtGui.QPushButton.__init__(self, icon, "", parent)
        self.setIconSize(icon.realsize())
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
    def updateMood(self, unblock=False):
        mood = self.chum.mood
        self.mood = mood
        self.setIcon(self.mood.icon(self.mainwindow.theme))
        try:
            self.setTextColor(QtGui.QColor(self.mainwindow.theme["main/chums/moods"][self.mood.name()]["color"]))
        except KeyError:
            self.setTextColor(QtGui.QColor(self.mainwindow.theme["main/chums/moods/chummy/color"]))
    def changeTheme(self, theme):
        self.setIcon(self.mood.icon(theme))
        try:
            self.setTextColor(QtGui.QColor(self.mainwindow.theme["main/chums/moods"][self.mood.name()]["color"]))
        except KeyError:
            self.setTextColor(QtGui.QColor(self.mainwindow.theme["main/chums/moods/chummy/color"]))
    def __lt__(self, cl):
        h1 = self.handle.lower()
        h2 = cl.handle.lower()
        return (h1 < h2)

class chumArea(RightClickList):
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

        self.optionsMenu = QtGui.QMenu(self)
        self.pester = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/pester"], self)
        self.connect(self.pester, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('activateChum()'))
        self.removechum = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/removechum"], self)
        self.connect(self.removechum, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('removeChum()'))
        self.blockchum = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/blockchum"], self)
        self.connect(self.blockchum, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('blockChum()'))
        self.optionsMenu.addAction(self.pester)
        self.optionsMenu.addAction(self.blockchum)
        self.optionsMenu.addAction(self.removechum)

        self.sortItems()
    def addChum(self, chum):
        if len([c for c in self.chums if c.handle == chum.handle]) != 0:
            return
        self.chums.append(chum)
        chumLabel = chumListing(chum, self.mainwindow)
        self.addItem(chumLabel)
        self.sortItems()

    def getChums(self, handle):
        chums = self.findItems(handle, QtCore.Qt.MatchFlags(0))
        return chums
    def updateMood(self, handle, mood):
        chums = self.getChums(handle)
        for c in chums:
            c.setMood(mood)
    def updateColor(self, handle, color):
        chums = self.findItems(handle, QtCore.Qt.MatchFlags(0))
        for c in chums:
            c.setColor(color)
    def changeTheme(self, theme):
        self.setGeometry(*(theme["main/chums/loc"]+theme["main/chums/size"]))
        self.setStyleSheet(theme["main/chums/style"])
        self.pester.setText(theme["main/menus/rclickchumlist/pester"])
        self.removechum.setText(theme["main/menus/rclickchumlist/removechum"])
        self.blockchum.setText(theme["main/menus/rclickchumlist/blockchum"])

        chumlistings = [self.item(i) for i in range(0, self.count())]
        for c in chumlistings:
            c.changeTheme(theme)
    @QtCore.pyqtSlot()
    def activateChum(self):
        self.itemActivated.emit(self.currentItem())
    @QtCore.pyqtSlot()
    def removeChum(self, handle = None):
        if handle:
            clistings = self.getChums(handle)
            for c in clistings:
                self.setCurrentItem(c)
        if not self.currentItem():
            return
        currentChum = self.currentItem().chum
        self.chums = [c for c in self.chums if c.handle != currentChum.handle]
        self.removeChumSignal.emit(self.currentItem())
        oldlist = self.takeItem(self.currentRow())
        del oldlist
    @QtCore.pyqtSlot()
    def blockChum(self):
        currentChum = self.currentItem()
        if not currentChum:
            return
        self.blockChumSignal.emit(self.currentItem().chum.handle)

    removeChumSignal = QtCore.pyqtSignal(QtGui.QListWidgetItem)
    blockChumSignal = QtCore.pyqtSignal(QtCore.QString)

class trollSlum(chumArea):
    def __init__(self, trolls, mainwindow, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        self.mainwindow = mainwindow
        theme = self.mainwindow.theme
        self.setStyleSheet(theme["main/trollslum/chumroll/style"])
        self.chums = trolls
        for c in self.chums:
            chandle = c.handle
            if not self.findItems(chandle, QtCore.Qt.MatchFlags(0)):
                chumLabel = chumListing(c, self.mainwindow)
                self.addItem(chumLabel)

        self.optionsMenu = QtGui.QMenu(self)
        self.unblockchum = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/unblockchum"], self)
        self.connect(self.unblockchum, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SIGNAL('unblockChumSignal()'))
        self.optionsMenu.addAction(self.unblockchum)

        self.sortItems()
    def changeTheme(self, theme):
        self.setStyleSheet(theme["main/trollslum/chumroll/style"])
        self.removechum.setText(theme["main/menus/rclickchumlist/removechum"])
        self.unblockchum.setText(theme["main/menus/rclickchumlist/blockchum"])

        chumlistings = [self.item(i) for i in range(0, self.count())]
        for c in chumlistings:
            c.changeTheme(theme)

    unblockChumSignal = QtCore.pyqtSignal(QtCore.QString)

class TrollSlumWindow(QtGui.QFrame):
    def __init__(self, trolls, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.mainwindow = mainwindow
        theme = self.mainwindow.theme
        self.slumlabel = QtGui.QLabel(self)
        self.initTheme(theme)

        self.trollslum = trollSlum(trolls, self.mainwindow, self)
        self.connect(self.trollslum, QtCore.SIGNAL('unblockChumSignal()'),
                     self, QtCore.SLOT('removeCurrentTroll()'))
        layout_1 = QtGui.QHBoxLayout()
        self.addButton = QtGui.QPushButton("ADD", self)
        self.connect(self.addButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addTrollWindow()'))
        self.removeButton = QtGui.QPushButton("REMOVE", self)
        self.connect(self.removeButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('removeCurrentTroll()'))
        layout_1.addWidget(self.addButton)
        layout_1.addWidget(self.removeButton)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.slumlabel)
        layout_0.addWidget(self.trollslum)
        layout_0.addLayout(layout_1)
        self.setLayout(layout_0)

    def initTheme(self, theme):
        self.resize(*theme["main/trollslum/size"])
        self.setStyleSheet(theme["main/trollslum/style"])
        self.slumlabel.setText(theme["main/trollslum/label/text"])
        self.slumlabel.setStyleSheet(theme["main/trollslum/label/style"])
        if not self.parent():
            self.setWindowTitle(theme["main/menus/profile/block"])
            self.setWindowIcon(self.mainwindow.windowIcon())
    def changeTheme(self, theme):
        self.initTheme(theme)
        self.trollslum.changeTheme(theme)
        # move unblocked trolls from slum to chumarea
    def closeEvent(self, event):
        self.mainwindow.closeTrollSlum()

    def updateMood(self, handle, mood):
        self.trollslum.updateMood(handle, mood)
    def addTroll(self, chum):
        self.trollslum.addChum(chum)
    def removeTroll(self, handle):
        self.trollslum.removeChum(handle)
    @QtCore.pyqtSlot()
    def removeCurrentTroll(self):
        currentListing = self.trollslum.currentItem()
        if not currentListing:
            return
        self.unblockChumSignal.emit(currentListing.chum.handle)
    @QtCore.pyqtSlot()
    def addTrollWindow(self):
        if not hasattr(self, 'addtrolldialog'):
            self.addtrolldialog = None
        if self.addtrolldialog:
            return
        self.addtrolldialog = QtGui.QInputDialog(self)
        (handle, ok) = self.addtrolldialog.getText(self, "Add Troll", "Enter Troll Handle:")
        if ok:
            handle = unicode(handle)
            if not (PesterProfile.checkLength(handle) and
                    PesterProfile.checkValid(handle)):
                errormsg = QtGui.QErrorMessage(self)
                errormsg.showMessage("THIS IS NOT A VALID CHUMTAG!")
                self.addchumdialog = None
                return
            self.blockChumSignal.emit(handle)
        self.addtrolldialog = None

    blockChumSignal = QtCore.pyqtSignal(QtCore.QString)
    unblockChumSignal = QtCore.pyqtSignal(QtCore.QString)

class PesterMoodHandler(QtCore.QObject):
    def __init__(self, parent, *buttons):
        QtCore.QObject.__init__(self)
        self.buttons = {}
        self.mainwindow = parent
        for b in buttons:
            self.buttons[b.mood.value()] = b
            if b.mood.value() == self.mainwindow.profile().mood.value():
                b.setSelected(True)
            self.connect(b, QtCore.SIGNAL('clicked()'),
                         b, QtCore.SLOT('updateMood()'))
            self.connect(b, QtCore.SIGNAL('moodUpdated(int)'),
                         self, QtCore.SLOT('updateMood(int)'))
    def removeButtons(self):
        for b in self.buttons.values():
            b.close()
    def showButtons(self):
        for b in self.buttons.values():
            b.show()
            b.raise_()
    @QtCore.pyqtSlot(int)
    def updateMood(self, m):
        oldmood = self.mainwindow.profile().mood
        try:
            oldbutton = self.buttons[oldmood.value()]
            oldbutton.setSelected(False)
        except KeyError:
            pass
        newbutton = self.buttons[m]
        newbutton.setSelected(True)
        newmood = Mood(m)
        self.mainwindow.userprofile.chat.mood = newmood
        self.mainwindow.moodUpdated.emit()

class PesterMoodButton(QtGui.QPushButton):
    def __init__(self, parent, **options):
        icon = PesterIcon(options["icon"])
        QtGui.QPushButton.__init__(self, icon, options["text"], parent)
        self.setIconSize(icon.realsize())
        self.setFlat(True)
        self.resize(*options["size"])
        self.move(*options["loc"])
        self.unselectedSheet = options["style"]
        self.selectedSheet = options["selected"]
        self.setStyleSheet(self.unselectedSheet)
        self.mainwindow = parent
        self.mood = Mood(options["mood"])
    def setSelected(self, selected):
        if selected:
            self.setStyleSheet(self.selectedSheet)
        else:
            self.setStyleSheet(self.unselectedSheet)
    @QtCore.pyqtSlot()
    def updateMood(self):
        self.moodUpdated.emit(self.mood.value())
    moodUpdated = QtCore.pyqtSignal(int)


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
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.mainwindow = mainwindow
        self.resize(*self.mainwindow.theme["convo/size"])
        self.setStyleSheet(self.mainwindow.theme["convo/style"])

        self.tabs = QtGui.QTabBar(self)
        self.tabs.setTabsClosable(True)
        self.connect(self.tabs, QtCore.SIGNAL('currentChanged(int)'),
                     self, QtCore.SLOT('changeTab(int)'))
        self.connect(self.tabs, QtCore.SIGNAL('tabCloseRequested(int)'),
                     self, QtCore.SLOT('tabClose(int)'))
        self.tabs.setShape(self.mainwindow.theme["convo/tabs/tabstyle"])
        self.tabs.setStyleSheet("QTabBar::tab{ %s } QTabBar::tab:selected { %s }" % (self.mainwindow.theme["convo/tabs/style"], self.mainwindow.theme["convo/tabs/selectedstyle"]))

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.convos = {}
        self.tabIndices = {}
        self.currentConvo = None
        self.changedTab = False
        self.softclose = False

        # get default tab color i guess
        self.defaultTabTextColor = self.getTabTextColor()
    def getTabTextColor(self):
        # ugly, ugly hack
        self.changedTab = True
        i = self.tabs.addTab(".")
        c = self.tabs.tabTextColor(i)
        self.tabs.removeTab(i)
        self.changedTab = False
        return c
    def addChat(self, convo):
        self.convos[convo.chum.handle] = convo
        # either addTab or setCurrentIndex will trigger changed()
        newindex = self.tabs.addTab(convo.chum.handle)
        self.tabIndices[convo.chum.handle] = newindex
        self.tabs.setCurrentIndex(newindex)
        self.tabs.setTabIcon(newindex, convo.chum.mood.icon(self.mainwindow.theme))
    def showChat(self, handle):
        tabi = self.tabIndices[handle]
        if self.tabs.currentIndex() == tabi:
            self.activateWindow()
            self.raise_()
            self.convos[handle].raiseChat()
        else:
            self.tabs.setCurrentIndex(tabi)

    def convoHasFocus(self, convo):
        if ((self.hasFocus() or self.tabs.hasFocus()) and 
            self.tabs.tabText(self.tabs.currentIndex()) == convo.chum.handle):
            return True
        
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
    def updateBlocked(self, handle):
        i = self.tabIndices[handle]
        icon = QtGui.QIcon(self.mainwindow.theme["main/chums/moods/blocked/icon"])
        self.tabs.setTabIcon(i, icon)
        if self.tabs.currentIndex() == i:
            self.setWindowIcon(icon)
    def updateMood(self, handle, mood, unblocked=False):
        i = self.tabIndices[handle]
        if handle in self.mainwindow.config.getBlocklist() and not unblocked:
            icon = QtGui.QIcon(self.mainwindow.theme["main/chums/moods/blocked/icon"])
        else:
            icon = mood.icon(self.mainwindow.theme)
        self.tabs.setTabIcon(i, icon)
        if self.tabs.currentIndex() == i:
            self.setWindowIcon(icon)
    def closeEvent(self, event):
        if not self.softclose:
            while self.tabs.count() > 0:
                self.tabClose(0)
        self.windowClosed.emit()
    def focusInEvent(self, event):
        # make sure we're not switching tabs!
        i = self.tabs.tabAt(self.mapFromGlobal(QtGui.QCursor.pos()))
        if i == -1:
              i = self.tabs.currentIndex()
        handle = unicode(self.tabs.tabText(i))
        self.clearNewMessage(handle)
    def convoHasFocus(self, handle):
        i = self.tabIndices[handle]
        if (self.tabs.currentIndex() == i and 
            (self.hasFocus() or self.tabs.hasFocus())):
            return True
        else:
            return False
    
    def notifyNewMessage(self, handle):
        i = self.tabIndices[handle]
        self.tabs.setTabTextColor(i, QtGui.QColor(self.mainwindow.theme["convo/tabs/newmsgcolor"]))
        convo = self.convos[handle]
        def func():
            convo.showChat()
        self.mainwindow.waitingMessages.addMessage(handle, func)
        # set system tray
    def clearNewMessage(self, handle):
        try:
            i = self.tabIndices[handle]
        except KeyError:
            pass
        self.tabs.setTabTextColor(i, self.defaultTabTextColor)
        self.mainwindow.waitingMessages.messageAnswered(handle)
    def changeTheme(self, theme):
        self.resize(*theme["convo/size"])
        self.setStyleSheet(theme["convo/style"])
        self.tabs.setShape(theme["convo/tabs/tabstyle"])
        self.tabs.setStyleSheet("QTabBar::tabs{ %s }" % (theme["convo/tabs/style"]))
        for c in self.convos.values():
            tabi = self.tabIndices[c.chum.handle]
            self.tabs.setTabIcon(tabi, c.chum.mood.icon(theme))
        currenttabi = self.tabs.currentIndex()
        if currenttabi >= 0:
            currentHandle = unicode(self.tabs.tabText(self.tabs.currentIndex()))
            self.setWindowIcon(self.convos[currentHandle].chum.mood.icon(theme))
        self.defaultTabTextColor = self.getTabTextColor()

    @QtCore.pyqtSlot(int)
    def tabClose(self, i):
        handle = unicode(self.tabs.tabText(i))
        self.mainwindow.waitingMessages.messageAnswered(handle)
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
        systemColor = QtGui.QColor(self.parent().mainwindow.theme["convo/systemMsgColor"])
        initials = chum.initials()
        msg = unicode(text)
        parent = self.parent()
        window = parent.mainwindow
        me = window.profile()
        if msg == "PESTERCHUM:BEGIN":
            parent.setChumOpen(True)
            msg = chum.pestermsg(me, systemColor, window.theme["convo/text/beganpester"])
            window.chatlog.log(chum.handle, convertColorTags(msg, "bbcode"))
            self.append(convertColorTags(msg))
        elif msg == "PESTERCHUM:CEASE":
            parent.setChumOpen(False)
            msg = chum.pestermsg(me, systemColor, window.theme["convo/text/ceasepester"])
            window.chatlog.log(chum.handle, convertColorTags(msg, "bbcode"))
            self.append(convertColorTags(msg))
        elif msg == "PESTERCHUM:BLOCK":
            msg = chum.pestermsg(me, systemColor, window.theme['convo/text/blocked'])
            window.chatlog.log(chum.handle, convertColorTags(msg, "bbcode"))
            self.append(convertColorTags(msg))
        elif msg == "PESTERCHUM:UNBLOCK":
            msg = chum.pestermsg(me, systemColor, window.theme['convo/text/unblocked'])
            window.chatlog.log(chum.handle, convertColorTags(msg, "bbcode"))
            self.append(convertColorTags(msg))
        else:
            if not parent.chumopen and chum is not me:
                beginmsg = chum.pestermsg(me, systemColor, window.theme["convo/text/beganpester"])
                parent.setChumOpen(True)
                window.chatlog.log(chum.handle, convertColorTags(beginmsg, "bbcode"))
                self.append(convertColorTags(beginmsg))

            msg = "<c=%s>%s: %s</c>" % (color, initials, msg)
            msg = escapeBrackets(msg)
            self.append(convertColorTags(msg))
            if chum is me:
                window.chatlog.log(parent.chum.handle, convertColorTags(msg, "bbcode"))
            else:
                window.chatlog.log(chum.handle, convertColorTags(msg, "bbcode"))
    def changeTheme(self, theme):
        self.setStyleSheet(theme["convo/textarea/style"])
        sb = self.verticalScrollBar()
        sb.setMaximum(sb.maximum()+1000) # ugly hack but whatcha gonna do
        sb.setValue(sb.maximum())
    def focusInEvent(self, event):
        self.parent().clearNewMessage()
        QtGui.QTextEdit.focusInEvent(self, event)

class PesterInput(QtGui.QLineEdit):
    def __init__(self, theme, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setStyleSheet(theme["convo/input/style"])
    def changeTheme(self, theme):
        self.setStyleSheet(theme["convo/input/style"])
    def focusInEvent(self, event):
        self.parent().clearNewMessage()
        QtGui.QLineEdit.focusInEvent(self, event)

class PesterConvo(QtGui.QFrame):
    def __init__(self, chum, initiated, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.chum = chum
        self.mainwindow = mainwindow
        convo = self.mainwindow.theme["convo"]
        self.resize(*convo["size"])
        self.setStyleSheet(convo["style"])
        self.setWindowIcon(chum.mood.icon(self.mainwindow.theme))
        self.setWindowTitle(chum.handle)

        t = Template(self.mainwindow.theme["convo/chumlabel/text"])
        
        self.chumLabel = QtGui.QLabel(t.safe_substitute(handle=chum.handle), self)
        self.chumLabel.setStyleSheet(self.mainwindow.theme["convo/chumlabel/style"])
        self.chumLabel.setAlignment(self.aligndict["h"][self.mainwindow.theme["convo/chumlabel/align/h"]] | self.aligndict["v"][self.mainwindow.theme["convo/chumlabel/align/v"]])
        self.chumLabel.setMaximumHeight(self.mainwindow.theme["convo/chumlabel/maxheight"])
        self.chumLabel.setMinimumHeight(self.mainwindow.theme["convo/chumlabel/minheight"])
        self.chumLabel.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding))
        self.textArea = PesterText(self.mainwindow.theme, self)
        self.textInput = PesterInput(self.mainwindow.theme, self)
        self.textInput.setFocus()

        self.connect(self.textInput, QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('sentMessage()'))

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.chumLabel)
        self.layout.addWidget(self.textArea)
        self.layout.addWidget(self.textInput)
        self.layout.setSpacing(0)
        
        self.setLayout(self.layout)

        self.chumopen = False

        if parent:
            parent.addChat(self)
        if initiated:
            msg = self.mainwindow.profile().pestermsg(self.chum, QtGui.QColor(self.mainwindow.theme["convo/systemMsgColor"]), self.mainwindow.theme["convo/text/beganpester"])
            self.setChumOpen(True)
            self.textArea.append(convertColorTags(msg))
            self.mainwindow.chatlog.log(self.chum.handle, convertColorTags(msg, "bbcode"))
        self.newmessage = False

    def updateMood(self, mood, unblocked=False):
        if mood.name() == "offline" and self.chumopen == True and not unblocked:
            msg = self.chum.pestermsg(self.mainwindow.profile(), QtGui.QColor(self.mainwindow.theme["convo/systemMsgColor"]), self.mainwindow.theme["convo/text/ceasepester"])
            self.textArea.append(convertColorTags(msg))
            self.mainwindow.chatlog.log(self.chum.handle, convertColorTags(msg, "bbcode"))
            self.chumopen = False
        if self.parent():
            self.parent().updateMood(self.chum.handle, mood, unblocked)
        else:
            if self.chum.blocked(self.mainwindow.userprofile) and not unblocked:
                self.setWindowIcon(QtGui.QIcon(self.mainwindow.theme["main/chums/moods/blocked/icon"]))
            else:
                self.setWindowIcon(mood.icon(self.mainwindow.theme))
        # print mood update?
    def updateBlocked(self):
        if self.parent():
            self.parent().updateBlocked(self.chum.handle)
        else:
            self.setWindowIcon(QtGui.QIcon(self.mainwindow.theme["main/chums/moods/blocked/icon"]))
    def updateColor(self, color):
        self.chum.color = color
    def addMessage(self, text, me=True):
        if me:
            chum = self.mainwindow.profile()
        else:
            chum = self.chum
            self.notifyNewMessage()
        self.textArea.addMessage(text, chum)

    def notifyNewMessage(self):
        # first see if this conversation HASS the focus
        if not (self.hasFocus() or self.textArea.hasFocus() or 
                self.textInput.hasFocus() or 
                (self.parent() and self.parent().convoHasFocus(self.chum.handle))):
            # ok if it has a tabconvo parent, send that the notify.
            if self.parent():
                self.parent().notifyNewMessage(self.chum.handle)
            # if not change the window title and update system tray
            else:
                self.newmessage = True
                self.setWindowTitle(self.chum.handle+"*")
                def func():
                    self.showChat()
                self.mainwindow.waitingMessages.addMessage(self.chum.handle, func)
                
    def clearNewMessage(self):
        if self.parent():
            self.parent().clearNewMessage(self.chum.handle)
        elif self.newmessage:
            self.newmessage = False
            self.setWindowTitle(self.chum.handle)
            self.mainwindow.waitingMessages.messageAnswered(self.chum.handle)
            # reset system tray
    def focusInEvent(self, event):
        self.clearNewMessage()
        self.textInput.setFocus()
    def raiseChat(self):
        self.activateWindow()
        self.raise_()
        self.textInput.setFocus()

    def showChat(self):
        if self.parent():
            self.parent().showChat(self.chum.handle)
        self.raiseChat()

    def closeEvent(self, event):
        self.mainwindow.waitingMessages.messageAnswered(self.chum.handle)
        self.windowClosed.emit(self.chum.handle)
    def setChumOpen(self, o):
        self.chumopen = o
    def changeTheme(self, theme):
        self.resize(*theme["convo/size"])
        self.setStyleSheet(theme["convo/style"])
        self.setWindowIcon(self.chum.mood.icon(theme))
        t = Template(self.mainwindow.theme["convo/chumlabel/text"])
        self.chumLabel.setText(t.safe_substitute(handle=self.chum.handle))
        self.chumLabel.setStyleSheet(theme["convo/chumlabel/style"])
        self.chumLabel.setAlignment(self.aligndict["h"][self.mainwindow.theme["convo/chumlabel/align/h"]] | self.aligndict["v"][self.mainwindow.theme["convo/chumlabel/align/v"]])
        self.chumLabel.setMaximumHeight(self.mainwindow.theme["convo/chumlabel/maxheight"])
        self.chumLabel.setMinimumHeight(self.mainwindow.theme["convo/chumlabel/minheight"])
        self.chumLabel.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding))
        self.textArea.changeTheme(theme)
        self.textInput.changeTheme(theme)

    @QtCore.pyqtSlot()
    def sentMessage(self):
        text = self.textInput.text()
        if text == "":
            return
        # deal with quirks here
        qtext = self.mainwindow.userprofile.quirks.apply(unicode(text))
        text = QtCore.QString(qtext)
        self.textInput.setText("")
        self.addMessage(text, True)
        # if ceased, rebegin
        if not self.chumopen:
            self.mainwindow.newConvoStarted.emit(QtCore.QString(self.chum.handle), True)
        self.messageSent.emit(text, self.chum)

    messageSent = QtCore.pyqtSignal(QtCore.QString, PesterProfile)
    windowClosed = QtCore.pyqtSignal(QtCore.QString)

    aligndict = {"h": {"center": QtCore.Qt.AlignHCenter,
                       "left": QtCore.Qt.AlignLeft,
                       "right": QtCore.Qt.AlignRight },
                 "v": {"center": QtCore.Qt.AlignVCenter,
                       "top": QtCore.Qt.AlignTop,
                       "bottom": QtCore.Qt.AlignBottom } }

class PesterWindow(MovingWindow):
    def __init__(self, parent=None):
        MovingWindow.__init__(self, parent, 
                              flags=(QtCore.Qt.CustomizeWindowHint | 
                                     QtCore.Qt.FramelessWindowHint))

        self.convos = {}
        self.tabconvo = None

        self.setObjectName("main")
        self.config = userConfig()
        if self.config.defaultprofile():
            self.userprofile = userProfile(self.config.defaultprofile())
            self.theme = self.userprofile.getTheme()
        else:
            self.userprofile = userProfile(PesterProfile("pesterClient%d" % (random.randint(100,999)), QtGui.QColor("black"), Mood(0)))
            self.theme = self.userprofile.getTheme()

        self.chatlog = PesterLog(self.profile().handle)

        self.move(100, 100)

        opts = QtGui.QAction(self.theme["main/menus/client/options"], self)
        self.opts = opts
        self.connect(opts, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('openOpts()'))
        exitaction = QtGui.QAction(self.theme["main/menus/client/exit"], self)
        self.exitaction = exitaction
        self.connect(exitaction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('close()'))
        userlistaction = QtGui.QAction(self.theme["main/menus/client/userlist"], self)
        self.userlistaction = userlistaction
        self.connect(userlistaction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('showAllUsers()'))
        self.menu = QtGui.QMenuBar(self)
        
        filemenu = self.menu.addMenu(self.theme["main/menus/client/_name"])
        self.filemenu = filemenu
        filemenu.addAction(opts)
        filemenu.addAction(userlistaction)
        filemenu.addAction(exitaction)

        changetheme = QtGui.QAction(self.theme["main/menus/profile/theme"], self)
        self.changetheme = changetheme
        self.connect(changetheme, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('pickTheme()'))
        changequirks = QtGui.QAction(self.theme["main/menus/profile/quirks"], self)
        self.changequirks = changequirks
        self.connect(changequirks, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('openQuirks()'))
        loadslum = QtGui.QAction(self.theme["main/menus/profile/block"], self)
        self.loadslum = loadslum
        self.connect(loadslum, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('showTrollSlum()'))

        changecoloraction = QtGui.QAction(self.theme["main/menus/profile/color"], self)
        self.changecoloraction = changecoloraction
        self.connect(changecoloraction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('changeMyColor()'))

        switch = QtGui.QAction(self.theme["main/menus/profile/switch"], self)
        self.switch = switch
        self.connect(switch, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('switchProfile()'))

        profilemenu = self.menu.addMenu(self.theme["main/menus/profile/_name"])
        self.profilemenu = profilemenu
        profilemenu.addAction(changetheme)
        profilemenu.addAction(changequirks)
        profilemenu.addAction(loadslum)
        profilemenu.addAction(changecoloraction)
        profilemenu.addAction(switch)

        self.closeButton = WMButton(PesterIcon(self.theme["main/close/image"]), self)
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))
        self.miniButton = WMButton(PesterIcon(self.theme["main/minimize/image"]), self)
        self.connect(self.miniButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('showMinimized()'))

        self.namesdb = {}
        self.chumdb = PesterProfileDB()

        chums = [PesterProfile(c, chumdb=self.chumdb) for c in set(self.config.chums())]
        self.chumList = chumArea(chums, self)
        self.connect(self.chumList, 
                     QtCore.SIGNAL('itemActivated(QListWidgetItem *)'),
                     self, 
                     QtCore.SLOT('newConversationWindow(QListWidgetItem *)'))
        self.connect(self.chumList,
                     QtCore.SIGNAL('removeChumSignal(QListWidgetItem *)'),
                     self,
                     QtCore.SLOT('removeChum(QListWidgetItem *)'))
        self.connect(self.chumList,
                     QtCore.SIGNAL('blockChumSignal(QString)'),
                     self,
                     QtCore.SLOT('blockChum(QString)'))
        
        self.addChumButton = QtGui.QPushButton(self.theme["main/addchum/text"], self)
        self.connect(self.addChumButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addChumWindow()'))
        self.pesterButton = QtGui.QPushButton(self.theme["main/pester/text"], self)
        self.connect(self.pesterButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('pesterSelectedChum()'))
        self.blockButton = QtGui.QPushButton(self.theme["main/block/text"], self)
        self.connect(self.blockButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('blockSelectedChum()'))

        self.moodsLabel = QtGui.QLabel(self.theme["main/moodlabel/text"], self)

        self.mychumhandleLabel = QtGui.QLabel(self.theme["main/mychumhandle/label/text"], self)
        self.mychumhandle = QtGui.QPushButton(self.profile().handle, self)
        self.mychumhandle.setFlat(True)
        self.connect(self.mychumhandle, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('switchProfile()'))

        self.mychumcolor = QtGui.QPushButton(self)
        self.connect(self.mychumcolor, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('changeMyColor()'))

        self.initTheme(self.theme)

        self.waitingMessages = waitingMessageHolder(self)

        if not self.config.defaultprofile():
            self.changeProfile()

    def profile(self):
        return self.userprofile.chat
    def closeConversations(self):
        if not hasattr(self, 'tabconvo'):
            self.tabconvo = None
        if self.tabconvo:
            self.tabconvo.close()
        else:
            for c in self.convos.values():
                c.close()
    def closeEvent(self, event):
        self.closeConversations()
        if hasattr(self, 'trollslum') and self.trollslum:
            self.trollslum.close()
        event.accept()
    def newMessage(self, handle, msg):
        if handle in self.config.getBlocklist():
            #yeah suck on this
            return
        if not self.convos.has_key(handle):
            if msg == "PESTERCHUM:CEASE": # ignore cease after we hang up
                return
            matchingChums = [c for c in self.chumList.chums if c.handle == handle]
            if len(matchingChums) > 0:
                mood = matchingChums[0].mood
            else:
                mood = Mood(0)
            chum = PesterProfile(handle, mood=mood, chumdb=self.chumdb)
            self.newConversation(chum, False)
            if len(matchingChums) == 0:
                self.moodRequest.emit(chum)
        convo = self.convos[handle]
        convo.addMessage(msg, False)
        # play sound here
        self.alarm.play()

    def changeColor(self, handle, color):
        # pesterconvo and chumlist
        self.chumList.updateColor(handle, color)
        if self.convos.has_key(handle):
            self.convos[handle].updateColor(color)
        self.chumdb.setColor(handle, color)

    def updateMood(self, handle, mood):
        self.chumList.updateMood(handle, mood)
        if self.convos.has_key(handle):
            self.convos[handle].updateMood(mood)
        if hasattr(self, 'trollslum') and self.trollslum:
            self.trollslum.updateMood(handle, mood)
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
        self.newConvoStarted.emit(QtCore.QString(chum.handle), initiated)
        convoWindow.show()
    def createTabWindow(self):
        self.tabconvo = PesterTabWindow(self)
        self.connect(self.tabconvo, QtCore.SIGNAL('windowClosed()'),
                     self, QtCore.SLOT('tabsClosed()'))

    def changeProfile(self, collision=None):
        if not hasattr(self, 'chooseprofile'):
            self.chooseprofile = None
        if not self.chooseprofile:
            self.chooseprofile = PesterChooseProfile(self.userprofile, self.config, self.theme, self, collision=collision)
            self.chooseprofile.exec_()

    def themePicker(self):
        if not hasattr(self, 'choosetheme'):
            self.choosetheme = None
        if not self.choosetheme:
            self.choosetheme = PesterChooseTheme(self.config, self.theme, self)
            self.choosetheme.exec_()
    def initTheme(self, theme):
        self.resize(*theme["main/size"])
        self.setWindowIcon(PesterIcon(theme["main/icon"]))
        self.setWindowTitle(theme["main/windowtitle"])
        self.setStyleSheet("QFrame#main { "+theme["main/style"]+" }")
        self.menu.setStyleSheet("QMenuBar { background: transparent; %s } QMenuBar::item { background: transparent; %s } " % (theme["main/menubar/style"], theme["main/menu/menuitem"]) + "QMenu { background: transparent; %s } QMenu::item::selected { %s }" % (theme["main/menu/style"], theme["main/menu/selected"]))
        newcloseicon = PesterIcon(theme["main/close/image"])
        self.closeButton.setIcon(newcloseicon)
        self.closeButton.setIconSize(newcloseicon.realsize())
        self.closeButton.move(*theme["main/close/loc"])
        newminiicon = PesterIcon(theme["main/minimize/image"])
        self.miniButton.setIcon(newminiicon)
        self.miniButton.setIconSize(newminiicon.realsize())
        self.miniButton.move(*theme["main/minimize/loc"])
        # menus
        self.menu.move(*theme["main/menu/loc"])
        self.opts.setText(theme["main/menus/client/options"])
        self.exitaction.setText(theme["main/menus/client/exit"])
        self.userlistaction.setText(theme["main/menus/client/userlist"])
        self.filemenu.setTitle(theme["main/menus/client/_name"])
        self.changetheme.setText(theme["main/menus/profile/theme"])
        self.changequirks.setText(theme["main/menus/profile/quirks"])
        self.loadslum.setText(theme["main/menus/profile/block"])
        self.changecoloraction.setText(theme["main/menus/profile/color"])
        self.switch.setText(theme["main/menus/profile/switch"])
        self.profilemenu.setTitle(theme["main/menus/profile/_name"])

        # moods
        self.moodsLabel.setText(theme["main/moodlabel/text"])
        self.moodsLabel.move(*theme["main/moodlabel/loc"])
        self.moodsLabel.setStyleSheet(theme["main/moodlabel/style"])

        if hasattr(self, 'moods'):
            self.moods.removeButtons()
        self.moods = PesterMoodHandler(self, *[PesterMoodButton(self, **d) for d in theme["main/moods"]])
        self.moods.showButtons()
        # chum
        self.addChumButton.setText(theme["main/addchum/text"])
        self.addChumButton.resize(*theme["main/addchum/size"])
        self.addChumButton.move(*theme["main/addchum/loc"])
        self.addChumButton.setStyleSheet(theme["main/addchum/style"])
        self.pesterButton.setText(theme["main/pester/text"])
        self.pesterButton.resize(*theme["main/pester/size"])
        self.pesterButton.move(*theme["main/pester/loc"])
        self.pesterButton.setStyleSheet(theme["main/pester/style"])
        self.blockButton.setText(theme["main/block/text"])
        self.blockButton.resize(*theme["main/block/size"])
        self.blockButton.move(*theme["main/block/loc"])
        self.blockButton.setStyleSheet(theme["main/block/style"])
        # buttons
        self.mychumhandleLabel.setText(theme["main/mychumhandle/label/text"])
        self.mychumhandleLabel.move(*theme["main/mychumhandle/label/loc"])
        self.mychumhandleLabel.setStyleSheet(theme["main/mychumhandle/label/style"])
        self.mychumhandle.setText(self.profile().handle)
        self.mychumhandle.move(*theme["main/mychumhandle/handle/loc"])
        self.mychumhandle.resize(*theme["main/mychumhandle/handle/size"])
        self.mychumhandle.setStyleSheet(theme["main/mychumhandle/handle/style"])
        self.mychumcolor.resize(*theme["main/mychumhandle/colorswatch/size"])
        self.mychumcolor.move(*theme["main/mychumhandle/colorswatch/loc"])
        self.mychumcolor.setStyleSheet("background: %s" % (self.profile().colorhtml()))
        if theme["main/mychumhandle/colorswatch/text"]:
            self.mychumcolor.setText(theme["main/mychumhandle/colorswatch/text"])

        # sounds
        if not pygame.mixer:
            self.alarm = NoneSound()
        else:
            self.alarm = pygame.mixer.Sound(theme["main/sounds/alertsound"]
)

    def addChum(self, chum):
        self.chumList.addChum(chum)
        self.config.addChum(chum)
        self.moodRequest.emit(chum)
        
    def changeTheme(self, theme):
        self.theme = theme
        # do self
        self.initTheme(theme)
        # chum area
        self.chumList.changeTheme(theme)
        # do open windows
        if self.tabconvo:
            self.tabconvo.changeTheme(theme)
        for c in self.convos.values():
            c.changeTheme(theme)
        if hasattr(self, 'trollslum') and self.trollslum:
            self.trollslum.changeTheme(theme)
        if hasattr(self, 'allusers') and self.allusers:
            self.allusers.changeTheme(theme)
        # system tray icon
        self.updateSystemTray()

    def updateSystemTray(self):
        if len(self.waitingMessages) == 0:
            self.trayIconSignal.emit(0)
        else:
            self.trayIconSignal.emit(1)

    def systemTrayFunction(self):
        if len(self.waitingMessages) == 0:
            if self.isMinimized():
                self.showNormal()
            else:
                if self.isActiveWindow():
                    self.showMinimized()
                else:
                    self.raise_()
                    self.activateWindow()
        else:
            self.waitingMessages.answerMessage()

    @QtCore.pyqtSlot()
    def blockSelectedChum(self):
        curChumListing = self.chumList.currentItem()
        if curChumListing:
            curChum = curChumListing.chum
            self.blockChum(curChum.handle)
    @QtCore.pyqtSlot()
    def pesterSelectedChum(self):
        curChum = self.chumList.currentItem()
        if curChum:
            self.newConversationWindow(curChum)
    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def newConversationWindow(self, chumlisting):
        # check chumdb
        chum = chumlisting.chum
        color = self.chumdb.getColor(chum)
        if color:
            chum.color = color
        self.newConversation(chum)
    @QtCore.pyqtSlot(QtCore.QString)
    def closeConvo(self, handle):
        h = unicode(handle)
        chum = self.convos[h].chum
        chumopen = self.convos[h].chumopen
        if chumopen:
            self.chatlog.log(chum.handle, convertColorTags(self.profile().pestermsg(chum, QtGui.QColor(self.theme["convo/systemMsgColor"]), self.theme["convo/text/ceasepester"]), "bbcode"))
            self.chatlog.finish(h)
            self.convoClosed.emit(handle)
        del self.convos[h]
    @QtCore.pyqtSlot()
    def tabsClosed(self):
        del self.tabconvo
        self.tabconvo = None
                 
    @QtCore.pyqtSlot(QtCore.QString, Mood)
    def updateMoodSlot(self, handle, mood):
        h = unicode(handle)
        self.updateMood(h, mood)

    @QtCore.pyqtSlot(QtCore.QString, QtGui.QColor)
    def updateColorSlot(self, handle, color):
        h = unicode(handle)
        self.changeColor(h, color)

    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString)
    def deliverMessage(self, handle, msg):
        h = unicode(handle)
        m = unicode(msg)
        self.newMessage(h, m)

    @QtCore.pyqtSlot(QtCore.QString, PesterList)
    def updateNames(self, channel, names):
        c = unicode(channel)
        # update name DB
        self.namesdb[c] = names
        # warn interested party of names
        self.namesUpdated.emit()
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString, QtCore.QString)
    def userPresentUpdate(self, handle, channel, update):
        c = unicode(channel)
        n = unicode(handle)
        if update == "quit":
            for c in self.namesdb.keys():
                try:
                    i = self.namesdb[c].index(n)
                    self.namesdb[c].pop(i)
                except ValueError:
                    pass
                except KeyError:
                    self.namesdb[c] = []
        elif update == "left":
            try:
                i = self.namesdb[c].index(n)
                self.namesdb[c].pop(i)
            except ValueError:
                pass
            except KeyError:
                self.namesdb[c] = []
        elif update == "join":
            try:
                i = self.namesdb[c].index(n)
            except ValueError:
                self.namesdb[c].append(n)
            except KeyError:
                self.namesdb[c] = [n]

        self.userPresentSignal.emit(handle, channel, update)

    @QtCore.pyqtSlot()
    def addChumWindow(self):
        if not hasattr(self, 'addchumdialog'):
            self.addchumdialog = None
        if not self.addchumdialog:
            self.addchumdialog = QtGui.QInputDialog(self)
            (handle, ok) = self.addchumdialog.getText(self, "New Chum", "Enter Chum Handle:")
            if ok:
                handle = unicode(handle)
                if not (PesterProfile.checkLength(handle) and
                        PesterProfile.checkValid(handle)):
                    errormsg = QtGui.QErrorMessage(self)
                    errormsg.showMessage("THIS IS NOT A VALID CHUMTAG!")
                    self.addchumdialog = None
                    return
                chum = PesterProfile(handle, chumdb=self.chumdb)
                self.addChum(chum)
            self.addchumdialog = None
    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def removeChum(self, chumlisting):
        self.config.removeChum(chumlisting.chum)
    @QtCore.pyqtSlot(QtCore.QString)
    def blockChum(self, handle):
        h = unicode(handle)
        self.config.addBlocklist(h)
        self.config.removeChum(h)
        if self.convos.has_key(h):
            convo = self.convos[h]
            msg = self.profile().pestermsg(convo.chum, QtGui.QColor(self.theme["convo/systemMsgColor"]), self.theme["convo/text/blocked"])
            convo.textArea.append(convertColorTags(msg))
            self.chatlog.log(convo.chum.handle, convertColorTags(msg, "bbcode"))
            convo.updateBlocked()
        self.chumList.removeChum(h)
        if hasattr(self, 'trollslum') and self.trollslum:
            newtroll = PesterProfile(h)
            self.trollslum.addTroll(newtroll)
            self.moodRequest.emit(newtroll)
        self.blockedChum.emit(handle)

    @QtCore.pyqtSlot(QtCore.QString)
    def unblockChum(self, handle):
        h = unicode(handle)
        self.config.delBlocklist(h)
        if self.convos.has_key(h):
            convo = self.convos[h]
            msg = self.profile().pestermsg(convo.chum, QtGui.QColor(self.theme["convo/systemMsgColor"]), self.theme["convo/text/unblocked"])
            convo.textArea.append(convertColorTags(msg))
            self.chatlog.log(convo.chum.handle, convertColorTags(msg, "bbcode"))
            convo.updateMood(convo.chum.mood, unblocked=True)
        chum = PesterProfile(h, chumdb=self.chumdb)
        if hasattr(self, 'trollslum') and self.trollslum:
            self.trollslum.removeTroll(handle)
        self.config.addChum(chum)
        self.chumList.addChum(chum)
        self.moodRequest.emit(chum)
        self.unblockedChum.emit(handle)

    @QtCore.pyqtSlot()
    def showAllUsers(self):
        if not hasattr(self, 'allusers'):
            self.allusers = None
        if not self.allusers:
            self.allusers = PesterUserlist(self.config, self.theme, self)
            self.connect(self.allusers, QtCore.SIGNAL('accepted()'),
                         self, QtCore.SLOT('userListClose()'))
            self.connect(self.allusers, QtCore.SIGNAL('rejected()'),
                         self, QtCore.SLOT('userListClose()'))
            self.connect(self.allusers, QtCore.SIGNAL('addChum(QString)'),
                         self, QtCore.SLOT('userListAdd(QString)'))
            self.requestNames.emit("#pesterchum")
            self.allusers.show()

    @QtCore.pyqtSlot(QtCore.QString)
    def userListAdd(self, handle):
        h = unicode(handle)
        chum = PesterProfile(h, chumdb=self.chumdb)
        self.addChum(chum)
    @QtCore.pyqtSlot()
    def userListClose(self):
        self.allusers = None
    @QtCore.pyqtSlot()
    def openQuirks(self):
        if not hasattr(self, 'quirkmenu'):
            self.quirkmenu = None
        if not self.quirkmenu:
            self.quirkmenu = PesterChooseQuirks(self.config, self.theme, self)
            self.connect(self.quirkmenu, QtCore.SIGNAL('accepted()'),
                         self, QtCore.SLOT('updateQuirks()'))
            self.connect(self.quirkmenu, QtCore.SIGNAL('rejected()'),
                         self, QtCore.SLOT('closeQuirks()'))
            self.quirkmenu.show()
            self.quirkmenu.raise_()
            self.quirkmenu.activateWindow()
    @QtCore.pyqtSlot()
    def updateQuirks(self):
        quirks = pesterQuirks(self.quirkmenu.quirks())
        self.userprofile.setQuirks(quirks)
        self.quirkmenu = None
    @QtCore.pyqtSlot()
    def closeQuirks(self):
        self.quirkmenu = None
    @QtCore.pyqtSlot()
    def openOpts(self):
        if not hasattr(self, 'optionmenu'):
            self.optionmenu = None
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
        themename = unicode(self.choosetheme.themeBox.currentText())
        if themename != self.theme.name:
            try:
                self.changeTheme(pesterTheme(themename))
            except ValueError, e:
                themeWarning = QtGui.QMessageBox(self)
                themeWarning.setText("Theme Error: %s" % (e))
                themeWarning.exec_()
                self.choosetheme = None
                return
            # update profile
            self.userprofile.setTheme(self.theme)
        self.choosetheme = None
    @QtCore.pyqtSlot()
    def closeTheme(self):
        self.choosetheme = None
    @QtCore.pyqtSlot()
    def profileSelected(self):
        if self.chooseprofile.profileBox and \
                self.chooseprofile.profileBox.currentIndex() > 0:
            handle = unicode(self.chooseprofile.profileBox.currentText())
            if handle == self.profile().handle:
                self.chooseprofile = None
                return
            self.userprofile = userProfile(handle)
            self.changeTheme(self.userprofile.getTheme())
        else:
            handle = unicode(self.chooseprofile.chumHandle.text())
            if handle == self.profile().handle:
                self.chooseprofile = None
                return
            profile = PesterProfile(handle,
                                    self.chooseprofile.chumcolor)
            self.userprofile = userProfile.newUserProfile(profile)
            self.changeTheme(self.userprofile.getTheme())

        self.chatlog.close()
        self.chatlog = PesterLog(handle)

        # is default?
        if self.chooseprofile.defaultcheck.isChecked():
            self.config.set("defaultprofile", self.userprofile.chat.handle)
        # this may have to be fixed
        self.closeConversations()
        if hasattr(self, 'trollslum') and self.trollslum:
            self.trollslum.close()
        self.chooseprofile = None
        self.profileChanged.emit()
    @QtCore.pyqtSlot()
    def showTrollSlum(self):
        if not hasattr(self, 'trollslum'):
            self.trollslum = None
        if self.trollslum:
            return
        trolls = [PesterProfile(h) for h in self.config.getBlocklist()]
        self.trollslum = TrollSlumWindow(trolls, self)
        self.connect(self.trollslum, QtCore.SIGNAL('blockChumSignal(QString)'),
                     self, QtCore.SLOT('blockChum(QString)'))
        self.connect(self.trollslum, 
                     QtCore.SIGNAL('unblockChumSignal(QString)'),
                     self, QtCore.SLOT('unblockChum(QString)'))
        self.moodsRequest.emit(PesterList(trolls))
        self.trollslum.show()
    @QtCore.pyqtSlot()
    def closeTrollSlum(self):
        self.trollslum = None
    @QtCore.pyqtSlot()
    def changeMyColor(self):
        if not hasattr(self, 'colorDialog'):
            self.colorDialog = None
        if self.colorDialog:
            return
        self.colorDialog = QtGui.QColorDialog(self)
        color = self.colorDialog.getColor(initial=self.profile().color)
        self.mychumcolor.setStyleSheet("background: %s" % color.name())
        self.userprofile.setColor(color)
        self.mycolorUpdated.emit()
        self.colorDialog = None
    @QtCore.pyqtSlot()
    def closeProfile(self):
        self.chooseprofile = None
    @QtCore.pyqtSlot()
    def switchProfile(self):
        if self.convos:
            closeWarning = QtGui.QMessageBox()
            closeWarning.setText("WARNING: CHANGING PROFILES WILL CLOSE ALL CONVERSATION WINDOWS!")
            closeWarning.setInformativeText("i warned you about windows bro!!!! i told you dog!")
            closeWarning.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
            closeWarning.setDefaultButton(QtGui.QMessageBox.Ok)
            ret = closeWarning.exec_()
            if ret == QtGui.QMessageBox.Cancel:
                return
        self.changeProfile()

    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString)
    def nickCollision(self, handle, tmphandle):
        self.mychumhandle.setText(tmphandle)
        if not hasattr(self, 'chooseprofile'):
            self.chooseprofile = None
        if not self.chooseprofile:
            h = unicode(handle)
            self.changeProfile(collision=h)
        
    @QtCore.pyqtSlot()
    def pickTheme(self):
        self.themePicker()

    @QtCore.pyqtSlot(QtGui.QSystemTrayIcon.ActivationReason)
    def systemTrayActivated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.systemTrayFunction()
        elif reason == QtGui.QSystemTrayIcon.Context:
            # show context menu i guess
            pass

    newConvoStarted = QtCore.pyqtSignal(QtCore.QString, bool, name="newConvoStarted")
    sendMessage = QtCore.pyqtSignal(QtCore.QString, PesterProfile)
    convoClosed = QtCore.pyqtSignal(QtCore.QString)
    profileChanged = QtCore.pyqtSignal()
    moodRequest = QtCore.pyqtSignal(PesterProfile)
    moodsRequest = QtCore.pyqtSignal(PesterList)
    moodUpdated = QtCore.pyqtSignal()
    requestNames = QtCore.pyqtSignal(QtCore.QString)
    namesUpdated = QtCore.pyqtSignal()
    userPresentSignal = QtCore.pyqtSignal(QtCore.QString,QtCore.QString,QtCore.QString)
    mycolorUpdated = QtCore.pyqtSignal()
    trayIconSignal = QtCore.pyqtSignal(int)
    blockedChum = QtCore.pyqtSignal(QtCore.QString)
    unblockedChum = QtCore.pyqtSignal(QtCore.QString)

class PesterIRC(QtCore.QObject):
    def __init__(self, window):
        QtCore.QObject.__init__(self)
        self.mainwindow = window
    def IRCConnect(self):
        self.cli = IRCClient(PesterHandler, host="irc.tymoon.eu", port=6667, nick=self.mainwindow.profile().handle, blocking=True)
        self.cli.command_handler.parent = self
        self.cli.command_handler.mainwindow = self.mainwindow
        self.conn = self.cli.connect()

    @QtCore.pyqtSlot(PesterProfile)
    def getMood(self, *chums):
        self.cli.command_handler.getMood(*chums)
    @QtCore.pyqtSlot(PesterList)
    def getMoods(self, chums):
        self.cli.command_handler.getMood(*chums)
        
    @QtCore.pyqtSlot(QtCore.QString, PesterProfile)
    def sendMessage(self, text, chum):
        handle = chum.handle
        helpers.msg(self.cli, handle, text)

    @QtCore.pyqtSlot(QtCore.QString, bool)
    def startConvo(self, handle, initiated):
        h = unicode(handle)
        if initiated:
            helpers.msg(self.cli, h, "PESTERCHUM:BEGIN")
        helpers.msg(self.cli, h, "COLOR >%s" % (self.mainwindow.profile().colorcmd()))
    @QtCore.pyqtSlot(QtCore.QString)
    def endConvo(self, handle):
        h = unicode(handle)
        helpers.msg(self.cli, h, "PESTERCHUM:CEASE")
    @QtCore.pyqtSlot()
    def updateProfile(self):
        me = self.mainwindow.profile()
        handle = me.handle
        helpers.nick(self.cli, handle)
        self.updateMood()
    @QtCore.pyqtSlot()
    def updateMood(self):
        me = self.mainwindow.profile()
        helpers.msg(self.cli, "#pesterchum", "MOOD >%d" % (me.mood.value()))
    @QtCore.pyqtSlot()
    def updateColor(self):
        me = self.mainwindow.profile()
        for h in self.mainwindow.convos.keys():
            helpers.msg(self.cli, h, "COLOR >%s" % (self.mainwindow.profile().colorcmd()))
    @QtCore.pyqtSlot(QtCore.QString)
    def blockedChum(self, handle):
        h = unicode(handle)
        helpers.msg(self.cli, h, "PESTERCHUM:BLOCK")
    @QtCore.pyqtSlot(QtCore.QString)
    def unblockedChum(self, handle):
        h = unicode(handle)
        helpers.msg(self.cli, h, "PESTERCHUM:UNBLOCK")
    @QtCore.pyqtSlot(QtCore.QString)
    def requestNames(self, channel):
        c = unicode(channel)
        helpers.names(self.cli, c)

    def updateIRC(self):
        self.conn.next()

    moodUpdated = QtCore.pyqtSignal(QtCore.QString, Mood)
    colorUpdated = QtCore.pyqtSignal(QtCore.QString, QtGui.QColor)
    messageReceived = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
    namesReceived = QtCore.pyqtSignal(QtCore.QString, PesterList)
    nickCollision = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
    userPresentUpdate = QtCore.pyqtSignal(QtCore.QString, QtCore.QString,
                                   QtCore.QString)

class PesterHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        # display msg, do other stuff
        # silently ignore CTCP
        if msg[0] == '\x01':
            return
        handle = nick[0:nick.find("!")]
        logging.info("---> recv \"PRIVMSG %s :%s\"" % (handle, msg))
        if chan == "#pesterchum":
            # follow instructions
            if msg[0:6] == "MOOD >":
                try:
                    mood = Mood(int(msg[6:]))
                except ValueError:
                    mood = Mood(0)
                self.parent.moodUpdated.emit(handle, mood)
            elif msg[0:7] == "GETMOOD":
                mychumhandle = self.mainwindow.profile().handle
                mymood = self.mainwindow.profile().mood.value()
                if msg.find(mychumhandle, 8) != -1:
                    helpers.msg(self.client, "#pesterchum", 
                                "MOOD >%d" % (mymood))
                    
        else:
            # private message
            # silently ignore messages to yourself.
            if handle == self.mainwindow.profile().handle:
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
        mychumhandle = self.mainwindow.profile().handle
        mymood = self.mainwindow.profile().mood.value()
        helpers.msg(self.client, "#pesterchum", "MOOD >%d" % (mymood))

        chums = self.mainwindow.chumList.chums
        self.getMood(*chums)

    def nicknameinuse(self, server, cmd, nick, msg):
        newnick = "pesterClient%d" % (random.randint(100,999))
        helpers.nick(self.client, newnick)
        self.parent.nickCollision.emit(nick, newnick)
    def quit(self, nick, reason):
        handle = nick[0:nick.find("!")]
        self.parent.userPresentUpdate.emit(handle, "", "quit")
        self.parent.moodUpdated.emit(handle, Mood("offline"))        
    def part(self, nick, channel, reason="nanchos"):
        handle = nick[0:nick.find("!")]
        self.parent.userPresentUpdate.emit(handle, channel, "left")
        if channel == "#pesterchum":
            self.parent.moodUpdated.emit(handle, Mood("offline"))
    def join(self, nick, channel):
        handle = nick[0:nick.find("!")]
        self.parent.userPresentUpdate.emit(handle, channel, "join")
        if channel == "#pesterchum":
            self.parent.moodUpdated.emit(handle, Mood("chummy"))
    def nick(self, oldnick, newnick):
        oldhandle = oldnick[0:oldnick.find("!")]
        newchum = PesterProfile(newnick, chumdb=self.mainwindow.chumdb)
        self.parent.moodUpdated.emit(oldhandle, Mood("offline"))        
        if newnick in self.mainwindow.chumList.chums:
            self.getMood(newchum)
    def namreply(self, server, nick, op, channel, names):
        namelist = names.split(" ")
        logging.info("---> recv \"NAMES %s: %d names\"" % (channel, len(namelist)))
        if not hasattr(self, 'channelnames'):
            self.channelnames = {}
        if not self.channelnames.has_key(channel):
            self.channelnames[channel] = []
        self.channelnames[channel].extend(namelist)
    def endofnames(self, server, nick, channel, msg):
        namelist = self.channelnames[channel]
        pl = PesterList(namelist)
        del self.channelnames[channel]
        self.parent.namesReceived.emit(channel, pl)
        
    def getMood(self, *chums):
        chumglub = "GETMOOD "
        for c in chums:
            chandle = c.handle
            if len(chumglub+chandle) >= 350:
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

class PesterTray(QtGui.QSystemTrayIcon):
    def __init__(self, icon, mainwindow, parent):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        self.mainwindow = mainwindow
        traymenu = QtGui.QMenu()
        traymenu.addAction("Hi!! HI!!")
        self.setContextMenu(traymenu)

    @QtCore.pyqtSlot(int)
    def changeTrayIcon(self, i):
        if i == 0:
            self.setIcon(PesterIcon(self.mainwindow.theme["main/icon"]))
        else:
            self.setIcon(PesterIcon(self.mainwindow.theme["main/newmsgicon"]))

def main():

    app = QtGui.QApplication(sys.argv)
    if pygame.mixer:
        # we could set the frequency higher but i love how cheesy it sounds
        pygame.mixer.init()
    else:
        print "Warning: No sound!"
    widget = PesterWindow()
    widget.show()

    trayicon = PesterTray(PesterIcon(widget.theme["main/icon"]), widget, app)
    trayicon.show()
    
    trayicon.connect(trayicon, 
                     QtCore.SIGNAL('activated(QSystemTrayIcon::ActivationReason)'),
                     widget,
                     QtCore.SLOT('systemTrayActivated(QSystemTrayIcon::ActivationReason)'))
    trayicon.connect(widget,
                     QtCore.SIGNAL('trayIconSignal(int)'),
                     trayicon,
                     QtCore.SLOT('changeTrayIcon(int)'))
        
    
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
    irc.connect(widget,
                QtCore.SIGNAL('moodsRequest(PyQt_PyObject)'),
                irc,
                QtCore.SLOT('getMoods(PyQt_PyObject)'))
    irc.connect(widget,
                QtCore.SIGNAL('moodUpdated()'),
                irc,
                QtCore.SLOT('updateMood()'))
    irc.connect(widget,
                QtCore.SIGNAL('mycolorUpdated()'),
                irc,
                QtCore.SLOT('updateColor()'))
    irc.connect(widget,
                QtCore.SIGNAL('blockedChum(QString)'),
                irc,
                QtCore.SLOT('blockedChum(QString)'))
    irc.connect(widget,
                QtCore.SIGNAL('unblockedChum(QString)'),
                irc,
                QtCore.SLOT('unblockedChum(QString)'))
    irc.connect(widget,
                QtCore.SIGNAL('requestNames(QString)'),
                irc,
                QtCore.SLOT('requestNames(QString)'))

# IRC --> Main window
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
                QtCore.SIGNAL('nickCollision(QString, QString)'),
                widget,
                QtCore.SLOT('nickCollision(QString, QString)'))
    irc.connect(irc,
                QtCore.SIGNAL('namesReceived(QString, PyQt_PyObject)'),
                widget,
                QtCore.SLOT('updateNames(QString, PyQt_PyObject)'))
    irc.connect(irc,
                QtCore.SIGNAL('userPresentUpdate(QString, QString, QString)'),
                widget,
                QtCore.SLOT('userPresentUpdate(QString, QString, QString)'))

    ircapp = IRCThread(irc)
    ircapp.start()
    sys.exit(app.exec_())

main()

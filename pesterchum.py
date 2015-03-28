# pesterchum
import os, shutil, sys, getopt
if os.path.dirname(sys.argv[0]):
    os.chdir(os.path.dirname(sys.argv[0]))
import version
version.pcVerCalc()
import logging
from datetime import *
import random
import re
from time import time
import threading, queue
import collections

reqmissing = []
optmissing = []
try:
    from PyQt5 import QtGui, QtCore, QtWidgets, QtMultimedia
except ImportError as e:
    module = str(e)
    if module.startswith("No module named ") or \
       module.startswith("cannot import name "):
        reqmissing.append(module[module.rfind(" ")+1:])
    else: print(e)

if reqmissing:
    print("ERROR: The following modules are required for Pesterchum to run and are missing on your system:")
    for m in reqmissing: print("* "+m)
    exit()
vnum = QtCore.qVersion()
major = int(vnum[:vnum.find(".")])
if vnum.find(".", vnum.find(".")+1) != -1:
    minor = int(vnum[vnum.find(".")+1:vnum.find(".", vnum.find(".")+1)])
else:
    minor = int(vnum[vnum.find(".")+1:])
if not ((major > 4) or (major == 4 and minor >= 6)):
    print("ERROR: Pesterchum requires Qt version >= 4.6")
    print("You currently have version " + vnum + ". Please upgrade Qt")
    exit()

import ostools
# Placed here before importing the rest of pesterchum, since bits of it need
#  OSX's data directory and it doesn't hurt to have everything set up before
#  plowing on. :o)
# ~Lex
_datadir = ostools.getDataDir()
# See, what I've done here is that _datadir is '' if we're not on OSX, so the
#  concatination is the same as if it wasn't there.
# UPDATE 2011-11-28 <Kiooeht>:
#   Now using data directory as defined by QDesktopServices on all platforms
#   (on Linux, same as using xdg). To stay safe with older versions, copy any
#   data (profiles, logs, etc) from old location to new data directory.

if _datadir:
    if not os.path.exists(_datadir):
        os.makedirs(_datadir)
    if not os.path.exists(_datadir+"profiles/") and os.path.exists("profiles/"):
        shutil.move("profiles/", _datadir+"profiles/")
    if not os.path.exists(_datadir+"pesterchum.js") and os.path.exists("pesterchum.js"):
        shutil.move("pesterchum.js", _datadir+"pesterchum.js")
    if not os.path.exists(_datadir+"logs/") and os.path.exists("logs/"):
        shutil.move("logs/", _datadir+"logs/")

if not os.path.exists(_datadir+"profiles"):
    os.mkdir(_datadir+"profiles")
if not os.path.exists(_datadir+"pesterchum.js"):
    f = open(_datadir+"pesterchum.js", 'w')
    f.write("{}")
    f.close()
if not os.path.exists(_datadir+"logs"):
    os.mkdir(_datadir+"logs")

from menus import PesterChooseQuirks, PesterChooseTheme, \
    PesterChooseProfile, PesterOptions, PesterUserlist, PesterMemoList, \
    LoadingScreen, AboutPesterchum, UpdatePesterchum, AddChumDialog, \
    LoginScreen
from mood import Mood, PesterMoodAction, PesterMoodHandler, PesterMoodButton
from dataobjs import PesterProfile, pesterQuirk, pesterQuirks, pesterBegin, pesterCease
from generic import PesterIcon, RightClickList, RightClickTree, \
    MultiTextDialog, PesterList, CaseInsensitiveDict, MovingWindow, \
    NoneSound, WMButton, PesterDict
from convo import PesterTabWindow, PesterText, PesterInput, PesterConvo
from parsetools import convertTags, addTimeInitial, themeChecker, ThemeException
from memos import PesterMemo, MemoTabWindow, TimeTracker
from osfcpester import PesterOSFC
from logviewer import PesterLogUserSelect, PesterLogViewer
from bugreport import BugReporter
from randomer import RandomHandler, RANDNICK
import nickservmsgs

# Rawr, fuck you OSX leopard
if not ostools.isOSXLeopard():
    from updatecheck import MSPAChecker

from toast import PesterToastMachine, PesterToast
from libs import pytwmn
from profile import *

canon_handles = ["apocalypseArisen", "arsenicCatnip", "arachnidsGrip", "adiosToreador", \
                 "caligulasAquarium", "cuttlefishCuller", "carcinoGeneticist", "centaursTesticle", \
                 "grimAuxiliatrix", "gallowsCalibrator", "gardenGnostic", "ectoBiologist", \
                 "twinArmageddons", "terminallyCapricious", "turntechGodhead", "tentacleTherapist"]
CUSTOMBOTS = ["CALSPRITE", RANDNICK.upper()]
BOTNAMES = ["NICKSERV", "CHANSERV", "MEMOSERV", "OPERSERV", "HELPSERV"]
BOTNAMES.extend(CUSTOMBOTS)


class waitingMessageHolder(object):
    def __init__(self, mainwindow, **msgfuncs):
        self.mainwindow = mainwindow
        self.funcs = msgfuncs
        self.queue = list(msgfuncs.keys())
        if len(self.queue) > 0:
            self.mainwindow.updateSystemTray()
    def waitingHandles(self):
        return self.queue
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
        if handle not in self.funcs:
            self.queue.append(handle)
        self.funcs[handle] = func
        if len(self.queue) > 0:
            self.mainwindow.updateSystemTray()
    def __len__(self):
        return len(self.queue)

class chumListing(QtWidgets.QTreeWidgetItem):
    def __init__(self, chum, window, clone=False):
        QtWidgets.QTreeWidgetItem.__init__(self, [chum.handle])
        self.mainwindow = window
        self.chum = chum
        self.handle = chum.handle
        if not clone:
            self.setMood(Mood("offline"))
        self.status = None
        self.setToolTip(0, "%s: %s" % (chum.handle, window.chumdb.getNotes(chum.handle)))
    def clone(self):
        cl = chumListing(self.chum, self.mainwindow, clone=True)
        cl.handle = self.handle
        cl.status = self.status
        cl.updateMood()
        return cl
    def setMood(self, mood):
        if hasattr(self.mainwindow, "chumList") and self.mainwindow.chumList.notify:
            #print "%s -> %s" % (self.chum.mood.name(), mood.name())
            if self.mainwindow.config.notifyOptions() & self.mainwindow.config.SIGNOUT and \
               mood.name() == "offline" and self.chum.mood.name() != "offline":
                #print "OFFLINE NOTIFY: " + self.handle
                uri = self.mainwindow.theme["toasts/icon/signout"]
                n = self.mainwindow.tm.Toast(self.mainwindow.tm.appName,
                                          "%s is Offline" % (self.handle), uri)
                n.show()
            elif self.mainwindow.config.notifyOptions() & self.mainwindow.config.SIGNIN and \
                 mood.name() != "offline" and self.chum.mood.name() == "offline":
                #print "ONLINE NOTIFY: " + self.handle
                uri = self.mainwindow.theme["toasts/icon/signin"]
                n = self.mainwindow.tm.Toast(self.mainwindow.tm.appName,
                                          "%s is Online" % (self.handle), uri)
                n.show()
        login = False
        logout = False
        if mood.name() == "offline" and self.chum.mood.name() != "offline":
            logout = True
        elif mood.name() != "offline" and self.chum.mood.name() == "offline":
            login = True
        self.chum.mood = mood
        self.updateMood(login=login, logout=logout)
    def setColor(self, color):
        self.chum.color = color
    def updateMood(self, unblock=False, login=False, logout=False):
        mood = self.chum.mood
        self.mood = mood
        icon = self.mood.icon(self.mainwindow.theme)
        if login:
            self.login()
        elif logout:
            self.logout()
        else:
            self.setIcon(0, icon)
        try:
            self.setForeground(0, QtGui.QBrush(QtGui.QColor(self.mainwindow.theme["main/chums/moods"][self.mood.name()]["color"])))
        except KeyError:
            self.setForeground(0, QtGui.QBrush(QtGui.QColor(self.mainwindow.theme["main/chums/moods/chummy/color"])))
    def changeTheme(self, theme):
        icon = self.mood.icon(theme)
        self.setIcon(0, icon)
        try:
            self.setForeground(0, QtGui.QBrush(QtGui.QColor(self.mainwindow.theme["main/chums/moods"][self.mood.name()]["color"])))
        except KeyError:
            self.setForeground(0, QtGui.QBrush(QtGui.QColor(self.mainwindow.theme["main/chums/moods/chummy/color"])))
    def login(self):
        self.setIcon(0, PesterIcon("themes/arrow_right.png"))
        self.status = "in"
        QtCore.QTimer.singleShot(5000, self.doneLogin)
    def doneLogin(self):
        icon = self.mood.icon(self.mainwindow.theme)
        self.setIcon(0, icon)
    def logout(self):
        self.setIcon(0, PesterIcon("themes/arrow_left.png"))
        self.status = "out"
        QtCore.QTimer.singleShot(5000, self.doneLogout)
    def doneLogout(self):
        hideoff = self.mainwindow.config.hideOfflineChums()
        icon = self.mood.icon(self.mainwindow.theme)
        self.setIcon(0, icon)
        if hideoff and self.status and self.status == "out":
            self.mainwindow.chumList.takeItem(self)
    def __lt__(self, cl):
        h1 = self.handle.lower()
        h2 = cl.handle.lower()
        return (h1 < h2)

class chumArea(RightClickTree):
    def __init__(self, chums, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.notify = False
        QtCore.QTimer.singleShot(30000, self.beginNotify)
        self.mainwindow = parent
        theme = self.mainwindow.theme
        self.chums = CaseInsensitiveDict()
        self.groups = CaseInsensitiveDict()
        self.openGroups = CaseInsensitiveDict()
        self.addGroup("Friends")
        for chandle in chums:
            self.addChum(chandle)
        if not self.mainwindow.config.showEmptyGroups():
            self.hideEmptyGroups()
        self.groupMenu = QtWidgets.QMenu(self)
        self.canonMenu = QtWidgets.QMenu(self)
        self.optionsMenu = QtWidgets.QMenu(self)
        self.pester = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/pester"], self, triggered=self.activateChum)
        self.removechum = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/removechum"], self, triggered=self.removeChum)
        self.blockchum = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/blockchum"], self, triggered=self.blockChum)
        self.logchum = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/viewlog"], self, triggered=self.openChumLogs)
        self.reportchum = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/report"], self, triggered=self.reportChum)
        self.findalts = QtWidgets.QAction("Find Alts", self, triggered=self.findAlts)
        self.removegroup = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/removegroup"], self, triggered=self.removeGroup)
        self.renamegroup = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/renamegroup"], self, triggered=self.renameGroup)
        self.notes = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/notes"], self, triggered=self.editNotes)

        self.optionsMenu.addAction(self.pester)
        self.optionsMenu.addAction(self.logchum)
        self.optionsMenu.addAction(self.notes)
        self.optionsMenu.addAction(self.blockchum)
        self.optionsMenu.addAction(self.removechum)
        self.moveMenu = QtWidgets.QMenu(self.mainwindow.theme["main/menus/rclickchumlist/movechum"], self)
        self.optionsMenu.addMenu(self.moveMenu)
        self.optionsMenu.addAction(self.reportchum)
        self.moveGroupMenu()

        self.groupMenu.addAction(self.renamegroup)
        self.groupMenu.addAction(self.removegroup)

        self.canonMenu.addAction(self.pester)
        self.canonMenu.addAction(self.logchum)
        self.canonMenu.addAction(self.blockchum)
        self.canonMenu.addAction(self.removechum)
        self.canonMenu.addMenu(self.moveMenu)
        self.canonMenu.addAction(self.reportchum)
        self.canonMenu.addAction(self.findalts)

        self.initTheme(theme)
        self.setSortingEnabled(False)
        self.header().hide()
        self.setDropIndicatorShown(True)
        self.setIndentation(4)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setAnimated(True)
        self.setRootIsDecorated(False)

        self.itemDoubleClicked.connect(self.expandGroup)

    @QtCore.pyqtSlot()
    def beginNotify(self):
        self.notify = True

    def getOptionsMenu(self):
        if not self.currentItem():
            return None
        text = self.currentItem().data(0, QtCore.Qt.ToolTipRole)
        if text == "Friends":
            return None
        elif text in self.groups:
            return self.groupMenu
        else:
            currenthandle = self.currentItem().chum.handle
            if currenthandle in canon_handles:
                return self.canonMenu
            else:
                return self.optionsMenu

    def startDrag(self, dropAction):
        # create mime data object
        mime = QtCore.QMimeData()
        mime.setData('application/x-item', '???')
        # start drag
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime)
        drag.start(QtCore.Qt.MoveAction)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-item"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        if (event.mimeData().hasFormat('application/x-item')):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if (event.mimeData().hasFormat('application/x-item')):
            event.acceptProposedAction()
        else:
            event.ignore()
            return
        thisitem = event.source().currentItem().text(0)
        if thisitem in self.chums:
            # Drop item is a chum
            item = self.itemAt(event.pos())
            if item:
                text = item.data(0, QtCore.Qt.ToolTipRole)
                # Figure out which group to drop into
                if text == "Friends" or text in self.groups:
                    group = text
                    gitem = item
                else:
                    ptext = item.parent().data(0, QtCore.Qt.ToolTipRole)
                    group = ptext
                    gitem = item.parent()
                self.moveChumToGroup()

    def moveGroupMenu(self):
        currentGroup = self.currentItem()
        if currentGroup:
            if currentGroup.parent():
                text = currentGroup.parent().data(0, QtCore.Qt.ToolTipRole)
            else:
                text = currentGroup.data(0, QtCore.Qt.ToolTipRole)
            currentGroup = text
        self.moveMenu.clear()
        actGroup = QtWidgets.QActionGroup(self)

        groups = self.groups.keys()
        for gtext in groups:
            if gtext == currentGroup:
                continue
            movegroup = self.moveMenu.addAction(gtext)
            actGroup.addAction(movegroup)
        actGroup.triggered.connect(self.moveToGroup)

    def addChum(self, chum):
        if chum.handle in self.chums:
            return
        self.chums[chum.handle] = chumListing(chum, self.mainwindow)
        self.refreshList()

    def addGroup(self, groupName):
        if groupName not in self.groups:
            self.groups[groupName] = QtWidgets.QTreeWidgetItem([groupName])
            self.groups[groupName].setData(0, QtCore.Qt.ToolTipRole, groupName)
            self.openGroups[groupName] = True
        self.refreshList()

    # The first rule of optimization: Don't do it.
    def refreshList(self):
        self.tmpchums = CaseInsensitiveDict()
        self.tmpchums = {k: v.clone() for k, v in self.chums.items()}
        self.clear()

        if "Friends" not in self.groups:
            self.groups["Friends"] = True # placeholder
            self.openGroups["Friends"]  = True

        for groupName in self.groups.keys():
            gItem = QtWidgets.QTreeWidgetItem([groupName])
            gItem.setData(0, QtCore.Qt.ToolTipRole, groupName)
            self.groups[groupName] = gItem
            self.addTopLevelItem(gItem)
            
        # add all visible groups and clients
        for chumName in self.chums.keys():
            listing = self.tmpchums[chumName]
            group = listing.chum.group
            if group not in self.groups:
                logging.error("---> Group not found during refresh: {0}; groups are {1}".format(group, self.groups))
                continue

            self.groups[group].addChild(listing)
        for groupName, openGroup in self.openGroups.items():
            self.groups[groupName].setExpanded(openGroup)
        if self.mainwindow.config.hideOfflineChums():
            self.hideOfflineChums()
        if not self.mainwindow.config.showEmptyGroups():
            self.hideEmptyGroups()
        self.sort()
        if self.mainwindow.config.showOnlineNumbers():
            self.showOnlineNumbers()

    def hideOfflineChums(self):
        for j in range(self.topLevelItemCount()):
            i = 0
            listing = self.topLevelItem(j).child(i)
            while listing is not None:
                if listing.chum.mood.name() == "offline":
                    self.topLevelItem(j).takeChild(i)
                else:
                    i += 1
                listing = self.topLevelItem(j).child(i)
            self.sort()

    def showOnlineNumbers(self):
        if hasattr(self, 'groups'):
          totals = {'Friends': 0}
          online = {'Friends': 0}
          for listing in self.chums.values():
              totals[listing.chum.group] = totals.setdefault(listing.chum.group, 0) + 1
              if listing.chum.mood.name() != "offline":
                  online[listing.chum.group] = totals.setdefault(listing.chum.group, 0) + 1
          for i in range(self.topLevelItemCount()):
              text = str(self.topLevelItem(i).text(0))
              if text in online:
                  self.topLevelItem(i).setText(0, "%s (%i/%i)" % (text, online[text], totals[text]))

    def hideEmptyGroups(self):
        i = 0
        listing = self.topLevelItem(i)
        while listing is not None:
            if listing.childCount() == 0:
                self.takeTopLevelItem(i)
            else:
                i += 1
            listing = self.topLevelItem(i)

    @QtCore.pyqtSlot()
    def expandGroup(self): # save expansion setting
        item = self.currentItem()
        text = item.text(0)
        expand = item.isExpanded()
        self.mainwindow.config.expandGroup(text, not expand)

    def updateMood(self, handle, mood):
        oldmood = None
        if handle in self.chums:
            oldmood = self.chums[handle].chum.mood
            self.chums[handle].setMood(mood)
        self.refreshList()
        return oldmood
    def updateColor(self, handle, color):
        if handle in self.chums:
            self.chums[handle].chum.setColor(color)
    def initTheme(self, theme):
        self.resize(*theme["main/chums/size"])
        self.move(*theme["main/chums/loc"])
        if "main/chums/scrollbar" in theme:
            self.setStyleSheet("QListWidget { %s } QScrollBar { %s } QScrollBar::handle { %s } QScrollBar::add-line { %s } QScrollBar::sub-line { %s } QScrollBar:up-arrow { %s } QScrollBar:down-arrow { %s }" % (theme["main/chums/style"], theme["main/chums/scrollbar/style"], theme["main/chums/scrollbar/handle"], theme["main/chums/scrollbar/downarrow"], theme["main/chums/scrollbar/uparrow"], theme["main/chums/scrollbar/uarrowstyle"], theme["main/chums/scrollbar/darrowstyle"] ))
        else:
            self.setStyleSheet(theme["main/chums/style"])
        self.pester.setText(theme["main/menus/rclickchumlist/pester"])
        self.removechum.setText(theme["main/menus/rclickchumlist/removechum"])
        self.blockchum.setText(theme["main/menus/rclickchumlist/blockchum"])
        self.logchum.setText(theme["main/menus/rclickchumlist/viewlog"])
        self.reportchum.setText(theme["main/menus/rclickchumlist/report"])
        self.notes.setText(theme["main/menus/rclickchumlist/notes"])
        self.removegroup.setText(theme["main/menus/rclickchumlist/removegroup"])
        self.renamegroup.setText(theme["main/menus/rclickchumlist/renamegroup"])
        self.moveMenu.setTitle(theme["main/menus/rclickchumlist/movechum"])
    def changeTheme(self, theme):
        self.initTheme(theme)
        chumlistings = []
        for i in range(self.topLevelItemCount()):
            for j in range(self.topLevelItem(i).childCount()):
                chumlistings.append(self.topLevelItem(i).child(j))
        #chumlistings = [self.item(i) for i in range(0, self.count())]
        for c in chumlistings:
            c.changeTheme(theme)

    def count(self):
        c = 0
        for i in range(self.topLevelItemCount()):
            c = c + self.topLevelItem(i).childCount()
        return c

    def sort(self):
        self.sortItems
        if self.mainwindow.config.sortMethod() == 1:
            for i in range(self.topLevelItemCount()):
                self.moodSort(i)
        else:
            for i in range(self.topLevelItemCount()):
                self.topLevelItem(i).sortChildren(0, QtCore.Qt.AscendingOrder)

    def moodSort(self, group):
        scrollPos = self.verticalScrollBar().sliderPosition()
        chums = []
        listing = self.topLevelItem(group).child(0)
        while listing is not None:
            chums.append(self.topLevelItem(group).takeChild(0))
            listing = self.topLevelItem(group).child(0)
        chums.sort(key=lambda x: ((999 if x.chum.mood.value() == 2 else x.chum.mood.value()), x.chum.handle), reverse=False)
        for c in chums:
            self.topLevelItem(group).addChild(c)
        self.verticalScrollBar().setSliderPosition(scrollPos)

    @QtCore.pyqtSlot()
    def activateChum(self):
        self.itemActivated.emit(self.currentItem(), 0)
    @QtCore.pyqtSlot()
    def removeChum(self, handle = None):
        if handle:
            if handle in self.chums:
                self.setCurrentItem(self.chums[handle])
        if not self.currentItem():
            return
        currentChum = self.currentItem().chum
        if currentChum.handle in self.chums:
            del self.chums[handle]
        self.removeChumSignal.emit(currentChum.handle)
        self.refreshList()
    @QtCore.pyqtSlot()
    def blockChum(self):
        currentChum = self.currentItem()
        if not currentChum:
            return
        self.blockChumSignal.emit(self.currentItem().chum.handle)
    @QtCore.pyqtSlot()
    def reportChum(self):
        currentChum = self.currentItem()
        if not currentChum:
            return
        self.mainwindow.reportChum(self.currentItem().chum.handle)
    @QtCore.pyqtSlot()
    def findAlts(self):
        currentChum = self.currentItem()
        if not currentChum:
            return
        self.mainwindow.sendMessage.emit("ALT %s" % (currentChum.chum.handle) , "calSprite")
    @QtCore.pyqtSlot()
    def openChumLogs(self):
        currentChum = self.currentItem()
        if not currentChum:
            return
        currentChum = currentChum.text(0)
        self.pesterlogviewer = PesterLogViewer(currentChum, self.mainwindow.config, self.mainwindow.theme, self.mainwindow)
        self.pesterlogviewer.rejected.connect(self.closeActiveLog)

        self.pesterlogviewer.show()
        self.pesterlogviewer.raise_()
        self.pesterlogviewer.activateWindow()
    @QtCore.pyqtSlot()
    def closeActiveLog(self):
        self.pesterlogviewer.close()
        self.pesterlogviewer = None
    @QtCore.pyqtSlot()
    def editNotes(self):
        currentChum = self.currentItem()
        if not currentChum:
            return
        (notes, ok) = QtWidgets.QInputDialog.getText(self, "Notes", "Enter your notes...")
        if ok:
            notes = str(notes)
            self.mainwindow.chumdb.setNotes(currentChum.handle, notes)
            currentChum.setToolTip(0, "%s: %s" % (currentChum.handle, notes))

    @QtCore.pyqtSlot()
    def renameGroup(self):
        if not hasattr(self, 'renamegroupdialog'):
            self.renamegroupdialog = None
        if not self.renamegroupdialog:
            self.renamegroupdialg = True
            (gname, ok) = QtWidgets.QInputDialog.getText(self, "Rename Group", "Enter a new name for the group:")
            if ok:
                if re.search("[^A-Za-z0-9_\s]", gname) is not None:
                    msgbox = QtWidgets.QMessageBox()
                    msgbox.setInformativeText("THIS IS NOT A VALID GROUP NAME")
                    msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    ret = msgbox.exec_()
                    self.renamegroupdialog = None
                    return
                currentGroup = self.currentItem()
                if not currentGroup:
                    self.renamegroupdialog = None
                    return
                text = currentGroup.data(0, QtCore.Qt.ToolTipRole)
                self.groups[gname] = currentGroup
                if text in self.groups:
                    del self.groups[text]
                if text in self.openGroups:
                    self.openGroups[gname] = self.openGroups[text]
                    del self.openGroups[text]
                for i in range(currentGroup.childCount()):
                    currentGroup.child(i).chum.group = gname
                    self.regroupChumSignal.emit(currentGroup.child(i).chum.handle, gname)
                currentGroup.setText(0, gname)
                currentGroup.setData(0, gname, QtCore.Qt.ToolTipRole)
                self.refreshList()
        self.renamegroupdialog = None
    @QtCore.pyqtSlot()
    def removeGroup(self):
        currentGroup = self.currentItem()
        if not currentGroup:
            return
        text = currentGroup.data(0, QtCore.Qt.ToolTipRole)
        if text in self.groups:
            del self.groups[text]
        if text in self.openGroups:
            del self.openGroups[text]
        for listing in self.chums:
            if listing.chum.group == text:
                listing.chum.group = "Friends"
        self.refreshList()

    def moveChumToGroup(self, handle, group):
        if handle not in self.chums:
            return
        chumLabel = self.chums[handle]
        chumLabel.chum.group = group
        self.regroupChumSignal.emit(chumLabel.chum.handle, group)
        self.refreshList()

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def moveToGroup(self, item):
        if not item:
            return
        group = item.text()
        chumLabel = self.currentItem()
        if not chumLabel:
            return
        self.moveChumToGroup(chumLabel.chum.handle, group)

    removeChumSignal = QtCore.pyqtSignal('QString')
    blockChumSignal = QtCore.pyqtSignal('QString')
    regroupChumSignal = QtCore.pyqtSignal(str, str)

class PesterWindow(MovingWindow):
    def __init__(self, options, parent=None, app=None):
        MovingWindow.__init__(self, parent,
                              (QtCore.Qt.CustomizeWindowHint |
                               QtCore.Qt.FramelessWindowHint))
        self.autoJoinDone = False
        self.app = app
        self.convos = CaseInsensitiveDict()
        self.memos = CaseInsensitiveDict()
        self.tabconvo = None
        self.tabmemo = None
        if "advanced" in options:
              self.advanced = options["advanced"]
        else: self.advanced = False
        if "server" in options:
            self.serverOverride = options["server"]
        if "port" in options:
            self.portOverride = options["port"]
        if "honk" in options:
              self.honk = options["honk"]
        else: self.honk = True

        self.setAutoFillBackground(True)
        self.setObjectName("main")
        self.config = userConfig(self)
        if self.config.defaultprofile():
            self.userprofile = userProfile(self.config.defaultprofile())
            self.theme = self.userprofile.theme
        else:
            self.userprofile = userProfile(PesterProfile("pesterClient%d" % (random.randint(100,999)), QtGui.QColor("black"), Mood(0)))
            self.theme = self.userprofile.theme
        self.modes = ""

        self.randhandler = RandomHandler(self)

        try:
            themeChecker(self.theme)
        except ThemeException as xxx_todo_changeme:
            (inst) = xxx_todo_changeme
            print("Caught: "+inst.parameter)
            themeWarning = QtWidgets.QMessageBox(self)
            themeWarning.setText("Theme Error: %s" % (inst))
            themeWarning.exec_()
            self.theme = pesterTheme("pesterchum")

        extraToasts = {'default': PesterToast}
        if pytwmn.confExists():
            extraToasts['twmn'] = pytwmn.Notification
        self.tm = PesterToastMachine(self, lambda: self.theme["main/windowtitle"], on=self.config.notify(),
                                     type=self.config.notifyType(), extras=extraToasts)
        self.tm.run()

        self.chatlog = PesterLog(self.profile().handle, self)

        self.move(100, 100)

        talk = QtWidgets.QAction(self.theme["main/menus/client/talk"], self, triggered=self.openChat)
        self.talk = talk
        logv = QtWidgets.QAction(self.theme["main/menus/client/logviewer"], self, triggered=self.openLogv)
        self.logv = logv
        grps = QtWidgets.QAction(self.theme["main/menus/client/addgroup"], self, triggered=self.addGroupWindow)
        self.grps = grps
        self.rand = QtWidgets.QAction(self.theme["main/menus/client/randen"], self, triggered=self.randhandler.getEncounter)
        opts = QtWidgets.QAction(self.theme["main/menus/client/options"], self, triggered=self.openOpts)
        self.opts = opts
        exitaction = QtWidgets.QAction(self.theme["main/menus/client/exit"], self, triggered=self.app.quit)
        self.exitaction = exitaction
        userlistaction = QtWidgets.QAction(self.theme["main/menus/client/userlist"], self, triggered=self.showAllUsers)
        self.userlistaction = userlistaction
        memoaction = QtWidgets.QAction(self.theme["main/menus/client/memos"], self, triggered=self.showMemos)
        self.memoaction = memoaction
        self.importaction = QtWidgets.QAction(self.theme["main/menus/client/import"], self, triggered=self.importExternalConfig)
        self.idleaction = QtWidgets.QAction(self.theme["main/menus/client/idle"], self)
        self.idleaction.setCheckable(True)
        self.idleaction.toggled.connect(self.toggleIdle)
        self.reconnectAction = QtWidgets.QAction(self.theme["main/menus/client/reconnect"], self, triggered=self.reconnectOSFC)

        self.menu = QtWidgets.QMenuBar(self)
        self.menu.setNativeMenuBar(False)

        filemenu = self.menu.addMenu(self.theme["main/menus/client/_name"])
        self.filemenu = filemenu
        filemenu.addAction(opts)
        filemenu.addAction(memoaction)
        filemenu.addAction(logv)
        filemenu.addAction(self.rand)
        if not self.randhandler.running:
            self.rand.setEnabled(False)
        filemenu.addAction(userlistaction)
        filemenu.addAction(talk)
        filemenu.addAction(self.idleaction)
        filemenu.addAction(grps)
        filemenu.addAction(self.importaction)
        filemenu.addAction(self.reconnectAction)
        filemenu.addAction(exitaction)

        changequirks = QtWidgets.QAction(self.theme["main/menus/profile/quirks"], self, triggered=self.openQuirks)
        self.changequirks = changequirks

        changecoloraction = QtWidgets.QAction(self.theme["main/menus/profile/color"], self, triggered=self.changeMyColor)
        self.changecoloraction = changecoloraction

        switch = QtWidgets.QAction(self.theme["main/menus/profile/switch"], self, triggered=self.switchProfile)
        self.switch = switch

        profilemenu = self.menu.addMenu(self.theme["main/menus/profile/_name"])
        self.profilemenu = profilemenu
        profilemenu.addAction(changequirks)
        # profilemenu.addAction(loadslum)
        profilemenu.addAction(changecoloraction)
        profilemenu.addAction(switch)

        self.helpAction = QtWidgets.QAction(self.theme["main/menus/help/help"], self, triggered=self.launchHelp)
        self.botAction = QtWidgets.QAction(self.theme["main/menus/help/calsprite"], self, triggered=self.loadCalsprite)
        self.nickServAction = QtWidgets.QAction(self.theme["main/menus/help/nickserv"], self, triggered=self.loadNickServ)
        self.chanServAction = QtWidgets.QAction(self.theme["main/menus/help/chanserv"], self, triggered=self.loadChanServ)
        self.aboutAction = QtWidgets.QAction(self.theme["main/menus/help/about"], self, triggered=self.aboutPesterchum)
        self.reportBugAction = QtWidgets.QAction("REPORT BUG", self, triggered=self.reportBug)
        helpmenu = self.menu.addMenu(self.theme["main/menus/help/_name"])
        self.helpmenu = helpmenu
        self.helpmenu.addAction(self.helpAction)
        self.helpmenu.addAction(self.botAction)
        self.helpmenu.addAction(self.chanServAction)
        self.helpmenu.addAction(self.nickServAction)
        self.helpmenu.addAction(self.aboutAction)
        self.helpmenu.addAction(self.reportBugAction)

        self.closeButton = WMButton(PesterIcon(self.theme["main/close/image"]), self)
        self.setButtonAction(self.closeButton, self.config.closeAction(), -1)
        self.miniButton = WMButton(PesterIcon(self.theme["main/minimize/image"]), self)
        self.setButtonAction(self.miniButton, self.config.minimizeAction(), -1)

        self.namesdb = CaseInsensitiveDict()
        self.onlineUsers = CaseInsensitiveDict()
        self.chumdb = PesterProfileDB()

        # from old Pesterchum
        # chums = [PesterProfile(c, chumdb=self.chumdb) for c in set(self.config.chums())]
        self.chumList = chumArea([], self)
        self.chumList.itemActivated.connect(self.pesterSelectedChum)
        self.chumList.removeChumSignal.connect(self.removeChum)
        self.chumList.blockChumSignal.connect(self.blockChum)

        self.addChumButton = QtWidgets.QPushButton(self.theme["main/addchum/text"], self, clicked=self.addChumWindow)
        self.pesterButton = QtWidgets.QPushButton(self.theme["main/pester/text"], self, clicked=self.pesterSelectedChum)
        self.blockButton = QtWidgets.QPushButton(self.theme["main/block/text"], self, clicked=self.blockSelectedChum)

        self.moodsLabel = QtWidgets.QLabel(self.theme["main/moodlabel/text"], self)

        self.mychumhandleLabel = QtWidgets.QLabel(self.theme["main/mychumhandle/label/text"], self)
        self.mychumhandle = QtWidgets.QPushButton(self.profile().handle, self, clicked=self.switchProfile)
        self.mychumhandle.setFlat(True)

        self.mychumcolor = QtWidgets.QPushButton(self, clicked=self.changeMyColor)

        self.initTheme(self.theme)

        self.waitingMessages = waitingMessageHolder(self)

        self.autoidle = False
        self.idlethreshold = 60*self.config.idleTime()
        self.idletimer = QtCore.QTimer(self, timeout=self.checkIdle)
        self.idleposition = QtGui.QCursor.pos()
        self.idletime = 0
        self.idletimer.start(1000)

        if not (self.config.username() and self.config.password()):
            self.username, self.password = self.getLogin(self.config.username())

        if not self.config.defaultprofile():
            self.changeProfile()

        # Fuck you some more OSX leopard! >:(
        if not ostools.isOSXLeopard():
            QtCore.QTimer.singleShot(1000, self.mspacheck)

        self.pcUpdate.connect(self.updateMsg)

        self.pingtimer = QtCore.QTimer(timeout=self.checkPing)
        self.lastping = int(time())
        self.pingtimer.start(1000*90)

    @QtCore.pyqtSlot()
    def mspacheck(self):
        # Fuck you EVEN more OSX leopard! >:((((
        if not ostools.isOSXLeopard():
            checker = MSPAChecker(self)

    @QtCore.pyqtSlot('QString', 'QString')
    def updateMsg(self, ver, url):
        if not hasattr(self, 'updatemenu'):
            self.updatemenu = None
        if not self.updatemenu:
            self.updatemenu = UpdatePesterchum(ver, url, self)
            self.updatemenu.accepted.connect(self.updatePC)
            self.updatemenu.rejected.connect(self.noUpdatePC)
            self.updatemenu.show()
            self.updatemenu.raise_()
            self.updatemenu.activateWindow()

    @QtCore.pyqtSlot()
    def updatePC(self):
        version.updateDownload(str(self.updatemenu.url))
        self.updatemenu = None
    @QtCore.pyqtSlot()
    def noUpdatePC(self):
        self.updatemenu = None

    @QtCore.pyqtSlot()
    def checkPing(self):
        curtime = int(time())
        if curtime - self.lastping > 600:
            self.pingServer.emit()

    def profile(self):
        return self.userprofile.chat
    def closeConversations(self, switch=False):
        if not hasattr(self, 'tabconvo'):
            self.tabconvo = None
        if self.tabconvo:
            self.tabconvo.close()
        else:
            for c in self.convos.values():
                c.close()
        if self.tabmemo:
            if not switch:
                self.tabmemo.close()
            else:
                for m in self.tabmemo.convos:
                    self.tabmemo.convos[m].sendtime()
        else:
            for m in self.memos.values():
                if not switch:
                    m.close()
                else:
                    m.sendtime()
    def paintEvent(self, event):
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(self.backgroundImage))
        self.setPalette(palette)

    @QtCore.pyqtSlot()
    def closeToTray(self):
        self.hide()
        self.closeToTraySignal.emit()
    def closeEvent(self, event):
        self.closeConversations()
        self.closeSignal.emit()
        event.accept()
    def newMessage(self, handle, msg):
        if handle in self.config.getBlocklist():
            #yeah suck on this
            self.sendMessage.emit("PESTERCHUM:BLOCKED", handle)
            return
        # notify
        if self.config.notifyOptions() & self.config.NEWMSG:
            if handle not in self.convos:
                t = self.tm.Toast("New Conversation", "From: %s" % handle)
                t.show()
            elif not self.config.notifyOptions() & self.config.NEWCONVO:
                if type(msg) not in (pesterBegin):
                    if handle.upper() not in BOTNAMES:
                        t = self.tm.Toast("From: %s" % handle, re.sub("</?c(=.*?)?>", "", msg))
                        t.show()
                else:
                    if msg == "PESTERCHUM:CEASE":
                        t = self.tm.Toast("Closed Conversation", handle)
                        t.show()
                    elif msg == "PESTERCHUM:BLOCK":
                        t = self.tm.Toast("Blocked", handle)
                        t.show()
                    elif msg == "PESTERCHUM:UNBLOCK":
                        t = self.tm.Toast("Unblocked", handle)
                        t.show()
        if handle not in self.convos:
            if msg == "PESTERCHUM:CEASE": # ignore cease after we hang up
                return
            matchingChum = self.chumList.chums.get(handle)
            if matchingChum:
                mood = matchingChum.mood
            else:
                mood = Mood(0)
            chum = PesterProfile(handle, mood=mood, chumdb=self.chumdb)
            self.newConversation(chum, False)
            if not matchingChum:
                self.moodRequest.emit(chum)
        convo = self.convos[handle]
        if type(msg) is pesterBegin:
            convo.beginConvo()
        else:
            convo.addMessage(msg, False)
        # play sound here
        if self.config.soundOn():
            if self.config.chatSound():
                if msg in ["PESTERCHUM:CEASE", "PESTERCHUM:BLOCK"]:
                    self.ceasesound.play()
                else:
                    self.alarm.play()
    def beginMessage(self, handle):
        self.newMessage(handle, pesterBegin())
    def newMemoMsg(self, chan, handle, msg):
        if chan not in self.memos:
            # silently ignore in case we forgot to /part
            return
        memo = self.memos[chan]
        msg = str(msg)
        if handle not in memo.times:
            # new chum! time current
            newtime = timedelta(0)
            time = TimeTracker(newtime)
            memo.times[handle] = time
        if msg[0:3] != "/me" and msg[0:13] != "PESTERCHUM:ME":
            msg = addTimeInitial(msg, memo.times[handle].getGrammar())
        if handle == "ChanServ":
            systemColor = QtGui.QColor(self.theme["memos/systemMsgColor"])
            msg = "<c=%s>%s</c>" % (systemColor.name(), msg)
        memo.addMessage(msg, handle)
        mentioned = False
        m = convertTags(msg, "text")
        if m.find(":") <= 3:
          m = m[m.find(":"):]
        for search in self.userprofile.mentions:
            if re.search(search, m):
                mentioned = True
                break
        if mentioned:
            if self.config.notifyOptions() & self.config.INITIALS:
                t = self.tm.Toast(chan, re.sub("</?c(=.*?)?>", "", msg))
                t.show()

        if self.config.soundOn():
            if self.config.memoSound():
                if self.config.nameSound():
                    if mentioned:
                        self.namesound.play()
                        return
                if self.honk and re.search(r"\bhonk\b", convertTags(msg, "text"), re.I):
                    self.honksound.play()
                elif self.config.memoPing():
                    self.memosound.play()

    def changeColor(self, handle, color):
        # pesterconvo and chumlist
        self.chumList.updateColor(handle, color)
        if handle in self.convos:
            self.convos[handle].updateColor(color)
        self.chumdb.setColor(handle, color)

    def updateMood(self, handle, mood):
        # updates OTHER chums' moods
        oldmood = self.chumList.updateMood(handle, mood)
        if handle in self.convos:
            self.convos[handle].updateMood(mood, old=oldmood)
    def newConversation(self, chum, initiated=True):
        if type(chum) in [str, str]:
            matchingChum = self.chumList.chums.get(chum)
            if matchingChum:
                mood = matchingChum.mood
            else:
                mood = Mood(2)
            chum = PesterProfile(chum, mood=mood, chumdb=self.chumdb)
            if not matchingChum:
                self.moodRequest.emit(chum)

        if chum.handle in self.convos:
            self.convos[chum.handle].showChat()
            return
        if self.config.tabs():
            if not self.tabconvo:
                self.createTabWindow()
            convoWindow = PesterConvo(chum, initiated, self, self.tabconvo)
            self.tabconvo.show()
        else:
            convoWindow = PesterConvo(chum, initiated, self)
        convoWindow.messageSent.connect(self.sendMessage)
        convoWindow.windowClosed.connect(self.closeConvo)
        self.convos[chum.handle] = convoWindow
        if str(chum.handle).upper() in BOTNAMES:
            convoWindow.toggleQuirks(True)
            convoWindow.quirksOff.setChecked(True)
            if str(chum.handle).upper() in CUSTOMBOTS:
                self.newConvoStarted.emit(chum.handle, initiated)
        else:
            self.newConvoStarted.emit(chum.handle, initiated)
        convoWindow.show()

    def createTabWindow(self):
        self.tabconvo = PesterTabWindow(self)
        self.tabconvo.windowClosed.connect(self.tabsClosed)
    def createMemoTabWindow(self):
        self.tabmemo = MemoTabWindow(self)
        self.tabmemo.windowClosed.connect(self.memoTabsClosed)

    def newMemo(self, channel, timestr, secret=False, invite=False):
        if channel == "#pesterchum":
            return
        if channel in self.memos:
            self.memos[channel].showChat()
            return
        # do slider dialog then set
        if self.config.tabMemos():
            if not self.tabmemo:
                self.createMemoTabWindow()
            memoWindow = PesterMemo(channel, timestr, self, self.tabmemo)
            self.tabmemo.show()
        else:
            memoWindow = PesterMemo(channel, timestr, self, None)
        # connect signals
        self.inviteOnlyChan.connect(memoWindow.closeInviteOnly)
        self.namesUpdated.connect(memoWindow.namesUpdated)
        self.modesUpdated.connect(memoWindow.modesUpdated)
        self.userPresentSignal.connect(memoWindow.userPresentChange)
        self.userRankSignal.connect(memoWindow.userRankChange)
        memoWindow.messageSent.connect(self.sendChannel)
        memoWindow.windowClosed.connect(self.closeMemo)

        # chat client send memo open
        self.memos[channel] = memoWindow
        self.joinChannel.emit(channel) # race condition?
        self.secret = secret
        if self.secret:
            self.secret = True
            self.setChannelMode.emit(channel, "+s", "")
        if invite:
            self.setChannelMode.emit(channel, "+i", "")
        # memoWindow.sendTimeInfo()
        # sorry time travellers :(
        memoWindow.show()

    def addChum(self, chum):
        self.chumList.addChum(chum)
        self.moodRequest.emit(chum)
        self.friendRequest.emit(chum)

    def addGroup(self, gname):
        self.chumList.addGroup(gname)

    def changeProfile(self, collision=None):
        if not hasattr(self, 'chooseprofile'):
            self.chooseprofile = None
        if not self.chooseprofile:
            self.chooseprofile = PesterChooseProfile(self.userprofile, self.config, self.theme, self, collision=collision)
            self.chooseprofile.exec_()

    def getLogin(self, username=None):
        self.loginscreen = LoginScreen(self)
        if username:
            self.loginscreen.username.setText(username)
        status = self.loginscreen.exec_()
        if status == QtWidgets.QDialog.Rejected:
            sys.exit(0)
        else:
            return (self.loginscreen.username.text(), self.loginscreen.password.text()) if not self.loginscreen.anonymous.isChecked() else \
                (None, None)

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
        self.setStyleSheet("QFrame#main { %s }" % (theme["main/style"]))
        self.backgroundImage = QtGui.QPixmap(theme["main/background-image"])
        self.backgroundMask = self.backgroundImage.mask()
        self.setMask(self.backgroundMask)
        self.menu.setStyleSheet("QMenuBar { background: transparent; %s } QMenuBar::item { background: transparent; %s } " % (theme["main/menubar/style"], theme["main/menu/menuitem"]) + "QMenu { background: transparent; %s } QMenu::item::selected { %s } QMenu::item::disabled { %s }" % (theme["main/menu/style"], theme["main/menu/selected"], theme["main/menu/disabled"]))
        newcloseicon = PesterIcon(theme["main/close/image"])
        self.closeButton.setIcon(newcloseicon)
        self.closeButton.setIconSize(newcloseicon.realsize())
        self.closeButton.resize(newcloseicon.realsize())
        self.closeButton.move(*theme["main/close/loc"])
        newminiicon = PesterIcon(theme["main/minimize/image"])
        self.miniButton.setIcon(newminiicon)
        self.miniButton.setIconSize(newminiicon.realsize())
        self.miniButton.resize(newminiicon.realsize())
        self.miniButton.move(*theme["main/minimize/loc"])
        # menus
        self.menu.move(*theme["main/menu/loc"])
        self.talk.setText(theme["main/menus/client/talk"])
        self.logv.setText(theme["main/menus/client/logviewer"])
        self.grps.setText(theme["main/menus/client/addgroup"])
        self.rand.setText(self.theme["main/menus/client/randen"])
        self.opts.setText(theme["main/menus/client/options"])
        self.exitaction.setText(theme["main/menus/client/exit"])
        self.userlistaction.setText(theme["main/menus/client/userlist"])
        self.memoaction.setText(theme["main/menus/client/memos"])
        self.importaction.setText(theme["main/menus/client/import"])
        self.idleaction.setText(theme["main/menus/client/idle"])
        self.reconnectAction.setText(theme["main/menus/client/reconnect"])
        self.filemenu.setTitle(theme["main/menus/client/_name"])
        self.changequirks.setText(theme["main/menus/profile/quirks"])
        # self.loadslum.setText(theme["main/menus/profile/block"])
        self.changecoloraction.setText(theme["main/menus/profile/color"])
        self.switch.setText(theme["main/menus/profile/switch"])
        self.profilemenu.setTitle(theme["main/menus/profile/_name"])
        self.aboutAction.setText(self.theme["main/menus/help/about"])
        self.helpAction.setText(self.theme["main/menus/help/help"])
        self.botAction.setText(self.theme["main/menus/help/calsprite"])
        self.chanServAction.setText(self.theme["main/menus/help/chanserv"])
        self.nickServAction.setText(self.theme["main/menus/help/nickserv"])
        self.helpmenu.setTitle(self.theme["main/menus/help/_name"])

        # moods
        self.moodsLabel.setText(theme["main/moodlabel/text"])
        self.moodsLabel.move(*theme["main/moodlabel/loc"])
        self.moodsLabel.setStyleSheet(theme["main/moodlabel/style"])

        if hasattr(self, 'moods'):
            self.moods.removeButtons()
        mood_list = theme["main/moods"]
        mood_list = [dict([(str(k),v) for (k,v) in d.items()])
                     for d in mood_list]
        self.moods = PesterMoodHandler(self, *[PesterMoodButton(self, **d) for d in mood_list])
        self.moods.showButtons()
        # chum
        addChumStyle = "QPushButton { %s }" % (theme["main/addchum/style"])
        if "main/addchum/pressed" in theme:
            addChumStyle += "QPushButton:pressed { %s }" % (theme["main/addchum/pressed"])
        pesterButtonStyle = "QPushButton { %s }" % (theme["main/pester/style"])
        if "main/pester/pressed" in theme:
            pesterButtonStyle += "QPushButton:pressed { %s }" % (theme["main/pester/pressed"])
        blockButtonStyle = "QPushButton { %s }" % (theme["main/block/style"])
        if "main/block/pressed" in theme:
            pesterButtonStyle += "QPushButton:pressed { %s }" % (theme["main/block/pressed"])
        self.addChumButton.setText(theme["main/addchum/text"])
        self.addChumButton.resize(*theme["main/addchum/size"])
        self.addChumButton.move(*theme["main/addchum/loc"])
        self.addChumButton.setStyleSheet(addChumStyle)
        self.pesterButton.setText(theme["main/pester/text"])
        self.pesterButton.resize(*theme["main/pester/size"])
        self.pesterButton.move(*theme["main/pester/loc"])
        self.pesterButton.setStyleSheet(pesterButtonStyle)
        self.blockButton.setText(theme["main/block/text"])
        self.blockButton.resize(*theme["main/block/size"])
        self.blockButton.move(*theme["main/block/loc"])
        self.blockButton.setStyleSheet(blockButtonStyle)
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
        if "main/mychumhandle/currentMood" in self.theme:
            moodicon = self.profile().mood.icon(theme)
            if hasattr(self, 'currentMoodIcon') and self.currentMoodIcon:
                self.currentMoodIcon.hide()
                self.currentMoodIcon = None
            self.currentMoodIcon = QtWidgets.QLabel(self)
            self.currentMoodIcon.setPixmap(moodicon.pixmap(moodicon.realsize()))
            self.currentMoodIcon.move(*theme["main/mychumhandle/currentMood"])
            self.currentMoodIcon.show()
        else:
            if hasattr(self, 'currentMoodIcon') and self.currentMoodIcon:
                self.currentMoodIcon.hide()
            self.currentMoodIcon = None


        if theme["main/mychumhandle/colorswatch/text"]:
            self.mychumcolor.setText(theme["main/mychumhandle/colorswatch/text"])
        else:
            self.mychumcolor.setText("")

        # sounds
        try:
            self.alarm, self.memosound, self.namesound, self.ceasesound, self.honksound = \
                [QtMultimedia.QSoundEffect() for i in range(5)]
            self.alarm.setSource(QtCore.QUrl.fromLocalFile(theme["main/sounds/alertsound"]))
            self.memosound.setSource(QtCore.QUrl.fromLocalFile(theme["main/sounds/memosound"]))
            self.namesound.setSource(QtCore.QUrl.fromLocalFile("themes/namealarm.wav"))
            self.ceasesound.setSource(QtCore.QUrl.fromLocalFile(theme["main/sounds/ceasesound"]))
            self.honksound.setSource(QtCore.QUrl.fromLocalFile("themes/honk.wav"))
        except Exception as e:
            self.alarm = NoneSound()
            self.memosound = NoneSound()
            self.namesound = NoneSound()
            self.ceasesound = NoneSound()
            self.honksound = NoneSound()
        self.setVolume(self.config.volume())

    def setVolume(self, vol):
        vol = vol/100.0
        self.alarm.setVolume(vol)
        self.memosound.setVolume(vol)
        self.namesound.setVolume(vol)
        self.ceasesound.setVolume(vol)
        self.honksound.setVolume(vol)

    def changeTheme(self, theme):
        # check theme
        try:
            themeChecker(theme)
        except ThemeException as xxx_todo_changeme1:
            (inst) = xxx_todo_changeme1
            themeWarning = QtWidgets.QMessageBox(self)
            themeWarning.setText("Theme Error: %s" % (inst))
            themeWarning.exec_()
            theme = pesterTheme("pesterchum")
            return
        self.theme = theme
        # do self
        self.initTheme(theme)
        # set mood
        self.moods.updateMood(theme['main/defaultmood'])
        # chum area
        self.chumList.changeTheme(theme)
        # do open windows
        if self.tabconvo:
            self.tabconvo.changeTheme(theme)
        if self.tabmemo:
            self.tabmemo.changeTheme(theme)
        for c in self.convos.values():
            c.changeTheme(theme)
        for m in self.memos.values():
            m.changeTheme(theme)
        if hasattr(self, 'allusers') and self.allusers:
            self.allusers.changeTheme(theme)
        if self.config.ghostchum():
            self.theme["main"]["icon"] = "themes/pesterchum/pesterdunk.png"
            self.theme["main"]["newmsgicon"] = "themes/pesterchum/ghostchum.png"
            self.setWindowIcon(PesterIcon(self.theme["main/icon"]))
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
            elif self.isHidden():
                self.show()
            else:
                if self.isActiveWindow():
                    self.closeToTray()
                else:
                    self.raise_()
                    self.activateWindow()
        else:
            self.waitingMessages.answerMessage()

    def doAutoIdentify(self):
        # TODO
        pass
        # if self.userprofile.getAutoIdentify():
        #     self.sendMessage.emit("identify " + self.userprofile.getNickServPass(), "NickServ")

    def doAutoJoins(self):
        # TODO
        pass
        # if not self.autoJoinDone:
        #     self.autoJoinDone = True
        #     for memo in self.userprofile.getAutoJoins():
        #         self.newMemo(memo, "i")

    @QtCore.pyqtSlot()
    def connected(self):
        if self.loadingscreen:
            self.loadingscreen.done(QtWidgets.QDialog.Accepted)
        self.loadingscreen = None

        self.doAutoIdentify()
        self.doAutoJoins()

    @QtCore.pyqtSlot()
    def loginFailed(self):
        self.username, self.password = self.getLogin(self.config.username())
        self.registerOSFC.emit()

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
            text = curChum.data(0, QtCore.Qt.ToolTipRole) # might be group
            if text not in self.chumList.groups and \
               text != "Friends":
                self.newConversationWindow(curChum)
    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def newConversationWindow(self, chumlisting):
        # check chumdb
        chum = chumlisting.chum
        color = self.chumdb.getColor(chum)
        if color:
            chum.color = color
        self.newConversation(chum)
    @QtCore.pyqtSlot('QString')
    def closeConvo(self, handle):
        h = str(handle)
        try:
            chum = self.convos[h].chum
        except KeyError:
            chum = self.convos[h.lower()].chum
        try:
            chumopen = self.convos[h].chumopen
        except KeyError:
            chumopen = self.convos[h.lower()].chumopen
        if chumopen:
            self.chatlog.log(chum.handle, self.profile().pestermsg(chum, QtGui.QColor(self.theme["convo/systemMsgColor"]), self.theme["convo/text/ceasepester"]))
            self.convoClosed.emit(handle)
        self.chatlog.finish(h)
        del self.convos[h]
    @QtCore.pyqtSlot('QString')
    def closeMemo(self, channel):
        c = str(channel)
        self.chatlog.finish(c)
        self.leftChannel.emit(channel)
        try:
            del self.memos[c]
        except KeyError:
            del self.memos[c.lower()]
    @QtCore.pyqtSlot()
    def tabsClosed(self):
        del self.tabconvo
        self.tabconvo = None
    @QtCore.pyqtSlot()
    def memoTabsClosed(self):
        del self.tabmemo
        self.tabmemo = None

    @QtCore.pyqtSlot('QString', Mood)
    def updateMoodSlot(self, handle, mood):
        self.updateMood(handle, mood)

    @QtCore.pyqtSlot('QString', QtGui.QColor)
    def updateColorSlot(self, handle, color):
        self.changeColor(handle, color)

    @QtCore.pyqtSlot('QString', 'QString')
    def deliverMessage(self, handle, msg):
        self.newMessage(handle, msg)
    @QtCore.pyqtSlot('QString', 'QString', 'QString')
    def deliverMemo(self, chan, handle, msg):
        (c, h, m) = (str(chan), str(handle), str(msg))
        self.newMemoMsg(c,h,m)
    @QtCore.pyqtSlot(str)
    def deliverBegin(self, handle):
        self.beginMessage(handle)
    @QtCore.pyqtSlot('QString', 'QString')
    def deliverNotice(self, handle, msg):
        h = str(handle)
        m = str(msg)
        if m.startswith("Your nickname is now being changed to"):
            changedto = m[39:-1]
            msgbox = QtWidgets.QMessageBox()
            msgbox.setText("This chumhandle has been registered; you may not use it.")
            msgbox.setInformativeText("Your handle is now being changed to %s." % (changedto))
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            ret = msgbox.exec_()
        elif h == self.randhandler.randNick:
            self.randhandler.incoming(msg)
        elif h in self.convos:
            self.newMessage(h, m)
        elif h.upper() == "NICKSERV" and "PESTERCHUM:" not in m:
            m = nickservmsgs.translate(m)
            if m:
                t = self.tm.Toast("NickServ:", m)
                t.show()
    @QtCore.pyqtSlot('QString', 'QString')
    def deliverInvite(self, handle, channel):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText("You're invited!")
        msgbox.setInformativeText("%s has invited you to the memo: %s\nWould you like to join them?" % (handle, channel))
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        ret = msgbox.exec_()
        if ret == QtWidgets.QMessageBox.Ok:
            self.newMemo(str(channel), "+0:00")
    @QtCore.pyqtSlot('QString')
    def chanInviteOnly(self, channel):
        self.inviteOnlyChan.emit(channel)
    @QtCore.pyqtSlot('QString', 'QString')
    def cannotSendToChan(self, channel, msg):
        self.deliverMemo(channel, "ChanServ", msg)
    @QtCore.pyqtSlot('QString', 'QString')
    def modesUpdated(self, channel, modes):
        self.modesUpdated.emit(channel, modes)
    @QtCore.pyqtSlot('QString', 'QString', 'QString')
    def timeCommand(self, chan, handle, command):
        (c, h, cmd) = (str(chan), str(handle), str(command))
        if self.memos[c]:
            self.memos[c].timeUpdate(h, cmd)

    @QtCore.pyqtSlot('QString', 'QString', 'QString')
    def quirkDisable(self, channel, msg, op):
        (c, msg, op) = (str(channel), str(msg), str(op))
        if c not in self.memos:
            return
        memo = self.memos[c]
        memo.quirkDisable(op, msg)

    @QtCore.pyqtSlot('QString', PesterList)
    def updateNames(self, channel, names):
        c = str(channel)
        # update name DB
        self.namesdb[c] = names
        # warn interested party of names
        self.namesUpdated.emit(c)
    @QtCore.pyqtSlot(PesterList)
    def updateOnlineUsers(self, names):
        self.onlineUsers = CaseInsensitiveDict()
        for n in names:
            self.onlineUsers[n] = True
        self.onlineUsersUpdated.emit()
    @QtCore.pyqtSlot('QString', 'QString', 'QString')
    def userPresentUpdate(self, handle, channel, update):
        c = str(channel)
        n = str(handle)
        if update == "nick":
            l = n.split(":")
            oldnick = l[0]
            newnick = l[1]
        if update == "left":
            try:
                i = self.namesdb[c].index(n)
                self.namesdb[c].pop(i)
            except ValueError:
                pass
            except KeyError:
                self.namesdb[c] = []
        elif update == "nick":
            for c in list(self.namesdb.keys()):
                try:
                    i = self.namesdb[c].index(oldnick)
                    self.namesdb[c].pop(i)
                    self.namesdb[c].append(newnick)
                except ValueError:
                    pass
                except KeyError:
                    pass
        elif update == "join":
            try:
                i = self.namesdb[c].index(n)
            except ValueError:
                self.namesdb[c].append(n)
            except KeyError:
                self.namesdb[c] = [n]

        self.userPresentSignal.emit(handle, channel, update)

    @QtCore.pyqtSlot('QString', 'QString', int, 'QString')
    def userRankUpdate(self, handle, channel, rank, actingHandle):
        self.userRankSignal.emit(handle, channel, rank, actingHandle)

    @QtCore.pyqtSlot()
    def addChumWindow(self):
        if not hasattr(self, 'addchumdialog'):
            self.addchumdialog = None
        if not self.addchumdialog:
            available_groups = self.chumList.groups
            self.addchumdialog = AddChumDialog(list(available_groups.keys()), self)
            ok = self.addchumdialog.exec_()
            handle = str(self.addchumdialog.chumBox.text()).strip()
            newgroup = str(self.addchumdialog.newgroup.text()).strip()
            selectedGroup = self.addchumdialog.groupBox.currentText()
            group = newgroup if newgroup else selectedGroup
            if ok:
                handle = str(handle)
                if handle in self.chumList.chums:
                    self.addchumdialog = None
                    return
                if not (PesterProfile.checkLength(handle) and
                        PesterProfile.checkValid(handle)[0]):
                    errormsg = QtWidgets.QErrorMessage(self)
                    errormsg.showMessage("THIS IS NOT A VALID CHUMTAG!")
                    self.addchumdialog = None
                    return
                if re.search("[^A-Za-z0-9_\s]", group) is not None:
                    errormsg = QtWidgets.QErrorMessage(self)
                    errormsg.showMessage("THIS IS NOT A VALID GROUP NAME")
                    self.addchumdialog = None
                    return
                if newgroup:
                    # make new group
                    self.addGroup(group)
                chum = PesterProfile(handle, chumdb=self.chumdb, group=group)
                # send friend command?
                self.addChum(chum)
            self.addchumdialog = None
    @QtCore.pyqtSlot('QString')
    def removeChum(self, chumlisting):
        self.config.removeChum(chumlisting)
    def reportChum(self, handle):
        (reason, ok) = QtWidgets.QInputDialog.getText(self, "Report User", "Enter the reason you are reporting this user (optional):")
        if ok:
            self.sendMessage.emit("REPORT %s %s" % (handle, reason) , "calSprite")

    @QtCore.pyqtSlot('QString')
    def blockChum(self, handle):
        # TODO: IMPLEMENT
        logging.info("---> BLOCKCHUM NOT IMPLEMENTED YET <---")
        return
        h = str(handle)
        self.config.addBlocklist(h)
        self.config.removeChum(h)
        if h in self.convos:
            convo = self.convos[h]
            msg = self.profile().pestermsg(convo.chum, QtGui.QColor(self.theme["convo/systemMsgColor"]), self.theme["convo/text/blocked"])
            convo.textArea.append(convertTags(msg))
            self.chatlog.log(convo.chum.handle, msg)
            convo.updateBlocked()
        self.chumList.removeChum(h)
        self.blockedChum.emit(handle)

    @QtCore.pyqtSlot('QString')
    def unblockChum(self, handle):
        # TODO: IMPLEMENT
        logging.info("---> UNBLOCKCHUM NOT IMPLEMENTED YET <---")
        return
        h = str(handle)
        self.config.delBlocklist(h)
        if h in self.convos:
            convo = self.convos[h]
            msg = self.profile().pestermsg(convo.chum, QtGui.QColor(self.theme["convo/systemMsgColor"]), self.theme["convo/text/unblocked"])
            convo.textArea.append(convertTags(msg))
            self.chatlog.log(convo.chum.handle, msg)
            convo.updateMood(convo.chum.mood, unblocked=True)
        chum = PesterProfile(h, chumdb=self.chumdb)
        self.chumList.addChum(chum)
        self.moodRequest.emit(chum)
        self.unblockedChum.emit(handle)

    @QtCore.pyqtSlot(bool)
    def toggleIdle(self, idle):
        if idle:
            self.setAway.emit(True)
            self.randhandler.setIdle(True)
            sysColor = QtGui.QColor(self.theme["convo/systemMsgColor"])
            verb = self.theme["convo/text/idle"]
            for (h, convo) in self.convos.items():
                if convo.chumopen:
                    msg = self.profile().idlemsg(sysColor, verb)
                    convo.textArea.append(convertTags(msg))
                    self.chatlog.log(h, msg)
                    self.sendMessage.emit("PESTERCHUM:IDLE", h)
        else:
            self.setAway.emit(False)
            self.randhandler.setIdle(False)
            self.idletime = 0
    @QtCore.pyqtSlot()
    def checkIdle(self):
        newpos = QtGui.QCursor.pos()
        if newpos == self.idleposition:
            self.idletime += 1
        else:
            self.idletime = 0
        if self.idletime >= self.idlethreshold:
            if not self.idleaction.isChecked():
                self.idleaction.toggle()
            self.autoidle = True
        else:
            if self.autoidle:
                if self.idleaction.isChecked():
                    self.idleaction.toggle()
                self.autoidle = False
        self.idleposition = newpos
    @QtCore.pyqtSlot()
    def importExternalConfig(self):
        f = QtWidgets.QFileDialog.getOpenFileName(self)
        if f == "":
            return
        fp = open(f, 'r')
        regexp_state = None
        for l in fp:
            # import chumlist
            l = l.rstrip()
            chum_mo = re.match("handle: ([A-Za-z0-9]+)", l)
            if chum_mo is not None:
                chum = PesterProfile(chum_mo.group(1))
                self.addChum(chum)
                continue
            if regexp_state is not None:
                replace_mo = re.match("replace: (.+)", l)
                if replace_mo is not None:
                    replace = replace_mo.group(1)
                    try:
                        re.compile(regexp_state)
                    except re.error as e:
                        continue
                    newquirk = pesterQuirk({"type": "regexp",
                                            "from": regexp_state,
                                            "to": replace})
                    qs = self.userprofile.quirks
                    qs.addQuirk(newquirk)
                    self.userprofile.quirks = qs
                regexp_state = None
                continue
            search_mo = re.match("search: (.+)", l)
            if search_mo is not None:
                regexp_state = search_mo.group(1)
                continue
            other_mo = re.match("(prefix|suffix): (.+)", l)
            if other_mo is not None:
                newquirk = pesterQuirk({"type": other_mo.group(1),
                                        "value": other_mo.group(2)})
                qs = self.userprofile.quirks
                qs.addQuirk(newquirk)
                self.userprofile.quirks = qs

    @QtCore.pyqtSlot()
    def showMemos(self, channel=""):
        if not hasattr(self, 'memochooser'):
            self.memochooser = None
        if self.memochooser:
            return
        self.memochooser = PesterMemoList(self, channel)
        self.memochooser.accepted.connect(self.joinSelectedMemo)
        self.memochooser.rejected.connect(self.memoChooserClose)
        self.requestChannelList.emit()
        self.memochooser.show()
    @QtCore.pyqtSlot()
    def joinSelectedMemo(self):

        time = str(self.memochooser.timeinput.text())
        secret = self.memochooser.secretChannel.isChecked()
        invite = self.memochooser.inviteChannel.isChecked()

        if self.memochooser.newmemoname():
            newmemo = self.memochooser.newmemoname()
            channel = str(newmemo).replace(" ", "_")
            channel = re.sub(r"[^A-Za-z0-9#_]", "", channel)
            self.newMemo(channel, time, secret=secret, invite=invite)

        for SelectedMemo in self.memochooser.SelectedMemos():
            channel = str(SelectedMemo.target)
            self.newMemo(channel, time)

        self.memochooser = None
    @QtCore.pyqtSlot()
    def memoChooserClose(self):
        self.memochooser = None

    @QtCore.pyqtSlot(PesterList)
    def updateChannelList(self, channels):
        if hasattr(self, 'memochooser') and self.memochooser:
            self.memochooser.updateChannels(channels)

    @QtCore.pyqtSlot(PesterDict)
    def updateFriendList(self, friends):
        for groupname, fs in friends.items():
            self.addGroup(groupname)
            for fname in fs:
                chum = PesterProfile(fname, chumdb=self.chumdb, group=groupname)
                self.chumList.addChum(chum)

    @QtCore.pyqtSlot()
    def showAllUsers(self):
        if not hasattr(self, 'allusers'):
            self.allusers = None
        if not self.allusers:
            self.allusers = PesterUserlist(self.config, self.theme, self)
            self.allusers.accepted.connect(self.userListClose)
            self.allusers.rejected.connect(self.userListClose)
            self.allusers.addChum.connect(self.userListAdd)
            self.allusers.pesterChum.connect(self.userListPester)
            self.requestUserList.emit('')
            self.allusers.show()

    @QtCore.pyqtSlot('QString')
    def userListAdd(self, handle):
        h = str(handle)
        chum = PesterProfile(h, chumdb=self.chumdb)
        self.addChum(chum)
    @QtCore.pyqtSlot('QString')
    def userListPester(self, handle):
        h = str(handle)
        self.newConversation(h)
    @QtCore.pyqtSlot()
    def userListClose(self):
        self.allusers = None

    @QtCore.pyqtSlot()
    def openQuirks(self):
        if not hasattr(self, 'quirkmenu'):
            self.quirkmenu = None
        if not self.quirkmenu:
            self.quirkmenu = PesterChooseQuirks(self.config, self.theme, self)
            self.quirkmenu.accepted.connect(self.updateQuirks)
            self.quirkmenu.rejected.connect(self.closeQuirks)
            self.quirkmenu.show()
            self.quirkmenu.raise_()
            self.quirkmenu.activateWindow()
    @QtCore.pyqtSlot()
    def updateQuirks(self):
        for i in range(self.quirkmenu.quirkList.topLevelItemCount()):
            curgroup = str(self.quirkmenu.quirkList.topLevelItem(i).text(0))
            for j in range(self.quirkmenu.quirkList.topLevelItem(i).childCount()):
                item = self.quirkmenu.quirkList.topLevelItem(i).child(j)
                item.quirk.quirk["on"] = item.quirk.on = (item.checkState(0) == QtCore.Qt.Checked)
                item.quirk.quirk["group"] = item.quirk.group = curgroup
        quirks = pesterQuirks(self.quirkmenu.quirks())
        self.userprofile.quirks = quirks
        if hasattr(self.quirkmenu, 'quirktester') and self.quirkmenu.quirktester:
            self.quirkmenu.quirktester.close()
        self.quirkmenu = None
    @QtCore.pyqtSlot()
    def closeQuirks(self):
        if hasattr(self.quirkmenu, 'quirktester') and self.quirkmenu.quirktester:
            self.quirkmenu.quirktester.close()
        self.quirkmenu = None
    @QtCore.pyqtSlot()
    def openChat(self):
        if not hasattr(self, "openchatdialog"):
            self.openchatdialog = None
        if not self.openchatdialog:
            (chum, ok) = QtWidgets.QInputDialog.getText(self, "Pester Chum", "Enter a handle to pester:")
            try:
                if ok:
                    self.newConversation(str(chum))
            except:
                pass
            finally:
                self.openchatdialog = None
    @QtCore.pyqtSlot()
    def openLogv(self):
        if not hasattr(self, 'logusermenu'):
            self.logusermenu = None
        if not self.logusermenu:
            self.logusermenu = PesterLogUserSelect(self.config, self.theme, self)
            self.logusermenu.accepted.connect(self.closeLogUsers)
            self.logusermenu.rejected.connect(self.closeLogUsers)
            self.logusermenu.show()
            self.logusermenu.raise_()
            self.logusermenu.activateWindow()
    @QtCore.pyqtSlot()
    def closeLogUsers(self):
        self.logusermenu.close()
        self.logusermenu = None

    @QtCore.pyqtSlot()
    def addGroupWindow(self):
        if not hasattr(self, 'addgroupdialog'):
            self.addgroupdialog = None
        if not self.addgroupdialog:
            (gname, ok) = QtWidgets.QInputDialog.getText(self, "Add Group", "Enter a name for the new group:")
            if ok:
                gname = str(gname)
                if re.search("[^A-Za-z0-9_\s]", gname) is not None:
                    msgbox = QtWidgets.QMessageBox()
                    msgbox.setInformativeText("THIS IS NOT A VALID GROUP NAME")
                    msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    ret = msgbox.exec_()
                    self.addgroupdialog = None
                    return
                self.addGroup(gname)
            self.addgroupdialog = None

    @QtCore.pyqtSlot()
    def openOpts(self):
        if not hasattr(self, 'optionmenu'):
            self.optionmenu = None
        if not self.optionmenu:
            self.optionmenu = PesterOptions(self.config, self.theme, self)
            self.optionmenu.accepted.connect(self.updateOptions)
            self.optionmenu.rejected.connect(self.closeOptions)
            self.optionmenu.show()
            self.optionmenu.raise_()
            self.optionmenu.activateWindow()
    @QtCore.pyqtSlot()
    def closeOptions(self):
        self.optionmenu.close()
        self.optionmenu = None
    @QtCore.pyqtSlot()
    def updateOptions(self):
        try:
            # tabs
            curtab = self.config.tabs()
            tabsetting = self.optionmenu.tabcheck.isChecked()
            if curtab and not tabsetting:
                # split tabs into windows
                windows = []
                if self.tabconvo:
                    windows = list(self.tabconvo.convos.values())

                for w in windows:
                    w.setParent(None)
                    w.show()
                    w.raiseChat()
                if self.tabconvo:
                    self.tabconvo.closeSoft()
                # save options
                self.config.set("tabs", tabsetting)
            elif tabsetting and not curtab:
                # combine
                self.createTabWindow()
                newconvos = {}
                for (h,c) in self.convos.items():
                    c.setParent(self.tabconvo)
                    self.tabconvo.addChat(c)
                    self.tabconvo.show()
                    newconvos[h] = c
                self.convos = newconvos
                # save options
                self.config.set("tabs", tabsetting)

            # tabs memos
            curtabmemo = self.config.tabMemos()
            tabmemosetting = self.optionmenu.tabmemocheck.isChecked()
            if curtabmemo and not tabmemosetting:
                # split tabs into windows
                windows = []
                if self.tabmemo:
                    windows = list(self.tabmemo.convos.values())

                for w in windows:
                    w.setParent(None)
                    w.show()
                    w.raiseChat()
                if self.tabmemo:
                    self.tabmemo.closeSoft()
                # save options
                self.config.set("tabmemos", tabmemosetting)
            elif tabmemosetting and not curtabmemo:
                # combine
                newmemos = {}
                self.createMemoTabWindow()
                for (h,m) in self.memos.items():
                    m.setParent(self.tabmemo)
                    self.tabmemo.addChat(m)
                    self.tabmemo.show()
                    newmemos[h] = m
                self.memos = newmemos
                # save options
                self.config.set("tabmemos", tabmemosetting)
            # hidden chums
            chumsetting = self.optionmenu.hideOffline.isChecked()
            self.config.set("hideOfflineChums", chumsetting)
            # sorting method
            sortsetting = self.optionmenu.sortBox.currentIndex()
            self.config.set("sortMethod", sortsetting)
            # sound
            soundsetting = self.optionmenu.soundcheck.isChecked()
            self.config.set("soundon", soundsetting)
            chatsoundsetting = self.optionmenu.chatsoundcheck.isChecked()
            curchatsound = self.config.chatSound()
            if chatsoundsetting != curchatsound:
                self.config.set('chatSound', chatsoundsetting)
            memosoundsetting = self.optionmenu.memosoundcheck.isChecked()
            curmemosound = self.config.memoSound()
            if memosoundsetting != curmemosound:
                self.config.set('memoSound', memosoundsetting)
            memopingsetting = self.optionmenu.memopingcheck.isChecked()
            curmemoping = self.config.memoPing()
            if memopingsetting != curmemoping:
                self.config.set('pingSound', memopingsetting)
            namesoundsetting = self.optionmenu.namesoundcheck.isChecked()
            curnamesound = self.config.nameSound()
            if namesoundsetting != curnamesound:
                self.config.set('nameSound', namesoundsetting)
            volumesetting = self.optionmenu.volume.value()
            curvolume = self.config.volume()
            if volumesetting != curvolume:
                self.config.set('volume', volumesetting)
                self.setVolume(volumesetting)
            # timestamps
            timestampsetting = self.optionmenu.timestampcheck.isChecked()
            self.config.set("showTimeStamps", timestampsetting)
            timeformatsetting = str(self.optionmenu.timestampBox.currentText())
            if timeformatsetting == "12 hour":
              self.config.set("time12Format", True)
            else:
              self.config.set("time12Format", False)
            secondssetting = self.optionmenu.secondscheck.isChecked()
            self.config.set("showSeconds", secondssetting)
            # groups
            #groupssetting = self.optionmenu.groupscheck.isChecked()
            #self.config.set("useGroups", groupssetting)
            emptygroupssetting = self.optionmenu.showemptycheck.isChecked()
            self.config.set("emptyGroups", emptygroupssetting)
            # online numbers
            onlinenumsetting = self.optionmenu.showonlinenumbers.isChecked()
            self.config.set("onlineNumbers", onlinenumsetting)
            self.chumList.refreshList()
            # logging
            logpesterssetting = 0
            if self.optionmenu.logpesterscheck.isChecked():
                logpesterssetting = logpesterssetting | self.config.LOG
            if self.optionmenu.stamppestercheck.isChecked():
                logpesterssetting = logpesterssetting | self.config.STAMP
            curlogpesters = self.config.logPesters()
            if logpesterssetting != curlogpesters:
                self.config.set('logPesters', logpesterssetting)
            logmemossetting = 0
            if self.optionmenu.logmemoscheck.isChecked():
                logmemossetting = logmemossetting | self.config.LOG
            if self.optionmenu.stampmemocheck.isChecked():
                logmemossetting = logmemossetting | self.config.STAMP
            curlogmemos = self.config.logMemos()
            if logmemossetting != curlogmemos:
                self.config.set('logMemos', logmemossetting)
            # memo and user links
            linkssetting = self.optionmenu.userlinkscheck.isChecked()
            curlinks = self.config.disableUserLinks()
            if linkssetting != curlinks:
                self.config.set('userLinks', not linkssetting)
            # idle time
            idlesetting = self.optionmenu.idleBox.value()
            curidle = self.config.idleTime()
            if idlesetting != curidle:
                self.config.set('idleTime', idlesetting)
                self.idlethreshold = 60*idlesetting
            # theme
            ghostchumsetting = self.optionmenu.ghostchum.isChecked()
            curghostchum = self.config.ghostchum()
            self.config.set('ghostchum', ghostchumsetting)
            self.themeSelected(ghostchumsetting != curghostchum)
            # randoms
            if self.randhandler.running:
                self.randhandler.setRandomer(self.optionmenu.randomscheck.isChecked())
            # button actions
            minisetting = self.optionmenu.miniBox.currentIndex()
            curmini = self.config.minimizeAction()
            if minisetting != curmini:
                self.config.set('miniAction', minisetting)
                self.setButtonAction(self.miniButton, minisetting, curmini)
            closesetting = self.optionmenu.closeBox.currentIndex()
            curclose = self.config.closeAction()
            if closesetting != curclose:
                self.config.set('closeAction', closesetting)
                self.setButtonAction(self.closeButton, closesetting, curclose)
            # op and voice messages
            opvmesssetting = self.optionmenu.memomessagecheck.isChecked()
            curopvmess = self.config.opvoiceMessages()
            if opvmesssetting != curopvmess:
                self.config.set('opvMessages', opvmesssetting)
            # animated smiles
            if ostools.isOSXBundle():
                animatesetting = False;
            else:
                animatesetting = self.optionmenu.animationscheck.isChecked()
            curanimate = self.config.animations()
            if animatesetting != curanimate:
                self.config.set('animations', animatesetting)
                self.animationSetting.emit(animatesetting)
            # update checked
            updatechecksetting = self.optionmenu.updateBox.currentIndex()
            curupdatecheck = self.config.checkForUpdates()
            if updatechecksetting != curupdatecheck:
                self.config.set('checkUpdates', updatechecksetting)
            # mspa update check
            if ostools.isOSXLeopard():
                mspachecksetting = false
            else:
                mspachecksetting = self.optionmenu.mspaCheck.isChecked()
            curmspacheck = self.config.checkMSPA()
            if mspachecksetting != curmspacheck:
                self.config.set('mspa', mspachecksetting)
            # Taskbar blink
            blinksetting = 0
            if self.optionmenu.pesterBlink.isChecked():
              blinksetting |= self.config.PBLINK
            if self.optionmenu.memoBlink.isChecked():
              blinksetting |= self.config.MBLINK
            curblink = self.config.blink()
            if blinksetting != curblink:
              self.config.set('blink', blinksetting)
            # toast notifications
            self.tm.setEnabled(self.optionmenu.notifycheck.isChecked())
            self.tm.setCurrentType(str(self.optionmenu.notifyOptions.currentText()))
            notifysetting = 0
            if self.optionmenu.notifySigninCheck.isChecked():
                notifysetting |= self.config.SIGNIN
            if self.optionmenu.notifySignoutCheck.isChecked():
                notifysetting |= self.config.SIGNOUT
            if self.optionmenu.notifyNewMsgCheck.isChecked():
                notifysetting |= self.config.NEWMSG
            if self.optionmenu.notifyNewConvoCheck.isChecked():
                notifysetting |= self.config.NEWCONVO
            if self.optionmenu.notifyMentionsCheck.isChecked():
                notifysetting |= self.config.INITIALS
            curnotify = self.config.notifyOptions()
            if notifysetting != curnotify:
                self.config.set('notifyOptions', notifysetting)
            # auto join memos
            autojoins = []
            for i in range(self.optionmenu.autojoinlist.count()):
                autojoins.append(str(self.optionmenu.autojoinlist.item(i).text()))
            self.userprofile.autojoins = autojoins
            # advanced
            ## user mode
            if self.advanced:
                newmodes = self.optionmenu.modechange.text()
                if newmodes:
                    self.setChannelMode.emit(self.profile().handle, newmodes, "")
        except Exception as e:
            logging.error(e)
        finally:
            self.optionmenu = None

    def setButtonAction(self, button, setting, old):
        if old == 0: # minimize to taskbar
            button.clicked.disconnect(self.showMinimized)
        elif old == 1: # minimize to tray
            button.clicked.disconnect(self.closeToTray)
        elif old == 2: # quit
            button.clicked.disconnect(self.app.quit)

        if setting == 0: # minimize to taskbar
            button.clicked.connect(self.showMinimized)
        elif setting == 1: # minimize to tray
            button.clicked.connect(self.closeToTray)
        elif setting == 2: # quit
            button.clicked.connect(self.app.quit)

    @QtCore.pyqtSlot()
    def themeSelectOverride(self):
        self.themeSelected(self.theme.name)

    @QtCore.pyqtSlot()
    def themeSelected(self, override=False):
        if not override:
            themename = str(self.optionmenu.themeBox.currentText())
        else:
            themename = override
        if override or themename != self.theme.name:
            try:
                self.changeTheme(pesterTheme(themename))
            except ValueError as e:
                themeWarning = QtWidgets.QMessageBox(self)
                themeWarning.setText("Theme Error: %s" % (e))
                themeWarning.exec_()
                self.choosetheme = None
                return
            # update profile
            self.userprofile.theme = self.theme
        self.choosetheme = None
    @QtCore.pyqtSlot()
    def closeTheme(self):
        self.choosetheme = None
    @QtCore.pyqtSlot()
    def profileSelected(self):
        if self.chooseprofile.profileBox and \
                self.chooseprofile.profileBox.currentIndex() > 0:
            handle = str(self.chooseprofile.profileBox.currentText())
            if handle == self.profile().handle:
                self.chooseprofile = None
                return
            self.userprofile = userProfile(handle)
            self.changeTheme(self.userprofile.theme)
        else:
            handle = str(self.chooseprofile.chumHandle.text())
            if handle == self.profile().handle:
                self.chooseprofile = None
                return
            profile = PesterProfile(handle,
                                    self.chooseprofile.chumcolor)
            self.userprofile = userProfile.newUserProfile(profile)
            self.changeTheme(self.userprofile.theme)

        self.chatlog.close()
        self.chatlog = PesterLog(handle, self)

        # is default?
        if self.chooseprofile.defaultcheck.isChecked():
            self.config.set("defaultprofile", self.userprofile.chat.handle)
        self.chooseprofile = None
        self.profileChanged.emit()
    @QtCore.pyqtSlot()
    def changeMyColor(self):
        if not hasattr(self, 'colorDialog'):
            self.colorDialog = None
        if self.colorDialog:
            return
        self.colorDialog = QtWidgets.QColorDialog(self)
        color = self.colorDialog.getColor(initial=self.profile().color)
        if not color.isValid():
            color = self.profile().color
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
            closeWarning = QtWidgets.QMessageBox()
            closeWarning.setText("WARNING: CHANGING PROFILES WILL CLOSE ALL CONVERSATION WINDOWS!")
            closeWarning.setInformativeText("i warned you about windows bro!!!! i told you dog!")
            closeWarning.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
            closeWarning.setDefaultButton(QtWidgets.QMessageBox.Ok)
            ret = closeWarning.exec_()
            if ret == QtWidgets.QMessageBox.Cancel:
                return
        self.changeProfile()
    @QtCore.pyqtSlot()
    def aboutPesterchum(self):
        if hasattr(self, 'aboutwindow') and self.aboutwindow:
            return
        self.aboutwindow = AboutPesterchum(self)
        self.aboutwindow.exec_()
        self.aboutwindow = None
    @QtCore.pyqtSlot()
    def loadCalsprite(self):
        self.newConversation("calSprite")
    @QtCore.pyqtSlot()
    def loadChanServ(self):
        self.newConversation("chanServ")
    @QtCore.pyqtSlot()
    def loadNickServ(self):
        self.newConversation("nickServ")
    @QtCore.pyqtSlot()
    def launchHelp(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://nova.xzibition.com/~illuminatedwax/help.html", QtCore.QUrl.TolerantMode))
    @QtCore.pyqtSlot()
    def reportBug(self):
        if hasattr(self, 'bugreportwindow') and self.bugreportwindow:
            return
        self.bugreportwindow = BugReporter(self)
        self.bugreportwindow.exec_()
        self.bugreportwindow = None

    @QtCore.pyqtSlot('QString', 'QString')
    def nickCollision(self, handle, tmphandle):
        self.mychumhandle.setText(tmphandle)
        self.userprofile = userProfile(PesterProfile("pesterClient%d" % (random.randint(100,999)), QtGui.QColor("black"), Mood(0)))
        self.changeTheme(self.userprofile.theme)

        if not hasattr(self, 'chooseprofile'):
            self.chooseprofile = None
        if not self.chooseprofile:
            h = str(handle)
            self.changeProfile(collision=h)
    @QtCore.pyqtSlot('QString')
    def myHandleChanged(self, handle):
        if self.profile().handle == handle:
            self.doAutoIdentify()
            self.doAutoJoins()
            return
        else:
            self.nickCollision(self.profile().handle, handle)
    @QtCore.pyqtSlot()
    def pickTheme(self):
        self.themePicker()

    @QtCore.pyqtSlot(QtWidgets.QSystemTrayIcon.ActivationReason)
    def systemTrayActivated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.systemTrayFunction()
        elif reason == QtWidgets.QSystemTrayIcon.Context:
            pass
            # show context menu i guess
            #self.showTrayContext.emit()

    @QtCore.pyqtSlot()
    def tooManyPeeps(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setText("D: TOO MANY PEOPLE!!!")
        msg.setInformativeText("The server has hit max capacity. Please try again later.")
        msg.show()

    pcUpdate = QtCore.pyqtSignal('QString', 'QString')
    closeToTraySignal = QtCore.pyqtSignal()
    newConvoStarted = QtCore.pyqtSignal('QString', bool, name="newConvoStarted")
    sendMessage = QtCore.pyqtSignal('QString', 'QString')
    sendChannel = QtCore.pyqtSignal('QString', 'QString')
    sendNotice = QtCore.pyqtSignal('QString', 'QString')
    convoClosed = QtCore.pyqtSignal('QString')
    profileChanged = QtCore.pyqtSignal()
    animationSetting = QtCore.pyqtSignal(bool)
    friendRequest = QtCore.pyqtSignal(PesterProfile)
    moodRequest = QtCore.pyqtSignal(PesterProfile)
    moodsRequest = QtCore.pyqtSignal(PesterList)
    moodUpdated = QtCore.pyqtSignal()
    requestChannelList = QtCore.pyqtSignal()
    requestNames = QtCore.pyqtSignal('QString')
    requestUserList = QtCore.pyqtSignal('QString')
    namesUpdated = QtCore.pyqtSignal('QString')
    onlineUsersUpdated = QtCore.pyqtSignal()
    modesUpdated = QtCore.pyqtSignal('QString', 'QString')
    userPresentSignal = QtCore.pyqtSignal('QString','QString','QString')
    userRankSignal = QtCore.pyqtSignal('QString','QString',int,'QString')
    mycolorUpdated = QtCore.pyqtSignal()
    trayIconSignal = QtCore.pyqtSignal(int)
    blockedChum = QtCore.pyqtSignal('QString')
    unblockedChum = QtCore.pyqtSignal('QString')
    kickUser = QtCore.pyqtSignal('QString', 'QString')
    joinChannel = QtCore.pyqtSignal('QString')
    leftChannel = QtCore.pyqtSignal('QString')
    setChannelMode = QtCore.pyqtSignal('QString', 'QString', 'QString')
    channelNames = QtCore.pyqtSignal('QString')
    inviteChum = QtCore.pyqtSignal('QString', 'QString')
    inviteOnlyChan = QtCore.pyqtSignal('QString')
    closeSignal = QtCore.pyqtSignal()
    reconnectOSFC = QtCore.pyqtSignal()
    registerOSFC = QtCore.pyqtSignal()
    gainAttention = QtCore.pyqtSignal(QtWidgets.QWidget)
    pingServer = QtCore.pyqtSignal()
    setAway = QtCore.pyqtSignal(bool)
    killSomeQuirks = QtCore.pyqtSignal('QString', 'QString')

class PesterTray(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, mainwindow, parent):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.mainwindow = mainwindow

    @QtCore.pyqtSlot(int)
    def changeTrayIcon(self, i):
        if i == 0:
            self.setIcon(PesterIcon(self.mainwindow.theme["main/icon"]))
        else:
            self.setIcon(PesterIcon(self.mainwindow.theme["main/newmsgicon"]))
    @QtCore.pyqtSlot()
    def mainWindowClosed(self):
        self.hide()

class MainProgram(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName("OSFC 4.13")
        self.app.setQuitOnLastWindowClosed(False)

        options = self.oppts(sys.argv[1:])

        self.widget = PesterWindow(options, app=self.app)
        self.widget.show()

        self.trayicon = PesterTray(PesterIcon(self.widget.theme["main/icon"]), self.widget, self.app)
        self.traymenu = QtWidgets.QMenu()
        moodMenu = self.traymenu.addMenu("SET MOOD")
        moodCategories = {}
        for k in Mood.moodcats:
            moodCategories[k] = moodMenu.addMenu(k.upper())
        self.moodactions = {}
        for (i,m) in enumerate(Mood.moods):
            mobj = PesterMoodAction(i, self.widget.moods.updateMood)
            maction = QtWidgets.QAction(m.upper(), self, triggered=mobj.updateMood)
            self.moodactions[i] = mobj
            moodCategories[Mood.revmoodcats[m]].addAction(maction)
        miniAction = QtWidgets.QAction("MINIMIZE", self, triggered=self.widget.showMinimized)
        exitAction = QtWidgets.QAction("EXIT", self, triggered=self.app.quit)
        self.traymenu.addAction(miniAction)
        self.traymenu.addAction(exitAction)

        self.trayicon.setContextMenu(self.traymenu)
        self.trayicon.show()
        self.trayicon.activated.connect(self.widget.systemTrayActivated)
        self.widget.trayIconSignal.connect(self.trayicon.changeTrayIcon)
        self.widget.closeToTraySignal.connect(self.trayiconShow)
        self.widget.closeSignal.connect(self.trayicon.mainWindowClosed)
        self.trayicon.messageClicked.connect(self.trayMessageClick)

        self.attempts = 0

        self.osfc = PesterOSFC(self.widget.config, self.widget)
        self.connectWidgets(self.osfc, self.widget)

        self.widget.gainAttention.connect(self.alertWindow)

        # 0 Once a day
        # 1 Once a week
        # 2 Only on start
        # 3 Never
        check = self.widget.config.checkForUpdates()
        if check == 2:
            self.runUpdateSlot()
        elif check == 0:
            seconds = 60 * 60 * 24
            if int(time()) - self.widget.config.lastUCheck() < seconds:
                seconds -= int(time()) - self.widget.config.lastUCheck()
            if seconds < 0: seconds = 0
            QtCore.QTimer.singleShot(1000*seconds, self.runUpdateSlot)
        elif check == 1:
            seconds = 60 * 60 * 24 * 7
            if int(time()) - self.widget.config.lastUCheck() < seconds:
                seconds -= int(time()) - self.widget.config.lastUCheck()
            if seconds < 0: seconds = 0
            QtCore.QTimer.singleShot(1000*seconds, self.runUpdateSlot)

    @QtCore.pyqtSlot()
    def runUpdateSlot(self):
        q = queue.Queue(1)
        s = threading.Thread(target=version.updateCheck, args=(q,))
        w = threading.Thread(target=self.showUpdate, args=(q,))
        w.start()
        s.start()
        self.widget.config.set('lastUCheck', int(time()))
        check = self.widget.config.checkForUpdates()
        if check == 0:
            seconds = 60 * 60 * 24
        elif check == 1:
            seconds = 60 * 60 * 24 * 7
        else:
            return
        QtCore.QTimer.singleShot(1000*seconds, self.runUpdateSlot)

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def alertWindow(self, widget):
        self.app.alert(widget)

    @QtCore.pyqtSlot()
    def trayiconShow(self):
        self.trayicon.show()
        if self.widget.config.trayMessage():
            self.trayicon.showMessage("Pesterchum", "Pesterchum is still running in the system tray.\n\
Right click to close it.\n\
Click this message to never see this again.")

    @QtCore.pyqtSlot()
    def trayMessageClick(self):
        self.widget.config.set('traymsg', False)

    def osfcQtConnections(self, osfc, widget):
        # OSFC --> Main window
        return ((widget.sendMessage, osfc.sendMessage),
                (widget.sendChannel, osfc.sendChannel),
                (widget.sendNotice, osfc.sendNotice),
                (widget.newConvoStarted, osfc.startConvo),
                (widget.convoClosed, osfc.endConvo),
                (widget.profileChanged, osfc.updateProfile),
                (widget.friendRequest, osfc.addFriend),
                (widget.moodRequest, osfc.getMood),
                (widget.moodsRequest, osfc.getMoods),
                (widget.moodUpdated, osfc.updateMood),
                (widget.mycolorUpdated, osfc.updateColor),
                (widget.blockedChum, osfc.blockedChum),
                (widget.unblockedChum, osfc.unblockedChum),
                (widget.requestNames, osfc.requestNames),
                (widget.requestUserList, osfc.requestUserList),
                (widget.requestChannelList, osfc.requestChannelList),
                (widget.joinChannel, osfc.joinChannel),
                (widget.leftChannel, osfc.leftChannel),
                (widget.kickUser, osfc.kickUser),
                (widget.setChannelMode, osfc.setChannelMode),
                (widget.channelNames, osfc.channelNames),
                (widget.inviteChum, osfc.inviteChum),
                (widget.pingServer, osfc.pingServer),
                (widget.setAway, osfc.setAway),
                (widget.killSomeQuirks, osfc.killSomeQuirks),
                (widget.reconnectOSFC, osfc.reconnectOSFC),
                (widget.registerOSFC, osfc.registerOSFC),
                 # Main window --> OSFC    
                (osfc.connected, widget.connected),
                (osfc.loginFailed, widget.loginFailed),
                (osfc.moodUpdated, widget.updateMoodSlot),
                (osfc.messageReceived, widget.deliverMessage),
                (osfc.beginReceived, widget.deliverBegin),
                (osfc.memoReceived, widget.deliverMemo),
                (osfc.noticeReceived, widget.deliverNotice),
                (osfc.inviteReceived, widget.deliverInvite),
                (osfc.nickCollision, widget.nickCollision),
                (osfc.myHandleChanged, widget.myHandleChanged),
                (osfc.namesReceived, widget.updateNames),
                (osfc.userListReceived, widget.updateOnlineUsers),
                (osfc.userPresentUpdate, widget.userPresentUpdate),
                (osfc.userRankUpdate, widget.userRankUpdate),
                (osfc.channelListReceived, widget.updateChannelList),
                (osfc.friendListReceived, widget.updateFriendList),
                (osfc.timeCommand, widget.timeCommand),
                (osfc.chanInviteOnly, widget.chanInviteOnly),
                (osfc.modesUpdated, widget.modesUpdated),
                (osfc.cannotSendToChan, widget.cannotSendToChan),
                (osfc.tooManyPeeps, widget.tooManyPeeps),
                (osfc.quirkDisable, widget.quirkDisable))

    def connectWidgets(self, osfc, widget):
        osfc.finished.connect(self.restartOSFC)
        osfc.connected.connect(self.connected)
        for sig, slot in self.osfcQtConnections(osfc, widget):
            sig.connect(slot)

    def disconnectWidgets(self, osfc, widget):
        for sig, slot in self.osfcQtConnections(osfc, widget):
            sig.disconnect(slot)
        osfc.connected.disconnect(self.connected)
        self.osfc.finished.disconnect(self.restartOSFC)

    def showUpdate(self, q):
        new_url = q.get()
        if new_url[0]:
            self.widget.pcUpdate.emit(new_url[0], new_url[1])
        q.task_done()

    def showLoading(self, widget, msg="CONN3CT1NG"):
        self.widget.show()
        if len(msg) > 60:
            newmsg = []
            while len(msg) > 60:
                s = msg.rfind(" ", 0, 60)
                if s == -1:
                    break
                newmsg.append(msg[:s])
                newmsg.append("\n")
                msg = msg[s+1:]
            newmsg.append(msg)
            msg = "".join(newmsg)
        if hasattr(self.widget, 'loadingscreen') and widget.loadingscreen:
            widget.loadingscreen.loadinglabel.setText(msg)
            if self.reconnectok:
                widget.loadingscreen.showReconnect()
            else:
                widget.loadingscreen.hideReconnect()
        else:
            widget.loadingscreen = LoadingScreen(widget)
            widget.loadingscreen.loadinglabel.setText(msg)
            widget.loadingscreen.rejected.connect(widget.app.quit)
            self.widget.loadingscreen.tryAgain.connect(self.tryAgain)
            if hasattr(self, 'osfc') and self.osfc.madeConnection:
                return
            if self.reconnectok:
                widget.loadingscreen.showReconnect()
            else:
                widget.loadingscreen.hideReconnect()
            status = widget.loadingscreen.exec_()
            if status == QtWidgets.QDialog.Rejected:
                pass # TODO: What do we have to do here if we can't connect?
                # sys.exit(0)
            else:
                # join open memos
                if self.widget.tabmemo:
                    for c in self.widget.tabmemo.convos:
                        self.osfc.joinChannel(c)
                else:
                    for c in list(self.widget.memos.values()):
                        self.osfc.joinChannel(c.channel)
                return True

    @QtCore.pyqtSlot()
    def connected(self):
        self.attempts = 0
    @QtCore.pyqtSlot()
    def tryAgain(self):
        if not self.reconnectok:
            return
        if self.widget.loadingscreen:
            self.widget.loadingscreen.done(QtWidgets.QDialog.Accepted)
            self.widget.loadingscreen = None
        self.attempts += 1
        if hasattr(self, 'osfc') and self.osfc:
            self.osfc.reconnectOSFC()
            self.osfc.quit()
        else:
            self.restartOSFC()
    @QtCore.pyqtSlot()
    def restartOSFC(self):
        if hasattr(self, 'osfc') and self.osfc:
            self.disconnectWidgets(self.osfc, self.widget)
            stop = self.osfc.stopOSFC
            del self.osfc
        else:
            stop = None
        if stop is None:
            self.osfc = PesterOSFC(self.widget.config, self.widget)
            self.connectWidgets(self.osfc, self.widget)
            self.osfc.start()
            if self.attempts == 1:
                msg = "R3CONN3CT1NG"
            elif self.attempts > 1:
                msg = "R3CONN3CT1NG %d" % (self.attempts)
            else:
                msg = "CONN3CT1NG"
            self.reconnectok = False
            self.showLoading(self.widget, msg)
        else:
            self.reconnectok = True
            self.showLoading(self.widget, "F41L3D: %s" % stop)

    def oppts(self, argv):
        options = {}
        try:
            opts, args = getopt.getopt(argv, "s:p:", ["server=", "port=", "advanced", "no-honk"])
        except getopt.GetoptError:
            return options
        for opt, arg in opts:
            if opt in ("-s", "--server"):
                options["server"] = arg
            elif opt in ("-p", "--port"):
                options["port"] = arg
            elif opt in ("--advanced"):
                options["advanced"] = True
            elif opt in ("--no-honk"):
                options["honk"] = False
        return options

    def run(self):
        self.widget.show()
        self.reconnectok = False
        self.osfc.start()
        self.showLoading(self.widget)

        sys.exit(self.app.exec_())

pesterchum = MainProgram()
pesterchum.run()

from string import Template
import re
from PyQt4 import QtGui, QtCore

from dataobjs import PesterProfile, Mood
from generic import PesterIcon
from parsetools import escapeBrackets, convertTags

class PesterTabWindow(QtGui.QFrame):
    def __init__(self, mainwindow, parent=None, convo="convo"):
        QtGui.QFrame.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.mainwindow = mainwindow

        self.tabs = QtGui.QTabBar(self)
        self.tabs.setTabsClosable(True)
        self.connect(self.tabs, QtCore.SIGNAL('currentChanged(int)'),
                     self, QtCore.SLOT('changeTab(int)'))
        self.connect(self.tabs, QtCore.SIGNAL('tabCloseRequested(int)'),
                     self, QtCore.SLOT('tabClose(int)'))

        self.initTheme(self.mainwindow.theme[convo])
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.convos = {}
        self.tabIndices = {}
        self.currentConvo = None
        self.changedTab = False
        self.softclose = False

        self.type = convo

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
        self.convos[convo.title()] = convo
        # either addTab or setCurrentIndex will trigger changed()
        newindex = self.tabs.addTab(convo.title())
        self.tabIndices[convo.title()] = newindex
        self.tabs.setCurrentIndex(newindex)
        self.tabs.setTabIcon(newindex, convo.icon())
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
            self.tabs.tabText(self.tabs.currentIndex()) == convo.title()):
            return True
        
    def keyPressEvent(self, event):
        keypress = event.key()
        mods = event.modifiers()
        if ((mods & QtCore.Qt.ControlModifier) and 
            keypress == QtCore.Qt.Key_Tab):
            nexti = (self.tabIndices[self.currentConvo.title()] + 1) % self.tabs.count()
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
        self.tabs.setTabTextColor(i, QtGui.QColor(self.mainwindow.theme["%s/tabs/newmsgcolor" % (self.type)]))
        convo = self.convos[handle]
        def func():
            convo.showChat()
        self.mainwindow.waitingMessages.addMessage(handle, func)
        # set system tray
    def clearNewMessage(self, handle):
        try:
            i = self.tabIndices[handle]
            self.tabs.setTabTextColor(i, self.defaultTabTextColor)
        except KeyError:
            pass
        self.mainwindow.waitingMessages.messageAnswered(handle)
    def initTheme(self, convo):
        self.resize(*convo["size"])
        self.setStyleSheet(convo["style"])
        self.tabs.setShape(convo["tabs"]["tabstyle"])
        self.tabs.setStyleSheet("QTabBar::tab{ %s } QTabBar::tab:selected { %s }" % (convo["tabs"]["style"], convo["tabs"]["selectedstyle"]))

    def changeTheme(self, theme):
        self.initTheme(theme["memos"])
        for c in self.convos.values():
            tabi = self.tabIndices[c.title()]
            self.tabs.setTabIcon(tabi, c.icon())
        currenttabi = self.tabs.currentIndex()
        if currenttabi >= 0:
            currentHandle = unicode(self.tabs.tabText(self.tabs.currentIndex()))
            self.setWindowIcon(self.convos[currentHandle].icon())
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
        self.setWindowIcon(convo.icon())
        self.setWindowTitle(convo.title())
        self.activateWindow()
        self.raise_()
        convo.raiseChat()

    windowClosed = QtCore.pyqtSignal()

class PesterText(QtGui.QTextEdit):
    def __init__(self, theme, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setStyleSheet(theme["convo/textarea/style"])
        self.setReadOnly(True)
        self.setMouseTracking(True)
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
            window.chatlog.log(chum.handle, convertTags(msg, "bbcode"))
            self.append(convertTags(msg))
        elif msg == "PESTERCHUM:CEASE":
            parent.setChumOpen(False)
            msg = chum.pestermsg(me, systemColor, window.theme["convo/text/ceasepester"])
            window.chatlog.log(chum.handle, convertTags(msg, "bbcode"))
            self.append(convertTags(msg))
        elif msg == "PESTERCHUM:BLOCK":
            msg = chum.pestermsg(me, systemColor, window.theme['convo/text/blocked'])
            window.chatlog.log(chum.handle, convertTags(msg, "bbcode"))
            self.append(convertTags(msg))
        elif msg == "PESTERCHUM:UNBLOCK":
            msg = chum.pestermsg(me, systemColor, window.theme['convo/text/unblocked'])
            window.chatlog.log(chum.handle, convertTags(msg, "bbcode"))
            self.append(convertTags(msg))
        elif msg[0:3] == "/me" or msg[0:13] == "PESTERCHUM:ME":
            if msg[0:3] == "/me":
                start = 3
            else:
                start = 13
            space = msg.find(" ")
            msg = chum.memsg(systemColor, msg[start:space], msg[space:])
            if chum is me:
                window.chatlog.log(parent.chum.handle, convertTags(msg, "bbcode"))
            else:
                window.chatlog.log(chum.handle, convertTags(msg, "bbcode"))
            self.append(convertTags(msg))
        else:
            if not parent.chumopen and chum is not me:
                beginmsg = chum.pestermsg(me, systemColor, window.theme["convo/text/beganpester"])
                parent.setChumOpen(True)
                window.chatlog.log(chum.handle, convertTags(beginmsg, "bbcode"))
                self.append(convertTags(beginmsg))

            msg = "<c=%s>%s: %s</c>" % (color, initials, msg)
            msg = escapeBrackets(msg)
            self.append(convertTags(msg))
            if chum is me:
                window.chatlog.log(parent.chum.handle, convertTags(msg, "bbcode"))
            else:
                window.chatlog.log(chum.handle, convertTags(msg, "bbcode"))
    def changeTheme(self, theme):
        self.setStyleSheet(theme["convo/textarea/style"])
        sb = self.verticalScrollBar()
        sb.setMaximum(sb.maximum()+1000) # ugly hack but whatcha gonna do
        sb.setValue(sb.maximum())
    def focusInEvent(self, event):
        self.parent().clearNewMessage()
        QtGui.QTextEdit.focusInEvent(self, event)

    def mousePressEvent(self, event):
        url = self.anchorAt(event.pos())
        if url != "":
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url, QtCore.QUrl.TolerantMode))
        QtGui.QTextEdit.mousePressEvent(self, event)
    def mouseMoveEvent(self, event):
        QtGui.QTextEdit.mouseMoveEvent(self, event)
        if self.anchorAt(event.pos()):
            if self.viewport().cursor().shape != QtCore.Qt.PointingHandCursor:
                self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        else:
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))

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
        self.setWindowIcon(self.icon())
        self.setWindowTitle(self.title())

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
        margins = self.mainwindow.theme["convo/margins"]
        self.layout.setContentsMargins(margins["left"], margins["top"],
                                      margins["right"], margins["bottom"])
        
        self.setLayout(self.layout)

        self.chumopen = False

        if parent:
            parent.addChat(self)
        if initiated:
            msg = self.mainwindow.profile().pestermsg(self.chum, QtGui.QColor(self.mainwindow.theme["convo/systemMsgColor"]), self.mainwindow.theme["convo/text/beganpester"])
            self.setChumOpen(True)
            self.textArea.append(convertTags(msg))
            self.mainwindow.chatlog.log(self.title(), convertTags(msg, "bbcode"))
        self.newmessage = False

    def title(self):
        return self.chum.handle
    def icon(self):
        return self.chum.mood.icon(self.mainwindow.theme)

    def updateMood(self, mood, unblocked=False):
        if mood.name() == "offline" and self.chumopen == True and not unblocked:
            msg = self.chum.pestermsg(self.mainwindow.profile(), QtGui.QColor(self.mainwindow.theme["convo/systemMsgColor"]), self.mainwindow.theme["convo/text/ceasepester"])
            self.textArea.append(convertTags(msg))
            self.mainwindow.chatlog.log(self.title(), convertTags(msg, "bbcode"))
            self.chumopen = False
        if self.parent():
            self.parent().updateMood(self.title(), mood, unblocked)
        else:
            if self.chum.blocked(self.mainwindow.config) and not unblocked:
                self.setWindowIcon(QtGui.QIcon(self.mainwindow.theme["main/chums/moods/blocked/icon"]))
            else:
                self.setWindowIcon(mood.icon(self.mainwindow.theme))
        # print mood update?
    def updateBlocked(self):
        if self.parent():
            self.parent().updateBlocked(self.title())
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
                (self.parent() and self.parent().convoHasFocus(self.title()))):
            # ok if it has a tabconvo parent, send that the notify.
            if self.parent():
                self.parent().notifyNewMessage(self.title())
            # if not change the window title and update system tray
            else:
                self.newmessage = True
                self.setWindowTitle(self.title()+"*")
                def func():
                    self.showChat()
                self.mainwindow.waitingMessages.addMessage(self.title(), func)
                
    def clearNewMessage(self):
        if self.parent():
            self.parent().clearNewMessage(self.title())
        elif self.newmessage:
            self.newmessage = False
            self.setWindowTitle(self.title())
            self.mainwindow.waitingMessages.messageAnswered(self.title())
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
            self.parent().showChat(self.title())
        self.raiseChat()

    def closeEvent(self, event):
        self.mainwindow.waitingMessages.messageAnswered(self.title())
        self.windowClosed.emit(self.title())
    def setChumOpen(self, o):
        self.chumopen = o
    def changeTheme(self, theme):
        self.resize(*theme["convo/size"])
        self.setStyleSheet(theme["convo/style"])
        margins = theme["convo/margins"]
        self.layout.setContentsMargins(margins["left"], margins["top"],
                                       margins["right"], margins["bottom"])

        self.setWindowIcon(self.icon())
        t = Template(self.mainwindow.theme["convo/chumlabel/text"])
        self.chumLabel.setText(t.safe_substitute(handle=self.title()))
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
        if hasattr(self, 'chumopen') and not self.chumopen:
            self.mainwindow.newConvoStarted.emit(QtCore.QString(self.title()), True)
        # convert color tags
        text = convertTags(unicode(text), "ctag")
        self.messageSent.emit(text, self.title())

    messageSent = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
    windowClosed = QtCore.pyqtSignal(QtCore.QString)

    aligndict = {"h": {"center": QtCore.Qt.AlignHCenter,
                       "left": QtCore.Qt.AlignLeft,
                       "right": QtCore.Qt.AlignRight },
                 "v": {"center": QtCore.Qt.AlignVCenter,
                       "top": QtCore.Qt.AlignTop,
                       "bottom": QtCore.Qt.AlignBottom } }

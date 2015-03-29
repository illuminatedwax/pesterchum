from string import Template
import re
import logging
from copy import copy
from PyQt5 import QtGui, QtCore, QtWidgets

from mood import Mood
from dataobjs import PesterProfile, PesterHistory
from generic import PesterIcon, RightClickList
from convo import PesterConvo, PesterInput, PesterText, PesterTabWindow
from parsetools import convertTags, \
    lexMessage, colorBegin, colorEnd, mecmd, smiledict, oocre
from logviewer import PesterLogViewer

class MemoTabWindow(PesterTabWindow):
    def __init__(self, mainwindow, parent=None):
        PesterTabWindow.__init__(self, mainwindow, parent, "memos")
    def addChat(self, convo):
        self.convos[convo.channel] = convo
        # either addTab or setCurrentIndex will trigger changed()
        newindex = self.tabs.addTab(convo.channel)
        self.tabIndices[convo.channel] = newindex
        self.tabs.setCurrentIndex(newindex)
        self.tabs.setTabIcon(newindex, PesterIcon(self.mainwindow.theme["memos/memoicon"]))
    def updateBlocked(self):
        pass
    def updateMood(self):
        pass

_ctag_begin = re.compile(r'<c=(.*?)>')

class MemoText(PesterText):
    def __init__(self, theme, parent=None):
        QtWidgets.QTextEdit.__init__(self, parent)
        if hasattr(self.parent(), 'mainwindow'):
            self.mainwindow = self.parent().mainwindow
        else:
            self.mainwindow = self.parent()
        if type(parent.parent()) is PesterTabWindow:
            self.tabobject = parent.parent()
            self.hasTabs = True
        else:
            self.hasTabs = False
        self.initTheme(theme)
        self.setReadOnly(True)
        self.setMouseTracking(True)
        self.textSelected = False
        self.copyAvailable.connect(self.textReady)
        self.urls = {}
        for k in smiledict:
            self.addAnimation(QtCore.QUrl("smilies/%s" % (smiledict[k])), "smilies/%s" % (smiledict[k]))
        self.mainwindow.animationSetting.connect(self.animateChanged)

    def initTheme(self, theme):
        if "memos/scrollbar" in theme:
            self.setStyleSheet("QTextEdit { %s } QScrollBar:vertical { %s } QScrollBar::handle:vertical { %s } QScrollBar::add-line:vertical { %s } QScrollBar::sub-line:vertical { %s } QScrollBar:up-arrow:vertical { %s } QScrollBar:down-arrow:vertical { %s }" % (theme["memos/textarea/style"], theme["memos/scrollbar/style"], theme["memos/scrollbar/handle"], theme["memos/scrollbar/downarrow"], theme["memos/scrollbar/uparrow"], theme["memos/scrollbar/uarrowstyle"], theme["memos/scrollbar/darrowstyle"] ))
        else:
            self.setStyleSheet("QTextEdit { %s }" % theme["memos/textarea/style"])

    def addMessage(self, msg, chum):
        if type(msg) in [str]:
            lexmsg = lexMessage(msg)
        else:
            lexmsg = msg
        parent = self.parent()
        window = parent.mainwindow
        me = window.profile()
        if self.mainwindow.config.animations():
            for m in self.urls:
                if convertTags(lexmsg).find(self.urls[m].toString()) != -1:
                    if m.state() == QtGui.QMovie.NotRunning:
                        m.start()
        chumdb = window.chumdb
        if chum is not me: # SO MUCH WH1T3SP4C3 >:]
            if type(lexmsg[0]) is colorBegin: # get color tag
                colortag = lexmsg[0]
                try:
                    color = QtGui.QColor(*[int(c) for c in colortag.color.split(",")])
                except ValueError:
                    color = QtGui.QColor("black")
                else:
                    chumdb.setColor(chum.handle, color)
                    parent.updateColor(chum.handle, color)
            else:
                color = chumdb.getColor(chum.handle)
        else:
            color = me.color

        chum.color = color
        systemColor = QtGui.QColor(window.theme["memos/systemMsgColor"])

        def makeSafe(msg):
            if msg.count("<c") > msg.count("</c>"):
                for i in range(msg.count("<c") - msg.count("</c>")):
                    msg = msg + "</c>"
            return "<span style=\"color:#000000\">" + msg + "</span>"
        if type(lexmsg[0]) is mecmd:
            memsg = chum.memsg(systemColor, lexmsg)
            window.chatlog.log(parent.channel, memsg)
            self.append(convertTags(memsg))
        else:
            self.append(makeSafe(convertTags(lexmsg)))
            window.chatlog.log(parent.channel, lexmsg)

    def changeTheme(self, theme):
        self.initTheme(theme)
    def submitLogTitle(self):
        return "[%s]" % (self.parent().title())

class MemoInput(PesterInput):
    def __init__(self, theme, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)
        self.setStyleSheet(theme["memos/input/style"])
    def changeTheme(self, theme):
        self.setStyleSheet(theme["memos/input/style"])

class PesterMemo(PesterConvo):
    def __init__(self, channel, mainwindow, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.channel = channel
        self.setObjectName(self.channel)
        self.mainwindow = mainwindow
        self.setWindowTitle(channel)
        self.channelLabel = QtWidgets.QLabel(self)
        self.channelLabel.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding))

        self.textArea = MemoText(self.mainwindow.theme, self)
        self.textInput = MemoInput(self.mainwindow.theme, self)
        self.textInput.setFocus()

        self.miniUserlist = QtWidgets.QPushButton(">\n>", self, clicked=self.toggleUserlist)
        #self.miniUserlist.setStyleSheet("border:1px solid #a68168; border-width: 2px 0px 2px 2px; height: 90px; width: 10px; color: #cd8f9d; font-family: 'Arial'; background: white; margin-left: 2px;")

        self.userlist = RightClickList(self)
        self.userlist.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))
        self.userlist.optionsMenu = QtWidgets.QMenu(self)
        self.addchumAction = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/addchum"], self, triggered=self.addChumSlot)
        self.banuserAction = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/banuser"], self, triggered=self.banSelectedUser)
        self.opAction = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/opuser"], self, triggered=self.opSelectedUser)
        self.voiceAction = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/voiceuser"], self, triggered=self.voiceSelectedUser)
        self.quirkDisableAction = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/quirkkill"], self, triggered=self.killQuirkUser)
        self.userlist.optionsMenu.addAction(self.addchumAction)
        # ban & op list added if we are op

        self.optionsMenu = QtWidgets.QMenu(self)
        self.oocToggle = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/ooc"], self, toggled=self.toggleOOC)
        self.oocToggle.setCheckable(True)
        self.quirksOff = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/quirksoff"], self, toggled=self.toggleQuirks)
        self.quirksOff.setCheckable(True)
        self.logchum = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/viewlog"], self, triggered=self.openChumLogs)
        self.invitechum = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/invitechum"], self, triggered=self.inviteChums)
        self.optionsMenu.addAction(self.quirksOff)
        self.optionsMenu.addAction(self.oocToggle)
        self.optionsMenu.addAction(self.logchum)
        self.optionsMenu.addAction(self.invitechum)

        self.chanModeMenu = QtWidgets.QMenu(self.mainwindow.theme["main/menus/rclickchumlist/memosetting"], self)
        self.chanNoquirks = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/memonoquirk"], self, toggled=self.noquirksChan)
        self.chanNoquirks.setCheckable(True)
        self.chanHide = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/memohidden"], self, toggled=self.hideChan)
        self.chanHide.setCheckable(True)
        self.chanInvite = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/memoinvite"], self, toggled=self.inviteChan)
        self.chanInvite.setCheckable(True)
        self.chanMod = QtWidgets.QAction(self.mainwindow.theme["main/menus/rclickchumlist/memomute"], self, toggled=self.modChan)
        self.chanMod.setCheckable(True)
        self.chanModeMenu.addAction(self.chanNoquirks)
        self.chanModeMenu.addAction(self.chanHide)
        self.chanModeMenu.addAction(self.chanInvite)
        self.chanModeMenu.addAction(self.chanMod)

        self.initTheme(self.mainwindow.theme)

        # connect
        self.textInput.returnPressed.connect(self.sentMessage)

        layout_0 = QtWidgets.QVBoxLayout()
        layout_0.addWidget(self.textArea)
        layout_0.addWidget(self.textInput)

        layout_1 = QtWidgets.QHBoxLayout()
        layout_1.addLayout(layout_0)
        layout_1.addWidget(self.miniUserlist)
        layout_1.addWidget(self.userlist)

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.channelLabel)
        self.layout.addLayout(layout_1)
        self.layout.addLayout(layout_2)
        self.layout.setSpacing(0)
        margins = self.mainwindow.theme["memos/margins"]
        self.layout.setContentsMargins(margins["left"], margins["top"],
                                  margins["right"], margins["bottom"])

        self.setLayout(self.layout)

        if parent:
            parent.addChat(self)

        p = self.mainwindow.profile()
        systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
        msg = p.memoopenmsg(systemColor, self.mainwindow.theme["convo/text/openmemo"], self.channel)
        self.textArea.append(convertTags(msg))
        self.mainwindow.chatlog.log(self.channel, msg)

        self.op = False
        self.newmessage = False
        self.history = PesterHistory()
        self.applyquirks = True
        self.ooc = False

    @QtCore.pyqtSlot()
    def toggleUserlist(self):
        if self.userlist.isHidden():
            self.userlist.show()
            self.miniUserlist.setText(">\n>")
            self.miniUserlist.setStyleSheet("%s border-width: 2px 0px 2px 2px;" % self.miniUserlist.styleSheet())
        else:
            self.userlist.hide()
            self.miniUserlist.setText("<\n<")
            self.miniUserlist.setStyleSheet("%s border-width: 2px;" % self.miniUserlist.styleSheet())

    def title(self):
        return self.channel
    def icon(self):
        return PesterIcon(self.mainwindow.theme["memos/memoicon"])

    def updateMood(self):
        pass
    def updateBlocked(self):
        pass
    def updateColor(self, handle, color):
        chums = self.userlist.findItems(handle, QtCore.Qt.MatchFlags(8))
        for c in chums:
            c.setForeground(QtGui.QBrush(color))
    def addMessage(self, text, handle):
        if type(handle) is bool:
            chum = self.mainwindow.profile()
        else:
            chum = PesterProfile(handle)
            self.notifyNewMessage()
        self.textArea.addMessage(text, chum)

    def initTheme(self, theme):
        self.resize(*theme["memos/size"])
        self.setStyleSheet("QFrame#%s { %s }" % (self.channel, theme["memos/style"]))
        self.setWindowIcon(PesterIcon(theme["memos/memoicon"]))

        t = Template(theme["memos/label/text"])
        if self.mainwindow.advanced and hasattr(self, 'modes'):
            self.channelLabel.setText(t.safe_substitute(channel=self.channel) + "(%s)" % (self.modes))
        else:
            self.channelLabel.setText(t.safe_substitute(channel=self.channel))
        self.channelLabel.setStyleSheet(theme["memos/label/style"])
        self.channelLabel.setAlignment(self.aligndict["h"][theme["memos/label/align/h"]] | self.aligndict["v"][theme["memos/label/align/v"]])
        self.channelLabel.setMaximumHeight(theme["memos/label/maxheight"])
        self.channelLabel.setMinimumHeight(theme["memos/label/minheight"])

        self.userlist.optionsMenu.setStyleSheet(theme["main/defaultwindow/style"])
        scrolls = "width: 12px; height: 12px; border: 0; padding: 0;"
        if "main/chums/scrollbar" in theme:
            self.userlist.setStyleSheet("QListWidget { %s } QScrollBar { %s } QScrollBar::handle { %s } QScrollBar::add-line { %s } QScrollBar::sub-line { %s } QScrollBar:up-arrow { %s } QScrollBar:down-arrow { %s }" % (theme["memos/userlist/style"], theme["main/chums/scrollbar/style"] + scrolls, theme["main/chums/scrollbar/handle"], theme["main/chums/scrollbar/downarrow"], theme["main/chums/scrollbar/uparrow"], theme["main/chums/scrollbar/uarrowstyle"], theme["main/chums/scrollbar/darrowstyle"] ))
        elif "convo/scrollbar" in theme:
            self.userlist.setStyleSheet("QListWidget { %s } QScrollBar { %s } QScrollBar::handle { %s } QScrollBar::add-line { %s } QScrollBar::sub-line { %s } QScrollBar:up-arrow { %s } QScrollBar:down-arrow { %s }" % (theme["memos/userlist/style"], theme["convo/scrollbar/style"] + scrolls, theme["convo/scrollbar/handle"], "display:none;", "display:none;", "display:none;", "display:none;" ))
        else:
            self.userlist.setStyleSheet("QListWidget { %s } QScrollBar { %s } QScrollBar::handle { %s }" % (theme["memos/userlist/style"], scrolls, "background-color: black;"))
        self.userlist.setFixedWidth(theme["memos/userlist/width"])

        if self.userlist.isHidden():
            borders = "border-width: 2px;"
        else:
            borders = "border-width: 2px 0px 2px 2px;"
        self.miniUserlist.setStyleSheet("%s padding: 0px; margin: 0px; margin-left: 5px; width: 10px; height: 90px; %s" % (theme["memos/userlist/style"], borders))

        self.addchumAction.setText(theme["main/menus/rclickchumlist/addchum"])
        self.banuserAction.setText(theme["main/menus/rclickchumlist/banuser"])
        self.opAction.setText(theme["main/menus/rclickchumlist/opuser"])
        self.voiceAction.setText(theme["main/menus/rclickchumlist/voiceuser"])
        self.quirkDisableAction.setText(theme["main/menus/rclickchumlist/quirkkill"])
        self.quirksOff.setText(theme["main/menus/rclickchumlist/quirksoff"])
        self.logchum.setText(theme["main/menus/rclickchumlist/viewlog"])
        self.invitechum.setText(theme["main/menus/rclickchumlist/invitechum"])
        self.chanModeMenu.setTitle(theme["main/menus/rclickchumlist/memosetting"])
        self.chanNoquirks.setText(theme["main/menus/rclickchumlist/memonoquirk"])
        self.chanHide.setText(theme["main/menus/rclickchumlist/memohidden"])
        self.chanInvite.setText(theme["main/menus/rclickchumlist/memoinvite"])
        self.chanMod.setText(theme["main/menus/rclickchumlist/memomute"])

    def changeTheme(self, theme):
        self.initTheme(theme)
        self.textArea.changeTheme(theme)
        self.textInput.changeTheme(theme)
        margins = theme["memos/margins"]
        self.layout.setContentsMargins(margins["left"], margins["top"],
                                  margins["right"], margins["bottom"])
        for item in [self.userlist.item(i) for i in range(0,self.userlist.count())]:
            self.iconCrap(item)

    def addUser(self, handle):
        chumdb = self.mainwindow.chumdb
        defaultcolor = QtGui.QColor("black")
        founder = False
        op =      False
        halfop =  False
        admin =   False
        voice =   False
        item = QtWidgets.QListWidgetItem(handle)
        if handle == self.mainwindow.profile().handle:
            color = self.mainwindow.profile().color
        else:
            color = chumdb.getColor(handle, defaultcolor)
        item.box = (handle == "evacipatedBox")
        item.setForeground(QtGui.QBrush(color))
        item.founder = founder
        item.op = op
        item.halfop = halfop
        item.admin = admin
        item.voice = voice
        self.umodes = ["box", "founder", "admin", "op", "halfop", "voice"]
        self.iconCrap(item)
        self.userlist.addItem(item)
        self.sortUsers()

    def sortUsers(self):
        users = []
        listing = self.userlist.item(0)
        while listing is not None:
            users.append(self.userlist.takeItem(0))
            listing = self.userlist.item(0)
        users.sort(key=lambda x: ((-1 if x.box else (0 if x.founder else (1 if x.admin else (2 if x.op else (3 if x.halfop else (4 if x.voice else 5)))))), x.text()))
        for u in users:
            self.userlist.addItem(u)

    def updateChanModes(self, modes, op):
        if not hasattr(self, 'modes'): self.modes = ""
        chanmodes = list(str(self.modes))
        if chanmodes and chanmodes[0] == "+": chanmodes = chanmodes[1:]
        modes = str(modes)
        if op:
            systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
            chum = self.mainwindow.profile()
            opchum = PesterProfile(op)
        if modes[0] == "+":
            for m in modes[1:]:
                if m not in chanmodes:
                    chanmodes.extend(m)
            # Make +c (disable ANSI colours) disable quirks.
            if modes.find("c") >= 0:
                self.chanNoquirks.setChecked(True)
                self.quirksOff.setChecked(True)
                self.applyquirks = False
                if op:
                    msg = chum.memomodemsg(opchum, systemColor, "A No-Quirk zone", True)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
            if modes.find("s") >= 0:
                self.chanHide.setChecked(True)
                if op:
                    msg = chum.memomodemsg(opchum, systemColor, "Secret", True)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
            if modes.find("i") >= 0:
                self.chanInvite.setChecked(True)
                if op:
                    msg = chum.memomodemsg(opchum, systemColor, "Invite-Only", True)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
            if modes.find("m") >= 0:
                self.chanMod.setChecked(True)
                if op:
                    msg = chum.memomodemsg(opchum, systemColor, "Muted", True)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
        elif modes[0] == "-":
            for i in modes[1:]:
                try:
                    chanmodes.remove(i)
                except ValueError:
                    pass
            if modes.find("c") >= 0:
                self.chanNoquirks.setChecked(False)
                if op:
                    msg = chum.memomodemsg(opchum, systemColor, "A No-Quirk zone", False)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
            if modes.find("s") >= 0:
                self.chanHide.setChecked(False)
                if op:
                    msg = chum.memomodemsg(opchum, systemColor, "Secret", False)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
            if modes.find("i") >= 0:
                self.chanInvite.setChecked(False)
                if op:
                    msg = chum.memomodemsg(opchum, systemColor, "Invite-Only", False)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
            if modes.find("m") >= 0:
                self.chanMod.setChecked(False)
                if op:
                    msg = chum.memomodemsg(opchum, systemColor, "Muted", False)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
        chanmodes.sort()
        self.modes = "+" + "".join(chanmodes)
        if self.mainwindow.advanced:
            t = Template(self.mainwindow.theme["memos/label/text"])
            self.channelLabel.setText(t.safe_substitute(channel=self.channel) + "(%s)" % (self.modes))

    @QtCore.pyqtSlot()
    def sentMessage(self):
        text = str(self.textInput.text())
        if text == "":
            return
        oocDetected = oocre.match(text.strip())
        if self.ooc and not oocDetected:
            text = "(( %s ))" % (text)
        self.history.add(text)
        quirks = self.mainwindow.userprofile.quirks
        lexmsg = lexMessage(text)
        if type(lexmsg[0]) is not mecmd:
            if self.applyquirks and not (self.ooc or oocDetected):
                lexmsg = quirks.apply(lexmsg)
            initials = self.mainwindow.profile().initials()
            colorcmd = self.mainwindow.profile().colorcmd()
            clientMsg = [colorBegin("<c={0},{1},{2}>".format(*colorcmd[:3]), "{0},{1},{2}".format(*colorcmd[:3])),
                         "%s: " % (initials)] + lexmsg + [colorEnd("</c>")]
            # account for TC's parsing error
            serverMsg = [colorBegin("<c={0},{1},{2}>".format(*colorcmd[:3]), "{0},{1},{2}".format(*colorcmd[:3])),
                         "%s: " % (initials)] + lexmsg + [colorEnd("</c>"), " "]
        else:
            clientMsg = copy(lexmsg)
            serverMsg = copy(lexmsg)

        self.addMessage(clientMsg, True)
        serverText = convertTags(serverMsg, "ctag")
        self.messageSent.emit(serverText, self.title())

        self.textInput.setText("")
    @QtCore.pyqtSlot('QString')
    def namesUpdated(self, channel):
        c = str(channel)
        if c.lower() != self.channel.lower(): return
        # get namesdb
        namesdb = self.mainwindow.namesdb
        # reload names
        self.userlist.clear()
        for n in self.mainwindow.namesdb[self.channel]:
            self.addUser(n)
    @QtCore.pyqtSlot('QString', 'QString')
    def modesUpdated(self, channel, modes):
        c = str(channel)
        if c.lower() == self.channel.lower():
            self.updateChanModes(modes, None)

    @QtCore.pyqtSlot('QString')
    def closeInviteOnly(self, channel):
        c = str(channel)
        if c.lower() == self.channel.lower():
            self.mainwindow.inviteOnlyChan.disconnect(self.closeInviteOnly)
            if self.parent():
                print(self.channel)
                i = self.parent().tabIndices[self.channel]
                self.parent().tabClose(i)
            else:
                self.close()
            msgbox = QtWidgets.QMessageBox()
            msgbox.setText("%s: Invites only!" % (c))
            msgbox.setInformativeText("This channel is invite-only. You must get an invitation from someone on the inside before entering.")
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            ret = msgbox.exec_()

    def quirkDisable(self, op, msg):
        chums = self.userlist.findItems(op, QtCore.Qt.MatchFlags(QtCore.Qt.MatchFixedString))
        for c in chums:
            if c.op:
                if msg == self.mainwindow.profile().handle:
                    self.quirksOff.setChecked(True)
                    self.applyquirks = False
                    systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
                    chum = self.mainwindow.profile()
                    opchum = PesterProfile(op)
                    msg = chum.memoquirkkillmsg(opchum, systemColor)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)

    def chumOPstuff(self, h, op):
        chum = PesterProfile(h)
        if h == self.mainwindow.profile().handle:
            chum = self.mainwindow.profile()
        opchum = PesterProfile(op)
        return (chum, opchum)
    def iconCrap(self, c, down=True):
        for m in (self.umodes if down else reversed(self.umodes)):
            if eval("c."+m):
                if m == "box":
                    icon = PesterIcon("smilies/box.png")
                else:
                    icon = PesterIcon(self.mainwindow.theme["memos/"+m+"/icon"])
                c.setIcon(icon)
                return
        icon = QtGui.QIcon()
        c.setIcon(icon)

    @QtCore.pyqtSlot()
    def dumpNetsplit(self):
        if (len(self.netsplit) > 0):
            chum = self.mainwindow.profile()
            systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
            msg = chum.memonetsplitmsg(systemColor, self.netsplit)
            self.textArea.append(convertTags(msg))
            self.mainwindow.chatlog.log(self.channel, msg)
        del self.netsplit

    @QtCore.pyqtSlot('QString', 'QString', 'QString')
    def userPresentChange(self, handle, channel, update):
        h = str(handle)
        c = str(channel)
        update = str(update)
        if update[0:4] == "kick": # yeah, i'm lazy.
            l = update.split(":")
            update = l[0]
            op = l[1]
            reason = ":".join(l[2:])
        if update == "nick":
            l = h.split(":")
            oldnick = l[0]
            newnick = l[1]
            h = oldnick
        if update in ["join","left", "kick"] and c.lower() != self.channel.lower():
            return
        chums = self.userlist.findItems(h, QtCore.Qt.MatchFlags(QtCore.Qt.MatchFixedString))
        systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
        # print exit
        if update in ("quit", "left", "nick", "netsplit"):
            for c in chums:
                chum = PesterProfile(h)
                self.userlist.takeItem(self.userlist.row(c))
                allinitials = []
                msg = chum.memoclosemsg(systemColor, allinitials, self.mainwindow.theme["convo/text/closememo"])
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
                if update == "nick":
                    self.addUser(newnick)
                    newchums = self.userlist.findItems(newnick, QtCore.Qt.MatchFlags(QtCore.Qt.MatchFixedString))
                    for nc in newchums:
                        for c in chums:
                            nc.founder = c.founder
                            nc.op      = c.op
                            nc.halfop  = c.halfop
                            nc.admin   = c.admin
                            self.iconCrap(nc)
                    self.sortUsers()
        elif update == "kick":
            if len(chums) == 0:
                return
            c = chums[0]
            chum = PesterProfile(h)
            if h == self.mainwindow.profile().handle:
                chum = self.mainwindow.profile()
            allinitials = []
            opchum = PesterProfile(op)
            msg = chum.memobanmsg(opchum, systemColor, allinitials, reason)
            self.textArea.append(convertTags(msg))
            self.mainwindow.chatlog.log(self.channel, msg)

            if chum is self.mainwindow.profile():
                # are you next?
                msgbox = QtWidgets.QMessageBox()
                msgbox.setText(self.mainwindow.theme["convo/text/kickedmemo"])
                msgbox.setInformativeText("press 0k to rec0nnect or cancel to absc0nd")
                msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                ret = msgbox.exec_()
                if ret == QtWidgets.QMessageBox.Ok:
                    self.userlist.clear()
                    self.mainwindow.joinChannel.emit(self.channel)
                    me = self.mainwindow.profile()
                    msg = me.memoopenmsg(systemColor, self.mainwindow.theme["convo/text/openmemo"], self.channel)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
                elif ret == QtWidgets.QMessageBox.Cancel:
                    if self.parent():
                        i = self.parent().tabIndices[self.channel]
                        self.parent().tabClose(i)
                    else:
                        self.close()
            else:
                # i warned you about those stairs bro
                self.userlist.takeItem(self.userlist.row(c))
        elif update == "join":
            self.addUser(h)
    @QtCore.pyqtSlot('QString', 'QString', int, 'QString')
    def userRankChange(self, handle, channel, rank, actingHandle):
        logging.info("SETTING RANK: {} {} {} {}".format(handle, channel, rank, actingHandle))
        logging.info("USERLIST IS: {}".format(self.userlist))
        chums = self.userlist.findItems(handle, QtCore.Qt.MatchFlags(QtCore.Qt.MatchFixedString))
        logging.info("CHUMS IS: {}".format(chums))
        if rank == 4:
            for c in chums:
                c.founder = True
                self.iconCrap(c)
            self.sortUsers()
        else: 
            for c in chums:
                c.founder = False
                self.iconCrap(c)
        if rank >= 3:
            if self.mainwindow.config.opvoiceMessages() and actingHandle:
                (chum, opchum) = self.chumOPstuff(handle, actingHandle)
                msg = chum.memoopmsg(opchum, systemColor)
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
            for c in chums:
                c.op = True
                self.iconCrap(c)
                if str(c.text()) == self.mainwindow.profile().handle:
                    self.userlist.optionsMenu.addAction(self.opAction)
                    self.userlist.optionsMenu.addAction(self.voiceAction)
                    self.userlist.optionsMenu.addAction(self.banuserAction)
                    self.userlist.optionsMenu.addAction(self.quirkDisableAction)
            self.sortUsers()
        else:
            for c in chums:
                c.op = False
                self.iconCrap(c)
        if rank == 2:
            if self.mainwindow.config.opvoiceMessages() and actingHandle:
                (chum, opchum) = self.chumOPstuff(handle, actingHandle)
                msg = chum.memoopmsg(opchum, systemColor)
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
            for c in chums:
                c.halfop = True
                self.iconCrap(c)
                if str(c.text()) == self.mainwindow.profile().handle:
                    self.userlist.optionsMenu.addAction(self.banuserAction)
                    self.userlist.optionsMenu.addAction(self.quirkDisableAction)
                    self.userlist.optionsMenu.removeAction(self.opAction)
                    self.userlist.optionsMenu.removeAction(self.voiceAction)
        else:
            for c in chums:
                c.halfop = False
                self.iconCrap(c)
        if rank == 1:
            if self.mainwindow.config.opvoiceMessages() and actingHandle:
                (chum, opchum) = self.chumOPstuff(handle, actingHandle)
                msg = chum.memovoicemsg(opchum, systemColor)
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
            for c in chums:
                c.voice = True
                self.iconCrap(c)
                if str(c.text()) == self.mainwindow.profile().handle:
                    self.userlist.optionsMenu.removeAction(self.banuserAction)
                    self.userlist.optionsMenu.removeAction(self.quirkDisableAction)
                    self.userlist.optionsMenu.removeAction(self.opAction)
                    self.userlist.optionsMenu.removeAction(self.voiceAction)
        else:
            for c in chums:
                c.voice = False
                self.iconCrap(c)
        if not rank:
            if str(c.text()) == self.mainwindow.profile().handle:
                self.userlist.optionsMenu.removeAction(self.banuserAction)
                self.userlist.optionsMenu.removeAction(self.quirkDisableAction)
                self.userlist.optionsMenu.removeAction(self.opAction)
                self.userlist.optionsMenu.removeAction(self.voiceAction)
        self.sortUsers()

    @QtCore.pyqtSlot()
    def addChumSlot(self):
        if not self.userlist.currentItem():
            return
        currentChum = PesterProfile(str(self.userlist.currentItem().text()))
        self.mainwindow.addChum(currentChum)
    @QtCore.pyqtSlot()
    def banSelectedUser(self):
        if not self.userlist.currentItem():
            return
        currentHandle = str(self.userlist.currentItem().text())
        (reason, ok) = QtWidgets.QInputDialog.getText(self, "Ban User", "Enter the reason you are banning this user (optional):")
        if ok:
            self.mainwindow.kickUser.emit("%s:%s" % (currentHandle, reason), self.channel)
    @QtCore.pyqtSlot()
    def opSelectedUser(self):
        if not self.userlist.currentItem():
            return
        currentHandle = str(self.userlist.currentItem().text())
        self.mainwindow.setChannelMode.emit(self.channel, "+o", currentHandle)
    @QtCore.pyqtSlot()
    def voiceSelectedUser(self):
        if not self.userlist.currentItem():
            return
        currentHandle = str(self.userlist.currentItem().text())
        self.mainwindow.setChannelMode.emit(self.channel, "+v", currentHandle)
    @QtCore.pyqtSlot()
    def killQuirkUser(self):
        if not self.userlist.currentItem():
            return
        currentHandle = str(self.userlist.currentItem().text())
        self.mainwindow.killSomeQuirks.emit(self.channel, currentHandle)

    @QtCore.pyqtSlot()
    def openChumLogs(self):
        currentChum = self.channel
        self.mainwindow.chumList.pesterlogviewer = PesterLogViewer(currentChum, self.mainwindow.config, self.mainwindow.theme, self.mainwindow)
        self.mainwindow.chumList.pesterlogviewer.rejected.connect(self.mainwindow.chumList.closeActiveLog)
        self.mainwindow.chumList.pesterlogviewer.show()
        self.mainwindow.chumList.pesterlogviewer.raise_()
        self.mainwindow.chumList.pesterlogviewer.activateWindow()

    @QtCore.pyqtSlot()
    def inviteChums(self):
        if not hasattr(self, 'invitechums'):
            self.invitechums = None
        if not self.invitechums:
            (chum, ok) = QtWidgets.QInputDialog.getText(self, "Invite to Chat", "Enter the chumhandle of the user you'd like to invite:")
            if ok:
                chum = str(chum)
                self.mainwindow.inviteChum.emit(chum, self.channel)
            self.invitechums = None

    @QtCore.pyqtSlot(bool)
    def noquirksChan(self, on):
        x = ["-","+"][on]
        self.mainwindow.setChannelMode.emit(self.channel, x+"c", "")
    @QtCore.pyqtSlot(bool)
    def hideChan(self, on):
        x = ["-","+"][on]
        self.mainwindow.setChannelMode.emit(self.channel, x+"s", "")
    @QtCore.pyqtSlot(bool)
    def inviteChan(self, on):
        x = ["-","+"][on]
        self.mainwindow.setChannelMode.emit(self.channel, x+"i", "")
    @QtCore.pyqtSlot(bool)
    def modChan(self, on):
        x = ["-","+"][on]
        self.mainwindow.setChannelMode.emit(self.channel, x+"m", "")

    def closeEvent(self, event):
        self.mainwindow.waitingMessages.messageAnswered(self.channel)
        self.windowClosed.emit(self.title())

    windowClosed = QtCore.pyqtSignal('QString')


# for old times sake
timelist = ["0:00", "0:01", "0:02", "0:04", "0:06", "0:10", "0:14", "0:22", "0:30", "0:41", "1:00", "1:34", "2:16", "3:14", "4:13", "4:20", "5:25", "6:12", "7:30", "8:44", "10:25", "11:34", "14:13", "16:12", "17:44", "22:22", "25:10", "33:33", "42:00", "43:14", "50:00", "62:12", "75:00", "88:44", "100", "133", "143", "188", "200", "222", "250", "314", "333", "413", "420", "500", "600", "612", "888", "1000", "1025"]

# timedlist = [timedelta(0), timedelta(0, 60), timedelta(0, 120), timedelta(0, 240), timedelta(0, 360), timedelta(0, 600), timedelta(0, 840), timedelta(0, 1320), timedelta(0, 1800), timedelta(0, 2460), timedelta(0, 3600), timedelta(0, 5640), timedelta(0, 8160), timedelta(0, 11640), timedelta(0, 15180), timedelta(0, 15600), timedelta(0, 19500), timedelta(0, 22320), timedelta(0, 27000), timedelta(0, 31440), timedelta(0, 37500), timedelta(0, 41640), timedelta(0, 51180), timedelta(0, 58320), timedelta(0, 63840), timedelta(0, 80520), timedelta(1, 4200), timedelta(1, 34380), timedelta(1, 64800), timedelta(1, 69240), timedelta(2, 7200), timedelta(2, 51120), timedelta(3, 10800), timedelta(3, 60240), timedelta(4, 14400), timedelta(5, 46800), timedelta(5, 82800), timedelta(7, 72000), timedelta(8, 28800), timedelta(9, 21600), timedelta(10, 36000), timedelta(13, 7200), timedelta(13, 75600), timedelta(17, 18000), timedelta(17, 43200), timedelta(20, 72000), timedelta(25), timedelta(25, 43200), timedelta(37), timedelta(41, 57600), timedelta(42, 61200)]


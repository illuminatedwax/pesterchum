from string import Template
import re
from PyQt4 import QtGui, QtCore
from datetime import time, timedelta, datetime

from dataobjs import PesterProfile, Mood
from generic import PesterIcon
from convo import PesterConvo, PesterInput, PesterText, PesterTabWindow
from parsetools import convertTags, escapeBrackets, addTimeInitial, timeProtocol

def delta2txt(d, format="pc"):
    if format == "pc":
        sign = "+" if d >= timedelta(0) else "-"
    else:
        if d == timedelta(0):
            return "i"
        sign = "F" if d >= timedelta(0) else "P"
    d = abs(d)
    totalminutes = (d.days*86400 + d.seconds) // 60
    hours = totalminutes // 60
    leftovermins = totalminutes % 60
    if hours < 100:
        if format == "pc":
            return "%s%d:%02d" % (sign, hours, leftovermins)
        else:
            return "%s%02d:%02d" % (sign, hours, leftovermins)
    else:
        if format == "pc":
            return "%s%d" % (sign, hours)
        else:
            return "%s%02d:%02d" % (sign, hours, leftovermins)

def txt2delta(txt):
    sign = 1
    if txt[0] == '+':
        txt = txt[1:]
    elif txt[0] == '-':
        sign = -1
        txt = txt[1:]
    l = txt.split(":")
    try:
        h = int(l[0])
        m = 0
        if len(l) > 1:
            m = int(l[1])
        timed = timedelta(0, h*3600+m*60)
    except ValueError:
        timed = timedelta(0)
    return sign*timed

def pcfGrammar(td):
    if td > timedelta(0):
        when = "FROM NOW"
        temporal = "FUTURE"
        pcf = "F"
    elif td < timedelta(0):
        when = "AGO"
        temporal = "PAST"
        pcf = "P"
    else:
        when = "RIGHT NOW"
        temporal = "CURRENT"
        pcf = "C"
    return (temporal, pcf, when)

class TimeGrammar(object):
    def __init__(self, temporal, pcf, when, number="0"):
        self.temporal = temporal
        self.pcf = pcf
        self.when = when
        if number == "0" or number == 0:
            self.number = ""
        else:
            self.number = str(number)

class TimeTracker(list):
    def __init__(self, time=None):
        self.timerecord = {"P": [], "F": []}
        if time is not None:
            self.append(time)
            self.current=0
            self.addRecord(time)
        else:
            self.current=-1
    def addTime(self, timed):
        try:
            i = self.index(timed)
            self.current = i
            return True
        except ValueError:
            self.current = len(self)
            self.append(timed)
            self.addRecord(timed)
            return False
    def prevTime(self):
        i = self.current
        i = (i - 1) % len(self)
        return self[i]
    def nextTime(self):
        i = self.current
        i = (i + 1) % len(self)
        return self[i]
    def setCurrent(self, timed):
        self.current = self.index(timed)
    def addRecord(self, timed):
        (temporal, pcf, when) = pcfGrammar(timed - timedelta(0))
        if pcf == "C":
            return
        if timed in self.timerecord[pcf]:
            return
        self.timerecord[pcf].append(timed)
    def getRecord(self, timed):
        (temporal, pcf, when) = pcfGrammar(timed - timedelta(0))
        if pcf == "C":
            return 0
        if len(self.timerecord[pcf]) > 1:
            return self.timerecord[pcf].index(timed)+1
        else:
            return 0
    def removeTime(self, timed):
        try:
            self.pop(self.index(timed))
            self.current = len(self)-1
            return True
        except ValueError:
            return None
    def getTime(self):
        if self.current >= 0: 
            return self[self.current]
        else:
            return None
    def getGrammar(self):
        timed = self.getTime()
        return self.getGrammarTime(timed)
    def getGrammarTime(self, timed):
        mytime = timedelta(0)
        (temporal, pcf, when) = pcfGrammar(timed - mytime)
        if timed == mytime:
            return TimeGrammar(temporal, pcf, when, 0)
        return TimeGrammar(temporal, pcf, when, self.getRecord(timed))

class TimeInput(QtGui.QLineEdit):
    def __init__(self, timeslider, parent):
        QtGui.QLineEdit.__init__(self, parent)
        self.timeslider = timeslider
        self.setText("+0:00")
        self.connect(self.timeslider, QtCore.SIGNAL('valueChanged(int)'),
                     self, QtCore.SLOT('setTime(int)'))
        self.connect(self, QtCore.SIGNAL('editingFinished()'),
                    self, QtCore.SLOT('setSlider()'))
    @QtCore.pyqtSlot(int)
    def setTime(self, sliderval):
        self.setText(self.timeslider.getTime())
    @QtCore.pyqtSlot()
    def setSlider(self):
        value = unicode(self.text())
        timed = txt2delta(value)
        sign = 1 if timed >= timedelta(0) else -1
        abstimed = abs(txt2delta(value))
        index = 50
        for i, td in enumerate(timedlist):
            if abstimed < td:
                index = i-1
                break
        self.timeslider.setValue(sign*index)
        text = delta2txt(timed)
        self.setText(text)

class TimeSlider(QtGui.QSlider):
    def __init__(self, orientation, parent):
        QtGui.QSlider.__init__(self, orientation, parent)
        self.setTracking(True)
        self.setMinimum(-50)
        self.setMaximum(50)
        self.setValue(0)
        self.setPageStep(1)
    def getTime(self):
        time = timelist[abs(self.value())]
        sign = "+" if self.value() >= 0 else "-"
        return sign+time
    def mouseDoubleClickEvent(self, event):
        self.setValue(0)

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
        QtGui.QTextEdit.__init__(self, parent)
        self.setStyleSheet(theme["memos/textarea/style"])
        self.setReadOnly(True)
        self.setMouseTracking(True)
    def addMessage(self, text, chum):
        parent = self.parent()
        window = parent.mainwindow
        me = window.profile()
        msg = unicode(text)
        chumdb = window.chumdb
        if chum is not me: # SO MUCH WH1T3SP4C3 >:]
            mobj = _ctag_begin.match(text) # get color from tag
            if mobj:
                try:
                    color = QtGui.QColor(*[int(c) for c in mobj.group(1).split(",")])
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
        if chum is not me:
            if parent.times.has_key(chum.handle):
                time = parent.times[chum.handle]
            else:
                # new chum! time current
                newtime = timedelta(0)
                time = TimeTracker(newtime)
                parent.times[chum.handle] = time
                timeGrammar = time.getGrammar()
                self.append(convertTags(chum.memojoinmsg(systemColor, time.getTime(), timeGrammar, window.theme["convo/text/joinmemo"])))
        else:
            time = parent.time

        if msg[0:3] == "/me" or msg[0:13] == "PESTERCHUM:ME":
            if msg[0:3] == "/me":
                start = 3
            else:
                start = 13
            space = msg.find(" ")
            msg = chum.memsg(systemColor, msg[start:space], msg[space:], time=time.getGrammar())
            window.chatlog.log(parent.channel, convertTags(msg, "bbcode"))
            self.append(convertTags(msg))
        else:
            if chum is not me:
                msg = addTimeInitial(msg, parent.times[chum.handle].getGrammar())
            msg = escapeBrackets(msg)
            self.append(convertTags(msg))
            window.chatlog.log(parent.channel, convertTags(msg, "bbcode"))
            
        
    def changeTheme(self):
        pass

class MemoInput(PesterInput):
    def __init__(self, theme, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setStyleSheet(theme["memos/input/style"])
    def changeTheme(self, theme):
        self.setStyleSheet(theme["memos/input/style"])

class PesterMemo(PesterConvo):
    def __init__(self, channel, timestr, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.channel = channel
        self.mainwindow = mainwindow
        self.time = TimeTracker(txt2delta(timestr))
        self.setWindowTitle(channel)
        self.channelLabel = QtGui.QLabel(self)
        self.channelLabel.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding))

        self.textArea = MemoText(self.mainwindow.theme, self)
        self.textInput = MemoInput(self.mainwindow.theme, self)
        self.textInput.setFocus()

        self.userlist = QtGui.QListWidget(self)
        self.userlist.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding))

        self.timeslider = TimeSlider(QtCore.Qt.Horizontal, self)
        self.timeinput = TimeInput(self.timeslider, self)
        self.timeinput.setText(timestr)
        self.timeinput.setSlider()
        self.timetravel = QtGui.QPushButton("GO", self)
        self.timeclose = QtGui.QPushButton("CLOSE", self)
        self.timeswitchl = QtGui.QPushButton(self)
        self.timeswitchr = QtGui.QPushButton(self)

        self.connect(self.timetravel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('sendtime()'))
        self.connect(self.timeclose, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('smashclock()'))
        self.connect(self.timeswitchl, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('prevtime()'))
        self.connect(self.timeswitchr, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('nexttime()'))

        self.times = {}

        self.initTheme(self.mainwindow.theme)

        # connect
        self.connect(self.textInput, QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('sentMessage()'))

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.textArea)
        layout_0.addWidget(self.textInput)

        layout_1 = QtGui.QHBoxLayout()
        layout_1.addLayout(layout_0)
        layout_1.addWidget(self.userlist)

#        layout_1 = QtGui.QGridLayout()
#        layout_1.addWidget(self.timeslider, 0, 1, QtCore.Qt.AlignHCenter)
#        layout_1.addWidget(self.timeinput, 1, 0, 1, 3)
        layout_2 = QtGui.QHBoxLayout()
        layout_2.addWidget(self.timeslider)
        layout_2.addWidget(self.timeinput)
        layout_2.addWidget(self.timetravel)
        layout_2.addWidget(self.timeclose)
        layout_2.addWidget(self.timeswitchl)
        layout_2.addWidget(self.timeswitchr)
        self.layout = QtGui.QVBoxLayout()

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
        timeGrammar = self.time.getGrammar()
        systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
        self.textArea.append(convertTags(p.memoopenmsg(systemColor, self.time.getTime(), timeGrammar, self.mainwindow.theme["convo/text/openmemo"], self.channel)))

        self.newmessage = False

    def title(self):
        return self.channel
    def icon(self):
        return PesterIcon(self.mainwindow.theme["memos/memoicon"])

    def sendTimeInfo(self, newChum=False):
        if newChum:
            self.messageSent.emit("PESTERCHUM:TIME>%s" % (delta2txt(self.time.getTime(), "server")+"i"),
                                  self.title())
        else:
            self.messageSent.emit("PESTERCHUM:TIME>%s" % (delta2txt(self.time.getTime(), "server")),
                                  self.title())

    def updateMood(self):
        pass
    def updateBlocked(self):
        pass
    def updateColor(self, handle, color):
        chums = self.userlist.findItems(handle, QtCore.Qt.MatchFlags(0))
        for c in chums:
            c.setTextColor(color)
    def addMessage(self, text, handle):
        if type(handle) is bool:
            chum = self.mainwindow.profile()
        else:
            chum = PesterProfile(handle)
            self.notifyNewMessage()
        self.textArea.addMessage(text, chum)

    def initTheme(self, theme):
        memo = theme["memos"]
        self.resize(*memo["size"])
        self.setStyleSheet(memo["style"])
        self.setWindowIcon(PesterIcon(theme["memos/memoicon"]))

        t = Template(theme["memos/label/text"])
        self.channelLabel.setText(t.safe_substitute(channel=self.channel))
        self.channelLabel.setStyleSheet(theme["memos/label/style"])
        self.channelLabel.setAlignment(self.aligndict["h"][theme["memos/label/align/h"]] | self.aligndict["v"][theme["memos/label/align/v"]])
        self.channelLabel.setMaximumHeight(theme["memos/label/maxheight"])
        self.channelLabel.setMinimumHeight(theme["memos/label/minheight"])

        self.userlist.setStyleSheet(theme["memos/userlist/style"])
        self.userlist.setFixedWidth(theme["memos/userlist/width"])

        self.timeinput.setFixedWidth(theme["memos/time/text/width"])
        self.timeinput.setStyleSheet(theme["memos/time/text/style"])
        slidercss = "QSlider { %s } QSlider::groove { %s } QSlider::handle { %s }" % (theme["memos/time/slider/style"], theme["memos/time/slider/groove"], theme["memos/time/slider/handle"])
        self.timeslider.setStyleSheet(slidercss) 

        larrow = PesterIcon(self.mainwindow.theme["memos/time/arrows/left"])
        self.timeswitchl.setIcon(larrow)
        self.timeswitchl.setIconSize(larrow.realsize())
        self.timeswitchl.setStyleSheet(self.mainwindow.theme["memos/time/arrows/style"])
        self.timetravel.setStyleSheet(self.mainwindow.theme["memos/time/buttons/style"])
        self.timeclose.setStyleSheet(self.mainwindow.theme["memos/time/buttons/style"])

        rarrow = PesterIcon(self.mainwindow.theme["memos/time/arrows/right"])
        self.timeswitchr.setIcon(rarrow)
        self.timeswitchr.setIconSize(rarrow.realsize())
        self.timeswitchr.setStyleSheet(self.mainwindow.theme["memos/time/arrows/style"])


    def changeTheme(self, theme):
        self.initTheme(theme)
        self.textArea.changeTheme(theme)
        self.textInput.changeTheme(theme)
        margins = theme["memos/margins"]
        self.layout.setContentsMargins(margins["left"], margins["top"],
                                  margins["right"], margins["bottom"])

    def addUser(self, handle):
        chumdb = self.mainwindow.chumdb
        defaultcolor = QtGui.QColor("black")
        op = False
        if handle[0] == '@':
            op = True
            handle = handle[1:]
        item = QtGui.QListWidgetItem(handle)
        if handle == self.mainwindow.profile().handle:
            color = self.mainwindow.profile().color
        else:
            color = chumdb.getColor(handle, defaultcolor)
        item.setTextColor(color)
        self.userlist.addItem(item)

    def timeUpdate(self, handle, cmd):
        window = self.mainwindow
        chum = PesterProfile(handle)
        systemColor = QtGui.QColor(window.theme["memos/systemMsgColor"])
        close = None
        # old TC command?
        try:
            secs = int(cmd)
            time = datetime.fromtimestamp(secs)
            timed = time - datetime.now()
            s = (timed.seconds // 60)*60
            timed = timedelta(timed.days, s)
        except ValueError:
            if cmd == "i":
                timed = timedelta(0)
            else:
                if cmd[len(cmd)-1] == 'c':
                    close = timeProtocol(cmd)
                    timed = None
                else:
                    timed = timeProtocol(cmd)

        if self.times.has_key(handle):
            if close is not None:
                if close in self.times[handle]:
                    self.times[handle].setCurrent(close)
                    grammar = self.times[handle].getGrammar()
                    self.times[handle].removeTime(close)
                    self.textArea.append(convertTags(chum.memoclosemsg(systemColor, grammar, window.theme["convo/text/closememo"])))
            elif timed not in self.times[handle]:
                self.times[handle].addTime(timed)
                grammar = self.times[handle].getGrammar()
                self.textArea.append(convertTags(chum.memojoinmsg(systemColor, timed, grammar, window.theme["convo/text/joinmemo"])))
            else:
                self.times[handle].setCurrent(timed)
        else:
            if timed is not None:
                ttracker = TimeTracker(timed)
                grammar = ttracker.getGrammar()
                self.textArea.append(convertTags(chum.memojoinmsg(systemColor, timed, grammar, window.theme["convo/text/joinmemo"])))
                self.times[handle] = ttracker

    @QtCore.pyqtSlot()
    def sentMessage(self):
        text = self.textInput.text()
        if text == "":
            return
        grammar = self.time.getGrammar()
        # deal with quirks here
        qtext = self.mainwindow.userprofile.quirks.apply(unicode(text))
        if qtext[0:3] != "/me":
            initials = self.mainwindow.profile().initials()
            colorcmd = self.mainwindow.profile().colorcmd()
            clientText = "<c=%s>%s%s%s: %s</c>" % (colorcmd, grammar.pcf, initials, grammar.number, qtext)
            # account for TC's parsing error
            serverText = "<c=%s>%s: %s</c> " % (colorcmd, initials, qtext)
        else:
            clientText = qtext
            serverText = clientText
        self.textInput.setText("")
        self.addMessage(clientText, True)
        # convert color tags
        text = convertTags(unicode(serverText), "ctag")
        self.messageSent.emit(serverText, self.title())

    @QtCore.pyqtSlot()
    def namesUpdated(self):
        # get namesdb
        namesdb = self.mainwindow.namesdb
        # reload names
        self.userlist.clear()
        for n in self.mainwindow.namesdb[self.channel]:
            self.addUser(n)

    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString, QtCore.QString)
    def userPresentChange(self, handle, channel, update):
        if channel != self.channel:
            return
        chums = self.userlist.findItems(handle, QtCore.Qt.MatchFlags(0))
        h = unicode(handle)
        c = unicode(channel)
        systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
        # print exit
        if update == "quit" or update == "left":
            for c in chums:
                chum = PesterProfile(h)
                self.userlist.takeItem(self.userlist.row(c))
                while self.times[h].getTime() is not None:
                    t = self.times[h]
                    grammar = t.getGrammar()
                    self.textArea.append(convertTags(chum.memoclosemsg(systemColor, grammar, self.mainwindow.theme["convo/text/closememo"])))
                    self.times[h].removeTime(t.getTime())
        elif update == "join":
            self.addUser(h)
            time = self.time.getTime()
            serverText = "PESTERCHUM:TIME>"+delta2txt(time, "server")
            self.messageSent.emit(serverText, self.title())

    def resetSlider(self, time):
        self.timeinput.setText(delta2txt(time))
        self.timeinput.setSlider()
        self.sendtime()

    @QtCore.pyqtSlot()
    def sendtime(self):
        me = self.mainwindow.profile()
        systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
        time = txt2delta(self.timeinput.text())
        present = self.time.addTime(time)
        if not present:
            self.textArea.append(convertTags(me.memojoinmsg(systemColor, time, self.time.getGrammar(), self.mainwindow.theme["convo/text/joinmemo"])))

        serverText = "PESTERCHUM:TIME>"+delta2txt(time, "server")
        self.messageSent.emit(serverText, self.title())
    @QtCore.pyqtSlot()
    def smashclock(self):
        me = self.mainwindow.profile()
        time = txt2delta(self.timeinput.text())
        removed = self.time.removeTime(time)
        if removed:
            grammar = self.time.getGrammarTime(time)
            systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
            self.textArea.append(convertTags(me.memoclosemsg(systemColor, grammar, self.mainwindow.theme["convo/text/closememo"])))

        newtime = self.time.getTime()
        if newtime is None:
            newtime = timedelta(0)
        self.resetSlider(newtime)
    @QtCore.pyqtSlot()
    def prevtime(self):
        time = self.time.prevTime()
        self.time.setCurrent(time)
        self.resetSlider(time)
    @QtCore.pyqtSlot()
    def nexttime(self):
        time = self.time.nextTime()
        self.time.setCurrent(time)
        self.resetSlider(time)

    def closeEvent(self, event):
        self.mainwindow.waitingMessages.messageAnswered(self.channel)
        self.windowClosed.emit(self.title())

    windowClosed = QtCore.pyqtSignal(QtCore.QString)


timelist = ["0:00", "0:01", "0:02", "0:04", "0:06", "0:10", "0:14", "0:22", "0:30", "0:41", "1:00", "1:34", "2:16", "3:14", "4:13", "4:20", "5:25", "6:12", "7:30", "8:44", "10:25", "11:34", "14:13", "16:12", "17:44", "22:22", "25:10", "33:33", "42:00", "43:14", "50:00", "62:12", "75:00", "88:44", "100", "133", "143", "188", "200", "222", "250", "314", "333", "413", "420", "500", "600", "612", "888", "1000", "1025"]

timedlist = [timedelta(0), timedelta(0, 60), timedelta(0, 120), timedelta(0, 240), timedelta(0, 360), timedelta(0, 600), timedelta(0, 840), timedelta(0, 1320), timedelta(0, 1800), timedelta(0, 2460), timedelta(0, 3600), timedelta(0, 5640), timedelta(0, 8160), timedelta(0, 11640), timedelta(0, 15180), timedelta(0, 15600), timedelta(0, 19500), timedelta(0, 22320), timedelta(0, 27000), timedelta(0, 31440), timedelta(0, 37500), timedelta(0, 41640), timedelta(0, 51180), timedelta(0, 58320), timedelta(0, 63840), timedelta(0, 80520), timedelta(1, 4200), timedelta(1, 34380), timedelta(1, 64800), timedelta(1, 69240), timedelta(2, 7200), timedelta(2, 51120), timedelta(3, 10800), timedelta(3, 60240), timedelta(4, 14400), timedelta(5, 46800), timedelta(5, 82800), timedelta(7, 72000), timedelta(8, 28800), timedelta(9, 21600), timedelta(10, 36000), timedelta(13, 7200), timedelta(13, 75600), timedelta(17, 18000), timedelta(17, 43200), timedelta(20, 72000), timedelta(25), timedelta(25, 43200), timedelta(37), timedelta(41, 57600), timedelta(42, 61200)]

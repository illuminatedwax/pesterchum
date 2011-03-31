from PyQt4 import QtGui, QtCore
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import logging
import random
import socket

from dataobjs import Mood, PesterProfile
from generic import PesterList

logging.basicConfig(level=logging.INFO)

class PesterIRC(QtCore.QThread):
    def __init__(self, config, window):
        QtCore.QThread.__init__(self)
        self.mainwindow = window
        self.config = config
        self.registeredIRC = False
        self.stopIRC = None
    def IRCConnect(self):
        server = self.config.server()
        port = self.config.port()
        self.cli = IRCClient(PesterHandler, host=server, port=int(port), nick=self.mainwindow.profile().handle, real_name='pcc30', blocking=True, timeout=15)
        self.cli.command_handler.parent = self
        self.cli.command_handler.mainwindow = self.mainwindow
        self.cli.connect()
        self.conn = self.cli.conn()
    def run(self):
        try:
            self.IRCConnect()
        except socket.error, se:
            self.stopIRC = se
            return
        while 1:
            res = True
            try:
                logging.debug("updateIRC()")
                res = self.updateIRC()
            except socket.timeout, se:
                logging.debug("timeout in thread %s" % (self))
                self.cli.close()
                self.stopIRC = se
                return
            except socket.error, se:
                if self.registeredIRC:
                    self.stopIRC = None
                else:
                    self.stopIRC = se
                logging.debug("socket error, exiting thread")
                return
            else:
                if not res:
                    logging.debug("false Yield: %s, returning" % res)
                    return
                
    def setConnected(self):
        self.registeredIRC = True
        self.connected.emit()
    def setConnectionBroken(self):
        logging.debug("setconnection broken")
        self.reconnectIRC()
        #self.brokenConnection = True
    @QtCore.pyqtSlot()
    def updateIRC(self):
        try:
            res = self.conn.next()
        except socket.timeout, se:
            if self.registeredIRC:
                return True
            else:
                raise se
        except socket.error, se:
            raise se
        except StopIteration:
            self.conn = self.cli.conn()
            return True
        else:
            return res
    @QtCore.pyqtSlot()
    def reconnectIRC(self):
        logging.debug("reconnectIRC() from thread %s" % (self))
        self.cli.close()

    @QtCore.pyqtSlot(PesterProfile)
    def getMood(self, *chums):
        self.cli.command_handler.getMood(*chums)
    @QtCore.pyqtSlot(PesterList)
    def getMoods(self, chums):
        self.cli.command_handler.getMood(*chums)        
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString)
    def sendMessage(self, text, handle):
        h = unicode(handle)
        textl = [unicode(text)]
        def splittext(l):
            if len(l[0]) > 400:
                space = l[0].rfind(" ", 0,400)
                if space == -1:
                    space = 400
                a = l[0][0:space]
                b = l[0][space:]
                if len(b) > 0:
                    return [a] + splittext([b])
                else:
                    return [a]
            else:
                return l
        textl = splittext(textl)
        try:
            for t in textl:
                helpers.msg(self.cli, h, t)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString, bool)
    def startConvo(self, handle, initiated):
        h = unicode(handle)
        try:
            if initiated:
                helpers.msg(self.cli, h, "PESTERCHUM:BEGIN")
            helpers.msg(self.cli, h, "COLOR >%s" % (self.mainwindow.profile().colorcmd()))
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString)
    def endConvo(self, handle):
        h = unicode(handle)
        try:
            helpers.msg(self.cli, h, "PESTERCHUM:CEASE")
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot()
    def updateProfile(self):
        me = self.mainwindow.profile()
        handle = me.handle
        try:
            helpers.nick(self.cli, handle)
        except socket.error:
            self.setConnectionBroken()
        self.updateMood()
    @QtCore.pyqtSlot()
    def updateMood(self):
        me = self.mainwindow.profile()
        try:
            helpers.msg(self.cli, "#pesterchum", "MOOD >%d" % (me.mood.value()))
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot()
    def updateColor(self):
        me = self.mainwindow.profile()
        for h in self.mainwindow.convos.keys():
            try:
                helpers.msg(self.cli, h, "COLOR >%s" % (self.mainwindow.profile().colorcmd()))
            except socket.error:
                self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString)
    def blockedChum(self, handle):
        h = unicode(handle)
        try:
            helpers.msg(self.cli, h, "PESTERCHUM:BLOCK")
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString)
    def unblockedChum(self, handle):
        h = unicode(handle)
        try:
            helpers.msg(self.cli, h, "PESTERCHUM:UNBLOCK")
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString)
    def requestNames(self, channel):
        c = unicode(channel)
        try:
            helpers.names(self.cli, c)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot()
    def requestChannelList(self):
        try:
            helpers.channel_list(self.cli)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString)
    def joinChannel(self, channel):
        c = unicode(channel)
        try:
            helpers.join(self.cli, c)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString)
    def leftChannel(self, channel):
        c = unicode(channel)
        try:
            helpers.part(self.cli, c)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString)
    def kickUser(self, handle, channel):
        c = unicode(channel)
        h = unicode(handle)
        try:
            helpers.kick(self.cli, h, c)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString, QtCore.QString)
    def setChannelMode(self, channel, mode, command):
        c = unicode(channel)
        m = unicode(mode)
        cmd = unicode(command)
        if cmd == "":
            cmd = None
        try:
            helpers.mode(self.cli, c, m, cmd)
        except socket.error:
            self.setConnectionBroken()

    moodUpdated = QtCore.pyqtSignal(QtCore.QString, Mood)
    colorUpdated = QtCore.pyqtSignal(QtCore.QString, QtGui.QColor)
    messageReceived = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
    memoReceived = QtCore.pyqtSignal(QtCore.QString, QtCore.QString, QtCore.QString)
    timeCommand = QtCore.pyqtSignal(QtCore.QString, QtCore.QString, QtCore.QString)
    namesReceived = QtCore.pyqtSignal(QtCore.QString, PesterList)
    channelListReceived = QtCore.pyqtSignal(PesterList)
    nickCollision = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
    myHandleChanged = QtCore.pyqtSignal(QtCore.QString)
    connected = QtCore.pyqtSignal()
    userPresentUpdate = QtCore.pyqtSignal(QtCore.QString, QtCore.QString,
                                   QtCore.QString)

class PesterHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        try:
            msg = msg.decode('utf-8')
        except UnicodeDecodeError:
            msg = msg.decode('iso-8859-1', 'ignore')
        # display msg, do other stuff
        if len(msg) == 0:
            return
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
        elif chan[0] == '#':
            if msg[0:16] == "PESTERCHUM:TIME>":
                self.parent.timeCommand.emit(chan, handle, msg[16:])
            else:
                self.parent.memoReceived.emit(chan, handle, msg)
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
        self.parent.setConnected()
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
    def kick(self, opnick, channel, handle, op):
        self.parent.userPresentUpdate.emit(handle, channel, "kick:%s" % (op))
        # ok i shouldnt be overloading that but am lazy
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
    def mode(self, op, channel, mode, handle=""):
        self.parent.userPresentUpdate.emit(handle, channel, mode)
    def nick(self, oldnick, newnick):
        oldhandle = oldnick[0:oldnick.find("!")]
        if oldhandle == self.mainwindow.profile().handle:
            self.parent.myHandleChanged.emit(newnick)
        newchum = PesterProfile(newnick, chumdb=self.mainwindow.chumdb)
        self.parent.moodUpdated.emit(oldhandle, Mood("offline"))
        self.parent.userPresentUpdate.emit("%s:%s" % (oldhandle, newnick), "", "nick")
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

    def liststart(self, server, handle, *info):
        self.channel_list = []
        info = list(info)
        self.channel_field = info.index("Channel") # dunno if this is protocol
        logging.info("---> recv \"CHANNELS: %s " % (self.channel_field))
    def list(self, server, handle, *info):
        channel = info[self.channel_field]
        usercount = info[1]
        if channel not in self.channel_list and channel != "#pesterchum":
            self.channel_list.append((channel, usercount))
        logging.info("---> recv \"CHANNELS: %s " % (channel))
    def listend(self, server, handle, msg):
        pl = PesterList(self.channel_list)
        logging.info("---> recv \"CHANNELS END\"")
        self.parent.channelListReceived.emit(pl)
        self.channel_list = []
    
    def getMood(self, *chums):
        chumglub = "GETMOOD "
        for c in chums:
            chandle = c.handle
            if len(chumglub+chandle) >= 350:
                try:
                    helpers.msg(self.client, "#pesterchum", chumglub)
                except socket.error:
                    self.parent.setConnectionBroken()
                chumglub = "GETMOOD "
            chumglub += chandle
        if chumglub != "GETMOOD ":
            try:
                helpers.msg(self.client, "#pesterchum", chumglub)
            except socket.error:
                self.parent.setConnectionBroken()
            

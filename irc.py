from PyQt4 import QtGui, QtCore
from twisted.internet.protocol import ClientFactory
from twisted.words.protocols.irc import IRCClient
from twisted.internet import reactor
import logging
import random

from dataobjs import Mood, PesterProfile
from generic import PesterList

logging.basicConfig(level=logging.INFO)

class PesterIRC(QtCore.QObject):
    def __init__(self, config, window):
        QtCore.QObject.__init__(self)
        self.mainwindow = window
        self.config = config
    def IRCConnect(self):
        server = self.config.server()
        port = int(self.config.port())
        nick = self.mainwindow.profile()
        self.cli = PesterIRCFactory(nick, self)
        logging.info("---> Logging on...")
        reactor.connectTCP(server, port, self.cli)
        reactor.run()
    def closeConnection(self):
        #logging.info("---> Logging on...")
        # self.cli.close()
        pass
    @QtCore.pyqtSlot(PesterProfile)
    def getMood(self, *chums):
        self.cli.getMood(*chums)
    @QtCore.pyqtSlot(PesterList)
    def getMoods(self, chums):
        self.cli.getMood(*chums)
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString)
    def sendMessage(self, text, handle):
        h = unicode(handle)
        textl = [unicode(text)]
        CMD_LENGTH = 450
        def splittext(l):
            if len(l[0]) > CMD_LENGTH:
                space = l[0].rfind(" ", 0,CMD_LENGTH)
                if space == -1:
                    space = CMD_LENGTH
                a = l[0][0:space]
                b = l[0][space:]
                if len(b) > 0:
                    return [a] + splittext([b])
                else:
                    return [a]
            else:
                return l
        textl = splittext(textl)
        for t in textl:
            self.cli.msg(h, t)
    @QtCore.pyqtSlot(QtCore.QString, bool)
    def startConvo(self, handle, initiated):
        h = unicode(handle)
        if initiated:
            self.cli.msg(h, "PESTERCHUM:BEGIN")
        self.cli.msg(h, "COLOR >%s" % (self.mainwindow.profile().colorcmd()))
    @QtCore.pyqtSlot(QtCore.QString)
    def endConvo(self, handle):
        h = unicode(handle)
        self.cli.msg(h, "PESTERCHUM:CEASE")
    @QtCore.pyqtSlot()
    def updateProfile(self):
        me = self.mainwindow.profile()
        handle = me.handle
        self.cli.setNick(handle)
        self.updateMood()
    @QtCore.pyqtSlot()
    def updateMood(self):
        me = self.mainwindow.profile()
        self.cli.msg("#pesterchum", "MOOD >%d" % (me.mood.value()))
    @QtCore.pyqtSlot()
    def updateColor(self):
        me = self.mainwindow.profile()
        for h in self.mainwindow.convos.keys():
            self.cli.msg(h, "COLOR >%s" % (self.mainwindow.profile().colorcmd()))
    @QtCore.pyqtSlot(QtCore.QString)
    def blockedChum(self, handle):
        h = unicode(handle)
        self.cli.msg(h, "PESTERCHUM:BLOCK")
    @QtCore.pyqtSlot(QtCore.QString)
    def unblockedChum(self, handle):
        h = unicode(handle)
        self.cli.msg(h, "PESTERCHUM:UNBLOCK")
    @QtCore.pyqtSlot(QtCore.QString)
    def requestNames(self, channel):
        c = unicode(channel)
        self.cli.sendMessage("NAMES", c)
    @QtCore.pyqtSlot()
    def requestChannelList(self):
        self.cli.sendMessage("LIST")
    @QtCore.pyqtSlot(QtCore.QString)
    def joinChannel(self, channel):
        c = unicode(channel)
        self.cli.join(c)
    @QtCore.pyqtSlot(QtCore.QString)
    def leftChannel(self, channel):
        c = unicode(channel)
        self.cli.leave(c)
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString)
    def kickUser(self, handle, channel):
        c = unicode(channel)
        h = unicode(handle)
        self.cli.kick(h, c)
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString, QtCore.QString)
    def setChannelMode(self, channel, mode, command):
        c = unicode(channel)
        m = unicode(mode).replace("+", "")
        cmd = unicode(command)
        if cmd == "":
            cmd = None
        self.cli.mode(c, True, m, cmd)
    @QtCore.pyqtSlot()
    def reconnectIRC(self):
        pass

    moodUpdated = QtCore.pyqtSignal(QtCore.QString, Mood)
    colorUpdated = QtCore.pyqtSignal(QtCore.QString, QtGui.QColor)
    messageReceived = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
    memoReceived = QtCore.pyqtSignal(QtCore.QString, QtCore.QString, QtCore.QString)
    timeCommand = QtCore.pyqtSignal(QtCore.QString, QtCore.QString, QtCore.QString)
    namesReceived = QtCore.pyqtSignal(QtCore.QString, PesterList)
    channelListReceived = QtCore.pyqtSignal(PesterList)
    nickCollision = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
    connected = QtCore.pyqtSignal()
    userPresentUpdate = QtCore.pyqtSignal(QtCore.QString, QtCore.QString,
                                          QtCore.QString)


class PesterIRCClient(IRCClient):
    realname = "pcc30"
    username = "pcc30"

    def __init__(self, nick, qobj):
        self.nickname = nick
        self.parent = qobj
        self.mainwindow = qobj.mainwindow
        qobj.irc = self

    def msg(self, user, message):
        logging.info("---> send PRIVMSG %s %s" % (user, message))
        IRCClient.msg(self, user, message)

    def signedOn(self):
        logging.info("---> recv WELCOME")
        self.parent.connected.emit()
        self.join("#pesterchum")
        mychumhandle = self.mainwindow.profile().handle
        mymood = self.mainwindow.profile().mood.value()
        self.msg("#pesterchum", "MOOD >%d" % (mymood))
        
        chums = self.mainwindow.chumList.chums
        self.getMood(*chums)

    def getMood(self, *chums):
        chumglub = "GETMOOD "
        for c in chums:
            chandle = c.handle
            if len(chumglub+chandle) >= 350:
                self.msg("#pesterchum", chumglub)
                chumglub = "GETMOOD "
            chumglub += chandle
        if chumglub != "GETMOOD ":
            self.msg("#pesterchum", chumglub)

    def privmsg(self, nick, chan, msg):
        # do we still need this?
        #msg = msg.decode("utf-8")
        # display msg, do other stuff
        if len(msg) == 0:
            return
        # silently ignore CTCP
        if msg[0] == '\x01':
            return
        handle = nick[0:nick.find("!")]
        logging.info("---> recv PRIVMSG %s :%s" % (handle, msg))
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
                    self.msg("#pesterchum", "MOOD >%d" % (mymood))
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
    
    def irc_ERR_NICKNAMEINUSE(self, prefix, params):
        logging.info("---> recv NICKINUSE %s %s" % (prefix, params))
        newnick = "pesterClient%d" % (random.randint(100,999))
        self.setNick(newnick)
        self.parent.nickCollision.emit(nick, newnick)
    def userQuit(self, nick, reason):
        logging.info("---> recv QUIT %s %s" % (nick, reason))
        handle = nick[0:nick.find("!")]
        self.parent.userPresentUpdate.emit(handle, "", "quit")
        self.parent.moodUpdated.emit(handle, Mood("offline"))
    def userKicked(self, kickee, channel, kicker, msg):
        logging.info("---> recv KICK %s %s %s %s" % (kickee, channel, kicker, msg))
        self.parent.userPresentUpdate.emit(kickee, channel, "kick:%s" % (op))
        # ok i shouldnt be overloading that but am lazy
    def userLeft(self, nick, channel, reason="nanchos"):
        logging.info("---> recv LEFT %s %s" % (nick, channel))
        handle = nick[0:nick.find("!")]
        self.parent.userPresentUpdate.emit(handle, channel, "left")
        if channel == "#pesterchum":
            self.parent.moodUpdated.emit(handle, Mood("offline"))
    def userJoined(self, nick, channel):
        logging.info("---> recv JOIN %s %s" % (nick, channel))
        handle = nick[0:nick.find("!")]
        self.parent.userPresentUpdate.emit(handle, channel, "join")
        if channel == "#pesterchum":
            self.parent.moodUpdated.emit(handle, Mood("chummy"))
    def modeChannel(self, op, channel, set, modes, args):
        logging.info("---> recv MODE %s %s %s %s %s" % (op, channel, set, modes, args))
        if set:
            modes += "+"
        else:
            modes += "-"
        handle = ""
        print args
        self.parent.userPresentUpdate.emit(handle, channel, mode)
    def userRenamed(self, oldnick, newnick):
        logging.info("---> recv RENAME %s %s" % (oldnick, newnick))
        newchum = PesterProfile(newnick, chumdb=self.mainwindow.chumdb)
        self.parent.moodUpdated.emit(oldnick, Mood("offline"))
        self.parent.userPresentUpdate.emit("%s:%s" % (oldnick, newnick), "", "nick")
        if newnick in self.mainwindow.chumList.chums:
            self.getMood(newchum)
    def irc_RPL_NAMREPLY(self, prefix, params):
        logging.info("---> recv NAMREPLY %s %s" % (prefix, params))
        # namelist = names.split(" ")
        # logging.info("---> recv \"NAMES %s: %d names\"" % (channel, len(namelist)))
        # if not hasattr(self, 'channelnames'):
        #     self.channelnames = {}
        # if not self.channelnames.has_key(channel):
        #     self.channelnames[channel] = []
        # self.channelnames[channel].extend(namelist)
    def irc_RPL_ENDOFNAMES(self, prefix, params):
        logging.info("---> recv ENDOFNAMES %s %s" % (prefix, params))
        # namelist = self.channelnames[channel]
        # pl = PesterList(namelist)
        # del self.channelnames[channel]
        # self.parent.namesReceived.emit(channel, pl)
    def irc_RPL_LISTSTART(self, prefix, params):
        logging.info("---> recv LISTSTART %s %s" % (prefix, params))
        # self.channel_list = []
        # info = list(info)
        # self.channel_field = info.index("Channel") # dunno if this is protocol
    def irc_RPL_LIST(self, prefix, params):
        logging.info("---> recv LIST %s %s" % (prefix, params))
        # channel = info[self.channel_field]
        # if channel not in self.channel_list and channel != "#pesterchum":
        #     self.channel_list.append(channel)
    def irc_RPL_LISTEND(self, prefix, params):
        logging.info("---> recv LISTEND %s %s" % (prefix, params))
        # pl = PesterList(self.channel_list)
        # self.parent.channelListReceived.emit(pl)
        # self.channel_list = []
    
class PesterIRCFactory(ClientFactory):
    protocol = PesterIRCClient
    
    def __init__(self, nick, qobj):
        self.irc = self.protocol(nick, qobj)
    def buildProtocol(self, addr=None):
        return self.irc
    def clientConnectionLost(self, conn, reason):
        conn.connect()
    def clientConnectionFailed(self, conn, reason):
        conn.connect()

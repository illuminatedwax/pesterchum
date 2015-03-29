from PyQt5 import QtGui, QtCore
import logging
import random
import socket
from time import time
import functools

import osfc.client
from osfc import protocol

from mood import Mood
from dataobjs import PesterProfile
from generic import PesterList, PesterDict
from version import _pcVersion

import ostools
if ostools.isOSXBundle():
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

HANDLE_LIMIT = 32

class PesterOSFC(QtCore.QThread):
    def __init__(self, config, window):
        QtCore.QThread.__init__(self)
        self.mainwindow = window
        self.config = config
        self.madeConnection = False
        self.stopOSFC = None
        self.connectionid = False
    def OSFCConnect(self):
        server = self.config.server()
        port = self.config.port()
        self.phandler = PesterHandler(self)
        self.cli = osfc.client.OSFC(self.phandler)
        logging.info("---> CONNECTING to {}:{} as {} {}/{}".format(server, port, self.mainwindow.profile().handle, self.mainwindow.username, self.mainwindow.password))
        self.cli.connect(host=server, port=int(port), handle=self.mainwindow.profile().handle, username=self.mainwindow.username, password=self.mainwindow.password)
    def run(self):
        try:
            self.OSFCConnect()
        except socket.error as se:
            self.stopOSFC = se
            return
        try:
            self.cli.process_forever()
        except socket.timeout as se:
            logging.debug("timeout in thread %s" % (self))
            self.cli.close() 
            self.stopOSFC = se
            return
        except socket.error as se:
            if self.madeConnection:
                self.stopOSFC = None
            else:
                self.stopOSFC = se
            logging.debug("socket error, exiting thread")
            return

    def setConnected(self):
        self.madeConnection = True
        self.connected.emit()
    def setConnectionBroken(self):
        logging.debug("setconnection broken")
        self.reconnectOSFC()
        #self.brokenConnection = True
    @QtCore.pyqtSlot()
    def updateOSFC(self):
        try:
            res = next(self.conn)
        except socket.timeout as se:
            if self.madeConnection:
                return True
            else:
                raise se
        except socket.error as se:
            raise se
        except StopIteration:
            self.conn = self.cli.conn()
            return True
        else:
            return res
    @QtCore.pyqtSlot()
    def reconnectOSFC(self):
        logging.debug("reconnectOSFC() from thread %s" % (self))
        self.cli.close()

    @QtCore.pyqtSlot()
    def registerOSFC(self):
        self.cli.register(handle=self.mainwindow.profile().handle, username=self.mainwindow.username, password=self.mainwindow.password)

    @QtCore.pyqtSlot(PesterProfile)
    def addFriend(self, *chums):
        outfriends = {}
        for c in chums:
            outfriends.setdefault(c.group, []).append(c.handle)
        self.cli.send(protocol.friend(outfriends))

    @QtCore.pyqtSlot(PesterProfile)
    def getMood(self, *chums):
        for c in chums:
            chandle = c.handle
            try:
                self.cli.send(protocol.statusreq(handle=chandle))
            except socket.error:
                self.parent.setConnectionBroken()

    @QtCore.pyqtSlot(PesterList)
    def getMoods(self, chums):
        self.getMood(*chums)

    @QtCore.pyqtSlot('QString', 'QString')
    def sendNotice(self, text, handle):
        h = str(handle)
        t = str(text)
        try:
            helpers.notice(self.cli, h, t)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString', 'QString')
    def sendMessage(self, text, handle):
        h = str(handle)
        text = str(text)
        try:
            self.cli.send(protocol.msg(text, handle=h))
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString', 'QString')
    def sendChannel(self, text, channel):
        c = str(channel)
        text = str(text)
        try:
            self.cli.send(protocol.msg(text, channel=c))
        except socket.error:
            self.setConnectionBroken()

    @QtCore.pyqtSlot('QString', bool)
    def startConvo(self, handle, initiated):
        h = str(handle)
        try:
            if initiated:
                self.cli.send(protocol.begin(h))
            self.cli.send(protocol.color(self.mainwindow.profile().colorcmd(), handle=h))
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString')
    def endConvo(self, handle):
        h = str(handle)
        try:
            self.cli.send(protocol.cease(h))
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
        self.mainwindow.closeConversations(True)
        self.mainwindow.doAutoIdentify()
        self.mainwindow.autoJoinDone = False
        self.mainwindow.doAutoJoins()
        self.updateMood()
    @QtCore.pyqtSlot()
    def updateMood(self):
        me = self.mainwindow.profile()
        try:
            self.cli.send(protocol.status(mood=me.mood.value()))
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot()
    def updateColor(self):
        me = self.mainwindow.profile()
        for h in self.mainwindow.convos.keys():
            try:
                self.cli.send(protocol.color(self.mainwindow.profile().colorcmd(), handle=h))
            except socket.error:
                self.setConnectionBroken()
    @QtCore.pyqtSlot('QString')
    def blockedChum(self, handle):
        h = str(handle)
        try:
            helpers.msg(self.cli, h, "PESTERCHUM:BLOCK")
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString')
    def unblockedChum(self, handle):
        h = str(handle)
        try:
            helpers.msg(self.cli, h, "PESTERCHUM:UNBLOCK")
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString')
    def requestUserList(self, pattern): # TODO: limit, list of tags, offset
        try:
            self.cli.send(protocol.who())
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString')
    def requestNames(self, channel):
        c = str(channel)
        try:
            helpers.names(self.cli, c)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot()
    def requestChannelList(self): # TODO: Search
        try:
            self.cli.send(protocol.list())
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString')
    def joinChannel(self, channel):
        c = str(channel)
        try:
            self.cli.send(protocol.join(c)) # TODO: tmp channels, passwords
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString')
    def leftChannel(self, channel):
        c = str(channel)
        try:
            self.cli.send(protocol.part(c))
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString', 'QString')
    def kickUser(self, handle, channel):
        l = handle.split(":")
        c = str(channel)
        h = str(l[0])
        if len(l) > 1:
            reason = str(l[1])
            if len(l) > 2:
              for x in l[2:]:
                reason += str(":") + str(x)
        else:
            reason = ""
        try:
            helpers.kick(self.cli, h, c, reason)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString', 'QString', 'QString')
    def setChannelMode(self, channel, mode, command):
        c = str(channel)
        m = str(mode)
        cmd = str(command)
        if cmd == "":
            cmd = None
        try:
            helpers.mode(self.cli, c, m, cmd)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString')
    def channelNames(self, channel):
        c = str(channel)
        try:
            helpers.names(self.cli, c)
        except socket.error:
            self.setConnectionBroken()
    @QtCore.pyqtSlot('QString', 'QString')
    def inviteChum(self, handle, channel):
        h = str(handle)
        c = str(channel)
        try:
            helpers.invite(self.cli, h, c)
        except socket.error:
            self.setConnectionBroken()

    @QtCore.pyqtSlot()
    def pingServer(self):
        try:
            self.cli.send("PING %s" % int(time()))
        except socket.error:
            self.setConnectionBroken()

    @QtCore.pyqtSlot(bool)
    def setAway(self, away=True):
        try:
            if away:
                self.cli.send("AWAY Idle")
            else:
                self.cli.send("AWAY")
        except socket.error:
            self.setConnectionBroken()

    @QtCore.pyqtSlot('QString', 'QString')
    def killSomeQuirks(self, channel, handle):
        c = str(channel)
        h = str(handle)
        try:
            helpers.ctcp(self.cli, c, "NOQUIRKS", h)
        except socket.error:
            self.setConnectionBroken()

    loginFailed = QtCore.pyqtSignal()
    moodUpdated = QtCore.pyqtSignal('QString', Mood)
    colorUpdated = QtCore.pyqtSignal('QString', QtGui.QColor)
    messageReceived = QtCore.pyqtSignal('QString', 'QString')
    beginReceived = QtCore.pyqtSignal(str)
    memoReceived = QtCore.pyqtSignal('QString', 'QString', 'QString')
    noticeReceived = QtCore.pyqtSignal('QString', 'QString')
    inviteReceived = QtCore.pyqtSignal('QString', 'QString')
    timeCommand = QtCore.pyqtSignal('QString', 'QString', 'QString')
    userListReceived = QtCore.pyqtSignal(PesterList)
    namesReceived = QtCore.pyqtSignal('QString', PesterList)
    channelListReceived = QtCore.pyqtSignal(PesterList)
    friendListReceived = QtCore.pyqtSignal(PesterDict)
    nickCollision = QtCore.pyqtSignal('QString', 'QString')
    myHandleChanged = QtCore.pyqtSignal('QString')
    chanInviteOnly = QtCore.pyqtSignal('QString')
    modesUpdated = QtCore.pyqtSignal('QString', 'QString')
    connected = QtCore.pyqtSignal()
    userPresentUpdate = QtCore.pyqtSignal('QString', 'QString', 'QString')
    userRankUpdate = QtCore.pyqtSignal('QString', 'QString', int, 'QString')
    cannotSendToChan = QtCore.pyqtSignal('QString', 'QString')
    tooManyPeeps = QtCore.pyqtSignal()
    quirkDisable = QtCore.pyqtSignal('QString', 'QString', 'QString')



def _handler(fnc):
    fnc.handler = True
    def error(errfnc):
        fnc.errorHandler = errfnc.__name__
        return errfnc
    fnc.error = error
    return fnc

class PesterHandler(object):
    def __init__(self, parent):
        self.parent = parent

    def get_cmd_handler(self, cmdname):
        ret = getattr(self, cmdname, self.unknownCommand)
        if not getattr(ret, "handler", False):
            return self.unknownCommand
        return ret
    def get_error_handler(self, cmd):
        cmdname = cmd['cmd']
        cmdfunc = getattr(self, cmdname, None)
        if cmdfunc and hasattr(cmdfunc, "errorHandler"):
            ret = getattr(self, cmdfunc.errorHandler, self.unknownError)
        else:
            ret = self.unknownError
        return ret
    def unknownCommand(self, conn, cmd):
        logging.info("---> Unknown response {0}".format(cmd))
    def unknownError(self, conn, cmd):
        logging.info("---> Unknown error {0}".format(cmd))
    @_handler
    def register(self, conn, cmd):
        if cmd.get('connectionid'):
            logging.info("---> Registered! Connection ID {0}".format(cmd['connectionid']))
            logging.info("---> Friends list: {0}".format(cmd['friends']))
            self.parent.connectionid = cmd['connectionid']
            self.parent.setConnected()
            actualHandle = cmd['handle']
            if self.parent.mainwindow.profile().handle != actualHandle:
                self.parent.myHandleChanged.emit(actualHandle)

            mymood = self.parent.mainwindow.profile().mood.value()
            conn.send(protocol.status(mood=mymood))
            if cmd.get('friends'):
                self.parent.friendListReceived.emit(PesterDict(cmd['friends']))
            # TODO: Send default friend list
        else:
            # MAJOR SERVER failure TODO: deal
            pass
    @register.error
    def registerError(self, conn, cmd):
        self.parent.loginFailed.emit()
    @_handler
    def status(self, conn, cmd):
        handle = cmd['handle']
        try:
            mood = Mood(int(cmd.get('mood', 0)))
        except ValueError:
            mood = Mood(0)
        self.parent.moodUpdated.emit(handle, mood)
        # TODO: so much more than mood
        
    @_handler
    def msg(self, conn, cmd):
        handle = cmd.get('sender') # TODO None indicates system msg
        msg = cmd['msg']

        # TODO: msgid
        # TODO: timestamp
        # TODO: sig

        if cmd.get('channel'):
            self.parent.memoReceived.emit(cmd['channel'], handle, msg)
        elif handle == self.parent.mainwindow.profile().handle:
            return
        else:
            self.parent.messageReceived.emit(handle, msg)

    @_handler
    def begin(self, conn, cmd):
        handle = cmd.get('sender')
        self.parent.beginReceived.emit(handle)

    @_handler
    def color(self, conn, cmd):
        try:
            colors = [int(d) for d in cmd['color']]
        except ValueError:
            colors = [0,0,0,255]
        color = QtGui.QColor(*colors)
        handle = cmd['sender']
        self.parent.colorUpdated.emit(handle, color)

    @_handler
    def who(self, conn, cmd):
        handles = PesterList(cmd.get('handles', []))
        if not hasattr(self, 'onlinenames') or cmd.get('start'):
            self.onlinenames = []
        self.onlinenames.append(handles)
        if cmd.get('end'):
            self.parent.userListReceived.emit(handles)

    @_handler
    def list(self, conn, cmd):
        pl = PesterList(cmd.get("channels"))
        logging.info("---> recv \"CHANNELS\"")
        self.parent.channelListReceived.emit(pl)

    @_handler
    def join(self, conn, cmd):
        channel = cmd['channel']
        if cmd.get('handle'):
            handle = cmd.get('handle')
            logging.info("---> recv \"JOIN %s: %s\"" % (handle, channel))
        else:
            handle = cmd.get('tmphandle') # TODO: tmp handles

        self.parent.userPresentUpdate.emit(handle, channel, "join")

    @_handler
    def part(self, conn, cmd):
        channel = cmd['channel']
        if cmd.get('handle'):
            handle = cmd['handle']
        else:
            handle = cmd.get('tmphandle') # TODO: tmp handles
            
        logging.info("---> recv \"PART %s: %s\"" % (handle, channel))
        self.parent.userPresentUpdate.emit(handle, channel, "left")

    @_handler
    def channelinfo(self, conn, cmd):
        channel = cmd['channel']
        names = cmd.get('names', [])
        ranks = cmd.get('ranks', {})
        topic = cmd.get('topic')
        password = bool(cmd.get('password'))
        moderated = bool(cmd.get('moderated'))
        # TODO: roles, rolereq
        # TODO: history?
        invisible = bool(cmd.get('invisible'))
        tags = cmd.get('tags', [])

        pl = PesterList(names)
        self.parent.namesReceived.emit(channel, pl)
        for handle, rank in ranks.items():
            self.parent.userRankUpdate.emit(handle, channel, rank, '')
            pass

    @_handler
    def promote(self, conn, cmd):
        channel = cmd['channel']
        handle = cmd['handle']
        rank = cmd['rank']
        actingHandle = cmd['handle']
        self.parent.userRankUpdate.emit(handle, channel, rank, actingHandle)
        # TODO: ranks

    # TODO: kick/ban

    #### OLD FUNCTIONS

    def notice(self, nick, chan, msg):
        try:
            msg = msg.decode('utf-8')
        except UnicodeDecodeError:
            msg = msg.decode('iso-8859-1', 'ignore')
        handle = nick[0:nick.find("!")]
        logging.info("---> recv \"NOTICE %s :%s\"" % (handle, msg))
        if handle == "ChanServ" and chan == self.parent.mainwindow.profile().handle and msg[0:2] == "[#":
            self.parent.memoReceived.emit(msg[1:msg.index("]")], handle, msg)
        else:
            self.parent.noticeReceived.emit(handle, msg)
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
            handle = nick[0:nick.find("!")]
            logging.info("---> recv \"CTCP %s :%s\"" % (handle, msg[1:-1]))
            if msg[1:-1] == "VERSION":
                helpers.ctcp_reply(self.parent.cli, handle, "VERSION", "Pesterchum %s" % (_pcVersion))
            elif msg[1:-1].startswith("NOQUIRKS") and chan[0] == "#":
                op = nick[0:nick.find("!")]
                self.parent.quirkDisable.emit(chan, msg[10:-1], op)
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
                mychumhandle = self.parent.mainwindow.profile().handle
                mymood = self.parent.mainwindow.profile().mood.value()
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
            if handle == self.parent.mainwindow.profile().handle:
                return
            self.parent.messageReceived.emit(handle, msg)


    def nicknameinuse(self, server, cmd, nick, msg):
        newnick = "pesterClient%d" % (random.randint(100,999))
        helpers.nick(self.client, newnick)
        self.parent.nickCollision.emit(nick, newnick)
    def quit(self, nick, reason):
        handle = nick[0:nick.find("!")]
        logging.info("---> recv \"QUIT %s: %s\"" % (handle, reason))
        if handle == self.parent.mainwindow.randhandler.randNick:
            self.parent.mainwindow.randhandler.setRunning(False)
        server = self.parent.mainwindow.config.server()
        baseserver = server[server.rfind(".", 0, server.rfind(".")):]
        if reason.count(baseserver) == 2:
            self.parent.userPresentUpdate.emit(handle, "", "netsplit")
        else:
            self.parent.userPresentUpdate.emit(handle, "", "quit")
        self.parent.moodUpdated.emit(handle, Mood("offline"))
    def kick(self, opnick, channel, handle, reason):
        op = opnick[0:opnick.find("!")]
        self.parent.userPresentUpdate.emit(handle, channel, "kick:%s:%s" % (op, reason))
        # ok i shouldnt be overloading that but am lazy
    def partx(self, nick, channel, reason="nanchos"):
        handle = nick[0:nick.find("!")]
        logging.info("---> recv \"PART %s: %s\"" % (handle, channel))
        self.parent.userPresentUpdate.emit(handle, channel, "left")
        if channel == "#pesterchum":
            self.parent.moodUpdated.emit(handle, Mood("offline"))
    def joinx(self, nick, channel):
        handle = nick[0:nick.find("!")]
        logging.info("---> recv \"JOIN %s: %s\"" % (handle, channel))
        self.parent.userPresentUpdate.emit(handle, channel, "join")
        if channel == "#pesterchum":
            if handle == self.parent.mainwindow.randhandler.randNick:
                self.parent.mainwindow.randhandler.setRunning(True)
            self.parent.moodUpdated.emit(handle, Mood("chummy"))
    def mode(self, op, channel, mode, *handles):
        if len(handles) <= 0: handles = [""]
        opnick = op[0:op.find("!")]
        if op == channel or channel == self.parent.mainwindow.profile().handle:
            modes = list(self.parent.mainwindow.modes)
            if modes and modes[0] == "+": modes = modes[1:]
            if mode[0] == "+":
                for m in mode[1:]:
                    if m not in modes:
                        modes.extend(m)
            elif mode[0] == "-":
                for i in mode[1:]:
                    try:
                        modes.remove(i)
                    except ValueError:
                        pass
            modes.sort()
            self.parent.mainwindow.modes = "+" + "".join(modes)
        modes = []
        cur = "+"
        for l in mode:
            if l in ["+","-"]: cur = l
            else:
                modes.append("%s%s" % (cur, l))
        for (i,m) in enumerate(modes):
            try:
                self.parent.userPresentUpdate.emit(handles[i], channel, m+":%s" % (op))
            except IndexError:
                self.parent.userPresentUpdate.emit("", channel, m+":%s" % (op))
    def nick(self, oldnick, newnick):
        oldhandle = oldnick[0:oldnick.find("!")]
        if oldhandle == self.parent.mainwindow.profile().handle:
            self.parent.myHandleChanged.emit(newnick)
        newchum = PesterProfile(newnick, chumdb=self.parent.mainwindow.chumdb)
        self.parent.moodUpdated.emit(oldhandle, Mood("offline"))
        self.parent.userPresentUpdate.emit("%s:%s" % (oldhandle, newnick), "", "nick")
        if newnick in self.parent.mainwindow.chumList.chums:
            self.getMood(newchum)
        if oldhandle == self.parent.mainwindow.randhandler.randNick:
                self.parent.mainwindow.randhandler.setRunning(False)
        elif newnick == self.parent.mainwindow.randhandler.randNick:
                self.parent.mainwindow.randhandler.setRunning(True)
    def namreply(self, server, nick, op, channel, names):
        namelist = names.split(" ")
        logging.info("---> recv \"NAMES %s: %d names\"" % (channel, len(namelist)))
        if not hasattr(self, 'channelnames'):
            self.channelnames = {}
        if channel not in self.channelnames:
            self.channelnames[channel] = []
        self.channelnames[channel].extend(namelist)
    def endofnames(self, server, nick, channel, msg):
        namelist = self.channelnames[channel]
        pl = PesterList(namelist)
        del self.channelnames[channel]
        self.parent.namesReceived.emit(channel, pl)
        if channel == "#pesterchum" and (not hasattr(self, "joined") or not self.joined):
            self.joined = True
            self.parent.mainwindow.randhandler.setRunning(self.parent.mainwindow.randhandler.randNick in namelist)
            chums = self.parent.mainwindow.chumList.chums
            lesschums = []
            for c in chums:
                chandle = c.handle
                if chandle in namelist:
                    lesschums.append(c)
            self.getMood(*lesschums)

    def liststart(self, server, handle, *info):
        self.channel_list = []
        info = list(info)
        self.channel_field = info.index("Channel") # dunno if this is protocol
        logging.info("---> recv \"CHANNELS: %s " % (self.channel_field))
    def listx(self, server, handle, *info):
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

    def umodeis(self, server, handle, modes):
        self.parent.mainwindow.modes = modes
    def invite(self, sender, you, channel):
        handle = sender.split('!')[0]
        self.parent.inviteReceived.emit(handle, channel)
    def inviteonlychan(self, server, handle, channel, msg):
        self.parent.chanInviteOnly.emit(channel)
    def channelmodeis(self, server, handle, channel, modes):
        self.parent.modesUpdated.emit(channel, modes)
    def cannotsendtochan(self, server, handle, channel, msg):
        self.parent.cannotSendToChan.emit(channel, msg)
    def toomanypeeps(self, *stuff):
        self.parent.tooManyPeeps.emit()

    def ping(self, prefix, server):
        self.parent.mainwindow.lastping = int(time())
        self.client.send('PONG', server)

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


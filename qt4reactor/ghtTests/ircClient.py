from PySide.QtCore import *
from PySide.QtGui import *
import sys, qt4reactor

app = QApplication(sys.argv)
qt4reactor.install()

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import time, sys

class IRCCore(irc.IRCClient):
    nickname = 'dosdsdssd'
    def connectionMade(self):
        self.nickname = self.factory.window.nickName.text().encode('ascii')
        self.factory.window.protocol = self
        irc.IRCClient.connectionMade(self)
        self.log('connected!!')
    def connectionLost(self, reason):
        self.log('disconnected... :( %s'%reason)
    def signedOn(self):
        chanName = self.factory.window.channelName.text().encode('ascii')
        self.join(chanName)
    def joined(self, channel):
        self.log('joined %s'%channel)
    def privmsg(self, user, channel, msg):
        self.log('%s %s %s'%(user, channel, msg))
    def action(self, user, channel, msg):
        self.log('action: %s %s %s'%(user, channel, msg))
    def log(self, str):
        self.factory.window.view.addItem(str)

class IRCCoreFactory(protocol.ClientFactory):
    protocol = IRCCore
    def __init__(self, window):
        self.window = window
    def clientConnectionLost(self, connector, reason):
        # reconnect to server if lose connection
        connector.connect()
    def clientConnectionFailed(self, connector, reason):
        print('connection failed! :(', reason)
        reactor.stop()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        connectLayout = QHBoxLayout()
        connectLayout.addWidget(QLabel('Server:'))
        self.serverName = QLineEdit('irc.freenode.org')
        connectLayout.addWidget(self.serverName)
        connectLayout.addWidget(QLabel('Channel:'))
        self.channelName = QLineEdit('#pangaea')
        connectLayout.addWidget(self.channelName)
        connectLayout.addWidget(QLabel('Nick:'))
        self.nickName = QLineEdit('ceruleanwave9832')
        connectLayout.addWidget(self.nickName)
        self.connectButton = QPushButton('Connect!')
        connectLayout.addWidget(self.connectButton)
        self.connectButton.clicked.connect(self.connectIRC)

        self.view = QListWidget()
        self.entry = QLineEdit()
        self.entry.returnPressed.connect(self.sendMessage)
        irc = QWidget(self)
        vbox = QVBoxLayout()
        vbox.addLayout(connectLayout)
        vbox.addWidget(self.view)
        vbox.addWidget(self.entry)
        irc.setLayout(vbox)
        self.setCentralWidget(irc)
        self.setWindowTitle('IRC')
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.showMaximized()

        self.protocol = None
    def connectIRC(self):
        self.connectButton.setDisabled(True)
        self.channelName.setDisabled(True)
        self.nickName.setDisabled(True)
        self.serverName.setDisabled(True)
        ircCoreFactory = IRCCoreFactory(self)
        serverName = self.serverName.text().encode('ascii')
        reactor.connectTCP(serverName, 6667, ircCoreFactory)
        #reactor.runReturn()
        #app.exit()
        #app.exit()
        reactor.run()
    def sendMessage(self):
        if self.protocol:
            chanName = self.channelName.text().encode('ascii')
            message = self.entry.text().encode('ascii')
            self.protocol.msg(chanName, message)
            self.view.addItem('%s <%s> %s'%(chanName, self.protocol.nickname, message))
        else:
            self.view.addItem('Not connected.')
        self.entry.setText('')
    def closeEvent(self, event):
        print('Attempting to close the main window!')
        reactor.stop()
        event.accept()

if __name__ == '__main__':
    mainWin = MainWindow()
    sys.exit(app.exec_())

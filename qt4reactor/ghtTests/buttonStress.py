import sys
from PySide import QtGui, QtScript
from PySide.QtCore import QTimer, SIGNAL, QObject
import qt4reactor

app = QtGui.QApplication(sys.argv)
qt4reactor.install()

from twisted.internet import reactor, task
from twisted.python import log
log.startLogging(sys.stdout)

class doNothing(QObject):
    def __init__(self):
        self.count = 0
        self.looping=False
        task.LoopingCall(self.printStat).start(1.0)
        QObject.__init__(self)
        
    def doSomething(self):
        if not self.looping: return
        self.count += 1
        reactor.callLater(0.003,self.doSomething)
        
    def buttonClick(self):
        if self.looping: 
            self.looping=False
            log.msg('looping stopped....')
        else: 
            self.looping=True
            self.doSomething()
            log.msg('looping started....')
        
    def printStat(self):
        log.msg(' c: ' + str(self.count) + 
                ' st: ' + str(reactor._doSomethingCount))


t=doNothing()

engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, SIGNAL("clicked()"), t.buttonClick)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")

reactor.runReturn()
app.exec_()
log.msg('fell off the bottom?...')



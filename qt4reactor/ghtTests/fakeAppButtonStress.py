import sys
from PySide import QtGui, QtScript
from PySide.QtCore import QTimer, SIGNAL, QEventLoop
import qt4reactor
        
app = QtGui.QApplication(sys.argv)

qt4reactor.install()

from twisted.internet import reactor, task

class doNothing(object):
    def __init__(self):
        self.count = 0
        self.running=False
        task.LoopingCall(self.printStat).start(1.0)

        
    def buttonClick(self):
        if self.running:
            self.running=False
            print 'CLICK: calling reactor stop...'
            reactor.stop()
            print 'reactor stop called....'
        else:
            self.running=True
            print 'CLICK: entering run'
            reactor.run()
            print 'reactor run returned...'
        
    def printStat(self):
        print 'tick...'

t=doNothing()

engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, SIGNAL("clicked()"), t.buttonClick)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")

app.exec_()
print 'fell off the bottom?...'



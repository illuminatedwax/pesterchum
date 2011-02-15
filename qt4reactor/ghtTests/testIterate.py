import sys
from PySide import QtGui, QtScript
from PySide.QtCore import QTimer, SIGNAL
import qt4reactor

app = QtGui.QApplication(sys.argv)
qt4reactor.install()

from twisted.internet import reactor, task
from twisted.python import log
log.startLogging(sys.stdout)

def testReactor():
    print 'tick...'

def buttonClick():
    print 'click...'
    reactor.iterate(5.0)
    print 'click return'
    
engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, SIGNAL("clicked()"), buttonClick)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")

task.LoopingCall(testReactor).start(1.0)
reactor.run()
log.msg('fell off the bottom?...')



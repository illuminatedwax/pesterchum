import sys
from PyQt4 import QtGui, QtScript
from PyQt4.QtCore import QTimer, SIGNAL, QEventLoop
import qt4reactor
        
app = QtGui.QApplication(sys.argv)

qt4reactor.install()

from twisted.internet import reactor, task

class doNothing(object):
    def __init__(self):
        self.count = 0
        self.running=False
        
    def buttonClick(self):
        if not self.running:
            from twisted.scripts import trial
            trial.run()
            
def run():

    t=doNothing()
    
    engine = QtScript.QScriptEngine()
    
    button = QtGui.QPushButton()
    scriptButton = engine.newQObject(button)
    engine.globalObject().setProperty("button", scriptButton)
    
    app.connect(button, SIGNAL("clicked()"), t.buttonClick)
    
    engine.evaluate("button.text = 'Do Twisted Gui Trial'")
    engine.evaluate("button.styleSheet = 'font-style: italic'")
    engine.evaluate("button.show()")
    
    app.exec_()
    print 'fell off the bottom?...'



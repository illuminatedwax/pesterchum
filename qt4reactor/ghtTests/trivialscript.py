import sys

from twisted.application import reactors
import qt4reactor
qt4reactor.install()
#reactors.installReactor('qt4')

from twisted.internet import reactor, task
from twisted.python import log
log.startLogging(sys.stdout)
 
def testReactor():
    print 'tick...'

def doit():
    task.LoopingCall(testReactor).start(1.0)
    reactor.callLater(15.0,reactor.stop)
    
reactor.callWhenRunning(doit)
log.msg('calling reactor.run()')
reactor.run()
log.msg('fell off the bottom?...')

#sys.exit(app.exec_())


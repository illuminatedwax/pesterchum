import os, sys, re, ostools
try:
    import lua
except ImportError:
    lua = None
from quirks import ScriptQuirks
from PyQt4 import QtGui, QtCore

class LuaQuirks(ScriptQuirks):
    def loadModule(self, name, filename):
        if lua is None:
            return None
        fullname = os.path.join('quirks', name)
        lua.globals().package.loaded[fullname] = None
        return lua.require(fullname)

    def getExtension(self):
        return '.lua'

    def modHas(self, module, attr):
        return module[attr] is not None

    def register(self, module):
        class Wrapper(object):
            def __init__(self, module, name):
                self.module = module
                self.name = name

            def __call__(self, text):
                return self.module.commands[self.name](lua.globals().tostring(text))

        for name in module.commands:
            try:
                if not isinstance(module.commands[name]("test"), basestring):
                    raise Exception
            except:
                print "Quirk malformed: %s" % (name)
                msgbox = QtGui.QMessageBox()
                msgbox.setWindowTitle("Error!")
                msgbox.setText("Quirk malformed: %s" % (name))
                msgbox.exec_()
            else:
                self.quirks[name] = Wrapper(module, name)


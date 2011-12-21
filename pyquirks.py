import os, sys, imp, re, ostools
from PyQt4 import QtGui, QtCore

class PythonQuirks(object):
    def __init__(self):
        self._datadir = ostools.getDataDir()
        self.home = os.getcwd()
        self.quirks = {}
        self.last = {}
        self.load()

    def load(self):
        self.last = self.quirks.copy()
        self.quirks.clear()
        filenames = []
        if not os.path.exists(os.path.join(self.home, 'quirks')):
            os.mkdir(os.path.join(self.home, 'quirks'))
        for fn in os.listdir(os.path.join(self.home, 'quirks')):
            if fn.endswith('.py') and not fn.startswith('_'):
                filenames.append(os.path.join(self.home, 'quirks', fn))
        if self._datadir:
            if not os.path.exists(os.path.join(self._datadir, 'quirks')):
                os.mkdir(os.path.join(self._datadir, 'quirks'))
            for fn in os.listdir(os.path.join(self._datadir, 'quirks')):
                if fn.endswith('.py') and not fn.startswith('_'):
                    filenames.append(os.path.join(self._datadir, 'quirks', fn))

        modules = []
        for filename in filenames:
            name = os.path.basename(filename)[:-3]
            try: module = imp.load_source(name, filename)
            except Exception, e:
                print "Error loading %s: %s (in pyquirks.py)" % (name, e)
                msgbox = QtGui.QMessageBox()
                msgbox.setWindowTitle("Error!")
                msgbox.setText("Error loading %s: %s (in pyquirks.py)" % (name, e))
                msgbox.exec_()
            else:
                if hasattr(module, 'setup'):
                    module.setup()
                self.register(vars(module))
                modules.append(name)
        for k in self.last:
            if k in self.quirks:
                if self.last[k] == self.quirks[k]:
                    del self.quirks[k]

        if self.quirks:
            print 'Registered quirks:', '), '.join(self.quirks) + ")"
        else:print "Warning: Couldn't find any python quirks"

    def register(self, variables):
        for name, obj in variables.iteritems():
            if hasattr(obj, 'command'):
                try:
                    if not isinstance(obj("test"), basestring):
                        raise Exception
                except:
                    print "Quirk malformed: %s" % (obj.command)
                    msgbox = QtGui.QMessageBox()
                    msgbox.setWindowTitle("Error!")
                    msgbox.setText("Quirk malformed: %s" % (obj.command))
                    msgbox.exec_()
                else:
                    self.quirks[obj.command+"("] = obj

    def funcre(self):
        if not self.quirks:
            return r"\\[0-9]+"
        f = r"("
        for q in self.quirks:
            f = f + q[:-1]+r"\(|"
        f = f + r"\)|\\[0-9]+)"
        return f

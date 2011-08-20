import inspect
import threading
import time
from PyQt4 import QtGui, QtCore

try:
    import pynotify
except:
    pynotify = None

class DefaultToast(object):
    def __init__(self, title, msg, icon):
        self.title = title
        self.msg   = msg
        self.icon  = icon
    def show(self):
        print self.title, self.msg, self.icon

class ToastMachine(object):
    class __Toast__(object):
        def __init__(self, parent, window, title, msg, time=3000, icon="", importance=0):
            self.parent     = parent
            self.mainwindow = window
            self.title      = title
            self.msg        = msg
            self.time       = time
            self.icon       = icon
            self.importance = importance
            if inspect.ismethod(self.title) or inspect.isfunction(self.title):
                self.title = self.title()

        def titleM(self, title=None):
            if title:
                self.title = title
                if inspect.ismethod(self.title) or inspect.isfunction(self.title):
                    self.title = self.title()
            else:     return self.title
        def msgM(self, msg=None):
            if msg:   self.msg = msg
            else:     return self.msg
        def timeM(self, time=None):
            if time:  self.time = time
            else:     return self.time
        def iconM(self, icon=None):
            if icon:  self.icon = icon
            else:     return self.icon
        def importanceM(self, importance=None):
            if importance != None: self.importance = importance
            else:                  return self.importance

        def show(self):
            # Use libnotify's queue if using libnotify
            if self.parent.toasts and self.parent.type != "libnotify":
                self.parent.toasts.append(self)
            else:
                self.realShow()

        def realShow(self):
            t = None
            for (k,v) in self.parent.types.iteritems():
                if self.parent.type == k:
                    t = v(self.title, self.msg, self.icon)
                    # Use libnotify's urgency setting
                    if k == "libnotify":
                        if self.importance < 0:
                            t.set_urgency(pynotify.URGENCY_CRITICAL)
                        elif self.importance == 0:
                            t.set_urgency(pynotify.URGENCY_NORMAL)
                        elif self.importance > 0:
                            t.set_urgency(pynotify.URGENCY_LOW)
                    break
            if not t:
                if 'default' in self.parent.types:
                    if 'parent' in inspect.getargspec(self.parent.types['default']).args:
                        t = self.parent.types['default'](self.title, self.msg, self.icon, self.mainwindow)
                    else:
                        t = self.parent.types['default'](self.title, self.msg, self.icon)
                else:
                    t = DefaultToast(self.title, self.msg, self.icon)
            t.show()
            print "SLEEPING"
            #time.sleep(self.time/1000)
            if self in self.parent.toasts:
                self.parent.toasts.remove(self)

    def __init__(self, parent, name, type="default", types=({'default'  : DefaultToast,
                                                            'libnotify': pynotify.Notification}
                                                            if pynotify else
                                                            {'default'  : DefaultToast}),
                                                     extras={}):
        print types
        self.mainwindow = parent
        self.name       = name
        types.update(extras)
        self.types      = types
        self.type       = type
        self.quit       = False

        if type == "libnotify":
            try:
                if not pynotify or not pynotify.init("ToastMachine"):
                    raise Exception
            except:
                print "Problem initilizing pynotify"
                self.type = type = "default"

        self.toasts = []

    def Toast(self, title, msg, icon=""):
        return self.__Toast__(self, self.mainwindow, title, msg, time=0, icon=icon)

    def appName(self):
        if inspect.ismethod(self.name) or inspect.isfunction(self.name):
            return self.name()
        else:
            return self.name

    def showNext(self):
        high   = filter(lambda x: x.importance < 0, self.toasts)
        normal = filter(lambda x: x.importance == 0, self.toasts)
        low    = filter(lambda x: x.importance > 0, self.toasts)

        if high:
            high.sort(key=lambda x: x.importance)
            high[0].realShow()
        elif normal:
            normal[0].realShow()
        elif low:
            low.sort(key=lambda x: x.importance)
            low[0].realShow()

    def showAll(self):
        while self.toasts:
            self.showNext()

    def run(self):
        while not self.quit:
            if self.toasts:
                self.showNext()


class PesterToast(QtGui.QFrame, DefaultToast):
    def __init__(self, title, msg, icon, parent=None):
        QtGui.QFrame.__init__(self, parent,
                              (QtCore.Qt.CustomizeWindowHint |
                               QtCore.Qt.FramelessWindowHint))
        #self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        #self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setObjectName("toast")
        self.setWindowTitle("toast")
        #self.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.title = QtGui.QLabel(title, self)
        self.msg = QtGui.QLabel(msg, self)

        self.btn = QtGui.QPushButton("Push Me", self)
        self.connect(self.btn, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.title)
        layout_0.addWidget(self.btn)
        layout_0.addWidget(self.msg)

        self.setLayout(layout_0)

        print self.isWindow()

    def show(self):
        QtGui.QFrame.setVisible(self, True)
        print "SHOWING"
        #~ themeWarning = QtGui.QMessageBox(self)
        #~ themeWarning.setText("ASDFASD")
        #~ themeWarning.exec_()

class PesterToastMachine(ToastMachine, QtCore.QObject):
    def __init__(self, parent, name, type="default",
                 types=({'default'  : DefaultToast,
                        'libnotify' : pynotify.Notification}
                        if pynotify else
                        {'default' : DefaultToast}),
                 extras={}):
        ToastMachine.__init__(self, parent, name, type, types, extras)
        QtCore.QObject.__init__(self, parent)

    @QtCore.pyqtSlot()
    def showNext(self):
        ToastMachine.showNext(self)

    def run(self):
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL('timeout()'),
                     self, QtCore.SLOT('showNext()'))
        #self.timer.start(1000)

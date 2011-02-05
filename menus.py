from PyQt4 import QtGui, QtCore
import re

from generic import RightClickList, MultiTextDialog
from dataobjs import pesterQuirk, PesterProfile

class PesterQuirkItem(QtGui.QListWidgetItem):
    def __init__(self, quirk, parent):
        QtGui.QListWidgetItem.__init__(self, parent)
        self.quirk = quirk
        self.setText(unicode(quirk))

    def __lt__(self, quirkitem):
        if self.quirk.type == "prefix":
            return True
        elif (self.quirk.type == "replace" or self.quirk.type == "regexp") and \
                quirkitem.type == "suffix":
            return True
        else:
            return False
        
class PesterQuirkList(QtGui.QListWidget):
    def __init__(self, mainwindow, parent):
        QtGui.QListWidget.__init__(self, parent)
        self.resize(400, 200)
        self.mainwindow = mainwindow
        self.setStyleSheet("background:black; color:white;")

        for q in mainwindow.userprofile.quirks:
            item = PesterQuirkItem(q, self)
            self.addItem(item)
        self.sortItems()

    @QtCore.pyqtSlot()
    def removeCurrent(self):
        i = self.currentRow()
        if i >= 0:
            self.takeItem(i)

class PesterChooseQuirks(QtGui.QDialog):
    def __init__(self, config, theme, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.config = config
        self.theme = theme
        self.mainwindow = parent
        self.setStyleSheet(self.theme["main/defaultwindow/style"])
        self.setWindowTitle("Set Quirks")

        self.quirkList = PesterQuirkList(self.mainwindow, self)
        
        self.addPrefixButton = QtGui.QPushButton("ADD PREFIX", self)
        self.connect(self.addPrefixButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addPrefixDialog()'))
        self.addSuffixButton = QtGui.QPushButton("ADD SUFFIX", self)
        self.connect(self.addSuffixButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addSuffixDialog()'))
        self.addSimpleReplaceButton = QtGui.QPushButton("SIMPLE REPLACE", self)
        self.connect(self.addSimpleReplaceButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addSimpleReplaceDialog()'))
        self.addRegexpReplaceButton = QtGui.QPushButton("REGEXP REPLACE", self)
        self.connect(self.addRegexpReplaceButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addRegexpDialog()'))
        layout_1 = QtGui.QHBoxLayout()
        layout_1.addWidget(self.addPrefixButton)
        layout_1.addWidget(self.addSuffixButton)
        layout_1.addWidget(self.addSimpleReplaceButton)
        layout_1.addWidget(self.addRegexpReplaceButton)

        self.removeSelectedButton = QtGui.QPushButton("REMOVE", self)
        self.connect(self.removeSelectedButton, QtCore.SIGNAL('clicked()'),
                     self.quirkList, QtCore.SLOT('removeCurrent()'))
        
        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        layout_ok = QtGui.QHBoxLayout()
        layout_ok.addWidget(self.cancel)
        layout_ok.addWidget(self.ok)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.quirkList)
        layout_0.addLayout(layout_1)
        layout_0.addWidget(self.removeSelectedButton)
        layout_0.addLayout(layout_ok)
        self.setLayout(layout_0)

    def quirks(self):
        return [self.quirkList.item(i).quirk for i in 
                range(0,self.quirkList.count())]
            

    @QtCore.pyqtSlot()
    def addPrefixDialog(self):
        pdict = MultiTextDialog("ENTER PREFIX", self, {"label": "Value:", "inputname": "value"}).getText()
        pdict["type"] = "prefix"
        prefix = pesterQuirk(pdict)
        pitem = PesterQuirkItem(prefix, self.quirkList)
        self.quirkList.addItem(pitem)
        self.quirkList.sortItems()
    @QtCore.pyqtSlot()
    def addSuffixDialog(self):
        vdict = MultiTextDialog("ENTER SUFFIX", self, {"label": "Value:", "inputname": "value"}).getText()
        vdict["type"] = "suffix"
        quirk = pesterQuirk(vdict)
        item = PesterQuirkItem(quirk, self.quirkList)
        self.quirkList.addItem(item)
        self.quirkList.sortItems()
    @QtCore.pyqtSlot()
    def addSimpleReplaceDialog(self):
        vdict = MultiTextDialog("REPLACE", self, {"label": "Replace:", "inputname": "from"}, {"label": "With:", "inputname": "to"}).getText()
        vdict["type"] = "replace"
        quirk = pesterQuirk(vdict)
        item = PesterQuirkItem(quirk, self.quirkList)
        self.quirkList.addItem(item)
        self.quirkList.sortItems()
    @QtCore.pyqtSlot()
    def addRegexpDialog(self):
        vdict = MultiTextDialog("REGEXP REPLACE", self, {"label": "Regexp:", "inputname": "from"}, {"label": "Replace With:", "inputname": "to"}).getText()
        vdict["type"] = "regexp"
        try:
            re.compile(vdict["from"])
        except re.error, e:
            quirkWarning = QtGui.QMessageBox(self)
            quirkWarning.setText("Not a valid regular expression!")
            quirkWarning.setInformativeText("H3R3S WHY DUMP4SS: %s" % (e))
            quirkWarning.exec_()
            return
            
        quirk = pesterQuirk(vdict)
        item = PesterQuirkItem(quirk, self.quirkList)
        self.quirkList.addItem(item)
        self.quirkList.sortItems()

class PesterChooseTheme(QtGui.QDialog):
    def __init__(self, config, theme, parent):
        QtGui.QDialog.__init__(self, parent)
        self.config = config
        self.theme = theme
        self.parent = parent
        self.setStyleSheet(self.theme["main/defaultwindow/style"])
        self.setWindowTitle("Pick a theme")

        instructions = QtGui.QLabel("Pick a theme:")

        avail_themes = config.availableThemes()
        self.themeBox = QtGui.QComboBox(self)
        for (i, t) in enumerate(avail_themes):
            self.themeBox.addItem(t)
            if t == theme.name:
                self.themeBox.setCurrentIndex(i)

        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        layout_ok = QtGui.QHBoxLayout()
        layout_ok.addWidget(self.cancel)
        layout_ok.addWidget(self.ok)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(instructions)
        layout_0.addWidget(self.themeBox)
        layout_0.addLayout(layout_ok)

        self.setLayout(layout_0)

        self.connect(self, QtCore.SIGNAL('accepted()'),
                     parent, QtCore.SLOT('themeSelected()'))
        self.connect(self, QtCore.SIGNAL('rejected()'),
                     parent, QtCore.SLOT('closeTheme()'))

class PesterChooseProfile(QtGui.QDialog):
    def __init__(self, userprofile, config, theme, parent, collision=None):
        QtGui.QDialog.__init__(self, parent)
        self.userprofile = userprofile
        self.theme = theme
        self.config = config
        self.parent = parent
        self.setStyleSheet(self.theme["main/defaultwindow/style"])

        self.chumHandle = QtGui.QLineEdit(self)
        self.chumHandle.setMinimumWidth(200)
        self.chumHandleLabel = QtGui.QLabel(self.theme["main/mychumhandle/label/text"], self)
        self.chumColorButton = QtGui.QPushButton(self)
        self.chumColorButton.resize(50, 20)
        self.chumColorButton.setStyleSheet("background: %s" % (userprofile.chat.colorhtml()))
        self.chumcolor = userprofile.chat.color
        self.connect(self.chumColorButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('openColorDialog()'))
        layout_1 = QtGui.QHBoxLayout()
        layout_1.addWidget(self.chumHandleLabel)
        layout_1.addWidget(self.chumHandle)
        layout_1.addWidget(self.chumColorButton)

        # available profiles?
        avail_profiles = self.config.availableProfiles()
        if avail_profiles:
            self.profileBox = QtGui.QComboBox(self)
            self.profileBox.addItem("Choose a profile...")
            for p in avail_profiles:
                self.profileBox.addItem(p.chat.handle)
        else:
            self.profileBox = None

        self.defaultcheck = QtGui.QCheckBox(self)
        self.defaultlabel = QtGui.QLabel("Set This Profile As Default", self)
        layout_2 = QtGui.QHBoxLayout()
        layout_2.addWidget(self.defaultlabel)
        layout_2.addWidget(self.defaultcheck)
        
        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('validateProfile()'))
        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        layout_ok = QtGui.QHBoxLayout()
        layout_ok.addWidget(self.cancel)
        layout_ok.addWidget(self.ok)

        layout_0 = QtGui.QVBoxLayout()
        if collision:
            collision_warning = QtGui.QLabel("%s is taken already! Pick a new profile." % (collision))
            layout_0.addWidget(collision_warning)
        layout_0.addLayout(layout_1)
        if avail_profiles:
            profileLabel = QtGui.QLabel("Or choose an existing profile:", self)
            layout_0.addWidget(profileLabel)
            layout_0.addWidget(self.profileBox)
        layout_0.addLayout(layout_ok)
        layout_0.addLayout(layout_2)
        self.errorMsg = QtGui.QLabel(self)
        self.errorMsg.setStyleSheet("color:red;")
        layout_0.addWidget(self.errorMsg)
        self.setLayout(layout_0)

        self.connect(self, QtCore.SIGNAL('accepted()'),
                     parent, QtCore.SLOT('profileSelected()'))
        self.connect(self, QtCore.SIGNAL('rejected()'),
                     parent, QtCore.SLOT('closeProfile()'))

    @QtCore.pyqtSlot()
    def openColorDialog(self):
        self.colorDialog = QtGui.QColorDialog(self)
        color = self.colorDialog.getColor(initial=self.userprofile.chat.color)
        self.chumColorButton.setStyleSheet("background: %s" % color.name())
        self.chumcolor = color
        self.colorDialog = None

    @QtCore.pyqtSlot()
    def validateProfile(self):
        if not self.profileBox or self.profileBox.currentIndex() == 0:
            handle = unicode(self.chumHandle.text())
            if not PesterProfile.checkLength(handle):
                self.errorMsg.setText("PROFILE HANDLE IS TOO LONG")
                return
            if not PesterProfile.checkValid(handle):
                self.errorMsg.setText("NOT A VALID CHUMTAG")
                return
        self.accept()

class PesterOptions(QtGui.QDialog):
    def __init__(self, config, theme, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.config = config
        self.theme = theme
        self.setStyleSheet(self.theme["main/defaultwindow/style"])

        self.tabcheck = QtGui.QCheckBox(self)
        if self.config.tabs():
            self.tabcheck.setChecked(True)
        self.tablabel = QtGui.QLabel("Tabbed Conversations", self)
        layout_1 = QtGui.QHBoxLayout()
        layout_1.addWidget(self.tablabel)
        layout_1.addWidget(self.tabcheck)
        
        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        layout_2 = QtGui.QHBoxLayout()
        layout_2.addWidget(self.cancel)
        layout_2.addWidget(self.ok)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addLayout(layout_1)
        layout_0.addLayout(layout_2)

        self.setLayout(layout_0)

class PesterUserlist(QtGui.QDialog):
    def __init__(self, config, theme, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.config = config
        self.theme = theme
        self.mainwindow = parent
        self.setStyleSheet(self.theme["main/defaultwindow/style"])
        self.resize(200, 600)

        self.label = QtGui.QLabel("USERLIST")
        self.userarea = RightClickList(self)
        self.userarea.setStyleSheet(self.theme["main/chums/style"])
        self.userarea.optionsMenu = QtGui.QMenu(self)

        self.addChumAction = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/addchum"], self)
        self.connect(self.addChumAction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('addChumSlot()'))
        self.userarea.optionsMenu.addAction(self.addChumAction)

        self.ok = QtGui.QPushButton("OK", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.label)
        layout_0.addWidget(self.userarea)
        layout_0.addWidget(self.ok)
        
        self.setLayout(layout_0)

        self.connect(self.mainwindow, QtCore.SIGNAL('namesUpdated()'),
                     self, QtCore.SLOT('updateUsers()'))

        self.connect(self.mainwindow, 
                     QtCore.SIGNAL('userPresentSignal(QString, QString, QString)'),
                     self, 
                     QtCore.SLOT('updateUserPresent(QString, QString, QString)'))
        self.updateUsers()
    @QtCore.pyqtSlot()
    def updateUsers(self):
        names = self.mainwindow.namesdb["#pesterchum"]
        self.userarea.clear()
        for n in names:
            item = QtGui.QListWidgetItem(n)
            item.setTextColor(QtGui.QColor(self.theme["main/chums/userlistcolor"]))
            self.userarea.addItem(item)
        self.userarea.sortItems()
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString, QtCore.QString)
    def updateUserPresent(self, handle, channel, update):
        h = unicode(handle)
        c = unicode(channel)
        if update == "quit":
            self.delUser(h)
        elif update == "left" and c == "#pesterchum":
            self.delUser(h)
        elif update == "join" and c == "#pesterchum":
            self.addUser(h)
    def addUser(self, name):
        item = QtGui.QListWidgetItem(name)
        item.setTextColor(QtGui.QColor(self.theme["main/chums/userlistcolor"]))
        self.userarea.addItem(item)
        self.userarea.sortItems()
    def delUser(self, name):
        matches = self.userarea.findItems(name, QtCore.Qt.MatchFlags(0))
        for m in matches:
            self.userarea.takeItem(self.userarea.row(m))

    def changeTheme(self, theme):
        self.theme = theme
        self.setStyleSheet(theme["main/defaultwindow/style"])
        self.userarea.setStyleSheet(theme["main/chums/style"])
        self.addChumAction.setText(theme["main/menus/rclickchumlist/addchum"])
        for item in [self.userarea.item(i) for i in range(0, self.userarea.count())]:
            item.setTextColor(QtGui.QColor(theme["main/chums/userlistcolor"]))

    @QtCore.pyqtSlot()
    def addChumSlot(self):
        cur = self.userarea.currentItem()
        if not cur:
            return
        self.addChum.emit(cur.text())

    addChum = QtCore.pyqtSignal(QtCore.QString)

class PesterMemoList(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.theme = parent.theme
        self.mainwindow = parent
        self.setStyleSheet(self.theme["main/defaultwindow/style"])
        self.resize(200, 300)

        self.label = QtGui.QLabel("MEMOS")
        self.channelarea = RightClickList(self)
        self.channelarea.setStyleSheet(self.theme["main/chums/style"])
        self.channelarea.optionsMenu = QtGui.QMenu(self)
        self.connect(self.channelarea, 
                     QtCore.SIGNAL('itemActivated(QListWidgetItem *)'),
                     self, QtCore.SLOT('joinActivatedMemo(QListWidgetItem *)'))

        self.orjoinlabel = QtGui.QLabel("OR MAKE A NEW MEMO:")
        self.newmemo = QtGui.QLineEdit(self)

        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        self.join = QtGui.QPushButton("JOIN", self)
        self.join.setDefault(True)
        self.connect(self.join, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        layout_ok = QtGui.QHBoxLayout()
        layout_ok.addWidget(self.cancel)
        layout_ok.addWidget(self.join)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.label)
        layout_0.addWidget(self.channelarea)
        layout_0.addWidget(self.orjoinlabel)
        layout_0.addWidget(self.newmemo)
        layout_0.addLayout(layout_ok)
        
        self.setLayout(layout_0)

    def newmemoname(self):
        return self.newmemo.text()
    def selectedmemo(self):
        return self.channelarea.currentItem()

    def updateChannels(self, channels):
        for c in channels:
            item = QtGui.QListWidgetItem(c[1:])
            item.setTextColor(QtGui.QColor(self.theme["main/chums/userlistcolor"]))
            item.setIcon(QtGui.QIcon(self.theme["memos/memoicon"]))
            self.channelarea.addItem(item)

    def updateTheme(self, theme):
        self.theme = theme
        self.setStyleSheet(theme["main/defaultwindow/style"])
        for item in [self.userarea.item(i) for i in range(0, self.channelarea.count())]:
            item.setTextColor(QtGui.QColor(theme["main/chums/userlistcolor"]))
            item.setIcon(QtGui.QIcon(theme["memos/memoicon"]))
    
    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def joinActivatedMemo(self, item):
        self.channelarea.setCurrentItem(item)
        self.accept()


class LoadingScreen(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent, flags=(QtCore.Qt.CustomizeWindowHint | 
                                                    QtCore.Qt.FramelessWindowHint))
        self.mainwindow = parent
        self.setStyleSheet(self.mainwindow.theme["main/defaultwindow/style"])

        self.loadinglabel = QtGui.QLabel("LO4D1NG")

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.loadinglabel)
        self.setLayout(self.layout)
        QtCore.QTimer.singleShot(25000, self, QtCore.SLOT('connectTimeout()'))
    @QtCore.pyqtSlot()
    def connectTimeout(self):
        if hasattr(self, 'failed'):
            self.accept()
        else:
            self.failed = True
            self.loadinglabel.setText("F41L3D")
            QtCore.QTimer.singleShot(1000, self, QtCore.SLOT('connectTimeout()'))

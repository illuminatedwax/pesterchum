from PyQt4 import QtGui, QtCore
import re

from generic import RightClickList, MultiTextDialog
from dataobjs import pesterQuirk, PesterProfile
from memos import TimeSlider, TimeInput

class PesterQuirkItem(QtGui.QListWidgetItem):
    def __init__(self, quirk, parent):
        QtGui.QListWidgetItem.__init__(self, parent)
        self.quirk = quirk
        self.setText(unicode(quirk))
    def update(self, quirk):
        self.quirk = quirk
        self.setText(unicode(quirk))
    def __lt__(self, quirkitem):
        """Sets the order of quirks if auto-sorted by Qt. Obsolete now."""
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
        # make sure we have access to mainwindow info like profiles
        self.mainwindow = mainwindow 
        self.setStyleSheet("background:black; color:white;")

        for q in mainwindow.userprofile.quirks: 
            item = PesterQuirkItem(q, self)
            self.addItem(item)
        #self.sortItems()

    def currentQuirk(self):
        return self.item(self.currentRow())

    def upShiftQuirk(self):
        i = self.currentRow()
        if i > 0:
            shifted_item = self.takeItem(i)
            self.insertItem(i-1,shifted_item)
            self.setCurrentRow(i-1)

    def downShiftQuirk(self):
        i = self.currentRow()
        if i < self.count() - 1 and i >= 0:
            shifted_item = self.takeItem(i)
            self.insertItem(i+1,shifted_item)
            self.setCurrentRow(i+1)

    @QtCore.pyqtSlot()
    def removeCurrent(self):
        i = self.currentRow()
        if i >= 0:
            self.takeItem(i)

class MispellQuirkDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("MISPELLER")
        layout_1 = QtGui.QHBoxLayout()
        zero = QtGui.QLabel("1%", self)
        hund = QtGui.QLabel("100%", self)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        layout_1.addWidget(zero)
        layout_1.addWidget(self.slider)
        layout_1.addWidget(hund)

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
        layout_0.addLayout(layout_1)
        layout_0.addLayout(layout_ok)

        self.setLayout(layout_0)
    def getPercentage(self):
        r = self.exec_()
        if r == QtGui.QDialog.Accepted:
            retval = {"percentage": self.slider.value()}
            return retval
        else:
            return None

class RandomQuirkDialog(MultiTextDialog):
    def __init__(self, parent, values={}):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("RANDOM QUIRK")
        self.inputs = {}
        layout_1 = QtGui.QHBoxLayout()
        regexpl = QtGui.QLabel("REGEXP:", self)
        self.regexp = QtGui.QLineEdit(values.get("regexp",""), self)
        layout_1.addWidget(regexpl)
        layout_1.addWidget(self.regexp)
        replacewithl = QtGui.QLabel("REPLACE WITH:", self)

        layout_2 = QtGui.QVBoxLayout()
        layout_3 = QtGui.QHBoxLayout()
        self.replacelist = QtGui.QListWidget(self)
        for v in values.get("list", []):
            item = QtGui.QListWidgetItem(v, self.replacelist)
        self.replaceinput = QtGui.QLineEdit(self)
        addbutton = QtGui.QPushButton("ADD", self)
        self.connect(addbutton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addRandomString()'))
        removebutton = QtGui.QPushButton("REMOVE", self)
        self.connect(removebutton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('removeRandomString()'))
        layout_3.addWidget(addbutton)
        layout_3.addWidget(removebutton)
        layout_2.addWidget(self.replacelist)
        layout_2.addWidget(self.replaceinput)
        layout_2.addLayout(layout_3)
        layout_1.addLayout(layout_2)

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
        layout_0.addLayout(layout_1)
        layout_0.addLayout(layout_ok)

        self.setLayout(layout_0)

    def getText(self):
        r = self.exec_()
        if r == QtGui.QDialog.Accepted:
            randomlist = [unicode(self.replacelist.item(i).text())
                          for i in range(0,self.replacelist.count())]
            retval = {"from": unicode(self.regexp.text()),
                      "randomlist": randomlist }
            return retval
        else:
            return None


    @QtCore.pyqtSlot()
    def addRandomString(self):
        text = unicode(self.replaceinput.text())
        item = QtGui.QListWidgetItem(text, self.replacelist)
        self.replaceinput.setText("")
        self.replaceinput.setFocus()
    @QtCore.pyqtSlot()
    def removeRandomString(self):
        if not self.replacelist.currentItem():
            return
        else:
            self.replacelist.takeItem(self.replacelist.currentRow())
        self.replaceinput.setFocus()

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
        self.addRandomReplaceButton = QtGui.QPushButton("RANDOM REPLACE", self)
        self.connect(self.addRandomReplaceButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addRandomDialog()'))

        self.addMispellingButton = QtGui.QPushButton("MISPELLER", self)
        self.connect(self.addMispellingButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('addSpellDialog()'))
        self.upShiftButton = QtGui.QPushButton("^", self)
        self.downShiftButton = QtGui.QPushButton("v", self)
        self.connect(self.upShiftButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('upShiftQuirk()'))
        self.connect(self.downShiftButton, QtCore.SIGNAL('clicked()'),
                    self, QtCore.SLOT('downShiftQuirk()'))

        layout_quirklist = QtGui.QHBoxLayout() #the nude layout quirklist
        layout_shiftbuttons = QtGui.QVBoxLayout() #the shift button layout
        layout_shiftbuttons.addWidget(self.upShiftButton)
        layout_shiftbuttons.addWidget(self.downShiftButton)
        layout_quirklist.addWidget(self.quirkList)
        layout_quirklist.addLayout(layout_shiftbuttons)

        layout_1 = QtGui.QHBoxLayout()
        layout_1.addWidget(self.addPrefixButton)
        layout_1.addWidget(self.addSuffixButton)
        layout_1.addWidget(self.addSimpleReplaceButton)
        layout_2 = QtGui.QHBoxLayout()
        layout_2.addWidget(self.addRegexpReplaceButton)
        layout_2.addWidget(self.addRandomReplaceButton)
        layout_2.addWidget(self.addMispellingButton)

        self.editSelectedButton = QtGui.QPushButton("EDIT", self)
        self.connect(self.editSelectedButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('editSelected()'))
        self.removeSelectedButton = QtGui.QPushButton("REMOVE", self)
        self.connect(self.removeSelectedButton, QtCore.SIGNAL('clicked()'),
                     self.quirkList, QtCore.SLOT('removeCurrent()'))
        layout_3 = QtGui.QHBoxLayout()
        layout_3.addWidget(self.editSelectedButton)
        layout_3.addWidget(self.removeSelectedButton)

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
        layout_0.addLayout(layout_quirklist)
        layout_0.addLayout(layout_1)
        layout_0.addLayout(layout_2)
        layout_0.addLayout(layout_3)
        layout_0.addLayout(layout_ok)
        self.setLayout(layout_0)

    def quirks(self):
        return [self.quirkList.item(i).quirk for i in
                range(0,self.quirkList.count())]
                
    # could probably do away with these and just connect to the relevant methods on the quirk list widget
    @QtCore.pyqtSlot()
    def upShiftQuirk(self): 
        self.quirkList.upShiftQuirk()

    @QtCore.pyqtSlot()
    def downShiftQuirk(self):
        self.quirkList.downShiftQuirk()
    #!!!    
    @QtCore.pyqtSlot()
    def editSelected(self):
        q = self.quirkList.currentQuirk()
        quirk = q.quirk
        if quirk.type == "prefix":
            self.addPrefixDialog(q)
        elif quirk.type == "suffix":
            self.addSuffixDialog(q)
        elif quirk.type == "replace":
            self.addSimpleReplaceDialog(q)
        elif quirk.type == "regexp":
            self.addRegexpDialog(q)
        elif quirk.type == "random":
            self.addRandomDialog(q)
        elif quirk.type == "spelling":
            self.addSpellDialog(q)

    @QtCore.pyqtSlot()
    def addPrefixDialog(self, qitem=None):
        d = {"label": "Value:", "inputname": "value" }
        if qitem is not None:
            d["value"] = qitem.quirk.quirk["value"]
        pdict = MultiTextDialog("ENTER PREFIX", self, d).getText()
        if pdict is None:
            return
        pdict["type"] = "prefix"
        prefix = pesterQuirk(pdict)
        if qitem is None:
            pitem = PesterQuirkItem(prefix, self.quirkList)
            self.quirkList.addItem(pitem)
        else:
            qitem.update(prefix)
        #self.quirkList.sortItems()

    @QtCore.pyqtSlot()
    def addSuffixDialog(self, qitem=None):
        d = {"label": "Value:", "inputname": "value" }
        if qitem is not None:
            d["value"] = qitem.quirk.quirk["value"]
        vdict = MultiTextDialog("ENTER SUFFIX", self, d).getText()
        if vdict is None:
            return
        vdict["type"] = "suffix"
        newquirk = pesterQuirk(vdict)
        if qitem is None:
            item = PesterQuirkItem(newquirk, self.quirkList)
            self.quirkList.addItem(item)
        else:
            qitem.update(newquirk)
        #self.quirkList.sortItems()

    @QtCore.pyqtSlot()
    def addSimpleReplaceDialog(self, qitem=None):
        d = [{"label": "Replace:", "inputname": "from"}, {"label": "With:", "inputname": "to"}]
        if qitem is not None:
            d[0]["value"] = qitem.quirk.quirk["from"]
            d[1]["value"] = qitem.quirk.quirk["to"]
        vdict = MultiTextDialog("REPLACE", self, *d).getText()
        if vdict is None:
            return
        vdict["type"] = "replace"
        newquirk = pesterQuirk(vdict)
        if qitem is None:
            item = PesterQuirkItem(newquirk, self.quirkList)
            self.quirkList.addItem(item)
        else:
            qitem.update(newquirk)
        #self.quirkList.sortItems()

    @QtCore.pyqtSlot()
    def addRegexpDialog(self, qitem=None):
        d = [{"label": "Regexp:", "inputname": "from"}, {"label": "Replace With:", "inputname": "to"}]
        if qitem is not None:
            d[0]["value"] = qitem.quirk.quirk["from"]
            d[1]["value"] = qitem.quirk.quirk["to"]
        vdict = MultiTextDialog("REGEXP REPLACE", self, *d).getText()
        if vdict is None:
            return
        vdict["type"] = "regexp"
        try:
            re.compile(vdict["from"])
        except re.error, e:
            quirkWarning = QtGui.QMessageBox(self)
            quirkWarning.setText("Not a valid regular expression!")
            quirkWarning.setInformativeText("H3R3S WHY DUMP4SS: %s" % (e))
            quirkWarning.exec_()
            return

        newquirk = pesterQuirk(vdict)
        if qitem is None:
            item = PesterQuirkItem(newquirk, self.quirkList)
            self.quirkList.addItem(item)
        else:
            qitem.update(newquirk)
        #self.quirkList.sortItems()
    @QtCore.pyqtSlot()
    def addRandomDialog(self, qitem=None):
        values = {}
        if qitem is not None:
            values["list"] = qitem.quirk.quirk["randomlist"]
            values["regexp"] = qitem.quirk.quirk["from"]
        vdict = RandomQuirkDialog(self, values).getText()
        if vdict is None:
            return
        vdict["type"] = "random"
        try:
            re.compile(vdict["from"])
        except re.error, e:
            quirkWarning = QtGui.QMessageBox(self)
            quirkWarning.setText("Not a valid regular expression!")
            quirkWarning.setInformativeText("H3R3S WHY DUMP4SS: %s" % (e))
            quirkWarning.exec_()
            return
        newquirk = pesterQuirk(vdict)
        if qitem is None:
            item = PesterQuirkItem(newquirk, self.quirkList)
            self.quirkList.addItem(item)
        else:
            qitem.update(newquirk)
        #self.quirkList.sortItems()
    @QtCore.pyqtSlot()
    def addSpellDialog(self, qitem=None):
        vdict = MispellQuirkDialog(self).getPercentage()
        if vdict is None:
            return
        vdict["type"] = "spelling"
        newquirk = pesterQuirk(vdict)
        if qitem is None:
            item = PesterQuirkItem(newquirk, self.quirkList)
            self.quirkList.addItem(item)
        else:
            qitem.update(newquirk)
        #self.quirkList.sortItems()

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

        self.currentHandle = QtGui.QLabel("CHANGING FROM %s" % userprofile.chat.handle)
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
        else:
            layout_0.addWidget(self.currentHandle, alignment=QtCore.Qt.AlignHCenter)
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

        self.tabcheck = QtGui.QCheckBox("Tabbed Conversations", self)
        if self.config.tabs():
            self.tabcheck.setChecked(True)
        self.hideOffline = QtGui.QCheckBox("Hide Offline Chums", self)
        if self.config.hideOfflineChums():
            self.hideOffline.setChecked(True)

        self.soundcheck = QtGui.QCheckBox("Sounds On", self)
        if self.config.soundOn():
            self.soundcheck.setChecked(True)

        self.timestampcheck = QtGui.QCheckBox("Time Stamps", self)
        if self.config.showTimeStamps():
            self.timestampcheck.setChecked(True)

        self.timestampBox = QtGui.QComboBox(self)
        self.timestampBox.addItem("12 hour")
        self.timestampBox.addItem("24 hour")
        if self.config.time12Format():
            self.timestampBox.setCurrentIndex(0)
        else:
            self.timestampBox.setCurrentIndex(1)
        self.secondscheck = QtGui.QCheckBox("Show Seconds", self)
        if self.config.showSeconds():
            self.secondscheck.setChecked(True)

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
        layout_0.addWidget(self.tabcheck)
        layout_0.addWidget(self.soundcheck)
        layout_0.addWidget(self.hideOffline)
        layout_0.addWidget(self.timestampcheck)
        layout_0.addWidget(self.timestampBox)
        layout_0.addWidget(self.secondscheck)
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


class MemoListItem(QtGui.QListWidgetItem):
    def __init__(self, channel, usercount):
        QtGui.QListWidgetItem.__init__(self, None)
        self.target = channel
        self.setText(channel + " (" + str(usercount) + ")")

class PesterMemoList(QtGui.QDialog):
    def __init__(self, parent, channel=""):
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
        self.newmemo = QtGui.QLineEdit(channel, self)
        self.secretChannel = QtGui.QCheckBox("HIDDEN CHANNEL?", self)

        self.timelabel = QtGui.QLabel("TIMEFRAME:")
        self.timeslider = TimeSlider(QtCore.Qt.Horizontal, self)
        self.timeinput = TimeInput(self.timeslider, self)

        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        self.join = QtGui.QPushButton("JOIN", self)
        self.join.setDefault(True)
        self.connect(self.join, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('checkEmpty()'))
        layout_ok = QtGui.QHBoxLayout()
        layout_ok.addWidget(self.cancel)
        layout_ok.addWidget(self.join)

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.label)
        layout_0.addWidget(self.channelarea)
        layout_0.addWidget(self.orjoinlabel)
        layout_0.addWidget(self.newmemo)
        layout_0.addWidget(self.secretChannel)
        layout_0.addWidget(self.timelabel)
        layout_0.addWidget(self.timeslider)
        layout_0.addWidget(self.timeinput)
        layout_0.addLayout(layout_ok)

        self.setLayout(layout_0)

    def newmemoname(self):
        return self.newmemo.text()
    def selectedmemo(self):
        return self.channelarea.currentItem()

    def updateChannels(self, channels):
        for c in channels:
            item = MemoListItem(c[0][1:],c[1])
            item.setTextColor(QtGui.QColor(self.theme["main/chums/userlistcolor"]))
            item.setIcon(QtGui.QIcon(self.theme["memos/memoicon"]))
            self.channelarea.addItem(item)

    def updateTheme(self, theme):
        self.theme = theme
        self.setStyleSheet(theme["main/defaultwindow/style"])
        for item in [self.userarea.item(i) for i in range(0, self.channelarea.count())]:
            item.setTextColor(QtGui.QColor(theme["main/chums/userlistcolor"]))
            item.setIcon(QtGui.QIcon(theme["memos/memoicon"]))

    @QtCore.pyqtSlot()
    def checkEmpty(self):
        newmemo = self.newmemoname()
        selectedmemo = self.selectedmemo()
        if newmemo or selectedmemo:
            self.accept()
    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def joinActivatedMemo(self, item):
        self.channelarea.setCurrentItem(item)
        self.accept()


class LoadingScreen(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent, (QtCore.Qt.CustomizeWindowHint |
                                              QtCore.Qt.FramelessWindowHint))
        self.mainwindow = parent
        self.setStyleSheet(self.mainwindow.theme["main/defaultwindow/style"])

        self.loadinglabel = QtGui.QLabel("CONN3CT1NG", self)
        self.cancel = QtGui.QPushButton("QU1T >:?", self)
        self.ok = QtGui.QPushButton("R3CONN3CT >:]", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SIGNAL('tryAgain()'))

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.loadinglabel)
        layout_1 = QtGui.QHBoxLayout()
        layout_1.addWidget(self.cancel)
        layout_1.addWidget(self.ok)
        self.layout.addLayout(layout_1)
        self.setLayout(self.layout)

    def hideReconnect(self):
        self.ok.hide()
    def showReconnect(self):
        self.ok.show()

    tryAgain = QtCore.pyqtSignal()

class AboutPesterchum(QtGui.QMessageBox):
    def __init__(self, parent=None):
        QtGui.QMessageBox.__init__(self, parent)
        self.setText("P3ST3RCHUM V. 3.14")
        self.setInformativeText("Programming by illuminatedwax (ghostDunk), art by Grimlive (aquaMarinist). Special thanks to ABT and gamblingGenocider.")
        self.mainwindow = parent

from PyQt4 import QtGui, QtCore
import urllib
import version

class BugReporter(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.mainwindow = parent
        self.setStyleSheet(self.mainwindow.theme["main/defaultwindow/style"])
        self.setWindowTitle("Report a Bug")
        self.setModal(False)

        self.title = QtGui.QLabel("Bug Report:")

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.title)

        layout_0.addWidget(QtGui.QLabel("Operating System (ex. Windows 7, Ubuntu 10.10):"))
        self.os = QtGui.QLineEdit(self)
        self.os.setStyleSheet("background:white; font-weight:bold; color:black; font-size: 10pt;")
        layout_0.addWidget(self.os)

        layout_0.addWidget(QtGui.QLabel("Description of bug:"))
        descLabel = QtGui.QLabel("Include as much information as possible\n(theme, related options, what you were doing at the time, etc.)")
        font = descLabel.font()
        font.setPointSize(8)
        descLabel.setFont(font)
        layout_0.addWidget(descLabel)

        self.textarea = QtGui.QTextEdit(self)
        self.textarea.setStyleSheet("background:white; font-weight:normal; color:black; font-size: 10pt;")

        layout_0.addWidget(self.textarea)

        self.ok = QtGui.QPushButton("SEND", self)
        self.ok.setDefault(True)
        self.connect(self.ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('sendReport()'))
        self.cancel = QtGui.QPushButton("CANCEL", self)
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        layout_2 = QtGui.QHBoxLayout()
        layout_2.addWidget(self.cancel)
        layout_2.addWidget(self.ok)

        layout_0.addLayout(layout_2)

        self.setLayout(layout_0)

    @QtCore.pyqtSlot()
    def sendReport(self):
        name = unicode(self.mainwindow.profile().handle)
        os = unicode(self.os.text())
        msg = unicode(self.textarea.toPlainText())

        if len(os) <= 0 or len(msg) <= 0:
            msgbox = QtGui.QMessageBox()
            msgbox.setStyleSheet(self.mainwindow.theme["main/defaultwindow/style"])
            msgbox.setText("You must fill out all fields first!")
            msgbox.setStandardButtons(QtGui.QMessageBox.Ok)
            ret = msgbox.exec_()
            return

        QtGui.QDialog.accept(self)
        data = urllib.urlencode({"name":name, "version": version._pcVersion, "os":os, "msg":msg})
        print "Sending..."
        f = urllib.urlopen("http://distantsphere.com/pc/reporter.php", data)
        text = f.read()
        print text
        if text == "success!":
            print "Sent!"
        else:
            print "Problems ):"


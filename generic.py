from PyQt4 import QtGui
class RightClickList(QtGui.QListWidget):
    def contextMenuEvent(self, event):
        #fuckin Qt
        if event.reason() == QtGui.QContextMenuEvent.Mouse:
            listing = self.itemAt(event.pos())
            self.setCurrentItem(listing)
            self.optionsMenu.popup(event.globalPos())


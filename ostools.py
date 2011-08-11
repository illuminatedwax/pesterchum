from os import path
from sys import platform
from PyQt4.QtGui import QDesktopServices

def isOSX():
    return platform == "darwin"

def isWin32():
    return platform == "win32"

def isOSXBundle():
    return isOSX() and path.abspath('.').find(".app")

def getDataDir():
    if isOSX():
        return path.join(str(QDesktopServices.storageLocation(QDesktopServices.DataLocation)), "Pesterchum/")
    else:
        return ''

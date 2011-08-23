import os, sys
import platform
from PyQt4.QtGui import QDesktopServices

def isOSX():
    return sys.platform == "darwin"

def isWin32():
    return sys.platform == "win32"

def isLinux():
    return sys.platform.startswith("linux")

def isOSXBundle():
    return isOSX() and (os.path.abspath('.').find(".app") != -1)

def osVer():
    if isWin32():
        return " ".join(platform.win32_ver())
    elif isOSX():
        ret = ""
        for i in platform.mac_ver():
            if type(i) == type(tuple()):
                for j in i:
                    ret += " %s" % (j)
            else:
                ret += " %s" % (i)
        return ret[1:]
    elif isLinux():
        return " ".join(platform.linux_distribution())

def getDataDir():
    if isOSX():
        return os.path.join(str(QDesktopServices.storageLocation(QDesktopServices.DataLocation)), "Pesterchum/")
    else:
        return ''

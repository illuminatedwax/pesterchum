import logging
import os
from string import Template
import json
import re
import codecs
import platform
from datetime import *
from time import strftime, time
from PyQt5 import QtGui, QtCore, QtWidgets
import sqlite3
import functools

import ostools
from mood import Mood
from dataobjs import PesterProfile, pesterQuirk, pesterQuirks
from parsetools import convertTags, addTimeInitial, themeChecker, ThemeException

_datadir = ostools.getDataDir()

class PesterLog(object):
    def __init__(self, handle, parent=None):
        global _datadir
        self.parent = parent
        self.handle = handle
        self.convos = {}
        self.logpath = _datadir+"logs"

    def log(self, handle, msg):
        if self.parent.config.time12Format():
            time = strftime("[%I:%M")
        else:
            time = strftime("[%H:%M")
        if self.parent.config.showSeconds():
            time += strftime(":%S] ")
        else:
            time += "] "
        if handle[0] == '#':
            if not self.parent.config.logMemos() & self.parent.config.LOG: return
            if not self.parent.config.logMemos() & self.parent.config.STAMP:
                time = ""
        else:
            if not self.parent.config.logPesters() & self.parent.config.LOG: return
            if not self.parent.config.logPesters() & self.parent.config.STAMP:
                time = ""
        if str(handle).upper() == "NICKSERV": return
        #watch out for illegal characters
        handle = re.sub(r'[<>:"/\\|?*]', "_", handle)
        bbcodemsg = time + convertTags(msg, "bbcode")
        html = time + convertTags(msg, "html")+"<br />"
        msg = time +convertTags(msg, "text")
        modes = {"bbcode": bbcodemsg, "html": html, "text": msg}
        if handle not in self.convos:
            time = datetime.now().strftime("%Y-%m-%d.%H.%M")
            self.convos[handle] = {}
            for (format, t) in modes.items():
                if not os.path.exists("%s/%s/%s/%s" % (self.logpath, self.handle, handle, format)):
                    os.makedirs("%s/%s/%s/%s" % (self.logpath, self.handle, handle, format))
                try:
                    fp = codecs.open("%s/%s/%s/%s/%s.%s.txt" % (self.logpath, self.handle, handle, format, handle, time), encoding='utf-8', mode='a')
                except IOError:
                    errmsg = QtWidgets.QMessageBox(self)
                    errmsg.setText("Warning: Pesterchum could not open the log file for %s!" % (handle))
                    errmsg.setInformativeText("Your log for %s will not be saved because something went wrong. We suggest restarting Pesterchum. Sorry :(" % (handle))
                    errmsg.show()
                    continue
                self.convos[handle][format] = fp
        for (format, t) in modes.items():
            f = self.convos[handle][format]
            if platform.system() == "Windows":
                f.write(t+"\r\n")
            else:
                f.write(t+"\r\n")
            f.flush()
    def finish(self, handle):
        if handle not in self.convos:
            return
        for f in list(self.convos[handle].values()):
            f.close()
        del self.convos[handle]
    def close(self):
        for h in list(self.convos.keys()):
            for f in list(self.convos[h].values()):
                f.close()

configsql = """
  CREATE TABLE IF NOT EXISTS config (
    name text UNIQUE,
    value text
  ) 
"""
profilesql = """
  CREATE TABLE IF NOT EXISTS profile (
    name text UNIQUE,
    value text
  ) 
"""
chumdbsql = """
  CREATE TABLE IF NOT EXISTS chumdb (
    handle text UNIQUE,
    value text
  ) 
"""

class userConfig(object):
    # Use for bit flag log setting
    LOG = 1
    STAMP = 2
    # Use for bit flag blink
    PBLINK = 1
    MBLINK = 2
    # Use for bit flag notfications
    SIGNIN = 1
    SIGNOUT = 2
    NEWMSG = 4
    NEWCONVO = 8
    INITIALS = 16

    def __init__(self, parent):
        self.parent = parent
        self.filename = os.path.join(_datadir, "pesterchum.db")
        self.conn = sqlite3.connect(self.filename, isolation_level=None)
        self.conn.execute(configsql) # bootstrap db
        
        if self.defaultprofile():
            self.userprofile = userProfile(self.defaultprofile())
        else:
            self.userprofile = None

        self.logpath = _datadir+"logs"

        if not os.path.exists(self.logpath):
            os.makedirs(self.logpath)

    def get(self, configname, default=None):
        try:
            self.conn.execute("SELECT value FROM config WHERE name = ?", (configname,))
            value, = self.conn.fetchone()
            return json.loads(value)
        except Exception:
            return default
    def set(self, name, value):
        jval = json.dumps(value)
        self.conn.execute("REPLACE INTO config (name, value) VALUES (?, ?)", (name, jval))

    def username(self):
        return self.get("username")
    def password(self):
        return self.get("password")
    def chums(self):
        return self.get("chums", [])
    def setChums(self, newchums):
        oldchums = self.chums()
        # Time to merge these two! :OOO
        for c in list(set(oldchums) - set(newchums)):
            newchums.append(c)
        self.set("chums", newchums)
    def addChum(self, chum):
        if type(chum) is PesterProfile:
            handle = chum.handle
        else:
            handle = chum
        newchums = list(set(self.chums() + [handle]))
        self.set("chums", newchums)
    def removeChum(self, chum):
        if type(chum) is PesterProfile:
            handle = chum.handle
        else:
            handle = chum
        newchums = list(set(self.chums()) - set([handle]))
        self.set("chums", newchums)
    def hideOfflineChums(self):
        return self.get("hideOfflineChums", False)
    def defaultprofile(self):
        return self.get("defaultprofile")
    def tabs(self):
        return self.get("tabs", True)
    def tabMemos(self):
        return self.get("tabmemos", self.tabs())
    def showTimeStamps(self):
        return self.get('showTimeStamps', True)
    def time12Format(self):
        return self.get('time12Format', True)
    def showSeconds(self):
        return self.get('showSeconds', False)
    def sortMethod(self):
        return self.get('sortMethod', 0)
    def showEmptyGroups(self):
        return self.get('emptyGroups', False)
    def showOnlineNumbers(self):
        return self.get('onlineNumbers', False)
    def logPesters(self):
        return self.get('logPesters', self.LOG | self.STAMP)
    def logMemos(self):
        return self.get('logMemos', self.LOG)
    def disableUserLinks(self):
        return not self.get('userLinks', True)
    def idleTime(self):
        return self.get('idleTime', 10)
    def minimizeAction(self):
        return self.get('miniAction', 0)
    def closeAction(self):
        return self.get('closeAction', 1)
    def opvoiceMessages(self):
        return self.get('opvMessages', True)
    def animations(self):
        return self.get('animations', True)
    def checkForUpdates(self):
        u = self.get('checkUpdates', 0)
        if type(u) == type(bool()):
            if u: u = 2
            else: u = 3
        return u
        # Once a day
        # Once a week
        # Only on start
        # Never
    def lastUCheck(self):
        return self.get('lastUCheck', 0)
    def checkMSPA(self):
        return self.get('mspa', False)
    def blink(self):
        return self.get('blink', self.PBLINK | self.MBLINK)
    def notify(self):
        return self.get('notify', True)
    def notifyType(self):
        return self.get('notifyType', "default")
    def notifyOptions(self):
        return self.get('notifyOptions', self.SIGNIN | self.NEWMSG | self.NEWCONVO | self.INITIALS)
    def lowBandwidth(self):
        return self.get('lowBandwidth', False)
    def ghostchum(self):
        return self.get('ghostchum', False)
    def getBlocklist(self):
        return self.get('block', [])
    def addBlocklist(self, handle):
        l = list(set(self.getBlocklist() + [handle]))
        self.set("block", l)
    def delBlocklist(self, handle):
        l = list(set(self.getBlocklist()) - set([handle]))
        self.set("block", l)
    def getExpandGroup(self):
        return self.get("expandGroup", [])
    def expandGroup(self, group, openGroup=True):
        s = set(self.getExpandGroup())
        if openGroup:
            s.add(group)
        else:
            s -= set([group])
        self.set("expandGroup", list(s))        

    def server(self):
        if hasattr(self.parent, 'serverOverride'):
            return self.parent.serverOverride
        # return self.get('server', 'irc.mindfang.org')
        return self.get('server', 'irc1.mindfang.org')
    def port(self):
        if hasattr(self.parent, 'portOverride'):
            return self.parent.portOverride
        #return self.get('port', '1413')
        return self.get('port', '1420')
    def soundOn(self):
        return self.get('soundon', True)
    def chatSound(self):
        return self.get('chatSound', True)
    def memoSound(self):
        return self.get('memoSound', True)
    def memoPing(self):
        return self.get('pingSound', True)
    def nameSound(self):
        return self.get('nameSound', True)
    def volume(self):
        return self.get('volume', 100)
    def trayMessage(self):
        return self.get('traymsg', True)
    def availableThemes(self):
        themes = []
        # Load user themes.
        for dirname, dirnames, filenames in os.walk(_datadir+'themes'):
            for d in dirnames:
                themes.append(d)
        # Also load embedded themes.
        if _datadir:
            for dirname, dirnames, filenames in os.walk('themes'):
                for d in dirnames:
                    if d not in themes:
                        themes.append(d)
        themes.sort()
        return themes
    def availableProfiles(self):
        profs = []
        profileloc = _datadir+'profiles'
        for dirname, dirnames, filenames in os.walk(profileloc):
            for filename in filenames:
                l = len(filename)
                if filename[l-3:l] == ".db":
                    profs.append(filename[0:l-3])
        profs.sort()
        return [userProfile(p) for p in profs]

class userProfile(object):
    def __init__(self, user):
        if type(user) is PesterProfile: # new profile
            self.handle = user.handle
            self.chat = user
            self.set("handle", user.handle)
            self.set("color", str(user.color.name()))
            self.theme = pesterTheme("pesterchum")
            self.quirks = pesterQuirks([])

            self.chat.mood = Mood(self.theme["main/defaultmood"])
            self.lastmood = self.chat.mood
        else: # existing profile
            self.handle = user
            self.lastmood = self.get("lastmood", Mood(self.theme["main/defaultmood"]))
            self.set("handle", user)
            self.chat = PesterProfile(user,
                                      QtGui.QColor(self.get("color")),
                                      self.lastmood)

    def get(self, name, default=None):
        handle = self.handle
        if handle[0:12] == "pesterClient":
            return
        try:
            self.conn.execute("SELECT value FROM profile WHERE name = ?", (configname,))
            value, = self.conn.fetchone()
            return json.loads(value)
        except Exception:
            return default
    def set(self, name, value):
        handle = self.handle
        if handle[0:12] == "pesterClient":
            return
        jval = json.dumps(value)
        self.conn.execute("REPLACE INTO profile (name, value) VALUES (?, ?)", (name, jval))

    @property
    def conn(self):
        handle = self.handle
        if handle[0:12] == "pesterClient":
            return
        if not getattr(self, "_conn", None):
            self._conn = sqlite3.connect(userProfile.profileDBFile(handle), isolation_level=None)
            self._conn.execute(profilesql)
        return self._conn

    def setMood(self, mood):
        self.chat.mood = mood

    @property
    def theme(self):
        if not getattr(self, "_theme", None):
            self._theme = pesterTheme(self.get("theme", "pesterchum"))
        return self._theme
    @theme.setter
    def theme(self, theme):
        self._theme = theme
        self.set("theme", theme.name)

    def setColor(self, color):
        self.chat.color = color
        self.set("color", color.name())

    @property
    def quirks(self):
        if not getattr(self, "_quirks", None):
            self._quirks = pesterQuirks(self.get("quirks", []))
        return self._quirks
    @quirks.setter
    def quirks(self, quirks):
        self._quirks = quirks
        self.set("quirks", self._quirks.plainList())

    @property
    def random(self):
        if not getattr(self, "_random", None):
            self._random = self.get("random", False)
        return self._random
    @random.setter
    def random(self, random):
        self._random = random
        self.set("random", random)

    @property
    def mentions(self):
        if not getattr(self, "_mentions", None):
            self._mentions = self.get("mentions", self.defaultMentions())
        return self._mentions
    @mentions.setter
    def mentions(self, mentions):
        try:
            for (i,m) in enumerate(mentions):
                re.compile(m)
        except re.error as e:
            logging.error("#%s Not a valid regular expression: %s" % (i, e))
        else:
            self._mentions = mentions
            self.set("mentions", mentions)

    def defaultMentions(self):
        initials = self.chat.initials()
        if len(initials) >= 2:
            initials = (initials, "%s%s" % (initials[0].lower(), initials[1]), "%s%s" % (initials[0], initials[1].lower()))
            return [r"\b(%s)\b" % ("|".join(initials))]
        else:
            return []
        
    @property
    def lastmood(self):
        if not getattr(self, "_lastmood", None):
            self._lastmood = self.get("lastmood", 0)
        return Mood(self._lastmood)
    @lastmood.setter
    def lastmood(self, mood):
        self._lastmood = mood.value()
        self.set("lastmood", self._lastmood)

    @property
    def autojoins(self):
        if not getattr(self, "_autojoins", None):
            self._autojoins = self.get("autojoins")
        return self._autojoins
    @autojoins.setter
    def autojoins(self, autojoins):
        self._autojoins = autojoins
        self.set("autojoins", autojoins)

    @staticmethod
    def profileDBFile(handle):
        return os.path.join(_datadir, "profiles", "%s.db" % (handle))

    @staticmethod
    def newUserProfile(chatprofile):
        if os.path.exists(userProfile.profileDBFile(chatprofile.handle)):
            newprofile = userProfile(chatprofile.handle)
        else:
            newprofile = userProfile(chatprofile)
        return newprofile

class PesterProfileDB(object):
    def __init__(self):
        self.logpath = os.path.join(_datadir, "logs")

        if not os.path.exists(self.logpath):
            os.makedirs(self.logpath)

        self.chumdb = {}
        self.conn = sqlite3.connect(os.path.join(self.logpath, "chums.db"), isolation_level=None)
        self.conn.execute(chumdbsql)

    def getValue(self, name, handle, default=None):
        if handle not in self.chumdb:
            try:
                self.conn.execute("SELECT value FROM chumdb WHERE handle = ?", (handle))
                value, = self.conn.fetchone()
                tmpdict = json.loads(value)
                tmpdict["color"] = QtGui.QColor(tmpdict.get("color", "#000000"))
                tmpdict["mood"] = Mood(tmpdict.get("mood", "offline"))
                self.chumdb[handle] = PesterProfile(handle, **tmpdict)
            except Exception:
                return default
        else:
            return getattr(self.chumdb[handle], name, default)
    def setValue(self, name, handle, value):
        if handle in chumdb:
            setattr(self.chumdb[handle], name, value)
        else:
            d = {name: value}
            self.chumdb[handle] = PesterProfile(handle, **d)
        jval = json.dumps(self.chumdb[handle].plaindict())
        self.conn.execute("REPLACE INTO chumdb (handle, value) VALUES (?, ?)", (handle, jval))

    def getColor(self, *x, **y):
        return self.getValue("color", *x, **y)
    def setColor(self, *x, **y):
        return self.setValue("color", *x, **y)
    def getNotes(self, *x, **y):
        return self.getValue("notes", *x, **y)
    def setNotes(self, *x, **y):
        return self.setValue("notes", *x, **y)

class pesterTheme(dict):
    def __init__(self, name, default=False):
        possiblepaths = (_datadir+"themes/%s" % (name),
                         "themes/%s" % (name),
                         _datadir+"themes/pesterchum",
                         "themes/pesterchum")
        self.path = "themes/pesterchum"
        for p in possiblepaths:
            if os.path.exists(p):
                self.path = p
                break

        self.name = name
        try:
            fp = open(self.path+"/style.js")
            theme = json.load(fp, object_hook=self.pathHook)
            fp.close()
        except IOError:
            theme = json.loads("{}")
        self.update(theme)
        if "inherits" in self:
            self.inheritedTheme = pesterTheme(self["inherits"])
        if not default:
            self.defaultTheme = pesterTheme("pesterchum", default=True)
    def __getitem__(self, key):
        keys = key.split("/")
        try:
            v = dict.__getitem__(self, keys.pop(0))
        except KeyError as e:
                if hasattr(self, 'inheritedTheme'):
                    return self.inheritedTheme[key]
                if hasattr(self, 'defaultTheme'):
                    return self.defaultTheme[key]
                else:
                    raise e
        for k in keys:
            try:
                v = v[k]
            except KeyError as e:
                if hasattr(self, 'inheritedTheme'):
                    return self.inheritedTheme[key]
                if hasattr(self, 'defaultTheme'):
                    return self.defaultTheme[key]
                else:
                    raise e
        return v
    def pathHook(self, d):
        for (k, v) in d.items():
            if type(v) is str:
                s = Template(v)
                d[k] = s.safe_substitute(path=self.path)
        return d
    def get(self, key, default):
        keys = key.split("/")
        try:
            v = dict.__getitem__(self, keys.pop(0))
            for k in keys:
                v = v[k]
            return default if v is None else v
        except KeyError:
            if hasattr(self, 'inheritedTheme'):
                return self.inheritedTheme.get(key, default)
            else:
                return default

    def has_key(self, key):
        keys = key.split("/")
        try:
            v = dict.__getitem__(self, keys.pop(0))
            for k in keys:
                v = v[k]
            return False if v is None else True
        except KeyError:
            if hasattr(self, 'inheritedTheme'):
                return key in self.inheritedTheme
            else:
                return False

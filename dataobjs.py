from PyQt4 import QtGui, QtCore
from datetime import *
import re

from generic import PesterIcon
from parsetools import timeDifference

class Mood(object):
    moods = ["chummy", "rancorous", "offline", "pleasant", "distraught", 
             "pranky", "smooth", "ecstatic", "relaxed", "discontent", 
             "devious", "sleek", "detestful", "mirthful", "manipulative",
             "vigorous", "perky", "acceptant", "protective", "mystified",
             "amazed", "insolent", "bemused" ]
    def __init__(self, mood):
        if type(mood) is int:
            self.mood = mood
        else:
            self.mood = self.moods.index(mood)
    def value(self):
        return self.mood
    def name(self):
        try:
            name = self.moods[self.mood]
        except IndexError:
            name = "chummy"
        return name
    def icon(self, theme):
        try:
            f = theme["main/chums/moods"][self.name()]["icon"]
        except KeyError:
            return PesterIcon(theme["main/chums/moods/chummy/icon"])
        return PesterIcon(f)

class pesterQuirk(object):
    def __init__(self, quirk):
        if type(quirk) != dict:
            raise ValueError("Quirks must be given a dictionary")
        self.quirk = quirk
        self.type = self.quirk["type"]
    def apply(self, string):
        if self.type == "prefix":
            return self.quirk["value"] + string
        if self.type == "suffix":
            return string + self.quirk["value"]
        if self.type == "replace":
            return string.replace(self.quirk["from"], self.quirk["to"])
        if self.type == "regexp":
            return re.sub(self.quirk["from"], self.quirk["to"], string)
    def __str__(self):
        if self.type == "prefix":
            return "BEGIN WITH: %s" % (self.quirk["value"])
        elif self.type == "suffix":
            return "END WITH: %s" % (self.quirk["value"])
        elif self.type == "replace":
            return "REPLACE %s WITH %s" % (self.quirk["from"], self.quirk["to"])
        elif self.type == "regexp":
            return "REGEXP: %s REPLACED WITH %s" % (self.quirk["from"], self.quirk["to"])

class pesterQuirks(object):
    def __init__(self, quirklist):
        self.quirklist = []
        for q in quirklist:
            if type(q) == dict:
                self.quirklist.append(pesterQuirk(q))
            elif type(q) == pesterQuirk:
                self.quirklist.append(q)
    def plainList(self):
        return [q.quirk for q in self.quirklist]
    def apply(self, string):
        # don't quirk /me commands
        if string[0:3] == "/me":
            space = string.find(" ")
            cmd = string[0:space]
            string = string[space:]
        else:
            cmd = ""
        presuffix = [q for q in self.quirklist if 
                     q.type=='prefix' or q.type=='suffix']
        replace = [q for q in self.quirklist if
                   q.type=='replace' or q.type=='regexp']
        for r in replace:
            string = r.apply(string)
        if not cmd:
            for ps in presuffix:
                string = ps.apply(string)
        string = cmd+string
        return string

    def __iter__(self):
        for q in self.quirklist:
            yield q

class PesterProfile(object):
    def __init__(self, handle, color=None, mood=Mood("offline"), chumdb=None):
        self.handle = handle
        if color is None:
            if chumdb:
                color = chumdb.getColor(handle, QtGui.QColor("black"))
            else:
                color = QtGui.QColor("black")
        self.color = color
        self.mood = mood
    def initials(self, time=None):
        handle = self.handle
        caps = [l for l in handle if l.isupper()]
        if not caps:
            caps = [""]
        initials = (handle[0]+caps[0]).upper()
        if hasattr(self, 'time') and time:
            if self.time > time:
                return "F"+initials
            elif self.time < time:
                return "P"+initials
            else:
                return "C"+initials
        else:
            return (handle[0]+caps[0]).upper() 
    def colorhtml(self):
        return self.color.name()
    def colorcmd(self):
        (r, g, b, a) = self.color.getRgb()
        return "%d,%d,%d" % (r,g,b)
    def plaindict(self):
        return (self.handle, {"handle": self.handle,
                              "mood": self.mood.name(),
                              "color": unicode(self.color.name())})
    def blocked(self, config):
        return self.handle in config.getBlocklist()

    def memsg(self, syscolor, suffix, msg, time=None):
        uppersuffix = suffix.upper()
        if time is not None:
            handle = "%s %s" % (time.temporal, self.handle)
            initials = time.pcf+self.initials()+time.number+uppersuffix
        else:
            handle = self.handle
            initials = self.initials()+uppersuffix
        return "<c=%s>-- %s%s <c=%s>[%s]</c> %s --</c>" % (syscolor.name(), handle, suffix, self.colorhtml(), initials, msg)
    def pestermsg(self, otherchum, syscolor, verb):
        return "<c=%s>-- %s <c=%s>[%s]</c> %s %s <c=%s>[%s]</c> at %s --</c>" % (syscolor.name(), self.handle, self.colorhtml(), self.initials(), verb, otherchum.handle, otherchum.colorhtml(), otherchum.initials(), datetime.now().strftime("%H:%M"))
    def moodmsg(self, syscolor, theme):
        return "<c=%s>-- %s <c=%s>[%s]</c> changed their mood to %s <img src='%s' /> --</c>" % (syscolor.name(), self.handle, self.colorhtml(), self.initials(), self.mood.name().upper(), theme["main/chums/moods"][self.mood.name()]["icon"])
    def memoclosemsg(self, syscolor, timeGrammar, verb):
        return "<c=%s><c=%s>%s%s%s</c> %s.</c>" % (syscolor.name(), self.colorhtml(), timeGrammar.pcf, self.initials(), timeGrammar.number, verb)
    def memoopenmsg(self, syscolor, td, timeGrammar, verb, channel):
        (temporal, pcf, when) = (timeGrammar.temporal, timeGrammar.pcf, timeGrammar.when)
        timetext = timeDifference(td)
        initials = pcf+self.initials()
        return "<c=%s><c=%s>%s</c> %s %s %s.</c>" % \
            (syscolor.name(), self.colorhtml(), initials, timetext, verb, channel[1:].upper().replace("_", " "))
    def memobanmsg(self, opchum, opgrammar, syscolor, timeGrammar):
        initials = timeGrammar.pcf+self.initials()+timeGrammar.number
        opinit = opgrammar.pcf+opchum.initials()+opgrammar.number
        return "<c=%s>%s</c> banned <c=%s>%s</c> from responding to memo." % \
            (opchum.colorhtml(), opinit, self.colorhtml(), initials)
    def memojoinmsg(self, syscolor, td, timeGrammar, verb):
        (temporal, pcf, when) = (timeGrammar.temporal, timeGrammar.pcf, timeGrammar.when)
        timetext = timeDifference(td)
        initials = pcf+self.initials()+timeGrammar.number
        return "<c=%s><c=%s>%s %s [%s]</c> %s %s." % \
            (syscolor.name(), self.colorhtml(), temporal, self.handle,
             initials, timetext, verb)

    @staticmethod
    def checkLength(handle):
        return len(handle) <= 256
    @staticmethod
    def checkValid(handle):
        caps = [l for l in handle if l.isupper()]
        if len(caps) != 1 or handle[0].isupper():
            return False
        if re.search("[^A-Za-z0-9]", handle) is not None:
            return False
        return True

class PesterHistory(object):
    def __init__(self):
        self.history = []
        self.current = 0
        self.saved = None
    def next(self, text):
        if self.current == 0:
            return None
        if self.current == len(self.history):
            self.save(text)
        self.current -= 1
        text = self.history[self.current]
        return text
    def prev(self):
        self.current += 1
        if self.current >= len(self.history):
            self.current = len(self.history)
            return self.retrieve()
        return self.history[self.current]
    def reset(self):
        self.current = len(self.history)
        self.saved = None
    def save(self, text):
        self.saved = text
    def retrieve(self):
        return self.saved
    def add(self, text):
        if len(self.history) == 0 or text != self.history[len(self.history)-1]:
            self.history.append(text)
        self.reset()

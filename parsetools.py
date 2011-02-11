import re
from copy import copy
from datetime import timedelta
from PyQt4 import QtGui

_ctag_begin = re.compile(r'(?i)<c=(.*?)>')
_ctag_end = re.compile(r'(?i)</c>')
_ctag_rgb = re.compile(r'\d+,\d+,\d+')
_urlre = re.compile(r"(?i)http://[^\s]+")
_memore = re.compile(r" (#[A-Za-z0-9_]+)")

def lexer(string, objlist):
    """objlist is a list: [(objecttype, re),...] list is in order of preference"""
    stringlist = [string]
    for (oType, regexp) in objlist:
        newstringlist = []
        for (stri, s) in enumerate(stringlist):
            if type(s) not in [str, unicode]:
                newstringlist.append(s)
                continue
            lasti = 0
            for m in regexp.finditer(s):
                start = m.start()
                end = m.end()
                tag = oType(m.group(0), *m.groups())
                if lasti != start:
                    newstringlist.append(s[lasti:start])
                newstringlist.append(tag)
                lasti = end
            if lasti < len(string):
                newstringlist.append(s[lasti:])
        stringlist = copy(newstringlist)
    return stringlist

class colorBegin(object):
    def __init__(self, string, color):
        self.string = string
        self.color = color
    def convert(self, format):
        color = self.color
        if _ctag_rgb.match(color) is not None:
            if format=='ctag':
                return "<c=%s>" % (color)
            try:
                qc = QtGui.QColor(*[int(c) for c in color.split(",")])
            except ValueError:
                qc = QtGui.QColor("black")
        else:
            qc = QtGui.QColor(color)
        if not qc.isValid():
            qc = QtGui.QColor("black")
        if format == "html":
            return '<span style="color:%s">' % (qc.name())
        elif format == "bbcode":
            return '[color=%s]' % (qc.name())
        elif format == "ctag":
            (r,g,b,a) = qc.getRgb()
            return '<c=%s,%s,%s>' % (r,g,b)
class colorEnd(object):
    def __init__(self, string):
        self.string = string
    def convert(self, format):
        if format == "html":
            return "</span>"
        elif format == "bbcode":
            return "[/color]"
        else:
            return self.string
class hyperlink(object):
    def __init__(self, string):
        self.string = string
    def convert(self, format):
        if format == "html":
            return "<a href='%s'>%s</a>" % (self.string, self.string)
        elif format == "bbcode":
            return "[url]%s[/url]" % (self.string)
        else:
            return self.string
class smiley(object):
    def __init__(self, string):
        self.string = string
    def convert(self, format):
        if format == "html":
            return "<img src='smilies/%s' />" % (smiledict[self.string])
        else:
            return self.string

def convertTags(string, format="html", quirkobj=None):
    if format not in ["html", "bbcode", "ctag"]:
        raise ValueError("Color format not recognized")
    lexlist = [(colorBegin, _ctag_begin), (colorEnd, _ctag_end),
               (hyperlink, _urlre), (hyperlink, _memore),
               (smiley, _smilere)]

    lexed = lexer(string, lexlist)
    balanced = []
    beginc = 0
    endc = 0
    for o in lexed:
        if type(o) is colorBegin:
            beginc += 1
            balanced.append(o)
        elif type(o) is colorEnd:
            if beginc >= endc:
                endc += 1
                balanced.append(o)
            else:
                balanced.append(o.string)
        else:
            balanced.append(o)
    if beginc > endc:
        for i in range(0, beginc-endc):
            balanced.append(colorEnd("</c>"))

    escaped = ""
    for o in balanced:
        if type(o) in [str, unicode]:
            if quirkobj:
                o = quirkobj.apply(o)
            if format == "html":
                escaped += o.replace("&", "&amp;").replace(">", "&gt;").replace("<","&lt;")
            else:
                escaped += o
        else:
            escaped += o.convert(format)
    return escaped


def addTimeInitial(string, grammar):
    endofi = string.find(":")
    endoftag = string.find(">")
    if endoftag < 0 or endoftag > 16 or endofi > 17:
        return string
    return string[0:endoftag+1]+grammar.pcf+string[endoftag+1:endofi]+grammar.number+string[endofi:]

def timeProtocol(cmd):
    dir = cmd[0]
    cmd = cmd[1:]
    cmd = re.sub("[^0-9:]", "", cmd)
    try:
        l = [int(x) for x in cmd.split(":")]
    except ValueError:
        l = [0,0]
    timed = timedelta(0, l[0]*3600+l[1]*60)
    if dir == "P":
        timed = timed*-1
    return timed

def timeDifference(td):
    if td < timedelta(0):
        when = "AGO"
    else:
        when = "FROM NOW"
    atd = abs(td)
    minutes = (atd.days*86400 + atd.seconds) // 60
    hours = minutes // 60
    leftoverminutes = minutes % 60
    if atd == timedelta(0):
        timetext = "RIGHT NOW"
    elif atd < timedelta(0,3600):
        if minutes == 1:
            timetext = "%d MINUTE %s" % (minutes, when)
        else: 
            timetext = "%d MINUTES %s" % (minutes, when)
    elif atd < timedelta(0,3600*100):
        if hours == 1 and leftoverminutes == 0:
            timetext = "%d:%02d HOUR %s" % (hours, leftoverminutes, when)
        else:
            timetext = "%d:%02d HOURS %s" % (hours, leftoverminutes, when)
    else:
        timetext = "%d HOURS %s" % (hours, when)
    return timetext


smiledict = {
    ":rancorous:": "pc_rancorous.gif",  
    ":apple:": "apple.gif",
    ":bathearst:": "bathearst.gif",
    ":pleasant:": "pc_pleasant.gif",
    ":blueghost:": "blueslimer.gif",
    ":candycorn:": "candycorn.gif",
    ":cheer:": "cheer.gif", 
    ":duhjohn:": "confusedjohn.gif",
    ":datrump:": "datrump.gif",
    ":facepalm:": "facepalm.gif",
    ":bonk:": "headbonk.gif",
    ":mspa:": "mspa_face.gif",
    ":gun:": "mspa_reader.gif",
    ":cal:": "lilcal.png",
    ":amazedfirman:": "pc_amazedfirman.gif",
    ":amazed:": "pc_amazed.gif",
    ":chummy:": "pc_chummy.gif",
    ":cool:": "pccool.gif",
    ":smooth:": "pccool.gif",
    ":distraughtfirman": "pc_distraughtfirman.gif",
    ":distraught:": "pc_distraught.gif",
    ":insolent:": "pc_insolent.gif",
    ":3:": "pckitty.gif",
    ":mystified:": "pc_mystified.gif",
    ":pranky:": "pc_pranky.gif",
    ":tense:": "pc_tense.gif",
    ":record:": "record.gif",
    ":squiddle:": "squiddle.gif",
    ":tab:": "tab.gif",
    ":beetip:": "theprofessor.gif",
    ":flipout:": "weasel.gif",
    ":befuddled:": "what.gif",
    ":pumpkin:": "whatpumpkin.gif",
    ":trollcool:": "trollcool.gif"}

_smilere = re.compile("|".join(smiledict.keys()))

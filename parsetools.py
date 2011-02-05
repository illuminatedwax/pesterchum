import re
from PyQt4 import QtGui

_ctag_begin = re.compile(r'<c=(.*?)>')
_ctag_rgb = re.compile(r'\d+,\d+,\d+')
_urlre = re.compile(r"(?i)(http://[^\s<]+)")

def convertTags(string, format="html"):
    if format not in ["html", "bbcode", "ctag"]:
        raise ValueError("Color format not recognized")
    def colorrepfunc(matchobj):
        color = matchobj.group(1)
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
    string = _ctag_begin.sub(colorrepfunc, string)
    endtag = {"html": "</span>", "bbcode": "[/color]", "ctag": "</c>"}
    string = string.replace("</c>", endtag[format])
    def urlrep(matchobj):
        if format=="html":
            return "<a href='%s'>%s</a>" % (matchobj.group(1).replace("&amp;", "&"), matchobj.group(1))
        elif format=="bbcode":
            return "[url]%s[/url]" % (matchobj.group(1).replace("&amp;", "&"))
        elif format=="ctag":
            return matchobj.group(1)
    string = _urlre.sub(urlrep, string)
    return string

def escapeBrackets(string):
    class beginTag(object):
        def __init__(self, tag):
            self.tag = tag
    class endTag(object):
        pass
    newlist = []
    begintagpos = [(m.start(), m.end()) for m in _ctag_begin.finditer(string)]
    lasti = 0
    for (s, e) in begintagpos:
        newlist.append(string[lasti:s])
        newlist.append(beginTag(string[s:e]))
        lasti = e
    if lasti < len(string):
        newlist.append(string[lasti:])
    tmp = []
    for o in newlist:
        if type(o) is not beginTag:
            l = o.split("</c>")
            tmp.append(l[0])
            l = l[1:]
            for item in l:
                tmp.append(endTag())
                tmp.append(item)
        else:
            tmp.append(o)
    btlen = 0
    etlen = 0
    retval = ""
    newlist = tmp
    for o in newlist:
        if type(o) is beginTag:
            retval += o.tag.replace("&", "&amp;")
            btlen +=1
        elif type(o) is endTag:
            if etlen >= btlen:
                continue
            else:
                retval += "</c>"
                etlen += 1
        else:
            retval += o.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if btlen > etlen:
        for i in range(0, btlen-etlen):
            retval += "</c>"
    return retval

import urllib
import re

USER_TYPE = "dev"

_pcMajor = "3.14"
_pcMinor = "2"
_pcStatus = "B" # A  = alpha
                # B  = beta
                # RC = release candidate
                # None = public release
_pcRevision = "3"
_pcVersion = ""

def pcVerCalc():
    global _pcVersion
    if _pcStatus:
        _pcVersion = "%s.%s-%s%s" % (_pcMajor, _pcMinor, _pcStatus, _pcRevision)
    else:
        _pcVersion = "%s.%s.%s" % (_pcMajor, _pcMinor, _pcRevision)

def verStrToNum(ver):
    w = re.match("(\d+\.?\d+)\.(\d+)-?([A-Za-z]{0,2})\.?(\d*):(\S+)", ver)
    if not w:
        print "Update check Failure: 3"; return
    full = ver[:ver.find(":")]
    return full,w.group(1),w.group(2),w.group(3),w.group(4),w.group(5)

def updateCheck():
    data = urllib.urlencode({"type" : USER_TYPE})
    try:
        f = urllib.urlopen("http://distantsphere.com/pesterchum.php?" + data)
    except:
        print "Update check Failure: 1"; return False,1
    newest = f.read()
    f.close()
    if not newest or newest[0] == "<":
        print "Update check Failure: 2"; return False,2
    try:
        (full, major, minor, status, revision, url) = verStrToNum(newest)
    except TypeError:
        return False,3
    print full
    if major <= _pcMajor:
        if minor <= _pcMinor:
            if status:
                if status <= _pcStatus:
                    if revision <= _pcRevision:
                        return False,0
            else:
                if not _pcStatus:
                    if revision <= _pcRevision:
                        return False,0
    print "A new version of Pesterchum is avaliable!"
    return full,url

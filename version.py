import urllib
import re
import time

USER_TYPE = "dev"

_pcMajor = "3.41"
_pcMinor = "0"
_pcStatus = "B" # A  = alpha
                # B  = beta
                # RC = release candidate
                # None = public release
_pcRevision = "5"
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

def updateCheck(q,num):
    time.sleep(3)
    data = urllib.urlencode({"type" : USER_TYPE})
    try:
        f = urllib.urlopen("http://distantsphere.com/pesterchum.php?" + data)
    except:
        print "Update check Failure: 1"; return q.put((False,1))
    newest = f.read()
    f.close()
    if not newest or newest[0] == "<":
        print "Update check Failure: 2"; return q.put((False,2))
    try:
        (full, major, minor, status, revision, url) = verStrToNum(newest)
    except TypeError:
        return q.put((False,3))
    print full
    if major <= _pcMajor:
        if minor <= _pcMinor:
            if status:
                if status <= _pcStatus:
                    if revision <= _pcRevision:
                        return q.put((False,0))
            else:
                if not _pcStatus:
                    if revision <= _pcRevision:
                        return q.put((False,0))
    print "A new version of Pesterchum is avaliable!"
    q.put((full,url))

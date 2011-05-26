import urllib

_pcMajor = "3.14"
_pcMinor = "2"
_pcStatus = "1" # 0 = alpha
                # 1 = beta
                # 2 = release candidate
                # 3 = public release
_pcRevision = "3"
_pcVersion = ""

def pcVerCalc():
    global _pcVersion
    _pcVersion = "%s.%s.%s-%s" % (_pcMajor, _pcMinor, _pcStatus, _pcRevision)

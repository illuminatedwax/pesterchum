def register(handle, username=None, password=None, anonymous=None, betakey=None):
    d = {"cmd": "register", "handle": handle}
    if username: d['username'] = username
    if password: d['password'] = password
    if anonymous is not None: d['anonymous'] = anonymous
    if betakey: d['betakey'] = betakey
    return d

def status(**kwargs):
    return kwargs.update({"cmd": "status"})

def friend(friends):
    return {"cmd": "friend", "handles": friends}

def msg(msg, handle=None, channel=None):
    d = {"cmd": "msg", "msg": msg}
    if handle:
        d['recp'] = handle
    elif channel:
        d['channel'] = channel
    return d

def begin(handle):
    return {"cmd": "begin", "recp": handle}

def cease(handle):
    return {"cmd": "cease", "recp": handle}

def color(color, handle=None, channel=None):
    d = {"cmd": "color", "color": color}
    if handle:
        d['recp'] = handle
    elif channel:
        d['channel'] = channel
    return d

def status(mood=None, away=None, invisible=None, tags=None):
    d = {"cmd": "status"}
    if mood is not None:
        d['mood'] = int(mood)
    if away is not None:
        d['away'] = bool(away)
    if invisible is not None:
        d['invisible'] = bool(invisible)
    if tags is not None:
        d['tags'] = list(tags)
    return d

def statusreq(handle=None, alt=None):
    d = {"cmd": "statusreq"}
    if handle:
        d['handle'] = handle
    else:
        d['alt'] = alt
    return d

def who(pattern=None, tags=None, limit=None, offset=None):
    d = {"cmd": "who"}
    # TODO: add this stuff
    return d

def list(search=None):
    d = {"cmd": "list"}
    if search:
        d['search'] = search
    return d

def join(channel, tmphandle=None, password=None):
    d = {"cmd": "join", "channel": channel}
    if tmphandle:
        d['tmphandle'] = tmphandle
    if password:
        d['password'] = password
    return d

def part(channel, tmphandle=None):
    d = {"cmd": "part", "channel": channel}
    if tmphandle:
        d['tmphandle'] = tmphandle
    return d

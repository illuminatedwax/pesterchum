import os, socket

def init():
    port = 9797
    try:
        with open(os.path.expanduser("~/.config/twmn/twmn.conf")) as f:
            for line in f.readlines():
                if line.startswith("port=") and \
                   line[5:-1].isdigit():
                    port = int(line[5:-1])
                    break
    except IOError:
        pass
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("127.0.0.1", port))

class Notification(object):
    def __init__(self, title="", msg="", icon=""):
        self.title = unicode(title)
        self.msg = unicode(msg)
        if icon.startswith("file://"):
            icon = icon[7:]
        self.icon = icon

    def show(self):
        s.send("<root><title>" + self.title + "</title><content>" + self.msg + "</content></root>")

if __name__ == "__main__":
    init()
    n = Notification("PyTwmn", "This is a notification!")
    n.show()

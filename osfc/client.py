# Stole some ideas from irc.py:
#  Copyright © 1999-2002 Joel Rosdahl 
#  Copyright © 2011-2014 Jason R. Coombs 
#  Copyright © 2009 Ferry Boender
#
# However, this is a single server library!
# We will never make multiple server connections.

import json
import socket
import logging

from . import protocol

#  client = osfc.client.OSFC()
#  server = client.server()
#  server.connect()
#  client.process_forever()
#  server.privmsg("a_nickname", "Hi there!")

class OSFC(object):
    def __init__(self, handlerObj):
        self.handler = handlerObj
    def connect(self, host, port, handle, username=None, password=None, anon=None, betakey=None):
        self.connection = OSFCServerConnection(host, port)
        self.handle = handle
        self.username = username
        self.password = password
        self.anon = anon
        self.betakey = betakey

        self.connection.connect()
        self.register(handle, username, password, anon, betakey)

    def register(self, handle, username=None, password=None, anon=None, betakey=None):
        self.send(protocol.register(handle, username, password, anon, betakey))

    def send(self, cmd):
        self.connection.send(cmd)
        
    def process_cmd(self, cmd):
        cmdname = cmd.get("cmd")
        errorid = cmd.get("errorid")
        if errorid:
            fnc = self.handler.get_error_handler(cmd)
            if callable(fnc):
                fnc(self.connection, cmd)
        else:
            fnc = self.handler.get_cmd_handler(cmdname)
            if callable(fnc):
                fnc(self.connection, cmd)        
    def process_forever(self):
        while 1:
            if not self.connection.connected:
                break
            try:
                for cmd in self.connection.read():
                    self.process_cmd(cmd)
            except Exception as e:
                    logging.error(e)
                    self.close()
                    raise
    def close(self):
        self.connection.close()


class OSFCBuffer(object):
    def __init__(self):
        self.buffer = b''
    def feed(self, bs):
        self.buffer += bs
    def responses(self):
        lines = self.buffer.split(b"\x00")
        self.buffer = lines.pop()
        for l in lines:
            try:
                obj = json.loads(l.decode("ascii"))
            except Exception as e:
                pass # do what??
            else:
                yield obj

class OSFCServerConnection(object):
    def __init__(self, host, port, timeout=120): 
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connected = False
        self.recvbuffer = OSFCBuffer()
        self.sendbuffer = b''
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("{0}".format(self.host), self.port))
        self.socket.settimeout(self.timeout)
        self.connected = True
    def read(self):
        try:
            out = self.socket.recv(1024)
        except socket.timeout as e:
            return iter([])
        except socket.error as e:
            raise
        if len(out) == 0:
            raise socket.error("Connection closed")
        self.recvbuffer.feed(out)
        return self.recvbuffer.responses()
    def send(self, sendobj):
        self.sendbuffer += bytes(json.dumps(sendobj), "ascii")
        self.sendbuffer += b'\x00'
        while len(self.sendbuffer):
            byteswritten = self.socket.send(self.sendbuffer)
            if byteswritten == 0:
                raise socket.error("Connection closed")
            self.sendbuffer = self.sendbuffer[byteswritten:]
    def close(self):
        # with extreme prejudice
        if self.socket:
            logging.info('shutdown socket')
            self.socket.shutdown(socket.SHUT_RDWR)
            self.connected = False
# TODO: throttler?

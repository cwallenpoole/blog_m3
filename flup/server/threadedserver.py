# Copyright (c) 2005 Allan Saddi <allan@saddi.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# $Id: threadedserver.py 1760 2005-04-15 06:56:38Z asaddi $

__author__ = 'Allan Saddi <allan@saddi.com>'
__version__ = '$Revision: 1760 $'

import socket
import select
import signal
import errno

from .threadpool import ThreadPool

__all__ = ['ThreadedServer']

class ThreadedServer(object):
    def __init__(self, jobClass=None, jobArgs=(), **kw):
        self._jobClass = jobClass
        self._jobArgs = jobArgs

        self._threadPool = ThreadPool(**kw)

    def run(self, sock, timeout=1.0):
        """
        The main loop. Pass a socket that is ready to accept() client
        connections. Return value will be True or False indiciating whether
        or not the loop was exited due to SIGHUP.
        """
        # Set up signal handlers.
        self._keepGoing = True
        self._hupReceived = False
        self._installSignalHandlers()

        # Main loop.
        while self._keepGoing:
            try:
                r, w, e = select.select([sock], [], [], timeout)
            except select.error as e:
                if e[0] == errno.EINTR:
                    continue
                raise

            if r:
                try:
                    clientSock, addr = sock.accept()
                except socket.error as e:
                    if e[0] in (errno.EINTR, errno.EAGAIN):
                        continue
                    raise

                if not self._isClientAllowed(addr):
                    clientSock.close()
                    continue

                # Hand off to Connection.
                conn = self._jobClass(clientSock, addr, *self._jobArgs)
                if not self._threadPool.addJob(conn, allowQueuing=False):
                    # No thread left, immediately close the socket to hopefully
                    # indicate to the web server that we're at our limit...
                    # and to prevent having too many opened (and useless)
                    # files.
                    clientSock.close()

            self._mainloopPeriodic()

        # Restore signal handlers.
        self._restoreSignalHandlers()

        # Return bool based on whether or not SIGHUP was received.
        return self._hupReceived

    def _mainloopPeriodic(self):
        """
        Called with just about each iteration of the main loop. Meant to
        be overridden.
        """
        pass

    def _exit(self, reload=False):
        """
        Protected convenience method for subclasses to force an exit. Not
        really thread-safe, which is why it isn't public.
        """
        if self._keepGoing:
            self._keepGoing = False
            self._hupReceived = reload

    def _isClientAllowed(self, addr):
        """Override to provide access control."""
        return True

    # Signal handlers

    def _hupHandler(self, signum, frame):
        self._hupReceived = True
        self._keepGoing = False

    def _intHandler(self, signum, frame):
        self._keepGoing = False

    def _installSignalHandlers(self):
        self._oldSIGs = [(x,signal.getsignal(x)) for x in
                         (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)]
        signal.signal(signal.SIGHUP, self._hupHandler)
        signal.signal(signal.SIGINT, self._intHandler)
        signal.signal(signal.SIGTERM, self._intHandler)

    def _restoreSignalHandlers(self):
        for signum,handler in self._oldSIGs:
            signal.signal(signum, handler)

if __name__ == '__main__':
    class TestJob(object):
        def __init__(self, sock, addr):
            self._sock = sock
            self._addr = addr
        def run(self):
            print("Client connection opened from %s:%d" % self._addr)
            self._sock.send('Hello World!\n')
            self._sock.setblocking(1)
            self._sock.recv(1)
            self._sock.close()
            print("Client connection closed from %s:%d" % self._addr)
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 8080))
    sock.listen(socket.SOMAXCONN)
    ThreadedServer(maxThreads=10, jobClass=TestJob).run(sock)

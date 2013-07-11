#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple UNIX daemons

Subclass the Daemon and implement the 'run' method

    from daemon import Daemon

    class MyDaemon(Daemon):
        def initialize(self, data):
            self.data = data

        def run(self):
            print(data)

    if __name__ == "__main__":
        daemon = MyDaemon(
            pidfile='/home/user/mydaemon.pid', stdout='/home/user/output.log')
        daemon.initialize('Hello World')

        daemon.start()

You can also use the stop(), restart() and status() operations.

Reference implementation:
    http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
"""

import sys
import os
import time
import atexit
import signal


class Daemon(object):
    """A generic daemon class.

    Subclass the Daemon class and override the run() method
    """

    pidfile_directories = [u'/var/run', u'/tmp']

    @classmethod
    def create(cls, name, **kwargs):
        """Fabricate a daemon by name in a (mostly) standar way.

        pidfile will be located at /var/run or /tmp
        depending on the user's privileges
        """
        pidfile_directory = [
            d for d in cls.pidfile_directories if os.access(d, os.W_OK)
        ][0]

        pidfile = os.path.join(pidfile_directory, name + '.pid')
        return cls(pidfile, **kwargs)

    def __init__(self, pidfile, stdin=None, stdout=None, stderr=None):
        """Initialize daemon. File descriptors default to /dev/null"""
        self.pidfile = pidfile
        self.stdin = stdin if stdin is not None else u'/dev/null'
        self.stdout = stdout if stdout is not None else u'/dev/null'
        self.stderr = stderr if stderr is not None else u'/dev/null'

    def daemonize(self):
        """Do the UNIX double-fork magic
        see Stevens' "Advanced Programming in the UNIX Environment" for details
        (ISBN 0201563177) http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        self._fork()

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        self._fork()  # do second fork

        self._redirect_file_descriptors()

        # write pidfile
        atexit.register(self.remove_pid)
        self.write_pid(os.getpid())

    def _fork(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # exit from parent
        except OSError as e:
            sys.stderr.write(
                u"fork failed: {} ({})\n".format(e.errno, e.strerror))
            sys.exit(1)

    def _redirect_file_descriptors(self):
        """Redirect standard file descriptors"""
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'ab+')
        se = open(self.stderr, 'ab+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def start(self):
        """Start the daemon """
        pid = self.read_pid()

        if pid is not None:
            message = u"pidfile {} already exist. Daemon already running?\n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def write_pid(self, pid):
        """Write the pid file"""
        with open(self.pidfile, 'w+') as stream:
            stream.write(u"{pid}\n".format(pid=pid))

    def remove_pid(self):
        """Remove pid file"""
        os.remove(self.pidfile)

    def read_pid(self):
        """Obtain pid from pidfile"""
        # Get the pid from the pidfile
        try:
            with open(self.pidfile, 'r') as stream:
                return int(stream.read().strip())
        except (IOError, OSError):
            pass

    def status(self):
        """Describe the daemon status"""
        pid = self.read_pid()
        return u'running pid: {}'.format(pid) if pid is not None else u'stopped'

    def kill(self, pid):
        """Finish the daemon"""
        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find(u"No such process") > 0:
                if os.path.exists(self.pidfile):
                    self.remove_pid()
            else:
                print(err)
                sys.exit(1)

    def stop(self):
        """Stop the daemon"""
        pid = self.read_pid()

        if pid is None:
            message = u"pidfile {} does not exist. Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return  # not an error in a restart

        self.kill(pid)

    def restart(self):
        """Restart the daemon """
        self.stop()
        self.start()

    def run(self):
        """Execute daemon logic
        You should override this method when you subclass Daemon.
        It will be called after the process
        has been daemonized by start() or restart().
        """
        raise NotImplementedError(u'You must implement run()')

    def initialize(self):
        """Initialize daemon data
        You may override this method when you subclass Daemon.
        It should be called manually along with the necessary data.
        """
        raise NotImplementedError(u'You must implement initialize()')

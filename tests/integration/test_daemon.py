# -*- coding: utf-8 -*-

import os

from hermes.daemon import Daemon

from hamcrest import assert_that, is_, none


PID = 2020
NEW_PID = 5050
PIDFILE_NAME = 'pidfile.pid'
FIXTURES = os.path.realpath('tests/fixtures')
PIDFILE = os.path.join(FIXTURES, 'pidfile.pid')

DAEMON_ARGS = [PIDFILE]


def create_pidfile(path, content):
    with open(path, 'w+') as stream:
        stream.write("{content}\n".format(content=content))


def remove_pidfile(path):
    try:
        os.remove(path)
    except OSError:
        pass


def read_pidfile(path):
    with open(path, 'r') as stream:
        return int(stream.read().strip())


class TestPIDFile(object):
    def test_read_pid_returns_none_if_no_pidfile(self):
        remove_pidfile(PIDFILE)
        daemon = Daemon(*DAEMON_ARGS)

        pid = daemon.read_pid()

        assert_that(pid, is_(none()))

    def test_read_pid_returns_integer_PID(self):
        daemon = Daemon(*DAEMON_ARGS)

        pid = daemon.read_pid()

        assert_that(pid, is_(PID))

    def test_write_pid_writes_integer_PID(self):
        remove_pidfile(PIDFILE)
        daemon = Daemon(*DAEMON_ARGS)

        daemon.write_pid(NEW_PID)

        assert_that(read_pidfile(PIDFILE), is_(NEW_PID))

    def test_write_pid_overwrites_integer_PID(self):
        daemon = Daemon(*DAEMON_ARGS)

        daemon.write_pid(NEW_PID)

        assert_that(read_pidfile(PIDFILE), is_(NEW_PID))

    def test_remove_pid_removes_pidfile(self):
        daemon = Daemon(*DAEMON_ARGS)

        daemon.remove_pid()

        assert_that(not os.path.exists(PIDFILE))

    def setup(self):
        create_pidfile(PIDFILE, PID)

    def teardown(self):
        remove_pidfile(PIDFILE)

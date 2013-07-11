# -*- coding: utf-8 -*-

from nose.tools import assert_raises

from hermes.daemon import Daemon

from hamcrest import assert_that, has_property, is_


PID = 2020
PIDFILE = 'pidfile.pid'
DAEMON_ARGS = [PIDFILE]


class TestDaemon(object):
    def test_daemon_sets_pidfile(self):
        daemon = Daemon(PIDFILE)

        assert_that(daemon, has_property('pidfile', is_(PIDFILE)))

    def test_daemon_sets_stdin(self):
        stdin = 'stdin'

        daemon = Daemon(*DAEMON_ARGS, stdin=stdin)

        assert_that(daemon, has_property('stdin', is_(stdin)))

    def test_daemon_sets_stdout(self):
        stdout = 'stdout'

        daemon = Daemon(*DAEMON_ARGS, stdout=stdout)

        assert_that(daemon, has_property('stdout', is_(stdout)))

    def test_daemon_sets_stderr(self):
        stderr = 'stderr'

        daemon = Daemon(*DAEMON_ARGS, stderr=stderr)

        assert_that(daemon, has_property('stderr', is_(stderr)))

    def test_daemon_defaults_stdin_to_dev_null(self):
        daemon = Daemon(*DAEMON_ARGS)

        assert_that(daemon, has_property('stdin'), is_('/dev/null'))

    def test_daemon_defaults_stdout_to_dev_null(self):
        daemon = Daemon(*DAEMON_ARGS)

        assert_that(daemon, has_property('stdout'), is_('/dev/null'))

    def test_daemon_defaults_stderr_to_dev_null(self):
        daemon = Daemon(*DAEMON_ARGS)

        assert_that(daemon, has_property('stderr'), is_('/dev/null'))

    def test_daemon_does_not_implements_run_method(self):
        daemon = Daemon(*DAEMON_ARGS)

        with assert_raises(NotImplementedError):
            daemon.run()

    def test_daemon_does_not_implements_initialize_method(self):
        daemon = Daemon(*DAEMON_ARGS)

        with assert_raises(NotImplementedError):
            daemon.initialize()

    def test_daemon_status_returns_running_if_pid(self):
        daemon = Daemon(*DAEMON_ARGS)
        daemon.read_pid = lambda: PID

        status = daemon.status()

        assert_that(status, is_('running pid: {}'.format(PID)))

    def test_daemon_status_returns_stopped_if_not_pid(self):
        daemon = Daemon(*DAEMON_ARGS)
        daemon.read_pid = lambda: None

        status = daemon.status()

        assert_that(status, is_('stopped'))

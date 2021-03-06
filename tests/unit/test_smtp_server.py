# -*- coding: utf-8 -*-

from doublex import Spy, called
from hamcrest import assert_that, has_property, has_item, is_

from nose.tools import nottest

from hermes.smtp import Server


PORT = 8888
LOCALHOST = '127.0.0.1'
ADDRESS = (LOCALHOST, PORT)


def server_args():
    return [ADDRESS]


class TestServer(object):
    def test_create_initializes_hooks(self):
        hook = lambda: None

        server = Server.create(*server_args(), hooks=[hook])
        server.close()

        assert_that(server, has_property('hooks', has_item(hook)))

    def test_process_message_calls_hook(self):
        with Spy() as spy:
            server = Server.create(*server_args(), hooks=[spy.hook])
            server.close()

        server.process_message(*[1, 2, 3, 4])

        assert_that(spy.hook, is_(called()))

    @nottest
    def test_process_message_calls_hook_with_same_args(self):
        args, kwargs = [1, 2], {'a': 1, 'b': 2}
        with Spy() as spy:
            server = Server.create(*server_args(), hooks=[spy.hook])
            server.close()

        server.process_message(*args, **kwargs)

        assert_that(spy.hook, is_(called().with_args(*args, **kwargs)))

    @nottest
    def test_process_message_calls_all_hooks_with_same_args(self):
        args, kwargs = [1, 2], {'a': 1, 'b': 2}

        def anything(*args, **kwargs):
            pass

        with Spy() as spy:
            server = Server.create(*server_args(), hooks=[anything, spy.hook])
            server.close()

        server.process_message(*args, **kwargs)

        assert_that(spy.hook, is_(called().with_args(*args, **kwargs)))

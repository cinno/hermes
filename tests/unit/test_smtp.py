# -*- coding: utf-8 -*-


from doublex import Spy, called
from hamcrest import assert_that, has_property, has_item, is_

from hermes.smtp import HookedSMTPServer


PORT = 8888
LOCALHOST = '127.0.0.1'


def server_args():
    return (LOCALHOST, PORT)


class TestServer(object):
    def test_create_initializes_hooks(self):
        hook = lambda: None

        server = HookedSMTPServer.create(*server_args(), hooks=[hook])
        server.close()

        assert_that(server, has_property('hooks', has_item(hook)))

    def test_process_message_calls_hook(self):
        with Spy() as spy:
            server = HookedSMTPServer.create(*server_args(), hooks=[spy.hook])
            server.close()

        server.process_message()

        assert_that(spy.hook, is_(called()))

    def test_process_message_calls_hook_with_same_args(self):
        args, kwargs = [1, 2], {'a': 1, 'b': 2}
        with Spy() as spy:
            server = HookedSMTPServer.create(*server_args(), hooks=[spy.hook])
            server.close()

        server.process_message(*args, **kwargs)

        assert_that(spy.hook, is_(called().with_args(*args, **kwargs)))

    def test_process_message_calls_all_hook_with_same_args(self):
        args, kwargs = [1, 2], {'a': 1, 'b': 2}

        def anything(*args, **kwargs):
            pass

        with Spy() as spy:
            server = HookedSMTPServer.create(*server_args(), hooks=[anything, spy.hook])
            server.close()

        server.process_message(*args, **kwargs)

        assert_that(spy.hook, is_(called().with_args(*args, **kwargs)))

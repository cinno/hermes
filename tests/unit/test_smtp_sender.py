# -*- coding: utf-8 -*-

import smtplib

from doublex import Spy, called
from hamcrest import assert_that, has_property, is_, is_not

from hermes.smtp import Sender

IP = '127.0.0.1'
PORT = 8888
ADDRESS = (IP, PORT)
SENDER = 'email@email.em'
RECIPIENTS = [SENDER]
MESSAGE = 'foo'


class TestSender(object):
    def test_sender_stores_server_address_when_created(self):
        sender = Sender(ADDRESS)

        assert_that(sender, has_property('address', is_(ADDRESS)))

    def test_sender_returns_a_connected_sender_when_accessing_connection(self):
        sender = Sender(ADDRESS)

        with sender.connection() as connection:
            assert_that(connection.connect, called().with_args(IP, PORT))

    def test_sender_quits_connection_after_usage(self):
        sender = Sender(ADDRESS)

        with sender.connection() as connection:
            pass

        assert_that(connection.quit, is_(called()))

    def test_sender_does_not_quits_connection_before_its_use(self):
        sender = Sender(ADDRESS)

        with sender.connection() as connection:
            assert_that(connection.quit, is_not(called()))

    def test_sender_uses_standar_sendmail_function_when_calling_send(self):
        sender = Sender(ADDRESS)

        sender.send(SENDER, RECIPIENTS, MESSAGE)

        assert_that(self.connection.sendmail, called().with_args(SENDER, RECIPIENTS, MESSAGE))

    def setup(self):
        self.connection = Spy(smtplib.SMTP)
        Sender.sender_class = lambda _: self.connection

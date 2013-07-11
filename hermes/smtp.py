#!/usr/bin/env python

import smtpd
import socket
import smtplib
import logging
import asyncore
import contextlib


log = logging.getLogger('hermes')


class Sender(object):
    sender_class = smtplib.SMTP

    def __init__(self, address):
        self.address = address

    def send(self, sender, recipients, message):
        with self.connection() as connection:
            connection.sendmail(sender, recipients, message)

    @contextlib.contextmanager
    def connection(self):
        try:
            connection = self.sender_class()

            try:
                connection.connect(*self.address)
                yield connection
            finally:
                connection.quit()

        except (socket.error, smtplib.SMTPException) as error:
            log.error(error)


    def process_message(self, *args, **kwargs):
        for hook in self.hooks:
            logging.info('Running hook {}'.format(hook))
            hook(*args, **kwargs)

    def run(self):
        try:
            asyncore.loop()
        except Exception:
            self.close()

    @classmethod
    def create(cls, ip, port, hooks):
        instance = cls((ip, port), None)
        instance.hooks = hooks
        return instance

# -*- coding: utf-8 -*-

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


class Server(smtpd.SMTPServer):
    def __init__(self, local_address, remote_address):
        smtpd.SMTPServer.__init__(self, local_address, remote_address)
        self.sender = None if remote_address is None else Sender(remote_address)

    def process_message(self, *args, **kwargs):
        for hook in self.hooks:
            logging.info('Running hook {}'.format(hook))
            hook(*args, **kwargs)

        if self.sender:
            self.sender.send(*args, **kwargs)

    def run(self):
        try:
            asyncore.loop()
        except Exception:
            self.close()

    @classmethod
    def create(cls, address, hooks, proxy_address=None):
        instance = cls(address, proxy_address)
        instance.hooks = hooks
        return instance

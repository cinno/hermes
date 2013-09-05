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

    def process_message(self, address, sender, recipients, message):
        log.info('Message from {} at {} to {}'.format(
            sender, address, recipients))

        for hook in self.hooks:
            log.debug('Running hook {}'.format(type(hook)))
            self.run_hook(hook, address, sender, recipients, message)

        if self.sender:
            log.info('Proxying message to relay server at {}'
                     .format(self._remoteaddr))
            self.sender.send(sender, recipients, message)

    def run(self):
        log.info('Starting server at {}'.format(self._localaddr))
        try:
            asyncore.loop()
        except Exception:
            self.close()

    def run_hook(self, hook, address, sender, recipients, message):
        try:
            hook(address, sender, recipients, message)
        except Exception as error:
            log.error('Failed to run {}. {}: {}'.format(
                repr(type(hook)), type(error), error), exc_info=True)

    @classmethod
    def create(cls, address, hooks, proxy_address=None):
        instance = cls(address, proxy_address)
        instance.hooks = hooks
        return instance

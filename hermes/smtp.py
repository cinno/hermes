#!/usr/bin/env python

import smtpd
import logging
import asyncore


class HookedSMTPServer(smtpd.SMTPServer):
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

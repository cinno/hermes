# -*- coding: utf-8 -*-

import logging

from .base import Extension

log = logging.getLogger('hermes')


# TODO: Test this
class Printer(Extension):

    template = u"""FROM: {sender}
TO: {recipients}
IP: {address}
MESSAGE:
    {message}"""

    def __call__(self, address, sender, recipients, message):
        log.info(self.template.format(address=address, sender=sender,
                                      recipients=recipients, message=message))

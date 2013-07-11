# -*- coding: utf-8 -*-


class Extension(object):
    def __call__(self, address, sender, recipients, message):
        raise NotImplementedError('Not implemented')

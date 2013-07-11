# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse

from stevedore import extension

from .daemon import Daemon
from .smtp import Server

log = logging.getLogger('hermes')

_LOGGING_FMT_ = '%(asctime)s %(levelname)-8s %(message)s'


class MailDaemon(Daemon):
    def initialize(self, server_instance):
        self.server_instance = server_instance

    def run(self):
        try:
            print(u'Running server {}\n'.format(self.server_instance))
            self.server_instance.run()
        except Exception as error:
            log.error((Exception, error))


def public_ip():
    try:
        import subprocess
        return subprocess.call("/sbin/ifconfig").split("\n")[1].split()[1][5:]
    except Exception:
        import socket
        return socket.gethostbyname(socket.gethostname())


def create_server(args):
    # restrict extensions to the ones listed in hooks
    hooks = [obj for name, obj in args.extensions.items() if name in args.hooks]

    try:
        print(u'Starting SMTP server at {}:{}'.format(args.ip, args.port))
        return Server.create((args.ip, args.port), hooks, args.proxy_address)
    except PermissionError as error:
        print(u'Not enough privileges to run on {}:{}. {}'
              .format(args.ip, args.port, error))
        sys.exit(1)
    except OSError as error:
        print(u'Could not run daemon on {}:{}. {}'
              .format(args.ip, args.port, error))
        sys.exit(1)


def load_extensions():
    manager = extension.ExtensionManager(namespace='hermes.extensions.processors', invoke_on_load=True)
    return {extension.name: extension.obj for extension in manager.extensions}


def parse_args(extensions):
    parser = argparse.ArgumentParser()

    parser.add_argument("action", choices=['start', 'stop', 'restart', 'status', 'hooks'])
    parser.add_argument("--ip", default=public_ip(), help=u"Server public ip")
    parser.add_argument("--port", default=25, type=int, help=u"Server specific port (default: 25)")
    parser.add_argument("--stdout", default=None, help=u"Redirect standar output to a file")
    parser.add_argument("--stderr", default=None, help=u"Redirect standar error output to a file")
    parser.add_argument("--proxy", default=None, metavar='ADDR',
                        help=u"Proxy messages to another SMPT server (ip:port)")
    parser.add_argument("--hook", action='append', dest='hooks', default=[],
                        help=u"Loads and hooks the given message processor (one of: {}) "
                        "use it multiple times".format(extensions))

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verbose", action="store_true", default=False, help="Verbose output")
    group.add_argument("--silent", action="store_true", default=False, help="Less verbose output")

    args = parser.parse_args()
    args.extensions = extensions
    args.proxy_address = args.proxy.split(':') if args.proxy else None

    return args


def validate_args(args):
    unknown_hook_names = set(args.hooks) - set(args.extensions)
    if unknown_hook_names:
        print('Unknown hook names:\n {}'.format(", ".join(unknown_hook_names)))
        print('Should be one of:\n {}'.format(", ".join(args.extensions)))
        sys.exit(1)

    return args


def configure_logging(args):
    verbosity = logging.DEBUG if args.verbose else logging.INFO
    verbosity = logging.WARNING if args.silent else verbosity
    logging.basicConfig(level=verbosity, format=_LOGGING_FMT_)


def daemon_arguments(args):
    return dict(
        name=u'mailpit-{port}'.format(port=args.port),  # one daemon per port (different pidfile)
        stdout=os.path.realpath(args.stdout) if args.stdout else None,
        stderr=os.path.realpath(args.stderr) if args.stderr else None
    )


def start(args):
    daemon = MailDaemon.create(**daemon_arguments(args))
    daemon.initialize(create_server(args))
    daemon.start()


def stop(args):
    daemon = MailDaemon.create(**daemon_arguments(args))
    daemon.stop()


def restart(args):
    stop(args)
    start(args)


def status(args):
    daemon = MailDaemon.create(**daemon_arguments(args))
    print(daemon.status())


def list_hooks(args):
    if args.extensions:
        print("\n".join(args.extensions))


def main():
    args = validate_args(parse_args(load_extensions()))

    configure_logging(args)

    actions = dict(stop=stop, start=start, restart=restart, status=status, hooks=list_hooks)
    action = actions[args.action]
    action(args)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import logging.config
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
    except (IOError, OSError) as error:
        print(u'Could not run daemon on {}:{}. {}'
              .format(args.ip, args.port, error))
        sys.exit(1)


def load_extensions():
    manager = extension.ExtensionManager(namespace='hermes.extensions.processors', invoke_on_load=True)
    return {extension.name: extension.obj for extension in manager.extensions}


def parse_args(extensions):
    parser = argparse.ArgumentParser()

    parser.add_argument("action", choices=['run', 'start', 'stop', 'restart', 'status', 'hooks'])
    parser.add_argument("--ip", default=None, help=u"Server public ip")
    parser.add_argument("--port", default=None, type=int, help=u"Server specific port (default: 25)")
    parser.add_argument("--stdout", default=None, help=u"Redirect standar output to a file")
    parser.add_argument("--stderr", default=None, help=u"Redirect standar error output to a file")
    parser.add_argument("--config", default=None, help=u"Loads configuration from JSON file")
    parser.add_argument("--proxy", default=None, metavar='IP:PORT',
                        help=u"Proxy messages to another SMPT server (ip:port)")
    parser.add_argument("--hook", action='append', dest='hooks', default=[],
                        help=u"Load message processor by name. Can be used multiple times."
                        " the 'printer' processor is always attached".format(extensions))

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verbose", action="store_true", default=None, help="Verbose output")
    group.add_argument("--silent", action="store_true", default=None, help="Less verbose output")

    args = parser.parse_args()
    update_args_from_config(args)
    set_args_default_values(args)

    args.extensions = extensions

    validate_args(args)

    return args


def set_args_default_values(args):
    args.hooks = set(['printer'] + args.hooks)
    args.port = 25 if args.port is None else args.port
    args.ip = public_ip() if args.ip is None else args.ip
    args.stderr = 'error.log' if args.stderr is None else args.stderr
    args.proxy_address = args.proxy.split(':') if args.proxy else None
    args.stdout = 'output.log' if args.stdout is None else args.stdout

    return args


def update_args_from_config(args):
    if args.config is not None:
        with open(args.config, 'r') as stream:
            config = json.load(stream)

        for key, value in config.items():
            if getattr(args, key, value) is None:  # Do not override user input
                setattr(args, key, value)


def validate_args(args):
    unknown_hook_names = set(args.hooks) - set(args.extensions)
    if unknown_hook_names:
        print('Unknown hook names:\n {}'.format(", ".join(unknown_hook_names)))
        print('Should be one of:\n {}'.format(", ".join(args.extensions)))
        sys.exit(1)

    return args


def configure_logging(args):
    verbosity = 'DEBUG' if args.verbose else 'INFO'
    verbosity = 'WARNING' if args.silent else verbosity

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'precise': {
                'format': '%(asctime)s %(name)s %(levelname)s | %(message)s'
            }
        },
        'handlers': {
            'console': {
                'formatter': 'precise',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'hermes': {
                'level': 'INFO',
                'level': verbosity,
                'handlers': ['console']
            }
        }
    })


def daemon_arguments(args):
    return dict(
        name=u'hermes-{port}'.format(port=args.port),  # one daemon per port (different pidfile)
        stdout=os.path.realpath(args.stdout) if args.stdout else None,
        stderr=os.path.realpath(args.stderr) if args.stderr else None
    )


def run(args):
    server = create_server(args)
    server.run()


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
    args = parse_args(load_extensions())

    configure_logging(args)

    actions = dict(run=run, stop=stop, start=start, restart=restart, status=status, hooks=list_hooks)
    action = actions[args.action]
    action(args)


if __name__ == "__main__":
    main()

# Hermes: Mail trap

`Hermes` is a programmable SMTP server. 

It can act like a *mail trap* in order to register, log, destroy, redirect, rewrite or mangle
emails.

- Test against a real SMTP server, no just a mock object.
- Avoid accidents, annoying development-spam and email avalanches.
- Measure your application's  email behaviour.
- Avoid ugly conditional code and environmental dependencies.

Just setup `Hermes` as your application email server and all mails will be logged by default.

You can load code extensions to process messages and to control how the server should respond.

## Usage

To start the daemon use the `hermes` command line tool which is installed altogether.

	usage: hermes {start,stop,restart,status,hooks}
				  [-h] [--ip IP] [--port PORT] [--stdout STDOUT] [--stderr STDERR]
				  [--config CONFIG] [--proxy IP:PORT] [--hook HOOKS] 
				  [--verbose | --silent]

### Start server

	$ hermes start

This will start the mail daemon on the machine's public ip and port 25 which is SMTP default's. 
`Hermes` makes its best effort in order to obtain the machine's public ip automatically, so the server can be accessed from the outside.
However if this fails, it will use localhost, thus serving local requests only.

### Local server

	$ hermes start --ip 127.0.0.1 --port 8080

This will start a local server using a port within the user range.

### Multiple servers

You can have lots of `Hermes` daemons around by just by binding them to different ports.

	$ hermes start
	$ hermes start --port 8080

	$ hermes status
	running pid: 2782
	$ hermes status --port 8080
	running pid: 3210

Beware that daemons are identified by the port which they are binded to.

## Extensions

Custom code can be easily loaded by name on the command line:


	$ hermes start --hook printer
This loads printer, which will log and output all received emails and is loaded by default.

To list all the available extensions use the `hermes hooks` command.

	$ hermes hooks
	 printer


An extension is some code which is called per each email.
To write one, just extend the `Basel` class in `hermes/extensions/base.py`
and register the new plugin along with a name in the `setup.py` file. eg:


`hermes/extensions/printer.py`
```python
# -*- coding: utf-8 -*-

import logging

from .base import Extension

log = logging.getLogger('hermes')


class Printer(Extension):

    template = u"""FROM: {sender}
TO: {recipients}
IP: {address}
MESSAGE:
    {message}"""

    def __call__(self, address, sender, recipients, message):
        log.info(self.template.format(address=address, sender=sender,
                                      recipients=recipients, message=message))
```

`setup.py`
```
import os

from setuptools import setup, find_packages


setup(

...
    
	entry_points={

    	...

        'hermes.extensions.processors': [
            'printer = hermes.extensions.printer:Printer'
        ]
    },
)

```

### Get mails actually delivered

`Hermes` can proxy to a relay server by setting the `--proxy` option.

    $ hermes start --proxy my.mail.ip:25

It reads the relay server configuration ip:port and routes all emails to it.

## Configuration

Instead of using the command line, a custom configuration can be used in JSON format.

    $ hermes start --config hermes.json

The configuration file looks like this:

    {
        "ip": "192.168.1.25",
        "port": "25",
        "stdout": "/path/to/file",
        "stderr": "/path/to/file",
        "proxy": "my.mail.ip:25",
        "hooks": [
            'printer',
        ],
        "verbose": true
    }

## Installation

	python setup.py install

## Development

It should work flawlessly under 2.7 and 3.3

1. Create a virtualenv and activate it
	virtualenv hermes
	workon hermes

2. Install development requirements

	(hermes)$ pip install -r dev-requirements.txt

3. Install the application in development mode

	(hermes)$ python setup.py develop

4. Test with tox, which will run nosetests per each env
	(hermes)$ tox

## TODO: What's ahead?

- Write proxy as an extension
- Add mailboxes and store emails if needed.
- Add REST api to check and retrieve sent emails.
- Add simple client to consume the REST api.
- Add support for authentication on the relay server

# Hermes: Mail trap

`Hermes` is a programmable SMTP server. 
It can act like a *mail trap* in order to register, log, destroy, redirect, rewrite or mangle
emails.

Just setup `Hermes` as your application smtp server and all mails will be held and logged by default.
You can use various hooks to control how the server should respond.


## Usage

To start the daemon use the `hermes` command line tool which is installed altogether.

	usage: hermes [-h] [--ip IP] [--port PORT] [--stdout STDOUT] [--stderr STDERR] {start,stop,restart,status}

### Start server

	$ hermes start

This will start the mail daemon on the machine's public ip and port 25 which is SMTP default's. 
You need root access in order to bind to that port.

	$ hermes start --ip 127.0.0.1 --port 8080

This will start a local server in an available port in the user range.
`Hermes` makes its best effort in order to obtain the machine's public ip, so the server can be accessed. 
However if this fails, it will use localhost, thus serving local requests only.

### Multiple servers

You can have lots of `Hermes` daemons around just by binding them on different ports.

	$ hermes start

	$ hermes status
	running pid: 2782

	$ hermes start --port 8080

	$ hermes status --port 8080
	running pid: 3210

Beware that daemons are identificated by the port which the server is binded to.


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

4. Run tests
	(hermes)$ nosetests

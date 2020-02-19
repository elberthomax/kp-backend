#!/usr/bin/python3
import logging, sys
logging.basicConfig(stream=sys.stderr)

from kpabsensi import app as application
application.secret_key = 'Add your secret key'

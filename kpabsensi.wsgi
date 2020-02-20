#!/usr/bin/python3
import logging, sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/kpabsensi")

from kpabsensi import app as application
application.secret_key = 'Add your secret key'

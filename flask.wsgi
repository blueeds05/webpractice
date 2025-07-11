import os, sys

# edit your path below
sys.path.append("/home/riveredge.heliohost.us/httpdocs/app_01");

sys.path.insert(0, os.path.dirname(__file__))
from app_webpractice import app as application

# set this to something harder to guess
application.secret_key = 'Secret606560'
# get-pip.py
import os
from urllib.request import urlopen

exec(urlopen("https://bootstrap.pypa.io/get-pip.py").read())
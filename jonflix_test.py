# -*- coding: utf-8 -*-

from pprint import pprint
import json
import re
import os
import datetime
import urllib
import urllib2
import HTMLParser
import sys

import urllib
import urllib2

url = 'http://france.jonstones.com/api/info.json'

response = urllib2.urlopen(url)
data = json.loads(response.read())
pprint(data)
for key in data.keys(): print key


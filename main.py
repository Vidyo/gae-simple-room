#!/usr/bin/env python

# Copyright 2016 Vidyo Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# [START imports]
import os
import urllib2
import base64
import binascii
from datetime import datetime
import calendar
import time
import hashlib
import hmac
import sys
import random

# from google.appengine.ext import ndb

import jinja2
import webapp2

# Developer specific parameters
VIDYO_IO_DEVELOPER_KEY = "7de6100c55254f678335a4e94ad1291b"
VIDYO_IO_APPLICATION_ID = "7cb733.vidyo.io"
TOKEN_VALID_DURATION_SECS = 600

EPOCH_SECONDS = 62167219200
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]


def getVidyoIOToken(userName):
    type = 'provision'
    key = VIDYO_IO_DEVELOPER_KEY
    jid = userName + "@" + VIDYO_IO_APPLICATION_ID
    expires = TOKEN_VALID_DURATION_SECS + EPOCH_SECONDS + \
        int(time.mktime(datetime.now().timetuple()))
    vCard = ""

    def to_bytes(o):
        return str(o).encode("utf-8")

    sep = b"\0"  # Separator is a NULL character
    body = to_bytes(type) + sep + to_bytes(jid) + sep + \
        to_bytes(expires) + sep + to_bytes(vCard)
    mac = hmac.new(bytearray(key, 'utf8'), msg=body,
                   digestmod=hashlib.sha384).digest()
    # Combine the body with the hex version of the mac
    serialized = body + sep + binascii.hexlify(mac)
    b64 = base64.b64encode(serialized)
    token = b64.encode("utf8")
    encoded_token = urllib2.quote(token)
    return encoded_token

# [START main_page]


class MainPage(webapp2.RequestHandler):

    def get(self):
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]

# [START Room]


class Room(webapp2.RequestHandler):

    def get(self, roomId):
        # RoomID must not have spaces or special characters. Base64 encode will
        # ensure that.
        roomIdBase64AndEncoded = urllib2.quote(base64.b64encode(roomId))
        # Pick the VidyoIO client version or select latest
        version = self.request.get('version', 'latest')
        # Create a random username for each user
        username = ''.join(random.choice('0123456789ABCDEF')
                           for i in range(16))

        encoded_token = getVidyoIOToken(username)
        url_vidyoio = "https://static.vidyo.io/" + version + "/connector/VidyoConnector.html?host=vidyostaging.io&resourceId=" + \
            roomIdBase64AndEncoded + "&token=" + encoded_token + \
            "&hideConfig=1&" + self.request.query_string
        template_values = {
            'url_vidyoio': url_vidyoio,
        }
        template = JINJA_ENVIRONMENT.get_template('room.html')
        self.response.write(template.render(template_values))

# [END Room]

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/([^/]+)?', Room),
], debug=True)
# [END app]

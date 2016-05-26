#!/usr/bin/env python

import base64
import httplib2

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from email.mime.text import MIMEText
from oauth_util import Credentials


OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'


class GmailClient(object):

    def __init__(self,argparser=None):
        """Initialize API client."""
        credentials = Credentials(name='gmail',scope=OAUTH_SCOPE,argparser=argparser).get()
        self.service = build('gmail', 'v1', http=credentials.authorize(httplib2.Http()))

    def send_message(self,to,subject,body):
        """Send a message."""
        mime_message = MIMEText(body)
        #mime_message['from'] = from_
        mime_message['to'] = to
        mime_message['subject'] = subject
        raw_message = {'raw':base64.b64encode(mime_message.as_string())}
        message = self.service.users().messages().send(userId='me',body=raw_message).execute()
        print message['id']
        return message

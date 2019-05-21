#!/usr/bin/env python

import httplib2

from apiclient.discovery import build
from apiclient.http import MediaFileUpload,MediaIoBaseUpload
from oauth_util import Credentials
from StringIO import StringIO


OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'


class DriveClient(object):

    def __init__(self,argparser=None,client_args={}):
        """Initialize API client."""
        credentials = Credentials(name='drive',scope=OAUTH_SCOPE,argparser=argparser).get()
        self.service = build('drive', 'v2', http=credentials.authorize(httplib2.Http(**client_args)))

    def get_file(self,file_name):
        """Get file(s) by remote name."""
        result = []
        page_token = None
        while True:
            if page_token is not None:
                files = self.service.files().list(q="title='%s'"%file_name,pageToken=page_token).execute()
            else:
                files = self.service.files().list(q="title='%s'"%file_name).execute()
            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            if page_token is None:
                break
        return result

    def upload(self,file_name,mime_type,title=None,description=None,parent_ids=None):
        """Alias for upload_file."""
        return self.upload_file(file_name,mime_type,title,description,parent_ids)

    def upload_file(self,file_name,mime_type,title=None,description=None,parent_ids=None):
        """Upload a file by name."""
        if title is None:
            title = file_name
        if description is None:
            description = title
        body = {
            'title': title,
            'description': description,
            'mimeType': mime_type
        }
        if parent_ids is not None:
            if isinstance(parent_ids,list):
                body['parents'] = [{'id':parent_id} for parent_id in parent_ids if isinstance(parent_id,basestring)]
            elsif isinstance(parent_ids,basestring):
                body['parents'] = [{'id':parent_ids}]
        media_body = MediaFileUpload(file_name, mimetype=mime_type)
        return self.service.files().insert(body=body, media_body=media_body, convert=True).execute()

    def upload_string(self,contents,mime_type,title,description=None,parent_ids=None):
        """Upload a string."""
        if description is None:
            description = title
        body = {
            'title': title,
            'description': description,
            'mimeType': mime_type
        }
        if parent_ids is not None:
            if isinstance(parent_ids,list):
                body['parents'] = [{'id':parent_id} for parent_id in parent_ids if isinstance(parent_id,basestring)]
            elsif isinstance(parent_ids,basestring):
                body['parents'] = [{'id':parent_ids}]
        media_body = MediaIoBaseUpload(StringIO(contents),mimetype=mime_type)
        return self.service.files().insert(body=body, media_body=media_body, convert=True).execute()

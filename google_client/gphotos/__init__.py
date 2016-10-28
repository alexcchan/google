#!/usr/bin/env python

import atom
import gdata.photos.service
import httplib2
import os

from datetime import datetime
from pprint import pprint
from oauth_util import Credentials
from StringIO import StringIO
from timezones import UTC


OAUTH_SCOPE = 'https://picasaweb.google.com/data/'


class PhotosClient(object):

    def __init__(self,argparser=None,client_args={}):
        """Initialize API client."""
        credentials = Credentials(name='photos',scope=OAUTH_SCOPE,argparser=argparser).get()
        http_client = credentials.authorize(httplib2.Http(**client_args))
        class Adapter(object):
            def __init__(self,http):
                self.http = http
            def request(self,operation,url,data=None,headers=None):
                if str(url).startswith('https://picasaweb.google.com'):
                    uri = str(url)
                else:
                    uri = 'https://picasaweb.google.com' + str(url)
                class ResponseAdapter(object):
                    def __init__(self,response,content):
                        self.status = int(response['status'])
                        self.reason = response.reason
                        self.content = response
                    def read(self):
                        return content
                if operation == 'POST':
                    if isinstance(data,basestring):
                        body = data
                    elif isinstance(data,StringIO):
                        body = data.getvalue()
                    elif isinstance(data,atom.Entry):
                        if headers is None:
                            headers = {}
                        headers['content-type'] = 'application/atom+xml'
                        body = unicode(data)
                    elif isinstance(data,list):
                        body = ''
                        for part in data:
                            if isinstance(part,basestring):
                                body += part
                            elif isinstance(part,StringIO):
                                body += part.getvalue()
                            else:
                                body += str(data)
                else:
                    body = data
                response,content = self.http.request(uri=uri,method=operation,body=body,headers=headers)
                return  ResponseAdapter(response,content)
        self.service = gdata.photos.service.PhotosService(http_client=Adapter(http_client))
        self.service.email = 'default'

    def get_albums(self):
        """Get a list of albums (generator)."""
        albums = self.service.GetUserFeed()
        for album in albums.entry:
            yield album

    def create_album(self,title,summary=None):
        """Create an album."""
        return self.service.InsertAlbum(title=title,summary=summary,location=None,access='private',commenting_enabled='true',timestamp=None)

    def get_photos(self,album):
        """Get a list of photos (generator)."""
        if isinstance(album,basestring):
            album_id = album
        else:
            album_id = album.gphoto_id.text
        photos = self.service.GetFeed('/data/feed/api/user/default/albumid/%s?kind=photo' % album_id)
        for photo in photos.entry:
            yield photo

    def upload_photo(self,album,file,content_type=None,title=None,summary=None):
        """Upload a photo."""
        if isinstance(album,basestring):
            if '/' in album:
                album_id = album.split('/')[-1]
            else:
                album_id = album
            album_uri = '/data/feed/api/user/default/albumid/%s' % album
        elif isinstance(album,atom.Entry):
            album_uri = album.id.text
        if isinstance(file,basestring):
            if title is None:
                title = file.split('/')[-1]
            file_handle = open(file)
        else:
            if title is None:
                title = 'Photo uploaded at %s' % datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            file_handle = file
        return self.service.InsertPhotoSimple(album_or_uri=album_uri,title=title,summary=summary,filename_or_handle=file_handle,content_type=content_type)

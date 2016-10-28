import httplib2
try:
        import simplejson as json
except:
        import json


from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials


OAUTH_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'
DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'


class LanguageError(Exception):

    def __init__(self,msg,error_code=None):
        self.msg = msg
        self.error_code = error_code

    def __str__(self):
        return repr('%s: %s' % (self.error_code, self.msg))


class LanguageClient(object):

    def __init__(self,client_args={}):
        credentials = GoogleCredentials.get_application_default().create_scoped(OAUTH_SCOPE)
        http = httplib2.Http(**client_args)
        credentials.authorize(http)
        self.service = discovery.build('language','v1beta1',http=http,discoveryServiceUrl=DISCOVERY_URL)

    def get_entities(self,document):
        """Get named entites in document."""
        request_body={'document':{'type':'PLAIN_TEXT','content':document.encode('utf-8')},'encodingType':'UTF8'}
        service_request = self.service.documents().analyzeEntities(body=request_body)
        try:
            response_body = service_request.execute()
        except HttpError as e:
            raise LanguageError(e._get_reason().strip(),e.resp.status)
        return response_body['entities']

    def get_sentiment(self,document):
        """Get sentiment in document as polarity and magnitude."""
        request_body={'document':{'type':'PLAIN_TEXT','content':document.encode('utf-8')}}
        service_request = self.service.documents().analyzeSentiment(body=request_body)
        try:
            response_body = service_request.execute()
        except HttpError as e:
            raise LanguageError(e._get_reason().strip(),e.resp.status)
        return response_body['documentSentiment']

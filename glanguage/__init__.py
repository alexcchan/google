import httplib2
try:
        import simplejson as json
except:
        import json


from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


OAUTH_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'
DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'


class LanguageClient(object):

    def __init__(self):
        credentials = GoogleCredentials.get_application_default().create_scoped(OAUTH_SCOPE)
        http = httplib2.Http()
        credentials.authorize(http)
        self.service = discovery.build('language','v1beta1',http=http,discoveryServiceUrl=DISCOVERY_URL)

    def get_entities(self,document):
        """Get named entites in document."""
        request_body={'document':{'type':'PLAIN_TEXT','content':document.encode('utf-8')},'encodingType':'UTF8'}
        service_request = self.service.documents().analyzeEntities(body=request_body)
        response_body = service_request.execute()
        return response_body['entities']

    def get_sentiment(self,document):
        """Get sentiment in document as polarity and magnitude."""
        request_body={'document':{'type':'PLAIN_TEXT','content':document.encode('utf-8')}}
        service_request = self.service.documents().analyzeSentiment(body=request_body)
        response_body = service_request.execute()
        return response_body['documentSentiment']

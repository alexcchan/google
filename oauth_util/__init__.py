import httplib2

APPENGINE = False
try:
  from oauth2client.contrib.appengine import CredentialsModel
  from oauth2client.contrib.appengine import StorageByKeyName
  APPENGINE = True
except ImportError:
  pass
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage


class Credentials(object):
  """This is a wrapper for oauth2client which will store the named access/refresh token in either a local file or App Engine singleton."""

  def __init__(self,name,scope,secrets_file_name='client_secrets.json',cache_file_name=None,argparser=None):
    self.name = name
    self.scope = scope
    self.secrets_file_name = secrets_file_name
    if cache_file_name is None:
      if name is None:
        self.cache_file_name = 'credentials_cache.json'
      else:
        self.cache_file_name = '%s_credentials_cache.json' % name
    else:
      self.cache_file_name = cache_file_name
    self.argparser = argparser

  def get(self):
    """Fetch, authorize, refresh token."""
    def get_file_storage():
      return Storage(self.cache_file_name)
    def get_storage():
      if APPENGINE:
        return StorageByKeyName(CredentialsModel, self.name, 'credentials')
      else:
        return get_file_storage()
    storage = get_storage()
    credentials = storage.get()
    if credentials is None or credentials.invalid:
      if APPENGINE:
        credentials = get_file_storage().get()
        if credentials is not None and not credentials.invalid:
          credentials.set_store(storage)
        credentials.refresh(httplib2.Http())
      else:
        flow = flow_from_clientsecrets(filename=self.secrets_file_name,scope=self.scope)
        from oauth2client import tools
        if self.argparser is None:
          self.argparser = tools.argparser
        credentials = tools.run_flow(flow=flow, storage=storage, flags=self.argparser.parse_args())
    else:
      credentials.refresh(httplib2.Http())
    return credentials

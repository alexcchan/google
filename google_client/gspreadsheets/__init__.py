#!/usr/bin/env python

import gdata.gauth
import gdata.spreadsheets.client
import gdata.spreadsheets.data

from oauth_util import Credentials


OAUTH_SCOPE = 'https://spreadsheets.google.com/feeds'


class SimpleSpreadsheet(object):
  """A simple Google spreadsheet client."""

  def __init__(self, spreadsheet_key, worksheet_id='od6', argparser=None):
    """Initialize API client."""
    self.spreadsheet_key = spreadsheet_key
    self.worksheet_id = worksheet_id
    self.client = None
    self.get_client(argparser)

  def get_client(self, argparser=None):
    """Initialize and return client."""
    if self.client is None:
      credentials = Credentials(name='spreadsheets',scope=OAUTH_SCOPE,argparser=argparser).get()
      token = gdata.gauth.OAuth2Token(client_id=credentials.client_id,
                                      client_secret=credentials.client_secret,
                                      scope=OAUTH_SCOPE,
                                      user_agent='Python',
                                      access_token=credentials.access_token,
                                      refresh_token=credentials.refresh_token)
      self.client = gdata.spreadsheets.client.SpreadsheetsClient()
      token.authorize(self.client)
    return self.client

  def get_rows(self):
    """Get rows in spreadsheet as a list of dicts."""
    list = self.client.get_list_feed(spreadsheet_key=self.spreadsheet_key,
                                     worksheet_id=self.worksheet_id)
    rows = []
    for list_entry in list.entry:
      rows.append(list_entry.to_dict())
    return rows

  def add_row(self, row):
    """Add a row to the spreadsheet."""
    list_entry = gdata.spreadsheets.data.ListEntry()
    list_entry.from_dict(row)
    self.client.add_list_entry(list_entry=list_entry,
                               spreadsheet_key=self.spreadsheet_key,
                               worksheet_id=self.worksheet_id)

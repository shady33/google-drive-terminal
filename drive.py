#!/usr/bin/python

import httplib2
import pprint

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from apiclient import errors

def write_file(file_name,content):
	file=open(file_name,'w')
	file.write(content)
	file.close()


def download_file(service, drive_file,file_name):
  """Download a file's content.

  Args:
    service: Drive API service instance.
    drive_file: Drive File instance.

  Returns:
    File's content if successful, None otherwise.
  """
  download_url = drive_file.get('downloadUrl')
  print download_url
  if download_url:
    resp, content = service._http.request(download_url)
    print resp.status
    if resp.status == 200:
      print 'Status: %s' % resp
      write_file(file_name,content)
    else:
      print 'An error occurred: %s' % resp
      return None
  else:
    # The file doesn't have any content stored on Drive.
    return None

f=open('credentials.txt','r')
credential=f.read().splitlines()
# Copy your credentials from the console
CLIENT_ID = credential[0]
CLIENT_SECRET = credential[1]

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + authorize_url
code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

# Insert a file
#media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
body = {
'title': 'My document',
'description': 'A test document',
'mimeType': 'text/plain'
}

#file = drive_service.files().insert(body=body, media_body=media_body).execute()
#pprint.pprint(file)

result = []
page_token = None
while True:
	try:
	  param = {}
	  #if page_token:
	  param['q'] = credential[2] + " in parents"
	  files = drive_service.files().list(**param).execute()
	  #files = drive_service.files().list(fileId='').execute()
	  for filex in files['items']:
	  	print filex['title']
	  	download_file(drive_service,filex,filex['title'])
	  #result.extend(files['items'])
	  #page_token = files.get('nextPageToken')
	  #if not page_token:
	  break
	except errors.HttpError, error:
	  print 'An error occurred: %s' % error
	  break
print result
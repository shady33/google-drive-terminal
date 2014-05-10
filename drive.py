#!/usr/bin/python

import httplib2
import pprint
import sys

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from apiclient import errors
from oauth2client.file import Storage

def insert_file(service, title, description, parent_id, mime_type, filename):
  
  media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=False)
  body = {
    'title': title,
    'description': description,
    'mimeType': mime_type
  }
  # Set the parent folder.
  if parent_id:
    body['parents'] = [{'id': parent_id}]

  try:
    file = service.files().insert(
        body=body,
        media_body=media_body).execute()

    return file
  except errors.HttpError, error:
    print 'An error occured: %s' % error
    return None

def update_file(service, file_id, new_title, new_description, new_mime_type,
                new_filename, new_revision):

  try:
    # First retrieve the file from the API.
    file = service.files().get(fileId=file_id).execute()

    # File's new metadata.
    file['title'] = new_title
    file['description'] = new_description
    file['mimeType'] = new_mime_type

    # File's new content.
    media_body = MediaFileUpload(
        new_filename, mimetype=new_mime_type, resumable=True)

    # Send the request to the API.
    updated_file = service.files().update(
        fileId=file_id,
        body=file,
        newRevision=new_revision,
        media_body=media_body).execute()
    return updated_file
  except errors.HttpError, error:
    print 'An error occurred: %s' % error
    return None

def write_file(file_name,content):

	file=open(file_name,'w')
	file.write(content)
	file.close()

def download_file(service, drive_file,file_name):

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



if len(sys.argv) > 1:
    print "Argument Given:"+sys.argv[1]
else:
    print "Please enter a argument"
    sys.exit()

f=open('credentials.txt','r')
credential=f.read().splitlines()
# Copy your credentials from the console
CLIENT_ID = credential[0]
CLIENT_SECRET = credential[1]

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
storage = Storage('a_credentials_file')
try:
  credentials = storage.get()
except:
  print "error"
  # Run through the OAuth flow and retrieve credentials
  flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
  authorize_url = flow.step1_get_authorize_url()
  print 'Go to the following link in your browser: ' + authorize_url
  code = raw_input('Enter verification code: ').strip()
  credentials = flow.step2_exchange(code)
  storage.put(credentials)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

if sys.argv[1]== "pull":
  result = []
  page_token = None
  while True:
	 try:
	  param = {}
	  #if page_token:
	  param['q'] = "'"+credential[2] + "' in parents"
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
elif sys.argv[1]=="push":
  update_file(drive_service, credential[2], "new_title", "new_description", "text/xml",
                "filename", "new_revision")
  #insert_file(drive_service, "title", "description", "0B2UfUTlp455beWRHb3doMWZCeGc", "text/xml", "filename")


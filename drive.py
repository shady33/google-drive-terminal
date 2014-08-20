#!/usr/bin/python

import httplib2
import pprint
import sys
import os
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from apiclient import errors
from oauth2client.file import Storage
import os.path
import magic
from datetime import datetime

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

def write_file(file_name,content,mode):

	file=open(file_name,mode)
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
      write_file(file_name,content,"w")
    else:
      print 'An error occurred: %s' % resp
      return None
  else:
    # The file doesn't have any content stored on Drive.
    return None

def authenticate():
  f=open('.drive/credentials.txt','r')
  credential=f.read().splitlines()
  f.close()
  CLIENT_ID = credential[0]
  CLIENT_SECRET = credential[1]

  OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
  REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
  storage = Storage('.drive/a_credentials_file')
  credentials = storage.get()
  
  if credentials == None:
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)
  return credentials

def connect():
  credentials=authenticate()
  http = httplib2.Http()
  http = credentials.authorize(http)
  drive_service = build('drive', 'v2', http=http)
  return drive_service

# __init__
if len(sys.argv) > 1:
    print "Argument Given:"+sys.argv[1]
else:
    print "Please enter a argument"
    sys.exit()

if sys.argv[1]=="init":
  directory=os.getcwd()+"/.drive"
  if not os.path.exists(directory):
    os.makedirs(directory)
    print "Initialized the directory"

elif sys.argv[1]=="origin":
  if len(sys.argv) > 2:
    url=sys.argv[2].split("/")[4]
    write_file(".drive/credentials.txt",url,"a")
    authenticate()
  else:
    print "Enter the url"

elif sys.argv[1]=="add":
  if len(sys.argv) > 2:
    fname=os.getcwd()+"/.drive/fnames"
    if not os.path.isfile(fname):
      write_file(fname,sys.argv[2]+"\n",'w')
    else:
      f=open('.drive/fnames','r')
      pathnames=f.read().splitlines()
      try:
        if not filter(lambda x: sys.argv[2] in x, pathnames)[0] == sys.argv[2]:
          write_file(fname,sys.argv[2]+"\n",'a')
        else:
          print "Already in file"
      except:
        write_file(fname,sys.argv[2]+"\n",'a')
  else:
    print "Add a filename"  

#root in place of credentials[2]
elif sys.argv[1]== "pull":
  drive_service=connect()
  f=open('.drive/credentials.txt','r')
  credential=f.read().splitlines()
  f.close()
  try:
    param = {}
    if credential[2]=="":
    	location="root"
    else:
    	location=credential[2]
    	
    param['q'] = "'"+ location + "' in parents"
    files = drive_service.files().list(**param).execute()
    if len(sys.argv) > 2:
      if sys.argv[2]=="all":
        for filex in files['items']:
          print filex['title']
          download_file(drive_service,filex,filex['title'])
    else:
      for filex in files['items']:
        print filex['title']
        f=open('.drive/fnames','r')
        pathnames=f.read().splitlines()
        try:
          if filter(lambda x: filex['title'] in x, pathnames)[0] == filex['title']:
            download_file(drive_service,filex,filex['title'])
        except:
          print ""
  	  
	  break
  except errors.HttpError, error:
    print 'An error occurred: %s' % error
	   
elif sys.argv[1]=="push":
  drive_service=connect()
  f=open('.drive/credentials.txt','r')
  credential=f.read().splitlines()
  f.close()
  date=datetime.utcnow().strftime("%Y%m%d")

  mimetype=magic.from_file(sys.argv[2], mime=True)
  update_file(drive_service, credential[2], sys.argv[2], "file updated on "+date, mimetype,
                sys.argv[2], "new_revision")

elif sys.argv[1]=="upload":
  drive_service=connect()
  f=open('.drive/credentials.txt','r')
  credential=f.read().splitlines()
  f.close()
  mimetype=magic.from_file(sys.argv[2], mime=True)
  insert_file(drive_service,sys.argv[2], "Uploaded from drive terminal", credential[2], mimetype, sys.argv[2])

#!/usr/bin/python

import httplib
import httplib2
import os
import random
import sys
import time

import pdb

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "/home/justin/YouTube-batch-upload/api-samples/python/client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print "Uploading file..."
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print "Video id '%s' was successfully uploaded." % response['id']
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print error
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print "Sleeping %f seconds and then retrying..." % sleep_seconds
      time.sleep(sleep_seconds)

if __name__ == '__main__':

  # These aren't used. We overwrite 'args' below. I left them in bc argparser
  # seems to be a special object from oauth2client.tools.
  argparser.add_argument("--file", help="Video file to upload")
  argparser.add_argument("--title", help="Video title", default="Test Title")
  argparser.add_argument("--description", help="Video description",
    default="Test Description")
  argparser.add_argument("--category", default="22",
    help="Numeric video category. " +
      "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
  argparser.add_argument("--keywords", help="Video keywords, comma separated",
    default="")
  argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
    default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
  args = argparser.parse_args()


  # pdb.set_trace()
  
#  if not os.path.exists(args.file):
#    exit("Please specify a valid file using the --file= parameter.")



  ###############################################

  import csv
  from pprint import pprint
  import textwrap
  import datetime

  filename = 'CCDC Seminars - Seminars (1).csv'
  f = open(filename,'rU')


  # Video categories: https://gist.github.com/dgp/1b24bf2961521bd75d6c
  # 28 - Science & Technology  <-- this one seems good.
  # 27 - Education


  cols = [
      'Talk Video',
      'Talk Title',
      'Speaker Name',
      'Speaker Organization',
      'Date start',
      'Speaker Bio',
      'Talk Abstract',
      'Seminar Series',
      'Video URL'
      ]



  for nline,line in enumerate(csv.reader(f)):
    print('CSV Line {}: Starting.'.format(nline))
    if nline == 0:
      inds = {k:line.index(k) for k in cols}
      continue

    # if nline <= 106: continue # failed on csv line X. don't re-upload anything before then.

    # Don't re-upload if the URL already exists.
    vid_url = line[inds['Video URL']].strip()
    if len(vid_url) > 0:
      print('CSV line {}: Skipping existing YouTube video "{}"'.format(nline,vid_url))
      continue 

    # For now, only upload CCDC Seminars. No ECE236 lectures.
    seminar_type = line[inds['Seminar Series']].strip()
    if len(seminar_type) == 0 or seminar_type != 'CCDC Seminar':
      print('CSV line {}: Skipping non-CCDC-seminar type "{}"'.format(nline,seminar_type))
      continue

    file = line[inds['Talk Video']].strip()
    absfile = os.path.join('/media/justin/ccdc_vid_backup/videos_seminars/',file)
    title = line[inds['Talk Title']].strip()
    name = line[inds['Speaker Name']].strip()
    date = line[inds['Date start']].strip()

    if len(file) <= 0 or len(title) <= 0 or len(name) <= 0 or len(date) <= 0:
      print('CSV line {}: No file, title, name, or date: Skipping line "{}"'.format(nline,line))
      continue
    if ' ' not in name:
      print('CSV line {}: no space char in name "{}", probably not a real name. Skipping.'.format(nline,name))
      continue
    if not os.path.exists(absfile):
      print('CSV line {}: local video file "{}" no exist, skipping.'.format(nline,absfile))
      continue

    date = datetime.datetime.strptime(date,'%m/%d/%Y %H:%M:%S').strftime('%b %d, %Y')

    abstract = line[inds['Talk Abstract']].strip()
    bio = line[inds['Speaker Bio']].strip()
    org = line[inds['Speaker Organization']].strip()



    description = '''Research Seminar at the Center for Controls, Dynamical Systems, and Computation

Seminar speaker: {speaker} {org}
Title: {title}
Date: {date}
Host: University of California, Santa Barbara
            '''.format(
               speaker=name,
               date=date,
               title=title,
               org = '({})'.format(org) if len(org)>0 else ''
               )

    description = textwrap.dedent(description)

    if len(abstract) > 0 and abstract != 'seminar flyer (pdf)': description += '\nAbstract: {}\n'.format(abstract)
    if len(bio) > 0 : description += '\nSpeaker Bio: {}\n'.format(bio)

    description += '\nCopyright 2017 University of California. All rights reserved.'
    
    keywords = 'UCSB,CCDC,Engineering'
    category = '28' # Science & Technology
    priv = 'private'

    d = {}
    d['file']           = absfile
    d['title']          = title if len(title)<100 else (title[:95] + '...')  # YouTube 100-char limit on title lengths. Otherwise: "The request metadata specifies an invalid or empty video title."
    d['description']    = description
    d['keywords']       = keywords
    d['category']       = category
    d['privacyStatus']  = priv

    print('=======================================')

    # print(description)

    pprint(d)

    args.file = d['file']
    args.title = d['title']
    args.description = d['description']
    args.keywords = d['keywords']
    args.category = d['category']
    args.privacyStatus = d['privacyStatus']

    print('About to upload...')
    #######################################################

    youtube = get_authenticated_service(args)
    while True:
      try:
        initialize_upload(youtube, args)
        break;
      except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        print('Sleeping for 30 mins...')
        time.sleep(30*60)
        print('Retrying...')



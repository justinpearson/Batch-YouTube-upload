# Batch-YouTube-upload
A Python program to upload several video files to YouTube using Google's YouTube Data API.


## Table of Contents
- [Summary](#summary)
- [Background](#background)
- [Installation](#installation)
- [Test: Upload one video](#test-upload-one-video)
- [Upload multiple videos](#upload-multiple-videos)
- [Errors](#errors)

## Summary

This program uploads a bunch of video files to YouTube. You fill out a
CSV file with video filenames, titles, and descriptions, and the
program uploads each video to YouTube with that title and description.

I wrote this to upload several hundred 1-hour-long videos of professors' research seminars at my university.

This program just combines Google's YouTube API tutorial and sample
code for the YouTube Data API on GitHub:

- <https://developers.google.com/youtube/v3/guides/uploading_a_video>
- <https://github.com/youtube/api-samples>

However, it avoids some traps. For example, the (free) YouTube Data
API limits how many "queries" you can make per day (I got ~100 1-hour
videos uploaded per day), so this program automatically re-tries the
upload every half hour waiting for the quota to reset.

## Background

- Google offers a lot of APIs:
  - <https://console.developers.google.com/apis/library>
- The API of interest is the YouTube Data API:
  - <https://console.developers.google.com/apis/api/youtube.googleapis.com/overview>
- These APIs are intended for app developers to write apps that users use to interact with their Google Accounts. Consequently, the system that Google uses to manage credentials is complicated. 
- To use the YouTube API, you need to have a Google account, then make a Project in the Developer Console, then get credentials (a Client ID and Client Secret).
- Credential types: OAuth 2.0 credentials vs API keys
  - Using an API key: To use this API you need an API key. An API key identifies your project to check quotas and access. Go to the Credentials page to get an API key. You’ll need a key for each platform, such as Web, Android, and iOS. 
  - Accessing user data with OAuth 2.0: You can access user data with this API. On the Credentials page, create an OAuth 2.0 client ID. A client ID requests user consent so that your app can access user data. Include that client ID when making your API call to Google.
  - Because we're trying to access private user data (private videos), we need OAuth 2.0 credentials.
  - Source: <https://console.developers.google.com/apis/api/youtube.googleapis.com/overview>

## Installation

Following the YouTube Data API tutorial "Upload a Video" (<https://developers.google.com/youtube/v3/guides/uploading_a_video>),

- Use Python 2.5 or higher
- Install Google APIs client library for Python:
  - `$ pip install --upgrade google-api-python-client`
  - <https://developers.google.com/api-client-library/python/start/installation>

- Create a Google Account if you don't have one (or make a temporary one)
  - TIP: If using a different Google account than your normal one, do all this in "private" or "incognito" browser windows to avoid getting logged-out of your normal gmail etc.
  - If your videos are longer than 15 minutes, you'll need to "verify" your Google account before uploading them:
    - <https://www.youtube.com/verify>

- Create a new Google APIs project:
  - <https://console.developers.google.com/projectselector/apis/credentials>
  - <https://developers.google.com/youtube/registering_an_application>
  - This results in you getting a 'client id' and 'client secret', which you should put in a file `client_secrets.json` like this:

      {
        "web": {
          "client_id": "[[INSERT CLIENT ID HERE]]",
          "client_secret": "[[INSERT CLIENT SECRET HERE]]",
          "redirect_uris": [],
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://accounts.google.com/o/oauth2/token"
        }
      }
                    

## Test: Upload one video

In `upload_video.py`, edit this line to include the absolute path to `client_secrets.json`:

     CLIENT_SECRETS_FILE = "/Users/justin/Projects/YouTube-batch-upload/api-samples/python/client_secrets.json"

(This seems to avoid a weird error about not being able to find the json file.)

Then edit and run `upload-to-youtube-api-test.py`, which just does this:

    python upload_video.py --file="/tmp/test_video_file.flv"   # <----- your video file here
                           --title="Summer vacation in California"
                           --description="Had fun surfing in Santa Cruz"
                           --keywords="surfing,Santa Cruz"
                           --category="22"
                           --privacyStatus="private"


**Note**: Use absolute paths for the video.


## Upload multiple videos

Like `upload_video.py`, edit `upload_video-many.py` so the CLIENT_SECRETS_FILE has an absolute path.

The file `upload_video-many.py` is mostly the same as `upload_video.py`, except that it reads the CSV file `CCDC Seminars - Seminars (1).csv`, which has columns

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

Each line represents a video that may or may not be uploaded. 

- The program `seminar-csv-parse.py` is a test program that reads through the CSV file and makes a Title and Description for each line. I pasted its code into `upload_video-many.py` afterward.
- If 'Video URL' is present, the line is skipped (presumably the video has been already uploaded during a previous run).
  - See the code for other conditions that skip the line, you'll probably want to modify it for your own application.
- The 'Talk Video' field is the name of the video. Its absolute path is hard-coded in the code, you'll need to change this line:
  - `absfile = os.path.join('/media/justin/ccdc_vid_backup/videos_seminars/',file)`



## Errors


### Error: redirect_uri_mismatch

"The redirect URI in the request, http://localhost:8080/, does not match the ones authorized for the OAuth client. Visit https://console.developers.google.com/apis/credentials/oauthclient/blahblahblah to update the authorized redirect URIs."

- Went to <https://developers.google.com/identity/protocols/OpenIDConnect#setredirecturi>.
- Added "http://localhost:8080/" to 'redirect url' in some google api page.
- I see `client_secrets.json` has the line `"redirect_uris": []`, maybe I should've filled it in?


### Error: "UserWarning: Cannot access oauth2.json: No such file or directory"

From <https://stackoverflow.com/questions/40546319/drive-api-error-python-doesnt-found-json-quickstart-file>:

'''
I went into the same issue with google calendar api. To solve the problem simply use the absolute file path to your CLIENT_SECRET_FILE like:

CLIENT_SECRET_FILE = r'C:\Users\xxx\client_secret.json'
The file drive-python-quickstart.json will be created after authentication automatically.
'''

Edited upload_video.py : Used absolute path to CLIENT_SECRET. Worked.


### Error: Cannot access ./upload_video-many.py-oauth2.json: No such file or directory

- Since `upload_video.py` worked, I just copied the `oauth2.json` file from `upload_video.py`:

      $ cp -a upload_video.py-oauth2.json upload_video-many.py-oauth2.json


### Error: On the video's youtube page: "Upload failed: Video too long"

<https://support.google.com/youtube/answer/71673?visit_id=1-636406986494486922-4140592693&hl=en&rd=1>

We should've 'verified' our  account first. (Google texts or calls a phone #. Can use 1 phone # twice per year for this.)

Go to <https://www.youtube.com/verify> to verify.


### Error "uploadLimitExceeded: The user has exceeded the number of videos they may upload."

This was after uploading 94 videos. Apparently there's some limit we've exceeded?

- https://stackoverflow.com/questions/43110558/upload-more-than-50-videos-using-youtube-api/43111008
- https://stackoverflow.com/questions/42998086/youtube-video-uploads-rejected-before-api-quota-limit-reached
- https://console.developers.google.com/apis/api/youtube.googleapis.com/quotas?project=upload-ccdc-videos   (your project name here)
- https://console.developers.google.com/iam-admin/quotas?project=upload-ccdc-videos

Hm, can't understand their units of "quota": Says I've only used 40k of 1M queries today, but I'm still getting this error.. Why??

Added a while loop to catch errors and retry every 30 mins. At 4pm
PDT, they resumed for a while: uploaded another 100 vids, then got the
error again. Fine.


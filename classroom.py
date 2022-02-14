from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.student-submissions.students.readonly',
          'https://www.googleapis.com/auth/classroom.courses.readonly', 'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly']


class Classroom():
  def __init__(self):
    self.service = self.__get_service()

  def list_courses(self) -> list:
    service = self.service
    courses = []
    page_token = None

    while True:
      response = service.courses().list(pageToken=page_token,
                                        pageSize=100).execute()
      courses.extend(response.get('courses', []))
      page_token = response.get('nextPageToken', None)
      if not page_token:
        break
    return courses

  def list_course_work(self, courseID: int) -> list:
    service = self.service
    courses = service.courses().courseWork().list(courseId=courseID, pageSize=100).execute()
    return courses.get('courseWork', [])

  def __get_service(self):
    """Shows basic usage of the Classroom API.
    Prints the names of the first 10 courses the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('credentials/token.json'):
      creds = Credentials.from_authorized_user_file('credentials/token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'creds/credentials.json', SCOPES)
        creds = flow.run_console()
      # Save the credentials for the next run
      with open('credentials/token.json', 'w') as token:
        token.write(creds.to_json())

    return build('classroom', 'v1', credentials=creds)


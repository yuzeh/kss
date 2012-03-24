#!/usr/bin/env python2.7

import boto.mturk
from boto.mturk.price import Price
import boto.mturk.connection
from boto.mturk.qualification import *
from boto.mturk.question import *
import datetime
import argparse
from settings import *

FIVE_DOLLA = Price(5.0)

parser = argparse.ArgumentParser(description='Approves a user for part 2')
parser.add_argument('--sandbox', action='store_true')

if __name__ == '__main__':
  args = parser.parse_args()
  if args.sandbox:
    host = HOST
    qualificationId = QUALIFICATION_ID_S
  else:
    host = None
    qualificationId = QUALIFICATION_ID

  connection = boto.mturk.connection.MTurkConnection(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    host=host)

  requirement = Requirement(qualificationId, 'EqualTo', 100, True)

  # Create file upload question
  uploadContent = QuestionContent()
  uploadContent.append_field('Title', 
    'Please upload the file "data.json" from the extension.')
  uploadAnswer = FileUploadAnswer(1, 2*10**9)
  uploadQuestion = Question(identifier='upload',
                            content=uploadContent,
                            answer_spec=AnswerSpecification(uploadAnswer),
                            is_required=True)

  # Create suggestions question
  suggestContent = QuestionContent()
  suggestContent.append_field('Title',
    'Any suggestions to improve the extension?')
  suggestAnswer = FreeTextAnswer()
  suggestQuestion = Question(identifier='suggest',
                             content=suggestContent,
                             answer_spec=AnswerSpecification(suggestAnswer),
                             is_required=False)
  
  # Create overview object
  overview = Overview()
  overview.append(FormattedContent(' '.join([
   '<p>',
   'Thank you for using this extension!',
   'In order to collect your reward for this task, please upload the data ' +
     'that you downloaded from the extension (titled "data.json").',
   '</p>',
   '<p>NOTE: This task will collect *all* browsing and typing within chrome',
   'for the duration of the extension\'s install. The data is transmitted securely',
   'to our servers, and we will never share your data with anyone. However, you',
   'should refrain from highly sensitive browsing (e.g. banking) while collecting',
   'data with the plugin, as that exposes both you and us to unnecessary risk.',
   '</p>',
   '<p>If you do not wish to complete the task you can uninstall the',
   'extension at any time, though this forfeits your ability to complete the',
   'second task. Data is only sent to our server when you upload it, meaning',
   'there is no risk of your data being shared until you choose to share it with',
   'us.</p>',
   '<p>Note that to avoid accidentally sharing sensitive data while using',
   'this extension you can use Chrome\'s "Incognito mode" to browse in a window',
   'with the extension not running. This protects your browsing, but does not',
   'count towards task completion.</p>'])))

  questionForm = QuestionForm()
  questionForm.append(overview)
  questionForm.append(uploadQuestion)
  questionForm.append(suggestQuestion)
  connection.create_hit(questions=questionForm,
    max_assignments=5,
    title='Collecting web browsing data on Google Chrome (Part 2)',
    description='Send your browsing activity to us',
    keywords='google chrome browsing',
    reward=FIVE_DOLLA,
    duration=datetime.timedelta(hours=3),
    approval_delay=datetime.timedelta(7),
    qualifications=Qualifications([requirement]))


import sqlite3
from datetime import datetime
from typing import Union

import pytz
import json

from classroom import Classroom as cl


def get_data(work, subject) -> list:
    dataList = {
        "subject": subject,
        "id": work['id'],
        "title": work['title'],
        "creation_time": convert_date_string(work['creationTime']),
        "update_time": convert_date_string(work['updateTime'])
    }

    if 'dueDate' in work.keys():
        date = {**work['dueDate'], **work['dueTime']}
        dataList['dueDate'] = get_date(date)
    else:
        dataList['dueDate'] = None

    return dataList


def get_date(date: dict) -> str:
    if 'hours' in date:
        a_date = datetime(date['year'], date['month'],
                          date['day'], hour=date['hours'])
    else:
        a_date = datetime(date['year'], date['month'], date['day'])
    return convert_date_string(a_date)


def to_local_timezone(date: datetime) -> datetime:
    local_timezone = pytz.timezone('Asia/Taipei')
    date = local_timezone.localize(date)
    return date


def convert_date_string(date: Union[str, datetime]) -> str:
    if isinstance(date, str):
        date = str_todatetime(date)
    date = to_local_timezone(date)
    return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def str_todatetime(date):
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date


def input_database(cur, data):
    cur.execute('''
  INSERT INTO classworks (id, subject, title, creation_date, update_time, due_date)
  VALUES (:id, :subject, :title, :creation_time, :update_time, :dueDate)
  ON CONFLICT(id) DO UPDATE SET title = :title, update_time = :update_time, due_date = :dueDate WHERE id = :id
  ''', data)


def check_for_dupes(courses):
    seen = set()
    for x in courses:
        id = x['id']
        if id in seen:
            raise ValueError(
                'duplicate value found: {}, {}'.format(id, x['name']))
        seen.add(id)
    return False


if __name__ == '__main__':
    service = cl()

    with open('values.json', 'r') as f:
        courseList = json.load(f)['courses']
        check_for_dupes(courseList)

    count = 0
    conn = sqlite3.connect('classwork.sqlite')
    cur = conn.cursor()

    cur.execute(''' CREATE TABLE IF NOT EXISTS 
    classworks (id INTIGER, subject TEXT, title TEXT, creation_date TEXT, update_time TEXT, due_date TEXT, PRIMARY KEY (id))
    ''')

    for course in courseList:
        courseName = course['name']
        courseId = course['id']
        courseWorks = service.list_course_work(courseId)
        for work in courseWorks:
            data = get_data(work, courseName)
            input_database(cur, data)
            count += 1
        conn.commit()
    print(count)
    cur.close()

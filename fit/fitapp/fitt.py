#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import os
import time
import pytz
import sys
import json
import httplib2  # pip3.5 install httplib2 --upgrade
from configparser import ConfigParser
from google.cloud import bigquery  # pip install --upgrade google-cloud-speech pip install google-cloud-bigquery
from datetime import datetime as dati  # Обращаем ВНИМАНИЕ НА эту строку
from datetime import timedelta
# https://developers.google.com/identity/protocols/oauth2/web-server
# sudo pip install --upgrade google-api-python-client
# вместо from apiclient.discovery import build >
from googleapiclient.discovery import build  # pip3.5 install google-api-python-client
from oauth2client.client import OAuth2WebServerFlow  # pip3.5 install --upgrade oauth2client 


# from the Google Developers Console
CLIENT_ID = '1063678558970-8rf7cf0c161sp6rp51673aoc1tg3597b.apps.googleusercontent.com'  # Другая клиентка
CLIENT_SECRET = 'BEZWFvR9-WvekDSW5IW-ujN9'
#  https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get  all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'

# DATA SOURCE
STEPS_DATASOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
CALORIES_DATASOURCE = 'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended'
ACTIVITY_DATASOURCE = "derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments"
HEART_RATE_DATASOURCE = 'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm'

# The ID is formatted like: "startTime-endTime" where startTime and endTime are
# 64 bit integers (epoch time with nanoseconds).
DATA_SET = "1051700038292387000-1951700038292387000" # http://satels.blogspot.com/2011/04/datetime-timestamp.html

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

DATE_FORMAT = '%Y-%m-%d'
ONE_DAY_MS = 86400000
if 'APP_CONFIG' in os.environ:
    APP_CONFIG_FILENAME = os.environ['APP_CONFIG']
else:
    APP_CONFIG_FILENAME = 'app.config'
config = ConfigParser()
config.read(APP_CONFIG_FILENAME)
DEFAULT_TIMEZONE = config.get('app_config', 'default_timezone')
epoch0 = dati(1970, 1, 1, tzinfo=pytz.utc)

Activ = dict((
(0, 'In vehicle*'),
(1, 'Biking*'),
(2, 'On foot*'),
(3, 'Still (not moving)*'),
(4, 'Unknown (unable to detect activity)*'),
(5, 'Tilting (sudden device gravity change)*'),
(7, 'Walking*'),
(8, 'Running*'),
(9, 'Aerobics'),
(10, 'Badminton'),
(11, 'Baseball'),
(12, 'Basketball'),
(13, 'Biathlon'),
(14, 'Handbiking'),
(15, 'Mountain biking'),
(16, 'Road biking'),
(17, 'Spinning'),
(18, 'Stationary biking'),
(19, 'Utility biking'),
(20, 'Boxing'),
(21, 'Calisthenics'),
(22, 'Circuit training'),
(23, 'Cricket'),
(24, 'Dancing'),
(25, 'Elliptical'),
(26, 'Fencing'),
(27, 'Football (American)'),
(28, 'Football (Australian)'),
(29, 'Football (Soccer)'),
(30, 'Frisbee'),
(31, 'Gardening'),
(32, 'Golf'),
(33, 'Gymnastics'),
(34, 'Handball'),
(35, 'Hiking'),
(36, 'Hockey'),
(37, 'Horseback riding'),
(38, 'Housework'),
(39, 'Jumping rope'),
(40, 'Kayaking'),
(41, 'Kettlebell training'),
(42, 'Kickboxing'),
(43, 'Kitesurfing'),
(44, 'Martial arts'),
(45, 'Meditation'),
(46, 'Mixed martial arts'),
(47, 'P90X exercises'),
(48, 'Paragliding'),
(49, 'Pilates'),
(50, 'Polo'),
(51, 'Racquetball'),
(52, 'Rock climbing'),
(53, 'Rowing'),
(54, 'Rowing machine'),
(55, 'Rugby'),
(56, 'Jogging'),
(57, 'Running on sand'),
(58, 'Running (treadmill)'),
(59, 'Sailing'),
(60, 'Scuba diving'),
(61, 'Skateboarding'),
(62, 'Skating'),
(63, 'Cross skating'),
(64, 'Inline skating (rollerblading)'),
(65, 'Skiing'),
(66, 'Back-country skiing'),
(67, 'Cross-country skiing'),
(68, 'Downhill skiing'),
(69, 'Kite skiing'),
(70, 'Roller skiing'),
(71, 'Sledding'),
(72, 'Sleeping'),
(73, 'Snowboarding'),
(74, 'Snowmobile'),
(75, 'Snowshoeing'),
(76, 'Squash'),
(77, 'Stair climbing'),
(78, 'Stair-climbing machine'),
(79, 'Stand-up paddleboarding'),
(80, 'Strength training'),
(81, 'Surfing'),
(82, 'Swimming'),
(83, 'Swimming (swimming pool)'),
(84, 'Swimming (open water)'),
(85, 'Table tennis (ping pong)'),
(86, 'Team sports'),
(87, 'Tennis'),
(88, 'Treadmill (walking or running)'),
(89, 'Volleyball'),
(90, 'Volleyball (beach)'),
(91, 'Volleyball (indoor)'),
(92, 'Wakeboarding'),
(93, 'Walking (fitness)'),
(94, 'Nording walking'),
(95, 'Walking (treadmill)'),
(96, 'Waterpolo'),
(97, 'Weightlifting'),
(98, 'Wheelchair'),
(99, 'Windsurfing'),
(100, 'Yoga'),
(101, 'Zumba'),
(102, 'Diving'),
(103, 'Ergometer'),
(104, 'Ice skating'),
(105, 'Indoor skating'),
(106, 'Curling'),
(108, 'Other (unclassified fitness activity)'),
(109, 'Light sleep'),
(110, 'Deep sleep'),
(111, 'REM sleep'),
(112, 'Awake (during sleep cycle)'),
(113, 'Crossfit'),
(114, 'HIIT'),
(115, 'Interval Training'),
(116, 'Walking (stroller)'),
(117, 'Elevator'),
(118, 'Escalator'),
(119, 'Archery'),
(120, 'Softball'))
)



def retrieve_data_steps():
    """
    Run through the OAuth flow and retrieve credentials.
    Returns a dataset (Users.dataSources.datasets):
    https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets """ 
    # больше инфы https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get   

    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print ('Go to the following link in your browser:', authorize_url)
    code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    fitness_service = build('fitness', 'v1', http=http)

    return fitness_service.users().dataSources(). \
              datasets(). \
              get(userId='me', dataSourceId=STEPS_DATASOURCE, datasetId=DATA_SET). \
              execute()

def retrieve_act():
    """
    Run through the OAuth flow and retrieve credentials.
    Returns a dataset (Users.dataSources.datasets):
    https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets """ 
    # больше инфы https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get   

    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print ('Go to the following link in your browser:', authorize_url)
    code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    fitness_service = build('fitness', 'v1', http=http)

    return fitness_service.users().dataSources(). \
              datasets(). \
              get(userId='me', dataSourceId=ACTIVITY_DATASOURCE, datasetId=DATA_SET). \
              execute()


def get_daily_activities():
    def get_aggregate(fit_service, startTimeMillis, endTimeMillis, dataSourceId):
        return fit_service.users().dataset().aggregate(userId="me", body={
            "aggregateBy": [{
                "dataTypeName": "com.google.step_count.delta",
                "dataSourceId": dataSourceId
            }],            
            "bucketByTime": {"durationMillis": ONE_DAY_MS},
            "startTimeMillis": startTimeMillis,
            "endTimeMillis": endTimeMillis
        }).execute()
    start_year = 2020
    start_month = 4
    start_day = 16
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print ('Go to the following link in your browser:', authorize_url)
    code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)
    http_auth = credentials.authorize(httplib2.Http())

    fit_service = build('fitness', 'v1', http=http_auth)
    # calculate the timestamp in local time to query Google fitness API
    local_timezone = DEFAULT_TIMEZONE
    local_0_hour = pytz.timezone(local_timezone).localize(dati(start_year, start_month, start_day))
    start_time_millis = int((local_0_hour - epoch0).total_seconds() * 1000)  # start_time_millis = 1584422238292
    end_time_millis = int(round(time.time() * 1000))  # end_time_millis = 1586700038292    
    print(start_time_millis, end_time_millis, nanoseconds(start_time_millis*1000*1000), nanoseconds(end_time_millis*1000*1000))
    activities = {}
    activityData = get_aggregate(fit_service, start_time_millis, end_time_millis, ACTIVITY_DATASOURCE)


    """stepsData = get_aggregate(fit_service, start_time_millis, end_time_millis, STEPS_DATASOURCE)
    #print(stepsData, "stepsData")
    for daily_steps in activityData['bucket']:
        # use local date as the key
        local_date = dati.fromtimestamp(int(daily_steps['startTimeMillis']) / 1000,
                                            tz=pytz.timezone(local_timezone))
        local_date_str = local_date.strftime(DATE_FORMAT)
        print("Дата local_date_str", local_date_str)
        """
        Дата local_date_str 2020-04-16
        {'dataTypeName': 'com.google.activity.summary', 'endTimeNanos': '1587070800000000000', 'startTimeNanos': '1586984400000000000', 'value': [{'mapVal': [], 'intVal': 3}, {'mapVal': [], 'intVal': 85459898}, {'mapVal': [], 'intVal': 7}], 'originDataSourceId': 'derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments'} activity steps_data_point

        """
        steps_data_point = daily_steps['dataset'][0]['point']
        if steps_data_point:
            for activity in steps_data_point:
                print(activity, "activity steps_data_point")
                activity_type = activity['value'][0]['intVal']
                length_ms = activity['value'][1]['intVal']
                n_segments = activity['value'][2]['intVal']
                #print("important", activity['value'], "activity['value']")
                return
                if(activity_type != 3):
                    print(activity_type, "№ of activity_type, this is", Activ[activity_type], "seconds:", round(length_ms / 1000), "segments:", n_segments)
                    n = round(length_ms / 1000)
                    h = str(n//3600)
                    m = str((n//60)%60)
                    s = str(n%60)
                    print(h+':'+m+':'+s)"""




    for daily_activity in activityData['bucket']:
        # use local date as the key
        local_date = dati.fromtimestamp(int(daily_activity['startTimeMillis']) / 1000,
                                            tz=pytz.timezone(local_timezone))
        local_date_str = local_date.strftime(DATE_FORMAT)
        print("local_date_str", local_date_str)
        if local_date_str not in activities:
            activities[local_date_str] = {
                'daily_activities': [],
                'activity_dataset': None
            }

        activity_data_point = daily_activity['dataset'][0]['point']
        #print(activity_data_point, "activity_data_point")
        if activity_data_point:
            for activity in activity_data_point:
                activity_type = activity['value'][0]['intVal']
                length_ms = activity['value'][1]['intVal']
                n_segments = activity['value'][2]['intVal']
                print("important", activity['value'], "activity['value']")
                return
                if(activity_type != 3):
                    print(activity_type, "№ of activity_type, this is", Activ[activity_type], "seconds:", round(length_ms / 1000), "segments:", n_segments)
                    n = round(length_ms / 1000)
                    h = str(n//3600)
                    m = str((n//60)%60)
                    s = str(n%60)
                    print(h+':'+m+':'+s)

                # add daily activities
                activities[local_date_str]['daily_activities'].append({
                    'activity_type': activity_type,
                    'seconds': round(length_ms / 1000),
                    'segments': n_segments,
                })

        # get activity datasets
        start_time_nanos = int((local_date - epoch0).total_seconds() * 1000 * 1000 * 1000)  # вручную
        end_time_nanos = start_time_nanos + 86400000000000
        activity_datasetId = '{}-{}'.format(start_time_nanos, end_time_nanos)
        #print('calling Google Fitness API to get activity segment from dataSetId {}'.format(activity_datasetId))
        activity_dataset = fit_service.users().dataSources().datasets().get(userId="me",
                                                                            dataSourceId=ACTIVITY_DATASOURCE,
                                                                            datasetId=DATA_SET).execute()
        activities[local_date_str]['activity_dataset'] = activity_dataset
    return activities

def nanoseconds(nanotime):
    """
    Convert epoch time with nanoseconds to human-readable.
    """
    dt = dati.fromtimestamp(nanotime // 1000000000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    # Point of entry in execution mode:
    #print(nanoseconds(1451700038292387000),nanoseconds(1584422238292000000), nanoseconds(1586700038292000000), nanoseconds(1561228200000000000), nanoseconds(1561652514300000000))
    #choice = int(input("Какую функцию хочешь вызвать? Введи номер и нажми ентер: "))
    #if(choice == 1):
    dataset = get_daily_activities()
    dataset = retrieve_data_steps()
    with open('dataset.txt', 'w') as outfile:
        json.dump(dataset, outfile)
    if(dataset["point"]):
        last_point = dataset["point"][-1]
        print ("Start time: {}".format( nanoseconds(int(last_point.get("startTimeNanos", 0)))))
        print ("End time: {}".format( nanoseconds(int(last_point.get("endTimeNanos", 0))) ))
        print ("Data type: {}".format( last_point.get("dataTypeName", None) ))
        print ("Steps: {}".format( last_point["value"][0].get("intVal", None) ))
    else: 
        print("Чёта пошло не так сорян")    
    
    #with open('dataset.txt', 'w') as outfile:
    #    json.dump(dataset, outfile)

#=.= code by (ab)
"""
как начать забирать данные https://developers.google.com/fit/rest/v1/get-started
https://developers.google.com/fit/android/history

смотрю:
https://github.com/onejgordon/flow-dashboard/commit/5fd3d230494c2d15399c406bb07010423e447a05
https://github.com/onejgordon/flow-dashboard
https://github.com/UoA-eResearch/fit_api
все https://github.com/topics/google-fit
шоб работало:
pip install pygame

""" 

 


"""
логика приложения здесь. Каждое представление(view) получает HTTP-запрос, обрабатывает его и возвращает ответ
"""

import os
import time
import pytz
import sys
import json
import httplib2  # pip3.6 install httplib2 --upgrade
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.utils import timezone
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic.edit import FormView
from django.template.loader import render_to_string
from django.db import IntegrityError
from .models import Type_Of_Training
from .models import Training
from .forms import PostTrainTypeForm
from .forms import PostTrainingForm
from .forms import VefiryForm
#FOR GOOGLE FIT

from django.conf import settings
from django.http.response import JsonResponse
from django.contrib.auth import get_user_model
from django.http import HttpResponse

from configparser import ConfigParser
#from google.cloud import bigquery  # pip install --upgrade google-cloud-speech pip install google-cloud-bigquery
from datetime import datetime as dati  # Обращаем ВНИМАНИЕ НА эту строку
from datetime import timedelta
# https://developers.google.com/identity/protocols/oauth2/web-server
# sudo pip install --upgrade google-api-python-client
# вместо from apiclient.discovery import build >
from googleapiclient.discovery import build  # pip3.5 install google-api-python-client
from oauth2client import client  # pip3.5 install --upgrade oauth2client GIVE US dat: OAuth2WebServerFlow

# from the Google Developers Console
CLIENT_ID = '1063678558970-8rf7cf0c161sp6rp51673aoc1tg3597b.apps.googleusercontent.com'  # Другая клиентка
CLIENT_SECRET = 'BEZWFvR9-WvekDSW5IW-ujN9'
#  https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get  all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'
# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
DATA_SET = "1051700038292387000-1951700038292387000"
DATE_FORMAT = '%Y-%m-%d'
ONE_DAY_MS = 86400000
# DATA SOURCE
STEPS_DATASOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
CALORIES_DATASOURCE = 'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended'
ACTIVITY_DATASOURCE = "derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments"
HEART_RATE_DATASOURCE = 'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm'
DEFAULT_TIMEZONE = "Europe/Moscow"


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


def goto_html(request):
    flow = client.OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    html_go = ('Go to the following link in your browser:', authorize_url)
    print(html_go)
    return HttpResponse(html_go)


def verify(request):  
    if request.method == "POST":
        form = VefiryForm(request.POST)
        if form.is_valid():
            ver = request.POST.get('ver') 
            ver = ver.strip()  # код верификации
            ver = ver.replace("/", "|")
            data_day = request.POST.get('date_day') 
            data_end = request.POST.get('date_end') 
            print(ver, 'VER HEREEE') 
            print(data_day, "data_day", data_end, "data_end")    
            return redirect(reverse('import_list', args = [ver, data_day, data_end],)) # kwargs={'ver': ver}
    else:
        form = VefiryForm(request.POST)
    return render(request, 'tracking/verify.html', {'form': form})


def import_list(request, *args, ver = None, data_day = None, data_end = None, **kwargs):
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

    ver = ver
    #TIME THING
    epoch0 = dati(1970, 1, 1, tzinfo=pytz.utc)
    local_timezone = DEFAULT_TIMEZONE
    print(data_day, data_end, "data_day, data_end")
    data_day = data_day.split("T")
    day_time = data_day[1].split(":")
    data_day = data_day[0].split("-")
    data_end = data_end.split("T")
    end_time = data_end[1].split(":")
    data_end = data_end[0].split("-")
    print(args, kwargs, ver, "ver", data_day, "data_day")
    if(data_day):  # если дата получена
        start_year = int(data_day[0])
        start_month = int(data_day[1])
        start_day = int(data_day[2])
        local_0_hour = pytz.timezone(local_timezone).localize(dati(start_year, start_month, start_day, int(day_time[0]), int(day_time[1]))) 
        start_time_millis = int((local_0_hour - epoch0).total_seconds() * 1000)
        local_0_hour = pytz.timezone(local_timezone).localize(dati(int(data_end[0]),int(data_end[1]),int(data_end[2]),int(end_time[0]),int(end_time[1])))
        #local_0_hour = pytz.timezone(local_timezone).localize(dati(start_year, start_month, start_day+1)) 
        end_time_millis = int((local_0_hour - epoch0).total_seconds() * 1000)  
    else:
        start_time_millis = int(round((time.time()- 86400) * 1000))  # со вчера
        end_time_millis = int(round(time.time() * 1000))  # до сегодня  
    print(start_year, start_month, start_day, "start_year, start_month, start_day")         
    print(start_time_millis, end_time_millis, "start_time_millis, end_time_millis")
    tim = ""

    flow = client.OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    ver = ver.replace("|", "/")
    code = ver  
    credentials = flow.step2_exchange(code)
    print(credentials, "credentials", flow, "flow")
    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)
    http_auth = credentials.authorize(httplib2.Http())
    print(http_auth, "http_auth")
    fit_service = build('fitness', 'v1', http=http_auth)
    print(fit_service, "fit_service")
    # STEPS
    steps = {}
    steps_data = get_aggregate(fit_service, start_time_millis, end_time_millis, STEPS_DATASOURCE)  

    for daily_step_data in steps_data['bucket']:
        data_point = daily_step_data['dataset'][0]['point']
        # use local date as the key
        local_date = dati.fromtimestamp(int(daily_step_data['startTimeMillis']) / 1000,
                                            tz=pytz.timezone(local_timezone))
        local_date_str = local_date.strftime(DATE_FORMAT)
        count = data_point[0]['value'][0]['intVal']
        data_source_id = data_point[0]['originDataSourceId']
        steps[local_date_str] = {'steps': count, 'originDataSourceId': data_source_id}
        print("Steps:", steps)  


    # ACTIVITY
    activities = {}
    activities['daily_activities'] = []
    activityData = get_aggregate(fit_service, start_time_millis, end_time_millis, ACTIVITY_DATASOURCE)

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
                #return
                if(activity_type != 3):
                    print(activity_type, "№ of activity_type, this is", Activ[activity_type], "seconds:", round(length_ms / 1000), "segments:", n_segments)
                    n = round(length_ms / 1000)
                    hours = str(n//3600)
                    m = str((n//60)%60)
                    s = str(n%60)
                    tim = hours+':'+m+':'+s
                    print(hours+':'+m+':'+s)
                    # add daily activities
                    if(steps[local_date_str]):
                        print(steps[local_date_str], "steps[local_date_str]")
                    activities['daily_activities'].append({
                        'activity_type': Activ[activity_type],
                        'time': tim,
                        'segments': n_segments,
                        'date': local_date_str,
                    })
    print(activities['daily_activities'], "activities['daily_activities']", steps[local_date_str], "steps[local_date_str]", steps[local_date_str]['steps'], "steps[local_date_str]['steps']")
    data = {'steps': steps[local_date_str]['steps'],
            'app_train_type': activities['daily_activities'][0]['activity_type'],
            'duration': activities['daily_activities'][0]['time']}#
    """if request.method == "POST":
        print("if request.method == POST")
        form = PostTrainingForm(request.POST, initial=data)
        if form.is_valid():            
            training = form.save(commit=False)
            get_id = Training.objects.all().last()
            if(get_id):
                training.training = get_id.training + 1
            else:
                training.training = 0
            get_ex = Type_Of_Training.objects.get(title_exercise = training.exercise)
            training.exercise = get_ex
            training.save()
            ret
    else:
        form = PostTrainingForm(initial=data)"""
    return redirect('new_training', data = data)     
    #return render(request, 'tracking/import_list.html', {'form': form})
    #return render(request, 'tracking/import_list.html', {'activities' : activities['daily_activities'], 'steps' : steps[local_date_str]})
   


def home(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    # Отрисовка HTML-шаблона home.html с данными внутри переменной контекста context
    return render(request, 'home.html', context = {})


def traintypes_list(request):
    traintypes = Type_Of_Training.objects.filter().exclude(published = False).order_by('id_exercise')
    return render(request, 'trainings/traintypes_list.html', {'traintypes' : traintypes})


def traintype_detail(request, translit_title):
    traintype = get_object_or_404(Type_Of_Training, translit_title=translit_title)
    return render(request, 'trainings/traintype_detail.html', {'traintype' : traintype})


def trainings_list(request):
    trainings = Training.objects.filter().exclude(t_published = False).order_by('pub_date')
    return render(request, 'tracking/trainings_list.html', {'trainings' : trainings})


def trainings_detail(request):
    training = get_object_or_404(Training)
    return render(request, 'tracking/training_detail.html', {'training' : training})


#@login_required
def new_traintype(request):
    if request.method == "POST":
        form = PostTrainTypeForm(request.POST)
        if form.is_valid():
            traintype = form.save(commit=False)
            get_id = Type_Of_Training.objects.all().last()
            if(get_id):
                traintype.id_exercise = get_id.id_exercise + 1
            else:
                traintype.id_exercise = 0
            traintype.save()
            translit_title = traintype.translit_title
            return redirect('traintype_detail', translit_title)
    else:
        form = PostTrainTypeForm()
    return render(request, 'trainings/new_traintype.html', {'form': form})


#@login_required
def traintype_edit(request, translit_title):
    traintype = get_object_or_404(Type_Of_Training, translit_title=translit_title)
    if request.method == "POST":
        form = PostTrainTypeForm(request.POST, instance=traintype)
        if form.is_valid():
            traintype = form.save(commit=False)
            traintype.save()
            return redirect('traintype_detail', translit_title=translit_title)
    else:
        form = PostTrainTypeForm(instance=traintype)
    return render(request, 'trainings/new_traintype.html', {'form': form})


#@login_required
def traintype_publish(request, translit_title):
    traintype = get_object_or_404(Type_Of_Training, translit_title=translit_title)
    traintype.publish()
    return redirect('traintype_detail', translit_title)


#@login_required
def traintype_remove(request, translit_title):
    traintype = get_object_or_404(Type_Of_Training, translit_title=translit_title)
    traintype.delete()
    return redirect('traintypes_list')



#@login_required
def new_training(request, *args, data = None, **kwargs):
    print(data, "data")
    data = eval(data)
    if request.method == "POST":
        form = PostTrainingForm(request.POST, initial=data)
        if form.is_valid():            
            training = form.save(commit=False)
            get_id = Training.objects.all().last()
            if(get_id):
                training.training = get_id.training + 1
            else:
                training.training = 0
            get_ex = Type_Of_Training.objects.get(title_exercise = training.exercise)
            training.exercise = get_ex
            training.save()
            return redirect('training_detail')
    else:
        form = PostTrainingForm(initial=data)
    return render(request, 'tracking/new_training.html', {'form': form})


#@login_required
def training_edit(request):
    training = get_object_or_404(Training)
    if request.method == "POST":
        form = PostTrainingForm(request.POST, instance=training)
        if form.is_valid():
            training = form.save(commit=False)
            training.save()
            return redirect('training_detail')
    else:
        form = PostTrainingForm(instance=training)
    return render(request, 'training/new_training.html', {'form': form})


#@login_required
def training_publish(request):
    training = get_object_or_404(Training)
    training.publish()
    return redirect('training_detail')


#@login_required
def training_remove(request):
    training = get_object_or_404(Training)
    training.delete()
    return redirect('trainings_list')

# https://pypi.org/project/django-google-api/  DJANGO GOOGLE 


# Create your views here.
"""
Создание представлений
"""

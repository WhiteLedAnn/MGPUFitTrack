from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [  
    path('verify/', views.verify, name='verify'),
    path('search/<term>/', RedirectView.as_view(url='https://google.com/?q=%(term)s')),    
    path(r'verifhtml', views.goto_html, name='goto_html'),
    path(r'trainings/', views.traintypes_list, name='traintypes_list'),
    path(r'trainings/<translit_title>', views.traintype_detail, name='traintype_detail'),
    path('newtraintype/', views.new_traintype, name='new_traintype'),
    path(r'<translit_title>/edit/', views.traintype_edit, name='traintype_edit'),
    path(r'<translit_title>/publish/', views.traintype_publish, name='traintype_publish'),
    path(r'<translit_title>/remove/', views.traintype_remove, name='traintype_remove'),
    path(r'tracking/', views.trainings_list, name='trainings_list'),
    path('trainingsdetail/', views.trainings_detail, name='training_detail'),
    path('newtraining/', views.new_training, name='new_training'),
    path('training/edit/', views.traintype_edit, name='training_edit'),
    path('training/publish/', views.traintype_publish, name='training_publish'),
    path('training/remove/', views.traintype_remove, name='training_remove'),
    path(r'import_list/<ver>/<data_day>/<data_end>/', views.import_list, name='import_list'),

]
# =.= code by (ab)
"""pip install django-uuslug"""

from django import forms
from .models import Type_Of_Training
from .models import Training
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta

class PostTrainTypeForm(forms.ModelForm):
    class Meta:
        model = Type_Of_Training
        fields = ('title_exercise', 'link', 'exercise_description', 'published', )


class PostTrainingForm(forms.ModelForm):
    """
    https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
    """
    class Meta:
        model = Training
        fields = ('exercise', 'student', 't_app', 't_date', 't_result', 'steps', 'duration', 'pub_date', 'review', 'app_train_type', 't_published', )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """if kwargs.has_key('steps'):
            self.fields['steps'].initial = self.initial['steps']
        if kwargs.has_key('app_train_type'):
            self.fields['app_train_type'].initial = self.initial['app_train_type']"""
        #self.fields['exercise'].queryset = Type_Of_Training.objects.all()  # .none()


class VefiryForm(forms.Form):
    today = date.today()
    yesterday = today - timedelta(days = 1)
    ver = forms.CharField(label="Код верификации")
    date_day = forms.DateTimeField(required=False, widget=forms.DateInput(attrs={'type': 'datetime-local', 'placeholder': 'Дата день-мес-год', 'class': 'datepicker'}), initial=yesterday, label="Дата время начала тренировки", input_formats=['%Y-%m-%dT%H:%M'], localize=True)
    date_end = forms.DateTimeField(required=False, widget=forms.DateInput(attrs={'type': 'datetime-local', 'placeholder': 'Дата день-мес-год', 'class': 'datepicker'}), initial=today, label="Дата время конца тренировки", input_formats=['%Y-%m-%dT%H:%M'], localize=True)
    """data_day = forms.DateField(initial=yesterday, label="День", input_formats=['%d-%m-%Y'],
                           widget=forms.DateInput(
                                   format='%d-%m-%Y',
                                   attrs={'placeholder': 'Дата день-мес-год', 'class': 'datepicker'}))  # сегодня"""

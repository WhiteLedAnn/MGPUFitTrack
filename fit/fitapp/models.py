from django.db import models
from django.conf import settings
from django.utils import timezone
from unidecode import unidecode  # pip install unidecode
from django.template import defaultfilters
from uuslug import slugify  # преобразование заголовков в ссылки pip install django-uuslug
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

class Type_Of_Training(models.Model):
    id_exercise = models.IntegerField(primary_key=True)
    title_exercise = models.CharField(max_length=50)  # название упражнения
    translit_title_e = models.CharField(verbose_name='Транслит', max_length=210, blank=True)  # save ссылки на тип упражн для сайта
    link = models.CharField(max_length=100, blank=True)  # название упражнения
    exercise_description = models.TextField(blank=True)  # описание

    def save(self):
        self.translit_title = '{0}-{1}'.format('exercise', defaultfilters.slugify(unidecode(self.title)))# slugify(self.title)
        super(Type_Of_Training, self).save()


class Trainer(models.Model):
    trainer = models.IntegerField(primary_key=True)  # id
    full_name_trainer = models.CharField(max_length=100)  # фио


class MGPU_Group(models.Model):
    mgpu_group = models.IntegerField(primary_key=True)  # id
    trainer = models.ForeignKey(Trainer, on_delete = models.SET_NULL, null=True, blank=True)  # fk группа может поменять тренера
    group_name = models.CharField(max_length=50)  # шифр группы
    study_direction = models.TextField(blank=True)  # направление подготовки
    course = models.IntegerField(blank=True)  # какой курс


class Student_Profile(models.Model):
    student = models.IntegerField(primary_key=True)  # id
    mgpu_group = models.ForeignKey(MGPU_Group, on_delete = models.SET_NULL, null=True, blank=True)  # fk обучающийся может поменять группу
    prepare_level = models.ForeignKey('Classification', on_delete = models.SET_NULL, null=True, blank=True)  # fk уровень подготовки
    health_card = models.ForeignKey('Health_Card_Test', on_delete = models.SET_NULL, null=True, blank=True)  # fk код теста карты здоровья 
    full_name_student = models.CharField(max_length=100, null=True, blank=True)  # фио
    health_group = models.CharField(max_length=30, null=True, blank=True)  # группа здоровья    
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=150, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    student_photo = models.ImageField(null=True, blank=True, upload_to='images/students')  # фото обучающегося
    SEX_CHOICES = (
        ('w',u"женский"),
        ('m',u"мужской"),        
    )
    sex = models.CharField(max_length=1,verbose_name=u"пол",choices=SEX_CHOICES, blank=True)  # пол
    body_index = models.IntegerField(null=True, blank=True)  # индекс массы тела
    chest = models.IntegerField(null=True, blank=True)  # окружность грудной клетки
    signup_confirmation = models.BooleanField(default=False)   

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def save_or_create_profile(sender, instance, created, **kwargs):
    if created:
        Student_Profile.objects.create(user=instance)
    else:
        try:
            instance.student_profile.save()
        except (ValueError, ObjectDoesNotExist):
            Student_Profile.objects.create(user=instance)
"""
В forms.py
SEX_CHOICES = (
        ('m',u"мужской"),
        ('w',u"женский"),
    )
    sex = forms.ChoiceField(label=u'Пол', choices = SEX_CHOICES)"""

class Goals(models.Model):
    goal = models.IntegerField(primary_key=True)  # id код цели
    trainer = models.ForeignKey(Trainer, on_delete = models.CASCADE)  # fk код тренера
    goal_text = models.CharField(max_length=100) # цель
    goal_comment = models.TextField(max_length=200, null=True, blank=True)  # комментарий к цели
    goal_date = models.DateTimeField(default=timezone.now, blank=True)  # дата постановки целей
    answer = models.ForeignKey('Student_Answers', on_delete = models.SET_NULL, null=True, blank=True)  # fk

 
class Competitions(models.Model):
    competition = models.IntegerField(primary_key=True)  # id код соревнования
    student = models.ForeignKey(Student_Profile, on_delete = models.CASCADE)  # fk код обучающегося
    name_comp = models.CharField(max_length=50)  # название соревнования
    place = models.CharField(max_length=50, null=True, blank=True)  # место проведения
    comp_date = models.DateField(default=timezone.now, blank=True)


class Health_Card_Test(models.Model):
    health_card = models.IntegerField(primary_key=True)  # id
    student = models.ForeignKey(Student_Profile, on_delete = models.CASCADE)  # fk 
    result_hc = models.TextField(max_length=50, null=True, blank=True)  # результат теста    
    trainer = models.ForeignKey(Trainer, null=True, blank=True, on_delete = models.SET_NULL)  # fk 
    hc_date = models.DateTimeField(default=timezone.now, blank=True)  # дата проведения
    hc_date_add = models.DateField(default=timezone.now, blank=True)  # дата заполнения
    pulse_before = models.IntegerField(null=True, blank=True) 
    pulse_after = models.IntegerField(null=True, blank=True) 
    pulse_rest = models.IntegerField(null=True, blank=True) 
    s_breath_hold = models.IntegerField(null=True, blank=True)
    g_breath_hold = models.IntegerField(null=True, blank=True)
    chest_rest = models.IntegerField(null=True, blank=True)
    chest_inhale = models.IntegerField(null=True, blank=True)
    chest_exhale = models.IntegerField(null=True, blank=True)
    pulse_lying = models.IntegerField(null=True, blank=True)
    pulse_stand = models.IntegerField(null=True, blank=True)


class Classification(models.Model):
    s_class = models.IntegerField(primary_key=True)  # id
    student = models.ForeignKey(Student_Profile, on_delete = models.CASCADE)  # fk 
    prepare_level = models.CharField(max_length=30, null=True, blank=True)  # уровень подготовки обучающегося


class Training(models.Model):
    training = models.IntegerField(primary_key=True)  # id код тренировки
    exercise = models.ForeignKey(Type_Of_Training, on_delete = models.CASCADE)  # fk код упражнения
    student = models.ForeignKey(Student_Profile, on_delete = models.CASCADE)  # fk код обучающегося
    goal = models.ForeignKey(Goals, on_delete = models.SET_NULL, null=True, blank=True)  # fk код цели
    t_result = models.CharField(null=True, max_length=100, blank=True)  # если данные из приложения - то из какого
    t_date = models.DateTimeField(default=timezone.now, blank=True)  # дата проведения тренировки
    t_result = models.CharField(max_length=100, blank=True)  # результат тренировки
    heart = models.IntegerField(null=True, blank=True)  # число сердечных сокращений
    duration = models.IntegerField(null=True, blank=True)  # длительность время выполнения
    pace = models.IntegerField(default=0, blank=True)  # темп интенсивность баллы кардио
    distance = models.IntegerField(null=True, blank=True)  # расстояние
    max_weig = models.IntegerField(default=0, null=True, blank=True)  # максимальный поднятый вес
    rep = models.IntegerField(default=0, null=True, blank=True)  # количество повторений
    approach = models.IntegerField(default=0, null=True, blank=True)  # количество подходов
    pub_date = models.DateTimeField(default=timezone.now, blank=True)  # дата публикации тренировки
    screen = models.ImageField(null=True, blank=True, upload_to='images/students')  # скрин экрана
    advice = models.TextField(max_length=200, null=True, blank=True)  # совет тренера по результатам
    review = models.TextField(max_length=200, null=True, blank=True)  # комментарий обучающегося о тренировке


class Tests(models.Model):
    test = models.IntegerField(primary_key=True)  # id
    test_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)


class Questions(models.Model):
    question = models.IntegerField(primary_key=True)  # id
    question_text = models.CharField(max_length=200)


class Test_Questions(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
   

class Student_Answers(models.Model):
    answer = models.IntegerField(primary_key=True)  # id
    student = models.ForeignKey(Student_Profile, on_delete = models.CASCADE)  # fk
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200)
    ans_date = models.DateTimeField(default=timezone.now, blank=True)
    comment_tr = models.CharField(max_length=200, blank=True)
    trainer = models.ForeignKey(Trainer, null=True, on_delete = models.SET_NULL, blank=True)


# Create your models here.

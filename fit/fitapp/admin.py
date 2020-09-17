from django.contrib import admin
from .models import Student_Profile  # возможность заполнять с админки базу данных
from .models import Trainer
from .models import Type_Of_Training
from .models import MGPU_Group
from .models import Training


class TrainingAdmin(admin.ModelAdmin):
    list_display = ('training', 'exercise', 'app_train_type', 'steps', 't_date', 'pub_date', 't_published')
    list_filter = ('app_train_type', 't_date', 'pub_date', 't_published')
    raw_id_fields = ('exercise', 'student', 'goal')  # помогает внешним ключам
    date_hierarchy = 't_date'
    ordering = ['training', 'steps', 't_published']


class Type_Of_TrainingAdmin(admin.ModelAdmin):
    list_display = ('id_exercise', 'title_exercise', 'translit_title', 'published', 'link')
    list_filter = ('title_exercise', 'published')
    prepopulated_fields = {'translit_title': ('translit_title',)}
    #raw_id_fields = ('id_exercise',)
    ordering = ['id_exercise', 'title_exercise']


admin.site.register(Student_Profile)
admin.site.register(Trainer)
admin.site.register(Training, TrainingAdmin)
admin.site.register(Type_Of_Training, Type_Of_TrainingAdmin)
admin.site.register(MGPU_Group)

# Register your models here.

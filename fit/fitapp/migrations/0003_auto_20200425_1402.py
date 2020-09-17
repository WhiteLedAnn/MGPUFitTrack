# Generated by Django 3.0.5 on 2020-04-25 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitapp', '0002_auto_20200404_1528'),
    ]

    operations = [
        migrations.RenameField(
            model_name='type_of_training',
            old_name='translit_title_e',
            new_name='translit_title',
        ),
        migrations.AddField(
            model_name='training',
            name='app_train_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='training',
            name='steps',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='training',
            name='t_app',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='training',
            name='t_published',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='type_of_training',
            name='published',
            field=models.BooleanField(default=True),
        ),
    ]

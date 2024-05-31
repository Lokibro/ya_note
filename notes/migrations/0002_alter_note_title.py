# Generated by Django 3.2.15 on 2024-05-27 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(default='Название заметки', help_text='Дайте короткое название заметке', max_length=100, verbose_name='Заголовок'),
        ),
    ]

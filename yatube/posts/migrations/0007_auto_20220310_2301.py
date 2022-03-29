# Generated by Django 2.2.6 on 2022-03-10 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220310_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='Краткое описание группы', verbose_name='Описание группы'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='уникальная строка идентификатор, содержащая только "безопасные" символы', max_length=15, unique=True, verbose_name='Идентификатор'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Группа, к которой будет относиться пост', max_length=200, verbose_name='Название группы'),
        ),
    ]
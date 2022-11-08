# Generated by Django 2.2.6 on 2022-10-30 20:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20221007_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(verbose_name='описание группы'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='уникальный адрес'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200, verbose_name='название группы'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Группа, к которой будет относиться пост', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Введите текст поста', verbose_name='текст поста'),
        ),
    ]
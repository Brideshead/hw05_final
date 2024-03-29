# Generated by Django 2.2.6 on 2022-11-17 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20221117_1757'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='post',
            name='modified',
        ),
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='дата публикации'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='дата публикации'),
        ),
    ]

# Generated by Django 2.2.6 on 2022-11-17 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_auto_20221117_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='modified',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='дата изменения'),
        ),
        migrations.AddField(
            model_name='post',
            name='modified',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='дата изменения'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='дата публикации'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='дата публикации'),
        ),
    ]

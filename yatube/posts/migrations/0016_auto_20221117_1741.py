# Generated by Django 2.2.6 on 2022-11-17 16:41

import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0015_auto_20221117_1730'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='user_author_pair_unique'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, author=django.db.models.expressions.F('user')), name='user_prevent_self_follow'),
        ),
    ]

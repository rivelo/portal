# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-26 21:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_calendar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='email_text',
            field=models.TextField(blank=True),
        ),
    ]

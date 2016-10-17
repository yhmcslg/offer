# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app001', '0003_auto_20160922_2008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='template_name',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app001', '0002_auto_20160922_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='template_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]

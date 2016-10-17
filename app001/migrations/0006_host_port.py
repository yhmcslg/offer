# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app001', '0005_auto_20160923_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='port',
            field=models.IntegerField(default=22),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app001', '0004_remove_task_template_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hoststatus',
            name='name',
            field=models.CharField(max_length=100, verbose_name='\u72b6\u6001', choices=[(b'online', '\u5728\u7ebf'), (b'offline', '\u79bb\u7ebf'), (b'all', '\u5168\u90e8')]),
        ),
    ]

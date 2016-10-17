# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=100, verbose_name='\u7528\u6237\u540d')),
                ('password', models.CharField(max_length=100, verbose_name='\u5bc6\u7801')),
            ],
            options={
                'db_table': 'AdminInfo',
            },
        ),
        migrations.CreateModel(
            name='ExecuteType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.CharField(max_length=100, verbose_name='\u6267\u884c\u65b9\u6cd5')),
                ('code', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'ExecuteType',
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(unique=True, max_length=100)),
                ('lan_ip', models.GenericIPAddressField(unique=True)),
                ('wan_ip', models.GenericIPAddressField(null=True, blank=True)),
                ('memory', models.CharField(default=b'', max_length=10)),
                ('cpu', models.CharField(default=b'', max_length=100)),
                ('brand', models.CharField(default=b'', max_length=100)),
                ('os', models.CharField(default=b'', max_length=100)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'Host',
            },
        ),
        migrations.CreateModel(
            name='HostGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('groupname', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'HostGroup',
            },
        ),
        migrations.CreateModel(
            name='HostStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u72b6\u6001', choices=[(b'online', '\u5728\u7ebf'), (b'offline', '\u79bb\u7ebf'), (b'unknow', '\u672a\u548c')])),
                ('memo', models.TextField(null=True, verbose_name='\u5907\u6ce8', blank=True)),
            ],
            options={
                'db_table': 'HostStatus',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u4efb\u52a1\u540d\u79f0')),
                ('content', models.TextField(null=True, verbose_name='\u4efb\u52a1\u5185\u5bb9', blank=True)),
                ('file', models.FileField(upload_to=b'', null=True, verbose_name='\u4e0a\u4f20\u6587\u4ef6\u6216\u76ee\u5f55', blank=True)),
                ('description', models.TextField(null=True, verbose_name='\u4efb\u52a1\u63cf\u8ff0', blank=True)),
                ('template_name', models.CharField(unique=True, max_length=100)),
                ('kick_off_at', models.DateTimeField(auto_now=True, verbose_name='\u6267\u884c\u65f6\u95f4')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('execute_type', models.ForeignKey(default=1, to='app001.ExecuteType')),
                ('hosts', models.ManyToManyField(to='app001.Host', verbose_name='\u9009\u62e9\u4efb\u52a1\u4e3b\u673a', blank=True)),
                ('hostsgroup', models.ForeignKey(verbose_name='\u9009\u62e9\u4e3b\u673a\u7ec4', blank=True, to='app001.HostGroup')),
            ],
            options={
                'db_table': 'Task',
            },
        ),
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.CharField(max_length=256, verbose_name='\u7ed3\u679c', choices=[(b'success', '\u6210\u529f'), (b'failed', '\u5931\u8d25'), (b'unknow', '\u672a\u548c')])),
                ('log', models.TextField(verbose_name='\u4efb\u52a1\u65e5\u5fd7')),
                ('host_id', models.IntegerField(default=1, verbose_name='\u4e3b\u673aID')),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('task', models.ForeignKey(to='app001.Task')),
            ],
            options={
                'db_table': 'TaskLog',
            },
        ),
        migrations.CreateModel(
            name='TaskTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=256)),
                ('content', models.TextField()),
            ],
            options={
                'db_table': 'TaskTemplate',
            },
        ),
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.CharField(max_length=100, verbose_name='\u4efb\u52a1\u7c7b\u578b')),
                ('code', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'TaskType',
            },
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.CharField(max_length=100, verbose_name='\u7528\u6237\u7ec4')),
            ],
            options={
                'db_table': 'UserGroup',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='\u540d\u5b57')),
                ('email', models.EmailField(max_length=254, verbose_name='\u90ae\u7bb1')),
                ('phone', models.CharField(max_length=50, verbose_name='\u5ea7\u673a')),
                ('mobile', models.CharField(max_length=32, verbose_name='\u624b\u673a')),
                ('memo', models.TextField(verbose_name='\u5907\u6ce8', blank=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'UserProfile',
                'verbose_name': '\u7528\u6237\u4fe1\u606f',
                'verbose_name_plural': '\u7528\u6237\u4fe1\u606f',
            },
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'UserType',
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_type',
            field=models.ForeignKey(to='app001.UserType'),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='users',
            field=models.ManyToManyField(to='app001.UserProfile'),
        ),
        migrations.AddField(
            model_name='task',
            name='task_template',
            field=models.ForeignKey(to='app001.TaskTemplate'),
        ),
        migrations.AddField(
            model_name='host',
            name='hostgroup',
            field=models.ForeignKey(to='app001.HostGroup'),
        ),
        migrations.AddField(
            model_name='host',
            name='status',
            field=models.ForeignKey(to='app001.HostStatus'),
        ),
        migrations.AddField(
            model_name='admininfo',
            name='user_info',
            field=models.OneToOneField(to='app001.UserProfile'),
        ),
    ]

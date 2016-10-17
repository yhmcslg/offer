#_*_coding:utf-8_*_
import sys
#reload(sys) 
#sys.setdefaultencoding("utf-8") 
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Create your models here.

class UserType(models.Model):
    caption = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.caption
    
    class Meta:
        db_table = 'UserType'
    
class UserProfile(models.Model):
    user_type = models.ForeignKey('UserType')
    name = models.CharField(u'名字',max_length=32) 
    email = models.EmailField(u'邮箱')
    phone = models.CharField(u'座机',max_length=50)
    mobile = models.CharField(u'手机',max_length=32)
    
    memo = models.TextField(u'备注',blank=True)
    create_at = models.DateTimeField(blank=True,auto_now_add=True)
    update_at = models.DateTimeField(blank=True,auto_now=True)
    
    class Meta:
        db_table = 'UserProfile'
        verbose_name = u'用户信息'
        verbose_name_plural = u'用户信息'

    def __unicode__(self):
        return '%s' % self.name



class AdminInfo(models.Model):
    user_info = models.OneToOneField(UserProfile)
    username = models.CharField(u'用户名',max_length=100)
    password = models.CharField(u'密码',max_length=100)
    
    def __unicode__(self):
        return self.username
    
    class Meta:
        db_table = 'AdminInfo'
    
    
class UserGroup(models.Model):
    caption = models.CharField(u'用户组',max_length=100)
    users = models.ManyToManyField(UserProfile)
    
    def __unicode__(self):
        return self.caption    


    class Meta:
        db_table = 'UserGroup'

class HostStatus(models.Model):
    result_choices = (
                      ('online',u'在线'),
                      ('offline',u'离线'),
                      ('all',u'全部')
                      )
    name = models.CharField(u'状态',max_length=100,choices=result_choices)
    memo = models.TextField(u'备注',null=True,blank=True)
    
    def __unicode__(self):
        return self.name


    class Meta:
        db_table = 'HostStatus'

class Host(models.Model):
    hostname = models.CharField(max_length=100,unique=True)
    lan_ip = models. GenericIPAddressField(unique=True)
    wan_ip = models.GenericIPAddressField(null=True,blank=True)
    port = models.IntegerField(default=22)
    memory = models.CharField(max_length=10,default='')
    cpu = models.CharField(max_length=100,default='')
    brand = models.CharField(max_length=100,default='')
    os = models.CharField(max_length=100,default='')
    status = models.ForeignKey('HostStatus')
    hostgroup = models.ForeignKey('HostGroup')
    create_at = models.DateTimeField(blank=True,auto_now_add=True)
    update_at = models.DateTimeField(blank=True,auto_now=True)
    
    def __unicode__(self):
        return self.hostname


    class Meta:
        db_table = 'Host'

class HostGroup(models.Model):
    groupname = models.CharField(max_length=100,unique=True)
    
    def __unicode__(self):
        return self.groupname

    class Meta:
        db_table = 'HostGroup'


class TaskTemplate(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    content = models.TextField()
    
    def __unicode__(self):
        return self.name    
    

    class Meta:
        db_table = 'TaskTemplate'


class TaskType(models.Model):
    caption = models.CharField(u'任务类型',max_length=100)
    code = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.caption


    class Meta:
        db_table = 'TaskType'


class ExecuteType(models.Model):
    caption = models.CharField(u'执行方法',max_length=100)
    code = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.caption

    class Meta:
        db_table = 'ExecuteType'


class Task(models.Model):
    name = models.CharField(u'任务名称',max_length=100)
    content = models.TextField(u'任务内容',blank=True,null=True)
    file = models.FileField(u'上传文件或目录',blank=True,null=True)
    description = models.TextField(u'任务描述',blank=True,null=True)
    #task_type = models.ForeignKey('TaskType')
    execute_type = models.ForeignKey('ExecuteType',default=1)

    hosts = models.ManyToManyField('Host',verbose_name=u'选择任务主机',blank=True,through='TaskHostStatus')
    
    hostsgroup = models.ForeignKey('HostGroup',verbose_name=u'选择主机组',blank=True)    
    
    task_template = models.ForeignKey('TaskTemplate')
    
    
    #created_by = models.ForeignKey('UserProfile',verbose_name=u'任务创建者')
    
    kick_off_at = models.DateTimeField(u'执行时间',auto_now=True)
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
        
    def __unicode__(self):
        return self.name


    class Meta:
        db_table = 'Task'

class TaskHostStatus(models.Model):
    status = models.IntegerField(default=0)
    log = models.TextField(null=True,blank=True)
    
    task = models.ForeignKey(Task)
    host = models.ForeignKey(Host)
    
    
    def __unicode__(self):
        return self.log

    class Meta:
        db_table = 'TaskHostStatus'
        auto_created=True



class TaskLog(models.Model):
    task = models.ForeignKey(Task)
    result_choices = (
                      ('success',u'成功'),
                      ('failed',u'失败'),
                      ('unknow',u'未和')
                      )
    result = models.CharField(u'结果',max_length=256,choices=result_choices)
    log = models.TextField(u'任务日志')
    host_id = models.IntegerField(u'主机ID',default=1)
    date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    
    def __unicode__(self):
        return self.task.name
    
    
    class Meta:
        db_table = 'TaskLog'

'''
class Idc(models.Model):
    name=models.CharField(max_length=50,unique=True)
    def __unicode__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=50,unique=True)
    display_name = models.CharField(max_length=50)
    template_list = models.ManyToManyField('Templates',null=True,blank=True)
    def __unicode__(self):
        return self.display_name

class Host(models.Model):
    hostname=models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=50, unique = True)
    ip = models.IPAddressField(unique=True)
    child_of = models.ForeignKey('TrunkServers', null=True,blank=True)
    idc = models.ForeignKey(Idc, null=True, blank=True)
    group = models.ManyToManyField(Group, null=True, blank=True)
    template_list = models.ManyToManyField('Templates',null=True,blank=True)
    custom_services = models.ManyToManyField('Services',null=True,blank=True)
    port = models.IntegerField(default='22')
    os = models.CharField(max_length=20, default='linux', verbose_name='Operating System')

    #snmp related
    status_monitor_on = models.BooleanField(default=True)
    snmp_on = models.BooleanField(default=True)
    snmp_version = models.CharField(max_length=10,default='2c')
    snmp_community_name = models.CharField(max_length=50,default='public')
    snmp_security_level = models.CharField(max_length=50,default='auth')
    snmp_auth_protocol = models.CharField(max_length=50,default='MD5')
    snmp_user = models.CharField(max_length=50,default='triaquae_snmp')
    snmp_pass = models.CharField(max_length=50,default='my_pass')

    ###########for task allocation#########
    poll_interval = models.IntegerField(default=300)

    def __unicode__(self):
        return self.display_name


class ServerStatus(models.Model):
    host = models.OneToOneField('Host')
    hostname = models.CharField(max_length=100)
    host_status = models.CharField(max_length=10,default='Unkown')
    ping_status = models.CharField(max_length=100,default='Unkown')
    last_check = models.CharField(max_length=100,default='N/A')
    host_uptime = models.CharField(max_length=50,default='Unkown')
    attempt_count = models.IntegerField(default=0)
    breakdown_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    snmp_alert_count = models.IntegerField(default=0)
    availability = models.CharField(max_length=20,default=0)
    def __unicode__(self):
        return self.host


class TrunkServers(models.Model):
    name = models.CharField(max_length=50,unique=True)
    description = models.CharField(max_length=150,blank=True)
    ip_address = models.IPAddressField()
    port = models.IntegerField(default = 9998)
    def __unicode__(self):
        return self.name

class Templates(models.Model):  #monitor template
    name = models.CharField(max_length=50, unique=True)
    service_list =  models.ManyToManyField('ServiceList')
    graph_list = models.ManyToManyField('Graphs',blank=True,null=True)
    # = models.ManyToManyField('Group',blank=True,null=True)
    
    def __unicode__(self):
        return self.name

class Services(models.Model):  #services list
    name = models.CharField(max_length=50,unique=True)
    monitor_type_list = (('agent','Agent'),('snmp','SNMP'),('wget','Wget'))
    monitor_type = models.CharField(max_length=50, choices=monitor_type_list)
    plugin = models.CharField(max_length=100) 
    item_list = models.ManyToManyField('Items')
    #trigger_list = models.ManyToManyField('triggers',blank=True)
    #trigger = models.ForeignKey('Triggers', null=True,blank=True)
    
    #flexible_intervals = 
    def __unicode__(self):
        return self.name

class Items(models.Model): # monitor item
    name = models.CharField(max_length=50, unique=True)
    key = models.CharField(max_length=100,unique=True)
    data_type_option = (('float','Float'),('string','String'),('integer', 'Integer') ) 
    data_type = models.CharField(max_length=50, choices=data_type_option)
    unit = models.CharField(max_length=30,default='%')
    enabled = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name

class ServiceList(models.Model): 
    name = models.CharField(max_length=50,unique=True)
    service = models.ForeignKey('Services')
    check_interval = models.IntegerField(default=300)
    conditons = models.ManyToManyField('Conditions',verbose_name=u'阀值列表',null=True,blank=True)
    #expression = models.CharField(max_length=1000)
    description = models.TextField()

    serverity_list = (('information','Information'),
                       ( 'warning' ,'Warning'),
                       ('critical', 'Critical'),
                       ('urgent','Urgent'),
                       ('disaster','Disaster') )
    serverity = models.CharField(max_length=30, choices=serverity_list)

    #dependencies 
    def __unicode__(self):
        return self.name

class Graphs(models.Model):
    name = models.CharField(max_length=50, unique=True)
    datasets = models.ManyToManyField('Items')
    graph_type = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

    
class Actions(models.Model):
    name = models.CharField(max_length=100,unique=True)
    condition_list = models.ManyToManyField('Conditions')
    operation_list = models.ManyToManyField('Operations')
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=250)
    recovery_notice = models.BooleanField(default=True)
    recovery_subject = models.CharField(max_length=100)
    recovery_message = models.CharField(max_length=250)
    enabled = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
class Formulas(models.Model):
    name = models.CharField(max_length=64,unique=True)
    key = models.CharField(max_length=64,unique=True)
    memo = models.TextField()
    
    def __unicode__(self):
        return self.name 
    
class Operators(models.Model):
    name = models.CharField(max_length=32,unique=True)    
    key = models.CharField(max_length=32)    
    memo = models.TextField()
    def __unicode__(self):
        return self.name 
     
class Conditions(models.Model):
    name = models.CharField(max_length=100,unique=True)
    item = models.ForeignKey('Items', verbose_name=u'监控值')
    formula = models.ForeignKey('Formulas', verbose_name=u'运算函数',null=True,blank=True)
    operator = models.ForeignKey(Operators,verbose_name=u'运算符',null=True,blank=True)
    data_type = models.CharField(default='char',max_length=32, verbose_name=u'数据类型')
    threshold = models.CharField(max_length=64, verbose_name=u'阀值')
    def __unicode__(self):
        return self.name

class Operations(models.Model):
    send_to_users = models.ManyToManyField('UserProfile')
    send_to_groups = models.ManyToManyField('Group')
    notifier_type = (('email','Email'),('sms','SMS'))
    send_via = models.CharField(max_length=30,choices=notifier_type)
    notice_times = models.IntegerField(default=5)
    notice_interval = models.IntegerField(default=300, verbose_name='notice_interval(sec)')
"""
class plugins(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150, blank=True)
    plugin_file_name = models.CharField(max_length=150)
    def __unicode__(self):
    return self.name
"""




######################below for the task allowcation syste#############
class TaskCenter(models.Model):
    name = models.CharField(u'任务名称',max_length=128)
    description = models.TextField(u'描述',blank=True,null=True)
    created_by= models.ForeignKey('UserProfile',verbose_name=u'任务创建者',blank=True,null=True)
    task_choices = (('cmd','命令执行'),
                    ('file_transfer','文件分发'),
                    ('config_allocation','配置下发'))
    
    task_type = models.CharField(u'任务类型',choices=task_choices,max_length=32)
    hosts = models.ManyToManyField(Host, verbose_name=u'选择任务主机',default=None)
    groups = models.ManyToManyField(Group, verbose_name=u'选择组' ,default=None)
    content = models.TextField(u'任务内容')
    kick_off_at = models.DateTimeField(u'执行时间',blank=True,null=True)
    
    memo = models.TextField(blank=True,null=True)
  
    def __unicode__(self):
        return self.name 
class TaskLog(models.Model):
    task = models.ForeignKey(TaskCenter)
    result_choices = (('success',u'成功'),
                      ('failed',u'失败'),
                      ('unknown',u'未知'))
    
    result = models.CharField(u'结果',choices=result_choices,max_length=32)
    log = models.TextField(u'任务日志')
    host_id = models.IntegerField(u'汇报主机ID',default=None)
    date = models.DateTimeField(auto_now_add=True,null=True)
    
    def __unicode__(self):
        return self.task.name 
    
'''
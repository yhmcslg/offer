# coding:utf8

from django.shortcuts import  render_to_response,redirect,render
from django.template import RequestContext  
from django.http import  HttpResponse,HttpResponseBadRequest,HttpResponseRedirect
#from django.views.decorators.http import require_http_methods
# Create your views here.
import os,sys,platform
reload(sys)

if platform.system() == 'Linux':
    sys.setdefaultencoding('utf8')

from app001 import models

from app001 import forms
  
import datetime
#from werkzeug import responder


from third import html_helper_bootstarp
from third import common

from django.db.models import Q

from django.db import connection,transaction

import paramiko
from django.core.management.sql import sql_all

from third import handle_uploaded

from offer.settings import BASE_DIR,PAGE_SIZE

import json

from django.views.decorators.csrf import csrf_exempt

def login_dresser(func):
    def outer(request,*args,**kwargs):
        cookie_username_password = request.COOKIES.get('username_password')
        
        if not cookie_username_password:
            return HttpResponseRedirect('/login')
        else:
            return func(request,*args,**kwargs)    
    return outer



def get_username_nick(request):    
    username = request.COOKIES.get('username_password')

    if username:
        username = username.split('&')[0]
        user_type = models.AdminInfo.objects.select_related().get(username=username).user_info.user_type.caption
        username = models.AdminInfo.objects.select_related().get(username=username).user_info.name

        username_nick = {'username':username,'user_type':user_type} 
    else:
        username_nick = {}
    return username_nick


def login(request):
    m = {}
    
    cookie_username_password = request.COOKIES.get('username_password')
 
    if cookie_username_password:
        return HttpResponseRedirect('/index')
    else:    
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember-me')
            
            
            a = models.AdminInfo.objects.filter(username=username,password=password).count()
            
            m = {'m':u'用户名或密码错误'}
            
            if a == 1:
                resp = HttpResponseRedirect('/index')
                dt = datetime.datetime.now() + datetime.timedelta(hours = int(2))
                resp.set_cookie('username_password','%s&%s'%(username,password),expires=dt)
                
                session_get_username = request.session.get(username,default=0)
                
                if not session_get_username:
                    request.session[username] = 1
                    
                return resp
                
            else:
                return render_to_response('login.html',{'m':m},context_instance=RequestContext(request))
        return render_to_response('login.html',{'m':m},context_instance=RequestContext(request))



def logout(request):
    try:
        username = request.COOKIES.get('username_password')
        if username:
            username = username.split('&')[0]
        del request.session[username]
    except KeyError:
        pass
    
    resp = HttpResponseRedirect('/login')
    if request.COOKIES.get('username_password'):
        resp.delete_cookie('username_password')
    return resp

def CheckOnLine(request):
    c = {}
    
    username = request.COOKIES.get('username_password')
    
    if username:
        username = username.split('&')[0]
    
    is_login  = request.session.get(username,default=None)

    c['Result'] = is_login
    c['sessionid'] = request.COOKIES.get('sessionid')
       
    return HttpResponse(json.dumps(c),content_type="application/json")

def test(request,id):  
    if request.method == 'POST':
        return HttpResponse(json.dumps(id),content_type="application/json")
    else:
        return render_to_response('test.html')
    

from third.WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET 
def weichat(request):
    sToken = "sF2N55REDOsWYnVC6dACwwhNJum"
    sEncodingAESKey = "fBSy5d73BFHjBnelPEFRyatfdzYXJlshNsTQV2Q7s8Y"
    sCorpID = "wxc46f6030a14f2c73"
    
    wxcpt=WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)

    sVerifyMsgSig=request.GET.get('msg_signature')

    sVerifyTimeStamp=request.GET.get('timestamp')

    sVerifyNonce=request.GET.get('nonce')

    sVerifyEchoStr=request.GET.get('echostr')
    ret,sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)
    
    if(ret!=0):
        result = "ERR: VerifyURL ret: %d"%ret
        return HttpResponse(result)
    
    return HttpResponse(sEchoStr)


def bootstrap(request,id):  
    if request.method == 'POST':
        return HttpResponse(json.dumps(id),content_type="application/json")
    else:
        return render_to_response('bootstrap.html')    
    
login_username = ''

@login_dresser
def index(request):
    return render_to_response('index.html',context_instance=RequestContext(request))

@login_dresser
def user_info(request):
    username = request.COOKIES.get('username_password').split('&')[0]
    user_inf_id = models.AdminInfo.objects.get(username=username).user_info_id
    username = models.UserProfile.objects.get(id=user_inf_id)
    
    return HttpResponse(u'欢迎光临:%s'%username)
#===========================task================================================================================
def task(request):    
    return render_to_response('task/task.html',context_instance=RequestContext(request))

@login_dresser
def task_create(request):
    f = forms.TaskForm()

    return render_to_response('task/task_create.html',{'f':f},context_instance=RequestContext(request))



def template_content_json(request):

    task_template_id = request.GET.get('task_template_id')

    if task_template_id:
        task_contents = models.TaskTemplate.objects.get(id = task_template_id)
        c = {}
        c['name'] = task_contents.name
        c['content'] = task_contents.content
    else:
        c = {}    
        

    return HttpResponse(json.dumps(c),content_type="application/json")


def host_Group_Name_json(request):

    hostGroup_id = request.GET.get('hostGroup_id')
    hostGroup_id = int(hostGroup_id)
    print type(hostGroup_id)   
    host_group_list = []
    
    if  hostGroup_id:
        print '11111111'
        task_contents = models.HostGroup.objects.get(id = hostGroup_id)
        if task_contents:
            for content in task_contents.host_set.filter(status=models.HostStatus.objects.get(name='online').id):    
                c = {}
                c['id'] = content.id
                c['hostname'] = content.hostname
                host_group_list.append(c)                
    else:
        for content in models.Host.objects.filter(status=models.HostStatus.objects.get(name='online').id):
            c = {}
            c['id'] = content.id
            c['hostname'] = content.hostname
            host_group_list.append(c)

    return HttpResponse(json.dumps(host_group_list),content_type="application/json")




#@api_view(['GET','POST'])
#@transaction.atomic
def new_task(request):
    
    username = request.COOKIES.get('username_password').split('&')[0]
    task_from = forms.TaskForm(request.POST,request.FILES)

    print r'task_from.cleaned_data:',task_from
    
    if task_from.is_valid():

        with transaction.atomic():        
            cursor = connection.cursor() 
            
            task_name = task_from.cleaned_data.get('name')
            task_description = task_from.cleaned_data.get('description')
            
            if not task_description:
                task_description = ''
            
            task_content = task_from.cleaned_data.get('content')

            task_host_name = task_from.cleaned_data.get('hosts')
            
            task_hostsgroup = task_from.cleaned_data.get('hostsgroup')
    
            task_execute_id = request.POST.get('execute_type')
     
            template_name = task_from.cleaned_data.get('template_name')
            
            task_kick_off_at = task_from.cleaned_data.get('kick_off_at')
            
            template_id = task_from.cleaned_data.get('task_template_id')
            
            if not task_kick_off_at:
                task_kick_off_at = datetime.datetime.now()
            
            create_time = datetime.datetime.now()
    
            dir_name = os.path.join(BASE_DIR,'upload',username)
            
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)  
                   
            filename = ''   
            
            
            upload_filename=[]

            if template_name:
                sql = '''insert into  tasktemplate(name,description,content) value ("%s","%s","%s")'''%(template_name,'custom',task_content)
                print sql
                cursor.execute(sql)
     
            if request.FILES:
                filename = request.FILES.getlist('file')
                for file_name in filename:
                    handle_uploaded.handle_uploaded_file(os.path.join(dir_name,file_name.name),file_name)
                    upload_filename.append(file_name.name)  
                    
                a = []    
                
                for i in upload_filename:
                    a.append(os.path.join('/tmp','upload',username,i))  
  
                sql = '''insert into task(name,content,kick_off_at,description,execute_type_id,create_time,file,hostsgroup_id,task_template_id)
                            values("%s","%s","%s","%s","%s","%s","%s","%s","%s");'''%(task_name,task_content,task_kick_off_at,task_description,task_execute_id,create_time,os.path.join('upload',username,'<br>'.join(a)).replace('\\','/'),task_hostsgroup.id,template_id)            
                print sql
                cursor.execute(sql)
            else:
                sql = '''insert into task(name,content,kick_off_at,description,execute_type_id,create_time,file,hostsgroup_id,task_template_id)
                            values("%s","%s","%s","%s","%s","%s","%s","%s","%s");'''%(task_name,task_content,task_kick_off_at,task_description,task_execute_id,create_time,'',task_hostsgroup.id,template_id)            
                print sql

                cursor.execute(sql)
           
            task_id = models.Task.objects.filter(name=task_name).last()
            
            try:
                if task_host_name:
                    for host_name in task_host_name:
                        host_name_id = models.Host.objects.get(hostname=host_name)
                        sql = 'insert into taskhoststatus(status,log,task_id,host_id)values(%d,"%s",%s,%s);'%(0,'',task_id.id,host_name_id.id)
                        print sql
        
                        cursor.execute(sql) 
        
                        host = models.Host.objects.get(hostname=host_name)
      
                        if  host.status.name == "online":
                            SSh = paramiko.SShClient()
                            SSh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            SSh.connect(host.wan_ip or host.lan_ip,22,'root',key_filename='D:\Documents\Identity')
                            #SSh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            #SSh.connect(str(host.lan_ip),22,"root","123456")
                            stdin, stdout, stderr = SSh.exec_command(task_content)
                        
                            std_out = stdout.readlines()
                            if  std_out:
                                sql = 'update taskhoststatus set status=1 where id=%d'%task_id.id
                                cursor.execute(sql)
                                
                                sql = 'insert into tasklog(result,log,host_id,date,task_id) values("%s","%s",%d,"%s",%d)'%('success',std_out,host.id,create_time,task_id.id)
                                cursor.execute(sql)
                            else:
                                sql = 'insert into tasklog(result,log,host_id,date,task_id) values("%s","%s",%d,"%s",%d)'%('failed',stderr.readlines(),host.id,create_time,task_id.id)
                                cursor.execute(sql)    
    
                        
                            if request.FILES:
                                
                                t = paramiko.Transport((host.wan_ip or host.lan_ip,22))
                                
                                mykey = paramiko.DSSKey.from_private_key_file('D:\Documents\Identity') 
                                   
                                t.connect(username='root',pkey=mykey)
                                
                                sftp = paramiko.SFTPClient.from_transport(t)
                                
                                remote_upload_dirname = os.path.join('/tmp','upload',username)
                                remote_upload_dirname = remote_upload_dirname.replace('\\','/')
                                stdin, stdout, stderr = SSh.exec_command('ls -ld %s'%remote_upload_dirname.replace('\\','/'))
                                
                                if not stdout.readlines():
                                    stdin, stdout, stderr = SSh.exec_command('mkdir -p %s'%remote_upload_dirname)
                                
                                for f_name in upload_filename:
                                    remotepath=os.path.join(remote_upload_dirname,f_name)
                                
                                    remotepath = remotepath.replace('\\','/')
                                
                                    localpath=os.path.join(dir_name,f_name)
                              
                                    sftp.put(localpath,remotepath)
                                
                                t.close() 
                        
         
                            
                            SSh.close()
                else:
                    
                    for host_name in models.Host.objects.filter(hostgroup_id = task_hostsgroup.id):
                        
                        host = models.Host.objects.get(hostname=host_name)
                        
                        if  host.status.name == "online":
                            host_name_id = models.Host.objects.get(hostname=host_name)
                            sql = 'insert into taskhoststatus(status,log,task_id,host_id)values(%d,"%s",%s,%s);'%(0,'',task_id.id,host_name_id.id)
                            print sql
        
                            cursor.execute(sql) 
        
                        
      
                        
                            SSh = paramiko.SShClient()
                            SSh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            SSh.connect(host.wan_ip or host.lan_ip,22,'root',key_filename='D:\Documents\Identity')
                            #SSh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            #SSh.connect(str(host.lan_ip),22,"root","123456")
                            stdin, stdout, stderr = SSh.exec_command(task_content)
                        
                            std_out = stdout.readlines()
                            if  std_out:
                                sql = 'update taskhoststatus set status=1 where id=%d'%task_id.id
                                cursor.execute(sql)
                                
                                sql = 'insert into tasklog(result,log,host_id,date,task_id) values("%s","%s",%d,"%s",%d)'%('success',std_out,host.id,create_time,task_id.id)
                                cursor.execute(sql)
                            else:
                                sql = 'insert into tasklog(result,log,host_id,date,task_id) values("%s","%s",%d,"%s",%d)'%('failed',stderr.readlines(),host.id,create_time,task_id.id)
                                cursor.execute(sql)    
    
                        
                            if request.FILES:
                                
                                t = paramiko.Transport((host.wan_ip or host.lan_ip,22))
                                
                                mykey = paramiko.DSSKey.from_private_key_file('D:\Documents\Identity') 
                                   
                                t.connect(username='root',pkey=mykey)
                                
                                sftp = paramiko.SFTPClient.from_transport(t)
                                
                                remote_upload_dirname = os.path.join('/tmp','upload',username)
                                remote_upload_dirname = remote_upload_dirname.replace('\\','/')
                                stdin, stdout, stderr = SSh.exec_command('ls -ld %s'%remote_upload_dirname.replace('\\','/'))
                                
                                if not stdout.readlines():
                                    stdin, stdout, stderr = SSh.exec_command('mkdir -p %s'%remote_upload_dirname)
                                
                                for f_name in upload_filename:
                                    remotepath=os.path.join(remote_upload_dirname,f_name)
                                
                                    remotepath = remotepath.replace('\\','/')
                                
                                    localpath=os.path.join(dir_name,f_name)
                              
                                    sftp.put(localpath,remotepath)
                                
                                t.close() 
                        
         
                            
                            SSh.close()            
            except Exception,e:
                print e
            if task_hostsgroup:
                sql = 'insert into task_hostsgroup(task_id,hostgroup_id)values(%d,%d);'%(task_id.id,task_hostsgroup.id)
                print sql 
                cursor.execute(sql)    
     
        return HttpResponseRedirect('/task/task_detail')
    else:
        print task_from.errors
        return render_to_response('task/task_create.html',{'f':task_from},context_instance=RequestContext(request))


@login_dresser
def task_detail(request,page):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    page = request.GET.get('page_id')
    
    form = forms.TaskForm()
    #task_list = models.TaskCenter.objects.all()

    page = common.try_int(page,1)
    
    count = models.Task.objects.all().count()

    pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

    result = models.Task.objects.all().order_by('-id')[pageObj.From:pageObj.To]

    task_list  = []

    for task in result:
        group_name = task.hostsgroup    

        hosts = []    
        for i in task.hosts.all():
            hosts.append(i.hostname)
            
        hosts = '<br>'.join(hosts)    

        task_info = {'id':task.id,
                     'name':task.name,
                     'content':task.content,
                     'filename':task.file,
                     'description':task.description,
                     'execute_type':task.execute_type,
                     'hosts':hosts,
                     'hostsgroup':group_name,
                     'created_by':username,
                     'kick_off_at':task.kick_off_at,
                     'create_time':task.create_time,
                     'total_tasks':models.TaskHostStatus.objects.filter(task_id=task.id).count(),
                     'failure':models.TaskLog.objects.filter(task_id=task.id,result='failed').count(),
                     'success':models.TaskLog.objects.filter(task_id=task.id,result='success').count(),
                    }
    
        task_list.append(task_info)
        
        
    page_string = html_helper_bootstarp.Custompager('/task/task_detail',page,pageObj.TotalPage)

    ret = {'f':form,'task_list':task_list,'count':count,'page_number':pageObj.TotalPage,'page':page_string}

    return render_to_response('task/task_detail.html',
                              ret,
                              context_instance=RequestContext(request)
                              )        

  
 
@login_dresser
def del_task(request):
    if request.method == 'POST':
        try:
            nid = request.POST.get('delnid')
            page_id = request.POST.get('page_id2')
            models.Task.objects.get(id=int(nid)).delete()
        except Exception,e:
            print e
        
    return redirect('/task/task_detail/%d'%int(page_id))  
  
@login_dresser
def task_log(request,page):        
    page = common.try_int(page,1)

    count = models.TaskLog.objects.filter().count()

    pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)
    
    status_id = request.GET.get('status_id')
    
    if status_id:
        result = models.TaskLog.objects.filter()[pageObj.From:pageObj.To]
    else:
        result = models.TaskLog.objects.all()[pageObj.From:pageObj.To]
        
    task_log = []
    
    for log in result:     
        #if isinstance(eval(log.log),list):
        #    log1 = '<br>'.join(eval(log.log)).replace(' ','&nbsp;')  
        #else:
        #    log1 = log.log.replace(' ','&nbsp;')
            
        
        log_dict = {
                    'id':log.id,
                    'task_id':log.task_id,
                    'task_name':models.Task.objects.get(id=log.task_id).name,
                    'content' : log.task.content,
                    'result':log.result,
                    'log':log.log.replace(' ','&nbsp;'),
                    'hostname':models.Host.objects.get(id=log.host_id).hostname,
                    'groupname':models.Host.objects.get(id=log.host_id).hostgroup,
                    'date':log.date
                    }

        task_log.append(log_dict)

    page_string = html_helper_bootstarp.Custompager('/task/task_log',page,pageObj.TotalPage)

    ret = {'data':task_log,'count':count,'page_number':pageObj.TotalPage,'page':page_string}

    return render_to_response('task/task_log.html',
                              ret,
                              context_instance=RequestContext(request)
                              )

    

@login_dresser
def del_task_log(request):
    if request.method == 'POST':
        try:
            nid = request.POST.get('delnid')
            page_id = request.POST.get('page_id')
            models.TaskLog.objects.get(id=int(nid)).delete()
        except Exception,e:
            print e
        
    return redirect('/task/task_log/?page_id=%d'%int(page_id))
    
#===================cmdb=====================================================


@login_dresser
def cmdb(request): 
    return render_to_response('cmdb/cmdb.html',context_instance=RequestContext(request))

@login_dresser
def create_host(request):
   
    if request.method == 'POST':
        form = forms.HostForm(request.POST)
        
        if form.is_valid():
            print  form.cleaned_data
            form.save()
        else:    
            print form.errors
            return render_to_response('cmdb/cmdb_create_host.html',
                              {'form':form},
                              context_instance=RequestContext(request)
                              )
    
    form = forms.HostForm()
    return render_to_response('cmdb/cmdb_create_host.html',
                              {'form':form},
                              context_instance=RequestContext(request)
                             )
        
@login_dresser
def del_host(request):
    if request.method == 'POST':
        try:
            nid = request.POST.get('delnid')
            page_id = request.POST.get('page_id2')
            models.Host.objects.get(id=int(nid)).delete()
        except Exception,e:
            print e
        
    return redirect('/cmdb/host_list/%d'%int(page_id))
    
import time
   
@login_dresser
def host_list(request):
    page = 1
    
    host_group_id = '' 
    
    hoststatus_id = ''
    
    if request.method == 'POST':   
        page =  request.POST.get('page_id')
        page = common.try_int(page,1)
    
        host_group_id = request.POST.get('hostgroup_id')
    
        if host_group_id:
            host_group_id = int(host_group_id)
 
    
        hoststatus_id = request.POST.get('hoststatus_id')
    
        if hoststatus_id:
            hoststatus_id = int(hoststatus_id)


        text_ip_hostname = request.POST.get("text_ip_hostname")    

    else:
        page =  request.GET.get('page_id')
        page = common.try_int(page,1)
    
        host_group_id = request.GET.get('hostgroup_id')
    
        if host_group_id:
            host_group_id = int(host_group_id)
 
    
        hoststatus_id = request.GET.get('hoststatus_id')
    
        if hoststatus_id:
            hoststatus_id = int(hoststatus_id)        

    
            
    if host_group_id and hoststatus_id:
        count = models.Host.objects.filter(hostgroup_id=host_group_id,status_id=hoststatus_id).count()

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

        results = models.Host.objects.filter(hostgroup_id=host_group_id,status_id=hoststatus_id).order_by("-id")[pageObj.From:pageObj.To]

        page_str = '?page_id=%d&hostgroup_id=%d&hoststatus_id=%d'%(page,host_group_id,hoststatus_id)

        if page>count:
            page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/%d'%count,page_str,pageObj.TotalPage)    
        else:
            page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page_str,pageObj.TotalPage)
            
    elif host_group_id:
        count = models.Host.objects.filter(hostgroup_id=host_group_id).count()

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

        results = models.Host.objects.filter(hostgroup_id=host_group_id).order_by("-id")[pageObj.From:pageObj.To]

        page_str = '?page_id=%d&hostgroup_id=%d'%(page,host_group_id)
        
        if page>pageObj.TotalPage:
            page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page_str,pageObj.TotalPage)      
        else:
            page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page_str,pageObj.TotalPage)
    elif hoststatus_id:
        count = models.Host.objects.filter(status_id=hoststatus_id).count()

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

        results = models.Host.objects.filter(status_id=hoststatus_id).order_by("-id")[pageObj.From:pageObj.To]

        page_str = '?page_id=%d&hoststatus_id=%d'%(page,hoststatus_id)

        page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page_str,pageObj.TotalPage)
        
    else:
        count = models.Host.objects.all().count()

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

        results = models.Host.objects.all().order_by("-id")[pageObj.From:pageObj.To]

        page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page,pageObj.TotalPage)                           
           

    ret = {'data':results,'count':count,'page_number':pageObj.TotalPage,'currentPage':page,'page':page_string}
    
    return render_to_response('cmdb/cmdb_host_list.html',
                              ret,
                              context_instance=RequestContext(request)
                              )

    
    
    
@login_dresser
def host_list_s(request):
    page = 1
    
    host_group_id = ''
    
    hoststatus_id = ''
    
    if request.method == 'POST':
        
        page = request.POST.get('page_id')
        
        page = common.try_int(page,1)
    
    
        host_group_id = request.POST.get('hostgroup_id') 
        hoststatus_id = request.POST.get('hoststatus_id')
    
        update_host_flag = request.POST.get("update_host_flag")
    
        text_ip_hostname = request.POST.get('text_ip_hostname')
    
    if host_group_id:
        host_group_id = int(host_group_id)   

    if hoststatus_id:
        hoststatus_id = int(hoststatus_id)

    if update_host_flag:  
        try:
            nid = request.POST.get('nid')
                     
            if nid:
                nid = int(nid)
                host_info = models.Host.objects.get(id=nid)
                host_info.hostname = request.POST.get('hostname')
                host_info.lan_ip = request.POST.get('lan_ip')
                host_info.wan_ip = request.POST.get('wan_ip')
                host_info.port = request.POST.get('port')
                host_info.memory = request.POST.get('memory')
                host_info.cpu = request.POST.get('cpu')
                host_info.brand = request.POST.get('brand')
                host_info.os = request.POST.get('os')
                host_info.status = models.HostStatus.objects.get(name=request.POST.get('status'))
                host_info.hostgroup = models.HostGroup.objects.get(groupname=request.POST.get('hostgroup2'))
                host_info.save()
            else:
               
                hostname = request.POST.get('hostname')
                lan_ip = request.POST.get('lan_ip')
                wan_ip = request.POST.get('wan_ip')
                port = request.POST.get('port')
                memory = request.POST.get('memory')
                cpu = request.POST.get('cpu')
                brand = request.POST.get('brand')
                os = request.POST.get('os')
                status = models.HostStatus.objects.get(name=request.POST.get('status'))
                hostgroup = models.HostGroup.objects.get(groupname=request.POST.get('hostgroup2'))
                host_info = models.Host(hostname=hostname,lan_ip=lan_ip,wan_ip=wan_ip,memory=memory,cpu=cpu,brand=brand,os=os,status=status,hostgroup=hostgroup)
                host_info.save()
        except Exception,e:
            print e 

     
    if text_ip_hostname:
        
        count = 1

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)


        results = models.Host.objects.filter(Q(hostname__contains = text_ip_hostname) | Q(lan_ip__contains = text_ip_hostname) | Q(wan_ip__contains = text_ip_hostname)).order_by("-id")
 
        str1 = '''
                <div id="host_list_conditions" class="table-responsive">
                <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>主机名</th>
                        <th>内网IP</th>
                        <th>外网IP</th>
                        <th>SSh端口</th>
                        <th>内存</th>
                        <th>CPU</th>
                        <th>品牌型号</th>
                        <th>操作系统</th>
                        <th>状态</th>
                        <th>主机组</th>
                        <th>创建时间</th>
                        <th>更新时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <div  >    <tbody>'''
        
        for result in results:
            s = ''
            if result.status.name == 'online':
                s = '<td class="success">%s</td>'%result.status
            else:
                s = '<td class="danger">%s</td>'%result.status
             
            if not result.wan_ip:
                result.wan_ip = ''
                  
              
            str2='''<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%d</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                %s
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                    <a onclick='EditItem(this);' class='label label-success'>编辑</a>
                    <a onclick='DeleteItem(this);' class='label label-danger''>删除</a
                </td>
            </tr>
            '''%(result.id,result.hostname,result.lan_ip,result.wan_ip,result.port,result.memory,result.cpu,result.brand,result.os,s,result.hostgroup,result.create_at,result.update_at)
            str1 = str1 +  str(str2)    
            
        
       
  
        return HttpResponse(str1)
     
     
     
    if host_group_id and hoststatus_id:

        count = models.Host.objects.filter(hostgroup_id=host_group_id,status_id=hoststatus_id).count()

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

        results = models.Host.objects.filter(hostgroup_id=host_group_id,status_id=hoststatus_id).order_by("-id")[pageObj.From:pageObj.To]
        
        str1 = '''
                <div id="host_list_conditions" class="table-responsive">
                <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>主机名</th>
                        <th>内网IP</th>
                        <th>外网IP</th>
                        <th>SSh端口</th>
                        <th>内存</th>
                        <th>CPU</th>
                        <th>品牌型号</th>
                        <th>操作系统</th>
                        <th>状态</th>
                        <th>主机组</th>
                        <th>创建时间</th>
                        <th>更新时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <div  >    <tbody>'''
        
        for result in results:
            s = ''
            if result.status.name == 'online':
                s = '<td class="success">%s</td>'%result.status
            else:
                s = '<td class="danger">%s</td>'%result.status
             
            if not result.wan_ip:
                result.wan_ip = ''
                  
              
            str2='''<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%d</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                %s
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                    <a onclick='EditItem(this);' class='label label-success'>编辑</a>
                    <a onclick='DeleteItem(this);' class='label label-danger''>删除</a
                </td>
            </tr>
            '''%(result.id,result.hostname,result.lan_ip,result.wan_ip,result.port,result.memory,result.cpu,result.brand,result.os,s,result.hostgroup,result.create_at,result.update_at)
            str1 = str1 +  str(str2)    
            
        
        
        str1 += '''
             <tr>
                <td>总记录数:%s</td>
                <td>总页数:%s</td>
                <td>当前页数:<span id="current_page" name="current_page">%s</span></td>
            </tr>   
        
            '''%(count,pageObj.TotalPage,page)
        
        page_str = '?page_id=%d&hostgroup_id=%d&hoststatus_id=%d'%(page,host_group_id,hoststatus_id)
        
        page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page_str,pageObj.TotalPage)

        
        str1 += '''
                </tbody>
                </table>
                %s
                </div>
                '''%page_string
  
        return HttpResponse(str1)  
        
    elif host_group_id:
        count = models.Host.objects.filter(hostgroup_id=host_group_id).count()

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

        results = models.Host.objects.filter(hostgroup_id=host_group_id).order_by("-id")[pageObj.From:pageObj.To]
        
        str1 = '''
                <div id="host_list_conditions" class="table-responsive">
                <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>主机名</th>
                        <th>内网IP</th>
                        <th>外网IP</th>
                        <th>SSh端口</th>
                        <th>内存</th>
                        <th>CPU</th>
                        <th>品牌型号</th>
                        <th>操作系统</th>
                        <th>状态</th>
                        <th>主机组</th>
                        <th>创建时间</th>
                        <th>更新时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <div  >    <tbody>'''
        
        for result in results:
            s = ''
            if result.status.name == 'online':
                s = '<td class="success">%s</td>'%result.status
            else:
                s = '<td class="danger">%s</td>'%result.status
                
            if not result.wan_ip:
                result.wan_ip = ''
                
                    
            str2='''<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%d</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                %s
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                    <a onclick='EditItem(this);' class='label label-success'>编辑</a>
                    <a onclick='DeleteItem(this);' class='label label-danger''>删除</a>
                </td>
            </tr>'''%(result.id,result.hostname,result.lan_ip,result.wan_ip,result.port,result.memory,result.cpu,
                 result.brand,result.os,s,result.hostgroup,result.create_at,result.update_at)
            
            str1 = str1 + str(str2)    
        
        str1 += '''
             <tr>
                <td>总记录数:%s</td>
                <td>总页数:%s</td>
                <td>当前页数:<span id="current_page" name="current_page">%s</span></td>
            </tr>   
        
            '''%(count,pageObj.TotalPage,page)
        
        page_str = '?page_id=%d&hostgroup_id=%d'%(page,host_group_id)
        
        page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page_str,pageObj.TotalPage)

        print page_string
        str1 += '''
                </tbody>
                </table>
                %s
                </div>
                '''%page_string
  
        return HttpResponse(str1)
            
        
    elif hoststatus_id:
        count = models.Host.objects.filter(status_id=hoststatus_id).count()

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

        results = models.Host.objects.filter(status_id=hoststatus_id).order_by("-id")[pageObj.From:pageObj.To]

        str1 = '''
                <div id="host_list_conditions" class="table-responsive">
                <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>主机名</th>
                        <th>内网IP</th>
                        <th>外网IP</th>
                        <th>SSh端口</th>
                        <th>内存</th>
                        <th>CPU</th>
                        <th>品牌型号</th>
                        <th>操作系统</th>
                        <th>状态</th>
                        <th>主机组</th>
                        <th>创建时间</th>
                        <th>更新时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <div  >    <tbody>'''
        for result in results:
            s = ''
            if result.status.name == 'online':
                s = '<td class="success">%s</td>'%result.status
            else:
                s = '<td class="danger">%s</td>'%result.status
                
            if not result.wan_ip:
                result.wan_ip = ''                
 
            str2='''<tr>
                <td>%d</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%d</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                %s
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                    <a onclick='EditItem(this);' class='label label-success'>编辑</a>
                    <a onclick='DeleteItem(this);' class='label label-danger''>删除</a
                </td>
            </tr>
            '''%(result.id,result.hostname,result.lan_ip,result.wan_ip,result.port,result.memory,result.cpu,result.brand,result.os,
                 s,result.hostgroup,result.create_at,result.update_at)

            str1 = str1 + str(str2)    
        
        str1 += '''
             <tr>
                <td>总记录数:%s</td>
                <td>总页数:%s</td>
                <td>当前页数:<span id="current_page" name="current_page">%s</span></td>
            </tr>   
        
            '''%(count,pageObj.TotalPage,page)
        
        page_str = '?page_id=%d&hoststatus_id=%d'%(page,hoststatus_id)
        
        page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page_str,pageObj.TotalPage)

        
        str1 += '''
                </tbody>
                </table>
                %s
                </div>
                '''%page_string
  
        return HttpResponse(str1)
        
    else:
        count = models.Host.objects.all().count()

        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

        results = models.Host.objects.all().order_by("-id")[pageObj.From:pageObj.To]

        str1 = '''
                <div id="host_list_conditions" class="table-responsive">
                <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>主机名</th>
                        <th>内网IP</th>
                        <th>外网IP</th>
                        <th>SSh端口</th>
                        <th>内存</th>
                        <th>CPU</th>
                        <th>品牌型号</th>
                        <th>操作系统</th>
                        <th>状态</th>
                        <th>主机组</th>
                        <th>创建时间</th>
                        <th>更新时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <div  >    <tbody>'''
        
        for result in results:
            s = ''
            if result.status.name == 'online':
                s = '<td class="success">%s</td>'%result.status
            else:
                s = '<td class="danger">%s</td>'%result.status
                
            if not result.wan_ip:
                result.wan_ip = ''
                                
            str2='''<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%d</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                %s
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                    <a onclick='EditItem(this);' class='label label-success'>编辑</a>
                    <a onclick='DeleteItem(this);' class='label label-danger''>删除</a
                </td>
            </tr>
            '''%(result.id,result.hostname,result.lan_ip,result.wan_ip,result.port,result.memory,result.cpu,result.brand,result.os,s,result.hostgroup,result.create_at,result.update_at)
            
            str1 = str1 + str(str2)    

        str1 += '''
             <tr>
                <td>总记录数:%d</td>
                <td>总页数:%d</td>
                <td>当前页数:<span id="current_page" name="current_page">%s</span></td>
            </tr>   
        
            '''%(count,pageObj.TotalPage,page)

     
        page_string = html_helper_bootstarp.Custompager('/cmdb/host_list_s/',page,pageObj.TotalPage)

        
        str1 += '''
                </tbody>
                </table>
                %s
                </div>
                '''%page_string
  
        return HttpResponse(str1)




@login_dresser
def host_group_list(request):
    
    if request.method == 'POST':
        
        page_id = request.POST.get('page_id')
        
        page_id = int(page_id)
        
        count = models.HostGroup.objects.all().count()

        pageObj = html_helper_bootstarp.PageInfo(page_id,count,peritems=PAGE_SIZE)

        results = models.HostGroup.objects.all()[pageObj.From:pageObj.To]
   
        str1 = '''
                <div id="host_group_list_conditions" class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>主机组名</th>
                            </tr>
                        </thead>
        
                        <tbody>
                
                '''
        for result in results:
            
            str2 = '''
                        <tr>
                            <td>%d</td>
                            <td>%s</td>
                            <td>
                                <a onclick='EditItem(this);' class='label label-success'>编辑</a>
                                <a onclick='DeleteItem(this);' class='label label-danger''>删除</a
                            </td>
                        </tr>
                    '''%(result.id,result.groupname)
                        
            str1 = str1 + str(str2)
            
            
        str1 += '''    
                        <tr>
                            <td>总记录数:%d</td>
                            <td>总页数:%d</td>
                            <td>当前页数:<span id="current_page" name="current_page">%s</span></td>
                        </tr>
                        
                '''%(count,pageObj.TotalPage,page_id)
                
        page_string = html_helper_bootstarp.Custompager('/cmdb/host_group_list/',page_id,pageObj.TotalPage)        
        str1 += '''        
                    </tbody>        
                </table>       
                %s
            </div>
            '''%page_string
            
        return HttpResponse(str1)    
        
    else:    
        page = 1
    
        count = models.HostGroup.objects.all().count()
    
        pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)
    
        results = models.HostGroup.objects.all()[pageObj.From:pageObj.To]
    
        page_string = html_helper_bootstarp.Custompager('/cmdb/host_group_list/',page,pageObj.TotalPage)                           
               
    
        ret = {'data':results,'count':count,'page_number':pageObj.TotalPage,'currentPage':page,'page':page_string}
    
        return render_to_response('cmdb/cmdb_host_group_list.html',
                                  ret,
                                  context_instance=RequestContext(request)
                                  )



@login_dresser
def host_group_create(request):
   
    if request.method == 'POST':
        form = forms.HostGroupForm(request.POST)
        
        if form.is_valid():
            print  form.cleaned_data
            form.save()
        else:    
            print form.errors
            return render_to_response('cmdb/cmdb_create_host_group.html',
                              {'form':form},
                              context_instance=RequestContext(request)
                              )
    
    form = forms.HostGroupForm()
    return render_to_response('cmdb/cmdb_create_host_group.html',
                              {'form':form},
                              context_instance=RequestContext(request)
                             )
    
    
    
    
    
    
    
@login_dresser    
def host_group_update_add(request):
   
    if request.method == 'POST':
        
        id = request.POST.get('id')
        
        groupname = request.POST.get('hostgroupname')
        
        page_id = request.POST.get('page_id')   
         
        if page_id:
            page_id = int(page_id)
        else:
            page_id = 1
        
        try:
            if id:
                a = models.HostGroup.objects.filter(groupname = groupname)
                if a:
                    pass
                else:
                    a = models.HostGroup.objects.get(id = id)
                    a.groupname = groupname
                    a.save()    
                    
            else:
                models.HostGroup.objects.create(groupname = groupname)    
        except Exception,e:
            print e
        count = models.HostGroup.objects.all().count()

        pageObj = html_helper_bootstarp.PageInfo(page_id,count,peritems=PAGE_SIZE)

        results = models.HostGroup.objects.all()[pageObj.From:pageObj.To]
   
        str1 = '''
                <div id="host_group_list_conditions" class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>主机组名</th>
                            </tr>
                        </thead>
        
                        <tbody>
                
                '''
        for result in results:
            
            str2 = '''
                        <tr>
                            <td>%d</td>
                            <td>%s</td>
                            <td>
                                <a onclick='EditItem(this);' class='label label-success'>编辑</a>
                                <a onclick='DeleteItem(this);' class='label label-danger''>删除</a
                            </td>
                        </tr>
                    '''%(result.id,result.groupname)
                        
            str1 = str1 + str(str2)
            
            
        str1 += '''    
                        <tr>
                            <td>总记录数:%d</td>
                            <td>总页数:%d</td>
                            <td>当前页数:<span id="current_page" name="current_page">%s</span></td>
                        </tr>
                        
                '''%(count,pageObj.TotalPage,page_id)
                
        page_string = html_helper_bootstarp.Custompager('/cmdb/host_group_list/',page_id,pageObj.TotalPage)        
        str1 += '''        
                    </tbody>        
                </table>       
                %s
            </div>
            '''%page_string
            
        return HttpResponse(str1) 

    





def host_group_del(request):
    if request.method == 'POST':
        
        id = request.POST.get('id')
        
        groupname = request.POST.get('hostgroupname')
        
        page_id = request.POST.get('page_id')   
         
        if page_id:
            page_id = int(page_id)
        else:
            page_id = 1
        
        try:
            if groupname:
                models.HostGroup.objects.get(groupname=groupname).delete()
            else:
                models.HostGroup.objects.get(id=id).delete()   
        except Exception,e:
            print e
            
        count = models.HostGroup.objects.all().count()

        pageObj = html_helper_bootstarp.PageInfo(page_id,count,peritems=PAGE_SIZE)

        results = models.HostGroup.objects.all()[pageObj.From:pageObj.To]
   
        str1 = '''
                <div id="host_group_list_conditions" class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>主机组名</th>
                            </tr>
                        </thead>
        
                        <tbody>
                
                '''
        for result in results:
            
            str2 = '''
                        <tr>
                            <td>%d</td>
                            <td>%s</td>
                            <td>
                                <a onclick='EditItem(this);' class='label label-success'>编辑</a>
                                <a onclick='DeleteItem(this);' class='label label-danger''>删除</a
                            </td>
                        </tr>
                    '''%(result.id,result.groupname)
                        
            str1 = str1 + str(str2)
            
            
        str1 += '''    
                        <tr>
                            <td>总记录数:%d</td>
                            <td>总页数:%d</td>
                            <td>当前页数:<span id="current_page" name="current_page">%s</span></td>
                        </tr>
                        
                '''%(count,pageObj.TotalPage,page_id)
                
        page_string = html_helper_bootstarp.Custompager('/cmdb/host_group_list/',page_id,pageObj.TotalPage)        
        str1 += '''        
                    </tbody>        
                </table>       
                %s
            </div>
            '''%page_string
        print str1    
        return HttpResponse(str1)
    
    



def getHostStatus(request):
    host_status_lists = models.HostStatus.objects.all()
  
    hoststatus_list = []
    
    for hsl in host_status_lists:
        L1 = {'host_status_id':hsl.id,'host_status':hsl.memo}
        hoststatus_list.append(L1)
        
    
    return HttpResponse(json.dumps(hoststatus_list),content_type="application/json")

    
    

def getHostGroup(reqeust):
    groups = models.HostGroup.objects.order_by('-id')
    
    group_list = []
    
    for group in groups:
        L1 = {'group_id':group.id,'group_name':group.groupname}
        group_list.append(L1)
        
        
    return HttpResponse(json.dumps(group_list),content_type="application/json")


#-------------------------------------------------------------------------------------------

@login_dresser
def service_status(request): 
    
    return render_to_response('cmdb/cmdb_service_status.html',
                              context_instance=RequestContext(request)
                              )

@login_dresser
def service_group(request):
    return render_to_response('cmdb/cmdb_service_group.html',
                              context_instance=RequestContext(request)
                              )
    
@login_dresser
def host_group(request):
    return render_to_response('cmdb/cmdb_host_group.html',
                              context_instance=RequestContext(request)
                              )



#-----------------rest---------------------------------------------------------------------------
from rest_framework.decorators import api_view
from third.serializers import HostSerializer,HostGroupSerializer,HostStatusSerializer
from rest_framework import viewsets

class HostGroupViewSet(viewsets.ModelViewSet):
    queryset = models.HostGroup.objects.all()
    serializer_class = HostGroupSerializer
    
    
    
class HostStatusViewSet(viewsets.ModelViewSet):
    queryset = models.HostStatus.objects.all()
    serializer_class = HostStatusSerializer    


#@api_view(['GET','POST'])
class HostViewSet(viewsets.ModelViewSet):
    queryset = models.Host.objects.all()
    serializer_class = HostSerializer
    
    
from django.contrib.auth.models import User, Group
from third.serializers import UserSerializer, GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    




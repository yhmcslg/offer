#coding:utf8

from django.shortcuts import  render_to_response,redirect,render
from django.template import RequestContext  
from django.http import  HttpResponse

import os,sys,platform
reload(sys)

if platform.system() == 'Linux':
    sys.setdefaultencoding('utf8')


from app001 import models

from app001.views import login_dresser

import json,datetime,time

import paramiko


from third import handle_uploaded

from offer.settings import BASE_DIR,PAGE_SIZE

import threading

import Queue

from third import html_helper_bootstarp

from third import common

from app001 import forms

from django.db import connection,transaction

import subprocess 

@login_dresser
def cmd(request):
    return render_to_response('cmdb/cmd.html',context_instance=RequestContext(request))


@login_dresser
def cmd_code_release(request):
    return render_to_response('cmdb/code_release.html',context_instance=RequestContext(request))

@login_dresser
def cmd_hostname(request):
    if request.method == 'POST':
        hostgroup_id = int(request.POST.get('hostgroup_id'))
        
        
    if hostgroup_id:    
        host_info = models.Host.objects.filter(hostgroup_id=hostgroup_id,status=models.HostStatus.objects.get(name='online'))  
    else:
        host_info = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))  
    
    h_i = []
    
    for host_in in host_info:
        H1 = {'id':host_in.id,'hostname':host_in.hostname,'wan_ip':host_in.wan_ip,'lan_ip':host_in.lan_ip,'port':host_in.port}
        h_i.append(H1)
        
    return HttpResponse(json.dumps(h_i),content_type="application/json")    


q = []


def ssh2(ip,hostname,port,username,cmd_content,files,login_username,hostgroup_ids,number_of_machine):
    
    content = ''

    dir_name = os.path.join(BASE_DIR,'upload',login_username)
    
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)  
                
                
    upload_filename=[]
    
    u_s = models.AdminInfo.objects.select_related().get(username=login_username).user_info.user_type.caption

    cursor = connection.cursor() 

    if files:
        filename = files.getlist('file')
        for file_name in filename:
            handle_uploaded.handle_uploaded_file(os.path.join(dir_name,file_name.name),file_name)
            upload_filename.append(file_name.name)  
                    
        a = []    
                
        for i in upload_filename:
            a.append(os.path.join('/tmp','upload',login_username,i))
        
        sql = '''insert into task(name,content,kick_off_at,description,execute_type_id,create_time,file,hostsgroup_id,task_template_id)
                    values("%s","%s","%s","%s","%s","%s","%s","%s","%s");
            '''%(u'立即执行命令',cmd_content,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'',4,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),os.path.join('upload',username,'<br>'.join(a)).replace('\\','/'),hostgroup_ids,'')            

        cursor.execute(sql)
        
        task_id = models.Task.objects.all().last().id
        host_name_id = models.Host.objects.get(hostname=hostname).id
        sql = 'insert into taskhoststatus(status,log,task_id,host_id)values(%d,"%s",%s,%s);'%(0,'',task_id,host_name_id)
        cursor.execute(sql)
    else:
        sql = '''insert into task(name,content,kick_off_at,description,execute_type_id,create_time,file,hostsgroup_id,task_template_id)
                values("%s","%s","%s","%s","%s","%s","%s","%s","%s");
            '''%(u'立即执行命令',cmd_content.replace('"',"'"),datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'',4,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'',hostgroup_ids,'')            

        cursor.execute(sql)
        
        task_id = models.Task.objects.all().last().id
        host_name_id = models.Host.objects.get(hostname=hostname).id
        sql = 'insert into taskhoststatus(status,log,task_id,host_id)values(%d,"%s",%s,%s);'%(0,'',task_id,host_name_id)
        cursor.execute(sql)        
            
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(ip,port,username,key_filename='D:\Documents\Identity',timeout=2)
            
            start_exec_time_stamp = time.time()
            
            start_exec_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            stdin, stdout, stderr = ssh.exec_command(cmd_content)  
            
            std_out = stdout.readlines()
    
            std_err = stderr.readlines()
    
            end_exec_time_stamp = time.time()
            
            end_exec_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
            diff_exec_time_stamp = end_exec_time_stamp - start_exec_time_stamp
    

            content = "第%d台机器</br>"%number_of_machine
            content += "<font color='red'>开始时间:" + start_exec_time +"<br/>"
            content += "结束时间:" + end_exec_time + "</font><br/>"
            content += "执行时间:" + str(diff_exec_time_stamp) + "</font></br>"
            content += "<font color='blue'>主机名:"+ hostname + "</br>"
            content += "IP:" + ip + "</font><br/>"
 
            content += "<font color='green'>输出内容:<br/>"



            if  std_out:
                sql = 'update taskhoststatus set status=1 where id=%d'%task_id
                cursor.execute(sql)
                     
                std_outs = ''
                          
                for out in std_out:
                    std_outs += out        
                                
                sql = 'insert into tasklog(result,log,host_id,date,task_id) values("%s","%s",%d,"%s",%d)'%('success',std_outs,host_name_id,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),task_id)
                print sql
                
                try:
                    cursor.execute(sql) 
                except Exception,e:
                    print e
                    content += e              

                for s in std_out:
                    s = s.replace("\n","<br/>")
                    s = s.replace(" ","&nbsp;")
                    if s.find('\x1b[7l'):
                        s = s.replace("\x1b[7l","")
                    content += s
                    
                content += "</font></br>"
                
                content += '-'*100+" <br/><br/>"  
                    
            elif std_err:
                std_errs = ''
                
                for err in std_err:
                    std_errs += err
                
                sql = 'insert into tasklog(result,log,host_id,date,task_id) values("%s","%s",%d,"%s",%d)'%('failed',std_errs,host_name_id,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),task_id)
                
                try:
                    cursor.execute(sql)   
                except Exception,e:
                    print e
                    content += e  
                                
                print '222:',std_err

                for s in std_err:
                    s = s.replace("\n","<br/>")
                    s = s.replace(" ","&nbsp;")
                    if s.find('\x1b[7l'):
                        s = s.replace("\x1b[7l","")
    
                    content += s  
                    
                content += "</font></br>"
                
                content += '-'*100+" <br/><br/>"        
                    
            else:
                sql = 'insert into tasklog(result,log,host_id,date,task_id) values("%s","%s",%d,"%s",%d)'%('failed',[u'命令执行完成，没有输出!'],host_name_id,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),task_id)
                cursor.execute(sql) 
          
                print '333:'
                content += u'命令执行完成，没有输出!<br />'
                content += '-'*100+" <br/>"
                
                
        except Exception,e:
            print '444:%s'%str(e)
            sql = 'insert into tasklog(result,log,host_id,date,task_id) values("%s","%s",%d,"%s",%d)'%('failed',[str(e)],host_name_id,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),task_id)
            cursor.execute(sql) 
            
            content = "第%d台机器<br />"%number_of_machine
            content += "<font color='red'>"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"<br/>"+hostname+":</font>  <br/>"
            content += str(e)
            content += u'<br />ip:%s 连接失败...............<br />'%ip
            content += '-'*100+" <br/>"
        
    except Exception,e:
        print e    
          
        
        if files:
           
            t = paramiko.Transport((ip,port))
           
            mykey = paramiko.DSSKey.from_private_key_file('D:\Documents\Identity') 
              
            t.connect(username=username,pkey=mykey)
           
            sftp = paramiko.SFTPClient.from_transport(t)
           
            remote_upload_dirname = os.path.join('/tmp','upload',login_username)
            remote_upload_dirname = remote_upload_dirname.replace('\\','/')
            stdin, stdout, stderr = ssh.exec_command('ls -ld %s'%remote_upload_dirname.replace('\\','/'))
           
            if not stdout.readlines():
                stdin, stdout, stderr = ssh.exec_command('mkdir -p %s'%remote_upload_dirname)
           
            for f_name in upload_filename:
                remotepath=os.path.join(remote_upload_dirname,f_name)
           
                remotepath = remotepath.replace('\\','/')
           
                localpath=os.path.join(dir_name,f_name)
         
                sftp.put(localpath,remotepath)
           
            t.close() 
   
        ssh.close()   
    except Exception,e:
        print e   
  
    q.append(content) 
    print '循环中的q:',q        
    #return content
    
@login_dresser
def cmd_run(request):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    u_s = models.AdminInfo.objects.select_related().get(username=username).user_info.user_type.caption
    
    if u_s == u'普通运维':
        username_s = 'level1'
    else:
        username_s = 'level2'
    
    username_s = 'root'
    
    if request.method == "POST":
        host_ids = request.POST.getlist('host_id[]')
        hostgroup_ids = request.POST.getlist('hostgroup_id[]')
        if hostgroup_ids:
            hostgroup_ids = hostgroup_ids[0:]
            
        cmd_content = str(request.POST.get('cmd_content'))


    if host_ids:
        if len(host_ids) == 1 and host_ids[0] == -1:
            return HttpResponse('请选择要执行命令的主机<br/>')
        elif not  cmd_content :
            return HttpResponse('请输入要执行的命令<br/>')
        else:
            contents = ''
            ths = []
            
            number_of_machine = 1
            for host in host_ids:
                host = models.Host.objects.get(id=host)

                th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,hostgroup_ids,number_of_machine))
                ths.append(th)
                
                number_of_machine = number_of_machine + 1

            for i in ths:
                i.setDaemon(False)    
                i.start()
            for i in ths:    
                i.join()  
                
        contents = ''
        
        q.reverse()
       
        for j in range(len(q)):
            contents +=  q.pop()
            print contents 
        return HttpResponse(contents) 
           
    elif hostgroup_ids:
        if  len(hostgroup_ids[0]) == 1 and int(hostgroup_ids[0]) == -1 :
            return HttpResponse('请选择要执行命令的主机组<br/>')
        elif not cmd_content:
            return HttpResponse('请输入要执行的命令<br/>')
        else:
            ths = []
            global q 
            q = []
            
            number_of_machine = 1
            
            for hostgroup in hostgroup_ids:
                hostgroup = int(hostgroup)
                if hostgroup == 0:
                    hosts = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))
                    for host in hosts:
                        th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,hostgroup,number_of_machine))
                        ths.append(th)
                        number_of_machine = number_of_machine + 1

                    for i in ths:
                        i.setDaemon(False)    
                        i.start()
                    for i in ths:    
                        i.join()  
  
                else:
                    for host in models.Host.objects.filter(hostgroup=models.HostGroup.objects.get(id=hostgroup),status=models.HostStatus.objects.get(name='online')):
                        th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,hostgroup,number_of_machine))
                        ths.append(th)
                        number_of_machine = number_of_machine + 1
                        
            for i in ths:
                i.setDaemon(False)    
                i.start()
            for i in ths:    
                i.join()    
            
        contents = ''
        
        q.reverse()
       
        print '最后的q:',q
        for j in range(len(q)):
            contents +=  q.pop()
            print '222:',contents      
                            
        return HttpResponse(contents)                
    else:
        return HttpResponse('请选择主机组或主机<br/>')   

@login_dresser
def update_svn(request):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    u_s = models.AdminInfo.objects.select_related().get(username=username).user_info.user_type.caption
    
    if u_s == u'普通运维':
        username_s = 'level1'
    else:
        username_s = 'level2'
    
    username_s = 'root'
    
    if request.method == "POST":
        host_ids = request.POST.getlist('host_id[]')
        hostgroup_ids = request.POST.getlist('hostgroup_id[]')
        if hostgroup_ids:
            hostgroup_ids = hostgroup_ids[0]
            
        change_code_url = request.POST.get('change_code_url')
        
        target_path_name = request.POST.get('target_path_name')

        svn_version = request.POST.get('svn_version')

    if svn_version != "CheckOut":
        cmd_content = '''
                    svn info %s;
                    if [ $? -eq 0 ];then
                        svn update -r %s %s
                    fi
                '''%(target_path_name,svn_version,target_path_name)
    else:
        cmd_content = ''' 
                        if [ ! -d %s ];then 
                            mkdir -p %s;
                        fi; 
                        
                        svn info %s >/dev/null 2>&1 ;
                        
                        if [ $? -ne 0 ];then  
                            svn co --username Yanhouming --password yhm %s %s ;
                        else  
                            svn update %s ;
                        fi;
                    '''%(target_path_name,target_path_name,target_path_name,change_code_url,target_path_name,target_path_name)

  
    if host_ids:
        if len(host_ids) == 1 and host_ids[0] == -1:
            return HttpResponse('请选择要执行命令的主机<br/>')
        elif not  target_path_name :
            return HttpResponse('请输入远端地址<br/>')
        elif not change_code_url:
            return HttpResponse('请选择SVN地址<br/>')
        else:
            contents = ''
            ths = []
            for host in host_ids:
                host = models.Host.objects.get(id=host)

                th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                ths.append(th)

            for i in ths:
                i.setDaemon(False)    
                i.start()
            for i in ths:    
                i.join()  
                
        contents = ''
        
        q.reverse()
       
        for j in range(len(q)):
            contents +=  q.pop()
            print contents 
        return HttpResponse(contents) 
           
    elif hostgroup_ids:
        if  int(hostgroup_ids) == -1 :
            return HttpResponse('请选择要执行命令的主机组<br/>')
        elif not  target_path_name :
            return HttpResponse('请输入远端地址<br/>')
        elif not change_code_url:
            return HttpResponse('请选择SVN地址<br/>')
        else:
            ths = []
            global q 
            q = []
            for hostgroup in hostgroup_ids:
                hostgroup = int(hostgroup)
                if hostgroup == 0:
                    hosts = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))
                    for host in hosts:
                        th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                        ths.append(th)

                    for i in ths:
                        i.setDaemon(False)    
                        i.start()
                    for i in ths:    
                        i.join()  
  
                else:
                    for host in models.Host.objects.filter(hostgroup=models.HostGroup.objects.get(id=hostgroup),status=models.HostStatus.objects.get(name='online')):
                        th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                        ths.append(th)
                        
                    for i in ths:
                        i.setDaemon(False)    
                        i.start()
                    for i in ths:    
                        i.join()    
            
        contents = ''
        
        q.reverse()
       
        print '最后的q:',q
        for j in range(len(q)):
            contents +=  q.pop()
            print '222:',contents      
                            
        return HttpResponse(contents)                
    else:
        return HttpResponse('请选择主机组或主机<br/>')

 

@login_dresser    
def get_svn_info(request):
    change_code_url = request.POST.get('change_code_url')
    
    resutl = []
    
    i = 1
    
    p = subprocess.Popen('svn log %s'%change_code_url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    for line in p.stdout.readlines():
        
        if not line.find('-'):
            continue
        
        L1 = {'id':i,'svn_log':line.encode('utf8')}
        
        resutl.append(L1)
        
        i+=1
    
        print line.encode('utf8')
    return HttpResponse(json.dumps(resutl),content_type="application/json")  


@login_dresser  
def select_svn(request):
    
    username = request.COOKIES.get('username_password')
  
    if username:
        username = username.split('&')[0]
        
    username_s = 'root'
    
    target_path_name = request.POST.get('target_path_name')
    
    cmd_content = '''
            svn info %s
    '''%target_path_name

    
    host_ids = request.POST.getlist('host_id[]')
    
    hostgroup_ids = request.POST.getlist('hostgroup_id[]')
    
    change_code_url = request.POST.getlist('change_code_url')
    
    

     
    if not change_code_url:
        return HttpResponse('请选择源SVN地址<br/>')
    
    elif not  target_path_name :
        return HttpResponse('请输入目标地址<br/>')
    
    elif hostgroup_ids:
        
        ths = []
        for hostgroup_id in hostgroup_ids:
            for host in models.Host.objects.filter(hostgroup=models.HostGroup.objects.get(id=hostgroup_id),status=models.HostStatus.objects.get(name='online')):
                th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                ths.append(th)
    
        for i in ths:
            i.setDaemon(False)    
            i.start()
        for i in ths:    
            i.join()  
            
        contents = ''
        
        q.reverse()
       
        for j in range(len(q)):
            contents +=  q.pop()
            print contents 
        return HttpResponse(contents)  
       

    elif not host_ids:  
        return HttpResponse("请选择主机!<br />") 
    else:
        for host_id in host_ids:
            host = models.Host.objects.get(id=host_id)

        th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,'',username,','.join(eval(hostgroup_ids))))

        th.start()
        
        th.join()

        contents = ''
        
        q.reverse()
       
        for j in range(len(q)):
            contents +=  q.pop()
            print contents 
        return HttpResponse(contents) 

@login_dresser
def cmd_detail(request,page):
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
        
        
    page_string = html_helper_bootstarp.Custompager('/cmdb/cmd_detail/',page,pageObj.TotalPage)

    ret = {'f':form,'task_list':task_list,'count':count,'page_number':pageObj.TotalPage,'page':page_string,'current_page':page}

    return render_to_response('cmdb/cmdb_detail.html',
                              ret,
                              context_instance=RequestContext(request)
                              )  
 
 
    
@login_dresser  
def cmd_log(request,page):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    page = request.GET.get('page_id')
    
    page = common.try_int(page,1)

    count = models.TaskLog.objects.filter().count()

    pageObj = html_helper_bootstarp.PageInfo(page,count,peritems=PAGE_SIZE)

    result = models.TaskLog.objects.all().order_by('-id')[pageObj.From:pageObj.To]
    
    task_log = []
    
    for log in result:              
        
            
            
        log_dict = {
                    'id':log.id,
                    'task_id':log.task_id,
                    'task_name':models.Task.objects.get(id=log.task_id).name,
                    'content' : log.task.content,
                    'result':log.result,
                    'log':log.log.replace(' ','&nbsp;').replace('\n','<br />'),
                    'hostname':models.Host.objects.get(id=log.host_id).hostname,
                    'groupname':models.Host.objects.get(id=log.host_id).hostgroup,
                    'date':log.date
                    }

        task_log.append(log_dict)

    page_string = html_helper_bootstarp.Custompager('/cmdb/cmd_log/',page,pageObj.TotalPage)

    ret = {'data':task_log,'count':count,'page_number':pageObj.TotalPage,'page':page_string,'current_page':page}

    return render_to_response('cmdb/cmdb_log.html',
                              ret,
                              context_instance=RequestContext(request)
                              )
 
@login_dresser
def del_cmdb_log(request):
    if request.method == 'POST':
        try:
            nid = request.POST.get('delnid')
            page_id = request.POST.get('page_id')
            models.TaskLog.objects.get(id=int(nid)).delete()
        except Exception,e:
            print e
        
    return redirect('/cmdb/cmd_log/?page_id=%d'%int(page_id))   
   
   
    
@login_dresser  
def nt_floor(request):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    u_s = models.AdminInfo.objects.select_related().get(username=username).user_info.user_type.caption
    
    if u_s == u'普通运维':
        username_s = 'level1'
    else:
        username_s = 'level2'
      
    username_s = 'root'
        
    if request.method == "POST":
        host_ids = request.POST.getlist('host_id[]')
        hostgroup_ids = request.POST.getlist('hostgroup_id[]')
        

    # cmd_content = '''
    #    netstat -ntu |grep -Ev '127.0.0|172.16|192.168' |  awk '{print $5}' | cut -d: -f1 | sed -n '/[0-9]/p' | sort | uniq -c | sort -nr |awk '{if($1>100) system("iptables -I " $2 " --dport 80 -j DROP")}'
    #'''
    
    cmd_content = '''
        netstat -ntu |grep -Ev '127.0.0|172.16|192.168' |  awk '{print $5}' | cut -d: -f1 | sed -n '/[0-9]/p' | sort | uniq -c | sort -nr |head -n 20
    '''
    
    if host_ids:
        contents = ''
        ths = []
        for host in host_ids:
            host = models.Host.objects.get(id=host)

            th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
            ths.append(th)

        for i in ths:
            i.setDaemon(False)    
            i.start()
        for i in ths:    
            i.join()  
                    
        contents = ''
        
        q.reverse()
       
        for j in range(len(q)):
            contents +=  q.pop()
            print contents 
        return HttpResponse(contents) 
           
    elif hostgroup_ids:
        
        ths = []
        global q 
        q = []
        for hostgroup in hostgroup_ids:
            hostgroup = int(hostgroup)
            if hostgroup == 0:
                hosts = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))
                for host in hosts:
                    th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                    ths.append(th)

                for i in ths:
                    i.setDaemon(False)    
                    i.start()
                for i in ths:    
                    i.join()  

            else:
                for host in models.Host.objects.filter(hostgroup=models.HostGroup.objects.get(id=hostgroup),status=models.HostStatus.objects.get(name='online')):
                    th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                    ths.append(th)
                    
                for i in ths:
                    i.setDaemon(False)    
                    i.start()
                for i in ths:    
                    i.join()    
            
        contents = ''
        
        q.reverse()
       
        
        for j in range(len(q)):
            contents +=  q.pop()
             
        return HttpResponse(contents)        
        
    else:
        return HttpResponse('请选择主机组或主机<br/>')       
        
  
@login_dresser  
def pic_floor(request):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    u_s = models.AdminInfo.objects.select_related().get(username=username).user_info.user_type.caption
    
    if u_s == u'普通运维':
        username_s = 'level1'
    else:
        username_s = 'level2'
        
    if request.method == "POST":
        host_ids = request.POST.getlist('host_id[]')
        hostgroup_ids = request.POST.getlist('hostgroup_id[]')
        
    username_s = 'root'    

    cmd_content = '''
        echo "最大的前10个文件:"
        cat   /var/log/nginx/access.log|awk '{print $7,$10}'|sort -k 2 -nr|uniq -i|head -n 10;
        echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>";
        echo "访问量最多前10个文件:";
        cat  /var/log/nginx/access.log|awk  '{a[$7]+=$10}END{for(i in a){print i,a[i]}}'|sort -k 2 -nr|head -n 10;
        echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>";
        echo "访问次数最多的10个文件:";
        cat   /var/log/nginx/access.log|awk '{print $7}'|uniq -c|sort -k1 -nr|head -n 10;
    '''
    
    if host_ids:
        contents = ''
        ths = []
        for host in host_ids:
            host = models.Host.objects.get(id=host)

            th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
            ths.append(th)

        for i in ths:
            i.setDaemon(False)    
            i.start()
        for i in ths:    
            i.join()  
                    
        contents = ''
        
        q.reverse()
       
        for j in range(len(q)):
            contents +=  q.pop()
            print contents 
        return HttpResponse(contents) 
           
    elif hostgroup_ids:
        
        ths = []
        global q 
        q = []
        for hostgroup in hostgroup_ids:
            hostgroup = int(hostgroup)
            if hostgroup == 0:
                hosts = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))
                for host in hosts:
                    th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                    ths.append(th)

                for i in ths:
                    i.setDaemon(False)    
                    i.start()
                for i in ths:    
                    i.join()  

            else:
                for host in models.Host.objects.filter(hostgroup=models.HostGroup.objects.get(id=hostgroup),status=models.HostStatus.objects.get(name='online')):
                    th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                    ths.append(th)
                    
                for i in ths:
                    i.setDaemon(False)    
                    i.start()
                for i in ths:    
                    i.join()    
            
        contents = ''
        
        q.reverse()
       
        
        for j in range(len(q)):
            contents +=  q.pop()
             
        return HttpResponse(contents)        
        
    else:
        return HttpResponse('请选择主机组或主机<br/>') 
        
        
   
@login_dresser  
def web_floor(request):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    u_s = models.AdminInfo.objects.select_related().get(username=username).user_info.user_type.caption
    
    if u_s == u'普通运维':
        username_s = 'level1'
    else:
        username_s = 'level2'
        
    if request.method == "POST":
        host_ids = request.POST.getlist('host_id[]')
        hostgroup_ids = request.POST.getlist('hostgroup_id[]')
        
    username_s = 'root'
    
    cmd_content = '''
        awk  '/%s\/%s\/2016/{++S[$1]} END {for(a in S) printf("%%-30s %%s\\n",a, S[a])}'  /var/log/nginx/access.log|sort -k 2 -nr
    '''%(datetime.datetime.now().strftime('%d'),datetime.datetime.now().strftime('%b'))
    
    print cmd_content
    print type(hostgroup_ids)
    print hostgroup_ids
    if host_ids:
        contents = ''
        ths = []
        for host in host_ids:
            host = models.Host.objects.get(id=host)

            th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(str(hostgroup_ids)))))
            ths.append(th)

        for i in ths:
            i.setDaemon(False)    
            i.start()
        for i in ths:    
            i.join()  
                
        contents = ''
        
        q.reverse()
       
        for j in range(len(q)):
            contents +=  q.pop()
            print contents 
        return HttpResponse(contents) 
       
    elif hostgroup_ids:
        
        ths = []
        global q 
        q = []
        for hostgroup in hostgroup_ids:
            hostgroup = int(hostgroup)
            if hostgroup == 0:
                hosts = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))
                for host in hosts:
                    th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                    ths.append(th)

                for i in ths:
                    i.setDaemon(False)    
                    i.start()
                for i in ths:    
                    i.join()  

            else:
                for host in models.Host.objects.filter(hostgroup=models.HostGroup.objects.get(id=hostgroup),status=models.HostStatus.objects.get(name='online')):
                    th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                    ths.append(th)
                    
                for i in ths:
                    i.setDaemon(False)    
                    i.start()
                for i in ths:    
                    i.join()    
            
        contents = ''
        
        q.reverse()
       
        
        for j in range(len(q)):
            contents +=  q.pop()
             
        return HttpResponse(contents)        
        
    else:
        return HttpResponse('请选择主机组或主机<br/>')      
   
        
@login_dresser          
def mysql_return(request):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    stop_time = request.POST.get('stop_time')
    
    if not stop_time:
        stop_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    u_s = models.AdminInfo.objects.select_related().get(username=username).user_info.user_type.caption
    
    if u_s == u'普通运维':
        username_s = 'level1'
    else:
        username_s = 'level2'
        
    if request.method == "POST":
        
        host_ids = request.POST.getlist('host_id[]')
        
        hostgroup_ids = request.POST.getlist('hostgroup_id[]')

    username_s = 'root'
    
    mysql_back_sql_file_gz = '%s-%s-%s.sql.gz'%(datetime.datetime.now().strftime('%Y'),datetime.datetime.now().strftime('%m'),datetime.datetime.now().strftime('%d'))
    
    mysql_back_sql_file = '%s-%s-%s.sql'%(datetime.datetime.now().strftime('%Y'),datetime.datetime.now().strftime('%m'),datetime.datetime.now().strftime('%d'))
    

    cmd_content = '''
        if [ -f /root/%s ];then
           gzip -d  /root/%s;
        fi   
    '''%(mysql_back_sql_file_gz,mysql_back_sql_file_gz)
    
    cmd_content += '''
        binlog_file=`mysql -Nse 'show master status;'|awk '{print $1}'`;
        mysqlbinlog  --base64-output="decode-rows" -vv --stop-datetime="%s"  /var/lib/mysql/$binlog_file >/root/binlog.sql;
    '''%stop_time
    
    cmd_content += '''
        mysql -uroot -e 'set session sql_log_bin=off;use offer;source /root/%s;source /root/binlog.sql;'
    '''%mysql_back_sql_file
    

    
    
    print cmd_content
    
    
    if host_ids:
        contents = ''
        ths = []
        for host in host_ids:
            host = models.Host.objects.get(id=host)

            th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
            ths.append(th)

        for i in ths:
            i.setDaemon(False)    
            i.start()
        for i in ths:    
            i.join()  
                    
            contents = ''
            
            q.reverse()
           
            for j in range(len(q)):
                contents +=  q.pop()
                print contents 
            return HttpResponse(contents)         
    elif hostgroup_ids:
        
        ths = []
        global q 
        q = []
        for hostgroup in hostgroup_ids:
            hostgroup = int(hostgroup)
            if hostgroup == 0:
                hosts = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))
                for host in hosts:
                    th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                    ths.append(th)

                for i in ths:
                    i.setDaemon(False)    
                    i.start()
                for i in ths:    
                    i.join()  

            else:
                for host in models.Host.objects.filter(hostgroup=models.HostGroup.objects.get(id=hostgroup),status=models.HostStatus.objects.get(name='online')):
                    th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,username_s,cmd_content,request.FILES,username,','.join(eval(hostgroup_ids))))
                    ths.append(th)
                    
                for i in ths:
                    i.setDaemon(False)    
                    i.start()
                for i in ths:    
                    i.join()    
            
        contents = ''
        
        q.reverse()
       
        
        for j in range(len(q)):
            contents +=  q.pop()
             
        return HttpResponse(contents)        
        
    else:
        return HttpResponse('请选择主机组或主机<br/>')       
#coding:utf8

from django.shortcuts import  render_to_response,redirect,render
from django.template import RequestContext  
from django.http import  HttpResponse

from app001 import models

from app001.views import login_dresser

import json,os,datetime

import paramiko


from third import handle_uploaded

from offer.settings import BASE_DIR

import threading

import Queue

@login_dresser
def cmd(request):
    
    return render_to_response('cmdb/cmd.html',context_instance=RequestContext(request))


def cmd_hostname(request):
    if request.method == 'POST':
        hostgroup_id = int(request.POST.get('hostgroup_id'))
        
        
    if hostgroup_id:    
        host_info = models.Host.objects.filter(hostgroup_id=hostgroup_id,status=models.HostStatus.objects.get(name='online'))  
    else:
        host_info = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))  
    
    h_i = []
    
    for host_in in host_info:
        H1 = {'id':host_in.id,'hostname':host_in.hostname,'wan_ip':host_in.wan_ip,'lan_ip':host_in.lan_ip}
        h_i.append(H1)
        
    return HttpResponse(json.dumps(h_i),content_type="application/json")    


q = []


def ssh2(ip,hostname,port,username,cmd_content,files,login_username):
    content = ''

    dir_name = os.path.join(BASE_DIR,'upload',username)
    
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)  
                
                
    upload_filename=[]
    
    u_s = models.AdminInfo.objects.select_related().get(username=login_username).user_info.user_type.caption

    if files:
        filename = files.getlist('file')
        for file_name in filename:
            handle_uploaded.handle_uploaded_file(os.path.join(dir_name,file_name.name),file_name)
            upload_filename.append(file_name.name)  
                    
        a = []    
                
        for i in upload_filename:
            a.append(os.path.join('/tmp','upload',username,i))
            
            
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(ip,port,username,key_filename='D:\Documents\Identity',timeout=1)
            
            if u_s == u'普通运维':
                print '1'
                stdin, stdout, stderr = ssh.exec_command('/bin/rm -rf /usr/custom;/bin/mkdir -p /usr/custom_bin;/bin/cp -a   /bin/df /usr/custom_bin; export PATH=/usr/custom_bin;%s'%cmd_content)       
            elif u_s == u'中级运维':
                print '2'
                stdin, stdout, stderr = ssh.exec_command('/bin/rm -rf /usr/custom;/bin/mkdir -p /usr/custom_bin;/bin/cp -a  /bin/df /sbin/ifconfig /sbin/ip /usr/bin/vmstat /usr/bin/dstat /usr/custom_bin;export PATH=/usr/custom_bin;%s'%cmd_content)
            else:
                print '3'
                stdin, stdout, stderr = ssh.exec_command(cmd_content)  
    
            std_out = stdout.readlines()
    
            if  std_out:
                std_out.insert(0,"<font color='red'>"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"<br/>"+hostname+":</font><br/>")
                print '1111:',std_out
                std_out.append('-'*100+" <br/>")
                content += std_out[0]
                for s in std_out[1:]:
                    s = s.replace("\n","<br/>")
                    s = s.replace(" ","&nbsp;")
                    s = s.replace("\x1b[7l","")
                    content += s
                    
            else:
                std_err = stderr.readlines()
                std_err.insert(0,"<font color='red'>"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"<br/>"+hostname+":</font>  <br/>")
                print '222:',std_err
                std_err.append('-'*100+" <br/>")
                content += std_err[0]
                for s in std_err[1:]:
                    s = s.replace("\n","<br/>")
                    s = s.replace(" ","&nbsp;")
                    s = s.replace("\x1b[7l","")
    
                    content += s  
            
        except Exception,e:
            print e
            content += 'ip:%s connection failed...............'%ip
        
        
          
        
        if files:
           
            t = paramiko.Transport((ip,port))
           
            mykey = paramiko.DSSKey.from_private_key_file('D:\Documents\Identity') 
              
            t.connect(username=username,pkey=mykey)
           
            sftp = paramiko.SFTPClient.from_transport(t)
           
            remote_upload_dirname = os.path.join('/tmp','upload',username)
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
    print '循环中的q',q        
    #return content
    
@login_dresser
def cmd_run(request):
    username = request.COOKIES.get('username_password').split('&')[0]
    
    if request.method == "POST":
        host_ids = request.POST.getlist('host_id[]')
        hostgroup_ids = request.POST.getlist('hostgroup_id[]')
        cmd_content = str(request.POST.get('cmd_content'))


    if host_ids:
        if len(host_ids) == 1 and host_ids[0] == -1:
            return HttpResponse('请选择要执行命令的主机<br/>')
        elif not  cmd_content :
            return HttpResponse('请输入要执行的命令<br/>')
        else:
            contents = ''
            ths = []
            for host in host_ids:
                host = models.Host.objects.get(id=host)

                th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,'root',cmd_content,request.FILES,username))
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
        if  len(hostgroup_ids[0]) == 1 and int(hostgroup_ids[0]) == -1 :
            return HttpResponse('请选择要执行命令的主机组<br/>')
        elif not cmd_content:
            return HttpResponse('请输入要执行的命令<br/>')
        else:
            ths = []
            global q 
            q = []
            for hostgroup in hostgroup_ids:
                hostgroup = int(hostgroup)
                if hostgroup == 0:
                    hosts = models.Host.objects.filter(status=models.HostStatus.objects.get(name='online'))
                    for host in hosts:
                        th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,'root',cmd_content,request.FILES,username))
                        ths.append(th)

                    for i in ths:
                        i.setDaemon(False)    
                        i.start()
                    for i in ths:    
                        i.join()  
  
                else:
                    for host in models.Host.objects.filter(hostgroup=models.HostGroup.objects.get(id=hostgroup),status=models.HostStatus.objects.get(name='online')):
                        th = threading.Thread(target=ssh2,args=(host.wan_ip or host.lan_ip,host.hostname,host.port,'root',cmd_content,request.FILES,username))
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
        
        
        
        
        
        
        
        
        
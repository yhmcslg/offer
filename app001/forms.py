#coding:utf8
from django import forms
from app001 import models

class HostForm(forms.ModelForm):
    class Meta:
        model = models.Host
        fields = "__all__"
        
        
    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['hostname'].widget.attrs.update({'class' : 'form-control','placeholder':'主机名,必须'})
        self.fields['lan_ip'].widget.attrs.update({'class' : 'form-control','placeholder':'内网IP,必须'})
        self.fields['wan_ip'].widget.attrs.update({'class' : 'form-control','placeholder':'外网IP,可为空'})
        self.fields['memory'].widget.attrs.update({'class' : 'form-control','placeholder':'内存,必须'})
        self.fields['cpu'].widget.attrs.update({'class' : 'form-control','placeholder':'CPU,必须','rows':3})
        self.fields['brand'].widget.attrs.update({'class' : 'form-control','placeholder':'品牌型号,必须'})
        self.fields['os'].widget.attrs.update({'class' : 'form-control','placeholder':'操作系统,必须'})   
        self.fields['status'].widget.attrs.update({'class' : 'form-control','placeholder':'状态,必须'})  
        self.fields['hostgroup'].widget.attrs.update({'class' : 'form-control','placeholder':'主机组,必须'})
        #self.fields['create_at'].widget.attrs.update({'class' : 'form-control','placeholder':'创建时间'})
        #self.fields['update_at'].widget.attrs.update({'class' : 'form-control','placeholder':'更新时间'})


class HostGroupForm(forms.ModelForm):
    class Meta:
        model = models.HostGroup
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(HostGroupForm, self).__init__(*args, **kwargs)
        self.fields['groupname'].widget.attrs.update({'class' : 'form-control','placeholder':'主机组名,必须'})



TaskTemplate = models.TaskTemplate.objects.all()
TaskTemplate_CHOICES = []
for template in TaskTemplate:
    TaskTemplate_CHOICES.append([template.id, template.name])
    
    
hostGroupName = models.HostGroup.objects.all()
hostGroupContent_CHOICES = []
for hostgroupname in hostGroupName:
    hostGroupContent_CHOICES.append([hostgroupname.id,hostgroupname.groupname])

class TaskForm(forms.ModelForm):
    #task_template_content =  forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control','cols': 40, 'rows': 5,'placeholder':'任务内容'}))
    template_name = forms.CharField(required=False,widget=forms.TextInput(attrs={'class' : 'form-control','placeholder':'任务内容'}))

    class Meta:
        model = models.Task
        fields = "__all__"
        
        
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class' : 'form-control','placeholder':'任务名,必须'})
        self.fields['content'].widget.attrs.update({'class' : 'form-control','placeholder':'任务内容,可为空','rows':3})
        self.fields['file'].widget.attrs.update({'class' : 'form-control','placeholder':'上传文件或目录','multiple':''})
        self.fields['content'].widget.attrs.update({'class' : 'form-control','placeholder':'任务内容,必须','rows':3})
        self.fields['description'].widget.attrs.update({'class' : 'form-control','placeholder':'任务描述,可为空','rows':3})
        #self.fields['kick_off_at'].widget.attrs.update({'class' : 'form-control','placeholder':'执行时间,必须'})
        #self.fields['create_time'].widget.attrs.update({'class' : 'form-control','placeholder':'创建时间,必须'})
        self.fields['task_template'].widget.attrs.update({'class' : 'form-control','onChange':'getTaskTemplateContent(this.value)','choices' :TaskTemplate_CHOICES,'placeholder':'存为任务模板,可为空'})
        
        #self.fields['task_type'].widget.attrs.update({'class' : 'form-control','placeholder':'任务类型,必须'})
        self.fields['execute_type'].widget.attrs.update({'class' : 'form-control','placeholder':'执行类型,必须'})   
        #self.fields['created_by'].widget.attrs.update({'class' : 'form-control','placeholder':'任务创建者,必须'})  
        self.fields['hosts'].widget.attrs.update({'class' : 'form-control','placeholder':'选择任务主机,必须','default':''})
        self.fields['hostsgroup'].widget.attrs.update({'class' : 'form-control','onChange':'getHostName(this.value)','choices' :hostGroupContent_CHOICES,'placeholder':'选择主机组'})
        #self.fields['status'].widget.attrs.update({'class' : 'form-control','placeholder':'任务状态'})
        

       
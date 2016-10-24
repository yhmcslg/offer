from django.conf.urls import include, url


import views
import cmd

from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'HostStatus', views.HostStatusViewSet)
router.register(r'HostGroup', views.HostGroupViewSet)
router.register(r'Host', views.HostViewSet)




urlpatterns = [
    url(r'^index$', views.index),
    
    url(r'^task/$',views.task),
    url(r'^task/task_create$',views.task_create),
    url(r'^task/template_content_json',views.template_content_json),
    url(r'^task/host_Group_Name_json',views.host_Group_Name_json),
    url(r'^task/task_detail/(\d+)?$',views.task_detail),
    url(r'^task/del_task/$',views.del_task),
    url(r'^task/task_log/(\d+)?$',views.task_log),
    url(r'^task/del_task_log/$',views.del_task_log),
    url(r'^task/new_task$',views.new_task),

    
    
    url(r'^cmdb/$',views.cmdb),
    
    url(r'^cmdb/create_host/',views.create_host),
    url(r'^cmdb/host_list/',views.host_list),
    url(r'^cmdb/host_list_s/',views.host_list_s),
    url(r'^cmdb/del_host/',views.del_host),       


    url(r'^cmdb/host_group_list/',views.host_group_list),
    url(r'^cmdb/host_group_create/',views.host_group_create),
    url(r'^cmdb/host_group_update_add/',views.host_group_update_add),
    url(r'^cmdb/host_group_del/',views.host_group_del),
     
      
    url(r'^cmdb/cmd/',cmd.cmd),  
    url(r'^cmdb/cmd_hostname/',cmd.cmd_hostname),
    url(r'^cmdb/cmd_run/',cmd.cmd_run),
    url(r'^cmdb/nt_floor/',cmd.nt_floor),   
    url(r'^cmdb/pic_floor/',cmd.pic_floor),   
    url(r'^cmdb/web_floor/',cmd.web_floor),     
      
      
    url(r'^cmdb/getHostGroup/',views.getHostGroup),  
    url(r'^cmdb/getHostStatus/',views.getHostStatus), 
    
    
    url(r'^cmdb/service_status/',views.service_status),
    url(r'^cmdb/service_group/',views.service_group),

    
    
    url(r'^cmdb/api/', include(router.urls)),
    url(r'^cmdb/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

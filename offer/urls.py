from django.conf.urls import include, url
from django.contrib import admin
from app001 import views


urlpatterns = [
    # Examples:
    # url(r'^$', 'offer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    

    url(r'^login/$',views.login),
    
    url(r'^$',views.login),    
    
    url(r'^logout/$',views.logout),
    
    
    url(r'^test/(\d+)?',views.test),
    
    url(r'^user_info/$',views.user_info),
    
    url(r'^', include('app001.urls')),

]

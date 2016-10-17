from django.shortcuts import render_to_response
from django.template import RequestContext  
from django.http import HttpResponseRedirect


class login(object):
    def process_request(self,request):
        if request.path.find('/login') != -1 and not request.COOKIES.get('username_password'):
            return HttpResponseRedirect('/login')
        elif request.path.find('/login') != -1:
            return render_to_response('login.html',context_instance=RequestContext(request))
    
            
            
    def process_view(self, request, callback, callback_args, callback_kwargs):
        pass
    def process_exception(self, request, exception):
        pass
    
    def process_response(self, request, response):
        return response
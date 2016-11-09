from django.shortcuts import  render_to_response

def test(request):
    render_to_response('test.html')
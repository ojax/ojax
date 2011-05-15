from django.http import HttpResponse
from django.utils import simplejson
from external_applications.models import ExternalApplication
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_app(request):
    application = request.POST['application']
    username = request.POST['username']
    print application
    print username
    
    # try:
    ea, created = ExternalApplication.objects.get_or_create(user=request.user, application=application)
    # if created:
    ea.username = username
    ea.save()
    # else:
    #     ExternalApplication.objects.create(user=request.user, application=application, username = username)
    if request.is_ajax():
        return HttpResponse(simplejson.dumps(True) , mimetype='application/json')
    else:
        return HttpResponse("true")
    # except:
    #     return HttpResponse(simplejson.dumps(False) , mimetype='application/json')

